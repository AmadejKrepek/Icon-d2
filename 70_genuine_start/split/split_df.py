import pandas as pd


def split_dataframe_by_hour(df):
    # Assuming your DataFrame has a 'Datetime' column
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Create a list to store DataFrames for each hour
    hourly_dataframes = []

    # Extract unique hours from the 'Datetime' column
    unique_hours = df['Datetime'].dt.hour.unique()

    for hour in unique_hours:
        # Select data for the current hour
        hour_df = df[df['Datetime'].dt.hour == hour]

        # Append the DataFrame to the list
        hourly_dataframes.append(hour_df)

    return hourly_dataframes


def split_dataframe_by_specific_hours_and_minutes(df):
    # Assuming your DataFrame has a 'Datetime' column
    df['Datetime'] = pd.to_datetime(df['Datetime'])

    # Extract and sort unique hours and minutes from the 'Datetime' column
    unique_hours = sorted(df['Datetime'].dt.hour.unique())
    unique_minutes = sorted(df['Datetime'].dt.minute.unique())

    # Create a list to store DataFrames for each specific hour and minute
    result_dataframes = []

    for hour in unique_hours:
        for minute in unique_minutes:
            # Select data for the current hour and minute
            specific_time_df = df[(df['Datetime'].dt.hour == hour) & (df['Datetime'].dt.minute == minute)]

            # Check if specific_time_df is not empty before appending
            if not specific_time_df.empty:
                # Append the DataFrame to the list
                result_dataframes.append(specific_time_df)

    return result_dataframes