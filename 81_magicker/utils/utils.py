import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
# Load environment variables
db_params_stations = {
    "dbname": os.getenv("STATIONS_DB_NAME"),
    "user": os.getenv("STATIONS_DB_USERNAME"),
    "password": os.getenv("STATIONS_DB_PASSWORD"),
    "host": os.getenv("STATIONS_DB_HOST"),
    "port": os.getenv("STATIONS_DB_PORT")
}

db_params_test = {
    "dbname": os.getenv("TEST_DB_NAME"),
    "user": os.getenv("TEST_DB_USERNAME"),
    "password": os.getenv("TEST_DB_PASSWORD"),
    "host": os.getenv("TEST_DB_HOST"),
    "port": os.getenv("TEST_DB_PORT")
}


def establish_stations_database_connection():
    try:
        conn = psycopg2.connect(**db_params_stations)
        return conn
    except Exception as e:
        print(f"Error establishing a database connection: {e}")
        return None


def establish_icon_d2_database_connection():
    try:
        conn = psycopg2.connect(**db_params_test)
        return conn
    except Exception as e:
        print(f"Error establishing a database connection: {e}")
        return None
