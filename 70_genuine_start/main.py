import sys
from collections import OrderedDict

import pytz

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

        csv_data, interval = merge_lat_lon_with_grid_data(conn, table_name, selected_start_date, selected_end_date,
                                                          selected_model_run, provider_id, model_id)

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


def get_model_id_sync(model_name, area, country, region):
    try:
        query = "SELECT id, bbox FROM model WHERE"
        params = []

        # Add conditions for each parameter that can be null
        if model_name is not None:
            query += " name = %s"
            params.append(model_name)

        if area is not None:
            query += " AND area = %s"
            params.append(area)

        if country is not None:
            query += " AND country = %s"
            params.append(country)

        if region is not None:
            query += " AND region = %s"
            params.append(region)

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        # Create a cursor
        with conn.cursor() as cursor:
            # Use the SQL module to safely format the query
            query = sql.SQL(query)
            cursor.execute(query, tuple(params))

            # Fetch the result
            result = cursor.fetchone()

        if result is not None:
            # Unpack the result
            model_id, bbox = result
            return model_id, bbox
        else:
            # Handle the case when no rows are found
            print("No matching rows found.")
            return None, None

    except Exception as e:
        print(f"Error: {e}")
        # Handle the exception or exit as needed
        sys.exit(1)


def choose_model(provider_id):
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

        # Query to get model information based on the provider_id
        cursor.execute("SELECT name, area, country, region FROM model WHERE provider_id = %s", (provider_id,))

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        # Unpack the rows into separate lists
        model_names, model_areas, model_countries, model_regions = zip(*rows)
        # Convert each list to a set to remove duplicates
        unique_model_names = list(set(model_names))
        unique_model_areas = list(set(model_areas))
        unique_model_countries = list(set(model_countries))
        unique_model_regions = list(set(model_regions))
        unique_model_countries.append(None)
        unique_model_regions.append(None)
        return unique_model_names, unique_model_areas, unique_model_countries, unique_model_regions

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None, None


def choose_provider():
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
        cursor.execute("SELECT name, id FROM provider")

        # Fetch all table names
        rows = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        # Unpack the rows into separate lists
        provider_names, provider_ids = zip(*rows)

        return provider_names, provider_ids

    except Exception as e:
        print(f"Error: {e}")
        return None, None


def list_tables(provider_id, model_id):
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

        # Query to get a list of tables in the 'public' schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        table_names = [table[0] for table in cursor.fetchall()]

        # Initialize a list to store tables with matching rows
        matching_tables = []

        # Iterate through each table and check for matching rows
        for table_name in table_names:
            if table_name not in ["model", "provider", "lat_lon_schema"]:
                query = f'SELECT COUNT(*) FROM "{table_name}" WHERE provider_id = %s AND model_id = %s'
                cursor.execute(query, (provider_id, model_id))
                count = cursor.fetchone()[0]

                if count > 0:
                    matching_tables.append(table_name)

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return matching_tables

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

        query = sql.SQL("SELECT start_date, end_date, model_run, valid_dates FROM {} "
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


entire_provider_id = None
entire_model_id = None

if __name__ == "__main__":
    provider_name, provider_ids = choose_provider()
    if not provider_ids:
        print("No providers found in the database.")
    else:
        print("Available Providers:")
        for idx, table in enumerate(provider_name):
            print(f"{idx + 1}. {table}")

        # Let the user choose a table
        provider_choice = input("Enter the number of the provider you want: ")
        selected_provider_id = None
        provider_choice = int(provider_choice)
        if 1 <= provider_choice <= len(provider_ids):
            selected_provider_id = provider_ids[provider_choice - 1]

        entire_provider_id = selected_provider_id
        model_names, model_areas, model_countries, model_regions = choose_model(provider_id=selected_provider_id)
        selected_model_name = None
        selected_model_area = None
        selected_model_country = None
        selected_model_region = None

        print("Available Model Names:")
        for idx, table in enumerate(model_names):
            print(f"{idx + 1}. {table}")
        model_name_choice = input("Enter the number of the model you want: ")
        model_name_choice = int(model_name_choice)
        if 1 <= model_name_choice <= len(model_names):
            selected_model_name = model_names[model_name_choice - 1]

        print("Available Areas:")
        for idx, table in enumerate(model_areas):
            print(f"{idx + 1}. {table}")
        modela_area_choice = input("Enter the number of the area you want: ")
        modela_area_choice = int(modela_area_choice)
        if 1 <= modela_area_choice <= len(model_areas):
            selected_model_area = model_areas[modela_area_choice - 1]

        print("Available Countries:")
        for idx, table in enumerate(model_countries):
            print(f"{idx + 1}. {table}")
        modela_country_choice = input("Enter the number of the country you want: ")
        modela_country_choice = int(modela_country_choice)
        if 1 <= modela_country_choice <= len(model_countries):
            selected_model_country = model_countries[modela_country_choice - 1]

        print("Available Region:")
        for idx, table in enumerate(model_regions):
            print(f"{idx + 1}. {table}")
        modela_region_choice = input("Enter the number of the region you want: ")
        modela_region_choice = int(modela_region_choice)
        if 1 <= modela_region_choice <= len(model_regions):
            selected_model_region = model_regions[modela_region_choice - 1]

        model_id, bbox = get_model_id_sync(model_name=selected_model_name,
                                     area=selected_model_area,
                                     country=selected_model_country,
                                     region=selected_model_region)

        entire_model_id = model_id
    # List all available tables
    tables = list_tables(entire_provider_id, entire_model_id)

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

                records = display_records(selected_table)
                if not records:
                    print(f"No records found in table '{selected_table}'.")
                else:
                    print(f"Records in table '{selected_table}':")
                    for idx, record in enumerate(records, start=1):
                        start_date, end_date, model_run, valid_dates = record
                        print(f"{idx}. Start Date: {start_date}, End Date: {end_date}, Model Run: {model_run}")
                # Let the user choose a specific record
                record_choice = input("Enter the number of the record you want to select: ")
                try:
                    record_choice = int(record_choice)
                    if 1 <= record_choice <= len(records):
                        selected_record = records[record_choice - 1]

                        selected_start_date, selected_end_date, selected_model_run, valid_dates = selected_record

                        # Calculate predefined dates for each day within the selected range
                        predefined_dates = []
                        target_timezone = pytz.timezone('Europe/Ljubljana')

                        # Iterate through each datetime object in valid_dates
                        for dt in valid_dates:
                            # Convert the datetime to the target timezone
                            dt_ljubljana = dt.astimezone(target_timezone)

                            # Extract the day in the format "%Y-%m-%d"
                            day_str = dt_ljubljana.strftime("%Y-%m-%d")

                            # Add the day to the set
                            predefined_dates.append(day_str)
                        # Remove duplicates while preserving order
                        predefined_dates = list(OrderedDict.fromkeys(predefined_dates))
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
                                                                                     "./data/output_with_coordinates"
                                                                                     ".csv",
                                                                                     entire_provider_id, entire_model_id)
                        color_configuration = read_colors("../assets/colors/colors.config")
                        storage_directory = "./data"
                        maps_output_directory = os.path.join(storage_directory, 'public/plots')
                        font_path = '../assets/fonts/'
                        custom_font = FontProperties(fname=font_path + 'font.ttf')
                        try:
                            create_maps(selected_model_run, df_array, maps_output_directory, color_configuration,
                                        custom_font,
                                        selected_start_date, selected_end_date, selected_date, bbox)
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
