from .find_latest.find_latest_model_run import get_latest_model_run_filename, download_and_extract_log_file
from datetime import datetime

def read_variable_names_from_file(file_path):
    with open(file_path, "r") as f:
        variable_names = [line.strip() for line in f if line.strip()]
    return variable_names

def getGribFileNames(selected_params):
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    variable_names_file = "./configuration/parameters/icon_d2.config"
    variable_names = read_variable_names_from_file(variable_names_file)
    data = download_and_extract_log_file()

    print("Selected parameters:")
    for param in selected_params:
        print(param)

    print("Searching for model runs...")
    filenames = []
    for param in selected_params:
        latest_file = get_latest_model_run_filename(data, param)
        if latest_file:
            filenames.append(latest_file)
            print(f"Latest model run filename for parameter '{param}': {latest_file}")
        else:
            print(f"No regular-lat-lon model run found for parameter '{param}'.")

    if not filenames:
        print("No filenames available for the selected parameters.")

    print("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return filenames
