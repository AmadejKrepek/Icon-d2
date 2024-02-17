import concurrent
import logging
from datetime import timedelta, timezone, datetime

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
import bz2
import pygrib
import logging


logger = logging.getLogger(__name__)


# to nicely display maps we need to adjust coordinates to make sure it fits
DEVIATION_LAT_MIN = 0.15
DEVIATION_LAT_MAX = 0.01
DEVIATION_LON_MIN = 0.02
DEVIATION_LON_MAX = 0.0045

LAT_MIN = 45.1512 - DEVIATION_LAT_MIN
LAT_MAX = 47.1212 + DEVIATION_LAT_MAX
LON_MIN = 12.9955 - DEVIATION_LON_MIN
LON_MAX = 16.7455 + DEVIATION_LON_MAX

db_pool = None


async def create_db_pool():
    try:
        logger.info(f"Started creating db pool")
        global db_pool
        # Your code to create the database connection pool
        db_pool = await create_db_connection_async()
        logger.info(f"Finished creating db pool")
    except Exception as e:
        logger.error(f"Error while creating db pool: {e}")


async def close_db_pool():
    try:
        logger.info(f"Started closing db pool")
        global db_pool
        if db_pool:
            db_pool.close()
            await db_pool.wait_closed()
            logger.info(f"Finished closing db pool")
    except Exception as e:
        logger.error(f"Error while closing db pool: {e}")


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


def ms_to_kmh(ms):
    return ms * 3.6


def replace_zeros_with_null(value):
    if value == 0.0:
        return None
    return value


def crop_dataframe_to_bbox(df, bbox):
    try:
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
    except Exception as e:
        logger.error(f"Error while cropping dataframe to bbox: {e}")


def process_data(filepath, bbox, index):
    try:
        logger.info(f"Processing grib data for file {filepath} with index: {index}")
        # Load the files with GRIB2 data using pygrib
        grbs = pygrib.open(filepath)

        # Retrieve the desired variable
        variable_data = None
        parameter_name = None

        inside_index = 0

        df_array = []

        for grb in grbs:
            variable_data = grb.values
            latitudes, longitudes = grb.latlons()
            valid_date = grb.validDate
            parameter_name = grb.name
            base_datetime = valid_date

            keywords = ['maximum Wind 10m']  # 'Base reflectivity' #'Base reflectivity (cmax)'

            accepted_parameters = [
                'Convective Snowfall water equivalent (s)',
                'Large-Scale snowfall - water equivalent (Accumulation)',
                'Total Precipitation'
            ]

            if any(keyword in parameter_name for keyword in keywords):
                time_range = timedelta(hours=index)
                valid_date = base_datetime + time_range
            elif parameter_name in accepted_parameters:
                if len(df_array) >= 1:
                    latest_df = df_array[-1]
                    latest_valid_date = latest_df['ValidDate'].iloc[-1]  # Assuming 'ValidDate' is the column name
                    latest_valid_date_timestamp = pd.Timestamp(latest_valid_date)
                    latest_time_range_minutes = timedelta(minutes=15)
                    valid_date = latest_valid_date_timestamp + latest_time_range_minutes
                else:
                    latest_time_range_hours = timedelta(hours=index)
                    valid_date = base_datetime + latest_time_range_hours
                inside_index += 1

            df_unique = create_multiple_dataframe_15min(latitudes, longitudes, parameter_name, variable_data, bbox,
                                                        valid_date)
            df_array.append(df_unique)
        grbs.close()
        logger.info(f"Processing grib data for file: {filepath} with index: {index}")

        if variable_data is None:
            return None

        if len(df_array) == 1:
            return df_array, parameter_name
        else:
            return df_array, parameter_name
    except Exception as e:
        logger.error(f"Error while processing grib data for file: {filepath} with index: {index}, error: {e}")


def create_multiple_dataframe_15min(latitudes, longitudes, parameter_name, variable_data, bbox, valid_date):
    logger.info("Parsing multiple dataframe 15min intervals...")
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
    logger.info(f"Finished parsing multiple dataframe 15min intervals")
    return df


def create_output_folders(year, month, day, model_run, parameter_name, output_directory):
    try:
        logger.info(f"Started creating output folders")
        model_run_dir = os.path.join(output_directory, parameter_name.replace(" ", "_"), year, month, day, model_run + "z")
        os.makedirs(model_run_dir, exist_ok=True)
        logger.info(f"Finished creating output folders")
        return model_run_dir
    except Exception as e:
        logger.error(f"Error while creating output folders: {e}")


