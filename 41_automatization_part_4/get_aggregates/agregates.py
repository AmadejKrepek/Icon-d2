import pandas as pd
import os
def aggregate_data(df, agg_column, agg_function):
    if agg_function == 'sum':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].sum()
    elif agg_function == 'max':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].max()
    elif agg_function == 'min':
        return df.groupby(['Latitude', 'Longitude'])[agg_column].min()

def create_aggregates(csv_file, output_folder):
    df = pd.read_csv(csv_file)
    
    # Convert 'ValidDate' column to datetime format
    df['ValidDate'] = pd.to_datetime(df['ValidDate'])

    import os

    filename_parts = os.path.basename(csv_file).split("_")
    print(f'filename parts: {filename_parts}')

    # Find the index of the year
    year_index = None
    for i, part in enumerate(filename_parts):
        if part.isdigit() and len(part) == 4:
            year_index = i
            break

    # Extract information based on the found year index
    if year_index is not None:
        parameter_name = "_".join(filename_parts[0:year_index])
        aggregate_name = filename_parts[0]
        year = filename_parts[year_index]
        month = filename_parts[year_index + 1]
        day = filename_parts[year_index + 2]
        model_run = filename_parts[year_index + 3].split(".")[0]

        agg_column = df.columns[2]

        print(f"Parameter name: {parameter_name}")
        print(f"Year: {year}")
        print(f"Month: {month}")
        print(f"Day: {day}")
        print(f"Model run: {model_run}")
    else:
        print("Year not found in filename")

    print("Available aggregation functions: sum, max, min")
    agg_function = input("Enter aggregation function (sum, max, min): ")

    if agg_function not in ['sum', 'max', 'min']:
        print("Invalid aggregation function. Exiting.")
        return

    # Construct the output directory structure
    output_dir = os.path.join(output_folder, parameter_name, agg_function, year, month, day, model_run + 'z')
    os.makedirs(output_dir, exist_ok=True)
    
    print("Choose aggregation time frame:")
    print("1. Single day")
    print("2. Interval of days")
    time_frame_choice = input("Enter your choice (1 or 2): ")
    
    unique_days = None
    output_file = None
    if time_frame_choice == '1':
        unique_days = df['ValidDate'].dt.date.unique()
        print("Available days:")
        for idx, date in enumerate(unique_days):
            print(f"{idx+1}. {date}")

        day_choice = int(input("Choose a day (enter the corresponding number): ")) - 1
        selected_day = unique_days[day_choice]

        # Filter data for the selected day
        filtered_data = df[df['ValidDate'].dt.date == selected_day]
        
        # Get the first and last ValidDate in the filtered_data
        first_valid_date = filtered_data['ValidDate'].min()
        last_valid_date = filtered_data['ValidDate'].max()
        
        # Format the first and last ValidDate to YYYY_MM_DD_HH_mm format
        formatted_first_valid_date = first_valid_date.strftime('%Y_%m_%d_%H_%M')
        formatted_last_valid_date = last_valid_date.strftime('%Y_%m_%d_%H_%M')
        
        print(f"First ValidDate: {formatted_first_valid_date}")
        print(f"Last ValidDate: {formatted_last_valid_date}")

        selected_year = str(selected_day.year)
        selected_month = str(selected_day.month).zfill(2)
        selected_day_number = str(selected_day.day).zfill(2)
        output_file = f"{agg_function}_{parameter_name}_{selected_year}_{selected_month}_{selected_day_number}_{model_run}_{formatted_first_valid_date}_{formatted_last_valid_date}.csv"

    elif time_frame_choice == '2':
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        filtered_data = df[(df['ValidDate'] >= start_date) & (df['ValidDate'] <= end_date)]
        
        # Get the first and last ValidDate in the filtered_data
        first_valid_date = filtered_data['ValidDate'].min()
        last_valid_date = filtered_data['ValidDate'].max()
        
        # Format the first and last ValidDate to YYYY_MM_DD_HH_mm format
        formatted_first_valid_date = first_valid_date.strftime('%Y_%m_%d_%H_%M')
        formatted_last_valid_date = last_valid_date.strftime('%Y_%m_%d_%H_%M')
        
        print(f"First ValidDate: {formatted_first_valid_date}")
        print(f"Last ValidDate: {formatted_last_valid_date}")
        
        selected_year = str(start_date.year)
        selected_month = str(start_date.month).zfill(2)
        selected_day_number = str(start_date.day).zfill(2)
        end_year = str(end_date.year)
        end_month = str(end_date.month).zfill(2)
        end_day_number = str(end_date.day).zfill(2)
        output_file = f"{agg_function}_{parameter_name}_{selected_year}_{selected_month}_{selected_day_number}_{end_year}_{end_month}_{end_day_number}_{model_run}_{formatted_first_valid_date}_{formatted_last_valid_date}.csv"
        
    else:
        print("Invalid choice. Exiting.")
        return

    aggregated_data = aggregate_data(filtered_data, agg_column, agg_function).reset_index()
    
    latest_date = unique_days[-1]
    year_latest = str(latest_date.year)
    month_latest = str(latest_date.month).zfill(2)
    day_latest = str(latest_date.day).zfill(2)
    
    output_path = os.path.join(output_dir, output_file)
    
    adjusted_parameter_name = parameter_name.replace("_", " ")
    aggregated_data.rename(columns={agg_column: f'{agg_function} {adjusted_parameter_name}'}, inplace=True)
    
    aggregated_data.to_csv(output_path, index=False)

    print(f"Aggregated data written to {output_path}")
    return output_path