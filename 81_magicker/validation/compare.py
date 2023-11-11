import pandas as pd


def compare_values(old_df, corrected_df):
    # Merge old and corrected DataFrames based on the common columns
    merged_df = pd.merge(old_df, corrected_df, on=['Datetime', 'Latitude', 'Longitude'], suffixes=('_old', '_corrected'))

    # Calculate the absolute difference between the 'Value' columns
    merged_df['Value_difference'] = abs(merged_df['Value_old'] - merged_df['Value_corrected'])

    return merged_df[['Datetime', 'Latitude', 'Longitude', 'Value_old', 'Value_corrected', 'Value_difference']]