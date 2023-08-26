import os
import time
from get_grib_filenames.choose_parameters import getGribFileNames
from download_grib_files import download_grib_files
from parse_gribs.parse_grib_files import parse_gribs
from get_aggregates.agregates import create_aggregates
from generate_maps.generate_maps_guide import generate_fancy_maps

def download_and_parse(output_directory_gribs, output_directory):
    try:
        filenames = getGribFileNames()

        for filename in filenames:
            resulted_gribs_directory = download_grib_files.download_gribs(filename, output_directory_gribs)
        
        resulted_csv_file = parse_gribs(resulted_gribs_directory, output_directory)
        return resulted_csv_file
    except Exception as e:
        print("Error during download and parse:", e)
        return None

def main():
    start_time = time.time()

    storage_directory = "./data"
    output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
    output_directory = os.path.join(storage_directory, "output")
    maps_output_directory = os.path.join(storage_directory, 'public/plots')

    resulted_gribs_directory = None
    resulted_csv_file = None

    while True:
        resulted_csv_file = download_and_parse(output_directory_gribs, output_directory)

        if resulted_csv_file:
            while True:
                try:
                    create_aggregates(resulted_csv_file, output_directory)
                    run_again = input("\nDo you want to create aggregates again? (y/n): ")
                    if run_again.lower() != 'y':
                        print("Exiting the aggregates section.")
                        break
                except Exception as e:
                    print("Error during aggregates:", e)
                    retry = input("Do you want to retry creating aggregates? (y/n): ")
                    if retry.lower() != 'y':
                        print("Exiting the aggregates section.")
                        break

            while True:
                try:
                    generate_fancy_maps(storage_directory, maps_output_directory)
                    run_again = input("\nDo you want to generate maps again? (y/n): ")
                    if run_again.lower() != 'y':
                        print("Exiting the map generation section.")
                        break
                except Exception as e:
                    print("Error during map generation:", e)
                    retry = input("Do you want to retry generating maps? (y/n): ")
                    if retry.lower() != 'y':
                        print("Exiting the map generation section.")
                        break

        run_again = input("\nDo you want to run the script again? (y/n): ")
        if run_again.lower() != 'y':
            print("Exiting the script.")
            break
    
    # Calculate and format script execution time
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_formatted = time.strftime("%H:%M:%S", time.gmtime(execution_time_seconds))
    print("Script finished. Execution time:", execution_time_formatted)

if __name__ == "__main__":
    main()
