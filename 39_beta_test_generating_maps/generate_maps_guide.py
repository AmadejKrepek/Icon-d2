import os
from create_dynamic_maps import create_maps

def choose_directory(options):
    print("Select a directory:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    choice = int(input("Enter the number of your choice: "))
    return options[choice - 1]

def construct_input_filename(base_path, parameter, aggregate, year, month, day, model_run, filename):
    return os.path.join(base_path, parameter, aggregate, year, month, day, model_run, filename).replace('\\', '/')

storage_directory = '../38_automatization_part_2/data'
base_path = os.path.join(storage_directory, 'output')

output_directory = '../38_automatization_part_2/data/public/plots'

# List available parameter directories
parameters = os.listdir(base_path)

# Guide user through selecting parameter
selected_parameter = choose_directory(parameters)

# List available aggregate directories
aggregate_dirs = os.listdir(os.path.join(base_path, selected_parameter))

# Guide user through selecting aggregate
selected_aggregate = choose_directory(aggregate_dirs)

# List available year directories
year_dirs = os.listdir(os.path.join(base_path, selected_parameter, selected_aggregate))

# Guide user through selecting year
selected_year = choose_directory(year_dirs)

# List available month directories
month_dirs = os.listdir(os.path.join(base_path, selected_parameter, selected_aggregate, selected_year))

# Guide user through selecting month
selected_month = choose_directory(month_dirs)

# List available day directories
day_dirs = os.listdir(os.path.join(base_path, selected_parameter, selected_aggregate, selected_year, selected_month))

# Guide user through selecting day
selected_day = choose_directory(day_dirs)

# List available model run directories
model_run_dirs = os.listdir(os.path.join(base_path, selected_parameter, selected_aggregate, selected_year, selected_month, selected_day))

# Guide user through selecting model run
selected_model_run = choose_directory(model_run_dirs)

# List available CSV files inside the selected model run directory
model_run_path = os.path.join(base_path, selected_parameter, selected_aggregate, selected_year, selected_month, selected_day, selected_model_run)
csv_files = [filename for filename in os.listdir(model_run_path) if filename.endswith('.csv')]

# Guide user through selecting CSV file
print("Select a CSV file:")
for idx, csv_file in enumerate(csv_files, start=1):
    print(f"{idx}. {csv_file}")
csv_choice = int(input("Enter the number of your choice: "))
selected_csv_file = csv_files[csv_choice - 1]

# Construct input_filename based on user selections
input_filename = construct_input_filename(base_path, selected_parameter, selected_aggregate, selected_year, selected_month, selected_day, selected_model_run, selected_csv_file)
# Now you can use the input_filename to perform further operations
print(f"Constructed input filename: {input_filename}")

create_maps(input_filename, output_directory)


