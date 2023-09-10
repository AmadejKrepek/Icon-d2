import re
from urllib.parse import urlparse
import os
from download_grib_files.download_grib_files import download_grib_file

base_url = "https://meteo.arso.gov.si/uploads/probase/www/model/data/"

def extract_date_and_model_run_parts(url):
    # Parse the URL to extract the filename
    parsed_url = urlparse(url)
    filename = parsed_url.path.split("/")[-1]

    # Use regular expressions to match the date and model run parts
    match = re.match(r'nwp_(\d{8})-(\d{4})\.zip', filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        model_run = time_str  # Extract the time part (HHmm)
        return year, month, day, model_run
    else:
        # Handle the case where the filename format doesn't match
        print('It does not match!')
        return None


def download_gribs(latest_model_run_url, output_directory):
    if latest_model_run_url:
        year, month, day, model_run = extract_date_and_model_run_parts(latest_model_run_url)
        if year and month and day and model_run:
            # Replace the last two digits of model_run with 'z'
            model_run = model_run[:-2] + 'z'
            
            # Create the directory structure if it doesn't exist
            parameter_name = "all"
            parameter_name_directory = os.path.join(output_directory, parameter_name)
            year_directory = os.path.join(parameter_name_directory, year)
            month_directory = os.path.join(year_directory, month)
            day_directory = os.path.join(month_directory, day)
            model_run_directory = os.path.join(day_directory, model_run)
            
            os.makedirs(model_run_directory, exist_ok=True)
            
            # Generate the local filename for the downloaded ZIP file
            local_filename = f"{parameter_name}_{year}_{month}_{day}_{model_run}.zip"
            local_filepath = os.path.join(model_run_directory, local_filename)
            
            print(latest_model_run_url)
            print(local_filepath)
            # Download the file using the provided function
            download_grib_file(latest_model_run_url, local_filepath)
            
            print(f"Downloaded {local_filename} to {model_run_directory}")
            return model_run_directory
        else:
            print("Invalid filename format")
            return None
    else:
        print("No GRIB files found for Aladin")
        return None