# Function to fetch data from the database based on 'parameter' and 'model'
import ast
import datetime
import json
from datetime import timedelta

from features.database.db_connector import create_db_connection


# Custom JSON encoder to handle timedelta serialization

def select_query_parameter_model(parameter):
    # Connect to the database
    conn = create_db_connection()

    # Use a cursor to execute a query
    with conn.cursor() as cursor:
        # Modify the query based on your database schema and structure
        query = f'SELECT data, start_date, end_date, interval, model_run FROM "{parameter}" LIMIT 1'
        cursor.execute(query)
        result = cursor.fetchone()

    # Close the database connection
    conn.close()

    data = {
        "data": result[0],
        "start_date": result[1].strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": result[2].strftime("%Y-%m-%d %H:%M:%S"),
        "interval": str(result[3]),
        "model_run": int(result[4])
    }
    # Preprocess the data by removing the outer square brackets
    # Parse the 'data' column as a Python object
    try:
        return data, parameter
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing data column: {e}")
    return result
