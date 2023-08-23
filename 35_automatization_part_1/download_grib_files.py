import requests
import os
from find_latest_model_run import get_latest_model_run_filename

# Base URL for the directory containing GRIB files
base_url = "https://opendata.dwd.de/weather/nwp/"

# Directory to save downloaded files
output_directory = "downloaded_grib_files"

# Call the function to get the latest model run filename
latest_model_run_filename = get_latest_model_run_filename()

if latest_model_run_filename:
    # Extract the parts of the latest model run filename
    parts = latest_model_run_filename.split("_")

    time_run = parts[-4]
    print("Time Run:", time_run)

    # Extract the date and model run time from the filename
    date_str = parts[-5]  # Extract the date part
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:8]
    model_run = date_str[8:10]  # Extract the model run time
    print("Date:", date_str)
    print("Year:", year)
    print("Month:", month)
    print("Day:", day)
    print("Model Run:", model_run)
    
    # Determine valid model run times (00, 03, 06, 09, 12, 15, 18, 21)
    valid_model_run_times = ["00", "03", "06", "09", "12", "15", "18", "21"]
    prev_model_run = None
    
    if model_run not in valid_model_run_times:
        model_run = max(valid_model_run_times, key=lambda x: abs(int(x) - int(model_run)))

    if int(time_run) < 48:
        latest_model_run_filename = latest_model_run_filename.replace(model_run, "048")
        prev_model_run = str((int(model_run) - 3) % 24).zfill(2)  # Choose previous model run
        model_run = prev_model_run

    # Remove any slashes ("/") from the filename
    latest_model_run_filename = latest_model_run_filename.replace("/", "_")
    
    # Construct the output directory path
    model_run_dir = os.path.join(output_directory, year, month, day, model_run + 'z')
    os.makedirs(model_run_dir, exist_ok=True)

    # Replace "048" with dynamic values from 000 to 047
    for new_dynamic_value in range(49):
        filename = latest_model_run_filename.replace("048", f"{new_dynamic_value:03d}")
        url = f"{base_url}/{filename}"
        
        output_path = os.path.join(model_run_dir, filename)

        response = requests.get(url)
        
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded: {filename}")

    print("Download complete.")
else:
    print("No regular-lat-lon model run found for parameter t_2m.")
