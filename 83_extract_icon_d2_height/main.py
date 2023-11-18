import requests
import pygrib
from io import BytesIO

def download_grib_file(url):
    response = requests.get(url)
    return BytesIO(response.content)

def print_grib_info_from_bytesio(grib_data):
    grbs = pygrib.fromstring(grib_data.getvalue())

    for idx, grb in enumerate(grbs, start=1):
        print(f"Index {idx}: {grb}")

    grbs.close()

if __name__ == "__main__":
    grib_url = "https://opendata.dwd.de/weather/nwp/icon-d2/grib/09/hsurf/icon-d2_germany_regular-lat-lon_time-invariant_2023111509_000_0_hsurf.grib2.bz2"

    # Download the GRIB file from the URL
    grib_data = download_grib_file(grib_url)

    # Print information about all available messages in the GRIB file from the URL
    print_grib_info_from_bytesio(grib_data)
