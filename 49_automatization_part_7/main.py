import os
import time
from get_grib_filenames.PROVIDER.DWD.NWP.choose_parameters import getGribFileNames as getDWDGribFileNames
from download_grib_files.PROVIDER.DWD.NWP import download_ICON_D2 as downloadDWD
from get_grib_filenames.PROVIDER.ARSO.NWP.choose_parameters import getGribFileNames as getARSOGribFileNames
from download_grib_files.PROVIDER.ARSO.NWP import download_ALADIN as downloadALADIN
from parse_gribs.parse_grib_files import parse_gribs
from get_aggregates.agregates_choose import choose_aggregates
from get_aggregates.agregates import create_aggregates
from generate_maps.generate_maps_guide import generate_fancy_maps
from parse_settings.read import read_colors

from matplotlib.font_manager import FontProperties

# Global variable to store the provider's directory
provider_directory = "DWD"

def choose_nwp_provider():
    global provider_directory
    print("Choose NWP provider:")
    print("1. DWD (German Weather Service)")
    print("2. ARSO (Slovenian Environment Agency)")
    
    choice = input("Enter your choice: ")

    if choice == '1':
        provider_directory = "DWD"
        return getDWDGribFileNames, downloadDWD
    elif choice == '2':
        provider_directory = "ARSO"
        return getARSOGribFileNames, downloadALADIN
    else:
        print("Invalid choice. Defaulting to DWD (German Weather Service).")
        return getDWDGribFileNames, downloadDWD

def download_and_parse(output_directory_gribs, output_directory, getGribFileNames, download_function):
    global provider_directory  # Access the global provider_directory variable
    try:
        filenames = getGribFileNames()

        for filename in filenames:
            # Append provider_directory after output_directory_gribs
            resulted_gribs_directory = download_function.download_gribs(filename, os.path.join(output_directory_gribs, provider_directory))
        
        # Append provider_directory after output_directory
        resulted_csv_file = parse_gribs(resulted_gribs_directory, os.path.join(output_directory, provider_directory))
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
    
    input_directory_plots = os.path.join(storage_directory, 'output', provider_directory)
    
    output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
    output_directory = os.path.join(storage_directory, "output")
    maps_output_directory = os.path.join(storage_directory, 'public/plots')

    resulted_csv_file = None

    while True:
        print("Options:")
        print("1. Choose NWP provider")
        print("2. Run download_and_parse script")
        print("3. Run create_aggregates script")
        print("4. Run generate_fancy_maps script")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            getGribFileNames, download_function = choose_nwp_provider()
        elif choice == '2':
            resulted_csv_file = download_and_parse(output_directory_gribs, output_directory, getGribFileNames, download_function)
        elif choice == '3':
            try:
                if resulted_csv_file is None:
                    resulted_csv_file = choose_aggregates()
                create_aggregates(resulted_csv_file, os.path.join(output_directory, provider_directory))
            except Exception as e:
                print("Error during aggregates:", e)
        elif choice == '4':
            try:
                generate_fancy_maps(input_directory_plots, os.path.join(maps_output_directory, provider_directory), color_configuration, custom_font)
            except Exception as e:
                print("Error during map generation:", e)
        elif choice == '5':
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
