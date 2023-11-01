import os
import pandas as pd
import pytz
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from datetime import timedelta, datetime
from scipy.spatial import cKDTree

load_dotenv()

# Load environment variables
db_params_stations = {
    "dbname": os.getenv("STATIONS_DB_NAME"),
    "user": os.getenv("STATIONS_DB_USERNAME"),
    "password": os.getenv("STATIONS_DB_PASSWORD"),
    "host": os.getenv("STATIONS_DB_HOST"),
    "port": os.getenv("STATIONS_DB_PORT")
}

db_params_test = {
    "dbname": os.getenv("TEST_DB_NAME"),
    "user": os.getenv("TEST_DB_USERNAME"),
    "password": os.getenv("TEST_DB_PASSWORD"),
    "host": os.getenv("TEST_DB_HOST"),
    "port": os.getenv("TEST_DB_PORT")
}

PROVIDER_ID = os.getenv("DWD_PROVIDER_ID")
MODEL_ID = os.getenv("DWD_MODEL_ID")


def establish_database_connection(db_params):
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Error establishing a database connection: {e}")
        return None


def get_latitudes_and_longitudes(provider_id, model_id):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(**db_params_test)

        # Create a cursor object
        cursor = conn.cursor()

        # Query the latitudes and longitudes based on provider_id and model_id from the lat_lon_schema table
        cursor.execute("SELECT latitudes, longitudes FROM lat_lon_schema WHERE provider_id = %s AND model_id = %s",
                       (provider_id, model_id))

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

                latitudes, longitudes = get_latitudes_and_longitudes(PROVIDER_ID, MODEL_ID)

                for lat, lon, value in zip(latitudes, longitudes, day_data):
                    combined_data = (current_date, value, lat, lon)
                    csv_data.append(combined_data)

        df = pd.DataFrame(csv_data, columns=['Datetime', 'Value', 'Latitude', 'Longitude'])
        return df
    else:
        print(f"No data found in table '{table_name}'.")
        return None


def get_lat_lon_from_basic(conn_stations, station_table):
    try:
        cursor = conn_stations.cursor()
        cursor.execute("SELECT latitude, longitude FROM basic WHERE station_name = %s", (station_table,))
        row = cursor.fetchone()

        if row:
            latitude, longitude = row
            return latitude, longitude
        else:
            print(f"No latitude and longitude found for station {station_table}.")
            return None, None
    except Exception as e:
        print(f"Error getting latitude and longitude: {e}")
        return None, None


def correct_icon_d2_with_station_data(icon_d2_data, conn_stations):
    icon_d2_df = pd.DataFrame(icon_d2_data, columns=["Datetime", "Value", "Latitude", "Longitude"])

    # Get a list of tables starting with "obs" or "auto"
    cursor_stations = conn_stations.cursor()
    cursor_stations.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND (table_name LIKE "
        "'obs%' OR table_name LIKE 'auto%')")
    station_tables = [row[0] for row in cursor_stations.fetchall()]

    for station_table in station_tables:
        latitude, longitude = get_lat_lon_from_basic(conn_stations, station_table)
        if latitude is not None and longitude is not None:
            # Retrieve station temperature data for the station
            station_temperature_data = get_station_temperature_data(conn_stations, station_table, start_date, end_date)

            if station_temperature_data is not None:
                # Replace the corresponding values in Icon D2 with station temperature data
                mask = (icon_d2_df['Latitude'] == latitude) & (icon_d2_df['Longitude'] == longitude)
                icon_d2_df.loc[mask, 'Value'] = station_temperature_data
            else:
                print(f"No temperature data found for station '{station_table}'.")
        else:
            print(f"No latitude and longitude found for station '{station_table}'.")

    return icon_d2_df



def get_station_temperature_data(conn_stations, station_name, start_date, end_date):
    try:
        cursor = conn_stations.cursor()
        query = sql.SQL("SELECT temperature, valid_utc FROM {table_name} "
                        "WHERE valid_utc >= %s AND valid_utc <= %s")
        cursor.execute(query, (station_name, start_date, end_date))
        rows = cursor.fetchall()

        temperature_data = {row[1]: row[0] for row in rows}  # Create a dictionary with valid_utc as key

        return [temperature_data[utc] if utc in temperature_data else None for utc in datetimes]
    except Exception as e:
        print(f"Error getting temperature data: {e}")
        return None



def main():
    conn_stations = establish_database_connection(db_params_stations)
    conn_test = establish_database_connection(db_params_test)

    if conn_stations and conn_test:
        start_date = datetime(2023, 10, 24, 9, 0)
        end_date = datetime(2023, 10, 26, 9, 0)

        df_icon_d2 = fetch_and_process_data(conn_test, "2_metre_temperature_icond2", start_date, end_date, "9")

        if df_icon_d2 is not None:
            cursor_stations = conn_stations.cursor()
            cursor_stations.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND (table_name LIKE "
                "'obs%' OR table_name LIKE 'auto%')")
            station_tables = [row[0] for row in cursor_stations.fetchall()]

            corrected_d2_data_list = []

            for station_table in station_tables:
                corrected_d2_data = correct_icon_d2_with_station_data(df_icon_d2, conn_stations)
                corrected_d2_data_list.append(corrected_d2_data)

                output_csv_filename = f"./data/corrected_{station_table}.csv"
                corrected_d2_data.to_csv(output_csv_filename)
                print(f"Corrected data for '{station_table}' has been saved to {output_csv_filename}")

            # Combine data from all stations
            combined_data = pd.concat(corrected_d2_data_list, ignore_index=True)

            # Save combined data to a CSV file
            combined_data.to_csv("./data/combined_corrected_data.csv", index=False)
            print("Combined corrected data has been saved to 'combined_corrected_data.csv'.")

        conn_stations.close()
        conn_test.close()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
