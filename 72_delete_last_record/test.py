import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def delete_last_record(table_name):
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

        # Determine the primary key of the table (assuming it's "id")
        primary_key = "id"

        # Get the ID of the last record in the table
        cursor.execute(f"SELECT MAX({primary_key}) FROM {table_name};")
        last_record_id = cursor.fetchone()[0]

        # Delete the last record
        cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key} = %s;", (last_record_id,))

        # Commit the changes
        conn.commit()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        print(f"Last record in table '{table_name}' deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Specify the table name from which you want to delete the last record
    table_name_to_modify = "2_metre_temperature_icond2"

    delete_last_record(table_name_to_modify)
