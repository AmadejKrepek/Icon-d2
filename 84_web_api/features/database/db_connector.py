# db_connector.py

from psycopg2 import connect
from dotenv import load_dotenv
import os


def create_db_connection():
    # Load environment variables from .env
    load_dotenv()

    # Database connection information
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Create a PostgreSQL connection
    conn = connect(
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    return conn
