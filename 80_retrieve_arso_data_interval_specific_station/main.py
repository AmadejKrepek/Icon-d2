import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import pytz

# Load environment variables from the .env file
load_dotenv()

# Retrieve database credentials from environment variables
db_params = {
    'host': os.getenv('STATIONS_DB_HOST'),
    'database': os.getenv('STATIONS_DB_NAME'),
    'user': os.getenv('STATIONS_DB_USERNAME'),
    'password': os.getenv('STATIONS_DB_PASSWORD'),
}


def connect_to_database():
    # Create a connection to the database
    return psycopg2.connect(**db_params)


def close_database_connection(conn):
    # Close the database connection
    conn.close()


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

    return results


def get_tables_with_prefix(conn, prefix):
    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Use the information_schema to get a list of all tables with the specified prefix
    query = sql.SQL("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE %s
    """)
    cursor.execute(query, (f'{prefix}%',))

    # Fetch the results
    results = cursor.fetchall()

    # Close the cursor
    cursor.close()

    return results


def example_usage():
    # Example usage
    valid_utc_column = 'valid_utc'

    # Specify start_date and end_date in Europe/Ljubljana timezone
    local_tz = pytz.timezone('Europe/Ljubljana')
    start_date = local_tz.localize(datetime(2023, 11, 1, 00, 00, 00))
    end_date = local_tz.localize(datetime(2023, 11, 11, 23, 59, 00))

    # Connect to the database
    conn = connect_to_database()

    # Get tables with the specified prefixes
    prefixes = ['auto', 'obs']
    for prefix in prefixes:
        tables_with_prefix = get_tables_with_prefix(conn, prefix)

        for table_info in tables_with_prefix:
            table_name = table_info[0]

            # Retrieve data for the interval for each table where temperature is not None
            data_for_interval = retrieve_data_for_interval(conn, table_name, valid_utc_column, start_date, end_date)

            # Print or process the results as needed
            for row in data_for_interval:
                print(f'Table: {table_name}, Row: {row}')

    # Close the database connection
    close_database_connection(conn)


# Call the example usage function
example_usage()
