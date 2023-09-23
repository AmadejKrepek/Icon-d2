from datetime import timedelta
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

def select_record(cursor, table_name):
    try:
        # Query to retrieve the rows from the selected table
        cursor.execute(f"SELECT DISTINCT start_date, end_date, model_run FROM {table_name} ORDER BY start_date DESC")

        # Fetch all available rows
        rows = cursor.fetchall()

        if not rows:
            print(f"No rows found in table '{table_name}'.")
            return None

        print("Available rows:")
        for i, (start_date, end_date, model_run) in enumerate(rows, start=1):
            print(f"{i}. Start Date: {start_date}, End Date: {end_date}, Model Run: {model_run}")

        try:
            row_index = int(input("Enter the number of the row you want to choose: ")) - 1
            if 0 <= row_index < len(rows):
                selected_row = rows[row_index]
                start_date, end_date, model_run = selected_row
                print("Selected row:")
                print(f"Start Date: {start_date}")
                print(f"End Date: {end_date}")
                print(f"Model Run: {model_run}")
                return start_date, end_date, model_run
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

def replace_none_with_zero(data):
    # Replace None (null) values with 0.0 in the data
    return [[0.0 if value is None or value == 'null' else value for value in row] for row in data]

def select_aggregation():
    print("Available aggregations:")
    print("1. Max")
    print("2. Min")
    print("3. Average")

    try:
        aggregation_choice = int(input("Enter the number of the aggregation you want to perform: "))
        if aggregation_choice in [1, 2, 3]:
            return aggregation_choice
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def aggregate_data(cursor, table_name, aggregation_choice):
    try:
        aggregation_sql = ""
        if aggregation_choice == 1:
            aggregation_sql = f"MAX(value) AS aggregated_data"
        elif aggregation_choice == 2:
            aggregation_sql = f"MIN(value) AS aggregated_data"
        elif aggregation_choice == 3:
            aggregation_sql = f"AVG(value) AS aggregated_data"

        # Query to retrieve aggregated data from the selected table, unnesting the 'data' column
        cursor.execute(f"""
            SELECT {aggregation_sql}
            FROM {table_name}, unnest(data) as t (value);
        """)

        # Fetch aggregated data
        aggregated_data = cursor.fetchall()

        return aggregated_data

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while aggregating data: {str(e)}"
        print(error_message)
        return None

def read_data_and_generate_csv(table_name, parameter_name, output_file, aggregation_choice):
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

        selected_row = select_record(cursor, table_name)
        if not selected_row:
            return

        # Aggregate the data based on the selected aggregation choice
        aggregated_data = aggregate_data(cursor, table_name, aggregation_choice)

        if not aggregated_data:
            print("No data found for the selected aggregation.")
            return

        # Replace None (null) values with 0.0
        aggregated_data = replace_none_with_zero(aggregated_data)

        # Prepare data for CSV
        csv_data = [[aggregated_value] for aggregated_value in aggregated_data]

        # Write data to CSV file
        with open(output_file, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([parameter_name])  # CSV header
            csv_writer.writerows(csv_data)

        print(f"CSV file '{output_file}' created successfully.")

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
