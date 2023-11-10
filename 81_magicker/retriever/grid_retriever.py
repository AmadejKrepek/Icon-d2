import os
from datetime import timedelta

import pandas as pd
import pytz
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()

PROVIDER_ID = os.getenv("DWD_PROVIDER_ID")
MODEL_ID = os.getenv("DWD_MODEL_ID")


def get_latitudes_and_longitudes(conn, provider_id, model_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT latitudes, longitudes FROM lat_lon_schema WHERE provider_id = %s AND model_id = %s",
                       (provider_id, model_id))
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


def fetch_and_process_data(conn, table_name, start_date, end_date, model_run):
    cursor = conn.cursor()
    table_identifier = sql.Identifier(table_name)

    query = sql.SQL("""
        SELECT start_date, end_date, interval, model_run, data 
        FROM {} 
        WHERE 
            DATE(start_date) = %s
            AND model_run = %s
    """).format(table_identifier)

    # Convert start_date and end_date to UTC and strip off the time component
    start_date_utc = start_date.astimezone(pytz.utc).strftime('%Y-%m-%d')
    end_date_utc = end_date.astimezone(pytz.utc).strftime('%Y-%m-%d')

    cursor.execute(query, (start_date_utc, model_run))
    rows = cursor.fetchall()

    if rows:
        csv_data = []
        for row in rows:
            counter = 0
            start_date, end_date, interval, model_run, data = row
            #start_date = start_date.astimezone(pytz.timezone('Europe/Ljubljana'))
            #end_date = end_date.astimezone(pytz.timezone('Europe/Ljubljana'))
            if interval == timedelta(hours=2):
                interval = timedelta(hours=1)

            current_date = start_date
            interval_seconds = int(interval.total_seconds())

            for day_data in data:
                if counter > 0:
                    current_date += timedelta(seconds=interval_seconds)
                counter += 1
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
