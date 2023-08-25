from choose_parameters import getGribFileNames
from download_grib_files import download_gribs
from parse_grib_files import parse_gribs
from agregates import create_aggregates

import os

# Define the main storage directory
storage_directory = "./data"

# Construct the output directories based on the storage_directory
output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
output_directory_output = os.path.join(storage_directory, "output")

# Get the list of GRIB filenames
filenames = getGribFileNames()

resulted_csv_files = None

# Download and parse GRIB files
for filename in filenames:
    download_gribs(filename, output_directory_gribs)

print("Downloaded GRIB files are located in: ", output_directory_gribs)
# Loop through the downloaded GRIB files and create aggregates
downloaded_files = os.listdir(output_directory_gribs)
for downloaded_file in downloaded_files:
    source_data_dir = os.path.join(output_directory_gribs, downloaded_file)
    
    # Assuming the CSV filename pattern is consistent
    csv_file = os.path.join(output_directory_output, downloaded_file.replace(".grib2.bz2", ".csv"))
    
    # Parse GRIB files
    resulted_csv_files = parse_gribs(source_data_dir, output_directory_output)
    
    # Create aggregates
    create_aggregates(resulted_csv_files, output_directory_output)
