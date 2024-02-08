import datetime
import os

from flask import Flask, jsonify, request, send_file
from matplotlib.font_manager import FontProperties

from features.brain.brain import fetch_data
from features.db_query.db_query import select_query_parameter_model
from features.generate_maps.create import create_maps
from features.parse_settings.read.read_colors import read_colors

app = Flask(__name__)


# Define a route that accepts two query parameters 'parameter' and 'model'
@app.route('/data', methods=['GET'])
def get_weather():
    # Get the 'parameter' and 'model' query parameters from the request
    parameter = request.args.get('parameter')
    day = request.args.get('day')
    agg = request.args.get('agg')
    start_date = request.args.get('start_date')
    # Check if both parameters are provided
    if parameter and day and start_date:
        result, parameter = select_query_parameter_model(parameter, start_date)
        if not result:
            return jsonify({"error": "Sorry no data available"}), 400
        df_array, selected_date = fetch_data(result, parameter, day, agg)
        color_configuration = read_colors("../assets/colors/colors.config")
        font_path = '../assets/fonts/'
        custom_font = FontProperties(fname=font_path + 'font.ttf')
        start_date = datetime.datetime.strptime(result['start_date'], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(result['end_date'], "%Y-%m-%d %H:%M:%S")
        img_io = create_maps(result['model_run'], df_array, color_configuration, custom_font, start_date, end_date,
                             selected_date)
        return send_file(img_io, mimetype='image/png')
    else:
        return jsonify({"error": "Missing parameters"}), 400


if __name__ == '__main__':
    app.run(debug=True)
