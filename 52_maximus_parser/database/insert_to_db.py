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

def extract_dates(data):
    # Extract start_date from the first row of the ValidDate column
    start_date = data['ValidDate'].iloc[0]
    
    # Extract end_date from the last row of the ValidDate column
    end_date = data['ValidDate'].iloc[-1]
    
    return start_date, end_date

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
    start_date = second_to_last_df['ValidDate'].iloc[0]

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

def insert_parameter_data(provider_id, model_id, parameter_name, data_list, model_run, parameter_table_name):
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

        # Initialize combined_data_list as an empty list
        combined_data_list = []

        # Initialize start_date and end_date
        start_date = None
        end_date = None            

        # Iterate through data_list and append parameter values for each DataFrame as a nested list
        for data_item in data_list:
            current_start_date, current_end_date = extract_dates(data_item[0])
            parameter_values = data_item[0][parameter_name].tolist()
            combined_data_list.append(parameter_values)

            # Update start_date with the first start_date in the loop
            if start_date is None:
                start_date = current_start_date
            
            # Update end_date with the current_end_date in each iteration
            end_date = current_end_date

        interval = get_interval_from_latest_df(data_list)

        # Insert the entire dataset into the new table
        cursor.execute(sql.SQL("""
            INSERT INTO {}
            (provider_id, model_id, model_run, {}, start_date, end_date, interval)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """).format(sql.Identifier(parameter_table_name), sql.Identifier(parameter_name)), (
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
