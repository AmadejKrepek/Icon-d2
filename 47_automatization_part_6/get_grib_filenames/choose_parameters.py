from .find_latest.find_latest_model_run import get_latest_model_run_filename, download_and_extract_log_file
from datetime import datetime

def read_variable_names_from_file(file_path):
    with open(file_path, "r") as f:
        variable_names = [line.strip() for line in f if line.strip()]
    return variable_names

def getGribFileNames():
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    variable_names_file = "./get_grib_filenames/variable_names/d2_variables.txt"
    variable_names = read_variable_names_from_file(variable_names_file)
    data = download_and_extract_log_file()

    print("Available parameters:")
    for idx, param in enumerate(variable_names, start=1):
        print(f"{idx}. {param}")

    parameter_input = input("Enter parameter numbers separated by commas: ")
    selected_indices = [int(idx.strip()) for idx in parameter_input.split(",")]

    selected_params = []
    for idx in selected_indices:
        if 1 <= idx <= len(variable_names):
            selected_params.append(variable_names[idx - 1])
        else:
            print(f"Invalid index {idx}. Skipping.")

    if not selected_params:
        print("No valid parameters selected. Exiting.")
        return

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