from animation.animation import create_gif_from_png
from merger.merge import merge_lat_lon_with_grid_data
from parse_settings.read.read_colors import read_colors
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
from generate_maps.create import create_maps
from matplotlib.font_manager import FontProperties

from split.splitter import split_data

# Load environment variables from .env
load_dotenv()

# Database connection information
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def extract_coordinates(coord_str):
    # Extract latitude and longitude from the coordinate string
    coord_str = coord_str.strip('()')
    lat, lon = map(float, coord_str.split(', '))
    return lat, lon


def write_data_to_csv_with_coordinates(selected_start_date, selected_end_date, selected_model_run, date_choice,
                                       table_name, output_file, provider_id, model_id):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        csv_data, interval = merge_lat_lon_with_grid_data(conn, table_name, selected_start_date, selected_end_date, selected_model_run, provider_id, model_id)

        if csv_data is None:
            print(f"No data found in table '{table_name}'.")
            return ValueError("Wrong")

        if interval is None:
            print(f"Interval is not correct.")
            return ValueError("Interval is not correct.")

        if sort_interval == "1":
            agg_name = 'animation' + '_' + table_name
        else:
            agg_name = agg_function + '_' + table_name
        df = pd.DataFrame(csv_data, columns=['Datetime', agg_name, 'Latitude', 'Longitude'])

        df, selected_date = filterSpecificDate(df, date_choice, end_date)

        df = convert_data(df, agg_name)
        if sort_interval == "0":
            df_array = [createAgregates(df, agg_function, table_name)]
        else:
            df_array = split_data(df, interval)
        conn.close()

        return df_array, selected_date

    except Exception as e:
        print(f"Error: {e}")


def filterSpecificDate(df, date_choice, end_date):
    try:
        selected_date = None
        date_choice = int(date_choice)
        if 1 <= date_choice <= len(predefined_dates):
            selected_date = predefined_dates[date_choice - 1]
            # Convert selected_date to a datetime object
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d")

            # Extract year, month, and day from the selected date
            year = selected_date.year
            month = selected_date.month
            day = selected_date.day

            # Filter the data for the same year, month, and day and perform aggregation
            df_filtered = df[
                (df['Datetime'].dt.year == year) &
                (df['Datetime'].dt.month == month) &
                (df['Datetime'].dt.day == day)
                ]

            # Perform aggregation here using df_filtered
            return df_filtered, selected_date
        else:
            print("Invalid date number. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def createAgregates(df, agg_function, table_name):
    agg_column = df.columns[1]
    if agg_function == 'sum':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].sum()
    elif agg_function == 'max':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].max()
    elif agg_function == 'min':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].min()


def convert_ms_to_kmh(ms):
    return ms * 3.6

def convert_m_to_cm(value):
    return value * 100;


def convert_data(df, table_name):
    if (table_name.startswith('max_10_metre_v_wind_component_icond2') or table_name.startswith(
            'max_maximum_wind_10m_icond2') or table_name.startswith('animation_maximum_wind_10m_icond2')):
        df[table_name] = df[table_name].apply(convert_ms_to_kmh)
    elif (table_name.startswith('max_snow_depth_icond2') or table_name.startswith('sum_snow_depth_icond2')):
        df[table_name] = df[table_name].apply(convert_m_to_cm)

    return df


def list_tables():
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Query to get a list of tables in the database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")

        # Fetch all table names
        tables = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return [table[0] for table in tables]

    except Exception as e:
        print(f"Error: {e}")
        return []


