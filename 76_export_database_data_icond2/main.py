import os
import csv
import psycopg2
from psycopg2 import sql
import pandas as pd
import pytz
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Get database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

PROVIDER_ID = os.getenv("DWD_PROVIDER_ID")
MODEL_ID = os.getenv("DWD_MODEL_ID")

def establish_database_connection():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Error establishing a database connection: {e}")
        return None

def get_latitudes_and_longitudes(conn, provider_id, model_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT latitudes, longitudes FROM lat_lon_schema WHERE provider_id = %s AND model_id = %s", (provider_id, model_id))
        row = cursor.fetchone()

        if row:
            latitudes, longitudes = row
            return latitudes, longitudes
        else:
            print(f"No latitudes and longitudes found for provider_id {provider_id} and model_id {model_id}.")
            return None, None
    except Exception as e:
        print(f"Error getting latitudes and longitudes: {e}")
        return None, None

def fetch_and_process_data(conn, table_name, selected_start_date, selected_end_date, selected_model_run):
    cursor = conn.cursor()
    table_identifier = sql.Identifier(table_name)
    query = sql.SQL("SELECT start_date, end_date, interval, model_run, data FROM {} "
                    "WHERE start_date = %s AND end_date = %s AND model_run = %s").format(table_identifier)
    
    cursor.execute(query, (selected_start_date, selected_end_date, selected_model_run))
    rows = cursor.fetchall()

    if rows:
        csv_data = []
        for row in rows:
            start_date, end_date, interval, model_run, data = row
            start_date = start_date.astimezone(pytz.timezone('Europe/Ljubljana'))
            end_date = end_date.astimezone(pytz.timezone('Europe/Ljubljana'))
            if interval == timedelta(hours=2):
                interval = timedelta(hours=1)

            current_date = start_date
            interval_seconds = int(interval.total_seconds())

            for day_data in data:
                current_date += timedelta(seconds=interval_seconds)
                day_data = [0.0 if value is None else value for value in day_data]

                latitudes, longitudes = get_latitudes_and_longitudes(conn, PROVIDER_ID, MODEL_ID)

                coordinate_index = 0

                for value in day_data:
                    coordinate_index %= len(latitudes)
                    lat = latitudes[coordinate_index]
                    lon = longitudes[coordinate_index]
                    combined_data = (current_date, value, lat, lon)
                    csv_data.append(combined_data)
                    coordinate_index += 1

        df = pd.DataFrame(csv_data, columns=['Datetime', 'Value', 'Latitude', 'Longitude'])
        return df
    else:
        print(f"No data found in table '{table_name}'.")
        return None
    
from datetime import datetime

def main():
    conn = establish_database_connection()
    if conn:
        # Define start_date and end_date as datetime objects
        start_date = datetime(2023, 10, 24, 9, 0)  # Replace with your actual datetime
        end_date = datetime(2023, 10, 26, 9, 0)    # Replace with your actual datetime

        df = fetch_and_process_data(conn, "2_metre_temperature_icond2", start_date, end_date, "9")
        if df is not None:
            df.to_csv("./data/temperature_grid_icond2.csv")
        conn.close()

if __name__ == "__main__":
    main()

