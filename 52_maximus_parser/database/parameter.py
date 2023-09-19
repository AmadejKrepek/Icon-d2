import psycopg2
from psycopg2 import sql
import logging
import os

# Initialize the logger
logger = logging.getLogger(__name__)

# Function to create a new table based on the parameter name
def create_parameter_table(parameter_table_name, parameter_name):
    # Connect to the database using environment variables for credentials
    try:
        # Access the environment variables for database credentials
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        # Create a connection to the database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        cursor = conn.cursor()

        # Create the SQL statement for table creation
        create_table_sql = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}
            (
                id SERIAL PRIMARY KEY,
                provider_id VARCHAR,
                model_id VARCHAR,
                model_run INT,
                {} DOUBLE PRECISION[],
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                interval INTERVAL
            )
        """).format(sql.Identifier(parameter_table_name), sql.Identifier(parameter_name))

        # Execute the SQL statement
        cursor.execute(create_table_sql)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        logger.info(f"Created table '{parameter_table_name}'.")
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
    finally:
        if conn is not None:
            conn.close()
