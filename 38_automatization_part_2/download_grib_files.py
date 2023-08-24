import requests
import os
import re

# Base URL for the directory containing GRIB files
base_url = "https://opendata.dwd.de/weather/nwp/"

# Directory to save downloaded files
output_directory = "downloaded_grib_files"

def extract_parameter_name(filename):
    parameter_name = filename.split(".grib2.bz2")[0]
    parts = parameter_name.split("_")
    parameter_name = "_".join(parts[-2:])  # Extract the last two parts
    if parameter_name.startswith("icon-"):
        parameter_name = parameter_name[len("icon-"):]
    return parameter_name

filename = "icon-d2_germany_regular-lat-lon_single-level_2023082415_000_2d_t_2m.grib2.bz2"
parameter_name = extract_parameter_name(filename)
print("Parameter Name:", parameter_name)

def extract_date_and_model_run_parts(filename):
    parts = filename.split("_")
    parameter_name = extract_parameter_name(filename)
    date_str = parts[-5]
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:8]
    model_run = date_str[8:10]
    return year, month, day, model_run, parameter_name

def determine_model_run(model_run, time_run):
    valid_model_run_times = ["00", "03", "06", "09", "12", "15", "18", "21"]
    if model_run not in valid_model_run_times:
        model_run = max(valid_model_run_times, key=lambda x: abs(int(x) - int(model_run)))

    if int(time_run) < 48:
        model_run = "048"
        prev_model_run = str((int(model_run) - 3) % 24).zfill(2)
        return model_run, prev_model_run
    return model_run, None

def download_grib_file(url, output_path):
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

def download_gribs(latest_model_run_filename):
    if latest_model_run_filename:
        year, month, day, model_run, parameter_name = extract_date_and_model_run_parts(latest_model_run_filename)
        time_run = latest_model_run_filename.split("_")[-4]
        
        model_run, prev_model_run = determine_model_run(model_run, time_run)
        
        model_run_dir = os.path.join(output_directory, parameter_name, year, month, day, model_run + 'z')
        os.makedirs(model_run_dir, exist_ok=True)

        for new_dynamic_value in range(49):
            filename = latest_model_run_filename.replace("048", f"{new_dynamic_value:03d}")
            url = f"{base_url}/{filename}"
            original_filename = filename.split("/")[-1]
            output_path = os.path.join(model_run_dir, original_filename)

            download_grib_file(url, output_path)

            print(f"Downloaded: {original_filename}")

        print("Download complete.")
    else:
        print("No regular-lat-lon model run found for parameter t_2m.")