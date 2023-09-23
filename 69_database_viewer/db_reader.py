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

def select_date_for_aggregation(data):
    try:
        # Get unique dates from the data
        unique_dates = list(set([row[0].date() for row in data]))

        if not unique_dates:
            print("No valid dates found in the data.")
            return None

        print("Available dates for aggregation:")
        for i, date in enumerate(unique_dates, start=1):
            print(f"{i}. {date}")

        try:
            date_index = int(input("Enter the number of the date you want to choose for aggregation: ")) - 1
            if 0 <= date_index < len(unique_dates):
                selected_date = unique_dates[date_index]
                return selected_date
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

def select_aggregation():
    print("Available aggregations:")
    print("1. Max")
    print("2. Min")
    print("3. Average")

    try:
        aggregation_choice = int(input("Enter the number of the aggregation you want to perform: "))
        if aggregation_choice in [1, 2, 3]:
            if aggregation_choice == 1:
                return "MAX"
            elif aggregation_choice == 2:
                return "MIN"
            elif aggregation_choice == 3:
                return "AVG"
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

def aggregate_data_by_date(data, selected_date, aggregation_choice):
    try:
        # Filter data for the selected date
        filtered_data = [row for row in data if row[0].date() == selected_date]

        if not filtered_data:
            print(f"No data found for the selected date: {selected_date}.")
            return None

        # Extract the values to be aggregated
        values_to_aggregate = [row[1] for row in filtered_data]

        # Perform aggregation (max, min, or average) on the values
        if aggregation_choice == "MAX":
            aggregated_value = max(values_to_aggregate)
        elif aggregation_choice == "MIN":
            aggregated_value = min(values_to_aggregate)
        elif aggregation_choice == "AVG":
            aggregated_value = sum(values_to_aggregate) / len(values_to_aggregate)
        else:
            print("Invalid aggregation choice.")
            return None

        return aggregated_value

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while aggregating data: {str(e)}"
        print(error_message)
        return None

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

        # Query to retrieve data from the selected table
        cursor.execute(f"SELECT start_date, end_date, interval, data FROM {table_name}")

        # Fetch all data
        data = cursor.fetchall()

        if not data:
            print("No data found in the selected table.")
            return

        # Append start_date and end_date with interval to every nested array in the "data" column
        for i in range(len(data)):
            start_date, end_date, interval, nested_data = data[i]
            current_date = start_date
            interval_seconds = int(interval.total_seconds())
            updated_nested_data = []
            for day_data in nested_data:
                current_date += timedelta(seconds=interval_seconds)
                updated_day_data = [current_date, *day_data]
                updated_nested_data.append(updated_day_data)
            data[i] = (start_date, end_date, updated_nested_data)

        selected_date = select_date_for_aggregation(data)
        if not selected_date:
            return

        aggregation_choice = select_aggregation()
        if not aggregation_choice:
            return

        # Aggregate data by the selected date and aggregation choice
        aggregated_value = aggregate_data_by_date(data, selected_date, aggregation_choice)

        if aggregated_value is not None:
            # Write data to CSV file
            with open(output_file, "w", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["Valid Date", f"Aggregated ({aggregation_choice}) Value"])  # CSV header
                csv_writer.writerow([selected_date, aggregated_value])  # Aggregated data row

            print(f"CSV file '{output_file}' created successfully.")

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
