import os
import psycopg2

def check_model_run_exists(table_name, model_run):
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
        print(f"Model run: {model_run}")
        print(f"Table name: {table_name}")
        # Check if a record with the same model_run exists
        cursor.execute(f"""
            SELECT model_run FROM "{table_name}"
            WHERE model_run = %s;
        """, (model_run,))

        existing_model_run = cursor.fetchone()
        print(f"Existing model run: {existing_model_run}")

        if existing_model_run:
            print("Record with the same model_run already exists. Returning False.")
            return True
        else:
            print("No record with the same model_run found. Returning True.")
            return False

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error here or re-raise it if needed
        raise