import requests
import os
import re

# Base URL for the directory containing GRIB files
base_url = "https://opendata.dwd.de/weather/nwp/"

def extract_parameter_name(filename):
    parameter_name = filename.split(".grib2.bz2")[0]
    parts = parameter_name.split("_")
    parameter_name = "_".join(parts[-2:])  # Extract the last two parts
    if parameter_name.startswith("icon-"):
        parameter_name = parameter_name[len("icon-"):]
    return parameter_name

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

    print("Model run:", model_run)
    print("Time run:", time_run)

    adjusted_model_run = model_run
    if int(time_run) < 48:
        adjusted_model_run = str(int(model_run) - 3).rjust(2, "0")

    print("Adjusted model run:", adjusted_model_run)
    return adjusted_model_run, None


def download_grib_file(url, output_path):
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

def download_gribs(latest_model_run_filename, output_directory):
    if latest_model_run_filename:
        year, month, day, model_run, parameter_name = extract_date_and_model_run_parts(latest_model_run_filename)
        time_run = latest_model_run_filename.split("_")[-4]
        
        model_run, prev_model_run = determine_model_run(model_run, time_run)
        
        model_run_dir = os.path.join(output_directory, parameter_name, year, month, day, model_run + 'z')
        os.makedirs(model_run_dir, exist_ok=True)

        # Define a regular expression pattern to match the numerical part between "000" and "048"
        pattern = r'_(0[0-9]|0[0-3][0-9]|048)_'
        model_run_pattern = r'\d{10}'

        # Find the match using the pattern
        match = re.search(pattern, latest_model_run_filename)
        model_run_match = re.search(model_run_pattern, latest_model_run_filename)
        
        filename = latest_model_run_filename
        for new_dynamic_value in range(49):
            if match:
                matched_substring = match.group()
                filename = filename.replace(matched_substring, f"{new_dynamic_value:03d}")
            if model_run_match:
                matched_model_run_substring = model_run_match.group()
                filename = latest_model_run_filename.replace(matched_model_run_substring, f'{year}{month}{day}{model_run}')
                
            filename = filename.replace("048", f"{new_dynamic_value:03d}")
            filename = filename.replace("__", "_")
            url = f"{base_url}/{filename}"
            original_filename = filename.split("/")[-1]
            output_path = os.path.join(model_run_dir, original_filename)

            download_grib_file(url, output_path)

            print(f"Downloaded: {original_filename}")

        print("Download complete.")
        return model_run_dir
    else:
        print("No regular-lat-lon model run found for parameter t_2m.")