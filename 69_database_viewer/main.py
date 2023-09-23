from db_reader import select_record_and_aggregate, select_table
import psycopg2
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Access the environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

try:
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )

    # Call the select_table function to choose a table
    selected_table = select_table(conn)

    if selected_table:
        # Call the select_record_and_aggregate function to perform record selection and aggregation
        select_record_and_aggregate(conn.cursor(), selected_table)

    # Close the connection
    conn.close()

except Exception as e:
    # Log the error and display a more informative message
    error_message = f"An error occurred: {str(e)}"
    print(error_message)
