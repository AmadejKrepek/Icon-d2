import requests
import logging

logger = logging.getLogger(__name__)


def download_grib_file(url, output_path):
    try:
        logger.info(f"Started download from url: {url}")
        response = requests.get(url)
        with open(output_path, "wb") as f:
            logger.info(f"Writing file to: {output_path}")
            f.write(response.content)
    except Exception as e:
        logger.error(f"Error while downloading grib file from url: {url}")
