import os
from datetime import datetime

def extract_output_names(model_run, variable, output_directory, start_date, end_date, selected_date):
        model_run_year = start_date.year
        model_run_month = start_date.month
        model_run_day = start_date.day
        output_variable_name = variable

        parts = variable.split('_')
        selected_aggregate = parts[0]
        last_part = parts[-1]

        model_run_model = last_part

        provider = None

        if model_run_model == "icond2":
            model_run_model = "ICON-D2"
            provider = "DWD"
        else:
             model_run_model = "ALADIN"
             provider = "ARSO"

        selected_year = selected_date.year
        selected_month = selected_date.month
        selected_day = selected_date.day
        selected_start_year = start_date.year
        selected_start_month = start_date.month
        selected_start_day = start_date.day
        selected_start_hour = start_date.hour
        selected_start_minute = start_date.minute
        selected_end_year = end_date.year
        selected_end_month = end_date.month
        selected_end_day = end_date.day
        selected_end_hour = end_date.hour
        selected_end_minute = end_date.minute

        # Continue with the rest of your code
        formatted_start_datetime = "_".join([str(selected_start_year), str(selected_start_month), str(selected_start_day), str(selected_start_hour), str(selected_start_minute)])
        formatted_end_datetime = "_".join([str(selected_end_year), str(selected_end_month), str(selected_end_day), str(selected_end_hour), str(selected_end_minute)])

        # Parse the date components
        model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
        model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")
        model_run_formatted_date = model_run_formatted_date + f" {model_run} UTC"

        if (output_variable_name.startswith("max_total_precipitation_") or output_variable_name == "sum_total_precipitation"):
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day} {selected_end_hour}:{selected_end_minute}", "%Y-%m-%d %H:%M")
            selected_formatted_date = selected_date_components.strftime("velja do %d. %m. %Y ob %H:%M")
        else:      
            selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day}", "%Y-%m-%d")
            selected_formatted_date = selected_date_components.strftime("%d. %m. %Y")
        
        # Construct the output directory and filename
        output_directory = f'{output_directory}/{output_variable_name}/{selected_aggregate}/{model_run_year}/{model_run_month}/{model_run_day}/{model_run}/'
        print(f"Output directory: {output_directory}")
        
        os.makedirs(output_directory, exist_ok=True)  # Create the output directory if it doesn't exist
        
        output_filename = f'{output_variable_name}_{selected_year}_{selected_month}_{selected_day}_{model_run}_{formatted_start_datetime}_{formatted_end_datetime}.png'
        output_filepath = os.path.join(output_directory, output_filename)
        
        return output_filepath, model_run_formatted_date, selected_formatted_date, model_run_model, provider