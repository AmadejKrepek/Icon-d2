import os

def select_item(prompt, items):
    print(prompt)
    for idx, item in enumerate(items, start=1):
        print(f"{idx}. {item}")
    
    choice = int(input("Enter the corresponding number: ")) - 1
    selected_item = items[choice]
    return selected_item

def choose_aggregates(provider_directory):
    storage_path = './data'
    base_path = './output'
    base_path = os.path.join(storage_path, base_path, provider_directory)
    
    available_subdirectories = os.listdir(base_path)
    selected_subdirectory = select_item("Select a subdirectory:", available_subdirectories)
    
    subdirectory_path = os.path.join(base_path, selected_subdirectory)
    available_years = os.listdir(subdirectory_path)
    selected_year = select_item("\nSelect a year:", available_years)
    
    year_path = os.path.join(subdirectory_path, selected_year)
    available_months = os.listdir(year_path)
    selected_month = select_item("\nSelect a month:", available_months)
    
    month_path = os.path.join(year_path, selected_month)
    available_days = os.listdir(month_path)
    selected_day = select_item("\nSelect a day:", available_days)
    
    day_path = os.path.join(month_path, selected_day)
    available_model_runs = os.listdir(day_path)
    selected_model_run = select_item("\nSelect a model run:", available_model_runs)
    
    model_run_path = os.path.join(day_path, selected_model_run)
    available_files = [file for file in os.listdir(model_run_path) if file.endswith('.csv')]
    selected_file = select_item("\nSelect a CSV file:", available_files)
    
    csv_file_path = os.path.join(model_run_path, selected_file)
    
    # Now you can use the csv_file_path as needed
    return csv_file_path