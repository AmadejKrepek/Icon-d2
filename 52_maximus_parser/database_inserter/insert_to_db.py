import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

def extract_dates_interval(data):
    logger.info("Extracting dates and interval...")
    # Extract start_date from the first row of valid_date column
    start_date = data['ValidDate'].iloc[0]
    
    # Extract end_date from the last row of valid_date column
    end_date = data['ValidDate'].iloc[-1]
    
    # Calculate interval as the difference between consecutive rows of valid_date
    interval = (data['ValidDate'] - data['ValidDate'].shift()).iloc[1]
    
    return start_date, end_date, interval

def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
         flat_list.extend(row)
    return flat_list

def insert_parameter_data(parameter_name, data_list):
    try:
        # Access the environment variables
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        logger.info("Establishing a connection to the PostgreSQL database...")
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        logger.info("Connection to PostgreSQL established.")

        # Create a cursor object
        cursor = conn.cursor()

        # Extract start_date, end_date, and interval
        start_date, end_date, interval = extract_dates_interval(data_list[0][0])

        # Create a new table based on the parameter name
        parameter_table_name = parameter_name.replace(" ", "_").lower()
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}
            (
                id SERIAL PRIMARY KEY,
                {} DOUBLE PRECISION[],
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                interval INTERVAL
            )
        """).format(sql.Identifier(parameter_table_name), sql.Identifier(parameter_name)))

        logger.info(f"Created table '{parameter_table_name}'.")

        # Insert data into the new table
        for data_item in data_list:
            parameter_df = data_item[0]

            parameter_values = parameter_df[parameter_name]  # Convert Series to a list

            cursor.execute(sql.SQL("""
                INSERT INTO {}
                ({}, start_date, end_date, interval)
                VALUES (%s, %s, %s, %s)
            """).format(sql.Identifier(parameter_table_name), sql.Identifier(parameter_name)), (
                parameter_values,
                start_date,
                end_date,
                interval
            ))

        conn.commit()

        logger.info(f"Data for parameter '{parameter_name}' inserted successfully into table '{parameter_table_name}'.")

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error: {e}")
