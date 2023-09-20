from datetime import timedelta
from parse_gribs.utils.remove_directories import removeDirectories
from parse_gribs.utils.remove_coordinates import delete_coordinates
from parse_gribs.utils.convert_to_one_decimal_place import convertToOneDecimalPlace
from database.insert_to_db import insert_parameter_data
from database.get_ids import get_model_id, get_provider_id
from database.check import check_model_run_exists
from database.parameter import create_parameter_table
from database.utils.remove_characters import remove_leading_zeros
import pandas as pd
import glob
import sys
import os
import bz2
import pygrib
import numpy as np

# to nicely display maps we need to adjust coordinates to make sure it fits
DEVIATION_LAT_MIN = 0.15
DEVIATION_LAT_MAX = 0.01
DEVIATION_LON_MIN = 0.02
DEVIATION_LON_MAX = 0.0045

LAT_MIN = 45.1512 - DEVIATION_LAT_MIN
LAT_MAX = 47.1212 + DEVIATION_LAT_MAX
LON_MIN = 12.9955 - DEVIATION_LON_MIN
LON_MAX = 16.7455 + DEVIATION_LON_MAX

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def ms_to_kmh(ms):
    return ms * 3.6

def replace_zeros_with_null(value):
    if value == 0.0:
        return None
    return value

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

def process_data(filepath, bbox, index):
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
        base_datetime = valid_date
        
        if parameter_name == 'Total Precipitation':
            time_range = timedelta(hours=index)
            valid_date = base_datetime + time_range
                
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
    
    df = delete_coordinates(df)
    
    # Convert valid date to datetime and add forecast time to it
    valid_date = pd.to_datetime(valid_date)
    df["ValidDate"] = valid_date
    
    return df, parameter_name

def create_output_folders(year, month, day, model_run, parameter_name, output_directory):
    model_run_dir = os.path.join(output_directory, parameter_name.replace(" ", "_"), year, month, day, model_run + "z")
    os.makedirs(model_run_dir, exist_ok=True)
    return model_run_dir

def save_parameter_data(parameter_data, output_directory, year, month, day, model_run):
    for parameter_name, data_list in parameter_data.items():
        parameter_df_list = [data_item[0] for data_item in data_list]
        combined_df = pd.concat(parameter_df_list, ignore_index=True)
        parameter_name = parameter_name.replace(" ", "_")
        model_run_dir = create_output_folders(year, month, day, model_run, parameter_name, output_directory)
        output_filename = f"{parameter_name}_{year}_{month}_{day}_{model_run}.csv"
        output_path = os.path.join(model_run_dir, output_filename)
        combined_df.to_csv(output_path, index=False)
        return output_path

def parse_gribs(source_data_dir, output_directory, output_directory_gribs):    
    os.makedirs(output_directory, exist_ok=True)
    deleted_directory = source_data_dir
    
    if not os.path.isdir(source_data_dir):
        print(f"Source data directory '{source_data_dir}' does not exist. Please provide the correct path.")
        sys.exit(1)
    
    filenames = glob.glob(os.path.join(source_data_dir, "*.grib2.bz2"))
    filenames = sorted(filenames)

    parameter_data = {}  # Dictionary to store data for each parameter
    
    index = 0

    last_model_run = None
    
    for file in filenames:
        with bz2.BZ2File(file, 'rb') as compressed_file:
            data = compressed_file.read()
        original_filename = os.path.splitext(os.path.basename(file))[0]
        temp_decompressed_path = f"{original_filename}_decompressed.grib2"
        with open(temp_decompressed_path, 'wb') as temp_file:
            temp_file.write(data)
        
        data, parameter_name = process_data(temp_decompressed_path, [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX], index)
        index = index + 1

        if data is not None:
            if parameter_name == "2 metre temperature" or parameter_name == "2 metre dewpoint temperature":
                data[parameter_name] = kelvin_to_celsius(data[parameter_name])

            data[parameter_name] = convertToOneDecimalPlace(data, parameter_name)
            
            # Split the filename using "/" as the separator
            parts = file.split("/")

            # Extract provider_name and model_name from the appropriate positions in the split parts
            provider_name = parts[3]
            model_name = parts[4]

            date_str = original_filename.split("_")[4]
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            model_run = date_str[8:]
            last_model_run = model_run
                        
            if parameter_name not in parameter_data:
                parameter_data[parameter_name] = []
            
            data_date = data["ValidDate"].iloc[0].strftime("%Y-%m-%d")
            parameter_data[parameter_name].append((data, data_date))
        
        os.remove(temp_decompressed_path)
        os.remove(file)
        
    removeDirectories(deleted_directory)

    last_model_run = remove_leading_zeros(last_model_run)
    parameter_table_name = parameter_name.replace(" ", "_").lower()
    create_parameter_table(parameter_table_name, parameter_name)
    
    if not check_model_run_exists(parameter_table_name, last_model_run):
        provider_id = get_provider_id(provider_name)
        model_id = get_model_id(model_name)
        insert_parameter_data(provider_id, model_id, parameter_name, parameter_data[parameter_name], last_model_run, parameter_table_name)

    # Save data for each parameter to separate CSV files
    #return save_parameter_data(parameter_data, output_directory, year, month, day, model_run)
    return None