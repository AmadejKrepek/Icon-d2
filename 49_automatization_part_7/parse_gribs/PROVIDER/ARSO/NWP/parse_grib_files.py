from datetime import timedelta
from parse_gribs.utils.remove_directories import removeDirectories
import pandas as pd
import glob
import sys
import os
import pygrib
import zipfile

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

def ms_to_kmh(ms):
    return ms * 3.6

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

def process_data(filepath, bbox, index):
    # Load the files with GRIB2 data using pygrib
    grbs = pygrib.open(filepath)
    
    # Initialize a dictionary to store parameter data
    parameter_data = {}
        
    for grb in grbs:
        parameter_name = grb.name
        variable_data = grb.values
        latitudes, longitudes = grb.latlons()        
        valid_date = grb.validDate
        
        valid_date = valid_date + timedelta(hours=index)
        
        # Create a DataFrame for the parameter
        df = pd.DataFrame()
        df["Latitude"] = latitudes.ravel()
        df["Longitude"] = longitudes.ravel()
        df[parameter_name] = variable_data.ravel()

        # Perform the bounding box filter
        df = crop_dataframe_to_bbox(df, bbox)

        # Convert valid date to datetime and add forecast time to it
        valid_date = pd.to_datetime(valid_date)
        df["ValidDate"] = valid_date
        
        # Store the DataFrame in the dictionary with parameter name as key
        parameter_data[parameter_name] = df
                
    grbs.close()
    
    return parameter_data

def parse_gribs(source_data_dir, output_directory, temp_directory):    
    os.makedirs(output_directory, exist_ok=True)
    delete_directory = source_data_dir

    if not os.path.isdir(source_data_dir):
        print(f"Source data directory '{source_data_dir}' does not exist. Please provide the correct path.")
        sys.exit(1)
    
    filenames = glob.glob(os.path.join(source_data_dir, "*.zip"))
    filenames = sorted(filenames)

    parameter_data = {}  # Dictionary to store data for each parameter
        
    for file in filenames:
        print("Processing", file)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(temp_directory)
            
        # Get a list of all extracted GRB files
        grb_files = [f for f in os.listdir(temp_directory) if f.endswith(".grb")]
        
        index = 0
        
        for grb_file in grb_files:
            print("Processing", grb_file)
            temp_decompressed_path = os.path.join(temp_directory, grb_file)
            
            processed_data = process_data(temp_decompressed_path, [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX], index)
            
            for parameter_name, data in processed_data.items():
                if data is not None:
                    if parameter_name == "2 metre temperature" or parameter_name == "2 metre dewpoint temperature":
                        data[parameter_name] = kelvin_to_celsius(data[parameter_name])
                    elif parameter_name == "maximum Wind 10m" or parameter_name == "10 metre V wind component":
                        data[parameter_name] = ms_to_kmh(data[parameter_name])
                    
                    date_str = os.path.splitext(grb_file)[0]  # Extract date and time from the GRB file name
                    year = date_str[4:8]
                    month = date_str[8:10]
                    day = date_str[10:12]
                    model_run = date_str[12:14]
                                
                    if parameter_name not in parameter_data:
                        parameter_data[parameter_name] = []
                    
                    data_date = data["ValidDate"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
                    parameter_data[parameter_name].append((data, data_date))
            
            index = index + 1
            
            os.remove(temp_decompressed_path)
        os.remove(file)
        
        removeDirectories(delete_directory)

    # Save data for each parameter to separate CSV files
    return save_parameter_data(parameter_data, output_directory, year, month, day, model_run)