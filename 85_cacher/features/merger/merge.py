import datetime
from datetime import timedelta

import pytz
from psycopg2 import sql

from features.merger.latitude import get_latitudes_and_longitudes


def merge_lat_lon_with_grid_data(conn, provider_id, model_id, data):
    try:
        csv_data = []
        latitudes, longitudes = get_latitudes_and_longitudes(provider_id, model_id, conn)

        # Convert interval string to timedelta
        interval_str = data["interval"]
        interval = datetime.datetime.strptime(interval_str, "%H:%M:%S").time()
        # Convert start_date and end_date strings to datetime objects
        start_date_str = data["start_date"]
        end_date_str = data["end_date"]

        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")

        # Check if the interval is 2 hours and adjust it to 1 hour if necessary.
        if interval == timedelta(hours=2):
            interval = timedelta(hours=1)

        current_date = start_date
        interval_seconds = interval.hour * 3600 + interval.minute * 60 + interval.second

        for day_data in data['data']:
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
    except Exception as e:
        return None

    return csv_data, interval
