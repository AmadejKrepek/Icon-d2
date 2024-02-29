from datetime import timedelta

import pytz
from psycopg2 import sql

from merger.latitude import get_latitudes_and_longitudes


def merge_lat_lon_with_grid_data(conn, table_name, selected_start_date, selected_end_date, selected_model_run,
                                 provider_id, model_id):
    # Create a cursor object
    cursor = conn.cursor()

    # Define the table name as an SQL Identifier
    table_identifier = sql.Identifier(table_name)

    # Query the data from the specified table
    # Use the table_identifier in the SQL query
    query = sql.SQL("SELECT start_date, end_date, interval, model_run, valid_dates, data FROM {} "
                    "WHERE start_date = %s AND end_date = %s AND model_run = %s").format(table_identifier)

    # Execute the SQL query with the provided parameters
    cursor.execute(query, (selected_start_date, selected_end_date, selected_model_run))

    # Fetch all rows
    rows = cursor.fetchall()

    csv_data = []
    latitudes, longitudes = get_latitudes_and_longitudes(provider_id, model_id, conn)

    if rows:
        for row in rows:
            start_date, end_date, interval, model_run, valid_dates, data = row

            for index, day_data in enumerate(data):
                current_date = valid_dates[index].astimezone(pytz.timezone('Europe/Ljubljana'))
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
        # Close the cursor and the connection
        cursor.close()
        return csv_data, interval
    else:
        # Close the cursor and the connection
        cursor.close()
        return None
