import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


async def check_model_run_exists(db_pool, table_name, model_run, start_date):
    try:
        formatted_start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Started checking if model run already exists in the database with table_name: {table_name}, "
                    f"model_rum: {model_run} and start_date: {formatted_start_date}")
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                logger.info(f"Model run: {model_run}")
                logger.info(f"Table name: {table_name}")

                # Check if a record with the same model_run and start_date exists
                await cursor.execute(f"""
                    SELECT model_run, start_date FROM "{table_name}"
                    WHERE model_run = %s AND start_date = %s;
                """, (model_run, start_date))

                existing_record = await cursor.fetchone()
                logger.info(f"Existing record (model_run, start_date): {existing_record}")

                if existing_record:
                    existing_model_run, existing_start_date = existing_record
                    logger.info(f"Existing start date: {start_date}")
                    time_difference = existing_start_date - start_date
                    duration_to_compare = timedelta(minutes=1)
                    logger.info(f"TIme difference: {time_difference}")
                    if time_difference < duration_to_compare:
                        logger.info("Record with the same model_run and start_date exists.")
                        return True
                    else:
                        logger.info("Record with the same model_run and start_date does not exist!")
                        return False

    except Exception as e:
        logger.error(f"Error while checking if model run exists in database: {e}")
        raise ValueError(f"{e}")
