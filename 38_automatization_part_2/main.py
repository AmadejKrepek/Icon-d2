from choose_parameters import getGribFileNames
from download_grib_files import download_gribs
from parse_grib_files import parse_gribs
from agregates import create_aggregates

import os

storage_directory = "./data"

output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")

# Construct the paths based on the storage_directory
source_data_dir = os.path.join(output_directory_gribs, "t_2m/2023/08/24/18z")
output_directory = os.path.join(storage_directory, "output")
csv_file = os.path.join(output_directory, "2_metre_temperature", "2023", "08", "24", "18z", "2_metre_temperature_2023_08_24_18.csv")

filenames = getGribFileNames()

for filename in filenames:
    download_gribs(filename, output_directory_gribs)

parse_gribs(source_data_dir, output_directory)

create_aggregates(csv_file, output_directory)
