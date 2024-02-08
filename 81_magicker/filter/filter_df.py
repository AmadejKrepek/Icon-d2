import pandas as pd


def filter_dataframes_on_datetime(df1, df2, datetime_column_df1, datetime_column_df2):
    """
    Keep only the rows in each DataFrame that have matching datetime values.

    Parameters:
    - df1: First DataFrame
    - df2: Second DataFrame
    - datetime_column_df1: Name of the datetime column in the first DataFrame
    - datetime_column_df2: Name of the datetime column in the second DataFrame

    Returns:
    - Tuple of filtered DataFrames
    """
    # Convert datetime columns to datetime type
    df1[datetime_column_df1] = pd.to_datetime(df1[datetime_column_df1])
    df2[datetime_column_df2] = pd.to_datetime(df2[datetime_column_df2])

    # Filter rows based on the specified datetime columns
    filtered_df1 = df1[df1[datetime_column_df1].isin(df2[datetime_column_df2])]
    filtered_df2 = df2[df2[datetime_column_df2].isin(df1[datetime_column_df1])]

    return filtered_df1, filtered_df2