import bz2
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

    for line in lines:
        parts = line.split("|")
        if len(parts) >= 3:
            file_info = parts[0]
            file_time = datetime.strptime(parts[2], "%Y-%m-%d %H:%M:%S")

            if "icon-d2" in file_info and parameter_name in file_info and "regular-lat-lon" in file_info:
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_info

    return latest_file

def main():
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    data = download_and_extract_log_file()

    parameter_input = input("Enter parameter names separated by commas: ")
    selected_params = [param.strip() for param in parameter_input.split(",")]

    filenames = []
    for param in selected_params:
        latest_file = get_latest_model_run_filename(data, param)
        if latest_file:
            filenames.append(latest_file)
            print(f"Latest model run filename for parameter '{param}': {latest_file}")
        else:
            print(f"No regular-lat-lon model run found for parameter '{param}'.")

    if not filenames:
        print("No filenames available for the selected parameters.")

    print("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
