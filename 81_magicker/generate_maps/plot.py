import os

from matplotlib.font_manager import FontProperties

from generate_maps.colors.read_colors import read_colors
from generate_maps.create import create_maps

color_configuration = read_colors("../assets/colors/colors.config")
storage_directory = "./data"
maps_output_directory = os.path.join(storage_directory, 'public/plots')
font_path = '../assets/fonts/'
custom_font = FontProperties(fname=font_path + 'font.ttf')


def create_plot(selected_model_run, df, selected_start_date, selected_end_date, selected_date):
    create_maps(selected_model_run, df, maps_output_directory, color_configuration, custom_font,
                selected_start_date, selected_end_date, selected_date)
