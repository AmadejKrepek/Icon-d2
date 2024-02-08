import os
from datetime import datetime, timedelta
import pytz


def extract_output_names(model_run, variable, start_date, end_date, selected_date):
    # Specify your local timezone (for example, 'US/Eastern')
    local_timezone = pytz.timezone('Europe/Ljubljana')

    model_run_year = start_date.year
    model_run_month = start_date.month
    model_run_day = start_date.day
    output_variable_name = variable

    print(start_date)
    print(end_date)
    print(selected_date)

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

    end_date = end_date.astimezone(local_timezone)
    if any(substring in variable for substring in ["total_precipitation", "base_reflectivity", "snow_depth", "convective", "large-scale"]):
        # Check if the time is 00:00 and adjust it to 00:00 of the next day
        if selected_date.day is not end_date.day:
            selected_date = selected_date + timedelta(days=1)  # Add one day to the selected_date
            selected_date = selected_date.replace(hour=0, minute=0)  # Set the time to 00:00 of the


    selected_end_year = selected_date.year
    selected_end_month = selected_date.month
    selected_end_day = selected_date.day
    selected_end_hour = selected_date.hour
    selected_end_minute = selected_date.minute

    if selected_day == end_date.day:
        selected_end_hour = end_date.hour
        selected_end_minute = end_date.minute

    # Continue with the rest of your code
    formatted_start_datetime = "_".join(
        [str(selected_start_year), str(selected_start_month), str(selected_start_day), str(selected_start_hour),
         str(selected_start_minute)])
    formatted_end_datetime = "_".join(
        [str(selected_end_year), str(selected_end_month), str(selected_end_day), str(selected_end_hour),
         str(selected_end_minute)])

    # Parse the date components
    model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
    model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")
    model_run_formatted_date = model_run_formatted_date + f" {model_run} UTC"

    if any(substring in variable for substring in ["total_precipitation", "base_reflectivity", "snow_depth", "convective", "large-scale"]):
        selected_date_components = datetime.strptime(
            f"{selected_end_year}-{selected_end_month}-{selected_end_day} {selected_end_hour}:{selected_end_minute}",
            "%Y-%m-%d %H:%M")
        selected_formatted_date = selected_date_components.strftime("velja do %d. %m. %Y ob %H.%M")
    else:
        selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day}", "%Y-%m-%d")
        selected_formatted_date = selected_date_components.strftime("%d. %m. %Y")


    return model_run_formatted_date, selected_formatted_date, model_run_model, provider

def extract_animation_output_names(model_run, variable, start_date, end_date, selected_date, counter):
    # Specify your local timezone (for example, 'US/Eastern')
    local_timezone = pytz.timezone('Europe/Ljubljana')

    model_run_year = start_date.year
    model_run_month = start_date.month
    model_run_day = start_date.day
    output_variable_name = variable

    print(start_date)
    print(end_date)
    print(selected_date)

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
    selected_hour = selected_date.hour

    selected_start_year = start_date.year
    selected_start_month = start_date.month
    selected_start_day = start_date.day
    selected_start_hour = start_date.hour
    selected_start_minute = start_date.minute

    end_date = end_date.astimezone(local_timezone)

    #selected_date += timedelta(hours=counter)
    selected_end_year = selected_date.year
    selected_end_month = selected_date.month
    selected_end_day = selected_date.day
    selected_end_hour = selected_date.hour
    selected_end_minute = selected_date.minute

    # Continue with the rest of your code
    formatted_start_datetime = "_".join(
        [str(selected_start_year), str(selected_start_month), str(selected_start_day), str(selected_start_hour),
         str(selected_start_minute)])
    formatted_end_datetime = "_".join(
        [str(selected_end_year), str(selected_end_month), str(selected_end_day), str(selected_end_hour),
         str(selected_end_minute)])

    # Parse the date components
    model_run_date_components = datetime.strptime(f"{model_run_year}-{model_run_month}-{model_run_day}", "%Y-%m-%d")
    model_run_formatted_date = model_run_date_components.strftime("%d. %m. %Y")
    model_run_formatted_date = model_run_formatted_date + f" {model_run} UTC"

    if any(substring in variable for substring in ["total_precipitation", "base_reflectivity", "snow_depth", "convective", "large-scale"]):
        selected_date_components = datetime.strptime(
            f"{selected_end_year}-{selected_end_month}-{selected_end_day} {selected_end_hour}:{selected_end_minute}",
            "%Y-%m-%d %H:%M")
        selected_formatted_date = selected_date_components.strftime("velja do %d. %m. %Y ob %H.%M")
    else:
        selected_date_components = datetime.strptime(f"{selected_year}-{selected_month}-{selected_day} {selected_hour}_00", "%Y-%m-%d %H_00")
        selected_formatted_date = selected_date_components.strftime("%d. %m. %Y %H:%M")

    return model_run_formatted_date, selected_formatted_date, model_run_model, provider
