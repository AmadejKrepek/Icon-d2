import os
from agregates import create_aggregates

storage_path = './data'

# Get base directory path
base_path = './output'
base_path = os.path.join(storage_path, base_path)

# Get the list of available subdirectories in the base path
available_subdirectories = os.listdir(base_path)

# Prompt user to select a subdirectory
print("Select a subdirectory:")
for idx, subdirectory in enumerate(available_subdirectories, start=1):
    print(f"{idx}. {subdirectory}")

subdirectory_choice = int(input("Enter the corresponding number: ")) - 1
selected_subdirectory = available_subdirectories[subdirectory_choice]

# Construct the path to the selected subdirectory
subdirectory_path = os.path.join(base_path, selected_subdirectory)

# Get the list of available years in the selected subdirectory
available_years = os.listdir(subdirectory_path)

# Prompt user to select a year
print("\nSelect a year:")
for idx, year in enumerate(available_years, start=1):
    print(f"{idx}. {year}")

year_choice = int(input("Enter the corresponding number: ")) - 1
selected_year = available_years[year_choice]

# Construct the path to the selected year
year_path = os.path.join(subdirectory_path, selected_year)

# Get the list of available months in the selected year
available_months = os.listdir(year_path)

# Prompt user to select a month
print("\nSelect a month:")
for idx, month in enumerate(available_months, start=1):
    print(f"{idx}. {month}")

month_choice = int(input("Enter the corresponding number: ")) - 1
selected_month = available_months[month_choice]

# Construct the path to the selected month
month_path = os.path.join(year_path, selected_month)

# Get the list of available days in the selected month
available_days = os.listdir(month_path)

# Prompt user to select a day
print("\nSelect a day:")
for idx, day in enumerate(available_days, start=1):
    print(f"{idx}. {day}")

day_choice = int(input("Enter the corresponding number: ")) - 1
selected_day = available_days[day_choice]

# Construct the path to the selected day
day_path = os.path.join(month_path, selected_day)

# Get the list of available model runs in the selected day
available_model_runs = os.listdir(day_path)

# Prompt user to select a model run
print("\nSelect a model run:")
for idx, model_run in enumerate(available_model_runs, start=1):
    print(f"{idx}. {model_run}")

model_run_choice = int(input("Enter the corresponding number: ")) - 1
selected_model_run = available_model_runs[model_run_choice]

# Construct the path to the selected model run
model_run_path = os.path.join(day_path, selected_model_run)

# Get the list of available CSV files in the selected model run
available_files = [file for file in os.listdir(model_run_path) if file.endswith('.csv')]

# Prompt user to select a CSV file
print("\nSelect a CSV file:")
for idx, file in enumerate(available_files, start=1):
    print(f"{idx}. {file}")

file_choice = int(input("Enter the corresponding number: ")) - 1
selected_file = available_files[file_choice]

# Construct the path to the selected CSV file
csv_file_path = os.path.join(model_run_path, selected_file)

while True:
    # Call the create_aggregates function with the selected CSV file and output folder
    create_aggregates(csv_file_path, base_path)
    run_again = input("\nDo you want to run the script again? (yes/no): ")
    if run_again.lower() != 'yes':
        print("Exiting the script.")
        break
