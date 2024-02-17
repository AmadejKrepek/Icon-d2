import os
import logging


logger = logging.getLogger(__name__)


def removeDirectories(deleted_directory):
    while os.path.basename(deleted_directory) != "downloaded_grib_files":
        try:
            if os.path.exists(deleted_directory) and os.path.isdir(deleted_directory):
                os.rmdir(deleted_directory)
        except OSError:
            logger.error("An error occurred while removing the directory.")

        deleted_directory = os.path.dirname(deleted_directory)
