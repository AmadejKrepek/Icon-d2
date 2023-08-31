import os
import time
from get_grib_filenames.choose_parameters import getGribFileNames
from download_grib_files import download_grib_files
from parse_gribs.parse_grib_files import parse_gribs
from get_aggregates.agregates_choose import choose_aggregates
from get_aggregates.agregates import create_aggregates
from generate_maps.generate_maps_guide import generate_fancy_maps
from parse_settings.read import read_colors

from matplotlib.font_manager import FontProperties

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

    color_configuration = read_colors.read_colors("./configuration/colors.config")
    
    font_path = '../assets/fonts/'

    custom_font = FontProperties(fname=font_path + 'font.ttf')

    storage_directory = "./data"
    output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
    output_directory = os.path.join(storage_directory, "output")
    maps_output_directory = os.path.join(storage_directory, 'public/plots')

    resulted_csv_file = None

    while True:
        print("Options:")
        print("1. Run download_and_parse script")
        print("2. Run create_aggregates script")
        print("3. Run generate_fancy_maps script")
        print("4. Exit")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            resulted_csv_file = download_and_parse(output_directory_gribs, output_directory)
        elif choice == '2':
            try:
                if resulted_csv_file is None:
                    resulted_csv_file = choose_aggregates()
                create_aggregates(resulted_csv_file, output_directory)
            except Exception as e:
                print("Error during aggregates:", e)
        elif choice == '3':
            try:
                generate_fancy_maps(storage_directory, maps_output_directory, color_configuration, custom_font)
            except Exception as e:
                print("Error during map generation:", e)
        elif choice == '4':
            print("Exiting the script.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

    # Calculate and format script execution time
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_formatted = time.strftime("%H:%M:%S", time.gmtime(execution_time_seconds))
    print("Script finished. Execution time:", execution_time_formatted)

if __name__ == "__main__":
    main()
