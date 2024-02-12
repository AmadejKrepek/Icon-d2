import datetime
import os
import threading
import time
import multiprocessing
import matplotlib

matplotlib.use('Agg')

import schedule
from flask import Flask, jsonify, request, send_file
from flask_caching import Cache

from assets.parameters.parameters import parameters
from background.proceed import run_background_task
from background.task import get_last_records, store_last_records
from features.brain.brain import fetch_data
from features.db_query.db_query import select_query_parameter_model
from features.generate_maps.create import create_maps
from features.parse_settings.read.read_colors import read_colors
from utils.processor import process_last_images

app = Flask(__name__)
# Configure Flask-Caching to use a disk-based cache
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'cache'
cache = Cache(app)
# Define the cache timeout (in seconds), for example, set to 1 hour
CACHE_TIMEOUT = 3600


@cache.cached(key_prefix='weather_data')
# Define a route that accepts two query parameters 'parameter' and 'model'
@app.route('/data', methods=['GET'])
def get_weather():
    # Get the 'parameter' and 'model' query parameters from the request
    parameter = request.args.get('parameter')
    day = request.args.get('day')
    agg = request.args.get('agg')
    start_date = request.args.get('start_date')
    cached_data = get_last_records(parameter, start_date, day, agg, cache)
    if cached_data:
        # Return the cached data as a response
        return send_file(cached_data[0]['data'], mimetype='image/png')

    img_io = process_last_images(parameter, day, start_date, agg)
    if img_io is None:
        return jsonify({"error": "Sorry no data available"}), 400

    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    # Loop through parameters, days, and aggregation values for icon_d2 and aladin separately
    for parameter in [param for param in parameters]:
        for agg in ["max", "min"]:  # Aggregation values
            for day in range(1, 4):  # Days from 1 to 3 for icon_d2
                start_date = "2024-02-08 18:00:00"  # Your specific start_date
                # background_process = multiprocessing.Process(target=run_background_task, args=(
                # parameter, day, agg, start_date, cache))
                # background_process.start()
                # background_process.join()
                run_background_task(parameter, day, agg, start_date, cache)

    app.run(debug=True, use_reloader=False)
