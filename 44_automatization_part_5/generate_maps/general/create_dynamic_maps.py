from .generate_maps import create_variable_plot, extract_output_names
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

def create_maps(input_filename, output_directory):
    precipitation_colors_1 = ["#f2f2f2","#b5c9fd","#9fbefd","#889eea","#6171f7","#3e55f4","#009694","#0cff00","#e6ff00","#ffff00","#ffcf00","#ff9f00","#ff6f00","#ff1b00","#e60000","#cc0000","#a600a4","#c27ec1","#e094c3","#ffbffd","#f5a6f9","#6fc3fb","#0098fe"]
    precipitation_colors_2 = ["#f1f1f1","#b2c7fc","#799adb","#4d6db5","#4159af","#17788e","#00938f","#24bc65","#98d344","#d7e205","#fff657","#ffd03b","#ff9124","#e55028","#ce2715","#ad0800",
                              "#aa3c90","#cc52c6","#d87fdd","#e89ef2","#f2bdff","#f7d4ff"]
    precipitation_colors = ["#ffffff","#cce1ff","#8fbdff","#529bdd","#2876b5","#208e91","#04aa8a","#2cc469","#98d344","#d7e205","#ffea92","#ffd03b","#ff9124",
                            "#e55028","#ce2715","#ad0800","#aa3c90","#cc52c6","#d87fdd","#e89ef2","#f2bdff"]

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

    wind_max_2m_colors_1 = ["#2961b2","#2876b5","#208e91","#04aa8a","#2cc469","#98d344","#d7e205","#ffea92","#ffd03b","#ff9124",
                            "#e55028","#ce2715","#ad0800","#aa3c90","#cc52c6","#d87fdd","#e89ef2","#fbebff"]
    
    wind_max_2m_colors = ["#FF5733", "#FF8844", "#FFBB55", "#FFDD66", "#FFEE77", "#FFFF88", "#CCFF99", "#AAFFAA", "#77FFBB", "#44FFCC",
                    "#22FFDD", "#11FFEE", "#33FFCC", "#55FFAA", "#77FF88", "#99FF66", "#BBFF44", "#DDFF22", "#FFFF11", "#FFDD00"]
    
    wind_max_2m_colors = ["#003300", "#115511", "#227722", "#339933", "#44AA44", "#55BB55", "#66CC66", "#77DD77", "#88EE88", "#99FF99",
             "#AAFFAA", "#BBFFBB", "#CCFFCC", "#DDFFDD", "#EEFFEE", "#FFFFDD", "#FFFFBB", "#FFFF99"]
    
    # Define custom tick labels for precipitation
    precip_ticks = [0.5,1,2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300]

    # Define the specific contour levels for precipitation
    precip_contour_levels = [0, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200]
    
    cmap_temperature = mcolors.LinearSegmentedColormap.from_list('temperature_cmap', temperature_colors, N=500)
    cmap_wind_max_2m_colors = mcolors.LinearSegmentedColormap.from_list('wind_max_2m_cmap', wind_max_2m_colors, N=500)
    
    cmap_precipitation = mcolors.LinearSegmentedColormap.from_list('precipitation_cmap', precipitation_colors, N=500)

    # Specify the path to the directory containing the custom font file
    font_path = '../assets/fonts/'

    # Register the custom font using FontProperties
    custom_font = FontProperties(fname=font_path + 'font.ttf')

    # List of variable names, titles, colormaps, legend ticks, and value ranges
    variables_and_settings = [
        ("max 2 metre temperature", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
        ("min 2 metre temperature", "najnižja temperatura zraka", "temperatura [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
        ("max 2 metre dewpoint temperature", "najvišja temperatura rosišča", "temperatura rosišča [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
        ("min 2 metre dewpoint temperature", "najnižja temperatura rosišča", "temperatura rosišča [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
        ("max maximum Wind 10m", "najvišji sunek vetra", "sunki vetra [km/h]", cmap_wind_max_2m_colors, list(range(0, 200, 10)), (0, 200)),
        ("max maximum Wind 10m", "najvišji sunek vetra", "sunki vetra [km/h]", cmap_wind_max_2m_colors, list(range(0, 200, 10)), (0, 200)),
        ("max Total Precipitation", "skupna višina padavin", "padavine [mm]",  cmap_precipitation, precip_ticks, (0, 300)),
    ]

    # Loop through the variables and create plots
    for variable, title, x_title, colormap, legend_ticks, value_range in variables_and_settings:        
        df = pd.read_csv(input_filename)
        if variable not in df.columns:
            print(f"Variable '{variable}' not found in the CSV file. Skipping...")
        else: 
            print(f"Creating plot for variable '{variable}'")
            output_filepath, model_run_formatted_date, model_run, selected_formatted_date = extract_output_names(input_filename, variable, output_directory)
            print(f"Output filepath: {output_filepath}")
            create_variable_plot(df, variable, title, x_title, colormap, legend_ticks, value_range, output_filepath, model_run_formatted_date, model_run, selected_formatted_date, custom_font, precip_ticks)



