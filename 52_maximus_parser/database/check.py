import logging
from datetime import timedelta


async def check_model_run_exists(db_pool, table_name, model_run, start_date):
    try:
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                print(f"Model run: {model_run}")
                print(f"Table name: {table_name}")

                # Check if a record with the same model_run and start_date exists
                await cursor.execute(f"""
                    SELECT model_run, start_date FROM "{table_name}"
                    WHERE model_run = %s AND start_date = %s;
                """, (model_run, start_date))

                existing_record = await cursor.fetchone()
                print(f"Existing record (model_run, start_date): {existing_record}")

                if existing_record:
                    existing_model_run, existing_start_date = existing_record
                    # formatted_timestamp = existing_start_date.strftime("%Y-%m-%d %H:%M:%S")
                    # formatted_timestamp = Timestamp(formatted_timestamp)

                    print(f"Existing start date: {start_date}")
                    time_difference = existing_start_date - start_date
                    duration_to_compare = timedelta(minutes=1)
                    print(f"TIme difference: {time_difference}")
                    if time_difference < duration_to_compare:
                        print("Record with the same model_run and start_date exists.")
                        return True
                    else:
                        print("Record with the same model_run and start_date does not exist!")
                        return False

    except Exception as e:
        print(f"Error: {e}")
        logging.error(e)
        # Handle the error here or re-raise it if needed
        raise ValueError(f"{e}")
