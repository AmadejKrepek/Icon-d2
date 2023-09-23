import csv
from datetime import datetime, timedelta
import re

def select_record_and_aggregate(cursor, table_name):
    try:
        # Query to retrieve the rows from the selected table
        cursor.execute(f"SELECT DISTINCT start_date, model_run FROM {table_name}")

        # Fetch the available records and model runs
        records_and_model_runs = cursor.fetchall()

        if not records_and_model_runs:
            print(f"No records found in table '{table_name}'.")
            return

        # Display available records and model runs
        print("Available records and model runs:")
        for i, (start_date, model_run) in enumerate(records_and_model_runs, start=1):
            print(f"{i}. Start Date: {start_date}, Model Run: {model_run}")

        try:
            record_choice = int(input("Enter the number of the record you want to choose: ")) - 1
            if 0 <= record_choice < len(records_and_model_runs):
                selected_record = records_and_model_runs[record_choice]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Ask the user to select a model run
        model_runs = [record[1] for record in records_and_model_runs if record[0] == selected_record[0]]
        print("Available model runs for the selected record:")
        for i, model_run in enumerate(model_runs, start=1):
            print(f"{i}. Model Run: {model_run}")

        try:
            model_run_choice = int(input("Enter the number of the model run you want to choose: ")) - 1
            if 0 <= model_run_choice < len(model_runs):
                selected_model_run = model_runs[model_run_choice]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return
        
        # Ask the user to select an aggregation method
        print("Available aggregations:")
        print("1. Max")
        print("2. Min")
        print("3. Average")

        try:
            aggregation_choice = int(input("Enter the number of the aggregation you want to perform: "))
            if aggregation_choice in [1, 2, 3]:
                selected_aggregation = aggregation_choice
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Aggregate the data based on the selected record, model run, and aggregation choice
        aggregated_data, start_date, end_date = aggregate_data(cursor, table_name, selected_record[0], selected_model_run, selected_aggregation)

        selected_date = selectTimeSeriesDates(start_date, end_date)

        filtered_data = filterDataBySelectedDate(aggregated_data, selected_date)

        # Define the file name where you want to write the filtered data
        output_file = "filtered_data.txt"  # You can change the file name and extension

        # Write the filtered data to the file
        with open(output_file, "w") as file:
            for record in filtered_data:
                file.write(str(record) + "\n")

        print(f"Filtered data has been written to {output_file}")

        if not aggregated_data:
            return

        # Write aggregated data to CSV file
        write_aggregated_data_to_csv(selected_record[0], selected_model_run, selected_aggregation, aggregated_data)

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)

def filterDataBySelectedDate(timestamped_data, selected_date):
    filtered_data = []
    for record in timestamped_data:
        for entry in record:
            entry_date_str = entry['date']
            entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d %H:%M:%S")
            if entry_date.date() == selected_date.date():
                filtered_data.append(entry)
    return filtered_data

def selectTimeSeriesDates(start_date, end_date):
    # Create a list of dates within the range
    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

    # Display the list of dates for user selection
    print("Select a date from the available options:")
    for idx, date in enumerate(date_range):
        print(f"{idx + 1}. {date.strftime('%Y-%m-%d')}")

    # User input to select a specific date
    selected_date_idx = int(input("Enter the number of the selected date: ")) - 1

    # Get the selected date
    selected_date = date_range[selected_date_idx]

    return selected_date

def createTimeStampedData(aggregated_data, start_date, interval):
    result = []
    current_date = start_date
    for data in aggregated_data:
        for value in data[3]:
            timestamped_values = []
            for v in value:
                timestamped_values.append({"date": current_date.strftime("%Y-%m-%d %H:%M:%S"), "value": v})
            result.append(timestamped_values)
            current_date += interval
    return result

def extract_data(aggregated_data):
    start_date = aggregated_data[0][0]
    end_date = aggregated_data[0][1]
    interval = aggregated_data[0][2]
    
    data = createTimeStampedData(aggregated_data, start_date, interval)
    return data, start_date, end_date

def aggregate_data(cursor, table_name, selected_record, selected_model_run, aggregation_choice):
    try:
        aggregation_sql = ""
        if aggregation_choice == 1:
            aggregation_sql = f"MAX(data) AS aggregated_data"
        elif aggregation_choice == 2:
            aggregation_sql = f"MIN(data) AS aggregated_data"
        elif aggregation_choice == 3:
            aggregation_sql = f"AVG(data) AS aggregated_data"

        # Modify the SQL query to include a GROUP BY clause
        cursor.execute(f"""
            SELECT start_date, end_date, interval, {aggregation_sql}
            FROM {table_name}
            WHERE start_date = %s AND model_run = %s
            GROUP BY start_date, end_date, interval
        """, (selected_record, selected_model_run))

        # Fetch aggregated data
        aggregated_data = cursor.fetchall()

        aggregated_data, start_date, end_date = extract_data(aggregated_data)

        return aggregated_data, start_date, end_date

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while aggregating data: {str(e)}"
        print(error_message)
        return None

def write_aggregated_data_to_csv(selected_record, selected_model_run, selected_aggregation, aggregated_data):
    try:
        # Prepare data for CSV
        csv_data = [[start_date, end_date, aggregated_value] for start_date, end_date, aggregated_value in aggregated_data]

        # Write data to CSV file
        output_file = f"aggregated_data_{selected_record}_{selected_model_run}_{selected_aggregation}.csv"
        with open(output_file, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Start Date", "End Date", "Aggregated Value"])  # CSV header
            csv_writer.writerows(csv_data)

        print(f"CSV file '{output_file}' created successfully.")

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred while writing data to CSV: {str(e)}"
        print(error_message)

def get_table_list(conn):
    try:
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

        # Close the cursor
        cursor.close()

        return [row[0] for row in table_names]

    except Exception as e:
        # Log the error and display a more informative message
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        return []

def select_table(conn):
    table_names = get_table_list(conn)
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


