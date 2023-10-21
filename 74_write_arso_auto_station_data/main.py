import os
from dotenv import load_dotenv
import csv
import requests
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql
import re
from datetime import datetime
import pytz
import logging
from logging.handlers import TimedRotatingFileHandler

# Load environment variables from .env
load_dotenv()

# Set up logging
log_dir = os.getenv("LOG_PATH_DIR")

if not log_dir:
    log_dir = "logs"

# Get the current date
current_date = datetime.now()
year, month, day = current_date.year, current_date.month, current_date.day

# Define the folder structure
log_year_dir = os.path.join(log_dir, str(year))
log_month_dir = os.path.join(log_year_dir, str(month))
log_day_dir = os.path.join(log_month_dir, str(day))

# Create the log directories if they don't exist
os.makedirs(log_day_dir, exist_ok=True)

# Define the custom log file name based on the year, month, and day
log_filename = os.path.join(log_day_dir, "daily_log.log")

# Configure logging with TimedRotatingFileHandler
handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d_%H-%M-%S.log"  # Include timestamp in log file name
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logging.getLogger('').addHandler(handler)

# Create a custom log formatter
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_formatter)

# Get database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# URLs to the XML files for stations
stations = [
    "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observationAms_si_latest.xml",
    "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_si_latest.xml",
]

# Function to extract temperature data from XML
def extract_temperature_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        metData_list = root.findall(".//metData")
        temperature_data = []
        for metData in metData_list:
            station_name = metData.find("domain_title").text
            temperature = metData.find("t").text
            valid_utc = metData.find("valid_UTC").text

            valid_utc = valid_utc.replace(" UTC", "")

            # Split the date and time components
            date_components, time_components = valid_utc.split(" ")

            # Split the date components
            day, month, year = map(int, date_components.split("."))

            # Split the time components
            hour, minute = map(int, time_components.split(":"))

            # Create a Python datetime object with UTC timezone
            valid_utc_datetime = datetime(year, month, day, hour, minute, tzinfo=pytz.utc)

            temperature_data.append([station_name, temperature, valid_utc_datetime])
        return temperature_data
    else:
        logging.error(f"Failed to fetch XML data from the URL: {url}. Status code: {response.status_code}")
        return []

import re

def format_station_name(station_name, is_auto_station):
    # Replace special characters and single whitespaces with a single underscore
    station_name = re.sub(r'[-;_\s]+', '_', station_name)

    # Remove all dots
    station_name = re.sub(r'\.', '', station_name)

    # Remove trailing underscores
    station_name = station_name.rstrip('_')

    # Convert to lowercase
    formatted_name = station_name.strip().lower()

    slashes_remove_formatted_name = formatted_name.replace("/", "_")

    # Add prefix based on the URL
    prefix = "auto" if is_auto_station else "obs"

    return f'"{prefix}_{slashes_remove_formatted_name}"'  # Quote the table name



# Connect to the database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Iterate through stations
for i, url in enumerate(stations):
    temperature_data = extract_temperature_data(url)

    # Determine if it's an auto station based on the index
    is_auto_station = (i == 0)

    for data in temperature_data:
        station_name = format_station_name(data[0], is_auto_station)  # Format the station name
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {station_name} (
            temperature DOUBLE PRECISION,
            valid_utc TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        temperature = data[1] if data[1] is not None else None
        valid_utc = data[2]

        # Check if the valid_utc value is available
        if valid_utc is not None:
            # Check if the valid_utc value already exists in the table
            check_query = sql.SQL(f"SELECT COUNT(*) FROM {station_name} WHERE valid_utc = %s;")
            cursor.execute(check_query, (valid_utc,))
            count = cursor.fetchone()[0]

            if count == 0:
                # No conflicts, insert the data with NULL for None values
                insert_query = sql.SQL(f"INSERT INTO {station_name} (temperature, valid_utc) VALUES ({'NULL' if temperature is None else temperature}, %s);")
                cursor.execute(insert_query, (valid_utc,))
                conn.commit()

# Close the database connection
conn.close()

# Close the logger when done
logging.shutdown()

logging.info("Temperature data for all stations with valid UTC has been successfully inserted into the database, and duplicates were ignored.")

