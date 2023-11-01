import os
import csv
import psycopg2
from psycopg2 import sql
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Get database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Connect to the database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# List of tables in the database
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = [table[0] for table in cursor.fetchall()]

# User selects a table
print("Select a table:")
for i, table in enumerate(tables):
    print(f"{i + 1}. {table}")

table_index = int(input("Enter the number of the table you want to select: ")) - 1

if 0 <= table_index < len(tables):
    selected_table = tables[table_index]
    print(f"You selected the '{selected_table}' table.")
else:
    print("Invalid table selection. Exiting.")
    conn.close()
    exit()

# Display the last 50 records from the selected table
cursor.execute(f"SELECT * FROM {selected_table} ORDER BY valid_utc DESC LIMIT 50;")
records = cursor.fetchall()

print("Last 50 records:")
for i, record in enumerate(records):
    print(f"{i + 1}. {record}")

# User selects a record
record_index = int(input("Enter the number of the record you want to export to a CSV file: ")) - 1

if 0 <= record_index < len(records):
    selected_record = records[record_index]

    # Create a "data" folder if it doesn't exist
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)

    csv_filename = f"{data_folder}/{selected_table}_record_{record_index + 1}.csv"

    # Write the selected record to a CSV file in the "data" folder
    with open(csv_filename, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["temperature", "valid_utc"])
        csv_writer.writerow(selected_record)

    print(f"The selected record has been written to '{csv_filename}'.")
else:
    print("Invalid record selection. Exiting.")

# Close the database connection
conn.close()
