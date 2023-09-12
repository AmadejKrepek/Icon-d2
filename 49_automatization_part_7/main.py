import os
import time
import traceback
from get_grib_filenames.PROVIDER.DWD.NWP.choose_parameters import getGribFileNames as getDWDGribFileNames
from download_grib_files.PROVIDER.DWD.NWP import download_ICON_D2 as downloadDWD
from get_grib_filenames.PROVIDER.ARSO.NWP.choose_parameters import getGribFileNames as getARSOGribFileNames
from download_grib_files.PROVIDER.ARSO.NWP import download_ALADIN as downloadALADIN
from parse_gribs.PROVIDER.DWD.NWP.parse_grib_files import parse_gribs as parse_gribs_DWD
from parse_gribs.PROVIDER.ARSO.NWP.parse_grib_files import parse_gribs as parse_gribs_ARSO
from get_aggregates.agregates_choose import choose_aggregates
from get_aggregates.agregates import create_aggregates
from generate_maps.generate_maps_guide import generate_fancy_maps
from generate_maps.general.create_dynamic_maps import create_maps
from parse_settings.read import read_colors
from matplotlib.font_manager import FontProperties

provider_models = {
    "DWD": ["IconD2"],
    "ARSO": ["Aladin"]
}

def choose_nwp_provider():
    while True:
        print("Choose NWP provider:")
        print("1. DWD (German Weather Service)")
        print("2. ARSO (Slovenian Environment Agency)")

        choice = input("Enter your choice: ")

        if choice == '1':
            provider_directory = "DWD"
            available_models = provider_models["DWD"]
            print("Choose NWP model for DWD:")
            for i, model in enumerate(available_models, start=1):
                print(f"{i}. {model}")

            model_choice = input("Enter the model number: ")
            if model_choice.isdigit() and 1 <= int(model_choice) <= len(available_models):
                model_directory = available_models[int(model_choice) - 1]
                return getDWDGribFileNames, downloadDWD, parse_gribs_DWD, provider_directory, model_directory
            else:
                print("Invalid model choice. Defaulting to IconD2.")
                return getDWDGribFileNames, downloadDWD, parse_gribs_DWD, provider_directory, "IconD2"
        elif choice == '2':
            provider_directory = "ARSO"
            available_models = provider_models["ARSO"]
            print("Choose NWP model for ARSO:")
            for i, model in enumerate(available_models, start=1):
                print(f"{i}. {model}")

            model_choice = input("Enter the model number: ")
            if model_choice.isdigit() and 1 <= int(model_choice) <= len(available_models):
                model_directory = available_models[int(model_choice) - 1]
                return getARSOGribFileNames, downloadALADIN, parse_gribs_ARSO, provider_directory, model_directory
            else:
                print("Invalid model choice. Defaulting to Aladin.")
                return getARSOGribFileNames, downloadALADIN, parse_gribs_ARSO, provider_directory, "Aladin"
        else:
            print("Invalid choice. Please select a valid option.")

def download_and_parse(output_directory_gribs, output_directory, temp_directory, getGribFileNames, download_function, parse_gribs, provider_directory, model_directory):
    try:
        filenames = getGribFileNames()

        for filename in filenames:
            # Create provider and model directories
            provider_model_directory = os.path.join(output_directory_gribs, provider_directory, model_directory)
            os.makedirs(provider_model_directory, exist_ok=True)

            resulted_gribs_directory = download_function.download_gribs(filename, provider_model_directory)

        # Append provider_directory and model_directory after output_directory
        resulted_csv_file = parse_gribs(resulted_gribs_directory, os.path.join(output_directory, provider_directory, model_directory), output_directory_gribs)
        print(f"Downloaded and parsed {resulted_csv_file}")
        return resulted_csv_file
    except Exception as e:
        print("Error during download and parse:", e)
        traceback.print_exc()
        return None

def main():
    start_time = time.time()

    color_configuration = read_colors.read_colors("./configuration/colors.config")

    font_path = '../assets/fonts/'

    custom_font = FontProperties(fname=font_path + 'font.ttf')

    storage_directory = "./data"

    input_directory_plots = os.path.join(storage_directory, 'output')

    output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
    output_directory = os.path.join(storage_directory, "output")
    maps_output_directory = os.path.join(storage_directory, 'public/plots')

    temp_directory = os.path.join(storage_directory, "temp")

    resulted_csv_file = None

    getGribFileNames, download_function, parse_gribs, provider_directory, model_directory = choose_nwp_provider()

    while True:
        print("\nOptions:")
        print("1. Run download_and_parse script")
        print("2. Run create_aggregates script")
        print("3. Run generate_fancy_maps script")
        print("4. Change NWP provider and model")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            resulted_csv_file = download_and_parse(output_directory_gribs, output_directory, temp_directory, getGribFileNames, download_function, parse_gribs, provider_directory, model_directory)
        elif choice == '2':
            try:
                if resulted_csv_file is None:
                    resulted_csv_file = choose_aggregates(output_directory, provider_directory, model_directory)
                create_aggregates(resulted_csv_file, os.path.join(output_directory, provider_directory, model_directory))
                resulted_csv_file = None
            except Exception as e:
                print("Error during aggregates:", e)
        elif choice == '3':
            try:
                generate_fancy_maps(input_directory_plots, maps_output_directory, color_configuration, custom_font)
            except Exception as e:
                traceback.print_exc()
                print("Error during map generation:", e)
        elif choice == '4':
            getGribFileNames, download_function, parse_gribs, provider_directory, model_directory = choose_nwp_provider()
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