def display_records(table_name):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Define the table name as an SQL Identifier
        table_identifier = sql.Identifier(table_name)

        query = sql.SQL("SELECT start_date, end_date, model_run FROM {} "
                        "ORDER BY start_date DESC "
                        "LIMIT 500").format(table_identifier)

        # Execute the SQL query
        cursor.execute(query)

        # Fetch all records
        records = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return records

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    # List all available tables
    tables = list_tables()

    if not tables:
        print("No tables found in the database.")
    else:
        print("Available tables:")
        for idx, table in enumerate(tables):
            print(f"{idx + 1}. {table}")

        # Let the user choose a table
        table_choice = input("Enter the number of the table you want to view records for: ")

        try:
            table_choice = int(table_choice)
            if 1 <= table_choice <= len(tables):
                selected_table = tables[table_choice - 1]

                # Determine the provider_id and model_id based on the table name
                if selected_table.endswith("_icond2"):
                    provider_id = os.getenv("DWD_PROVIDER_ID")  # Set the appropriate ID for icond2
                    model_id = os.getenv("DWD_MODEL_ID")  # Set the appropriate ID for icond2
                elif selected_table.endswith("_aladin"):
                    provider_id = os.getenv("ARSO_PROVIDER_ID")  # Set the appropriate ID for aladin
                    model_id = os.getenv("ARSO_MODEL_ID")  # Set the appropriate ID for aladin
                else:
                    print("Invalid table name format. The table name should end with '_icond2' or '_aladin'.")
                    exit(1)

                records = display_records(selected_table)

                if not records:
                    print(f"No records found in table '{selected_table}'.")
                else:
                    print(f"Records in table '{selected_table}':")
                    for idx, record in enumerate(records, start=1):
                        start_date, end_date, model_run = record
                        print(f"{idx}. Start Date: {start_date}, End Date: {end_date}, Model Run: {model_run}")

                # Let the user choose a specific record
                record_choice = input("Enter the number of the record you want to select: ")
                try:
                    record_choice = int(record_choice)
                    if 1 <= record_choice <= len(records):
                        selected_record = records[record_choice - 1]

                        selected_start_date, selected_end_date, selected_model_run = selected_record

                        # Calculate predefined dates for each day within the selected range
                        predefined_dates = []

                        current_date = selected_start_date
                        while current_date <= selected_end_date:
                            predefined_dates.append(current_date.strftime("%Y-%m-%d"))
                            current_date += timedelta(days=1)


                        # Display the predefined dates
                        for idx, date in enumerate(predefined_dates, start=1):
                            print(f"{idx}. {date}")

                        date_choice = input("Enter the number of the date for aggregation: ")

                        sort_interval = input("Enter type of generation (0 for normal, 1 for gif): ")

                        # Check if the input is either '0' or '1'
                        if sort_interval == '0':
                            print("Normal generation selected")
                            # Rest of your code for normal generation goes here
                        elif sort_interval == '1':
                            print("GIF generation selected")
                            # Rest of your code for GIF generation goes here
                        else:
                            print("Invalid input. Please enter '0' for normal or '1' for gif.")
                            raise TypeError("Invalid input. Please enter '0' for normal or '1' for gif.")

                        # Let the user choose an aggregation function
                        agg_function = input("Choose an aggregation function (sum, max, min): ")
                        if agg_function not in ["sum", "max", "min"]:
                            print("Invalid aggregation function. Please choose from 'sum', 'max', or 'min'.")

                        print(f"Aggregated data using {agg_function}:")

                        # Perform aggregation here using provider_id, model_id, and selected_record
                        df_array, selected_date = write_data_to_csv_with_coordinates(selected_start_date,
                                                                               selected_end_date,
                                                                               selected_model_run, date_choice,
                                                                               selected_table,
                                                                               "./data/output_with_coordinates.csv",
                                                                               provider_id, model_id)
                        color_configuration = read_colors("../assets/colors/colors.config")
                        storage_directory = "./data"
                        maps_output_directory = os.path.join(storage_directory, 'public/plots')
                        font_path = '../assets/fonts/'
                        custom_font = FontProperties(fname=font_path + 'font.ttf')
                        try:
                            create_maps(selected_model_run, df_array, maps_output_directory, color_configuration, custom_font,
                                    selected_start_date, selected_end_date, selected_date)
                        except Exception as e:
                            print(f"{e}")
                    else:
                        print("Invalid record number. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            else:
                print("Invalid table number. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
