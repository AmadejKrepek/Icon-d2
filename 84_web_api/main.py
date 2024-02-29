import multiprocessing
import os

import matplotlib
from diskcache import Cache
from dotenv import load_dotenv

from setup.set_logger import setup_logging

matplotlib.use('Agg')

from quart import Quart, jsonify, request, send_file

from background.task import get_last_records
from utils.processor import process_last_images_async

app = Quart(__name__)

# Load environment variables from .env
load_dotenv()

logger = setup_logging()
# Database connection information
CACHE_FILE_PATH = os.getenv("CACHE_FILE_PATH")

cache = Cache(CACHE_FILE_PATH)


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
