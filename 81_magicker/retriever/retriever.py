from psycopg2 import sql


def get_tables_with_prefix(conn, prefix):
    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Use the information_schema to get a list of all tables with the specified prefix
    query = sql.SQL("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE %s
    """)
    cursor.execute(query, (f'{prefix}%',))

    # Fetch the results
    results = cursor.fetchall()

    # Close the cursor
    cursor.close()

    return results
