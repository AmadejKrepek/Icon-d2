from choose_parameters import getGribFileNames
from download_grib_files import download_gribs
from parse_grib_files import parse_gribs
from agregates import create_aggregates

import os
import time

# Start measuring script execution time
start_time = time.time()

storage_directory = "./data"

output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")

# Construct the paths based on the storage_directory
source_data_dir = os.path.join(output_directory_gribs, "t_2m/2023/08/24/18z")
output_directory = os.path.join(storage_directory, "output")
csv_file = os.path.join(output_directory, "2_metre_temperature", "2023", "08", "24", "18z", "2_metre_temperature_2023_08_24_18.csv")

resulted_gribs_directory = None
resulted_csv_file = None

filenames = getGribFileNames()

for filename in filenames:
    resulted_gribs_directory = download_gribs(filename, output_directory_gribs)

print("Downloaded GRIB files are located in: ", resulted_gribs_directory)
resulted_csv_file = parse_gribs(resulted_gribs_directory, output_directory)

create_aggregates(resulted_csv_file, output_directory)

# Calculate and format script execution time
end_time = time.time()
execution_time_seconds = end_time - start_time
execution_time_formatted = time.strftime("%H:%M:%S", time.gmtime(execution_time_seconds))
print("Script finished. Execution time:", execution_time_formatted)
