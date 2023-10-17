import csv
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def execute_sql_query(sql_query):
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

        # Execute the provided SQL query
        cursor.execute(sql_query)

        # Fetch one row as a tuple
        data = cursor.fetchone()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return data

    except Exception as e:
        print(f"Error: {e}")
        return None

def write_data_to_csv(data, file_path):
    try:
        with open(file_path, mode='w', newline='') as file:
            if data is None:
                return False  # No data to write

            writer = csv.writer(file)

            # Write data to the CSV file
            writer.writerow(data)

        return True  # Data was successfully written to the CSV file

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Define the SQL query to execute
    sql_query = """
    SELECT UNNEST(data) AS unnested_data
    FROM total_precipitation_icond2
    LIMIT 1;
    """

    # Call the function to execute the SQL query
    query_result = execute_sql_query(sql_query)

    if query_result is not None:
        # Specify the file path where the CSV will be saved
        csv_file_path = "output.csv"

        # Call the function to write query result to the CSV file
        success = write_data_to_csv(query_result, csv_file_path)

        if success:
            print(f"Query result successfully written to {csv_file_path}")
        else:
            print("Failed to write query result to CSV file.")