def save_parameter_data(parameter_data, output_directory, year, month, day, model_run):
    try:
        logger.info(f"Started saving parameter data")
        for parameter_name, data_list in parameter_data.items():
            parameter_df_list = [data_item[0] for data_item in data_list]
            combined_df = pd.concat(parameter_df_list, ignore_index=True)
            parameter_name = parameter_name.replace(" ", "_")
            model_run_dir = create_output_folders(year, month, day, model_run, parameter_name, output_directory)
            output_filename = f"{parameter_name}_{year}_{month}_{day}_{model_run}.csv"
            output_path = os.path.join(model_run_dir, output_filename)
            combined_df.to_csv(output_path, index=False)
        logger.info(f"Finished saving parameter data")
        return output_path
    except Exception as e:
        logger.error(f"Error while saving parameter data: {e}")


def process_file(file_index_pair):
    index, temp_decompressed_path = file_index_pair
    return process_data(temp_decompressed_path, [LAT_MIN, LAT_MAX, LON_MIN, LON_MAX], index)


def search_combine_merge(source_data_dir):
    filenames = glob.glob(os.path.join(source_data_dir, "*.grib2.bz2"))
    filenames = sorted(filenames)
    print(filenames)

    parameter_data = {}  # Dictionary to store data for each parameter

    index = 0

    last_model_run = None

    for file in filenames:
        with bz2.BZ2File(file, 'rb') as compressed_file:
            data = compressed_file.read()
        original_filename = os.path.splitext(os.path.basename(file))[0]
        temp_decompressed_path = f"{original_filename}_decompressed.grib2"
        print(temp_decompressed_path)
        print("Write to file")
        with open(temp_decompressed_path, 'wb') as temp_file:
            print("Started writing to file")
            print(temp_file)
            temp_file.write(data)
        print("FInished writing to file")
        # Create a list of (index, temp_decompressed_path) pairs using enumerate and temp_directory
        file_index_pairs = [(index, temp_decompressed_path)]
        index = index + 1
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Process files in parallel
            processed_data_list = list(executor.map(process_file, file_index_pairs))

        print("Getting past this processing inside...")
        start_date = None
        end_date = None

        if len(data) > 0:
            for data_list, parameter_name in processed_data_list:
                data = data_list[0]
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

                if start_date is None:
                    # Create a UTC timezone object
                    utc_timezone = timezone.utc

                    # Create a datetime object in UTC time zone
                    start_date = datetime(int(year), int(month), int(day), int(model_run), 0, 0, tzinfo=utc_timezone)
                    end_date = start_date + timedelta(days=2)

                data_date = data["ValidDate"].iloc[0].strftime("%Y-%m-%d")
                parameter_data[parameter_name].append((data, data_date))

        print(f"Removing temp decompressed: {temp_decompressed_path}")
        os.remove(temp_decompressed_path)
        print(f"Removing file: {file}")
        os.remove(file)
    print("Finishing this")
    return last_model_run, model_name, provider_name, parameter_name, start_date, end_date, parameter_data


async def parse_gribs(source_data_dir, output_directory, output_directory_gribs):
    try:
        logger.info(f"Started parsing grib files with source_data_dir: {source_data_dir}, output_dir: {output_directory}")
        os.makedirs(output_directory, exist_ok=True)
        deleted_directory = source_data_dir

        if not os.path.isdir(source_data_dir):
            logger.error(f"Source data directory '{source_data_dir}' does not exist. Please provide the correct path.")
            sys.exit(1)

        # Create a list of (index, temp_decompressed_path) pairs using enumerate and temp_directory
        try:
            logger.info(f"Started multiple core process for reading grb files")
            file_index_pairs = [source_data_dir]
            with concurrent.futures.ProcessPoolExecutor() as executor:
                # Process files in parallel
                created_data = list(executor.map(search_combine_merge, file_index_pairs))
            logger.info(f"Finished multiple core process for reading grb files")

            if len(created_data) < 1:
                raise ValueError("There is no data to insert in parse grib files!")

            last_model_run = created_data[0][0]
            model_name = created_data[0][1]
            provider_name = created_data[0][2]
            parameter_name = created_data[0][3]
            start_date = created_data[0][4]
            end_date = created_data[0][5]
            parameter_data = created_data[0][6]
            removeDirectories(deleted_directory)
        except Exception as e:
            logger.error(f"Error while multiprocessing and extracting data: {e}")

        await create_db_pool()

        last_model_run = remove_leading_zeros(last_model_run)
        parameter_table_name = parameter_name.replace(" ", "_").lower()
        parameter_table_name = parameter_table_name + "_" + model_name.lower()
        await create_parameter_table(db_pool, parameter_table_name)

        if not await check_model_run_exists(db_pool, parameter_table_name, last_model_run, start_date):
            provider_id = await get_provider_id(db_pool, provider_name)
            model_id = await get_model_id(db_pool, model_name)
            await insert_parameter_data(db_pool, provider_id, model_id, parameter_name, parameter_data[parameter_name],
                                        last_model_run,
                                        parameter_table_name,
                                        start_date, end_date)

        # Save data for each parameter to separate CSV files
        # return save_parameter_data(parameter_data, output_directory, year, month, day, model_run)
        # return None
    except Exception as e:
        logger.error(f"Error while parsing grib files. {e}")
