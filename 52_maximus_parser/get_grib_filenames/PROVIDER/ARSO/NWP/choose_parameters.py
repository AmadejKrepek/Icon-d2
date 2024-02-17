from .find_latest.find_latest_model_run import get_latest_model_run_filenames
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def getGribFileNames():
    logger.info(f"Started getting grib file names")
    logger.info(f"Script started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    base_url = "https://meteo.arso.gov.si/uploads/probase/www/model/data/"
    filenames = get_latest_model_run_filenames(base_url)

    if not filenames:
        logger.warning("No filenames available for the selected parameters.")

    logger.info(f"Script finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Finished getting grib file names")
    return filenames
