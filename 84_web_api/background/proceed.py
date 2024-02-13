import logging
import time
from datetime import datetime, timedelta

from background.task import store_last_records, get_last_records
from utils.processor import process_last_images

logger = logging.getLogger(__name__)


def get_next_schedule_time(schedule):
    current_time = datetime.now()
    next_scheduled_time = None
    min_time_difference = float('inf')

    for schedule_time in schedule:
        hour, minute = schedule_time
        scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        time_difference = (scheduled_time - current_time).total_seconds()

        if time_difference < min_time_difference:
            min_time_difference = time_difference
            next_scheduled_time = scheduled_time

    return next_scheduled_time.hour, next_scheduled_time.minute if next_scheduled_time else (0, 0)


async def cache_data(future_days, interval_hours, past_days, cache, parameters):
    for parameter in [param for param in parameters]:
        for agg in ["max", "min"]:  # Aggregation values
            if agg == "min" and "temperature" not in parameter.lower():
                continue  # Skip "min" aggregation for parameters that do not contain "temperature"
            current_datetime = datetime.now()
            for past_day in range(0, past_days):  # Iterate over the past 4 days in reverse order
                for interval in interval_hours:
                    for day in range(1, future_days):  # Days from 1 to 4
                        interval_start_date = current_datetime.replace(hour=interval, minute=0,
                                                                       second=0, microsecond=0)
                        start_date = (interval_start_date - timedelta(days=past_day))

                        formatted_start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")

                        cached_data = await get_last_records(parameter, formatted_start_date, day, agg, cache)
                        if not cached_data:
                            await run_background_task(parameter, day, agg, formatted_start_date, cache)


async def run_tasks_for_model(model_schedule, future_days, interval_hours, past_days, cache, parameters):
    while True:
        next_hour, next_minute = get_next_schedule_time(model_schedule)
        current_time = datetime.now()
        scheduled_time = current_time.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)

        if current_time >= scheduled_time:
            # Submit the cache_data function for execution in a separate thread
            await cache_data(future_days, interval_hours, past_days, cache, parameters)

            # Calculate the next scheduled time
            next_hour, next_minute = get_next_schedule_time(model_schedule)

        # Sleep for a short interval before checking again
        time.sleep(100000)  # Sleep for 1 minute, adjust as needed


async def run_background_task(parameter, day, agg, start_date, cache):
    await background_task(parameter, day, agg, start_date, cache)


async def background_task(parameter, day, agg, start_date, cache):
    # Your background task logic here
    # Create a logger for the Quart app
    logger.info(f"Running background task for {parameter} parameters, day {day}, agg {agg}, start_date {start_date}...")
    print(f"Running background task for {parameter} parameters, day {day}, agg {agg}, start_date {start_date}...")
    img_io = process_last_images(parameter, day, start_date, agg)
    if img_io:
        await store_last_records(parameter, day, agg, start_date, img_io, cache)
