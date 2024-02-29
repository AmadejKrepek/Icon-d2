import logging
from datetime import timedelta

from psycopg2 import sql


logger = logging.getLogger(__name__)


def get_model_name(model_id, provider_id, conn):
    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Define the table name as an SQL Identifier
        table_identifier = sql.Identifier("model")

        # Query the data from the specified table
        query = sql.SQL("SELECT name FROM {} "
                        "WHERE id = %s AND provider_id = %s "
                        ).format(table_identifier)

        # Execute the SQL query with the provided parameters
        cursor.execute(query, (model_id, provider_id,))

        # Fetch the first row (assuming there's only one result, change accordingly if needed)
        row = cursor.fetchone()

        # Close the cursor
        cursor.close()

        # Check if a row is found
        if row:
            # The 'name' column is fetched from the row
            name = row[0]
            return name
        else:
            # Return None or handle the case where no row is found
            return None
    except Exception as e:
        logger.error(f"{e}")
