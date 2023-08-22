import requests
import os

# URL for the directory containing GRIB files
base_url = "https://opendata.dwd.de/weather/nwp/icon-d2/grib/03/t_2m/"

# Directory to save downloaded files
output_directory = "downloaded_grib_files"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)
# Loop through the dynamic values from 000 to 047
for dynamic_value in range(48):
    filename = f"icon-d2_germany_regular-lat-lon_single-level_2023082203_{dynamic_value:03d}_2d_t_2m.grib2.bz2"
    url = f"{base_url}/{filename}"
    output_path = os.path.join(output_directory, filename)

    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Downloaded: {filename}")

print("Download complete.")