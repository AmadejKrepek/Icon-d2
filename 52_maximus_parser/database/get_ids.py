import os
import psycopg2
import sys

def get_provider_id(provider_name):
    try:
        # Access the environment variables
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Check if the provider exists in the database
        cursor.execute("SELECT id FROM provider WHERE name = %s", (provider_name,))
        provider_id = cursor.fetchone()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return provider_id

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def get_model_id(model_name):
    try:
        # Access the environment variables
        DB_USERNAME = os.getenv("DB_USERNAME")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Check if the model exists in the database
        cursor.execute("SELECT id FROM model WHERE name = %s", (model_name,))
        model_id = cursor.fetchone()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return model_id

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)