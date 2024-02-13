import datetime
import multiprocessing

import matplotlib
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


def run_aladin(aladin_future_days, past_days):
    run_tasks_for_model(aladin_schedule, aladin_future_days, aladin_interval_hours,
                        past_days, cache, aladin_parameters)


def run_icond2(icond2_future_days, past_days):
    # Run tasks for icond2
    run_tasks_for_model(icond2_schedule, icond2_future_days,
                        icond2_interval_hours, past_days, cache, icond2_parameters)


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
    run_async_task()
