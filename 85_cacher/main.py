import asyncio
import datetime
import logging
import os

import matplotlib

from dotenv import load_dotenv

from assets.parameters.parameters import aladin_parameters, icond2_parameters
from background.proceed import run_tasks_for_model

matplotlib.use('Agg')

from aiocache import Cache

# Load environment variables from .env
load_dotenv()

# Database connection information
API_URL = os.getenv("API_URL")
PASSWORD = os.getenv("PASSWORD")

# Configure aiocache to use Redis as a cache backend
cache = Cache(Cache.REDIS, endpoint=API_URL, port=6379, namespace="weather_maps",
              password=PASSWORD)

# Configure logging once with a custom Formatter
log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(filename='app.log', level=logging.INFO, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')

# Create a logger for the Quart app
logger = logging.getLogger(__name__)

current_time = datetime.datetime.now()
aladin_interval_hours = [0, 6, 12, 18]
aladin_schedule = [(5, 30), (9, 10), (11, 30), (17, 30), (23, 30)]
icond2_interval_hours = [0, 3, 6, 9, 12, 15, 18, 21]
icond2_schedule = [(0, 44), (3, 44), (6, 44), (9, 44), (12, 49), (15, 44), (18, 44), (21, 44)]


async def run_async_task():
    aladin_future_days = 5
    icond2_future_days = 4
    past_days = 2

    # Run tasks for aladin
    await run_tasks_for_model([(current_time.hour, current_time.minute)], aladin_future_days, aladin_interval_hours,
                              past_days, cache, aladin_parameters)
    # Run tasks for icond2
    # await  run_tasks_for_model([(current_time.hour, current_time.minute)], icond2_future_days,
    # icond2_interval_hours, past_days, cache, icond2_parameters)


if __name__ == '__main__':
    asyncio.run(run_async_task())