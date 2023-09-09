import os
from datetime import datetime

def extract_output_names(input_filename, variable, output_directory):
        parts = input_filename.split('/')
        model_run_year = parts[-5]
        model_run_month = parts[-4]
        model_run_day = parts[-3]
        model_run = parts[-2]
        output_variable_name = variable.replace(' ', '_').lower()

        selected_file_name = parts[-1]
        selected_file_name_parts = selected_file_name.split('_')

        # Find the index of the year in selected_file_name_parts
        year_index = None
        for i, part in enumerate(selected_file_name_parts):
            if part.isdigit() and len(part) == 4:
                year_index = i
                break

        selected_aggregate = None

        if year_index is not None:
            selected_year = selected_file_name_parts[year_index]
            selected_month = selected_file_name_parts[year_index + 1]
            selected_day = selected_file_name_parts[year_index + 2]
            selected_start_year = selected_file_name_parts[year_index + 4]
            selected_start_month = selected_file_name_parts[year_index + 5]
            selected_start_day = selected_file_name_parts[year_index + 6]
            selected_start_hour = selected_file_name_parts[year_index + 7]
            selected_start_minute = selected_file_name_parts[year_index + 8]
            selected_end_year = selected_file_name_parts[year_index + 9]
            selected_end_month = selected_file_name_parts[year_index + 10]
            selected_end_day = selected_file_name_parts[year_index + 11]
            selected_end_hour = selected_file_name_parts[year_index + 12]
            selected_end_minute = selected_file_name_parts[year_index + 13].replace(".csv", "")
            selected_aggregate = selected_file_name_parts[0]
        else:
            print("Year not found in filename")

        # Continue with the rest of your code
        formatted_start_datetime = "_".join([selected_start_year, selected_start_month, selected_start_day, selected_start_hour, selected_start_minute])
        formatted_end_datetime = "_".join([selected_end_year, selected_end_month, selected_end_day, selected_end_hour, selected_end_minute])

        # Parse the date components
        model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
        model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")
        model_run_formatted_date = model_run_formatted_date + f" {model_run} UTC"

        if (output_variable_name == "max_total_precipitation"):
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day} {selected_end_hour}:{selected_end_minute}", "%Y-%m-%d %H:%M")
            selected_formatted_date = selected_date_components.strftime("velja do %d. %m. %Y ob %H:%M")
        else:      
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day}", "%Y-%m-%d")
            selected_formatted_date = selected_date_components.strftime("%d. %m. %Y")
        
        # Construct the output directory and filename
        output_directory = f'{output_directory}/{output_variable_name}/{selected_aggregate}/{model_run_year}/{model_run_month}/{model_run_day}/{model_run}/'
        print(f"Output directory: {output_directory}")
        
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist
        
        model_run = model_run.replace('z', '')
        model_run_formatted_date = model_run_formatted_date.replace('z', '')
        
        output_filename = f'{output_variable_name}_{selected_year}_{selected_month}_{selected_day}_{model_run}_{formatted_start_datetime}_{formatted_end_datetime}.png'
        output_filepath = os.path.join(output_directory, output_filename)
        
        return output_filepath, model_run_formatted_date, selected_formatted_date