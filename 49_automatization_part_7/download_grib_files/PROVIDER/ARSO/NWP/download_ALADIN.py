import re
from download_grib_files.download_grib_files import download_grib_file

base_url = "https://meteo.arso.gov.si/uploads/probase/www/model/data/"

def extract_date_and_model_run_parts(filename):
    # Use regular expressions to match the date and model run parts
    match = re.match(r'nwp_(\d{8}-\d{4})\.zip', filename)
    
    if match:
        date_and_time_str = match.group(1)
        year = date_and_time_str[:4]
        month = date_and_time_str[4:6]
        day = date_and_time_str[6:8]
        model_run = date_and_time_str[9:13]  # Extract the time part (HHmm)
        return year, month, day, model_run
    else:
        # Handle the case where the filename format doesn't match
        print('It does not match!')
        return None


def download_gribs(latest_model_run_filename, output_directory):
    if latest_model_run_filename:
        year, month, day, model_run = extract_date_and_model_run_parts(latest_model_run_filename)
        print(f'{year} {month} {day} {model_run}')
    else: 
        print(f'No GRIB files found for Aladin')