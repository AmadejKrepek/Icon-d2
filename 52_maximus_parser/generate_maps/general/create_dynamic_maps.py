from .generate_maps import create_variable_plot
from ..utils.extract_names import extract_output_names
from get_aggregates.utils.add_lat_lon_from_csv import add_lat_lon_columns_from_configuration_file
import pandas as pd
import matplotlib.colors as mcolors
from models.MapsModel import MapsModel
import logging

logger = logging.getLogger(__name__)


def create_maps(input_filename, output_directory, color_configuration, coordinates_configuration, custom_font):
    try:
        logger.info(f"Started process for creating maps with input_filename: {input_filename}, to output_directory: "
                    f"{output_directory}")
        precipitation_colors = color_configuration["precipitation_colors"]
        temperature_colors = color_configuration["temperature_colors"]
        wind_max_2m_colors = color_configuration["wind_max_2m_colors"]

        cmap_temperature = mcolors.LinearSegmentedColormap.from_list('temperature_cmap', temperature_colors, N=500)
        cmap_wind_max_2m_colors = mcolors.LinearSegmentedColormap.from_list('wind_max_2m_cmap', wind_max_2m_colors, N=500)
        cmap_precipitation = mcolors.LinearSegmentedColormap.from_list('precipitation_cmap', precipitation_colors, N=500)

        temperature_ticks = list(range(-20, 42, 2))
        wind_max_2m_ticks = list(range(10, 210, 10))
        precipitation_ticks = [0.1, 0.5, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300]

        temperature_contour_levels = list(range(-20, 42, 2))
        wind_max_2m_contour_levels = list(range(10, 210, 10))
        precipitation_contour_leves = precipitation_ticks

        variables_and_settings = [
            ("max 2 metre temperature", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature,
             temperature_ticks, temperature_contour_levels),
            ("min 2 metre temperature", "najnižja temperatura zraka", "temperatura [°C]", cmap_temperature,
             temperature_ticks, temperature_contour_levels),
            ("max 2 metre dewpoint temperature", "najvišja temperatura rosišča", "temperatura rosišča [°C]",
             cmap_temperature, temperature_ticks, temperature_contour_levels),
            ("min 2 metre dewpoint temperature", "najnižja temperatura rosišča", "temperatura rosišča [°C]",
             cmap_temperature, temperature_ticks, temperature_contour_levels),
            ("max maximum Wind 10m", "najvišji sunek vetra", "sunki vetra [km/h]", cmap_wind_max_2m_colors,
             wind_max_2m_ticks, wind_max_2m_contour_levels),
            ("max Total Precipitation", "skupna višina padavin", "padavine [mm]", cmap_precipitation, precipitation_ticks,
             precipitation_contour_leves),
            ("sum Total Precipitation", "skupna višina padavin", "padavine [mm]", cmap_precipitation, precipitation_ticks,
             precipitation_contour_leves),
        ]
        logger.info(f"Looping through variables and settings...")
        for variable, title, x_title, colormap, legend_ticks, contour_levels in variables_and_settings:
            df = pd.read_csv(input_filename)
            df = add_lat_lon_columns_from_configuration_file(df, coordinates_configuration)
            if variable not in df.columns:
                print(f"Variable '{variable}' not found in the CSV file. Skipping...")
            else:
                output_filepath, model_run_formatted_date, selected_formatted_date, model_run_model, provider = extract_output_names(
                    input_filename, variable, output_directory)
                model = MapsModel(df, variable, title, x_title, colormap, legend_ticks, contour_levels, output_filepath,
                                  model_run_formatted_date, selected_formatted_date, model_run_model, provider, custom_font)
                create_variable_plot(model)
        logger.info(f"Finished process for creating maps with input_filename: {input_filename}, to output_directory: "
                    f"{output_directory}")
    except Exception as e:
        logger.error(f"Error while creating process for creating maps: {e}")
