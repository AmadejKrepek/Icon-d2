import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
import os
import pandas as pd
import logging
import pytz
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

def extract_dates(data):
    # Extract start_date from the first row of the ValidDate column
    start_date = data['ValidDate'].iloc[0]
    
    # Extract end_date from the last row of the ValidDate column
    end_date = data['ValidDate'].iloc[-1]
    
    return start_date, end_date

def replaceZeroValuesWithNull(combined_data_list):
    result = [[None if value <= 0.0 else value for value in nested_array] for nested_array in combined_data_list]
    return result

def get_interval_from_latest_df(data_list):
    # Check if data_list has at least two elements
    if len(data_list) < 2:
        return None

    # Get the second-to-last and last DataFrames in data_list
    second_to_last_df = data_list[-2][0]
    latest_df = data_list[-1][0]

    # Sort both DataFrames by the 'ValidDate' column
    second_to_last_df = second_to_last_df.sort_values(by='ValidDate')
    latest_df = latest_df.sort_values(by='ValidDate')

    # Extract start_date from the first row of ValidDate column in the second-to-last DataFrame
    start_date = second_to_last_df['ValidDate'].iloc[-1]

    # Extract end_date from the first row of ValidDate column in the last DataFrame
    end_date = latest_df['ValidDate'].iloc[0]

    # Calculate interval as the difference between end_date and start_date
    interval = end_date - start_date

    return interval

def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
         flat_list.extend(row)
    return flat_list

def insert_parameter_data(provider_id, model_id, parameter_name, data_list, model_run, parameter_table_name, start_date, end_date):
    try:
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        logger.info("Establishing a connection to the PostgreSQL database...")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        logger.info("Connection to PostgreSQL established.")

        cursor = conn.cursor()

        combined_data_list = []

        for data_item in data_list:
            parameter_values = data_item[0][parameter_name].tolist()
            combined_data_list.append(parameter_values)

        interval = get_interval_from_latest_df(data_list)
        if "temperature" not in parameter_name.lower():
            combined_data_list = replaceZeroValuesWithNull(combined_data_list)

        insert_data_sql = sql.SQL("""
            INSERT INTO {}
            (provider_id, model_id, model_run, data, start_date, end_date, interval)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """).format(sql.Identifier(parameter_table_name))

        # Execute the SQL statement
        cursor.execute(insert_data_sql, (
            provider_id,
            model_id,
            model_run,
            combined_data_list,  # Pass the entire nested list as a parameter
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
