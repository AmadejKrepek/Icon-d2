import os
import re
from download_grib_files.download_grib_files import download_grib_file
import logging

base_url = "https://opendata.dwd.de/weather/nwp/"

logger = logging.getLogger(__name__)


def extract_parameter_name(filename):
    try:
        logger.info(f"Started extracting parameter name with filename: {filename}")
        parameter_name = filename.split(".grib2.bz2")[0]
        parts = parameter_name.split("_")
        parameter_name = "_".join(parts[-2:])  # Extract the last two parts
        if parameter_name.startswith("icon-"):
            parameter_name = parameter_name[len("icon-"):]
        logger.info(f"Finished extracting parameter name with filename: {filename}")
        return parameter_name
    except Exception as e:
        logger.error(f"Error while extracting parameter name: {e}")


def extract_date_and_model_run_parts(filename):
    try:
        logger.info(f"Extracting date and model run parts for file: {filename}")
        parts = filename.split("_")
        parameter_name = extract_parameter_name(filename)
        date_str = parts[-5]
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        model_run = date_str[8:10]
        logger.info(f"Finished extracting date and model run parts for file: {filename}")
        return year, month, day, model_run, parameter_name
    except Exception as e:
        logger.error(f"Error while extracting date and model run parts: {e}")


def determine_model_run(model_run, time_run):
    try:
        logger.info(f"Started determining model run with model_run: {model_run} and time_run: {time_run}")
        valid_model_run_times = ["00", "03", "06", "09", "12", "15", "18", "21"]

        if model_run not in valid_model_run_times:
            model_run = max(valid_model_run_times, key=lambda x: abs(int(x) - int(model_run)))

        logger.info("Possibly updated Model run:", model_run)

        adjusted_model_run = model_run
        if int(time_run) < 48:
            adjusted_model_run = str(int(model_run) - 3).rjust(2, "0")

        logger.info("Possibly adjusted model run:", adjusted_model_run)
        logger.info(f"Finished determining model run with new model run: {adjusted_model_run} "
                    f"and new time_run: {time_run}")
        return adjusted_model_run, model_run
    except Exception as e:
        logger.error(f"Error while determining model run: {e}")


def download_gribs(latest_model_run_filename, output_directory):
    try:
        logger.info(f"Started downloading gribs for latest_model_run_filename: {latest_model_run_filename}"
                    f" and output_directory: {output_directory}")
        if latest_model_run_filename:
            year, month, day, model_run, parameter_name = extract_date_and_model_run_parts(latest_model_run_filename)
            time_run = latest_model_run_filename.split("_")[-4]

            model_run, prev_model_run = determine_model_run(model_run, time_run)

            model_run_dir = os.path.join(output_directory, parameter_name, year, month, day, model_run + 'z')
            os.makedirs(model_run_dir, exist_ok=True)

            # Define a regular expression pattern to match the numerical part between "000" and "048"
            pattern = r'_(0[0-9]|0[0-3][0-9]|048)_'
            model_run_pattern = r'\d{10}'
            # Define a pattern to match the "grib" followed by a slash and a number
            first_model_run_pattern = r'grib/(\d+)'

            # Find the match using the pattern
            match = re.search(pattern, latest_model_run_filename)
            model_run_match = re.search(model_run_pattern, latest_model_run_filename)
            first_model_run_match = re.search(first_model_run_pattern, latest_model_run_filename)

            filename = latest_model_run_filename
            for new_dynamic_value in range(49):
                if match:
                    matched_substring = match.group()
                    filename = filename.replace(matched_substring, f"{new_dynamic_value:03d}")
                if model_run_match:
                    matched_model_run_substring = model_run_match.group()
                    filename = latest_model_run_filename.replace(matched_model_run_substring,
                                                                 f'{year}{month}{day}{model_run}')
                if first_model_run_match:
                    matched_first_model_run_value = first_model_run_match.group()
                    filename = filename.replace(matched_first_model_run_value, f'grib/{model_run}')

                filename = filename.replace(f"{time_run}", f"{new_dynamic_value:03d}")
                url = f"{base_url}/{filename}"
                original_filename = filename.split("/")[-1]
                output_path = os.path.join(model_run_dir, original_filename)
                logger.info(f"Output path for download location: {output_path}")
                download_grib_file(url, output_path)

            logger.info(f"Finished downloading gribs for latest_model_run_filename: {latest_model_run_filename}"
                        f" and output_directory: {output_directory}")
            return model_run_dir
        else:
            logger.warning(f"No regular-lat-lon model run found for parameter.")
    except Exception as e:
        logger.error(f"Error while downloading icond2 gribs: {e}")