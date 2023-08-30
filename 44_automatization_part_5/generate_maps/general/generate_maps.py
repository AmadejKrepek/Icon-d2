import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
from scipy.ndimage import zoom
from shapely.geometry import Polygon, Point

# Function to create the plot
def create_variable_plot(
    df, 
    variable_name, 
    title,
    x_title, 
    colormap, 
    legend_ticks, 
    value_range, 
    output_filename,
    model_run_formatted_date,
    model_run,
    selected_formatted_date,
    custom_font,
    precip_contour_levels):
    if variable_name not in df.columns:
        print(f"Variable '{variable_name}' not found in the CSV file. Skipping...")
        return
    
    # Read the variable data
    variable_values = df.pivot("Latitude", "Longitude", variable_name).values

    lat_values = df['Latitude'].unique()
    lon_values = df['Longitude'].unique()

    # Load the world map with medium resolution
    world = gpd.read_file('../data/shapes/shape/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')

    # Define the neighboring countries
    countries = ['Slovenia', 'Austria', 'Italy', 'Hungary', 'Croatia']

    # Filter the neighboring countries
    region = world[world['NAME'].isin(countries)]

    LAT_MIN = 45.1512
    LAT_MAX = 47.1512
    LON_MIN = 12.9955
    LON_MAX = 16.7955

    # Create bounding box for the region
    bbox_polygon = Polygon([(LON_MIN, LAT_MIN), (LON_MIN, LAT_MAX), (LON_MAX, LAT_MAX), (LON_MAX, LAT_MIN)])

    # Adjust the bounding box of the region to match the defined bounding box
    region_clipped = gpd.clip(region, bbox_polygon)

    # Plot the bounding areas with detailed geometries
    fig, ax = plt.subplots(figsize=(15, 15))    
    
    # Adjust the position of the axes to control left padding
    gpd.GeoSeries(bbox_polygon).boundary.plot(ax=ax, color='#333333', linestyle='--')
    fig.set_facecolor('#333333')

    # Clip variable values within the desired range
    if variable_name == "max Total Precipitation":
        variable_clipped = np.clip(variable_values, 0.0, None)
        contour_levels = precip_contour_levels
    elif variable_name == "max maximum Wind 10m":
        variable_clipped = np.clip(variable_values, value_range[0], None)
        contour_levels = np.arange(legend_ticks[0], legend_ticks[-1] + 1, step=10)
    else:
        variable_clipped = np.clip(variable_values, value_range[0], None)
        contour_levels = np.arange(legend_ticks[0], legend_ticks[-1] + 2, step=2)
        
    # Identify the maximum variable value and its coordinates
    max_value = variable_clipped.max()
    max_value_coords = np.unravel_index(variable_clipped.argmax(), variable_clipped.shape)

    # Use the specified colormap in the contour plot
    if (variable_name == "max Total Precipitation"):
        # Use the specified colormap with the custom normalization
        norm = mcolors.BoundaryNorm(contour_levels, colormap.N, clip=False)
        contour_plot = ax.contourf(lon_values, lat_values, variable_values, 
                                levels=contour_levels, cmap=colormap, extend='max', norm=norm)
    elif(variable_name == "max maximum Wind 10m"):
        contour_plot = ax.contourf(lon_values, lat_values, variable_values, levels=contour_levels, cmap=colormap, extend='max')
    else:
        contour_plot = ax.contourf(lon_values, lat_values, variable_values, levels=contour_levels, cmap=colormap, extend='both')
    # Optionally, set stride to control the density of the text
    stride = 4

    # Iterate through the grid and add text for variable values
    for i in range(0, len(lat_values), stride):
        for j in range(0, len(lon_values), stride):
            # Skip values outside of the bounding box
            if not bbox_polygon.contains(Point(lon_values[j], lat_values[i])):
                continue
            # Extract variable value and convert to integer
            var_val = int(round(variable_clipped[i, j]))
            # Include all values for temperature and maximum value, but exclude 0 for Total Precipitation
            if variable_name == "max Total Precipitation":
                if (i, j) == max_value_coords or var_val != 0 or var_val == max_value:
                    ax.text(lon_values[j], lat_values[i], f'{var_val}', fontsize=8, ha='center', va='center', color='black')
            else:
                ax.text(lon_values[j], lat_values[i], f'{var_val}', fontsize=8, ha='center', va='center', color='black')

    # Add borders between countries
    region_clipped.boundary.plot(ax=ax, linewidth=2, color='#333333')

    plt.xlim(LON_MIN, LON_MAX)
    plt.ylim(LAT_MIN, LAT_MAX)

    # Remove x and y axis
    plt.xticks([])
    plt.yticks([])

    # Load and resize the logo (replace 'logo.png' with your actual logo path)
    logo = mpimg.imread('../assets/logo/logo_512_39.webp')

    # Desired width and height for the resized logo
    desired_width = 800
    desired_height = 500

    # Calculate scaling factors for width and height
    scaling_factor_width = desired_width / logo.shape[1]
    scaling_factor_height = desired_height / logo.shape[0]

    # Choose the minimum scaling factor to maintain aspect ratio
    scaling_factor = min(scaling_factor_width, scaling_factor_height)

    # Resize the logo
    logo_resized = zoom(logo, (scaling_factor, scaling_factor, 1))

    fig.figimage(logo_resized, xo=60, yo=3110, zorder=20)
        
    title_font = {'family' : custom_font.get_name(), 'size':'15', 'color':'white', 'weight':'bold'}
    subtitle_font = {'family' : custom_font.get_name(), 'size':'11', 'color':'white'}
    
    header_padding = 0.01
    padding = 0.02
    
    # Invisible text to adjust the padding
    fig.text(0.5, 0.795 + padding, 'Upper', ha='center', **title_font, alpha=0)
    fig.text(0.904, 0.12 + padding, 'Left', ha="right", **subtitle_font, alpha=0)
    fig.text(0.127, 0.12, "Napovedni model: ICON-D2 15z", ha="left", **subtitle_font, alpha=0)
    fig.text(0.899, 0.12, "Vir podatkov: Open-Meteo", ha="right", **subtitle_font, alpha=0)
    
    # Set title and source information
    fig.text(0.5, 0.795 + header_padding, f'{selected_formatted_date}', ha='center', **title_font)
    fig.text(0.897, 0.125, "vir podatkov: DWD", ha="right", **subtitle_font)
    fig.text(0.127, 0.125, f'ICON-D2 ({model_run_formatted_date} {model_run} UTC)', ha="left", **subtitle_font)
    fig.text(0.897, 0.795 + header_padding, title, ha='right', **title_font)

    cax_height = 0.02

    # Create axes for the colorbar to make it the same width as the plot, and place at the very bottom
    cax = fig.add_axes([0.15, 0.17, 0.7, cax_height])
    if variable_name == "max Total Precipitation":
        colormap_modified = plt.cm.get_cmap(colormap)
        colormap_modified.set_under('#ffffff')   # Color for values below minimum
        colormap_modified.set_over('#f5d9fc') 
        # Adjust colorbar settings
        cbar = plt.colorbar(contour_plot, cax=cax, orientation='horizontal', 
                            ticks=legend_ticks, label=x_title)
    else:
        cbar = plt.colorbar(contour_plot, cax=cax, orientation='horizontal', ticks=legend_ticks, label=x_title)
 
    
    # Adjust the width of the colorbar
    cbar.ax.set_position([cax.get_position().x0 - 0.025, cax.get_position().y0 - 0, cax.get_position().width + 0.075, cax.get_position().height])
    
    # Set the colorbar tick label color
    cbar.ax.xaxis.set_tick_params(color='white')
    # Set the color of the tick labels
    #cbar.set_ticklabels([str(int(level)) for level in legend_ticks], )

    # Set the colorbar label color
    cbar.set_label(x_title, color='white', labelpad=11, fontproperties=custom_font)
    
    # Set edgecolor of colorbar to 'none' to remove the border
    cbar.outline.set_edgecolor('none')

    if (variable_name == "max Total Precipitation"):
        # Set colorbar tick labels for the entire range, excluding label for value 0
        cax.set_xticks([level for level in contour_levels if level != 0])
        cax.set_xticklabels([str(level) for level in contour_levels if level != 0], color='white')  # Adjust color as needed
    else:
        cax.set_xticks(contour_levels)
        cax.set_xticklabels([str(level) for level in contour_levels], color='white')

    # Make the border white and add padding
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')
        spine.set_linewidth(3)  # Adjust the border thickness to your liking

    # Set the tick color for both x and y axes
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Save the figure with adjusted left padding
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')  # Adjust the pad_inches value as needed
    plt.close()
    
