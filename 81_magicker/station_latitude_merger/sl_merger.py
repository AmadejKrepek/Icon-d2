import pandas as pd
import pytz
from psycopg2 import sql

from utils.utils import establish_stations_database_connection

# Get tables with the specified prefixes
prefixes = ['auto', 'obs']


def create_stations_with_lat_lon(start_date, end_date):
    conn_stations = establish_stations_database_connection()
    data = get_lat_lon(conn_stations)
    data = get_station_data(conn_stations, data, start_date, end_date)
    df = pd.DataFrame(data, columns=['Latitude', 'Longitude', 'StationName', 'Temperature', 'ValidUtc'])
    return df


def get_station_data(conn, data, start_date, end_date):
    updated_data = []
    for latitude, longitude, station_name in data:
        temperatures, valid_utcs = retrieve_data_for_interval(conn, station_name, 'valid_utc', start_date, end_date)
        for temperature, valid_utc in zip(temperatures, valid_utcs):
            # Format valid_utc to display date, hours, minutes, seconds, and append +00:00
            valid_utc_formatted = valid_utc.strftime('%Y-%m-%d %H:%M:%S') + '+00:00'
            updated_data.append([latitude, longitude, station_name, temperature, valid_utc_formatted])
    return updated_data


def retrieve_data_for_interval(conn, table, valid_utc_column, start_date, end_date):
    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Convert start_date and end_date to UTC
    start_date_utc = start_date.astimezone(pytz.utc)
    end_date_utc = end_date.astimezone(pytz.utc)

    # Construct the SQL query with parameterized valid_utc and temperature not being None
    query = sql.SQL("""
        SELECT temperature, valid_utc
        FROM {}
        WHERE {} BETWEEN %s AND %s AND temperature IS NOT NULL
    """).format(
        sql.Identifier(table),
        sql.Identifier(valid_utc_column)
    )

    # Execute the query with the specified interval
    cursor.execute(query, (start_date_utc, end_date_utc))

    # Fetch the results
    results = cursor.fetchall()

    # Close the cursor
    cursor.close()

    return [record[0] for record in results], [record[1] for record in results]


def get_lat_lon(conn):
    data = []
    query = "SELECT latitude, longitude, station_name FROM basic"

    # Execute the query
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    # Process the result
    for row in result:
        latitude, longitude, station_name = row
        data.append([latitude, longitude, station_name])

    return data
