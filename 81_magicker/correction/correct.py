import pandas as pd
from numpy import dtype
from scipy.spatial import cKDTree


def correct_data(df_stations, df_grid):
    # Assuming df_stations and df_grid are your DataFrames

    # Create a KDTree for stations
    tree_stations = cKDTree(df_stations[['Latitude', 'Longitude']].values)

    # Query the tree for each grid point to find the nearest station
    df_grid['station_index'] = tree_stations.query(df_grid[['Latitude', 'Longitude']].values)[1]

    # Merge the DataFrames based on the station_index
    df_merged = pd.merge(df_grid, df_stations, left_on='station_index', right_index=True)

    # Now, you can replace the 'Value' column in df_grid with the 'Temperature' column in df_stations
    df_merged['Value'] = df_merged['Temperature']

    # Drop unnecessary columns
    df_merged = df_merged.drop(['Latitude_y', 'Longitude_y', 'station_index'], axis=1)

    # Make sure ValidUtc and Datetime columns are matched
    df_merged = df_merged[df_merged['ValidUtc'] == df_merged['Datetime']]

    # Drop extra columns if needed
    df_result = df_merged[['Datetime', 'Latitude_x', 'Longitude_x', 'Value']]

    df_result = df_result.rename(columns={'Latitude_x': 'Latitude', 'Longitude_x': 'Longitude'})

    # Reorder the columns so that 'Value' comes first
    df_result = df_result[['Datetime', 'Value', 'Latitude', 'Longitude']]

    # Sort the DataFrame by the 'Datetime' column
    df_result = df_result.sort_values(by='Datetime')

    # If you want to reset the index of the resulting DataFrame
    df_result = df_result.reset_index(drop=True)

    return df_result
