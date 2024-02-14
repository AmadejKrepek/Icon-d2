import datetime
import multiprocessing
import time

import matplotlib
import schedule
from diskcache import Cache

from dotenv import load_dotenv
from flask import Flask

from assets.parameters.parameters import aladin_parameters, icond2_parameters
from background.proceed import run_tasks_for_model
from setup.set_logger import setup_logging

matplotlib.use('Agg')
app = Flask(__name__)

cache = Cache("shared-cache")

# Load environment variables from .env
load_dotenv()

logger = setup_logging()

current_time = datetime.datetime.now()
aladin_interval_hours = [0, 6, 12, 18]
aladin_schedule = [(5, 30), (9, 10), (11, 30), (17, 30), (23, 30)]
icond2_interval_hours = [0, 3, 6, 9, 12, 15, 18, 21]
icond2_schedule = [(0, 44), (3, 44), (6, 44), (9, 44), (12, 49), (15, 44), (18, 44), (21, 44)]

test_current_schedule = [(current_time.hour, current_time.minute)]


def run_aladin(aladin_future_days, past_days):
    run_tasks_for_model(aladin_schedule, aladin_future_days, aladin_interval_hours,
                        past_days, cache, aladin_parameters)


def run_icond2(icond2_future_days, past_days):
    # Run tasks for icond2
    run_tasks_for_model(icond2_schedule, icond2_future_days,
                        icond2_interval_hours, past_days, cache, icond2_parameters)


def run_async_aladin():
    aladin_future_days = 5
    past_days = 2

    # Create process for Aladin
    aladin_process = multiprocessing.Process(target=run_aladin, args=(aladin_future_days, past_days))

    # Start the process
    aladin_process.start()

    # Wait for the process to finish
    aladin_process.join()


def run_async_icond2():
    icond2_future_days = 4
    past_days = 2

    # Create process for icond2
    icond2_process = multiprocessing.Process(target=run_icond2, args=(icond2_future_days, past_days))

    # Start the process
    icond2_process.start()

    # Wait for the process to finish
    icond2_process.join()


def get_number_of_cores():
    return multiprocessing.cpu_count()


def run_async_task():
    aladin_future_days = 5
    icond2_future_days = 4
    past_days = 2

    # Create processes for Aladin and icond2
    aladin_process = multiprocessing.Process(target=run_aladin, args=(aladin_future_days, past_days))
    icond2_process = multiprocessing.Process(target=run_icond2, args=(icond2_future_days, past_days))

    # Start both processes
    aladin_process.start()
    icond2_process.start()

    # Wait for both processes to finish
    aladin_process.join()
    icond2_process.join()


if __name__ == '__main__':
    num_cores = get_number_of_cores()
    logger.info(f"The CPU has {num_cores} cores.")
    # Schedule the run_async_aladin function with provided aladin_schedule
    for hour, minute in aladin_schedule:
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_async_aladin)

    # Schedule the run_async_icond2 function with provided icond2_schedule
    for hour, minute in icond2_schedule:
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_async_icond2)

    while True:
        # Run pending scheduled tasks
        schedule.run_pending()
        time.sleep(30)
