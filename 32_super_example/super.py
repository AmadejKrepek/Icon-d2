from datetime import datetime, timedelta
import xarray as xr
import pandas as pd
import argparse
import glob
import sys
import os
import bz2
import pygrib


def parse_datetime_from_filename(filename):
    """
    Assuming that the filename matches Spire's naming convention,
    this function will parse the valid forecast time from the filename.
    Example filename: `sof-d.20200401.t00z.0p125.basic.global.f006.grib2`
    """

    parts = filename.split(".")
    # Parse the forecast date from the filename
    date = parts[1]
    forecast_date = datetime.strptime(date, "%Y%M%d")
    # Strip `t` and `z` to parse the forecast issuance time (an integer representing the hour in UTC)
    issuance_time = parts[2]
    issuance_time = int(issuance_time[1:3])
    # Strip `f` to parse the forecast lead time (an integer representing the number of hours since the forecast issuance)
    lead_time = parts[-2]
    lead_time = int(lead_time[1:])
    # Combine the forecast issuance and lead times to get the valid time for this file
    hours = issuance_time + lead_time
    forecast_time = forecast_date + timedelta(hours=hours)
    # Return the datetime as a string to store it in the DataFrame
    return str(forecast_time)


def crop_dataframe_to_bbox(df, bbox):
    """
    Perform a geospatial filter on the DataFrame
    based on the specified bounding box
    """
    # Get longitude and latitude values from the DataFrame index
    longitudes = df.index.get_level_values("lon_0")
    latitudes = df.index.get_level_values("lat_0")
    # Map longitude range from (0 to 360) into (-180 to 180)
    map_function = lambda lon: (lon - 360) if (lon > 180) else lon
    remapped_longitudes = longitudes.map(map_function)
    # Create new longitude and latitude columns in the DataFrame
    df["longitude"] = remapped_longitudes
    df["latitude"] = latitudes
    # Unpack the bounding box values
    min_lat = float(bbox[0])
    max_lat = float(bbox[1])
    min_lon = float(bbox[2])
    max_lon = float(bbox[3])
    lat_filter = (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)
    lon_filter = (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)

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
            break
    grbs.close()
    
    if variable_data is None:
        return None
    
    # Create a DataFrame with the extracted data
    df = pd.DataFrame()
    df["latitude"] = latitudes.ravel()
    df["longitude"] = longitudes.ravel()
    df[variable] = variable_data.ravel()

    # Perform the bounding box filter
    df = crop_dataframe_to_bbox(df, bbox)
    
    # Parse the filename from the full filepath string
    filename = os.path.basename(filepath)
    # Convert the filename to a datetime string
    timestamp = parse_datetime_from_filename(filename)
    # Store the forecast time in a new DataFrame column
    df["time"] = timestamp
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
        help="The name of the directory containing properly formatted Spire GRIB2 data",
        required=True,
    )
    parser.add_argument(
        "--bbox",
        nargs="+",
        default=[45.1512, 47.1512, 12.1955, 16.1955],  # min_lat max_lat min_lon max_lon
        help="The bounding box used to crop the data, specified as minimum/maximum latitudes and longitudes",
    )
    args = parser.parse_args()

    if len(args.bbox) != 4:
        sys.exit(
            "The `bbox` argument must contain four values: `minlat maxlat minlon maxlon`"
        )

    # Read all data files in the specified directory
    filepath = os.path.join(args.source_data, "*.grib2.bz2")
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
            output_df = pd.concat([output_df, data])
        # Remove the temporary decompressed file
        os.remove(temp_decompressed_path)

    output_df.to_csv("output_data.csv", index=False)