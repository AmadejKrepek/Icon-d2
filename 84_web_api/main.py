import logging
import multiprocessing
import os

import matplotlib
from dotenv import load_dotenv

matplotlib.use('Agg')

from quart import Quart, jsonify, request, send_file
from aiocache import Cache

from background.task import get_last_records
from utils.processor import process_last_images_async

app = Quart(__name__)

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


# Define a route that accepts two query parameters 'parameter' and 'model'
@app.route('/data', methods=['GET'])
async def get_weather():
    # Get the 'parameter' and 'model' query parameters from the request
    parameter = request.args.get('parameter')
    day = request.args.get('day')
    agg = request.args.get('agg')
    start_date = request.args.get('start_date')
    cached_data = await get_last_records(parameter, start_date, day, agg, cache)
    if cached_data:
        # Return the cached data as a response
        return await send_file(cached_data[0]['data'], mimetype='image/png')

    img_io = await process_last_images_async(parameter, day, start_date, agg)
    if img_io is None:
        return jsonify({"error": "Sorry no data available"}), 400

    return await send_file(img_io, mimetype='image/png')


def run_flask_app():
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    # Start the Flask app in a separate process
    flask_process = multiprocessing.Process(target=run_flask_app)
    flask_process.start()

    # Wait for the Flask process to finish
    flask_process.join()
