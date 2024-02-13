from datetime import timedelta

from features.split.split_df import split_dataframe_by_hour, split_dataframe_by_specific_hours_and_minutes


def split_data(df, interval):
    if interval == timedelta(hours=1):
        dfs = split_dataframe_by_hour(df)
    elif interval == timedelta(minutes=15):
        dfs = split_dataframe_by_specific_hours_and_minutes(df)
    else:
        raise ValueError(f"Interval is different: {interval}")
    return dfs
