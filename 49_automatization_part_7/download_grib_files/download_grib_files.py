import requests

def download_grib_file(url, output_path):
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)