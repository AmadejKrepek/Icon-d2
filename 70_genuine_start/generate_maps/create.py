from datetime import timedelta

from animation.animation import create_gif_from_png
from .models.MapsModel import MapsModel
from .basic import create_variable_plot
from .utils.extract_names import extract_output_names, extract_animation_output_names
import matplotlib.colors as mcolors


def create_maps(model_run, df_array, output_directory, color_configuration, custom_font, start_date, end_date,
                selected_date):
    precipitation_colors = color_configuration["precipitation_colors"]
    temperature_colors = color_configuration["temperature_colors"]
    wind_max_2m_colors = color_configuration["wind_max_2m_colors"]
    snow_depth_colors = color_configuration["snow_depth_colors"]

    cmap_temperature = mcolors.LinearSegmentedColormap.from_list('temperature_cmap', temperature_colors, N=500)
    cmap_wind_max_2m_colors = mcolors.LinearSegmentedColormap.from_list('wind_max_2m_cmap', wind_max_2m_colors, N=500)
    cmap_precipitation = mcolors.LinearSegmentedColormap.from_list('precipitation_cmap', precipitation_colors, N=500)
    cmap_snow_depth = mcolors.LinearSegmentedColormap.from_list('snow_depth_cmap', snow_depth_colors, N=1000)

    temperature_ticks = list(range(-20, 42, 2))
    wind_max_2m_ticks = list(range(10, 210, 10))
    precipitation_ticks = [0.1, 0.5, 1, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300]
    snow_depth_ticks = [1,2,3,4,5,6,8,10,12,14,16,20, 25, 30, 40, 50, 75, 100, 125, 150, 200]

    temperature_contour_levels = list(range(-20, 42, 2))
    wind_max_2m_contour_levels = list(range(10, 210, 10))
    precipitation_contour_leves = precipitation_ticks
    snow_depth_contour_levels = snow_depth_ticks

    variables_and_settings = [
        ("animation_2_metre_temperature_icond2", "animacija temperature zraka", "temperatura [°C]", cmap_temperature,
         temperature_ticks, temperature_contour_levels),
        ("max_2_metre_temperature_icond2", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature,
         temperature_ticks, temperature_contour_levels),
        ("max_2_metre_temperature_aladin", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature,
         temperature_ticks, temperature_contour_levels),
        ("min_2_metre_temperature_icond2", "najnižja temperatura zraka", "temperatura [°C]", cmap_temperature,
         temperature_ticks, temperature_contour_levels),
        ("min 2 metre dewpoint temperature", "najvišja temperatura rosišča", "temperatura rosišča [°C]",
         cmap_temperature, temperature_ticks, temperature_contour_levels),
        ("min 2 metre dewpoint temperature", "najnižja temperatura rosišča", "temperatura rosišča [°C]",
         cmap_temperature, temperature_ticks, temperature_contour_levels),
        ("max_maximum_wind_10m_icond2", "najvišji sunek vetra", "sunki vetra [km/h]", cmap_wind_max_2m_colors,
         wind_max_2m_ticks, wind_max_2m_contour_levels),
        ("max_10_metre_v_wind_component_icond2", "najvišji sunek vetra", "sunki vetra [km/h]", cmap_wind_max_2m_colors,
         wind_max_2m_ticks, wind_max_2m_contour_levels),
        ("max_total_precipitation_icond2", "skupna višina padavin", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("max_total_precipitation_aladin", "skupna višina padavin", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("animation_total_precipitation_aladin", "skupna višina padavin v snegu", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("max_large-scale_snowfall_-_water_equivalent_(accumulation)_icond2", "skupna višina padavin v snegu", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("animation_large-scale_snowfall_-_water_equivalent_(accumulation)_icond2", "skupna višina padavin", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("max_convective_snowfall_water_equivalent_(s)_icond2", "skupna višina padavin v snegu", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("animation_convective_snowfall_water_equivalent_(s)_icond2", "skupna višina padavin", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("max_snow_depth_icond2", "višina snežne odeje", "višina snežne odeje [cm]", cmap_snow_depth,
         snow_depth_ticks, snow_depth_contour_levels),
        ("animation_snow_depth_icond2", "višina snežne odeje", "višina snežne odeje [cm]", cmap_snow_depth,
         snow_depth_ticks, snow_depth_contour_levels),
        ("animation_total_precipitation_icond2", "skupna višina padavin", "padavine [mm]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("max_base_reflectivity_(cmax)_icond2", "maksimalna radarska odbojnost", "odboji [dBz]", cmap_precipitation,
         precipitation_ticks, precipitation_contour_leves),
        ("animation_base_reflectivity_(cmax)_icond2", "maksimalna radarska odbojnost", "odboji [dBz]", cmap_precipitation,
        precipitation_ticks, precipitation_contour_leves),
    ]
    chosen_file_path = None
    chosen_variable = 'animation'
    counter = None
    for variable, title, x_title, colormap, legend_ticks, contour_levels in variables_and_settings:
        for df in df_array:
            df_result = df.reset_index()
            print(variable)
            if variable not in df_result.columns:
                print(f"Variable '{variable}' not found in the CSV file. Skipping...")
                continue
            else:
                if len(df_array) > 1:
                    counter = 0
                    # Get the first date from the 'Datetime' column
                    selected_date = df_result['Datetime'].min()
                    output_filepath, model_run_formatted_date, selected_formatted_date, model_run_model, provider = extract_animation_output_names(
                        model_run, variable, output_directory, start_date, end_date, selected_date, counter)
                    counter += 1
                else:
                    output_filepath, model_run_formatted_date, selected_formatted_date, model_run_model, provider = extract_output_names(
                        model_run, variable, output_directory, start_date, end_date, selected_date)
                if counter is not None:
                    chosen_file_path = f"{output_filepath}_{counter}"
                chosen_variable = variable
                model = MapsModel(df_result, variable, title, x_title, colormap, legend_ticks, contour_levels,
                                  output_filepath, model_run_formatted_date, selected_formatted_date, model_run_model,
                                  provider, custom_font)
                create_variable_plot(model)
    create_gif_from_png(chosen_file_path, f"{chosen_variable}.gif")
