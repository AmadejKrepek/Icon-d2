import os
from dotenv import load_dotenv
import csv
import requests
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2 import sql
import re

# Load environment variables from .env
load_dotenv()

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
            temperature_data.append([station_name, temperature, valid_utc])
        return temperature_data
    else:
        print(f"Failed to fetch XML data from the URL: {url}. Status code: {response.status_code}")
        return []

# Function to clean and format the station name
def format_station_name(station_name):
    # Convert to lowercase and replace spaces with underscores
    return re.sub(r'\s+', '_', station_name.strip().lower())

# Connect to the database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Extract temperature data for each station and create a separate table for each with its 'station_name'
for url in stations:
    temperature_data = extract_temperature_data(url)

    for data in temperature_data:
        station_name = format_station_name(data[0])  # Format the station name
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

        # Check if the valid_utc value already exists in the table
        check_query = sql.SQL(f"SELECT COUNT(*) FROM {station_name} WHERE valid_utc = to_timestamp('{valid_utc}', 'DD.MM.YYYY HH24:MI:SS') AT TIME ZONE 'UTC';")
        cursor.execute(check_query)
        count = cursor.fetchone()[0]

        if count == 0:
            # No conflicts, insert the data
            insert_query = sql.SQL(f"INSERT INTO {station_name} (temperature, valid_utc) VALUES ({temperature}, to_timestamp('{valid_utc}', 'DD.MM.YYYY HH24:MI:SS') AT TIME ZONE 'UTC');")
            cursor.execute(insert_query)
            conn.commit()

# Close the database connection
conn.close()

print("Temperature data for all stations with valid UTC has been successfully inserted into the database, and duplicates were ignored.")
