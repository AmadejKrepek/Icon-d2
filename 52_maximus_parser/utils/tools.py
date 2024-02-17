import sys
import logging


logger = logging.getLogger(__name__)


def changeCoordinatesConfiguration(model_directory):
    logger.info(f"Changing coordinates configuration")
    if model_directory == "IconD2":
        return "./configuration/coordinates/icon_d2_lat_lon.csv"
    elif model_directory == "Aladin":
        return "./configuration/coordinates/aladin_lat_lon.csv"
    else:
        print("Invalid configuration coordinates for this model. Exiting.")
        sys.exit(1)


def changeGroupedCoordinatesConfiguration(model_directory):
    try:
        logger.info(f"Changing coordinates configuration")
        if model_directory == "IconD2":
            return "./configuration/coordinates/grouped/icon_d2_lat_lon_grouped.csv"
        elif model_directory == "Aladin":
            return "./configuration/coordinates/grouped/aladin_lat_lon_grouped.csv"
        else:
            logger.error("Invalid configuration coordinates for this model. Exiting.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"{e}")

