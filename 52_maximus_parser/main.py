import os
import time
import logging

from get_grib_filenames.PROVIDER.DWD.NWP.choose_parameters import getGribFileNames as getDWDGribFileNames
from download_grib_files.PROVIDER.DWD.NWP import download_ICON_D2 as downloadDWD
from parse_gribs.PROVIDER.DWD.NWP.parse_grib_files import parse_gribs as parse_gribs_DWD

logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

provider_models = {
    "DWD": ["IconD2"],
}

selected_params = ["tot_prec"]

def download_and_parse(output_directory_gribs, output_directory, getGribFileNames, download_function, parse_gribs, provider_directory, model_directory):
    try:
        filenames = getGribFileNames(selected_params)

        for filename in filenames:
            # Create provider and model directories
            provider_model_directory = os.path.join(output_directory_gribs, provider_directory, model_directory)
            os.makedirs(provider_model_directory, exist_ok=True)

            resulted_gribs_directory = download_function.download_gribs(filename, provider_model_directory)
        
        if (resulted_gribs_directory is None):
            return None

        # Append provider_directory and model_directory after output_directory
        resulted_csv_file = parse_gribs(resulted_gribs_directory, os.path.join(output_directory, provider_directory, model_directory), output_directory_gribs)
        print(f"Downloaded and parsed {resulted_csv_file}")
        return resulted_csv_file
    except Exception as e:
        print("Error during download and parse:", e)
        return None

storage_directory = "./data"
output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
output_directory = os.path.join(storage_directory, "output")

def run_job():
    for provider_directory, available_models in provider_models.items():
        for model_directory in available_models:
            try:
                logging.info(f"Provider: {provider_directory}, model: {model_directory}")

                resulted_csv_file = download_and_parse(output_directory_gribs, output_directory, getDWDGribFileNames, downloadDWD, parse_gribs_DWD, provider_directory, model_directory)

                logging.info("Download and parse completed successfully.")
            except Exception as e:
                logging.error(f"Error downloading and parsing data: {str(e)}")


# Define the specified hours
specified_hours = [0, 3, 6, 9, 12, 15, 18, 21]

run_job()

while True:
    current_hour = int(time.strftime("%H"))
    current_minute = int(time.strftime("%M"))

    if current_hour in specified_hours and current_minute == 44:
        run_job()  # Call the function when the time matches
        time.sleep(60)  # Sleep for a minute to avoid repeated calls in the same minute
    else:
        time.sleep(30)  # Check every 30 seconds
