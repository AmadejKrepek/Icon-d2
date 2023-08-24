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
        default=[LAT_MIN, LAT_MAX, LON_MIN, LON_MAX],  # min_lat max_lat min_lon max_lon
        help="The bounding box used to crop the data, specified as minimum/maximum latitudes and longitudes",
    )
    args = parser.parse_args()

    if len(args.bbox) != 4:
        sys.exit(
            "The `bbox` argument must contain four values: `minlat maxlat minlon maxlon`"
        )

    # Read all data files in the specified directory
    filepath = os.path.join(args.source_data, "*2d_t_2m.grib2.bz2")
    filenames = glob.glob(filepath)
    filenames = sorted(filenames)

    output_df = pd.DataFrame()

    for file in filenames:
        print("Processing ", file)
        # Decompress the file and read the decompressed data
        with bz2.BZ2File(file, 'rb') as compressed_file:
            data = compressed_file.read()
        # Create a temporary file to hold the decompressed data
        original_filename = os.path.splitext(os.path.basename(file))[0]  # Extract original filename
        temp_decompressed_path = f"{original_filename}_decompressed.grib2"  # Adjust the decompressed filename
        with open(temp_decompressed_path, 'wb') as temp_file:
            temp_file.write(data)
        # Process the data
        data = process_data(temp_decompressed_path, args.variable, args.bbox)
        if data is not None:
            
            # Convert temperature from Kelvin to Celsius
            if args.variable == "2 metre temperature":
                data[args.variable] = kelvin_to_celsius(data[args.variable])
            
            output_df = pd.concat([output_df, data])
        # Remove the temporary decompressed file
        os.remove(temp_decompressed_path)

    output_df.to_csv("output_data.csv", index=False)