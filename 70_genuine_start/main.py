from parse_settings.read.read_colors import read_colors
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import csv
from datetime import datetime, timedelta
import pandas as pd
from generate_maps.create import create_maps
from matplotlib.font_manager import FontProperties

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

def get_latitudes_and_longitudes(provider_id, model_id):
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

        # Query the latitudes and longitudes based on provider_id and model_id from the lat_lon_schema table
        cursor.execute("SELECT latitudes, longitudes FROM lat_lon_schema WHERE provider_id = %s AND model_id = %s", (provider_id, model_id))

        # Fetch the row
        row = cursor.fetchone()

        if row:
            latitudes, longitudes = row
            return latitudes, longitudes
        else:
            print(f"No latitudes and longitudes found for provider_id {provider_id} and model_id {model_id}.")
            return None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None

def write_data_to_csv_with_coordinates(selected_start_date, selected_end_date, selected_model_run, date_choice, table_name, output_file, provider_id, model_id):
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

       # Query the data from the specified table
        # Use the table_identifier in the SQL query
        query = sql.SQL("SELECT start_date, end_date, interval, model_run, data FROM {} "
                        "WHERE start_date = %s AND end_date = %s AND model_run = %s").format(table_identifier)

        # Execute the SQL query with the provided parameters
        cursor.execute(query, (selected_start_date, selected_end_date, selected_model_run))

        # Fetch all rows
        rows = cursor.fetchall()

        csv_data = []
        init_interval = None
        latitudes, longitudes = get_latitudes_and_longitudes(provider_id, model_id)

        if rows:
            for row in rows:
                start_date, end_date, interval, model_run, data = row
                current_date = start_date
                interval_seconds = int(interval.total_seconds())

                if init_interval == None:
                    init_interval = interval

                for day_data in data:
                    current_date += timedelta(seconds=interval_seconds)

                    # Replace None with 0.0 in weather data
                    day_data = [0.0 if value is None else value for value in day_data]

                    # Initialize an index to track the current coordinate
                    coordinate_index = 0

                    for value in day_data:
                        # Ensure the coordinate index stays within bounds
                        coordinate_index %= len(latitudes)

                        # Get the latitude and longitude for the current index
                        lat = latitudes[coordinate_index]
                        lon = longitudes[coordinate_index]

                        # Combine timestamp, weather data, and coordinates
                        combined_data = (current_date, value, lat, lon)

                        # Append the combined data point to the CSV data
                        csv_data.append(combined_data)

                        # Increment the coordinate index
                        coordinate_index += 1

            agg_name = agg_function + '_' + table_name

            df = pd.DataFrame(csv_data, columns=['Datetime', agg_name, 'Latitude', 'Longitude'])

            df, selected_date = filterSpecificDate(df, date_choice, end_date)

            df = convert_data(df, agg_name)

            df = createAgregates(df, agg_function, table_name)

            return df, selected_date

        else:
            print(f"No data found in table '{table_name}'.")

        # Close the cursor and the connection
        cursor.close()
        conn.close()

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

def convert_data(df, table_name):
    if (table_name.startswith('max_10_metre_v_wind_component_icond2') or table_name.startswith('max_maximum_wind_10m_icon_d2')):
        # Access the third column (index 2) and apply the conversion function
        print('Converted kmh to ms...')
        df[table_name] = df[table_name].apply(convert_ms_to_kmh)

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
                "LIMIT 40").format(table_identifier)
        
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
                    provider_id = "6be8cea2-f29b-4198-aa68-10c57845ad25"  # Set the appropriate ID for icond2
                    model_id = "581e4233-dc8c-44d3-b351-c115dc32fc53"  # Set the appropriate ID for icond2
                elif selected_table.endswith("_aladin"):
                    provider_id = "66b97430-1782-4793-906d-f77b4303373b"  # Set the appropriate ID for aladin
                    model_id = "62490a51-1f97-4858-874b-267ea06bdbcc"  # Set the appropriate ID for aladin
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

                        # Generate predefined dates within the range of selected_start_date to selected_end_date
                        predefined_dates = []
                        current_date = selected_start_date

                        while current_date <= selected_end_date:
                            predefined_dates.append(current_date.strftime("%Y-%m-%d"))
                            current_date += timedelta(days=1)

                        # Display the predefined dates and let the user choose one
                        print("Predefined Dates within the Range:")
                        for idx, date in enumerate(predefined_dates, start=1):
                            print(f"{idx}. {date}")

                        date_choice = input("Enter the number of the date for aggregation: ")

                        # Let the user choose an aggregation function
                        agg_function = input("Choose an aggregation function (sum, max, min): ")

                        # Perform aggregation if the choice is valid
                        if agg_function in ["sum", "max", "min"]:
                            print(f"Aggregated data using {agg_function}:")
                            # Perform aggregation here using provider_id, model_id, and selected_record
                            df, selected_date = write_data_to_csv_with_coordinates(selected_start_date, selected_end_date, selected_model_run, date_choice, selected_table, "./data/output_with_coordinates.csv", provider_id, model_id)
                            color_configuration = read_colors("../assets/colors/colors.config")
                            storage_directory = "./data"
                            maps_output_directory = os.path.join(storage_directory, 'public/plots')
                            font_path = '../assets/fonts/'
                            custom_font = FontProperties(fname=font_path + 'font.ttf')
                            create_maps(model_run, df, maps_output_directory, color_configuration, custom_font, selected_start_date, selected_end_date, selected_date)
                        else:
                            print("Invalid aggregation function. Please choose from 'sum', 'max', or 'min'.")
                    else:
                        print("Invalid record number. Please enter a valid number.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            else:
                print("Invalid table number. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
