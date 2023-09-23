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

def append_interval_to_nested_arrays(data):
    try:
        for i in range(len(data)):
            start_date, end_date, interval, nested_data = data[i]
            current_date = start_date
            interval_seconds = int(interval.total_seconds())
            updated_nested_data = []
            for _ in range(len(nested_data)):
                updated_day_data = [current_date, *nested_data[_]]
                updated_nested_data.append(updated_day_data)
                current_date += timedelta(seconds=interval_seconds)
            data[i] = (start_date, end_date, interval, updated_nested_data)

        return data

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return None

def aggregate_data_by_date(data, selected_date):
    try:
        # Filter data for the selected date
        filtered_data = [row for row in data if row[0].date() == selected_date]

        if not filtered_data:
            print(f"No data found for the selected date: {selected_date}.")
            return None

        # Extract the values to be aggregated
        values_to_aggregate = [row[3] for row in filtered_data]

        if not values_to_aggregate:
            print(f"No values found for aggregation on date: {selected_date}.")
            return None

        # Initialize aggregated values with the first coordinate values
        aggregated_values = values_to_aggregate[0]

        # Iterate through the coordinates and aggregate
        for values in values_to_aggregate[1:]:
            for i, value in enumerate(values):
                aggregated_values[i] += value

        return aggregated_values

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while aggregating data: {str(e)}"
        print(error_message)
        return None

def write_aggregated_data_to_csv(selected_date, aggregated_values, output_file):
    try:
        # Prepare data for CSV
        data_to_write = [selected_date] + aggregated_values

        # Write data to CSV file
        with open(output_file, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Date", "Aggregated_Values"])  # CSV header
            csv_writer.writerow(data_to_write)

        print(f"CSV file '{output_file}' created successfully.")

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while writing data to CSV: {str(e)}"
        print(error_message)

def read_data_and_generate_csv(table_name, output_file):
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

        # Query to retrieve data for the selected table
        cursor.execute(f"SELECT start_date, end_date, interval, data FROM {table_name}")

        # Fetch all data
        data = cursor.fetchall()

        if not data:
            print("No data found in the selected table.")
            return

        # Append interval to nested arrays
        data = append_interval_to_nested_arrays(data)

        if not data:
            print("Error occurred while appending interval to nested arrays.")
            return

        # Get unique dates from the data
        unique_dates = set(row[0].date() for row in data)

        if not unique_dates:
            print("No dates found in the data.")
            return

        # Display available dates for aggregation
        print("Available dates for aggregation:")
        for i, date in enumerate(unique_dates, start=1):
            print(f"{i}. {date}")

        # Ask the user to select a date
        try:
            date_choice = int(input("Enter the number of the date you want to choose for aggregation: "))
            if 1 <= date_choice <= len(unique_dates):
                selected_date = list(unique_dates)[date_choice - 1]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Aggregate data for the selected date
        aggregated_values = aggregate_data_by_date(data, selected_date)

        if not aggregated_values:
            print("Error occurred while aggregating data.")
            return

        # Write aggregated data to CSV file
        write_aggregated_data_to_csv(selected_date, aggregated_values, output_file)

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
