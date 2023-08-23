import requests
import os
from find_latest_model_run import get_latest_model_run_filename

# Base URL for the directory containing GRIB files
base_url = "https://opendata.dwd.de/weather/nwp/"

# Directory to save downloaded files
output_directory = "downloaded_grib_files"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Call the function to get the latest model run filename
latest_model_run_filename = get_latest_model_run_filename()

if latest_model_run_filename:
    print("Latest model run filename:", latest_model_run_filename)

    # Remove the dot from the filename
    latest_model_run_filename = latest_model_run_filename.replace("./", "")

    # Replace "048" with dynamic values from 000 to 047
    for new_dynamic_value in range(49):
        filename = latest_model_run_filename.replace("048", f"{new_dynamic_value:03d}")
        url = f"{base_url}/{filename}"
        output_path = os.path.join(output_directory, filename)

        response = requests.get(url)
        
        # Create the output path's directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded: {filename}")

    print("Download complete.")
else:
    print("No regular-lat-lon model run found for parameter t_2m.")
