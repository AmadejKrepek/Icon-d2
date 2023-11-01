import csv
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Get database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Open the input CSV file for reading
with open('all_stations_data.csv', 'r') as input_file:
    csvreader = csv.reader(input_file)
    
    # Skip the header row
    next(csvreader)
    
    # Create a database connection
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Create the "basic" table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS basic (
            id SERIAL PRIMARY KEY,
            station_name TEXT,
            latitude NUMERIC,
            longitude NUMERIC,
            altitude NUMERIC
        )
    ''')
    conn.commit()

    # Insert data into the "basic" table
    for row in csvreader:
        station_name = row[0]
        latitude = row[1]
        longitude = row[2]
        altitude = row[3]
        
        cur.execute('INSERT INTO basic (station_name, latitude, longitude, altitude) VALUES (%s, %s, %s, %s)', (station_name, latitude, longitude, altitude))
        conn.commit()

    # Close the database connection
    conn.close()
