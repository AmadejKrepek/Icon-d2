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
    df_merged = df_merged[['Datetime', 'Value', 'Latitude_x', 'Longitude_x', 'ValidUtc']]

    # Replace the 'Value' column in df_merged with the 'Temperature' column where Datetime and ValidUtc match
    df_merged.loc[df_merged['Datetime'] == df_merged['ValidUtc'], 'Value'] = df_merged['Value']

    # Drop unnecessary columns
    df_result = df_merged.drop(['ValidUtc'], axis=1)

    # Rename columns
    df_result = df_result.rename(columns={'Latitude_x': 'Latitude', 'Longitude_x': 'Longitude'})

    # Sort the DataFrame by the 'Datetime' column
    df_result = df_result.sort_values(by='Datetime')

    # Reset the index of the resulting DataFrame
    df_result = df_result.reset_index(drop=True)

    return df_result
