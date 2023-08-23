import requests
import os
import bz2
from datetime import datetime

def get_latest_model_run_filename():
    # URL of the base directory
    base_url = "https://opendata.dwd.de/weather/nwp/"
    file_path = "content.log.bz2"

    # Display script start time
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Download the content.log.bz2 file
    print("Downloading content.log.bz2...")
    response = requests.get(base_url + file_path)
    with open(file_path, "wb") as f:
        f.write(response.content)
    print("Download completed.")

    # Extract the content.log.bz2 file
    print("Extracting content.log.bz2...")
    with open(file_path, "rb") as f:
        data = bz2.decompress(f.read()).decode("utf-8")
    print("Extraction completed.")

    # Split the data into lines
    lines = data.split("\n")

    # Initialize variables to store the latest model run information
    latest_time = None
    latest_file = None

    # Iterate through the lines to find the latest model run for the specified parameter
    print("Searching for the latest model run...")
    for line in lines:
        parts = line.split("|")
        if len(parts) >= 3:
            file_info = parts[0]
            file_time = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S")
            
            if "icon-d2" in file_info and "t_2m" in file_info and "regular-lat-lon" in file_info:
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_info

    if latest_file:
        print("Latest model run filename:", latest_file)
    else:
        print("No regular-lat-lon model run found for parameter t_2m.")

    # Display script end time
    print("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return latest_file


