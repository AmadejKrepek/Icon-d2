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

def process_data(filepath, variable, bbox):
    # Load the files with GRIB2 data using pygrib
    grbs = pygrib.open(filepath)
    
    # Retrieve the desired variable
    variable_data = None
    for grb in grbs:
        if grb.name == variable:
            variable_data = grb.values
            latitudes, longitudes = grb.latlons()
            valid_date = grb.validDate
            break
    grbs.close()
    
    if variable_data is None:
        return None
    
    # Create a DataFrame with the extracted data
    df = pd.DataFrame()
    df["Latitude"] = latitudes.ravel()
    df["Longitude"] = longitudes.ravel()
    df[variable] = variable_data.ravel()

    # Perform the bounding box filter
    df = crop_dataframe_to_bbox(df, bbox)
    
    # Convert valid date to datetime and add forecast time to it
    valid_date = pd.to_datetime(valid_date)
    df["ValidDate"] = valid_date
    
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract weather data within a region")
    parser.add_argument(
        "--variable",
        type=str,
        default="2 metre temperature",
        help="The name of the weather data variable to extract",
    )
    parser.add_argument(
        "--source-data",
        type=str,
        help="The name of the directory containing the GRIB2 data files",
        required=True,
    )
    parser.add_argument(
        "--bbox",
        nargs="+",
        default=[LAT_MIN, LAT_MAX, LON_MIN, LON_MAX],
        help="The bounding box used to crop the data, specified as minimum/maximum latitudes and longitudes",
    )
    args = parser.parse_args()

    if len(args.bbox) != 4:
        sys.exit(
            "The `bbox` argument must contain four values: `minlat maxlat minlon maxlon`"
        )

    # Read all data files in the specified directory
    filenames = glob.glob(os.path.join(args.source_data, "*.grib2.bz2"))
    filenames = sorted(filenames)

    output_df = pd.DataFrame()

    for file in filenames:
        print("Processing", file)
        
        if data is not None:
            # Convert temperature from Kelvin to Celsius
            if args.variable == "2 metre temperature":
                data[args.variable] = kelvin_to_celsius(data[args.variable])
            
            # Get date from the data
            data_date = data["ValidDate"].iloc[0].strftime("%Y-%m-%d")
            
            # Create dynamic output folder
            output_folder = os.path.join("output", args.variable.replace(" ", "_"), data_date)
            os.makedirs(output_folder, exist_ok=True)
            
            # Save the processed data to CSV
            output_filename = os.path.splitext(os.path.basename(file))[0] + ".csv"
            output_path = os.path.join(output_folder, output_filename)
            data.to_csv(output_path, index=False)

    print("Script finished.")