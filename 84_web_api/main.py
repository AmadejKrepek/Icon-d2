import asyncio
import datetime
import multiprocessing
import threading

import matplotlib

matplotlib.use('Agg')

from quart import Quart, jsonify, request, send_file
from flask_caching import Cache

from assets.parameters.parameters import parameters
from background.proceed import run_background_task
from background.task import get_last_records
from utils.processor import process_last_images, process_last_images_async

app = Quart(__name__)
# Configure Flask-Caching to use a disk-based cache
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'cache'
cache = Cache(app)
# Define the cache timeout (in seconds), for example, set to 1 hour
CACHE_TIMEOUT = 3600


@cache.cached(key_prefix='weather_data')
# Define a route that accepts two query parameters 'parameter' and 'model'
@app.route('/data', methods=['GET'])
async def get_weather():
    # Get the 'parameter' and 'model' query parameters from the request
    parameter = request.args.get('parameter')
    day = request.args.get('day')
    agg = request.args.get('agg')
    start_date = request.args.get('start_date')
    cached_data = get_last_records(parameter, start_date, day, agg, cache)
    if cached_data:
        # Return the cached data as a response
        return await send_file(cached_data[0]['data'], mimetype='image/png')

    img_io = await process_last_images_async(parameter, day, start_date, agg)
    #img_io = process_last_images(parameter, day, start_date, agg)
    if img_io is None:
        return jsonify({"error": "Sorry no data available"}), 400

    return await send_file(img_io, mimetype='image/png')


aladin_interval_hours = [0, 6, 12, 18]  # Intervals at 00:00, 06:00, 12:00, and 18:00
aladin_schedule = [(5, 30), (9, 10), (11, 30), (17, 30), (23, 30)]


def run_flask_app():
    app.run(debug=True, use_reloader=False)


def cache_data():
    for parameter in [param for param in parameters]:
        for agg in ["max", "min"]:  # Aggregation values
            current_datetime = datetime.datetime.now()
            for past_day in range(0, 2):  # Iterate over the past 4 days in reverse order
                for aladin_interval in aladin_interval_hours:
                    for day in range(1, 5):  # Days from 1 to 4
                        interval_start_date = current_datetime.replace(hour=aladin_interval, minute=0,
                                                                       second=0, microsecond=0)
                        start_date = (interval_start_date - datetime.timedelta(days=past_day))

                        formatted_start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")

                        cached_data = get_last_records(parameter, formatted_start_date, day, agg, cache)
                        if not cached_data:
                            background_process = multiprocessing.Process(target=run_background_task, args=(
                                parameter, day, agg, formatted_start_date, cache))
                            background_process.start()
                            background_process.join()

if __name__ == '__main__':
    # Start the Flask app in a separate process
    flask_process = multiprocessing.Process(target=run_flask_app)
    flask_process.start()

    # Your background tasks can run concurrently with Flask
    cache_data()

    # Wait for the Flask process to finish
    flask_process.join()
