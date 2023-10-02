import requests
from bs4 import BeautifulSoup
import re


def get_latest_model_run_filenames(base_url):
    print("Fetching available model run filenames...")
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {base_url}. Status code: {response.status_code}")
        return []

    latest_files = []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Define the date format (yyyyMMdd)
    date_format = r'\d{8}'

    for link in soup.find_all('a', href=True):
        href = link['href']
        match = re.search(date_format, href)
        if match:
            date = match.group(0)

            # Extract the model run (HHmm) from the filename
            model_run_match = re.search(r'nwp_\d{8}-(\d{4})\.zip', href)
            if model_run_match:
                model_run = model_run_match.group(1)
                file_url = f"{base_url}/nwp_{date}-{model_run}.zip"
                latest_files.append(file_url)

    return [latest_files[0]]
