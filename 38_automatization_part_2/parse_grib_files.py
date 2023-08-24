from datetime import datetime, timedelta
import xarray as xr
import pandas as pd
import argparse
import glob
import sys
import os
import bz2
import pygrib
import re

# to nicely display maps we need to adjust coordinates to make sure it fits
DEVIATION_LAT_MIN = 0.15
DEVIATION_LAT_MAX = 0.01
DEVIATION_LON_MIN = 0.02
DEVIATION_LON_MAX = 0.0045

LAT_MIN = 45.1512 - DEVIATION_LAT_MIN
LAT_MAX = 47.1512 + DEVIATION_LAT_MAX
LON_MIN = 12.9955 - DEVIATION_LON_MIN
LON_MAX = 16.7955 + DEVIATION_LON_MAX

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def crop_dataframe_to_bbox(df, bbox):
    """
    Perform a geospatial filter on the DataFrame
    based on the specified bounding box
    """
    # Get longitude and latitude values from the DataFrame columns
    longitudes = df["Longitude"]
    latitudes = df["Latitude"]
    # Map longitude range from (0 to 360) into (-180 to 180)
    map_function = lambda lon: (lon - 360) if (lon > 180) else lon
    remapped_longitudes = longitudes.map(map_function)
    # Create new longitude and latitude columns in the DataFrame
    df["Longitude"] = remapped_longitudes
    df["Latitude"] = latitudes
    # Unpack the bounding box values
    min_lat = float(bbox[0])
    max_lat = float(bbox[1])
    min_lon = float(bbox[2])
    max_lon = float(bbox[3])
    lat_filter = (df["Latitude"] >= min_lat) & (df["Latitude"] <= max_lat)
    lon_filter = (df["Longitude"] >= min_lon) & (df["Longitude"] <= max_lon)

    # Apply filters to the DataFrame
    df = df.loc[lat_filter & lon_filter]
    return df

def process_data(filepath, bbox):
    # Load the files with GRIB2 data using pygrib
    grbs = pygrib.open(filepath)
    
    # Retrieve the desired variable
    variable_data = None
    parameter_name = None
    
    for grb in grbs:
        variable_data = grb.values
        latitudes, longitudes = grb.latlons()
        valid_date = grb.validDate
        parameter_name = grb.name
    grbs.close()
    
    if variable_data is None:
        return None
    
    # Create a DataFrame with the extracted data
    df = pd.DataFrame()
    df["Latitude"] = latitudes.ravel()
    df["Longitude"] = longitudes.ravel()
    df[parameter_name] = variable_data.ravel()

    # Perform the bounding box filter
    df = crop_dataframe_to_bbox(df, bbox)
    
    # Convert valid date to datetime and add forecast time to it
    valid_date = pd.to_datetime(valid_date)
    df["ValidDate"] = valid_date
    
    return df, parameter_name


if __name__ == "__main__":
    # Directory containing the GRIB2 data files
    source_data_dir = "./12z"
    
    # Create the "output" directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if the source data directory exists
    if not os.path.isdir(source_data_dir):
        print(f"Source data directory '{source_data_dir}' does not exist. Please provide the correct path.")
        sys.exit(1)
    
    # Read all data files in the specified directory
    filenames = glob.glob(os.path.join(source_data_dir, "*.grib2.bz2"))
    filenames = sorted(filenames)

    output_df = pd.DataFrame()

    parameter_data = {}  # Dictionary to store data for each parameter

    for file in filenames:
        print("Processing", file)
        
        # Decompress the file and read the decompressed data
        with bz2.BZ2File(file, 'rb') as compressed_file:
            data = compressed_file.read()
        # Create a temporary file to hold the decompressed data
        original_filename = os.path.splitext(os.path.basename(file))[0]
        temp_decompressed_path = f"{original_filename}_decompressed.grib2"
        with open(temp_decompressed_path, 'wb') as temp_file:
            print("Writing decompressed data to", temp_decompressed_path)
            temp_file.write(data)
         # Process the data and get parameter name
        data, parameter_name = process_data(temp_decompressed_path, [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX])
        if data is not None:
            print("Processing completed. Saving the data...")
            # Convert temperature from Kelvin to Celsius
            data[parameter_name] = kelvin_to_celsius(data[parameter_name])
            
            # Check if parameter data exists in the dictionary
            if parameter_name not in parameter_data:
                parameter_data[parameter_name] = pd.DataFrame()
            
            # Append the data to the parameter's DataFrame
            parameter_data[parameter_name] = pd.concat([parameter_data[parameter_name], data], ignore_index=True)
        
        # Remove the temporary decompressed file
        os.remove(temp_decompressed_path)

    # Save data for each parameter to separate CSV files
    for parameter_name, parameter_df in parameter_data.items():
        print(f"Saving data for parameter '{parameter_name}'...")
        parameter_df.to_csv(os.path.join("output", parameter_name.replace(" ", "_") + ".csv"), index=False)

    print("Script finished.")