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
