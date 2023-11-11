import pandas as pd


import pandas as pd
from scipy.spatial import cKDTree

def correct_data(df_stations, df_grid):
    # Create a KDTree for stations
    tree_stations = cKDTree(df_stations[['Latitude', 'Longitude']].values)

    # Query the tree for each grid point to find the nearest station
    df_grid['station_index'] = tree_stations.query(df_grid[['Latitude', 'Longitude']].values)[1]

    # Merge the DataFrames based on the station_index
    df_merged = pd.merge(df_grid, df_stations, left_on='station_index', right_index=True, how='left')

    # Keep only necessary columns for further comparison
    df_merged = df_merged[['Datetime', 'Value', 'Latitude_x', 'Longitude_x', 'ValidUtc', 'Temperature']]

    # Replace the 'Value' column in df_merged with the 'Temperature' column where Datetime and ValidUtc match
    tolerance = pd.Timedelta(seconds=1)  # Adjust the tolerance as needed
    df_merged['Datetime'] = pd.to_datetime(df_merged['Datetime'])
    df_merged['ValidUtc'] = pd.to_datetime(df_merged['ValidUtc'])
    mask = (df_merged['Datetime'] - df_merged['ValidUtc']).abs() < tolerance
    df_merged.loc[mask, 'Value'] = df_merged['Temperature']

    # Drop unnecessary columns
    df_result = df_merged.drop(['ValidUtc'], axis=1)

    # Rename columns
    df_result = df_result.rename(columns={'Latitude_x': 'Latitude', 'Longitude_x': 'Longitude'})

    # Sort the DataFrame by the 'Datetime' column
    df_result = df_result.sort_values(by='Datetime')

    # Replace 'Temperature' values in 'Value' where 'Temperature' is not None or NaT
    df_result['Value'] = df_result.apply(lambda row: row['Temperature'] if pd.notna(row['Temperature']) else row['Value'], axis=1)

    # Reset the index of the resulting DataFrame
    df_result = df_result.reset_index(drop=True)

    return df_result
