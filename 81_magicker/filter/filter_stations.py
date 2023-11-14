import pandas as pd


def filter_hourly_intervals(df, column_name):
    # Assuming you have a datetime column named 'ValidUtc' in your DataFrame
    # Replace 'ValidUtc' with the actual column name in your DataFrame
    df[column_name] = pd.to_datetime(df[column_name])
    # Filter rows based on the hour, minute, and second
    hourly_df = df[
        ((df[column_name].dt.hour >= 0) & (df[column_name].dt.hour <= 23)) &
        (df[column_name].dt.minute == 0) & (df[column_name].dt.second == 0)
    ]

    # Order the resulting DataFrame by 'ValidUtc'
    hourly_df = hourly_df.sort_values(by=column_name)

    return hourly_df
