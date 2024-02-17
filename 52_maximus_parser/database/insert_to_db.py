from psycopg2 import sql
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


def replaceZeroValuesWithNull(combined_data_list):
    try:
        logger.info(f"Replacing zero values with null values")
        result = [[None if value <= 0.0 else value for value in nested_array] for nested_array in combined_data_list]
        logger.info(f"Finished replacing zero values with null values")
        return result
    except Exception as e:
        logger.error(f"Error while replacing zero values with null: {e}")


def get_interval_from_latest_df(data_list):
    try:
        logger.info(f"Started getting interval from latest dataframe")
        # Check if data_list has at least two elements
        if len(data_list) < 2:
            logger.warning(f"Data list should have at least two elements to calculate interval from latest df")
            return None

        # Get the second-to-last and last DataFrames in data_list
        second_to_last_df = data_list[-2][0]
        latest_df = data_list[-1][0]

        # Sort both DataFrames by the 'ValidDate' column
        second_to_last_df = second_to_last_df.sort_values(by='ValidDate')
        latest_df = latest_df.sort_values(by='ValidDate')

        # Extract start_date from the first row of ValidDate column in the second-to-last DataFrame
        start_date = second_to_last_df['ValidDate'].iloc[-1]

        # Extract end_date from the first row of ValidDate column in the last DataFrame
        end_date = latest_df['ValidDate'].iloc[0]

        # Calculate interval as the difference between end_date and start_date
        interval = end_date - start_date

        logger.info(f"Finished getting interval from latest dataframe")
        return interval

    except Exception as e:
        logger.error(f"Error while getting interval from latest dataframe: {e}")


async def insert_parameter_data(db_pool, provider_id, model_id, parameter_name, data_list, model_run,
                                parameter_table_name, start_date,
                                end_date):
    try:
        logger.info(f"Started insterting parameter data with parameter_name: {parameter_name}, parameter_table_name: "
                    f"{parameter_table_name}, model_run: {model_run}, start_date: {start_date} and end_date: {end_date}")
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                logger.info("Connection to PostgreSQL established.")

                combined_data_list = []

                for data_item in data_list:
                    parameter_values = data_item[0][parameter_name].tolist()
                    combined_data_list.append(parameter_values)

                interval = get_interval_from_latest_df(data_list)
                if "temperature" not in parameter_name.lower():
                    combined_data_list = replaceZeroValuesWithNull(combined_data_list)

                insert_data_sql = sql.SQL("""
                    INSERT INTO {}
                    (provider_id, model_id, model_run, data, start_date, end_date, interval)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """).format(sql.Identifier(parameter_table_name))

                # Execute the SQL statement
                await cursor.execute(insert_data_sql, (
                    provider_id,
                    model_id,
                    model_run,
                    combined_data_list,  # Pass the entire nested list as a parameter
                    start_date,
                    end_date,
                    interval
                ))

                logger.info(
                    f"Data for parameter '{parameter_name}' inserted successfully into table '{parameter_table_name}'.")

    except Exception as e:
        logger.error(f"Error while inserting parameter data: {e}")
