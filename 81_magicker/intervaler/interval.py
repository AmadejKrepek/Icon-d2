import pandas as pd


def create_interval(selected_date, df):
    selected_date_utc = pd.to_datetime(selected_date).tz_convert('UTC')

    # Filter for the specified day, month, and year
    df_day = df[(df['Datetime'].dt.day == selected_date_utc.day) &
                (df['Datetime'].dt.month == selected_date_utc.month) &
                (df['Datetime'].dt.year == selected_date_utc.year)]

    # Check if there are any entries for the given date
    if df_day.empty:
        print(f"No data available for {selected_date_utc}")
        return None

    # Calculate the interval based on the 'Datetime' column
    interval_start = df_day['Datetime'].min()
    interval_end = df_day['Datetime'].max()

    # Display the interval
    print(f"Interval for {selected_date_utc}: {interval_start} to {interval_end}")

    return df_day
