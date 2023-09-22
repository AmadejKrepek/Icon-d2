import psycopg2
import csv
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
def get_table_list():
    try:


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

        # Query to retrieve table list
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)

        # Fetch all table names
        table_names = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        return [row[0] for row in table_names]

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return []

def select_table():
    table_names = get_table_list()
    if not table_names:
        print("No tables found in the database.")
        return

    print("Available tables:")
    for i, table in enumerate(table_names, start=1):
        print(f"{i}. {table}")

    try:
        table_index = int(input("Enter the number of the table you want to choose: ")) - 1
        if 0 <= table_index < len(table_names):
            return table_names[table_index]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def select_interval(table_name):
    try:
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

        # Query to retrieve start_date, end_date, and model_run from the selected table,
        # and order them by start_date in descending order (newest first)
        cursor.execute(f"""
            SELECT start_date, end_date, model_run
            FROM {table_name}
            ORDER BY start_date DESC;
        """)

        # Fetch all intervals
        intervals = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        if not intervals:
            print("No intervals found in the selected table.")
            return None

        # Create a dictionary to store unique intervals based on start_date
        unique_intervals = {}

        # Iterate through intervals and keep only the latest unique ones
        for interval in intervals:
            start_date, end_date, model_run = interval
            if start_date not in unique_intervals or unique_intervals[start_date] < end_date:
                unique_intervals[start_date] = end_date, model_run

        # Convert the dictionary back to a list of tuples
        unique_intervals_list = [(start_date, end_date, model_run) for start_date, (end_date, model_run) in unique_intervals.items()]

        print("Available intervals (newest first, duplicates removed based on start_date):")
        for i, (start_date, end_date, model_run) in enumerate(unique_intervals_list, start=1):
            print(f"{i}. Start Date: {start_date}, End Date: {end_date}, Model Run: {model_run}")

        try:
            interval_index = int(input("Enter the number of the interval you want to choose: ")) - 1
            if 0 <= interval_index < len(unique_intervals_list):
                return unique_intervals_list[interval_index]
            else:
                print("Invalid selection.")
                return None
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return None

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return None



def create_csv(table_name, interval):
    try:
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

        # Query to retrieve data for the selected interval
        cursor.execute(f"""
            SELECT *
            FROM {table_name}
            WHERE start_date = %s AND end_date = %s AND model_run = %s;
        """, interval)

        # Fetch all data for the interval
        data = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        if not data:
            print("No data found for the selected interval.")
            return

        # Define the CSV file name
        csv_file_name = f"{table_name}_{interval[0]}_{interval[1]}_{interval[2]}.csv"

        # Write the data to a CSV file
        with open(csv_file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([desc[0] for desc in cursor.description])
            csv_writer.writerows(data)

        print(f"CSV file '{csv_file_name}' has been created.")

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)

if __name__ == "__main__":
    selected_table = select_table()
    if selected_table:
        selected_interval = select_interval(selected_table)
        if selected_interval:
            create_csv(selected_table, selected_interval)
