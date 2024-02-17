import logging


logger = logging.getLogger(__name__)


def read_colors(file_path):
    try:
        logger.info(f"Started reading colors")
        color_configurations = {}

        with open(file_path, "r") as config_file:
            lines = config_file.readlines()

        for line in lines:
            line = line.strip()
            if line:
                config_name, colors = line.split(" = ")
                color_configurations[config_name] = colors.split(",")

        logger.info(f"Finished reading colors")
        return color_configurations
    except Exception as e:
        logger.error(f"Error while reading colors: {e}")