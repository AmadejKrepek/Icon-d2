import concurrent
from datetime import timedelta, datetime, timezone

from database.db_connector import create_db_connection_async
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

db_pool = None


async def create_db_pool():
    global db_pool
    # Your code to create the database connection pool
    db_pool = await create_db_connection_async()


async def close_db_pool():
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


def ms_to_kmh(ms):
    return ms * 3.6


def pa_to_hpa(pa):
    return pa * 0.01


def whole_to_percent(value):
    if 0 <= value <= 1:
        return value * 100
    else:
        raise ValueError("Input value must be in the range [0, 1]")


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
        # 4. Vertical Level
        vertical_level = grb.level
        # 2. Units
        units = grb.units

        # 3. Type of Level
        type_of_level = grb.typeOfLevel
        parameter_name = grb.name + "_" + str(vertical_level) + "_" + type_of_level

        variable_data = grb.values
        latitudes, longitudes = grb.latlons()
        valid_date = grb.validDate

        valid_date = valid_date + timedelta(hours=index)

        # Create a DataFrame for the parameter
        df = pd.DataFrame()
        df["Latitude"] = latitudes.ravel()
        df["Longitude"] = longitudes.ravel()
        df[parameter_name] = variable_data.ravel()

        df[parameter_name] = convertToOneDecimalPlace(df, parameter_name)

        # Perform the bounding box filter
        df = crop_dataframe_to_bbox(df, bbox)
        df = delete_coordinates(df)

        # Convert valid date to datetime and add forecast time to it
        valid_date = pd.to_datetime(valid_date)
        df["ValidDate"] = valid_date

        # Store the DataFrame in the dictionary with parameter name as key
        parameter_data[parameter_name] = df

    grbs.close()

    return parameter_data


def process_file(file_index_pair):
    index, temp_decompressed_path = file_index_pair
    return process_data(temp_decompressed_path, [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX], index)


async def parse_gribs(source_data_dir, output_directory, temp_directory):
    os.makedirs(output_directory, exist_ok=True)
    delete_directory = source_data_dir

    if not os.path.isdir(source_data_dir):
        print(f"Source data directory '{source_data_dir}' does not exist. Please provide the correct path.")
        sys.exit(1)

    filenames = glob.glob(os.path.join(source_data_dir, "*.zip"))
    filenames = sorted(filenames)

    start_date = None
    end_date = None

    parameter_data = {}  # Dictionary to store data for each parameter
    for file in filenames:
        print("Processing", file)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(temp_directory)

        # Get a list of all extracted GRB files
        grb_files = [f for f in os.listdir(temp_directory) if f.endswith(".grb")]
        sorted_grb_files = sorted(grb_files)
        sorted_file_list = sorted(sorted_grb_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        timestamp_to_match = sorted_file_list[0].split('_')[
            1]  # Extract the timestamp value from the first item in the list

        filtered_files = [file for file in sorted_file_list if file.split('_')[1] == timestamp_to_match]
        index = 0

        # Create a list of (index, temp_decompressed_path) pairs using enumerate and temp_directory
        file_index_pairs = [(index, os.path.join(temp_directory, grb_file)) for index, grb_file in
                            enumerate(filtered_files)]

        # Create a ProcessPoolExecutor
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Process files in parallel
            processed_data_list = list(executor.map(process_file, file_index_pairs))

        for processed_data in processed_data_list:
            for parameter_name, data in processed_data.items():
                if data is not None:
                    if "temperature" in parameter_name.lower():
                        data[parameter_name] = kelvin_to_celsius(data[parameter_name])
                    elif "wind" in parameter_name.lower():
                        data[parameter_name] = ms_to_kmh(data[parameter_name])
                    elif "pressure" in parameter_name.lower():
                        data[parameter_name] = pa_to_hpa(data[parameter_name])
                    # elif "humidity" in parameter_name.lower():
                    # data[parameter_name] = whole_to_percent(data[parameter_name])

                    # Split the filename using "/" as the separator
                    parts = file.split("/")

                    # Extract provider_name and model_name from the appropriate positions in the split parts
                    provider_name = parts[3]
                    model_name = parts[4]
                    first_file = filtered_files[0]
                    date_str = os.path.splitext(first_file)[0]
                    year = date_str[4:8]
                    month = date_str[8:10]
                    day = date_str[10:12]
                    model_run = date_str[12:14]
                    last_model_run = model_run

                    if parameter_name not in parameter_data:
                        parameter_data[parameter_name] = []

                    if start_date is None:
                        # Create a UTC timezone object
                        utc_timezone = timezone.utc

                        # Create a datetime object in UTC time zone
                        start_date = datetime(int(year), int(month), int(day), int(model_run), 0, 0,
                                              tzinfo=utc_timezone)
                        end_date = start_date + timedelta(days=3)

                    data_date = data["ValidDate"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
                    parameter_data[parameter_name].append((data, data_date))

            index = index + 1

        os.remove(file)

        removeDirectories(delete_directory)

        await create_db_pool()

        for parameter_name, parameter_entries in parameter_data.items():
            # start_date = parameter_data[parameter_name][0][0]['ValidDate'].iloc[0]
            last_model_run = remove_leading_zeros(last_model_run)
            parameter_table_name = parameter_name.replace(" ", "_").lower()
            parameter_table_name = parameter_table_name + "_" + model_name.lower()
            await create_parameter_table(db_pool, parameter_table_name)

            if not await check_model_run_exists(db_pool, parameter_table_name, last_model_run, start_date):
                provider_id = await get_provider_id(db_pool, provider_name)
                model_id = await get_model_id(db_pool, model_name)
                await insert_parameter_data(db_pool, provider_id, model_id, parameter_name,
                                            parameter_data[parameter_name], last_model_run,
                                            parameter_table_name, start_date, end_date)

            # Save data for each parameter to separate CSV files
            # save_parameter_data(parameter_data, output_directory, year, month, day, model_run)

        # start_date = parameter_data[parameter_name][0][0]['ValidDate'].iloc[0]
        # Save data for each parameter to separate CSV files
        # save_parameter_data(parameter_data, output_directory, year, month, day, model_run)
    await close_db_pool()

    # return None
