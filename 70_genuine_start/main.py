import psycopg2
import os
from dotenv import load_dotenv
import csv
from datetime import datetime, timedelta
import pandas as pd

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

def write_data_to_csv_with_coordinates(table_name, output_file, provider_id, model_id):
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

        # Query the data from the specified table
        cursor.execute(f"SELECT start_date, end_date, interval, data FROM {table_name} LIMIT 1")

        # Fetch all rows
        rows = cursor.fetchall()

        csv_data = []
        initial_start_date = None
        initial_end_date = None
        initial_interval = None
        index = None
        latitudes, longitudes = get_latitudes_and_longitudes(provider_id, model_id)

        if rows:
            for row in rows:
                start_date, end_date, interval, data = row
                current_date = start_date
                interval_seconds = int(interval.total_seconds())

                if initial_start_date == None:
                    initial_start_date = start_date
                    initial_end_date = end_date
                    initial_interval = interval

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


            df = createAgregates(csv_data, 'max', table_name)

            df.to_csv(output_file)

            print(f"CSV file '{output_file}' created successfully.")

            return df, initial_start_date, initial_end_date, interval

        else:
            print(f"No data found in table '{table_name}'.")

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

def createAgregates(csv_data, agg_function, table_name):
    df = pd.DataFrame(csv_data, columns=['Datetime', agg_function + '_' + table_name, 'Latitude', 'Longitude'])
    agg_column = df.columns[1]
    if agg_function == 'sum':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].sum()
    elif agg_function == 'max':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].max()
    elif agg_function == 'min':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].min()
    
if __name__ == "__main__":
    # Specify the table name, output file name, provider_id, and model_id
    table_name = "total_precipitation_icond2"  # Replace with your table name
    output_file = "./data/output_with_coordinates.csv"  # Replace with your desired output file name
    provider_id = "6be8cea2-f29b-4198-aa68-10c57845ad25"  # Replace with the desired provider_id as a string
    model_id = "581e4233-dc8c-44d3-b351-c115dc32fc53"  # Replace with the desired model_id as a string

    df = write_data_to_csv_with_coordinates(table_name, output_file, provider_id, model_id)
