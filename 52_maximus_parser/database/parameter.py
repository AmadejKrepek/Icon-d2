from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)


async def create_parameter_table(db_pool, parameter_table_name):
    # Connect to the database using environment variables for credentials
    try:
        logger.info(f"Started creating parameter table with parameter_table_name: {parameter_table_name}")
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Create the SQL statement for table creation with a dynamic table name
                create_table_sql = sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {}
                    (
                        id SERIAL PRIMARY KEY,
                        provider_id VARCHAR,
                        model_id VARCHAR,
                        model_run INT,
                        data REAL[][],
                        start_date TIMESTAMPTZ,
                        end_date TIMESTAMPTZ,
                        interval INTERVAL
                    )
                """).format(sql.Identifier(parameter_table_name))

                # Execute the SQL statement
                await cursor.execute(create_table_sql)

                logger.info(f"Created parameter table '{parameter_table_name}'.")
    except Exception as e:
        logger.error(f"Error creating parameter table: {str(e)}")
