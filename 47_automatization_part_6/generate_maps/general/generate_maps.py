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
from models.MapsModel import MapsModel
from osgeo import gdal

# Function to create the plot
def create_variable_plot(model: MapsModel):
    
    # Read the variable data
    variable_values = model.df.pivot("Latitude", "Longitude", model.variable).values

    lat_values = model.df['Latitude'].unique()
    lon_values = model.df['Longitude'].unique()

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
    
    shading_path = '../data/shading/sencenje_250.tif'  # Replace with the path to your shading GeoTIFF file

    # Open the shading GeoTIFF file
    shading_ds = gdal.Open(shading_path, gdal.GA_ReadOnly)

    # Read the shading data into a NumPy array
    shading_array = shading_ds.GetRasterBand(1).ReadAsArray()

    # Create a LightSource instance
    ls = mcolors.LightSource(azdeg=315, altdeg=45)  # Corrected import

    # Calculate the shaded relief
    shaded_relief = ls.shade(shading_array, cmap=plt.cm.gray, vert_exag=0.1, blend_mode='hsv')

    # Create bounding box for the region
    bbox_polygon = Polygon([(LON_MIN, LAT_MIN), (LON_MIN, LAT_MAX), (LON_MAX, LAT_MAX), (LON_MAX, LAT_MIN)])

    # Adjust the bounding box of the region to match the defined bounding box
    region_clipped = gpd.clip(region, bbox_polygon)

    # Plot the bounding areas with detailed
    fig, ax = plt.subplots(figsize=(15, 15))    

    # Adjust the position of the axes to control left padding
    gpd.GeoSeries(bbox_polygon).boundary.plot(ax=ax, color='#333333', linestyle='--')
    fig.set_facecolor('#333333')
        
    variable_clipped = np.clip(variable_values, -20, None)
        
    # Identify the maximum variable value and its coordinates
    max_value = variable_clipped.max()
    max_value_coords = np.unravel_index(variable_clipped.argmax(), variable_clipped.shape)
    
    norm = mcolors.BoundaryNorm(model.contour_levels, model.colormap.N, clip=False, extend='both')
    ax.contourf(lon_values, lat_values, variable_clipped, levels=model.contour_levels, norm=norm, cmap=model.colormap, alpha=0.7)
    plt.imshow(shaded_relief, extent=(LON_MIN, LON_MAX, LAT_MIN, LAT_MAX), origin='upper', cmap=plt.cm.gray, alpha=1.0)

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
            if model.variable == "max Total Precipitation":
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
        
    title_font = {'family' : model.custom_font.get_name(), 'size':'15', 'color':'white', 'weight':'bold'}
    subtitle_font = {'family' : model.custom_font.get_name(), 'size':'11', 'color':'white'}
    
    header_padding = 0.01
    padding = 0.02
    
    # Invisible text to adjust the padding
    fig.text(0.5, 0.795 + padding, 'Upper', ha='center', **title_font, alpha=0)
    fig.text(0.904, 0.12 + padding, 'Left', ha="right", **subtitle_font, alpha=0)
    fig.text(0.127, 0.12, "Napovedni model: ICON-D2 15z", ha="left", **subtitle_font, alpha=0)
    fig.text(0.899, 0.12, "Vir podatkov: Open-Meteo", ha="right", **subtitle_font, alpha=0)
    
    # Set title and source information
    fig.text(0.5, 0.795 + header_padding, f'{model.selected_formatted_date}', ha='center', **title_font)
    fig.text(0.897, 0.125, "vir podatkov: DWD", ha="right", **subtitle_font)
    fig.text(0.127, 0.125, f'ICON-D2 ({model.model_run_formatted_date})', ha="left", **subtitle_font)
    fig.text(0.897, 0.795 + header_padding, model.title, ha='right', **title_font)

    cax_height = 0.02

    # Create axes for the colorbar to make it the same width as the plot, and place at the very bottom
    cax = fig.add_axes([0.15, 0.17, 0.7, cax_height])
    
    colormap_modified = plt.cm.get_cmap(model.colormap, len(model.legend_ticks))
            
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=colormap_modified), cax=cax, orientation='horizontal', 
                            ticks=model.legend_ticks, label=model.x_title, extend='both')
 
    # Adjust the width of the colorbar
    cbar.ax.set_position([cax.get_position().x0 - 0.025, cax.get_position().y0 - 0, cax.get_position().width + 0.075, cax.get_position().height])
    
    # Set the colorbar tick label color
    cbar.ax.xaxis.set_tick_params(color='white')

    # Set the colorbar label color
    cbar.set_label(model.x_title, color='white', labelpad=11, fontproperties=model.custom_font)
    
    # Set edgecolor of colorbar to 'none' to remove the border
    cbar.outline.set_edgecolor('none')

    cax.set_xticks(model.legend_ticks)
    cax.set_xticklabels([str(level) for level in model.legend_ticks], color='white')

    # Make the border white and add padding
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')
        spine.set_linewidth(3)  # Adjust the border thickness to your liking

    # Set the tick color for both x and y axes
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Save the figure with adjusted left padding
    plt.savefig(model.output_filepath, dpi=300, bbox_inches='tight')  # Adjust the pad_inches value as needed
    plt.close()