import os
import time
import logging
import traceback
from datetime import datetime

from get_grib_filenames.PROVIDER.DWD.NWP.choose_parameters import getGribFileName as getDWDGribFileNames
from get_grib_filenames.PROVIDER.ARSO.NWP.choose_parameters import getGribFileNames as getARSOGribFileNames
from download_grib_files.PROVIDER.DWD.NWP import download_ICON_D2 as downloadDWD
from download_grib_files.PROVIDER.ARSO.NWP import download_ALADIN as downloadALADIN
from parse_gribs.PROVIDER.DWD.NWP.parse_grib_files import parse_gribs as parse_gribs_DWD
from parse_gribs.PROVIDER.ARSO.NWP.parse_grib_files import parse_gribs as parse_gribs_ARSO

logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get the current time
current_time = datetime.now()

# Extract the current hour and minute
current_hour = current_time.hour
current_minute = current_time.minute


provider_models = {
    "DWD": {
        "IconD2": {
            "schedule": [(0, 44), (3, 44), (6, 44), (9, 44), (12, 49), (15, 44), (18, 44), (21, 44)],
            "params": ["t_2m", "tot_prec", "vmax_10m", "v_10m", "h_snow", "snow_con", "snow_gsp", "cape_ml", "dbz_850", "dbz_cmax"],  # Parameters for IconD2
        },
    },
    "ARSO": {
        "Aladin": {
            "schedule": [(9, 10), (23, 30), (5, 30), (11, 30), (17, 30)],
            "params": ["tot_prec"],  # Parameters for Aladin FAKE FOR NOW ONLY total precipitation
        },
    },
}

def download_and_parse_one_param(output_directory_gribs, output_directory, getGribFileNames, download_function, parse_gribs, provider_directory, model_directory, param):
    try:
        if model_directory == "IconD2":
            filenames = getGribFileNames([param])
        else:
            filenames = getGribFileNames()  # Use without parameter selection for Aladin

        print(model_directory)

        for filename in filenames:
            provider_model_directory = os.path.join(output_directory_gribs, provider_directory, model_directory)
            os.makedirs(provider_model_directory, exist_ok=True)

            resulted_gribs_directory = download_function.download_gribs(filename, provider_model_directory)

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
    current_hour = int(time.strftime("%H"))
    current_minute = int(time.strftime("%M"))

    for provider_directory, models in provider_models.items():
        for model_directory, model_info in models.items():
            try:
                model_schedule = model_info["schedule"]
                model_params = model_info["params"]

                for (scheduled_hour, scheduled_minute) in model_schedule:
                    if current_hour == scheduled_hour and current_minute == scheduled_minute:
                        logging.info(f"Provider: {provider_directory}, model: {model_directory}, param: {model_params}")
                        getGribFileNamesFunc = getDWDGribFileNames if provider_directory == "DWD" else getARSOGribFileNames
                        download_function = downloadDWD if provider_directory == "DWD" else downloadALADIN
                        parse_gribs_function = parse_gribs_DWD if provider_directory == "DWD" else parse_gribs_ARSO

                        for param in model_params:
                            print(f"Which param???? {param}")
                            download_and_parse_one_param(output_directory_gribs, output_directory, getGribFileNamesFunc, download_function, parse_gribs_function, provider_directory, model_directory, param)
            except Exception as e:
                error_message = f"Error downloading and parsing data: {str(e)}"
                traceback_str = traceback.format_exc()  # Get the traceback as a string
                logging.error(f"{error_message}\n{traceback_str}")

run_job()

while True:
    run_job()
    time.sleep(30)
