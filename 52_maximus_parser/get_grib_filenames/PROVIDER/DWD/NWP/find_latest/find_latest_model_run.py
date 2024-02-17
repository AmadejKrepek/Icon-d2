import bz2
import re
from datetime import datetime
import requests


def download_and_extract_log_file():
    base_url = "https://opendata.dwd.de/weather/nwp/"
    file_path = "content.log.bz2"

    print("Downloading content.log.bz2...")
    response = requests.get(base_url + file_path, stream=True)

    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0

    with open(file_path, "wb") as f:
        for data in response.iter_content(chunk_size=8192):
            downloaded_size += len(data)
            f.write(data)
            progress = (downloaded_size / total_size) * 100
            print(f"Download progress: {progress:.2f}%\r", end="", flush=True)

    print("\nDownload completed.")

    print("Extracting content.log.bz2...")
    with open(file_path, "rb") as f:
        data = bz2.decompress(f.read()).decode("utf-8")
    print("Extraction completed.")

    return data


def get_latest_model_run_filename(data, parameter_name):
    lines = data.split("\n")

    latest_time = None
    latest_file = None

    latest_files = []
    latest_times = []

    for line in lines:
        parts = line.split("|")
        if len(parts) >= 3:
            file_info = parts[0]
            match = re.search(r'_\d{10}_\d{3}_\d{2}_', file_info)
            if match:
                result = match.group()
                result_extracted = result.split("_")
                time_run = result_extracted[2]
                print(result)
            else:
                print("Pattern not found.")
            file_time = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S")

            if "icon-d2" in file_info and parameter_name in file_info and "regular-lat-lon" in file_info:
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_info
                    latest_times.append(file_time)
                    latest_files.append(file_info)
                    # Keep only the last two items
                    latest_times = latest_times[-2:]
                    latest_files = latest_files[-2:]

    return latest_file
