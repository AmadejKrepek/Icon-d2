from datetime import timedelta
import os
import psycopg2

def check_model_run_exists(table_name, model_run, start_date):
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

        # Check if a record with the same model_run and start_date exists
        cursor.execute(f"""
            SELECT model_run, start_date FROM "{table_name}"
            WHERE model_run = %s AND start_date = %s;
        """, (model_run, start_date))

        existing_record = cursor.fetchone()
        print(f"Existing record (model_run, start_date): {existing_record}")

        if existing_record:
            existing_model_run, existing_start_date = existing_record
            #formatted_timestamp = existing_start_date.strftime("%Y-%m-%d %H:%M:%S")
            # formatted_timestamp = Timestamp(formatted_timestamp)

            print(f"Existing start date: {start_date}")
            time_difference = existing_start_date - start_date
            duration_to_compare = timedelta(minutes=1)
            print(f"TIme difference: {time_difference}")
            if time_difference < duration_to_compare:
                print("Record with the same model_run and start_date exists.")
                return True
            else:
                print("Record with the same model_run and start_date does not exist!")
                return False
            
        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        # Handle the error here or re-raise it if needed
        raise ValueError(f"{e}")