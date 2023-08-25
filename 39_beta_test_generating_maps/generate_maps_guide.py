from generate_maps import create_variable_plot
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
from scipy.ndimage import zoom
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import os
from datetime import datetime

# Enhanced colormap with more detailed gradient
colors = ["#f2f2f2","#b5c9fd","#9fbefd","#889eea","#6171f7","#3e55f4","#009694","#0cff00","#e6ff00","#ffff00","#ffcf00","#ff9f00","#ff6f00","#ff1b00","#e60000","#cc0000","#a600a4","#c27ec1","#e094c3","#ffbffd","#f5a6f9","#6fc3fb","#0098fe"]
cmap_custom = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors, N=300)

temperature_colors_1 = [
    "#ff89ff","#a774ff","#27b4ff","#88e4ff","#56c976","#bae972","#ffff6f","#fda450","#ff4941","#8c3232"
]

temperature_colors_2 = [
    "#dba1cf","#c983c1","#a779ba","#896db5","#6d66ad","#6a77c8","#5b8cd9","#4ba7f1","#56bbfe",
    "#6cc9fe","#85daff","#6094a0","#74ad83","#75bd6c","#a0c969","#cad778","#e7ea7f","#fff683",
    "#fef9ce","#fee4a6","#fed67c","#febb5b","#fea24f","#f88438","#f36a36","#e24f2c","#e13027",
    "#bf2b25","#962727","#a03937","#b55757","#ba8080"
]

temperature_colors = [
    "#dba1cf","#c180bc","#a779ba","#896db5","#6d66ad","#6c7bc4","#6091d8","#4ba7f1","#56bbfe",
    "#6cc9fe","#84d4fe","#6199a2","#74ad83","#75bd6c","#a0c969","#cad778","#e7ea7f","#fff683",
    "#fef9ce","#fee4a6","#fed67c","#febb5b","#fea24f","#f88438","#f36a36","#e24f2c","#e13027",
    "#bf2b25","#962727","#a03937","#b55757","#ba8080"
]

wind_max_2m_colors = [
    '#FFFFFF',                          # White (0 km/h)
    '#00FF00', '#00E600', '#00CC00',   # Green (0-50 km/h)
    '#FFFF00', '#FFCC00',              # Yellow (50-100 km/h)
    '#FFA500', '#FF8C00',              # Orange (100-150 km/h)
    '#FF0000', '#CC0000',              # Red (150-200 km/h)
    '#FFFF00'                          # Yellow (>200 km/h)
]

cmap_temperature = mcolors.LinearSegmentedColormap.from_list('temperature_cmap', temperature_colors, N=500)
cmap_wind_max_2m_colors = mcolors.LinearSegmentedColormap.from_list('wind_max_2m_cmap', wind_max_2m_colors, N=300)

# Define custom tick labels for precipitation
precip_ticks = [0, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350]

# Define the specific contour levels for precipitation
precip_contour_levels = [0, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350]

# Specify the path to the directory containing the custom font file
font_path = '../assets/fonts/'

# Register the custom font using FontProperties
custom_font = FontProperties(fname=font_path + 'font.ttf')

# List of variable names, titles, colormaps, legend ticks, and value ranges
variables_and_settings = [
    ("2 metre temperature", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
    ("2 metre dewpoint temperature", "najvišja temperatura rosišča", "temperatura rosišča [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
    ("temperature_2m_min", "Minimalna temperatura zraka na višini 2 m", "Temperatura zraka [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
    ("windgusts_10m_max", "Maksimalni sunki vetra na višini 10 m", "Sunki vetra [km/h]", cmap_wind_max_2m_colors, list(range(0, 200, 10)), (0, 200)),
    ("Total_Precipitation", "Napoved količine padavin", "Količina padavin [mm]",  cmap_custom, precip_ticks, (0, 350)),
]

# Loop through the variables and create plots
for variable, title, x_title, colormap, legend_ticks, value_range in variables_and_settings:
    input_filename = f'../38_automatization_part_2/data/output/2_metre_temperature/max/2023/08/25/15z/max_2_metre_temperature_2023_08_26_15_2023_08_26_00_00_2023_08_26_23_00.csv'
    
    df = pd.read_csv(input_filename)
    if variable not in df.columns:
        print(f"Variable '{variable}' not found in the CSV file. Skipping...")
    else: 
        # Extract relevant parts from the input filename
        parts = input_filename.split('/')
        model_run_year = parts[-5]
        model_run_month = parts[-4]
        model_run_day = parts[-3]
        model_run = parts[-2]
        output_variable_name = variable.replace(' ', '_').lower()
        
        selected_file_name = parts[-1]
        selected_file_name_parts = selected_file_name.split('_')
        print(selected_file_name_parts)
        
        selected_aggregate = selected_file_name_parts[0]
        selected_parameter = selected_file_name_parts[1:3]
        
        selected_year = selected_file_name_parts[4]
        selected_month = selected_file_name_parts[5]
        selected_day = selected_file_name_parts[6]
        
        selected_start_year = selected_file_name_parts[8]
        selected_start_month = selected_file_name_parts[9]
        selected_start_day = selected_file_name_parts[10]
        selected_start_hour = selected_file_name_parts[11]
        selected_start_minute = selected_file_name_parts[12]
        
        selected_end_year = selected_file_name_parts[13]
        selected_end_month = selected_file_name_parts[14]
        selected_end_day = selected_file_name_parts[15]
        selected_end_hour = selected_file_name_parts[16]
        selected_end_minute = selected_file_name_parts[17]
        
        formatted_start_datetime = "_".join([selected_start_year, selected_start_month, selected_start_day, selected_start_hour, selected_start_minute])
        formatted_end_datetime = "_".join([selected_end_year, selected_end_month, selected_end_day, selected_end_hour, selected_end_minute])

        # Parse the date components
        model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
        model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")
        
        selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day}", "%Y-%m-%d")
        selected_formatted_date = selected_date_components.strftime("%d. %m. %Y")
        
        # Construct the output directory and filename
        output_directory = f'../38_automatization_part_2/data/public/plots/{output_variable_name}/{selected_aggregate}/{model_run_year}/{model_run_month}/{model_run_day}/{model_run}/'
        print(f"Output directory: {output_directory}")
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist
        
        model_run = model_run.replace('z', '')
        
        output_filename = f'{selected_aggregate}_{output_variable_name}_{selected_year}_{selected_month}_{selected_day}_{model_run}_{formatted_start_datetime}_{formatted_end_datetime}.png'
        output_filepath = os.path.join(output_directory, output_filename)
        create_variable_plot(df, variable, title, x_title, colormap, legend_ticks, value_range, output_filepath, model_run_formatted_date, model_run, selected_formatted_date, custom_font)



