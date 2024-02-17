import logging
import sys

import aiopg
from psycopg2 import connect, OperationalError
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)


def create_db_connection():
    try:
        logger.info(f"Connecting to database...")
        # Database connection information
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        conn = connect(
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )

        return conn
    except OperationalError as e:
        # Log the error
        logger.error(f"Error connecting to the database: {e}")
        # Optionally raise a custom exception or return None
        sys.exit(1)


async def create_db_connection_async():
    try:
        logger.info(f"Connecting to asynchronus database...")
        # Load environment variables from .env
        load_dotenv()

        # Database connection information
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        # Create an asynchronous PostgreSQL connection
        dsn = f"dbname={DB_NAME} user={DB_USERNAME} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
        pool = await aiopg.create_pool(dsn)

        return pool


    except TimeoutError as te:
        logger.error(f"TimeoutError connecting to the database: {te}")

        sys.exit(1)


    except Exception as e:

        logger.error(f"Error connecting to the database: {e}")

        sys.exit(1)
