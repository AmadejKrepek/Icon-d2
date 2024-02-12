import datetime

from matplotlib.font_manager import FontProperties

from features.brain.brain import fetch_data
from features.db_query.db_query import select_query_parameter_model
from features.generate_maps.create import create_maps
from features.parse_settings.read.read_colors import read_colors


def process_last_images(parameter, day, start_date, agg):
    # Check if both parameters are provided
    if parameter and day and start_date:
        result, parameter = select_query_parameter_model(parameter, start_date)
        if not result:
            return None;
        df_array, selected_date = fetch_data(result, parameter, day, agg)
        color_configuration = read_colors("../assets/colors/colors.config")
        font_path = '../assets/fonts/'
        custom_font = FontProperties(fname=font_path + 'font.ttf')
        start_date = datetime.datetime.strptime(result['start_date'], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.datetime.strptime(result['end_date'], "%Y-%m-%d %H:%M:%S")
        img_io = create_maps(result['model_run'], df_array, color_configuration, custom_font, start_date, end_date,
                             selected_date)
        return img_io