def extract_output_names(input_filename, variable, output_directory):
        parts = input_filename.split('/')
        model_run_year = parts[-5]
        model_run_month = parts[-4]
        model_run_day = parts[-3]
        model_run = parts[-2]
        output_variable_name = variable.replace(' ', '_').lower()

        selected_file_name = parts[-1]
        selected_file_name_parts = selected_file_name.split('_')

        # Find the index of the year in selected_file_name_parts
        year_index = None
        for i, part in enumerate(selected_file_name_parts):
            if part.isdigit() and len(part) == 4:
                year_index = i
                break

        selected_aggregate = None

        if year_index is not None:
            selected_year = selected_file_name_parts[year_index]
            selected_month = selected_file_name_parts[year_index + 1]
            selected_day = selected_file_name_parts[year_index + 2]
            selected_start_year = selected_file_name_parts[year_index + 4]
            selected_start_month = selected_file_name_parts[year_index + 5]
            selected_start_day = selected_file_name_parts[year_index + 6]
            selected_start_hour = selected_file_name_parts[year_index + 7]
            selected_start_minute = selected_file_name_parts[year_index + 8]
            selected_end_year = selected_file_name_parts[year_index + 9]
            selected_end_month = selected_file_name_parts[year_index + 10]
            selected_end_day = selected_file_name_parts[year_index + 11]
            selected_end_hour = selected_file_name_parts[year_index + 12]
            selected_end_minute = selected_file_name_parts[year_index + 13].replace(".csv", "")
            selected_aggregate = selected_file_name_parts[0]
        else:
            print("Year not found in filename")

        # Continue with the rest of your code
        formatted_start_datetime = "_".join([selected_start_year, selected_start_month, selected_start_day, selected_start_hour, selected_start_minute])
        formatted_end_datetime = "_".join([selected_end_year, selected_end_month, selected_end_day, selected_end_hour, selected_end_minute])

        # Parse the date components
        model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
        model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")

        if (output_variable_name == "max_total_precipitation"):
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day} {selected_end_hour}:{selected_end_minute}", "%Y-%m-%d %H:%M")
            selected_formatted_date = selected_date_components.strftime("%d. %m. do %H:%M")
        else:      
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day}", "%Y-%m-%d")
            selected_formatted_date = selected_date_components.strftime("%d. %m. %Y")
        
        # Construct the output directory and filename
        output_directory = f'{output_directory}/{output_variable_name}/{selected_aggregate}/{model_run_year}/{model_run_month}/{model_run_day}/{model_run}/'
        print(f"Output directory: {output_directory}")
        
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist
        
        model_run = model_run.replace('z', '')
        
        output_filename = f'{output_variable_name}_{selected_year}_{selected_month}_{selected_day}_{model_run}_{formatted_start_datetime}_{formatted_end_datetime}.png'
        output_filepath = os.path.join(output_directory, output_filename)
        
        return output_filepath, model_run_formatted_date, model_run, selected_formatted_date