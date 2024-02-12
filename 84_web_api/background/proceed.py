import matplotlib
import schedule
import time
import threading
from datetime import datetime

from background.task import store_last_records
from utils.processor import process_last_images

# Define the schedules for different parameters
aladin_schedule = [(0, 44), (3, 44), (6, 44), (9, 44), (12, 49), (15, 44), (18, 44), (21, 44)]
icond2_schedule = [(5, 30), (9, 10), (11, 30), (17, 30), (23, 30)]


def get_next_schedule_time(schedule):
    current_time = datetime.now()
    current_hour, current_minute = current_time.hour, current_time.minute

    next_entries = [(hour, minute) for hour, minute in schedule if (hour, minute) > (current_hour, current_minute)]
    if next_entries:
        return min(next_entries)

    # If no future entries today, get the first entry for the next day
    return min([(hour, minute) for hour, minute in schedule])


def run_background_task(parameter, day, agg, start_date, cache):
    #while True:
        # Replace 'model_schedule' with the appropriate schedule ('aladin_schedule' or 'icond2_schedule')
        #next_hour, next_minute = get_next_schedule_time(aladin_schedule if "aladin" in parameter else icond2_schedule)
        ##current_time = datetime.now()
        #scheduled_time = current_time.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)

        #if current_time < scheduled_time:
            # Sleep until the next scheduled time
            #sleep_duration = (scheduled_time - current_time).seconds
            #time.sleep(sleep_duration)

        # Run the background task at the scheduled time
        background_task(parameter, day, agg, start_date, cache)


def background_task(parameter, day, agg, start_date, cache):
    # Your background task logic here
    print(f"Running background task for {parameter} parameters, day {day}, agg {agg}, start_date {start_date}...")
    img_io = process_last_images(parameter, day, start_date, agg)
    store_last_records(parameter, day, agg, start_date, img_io, cache)
