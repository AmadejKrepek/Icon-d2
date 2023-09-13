import os
import time
from get_grib_filenames.PROVIDER.DWD.NWP.choose_parameters import getGribFileNames as getDWDGribFileNames
from download_grib_files.PROVIDER.DWD.NWP import download_ICON_D2 as downloadDWD
from parse_gribs.PROVIDER.DWD.NWP.parse_grib_files import parse_gribs as parse_gribs_DWD

provider_models = {
    "DWD": ["IconD2"],
}

selected_params = ["t_2m"]

def download_and_parse(output_directory_gribs, output_directory, getGribFileNames, download_function, parse_gribs, provider_directory, model_directory):
    try:
        filenames = getGribFileNames(selected_params)

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
        return None

def main():
    storage_directory = "./data"
    output_directory_gribs = os.path.join(storage_directory, "downloaded_grib_files")
    output_directory = os.path.join(storage_directory, "output")

    while True:
        for provider_directory, available_models in provider_models.items():
            for model_directory in available_models:
                print(f"Provider: {provider_directory}, model: {model_directory}")
                
                resulted_csv_file = download_and_parse(output_directory_gribs, output_directory, getDWDGribFileNames, downloadDWD, parse_gribs_DWD, provider_directory, model_directory)
                
                if resulted_csv_file is not None:
                    print("Download and parse completed successfully.")
        
        # Sleep for 3 hours (3 hours * 60 minutes * 60 seconds)
        #time.sleep(3 * 60 * 60)
        time.sleep(60)

if __name__ == "__main__":
    main()
