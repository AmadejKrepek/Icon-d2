import pandas as pd


def filter_hourly_intervals(df):
    # Assuming you have a datetime column named 'ValidUtc' in your DataFrame
    # Replace 'ValidUtc' with the actual column name in your DataFrame
    df['ValidUtc'] = pd.to_datetime(df['ValidUtc'])
    print(df['ValidUtc'].dt.minute)
    # Filter rows based on the hour, minute, and second
    hourly_df = df[
        ((df['ValidUtc'].dt.hour >= 0) & (df['ValidUtc'].dt.hour <= 23)) &
        (df['ValidUtc'].dt.minute == 0) & (df['ValidUtc'].dt.second == 0)
    ]

    return hourly_df
