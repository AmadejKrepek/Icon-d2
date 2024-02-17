import logging

from .find_latest.find_latest_model_run import get_latest_model_run_filename, download_and_extract_log_file
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def read_variable_names_from_file(file_path):
    try:
        logger.info(f"Started reading variable names from file: {file_path}")
        with open(file_path, "r") as f:
            variable_names = [line.strip() for line in f if line.strip()]
        logger.info(f"Finished reading variable names from file: {file_path}")
        return variable_names
    except Exception as e:
        logger.error(f"Error while reading variable names from file: {e}")


def getGribFileName(param):
    try:
        logger.info(f"Started getting grib file name for parameter: {param}")
        logger.info("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        param = param[0]

        variable_names_file = "./configuration/parameters/icon_d2.config"
        variable_names = read_variable_names_from_file(variable_names_file)
        data = download_and_extract_log_file()

        logger.info("Selected parameters:")
        logger.info(param)

        logger.info("Searching for model runs...")
        filenames = []
        latest_file = get_latest_model_run_filename(data, param)
        if latest_file:
            filenames.append(latest_file)
            logger.info(f"Latest model run filename for parameter '{param}': {latest_file}")
        else:
            logger.info(f"No regular-lat-lon model run found for parameter '{param}'.")

        if not filenames:
            logger.info("No filenames available for the selected parameters.")

        logger.info("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"Finished getting grib file name for parameter: {param}")
        return filenames
    except Exception as e:
        logger.error(f"Error while getting grile file: {e}")
