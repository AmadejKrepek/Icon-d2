import pandas as pd

import pandas as pd
from scipy.spatial import cKDTree

import pandas as pd
from scipy.spatial import cKDTree
from tqdm import tqdm



def correct_data(df_stations, df_grid):
    # Create a KDTree for station coordinates
    tree_stations = cKDTree(df_stations[['Latitude', 'Longitude']].values)

    # Create a copy of df_grid to store the corrected values
    corrected_data = df_grid.copy()

    # Add new columns 'Station_Temperature' and 'Station_Name'
    corrected_data['Station_Temperature'] = None
    corrected_data['Station_Name'] = None

    # Find the index of the closest station in df_stations for the first interval for every station
    _, station_indices_first = tree_stations.query(df_grid.loc[df_grid['Datetime'] == df_grid.iloc[0]['Datetime']][['Latitude', 'Longitude']].values)

    # Iterate through each unique timestamp in df_grid with tqdm for a progress bar
    for timestamp in tqdm(corrected_data['Datetime'].unique(), desc='Correcting data'):
        # Filter df_grid for the current timestamp
        df_grid_timestamp = corrected_data[corrected_data['Datetime'] == timestamp]

        # Find the index of the closest station in df_stations for all points in the timestamp
        _, station_indices = tree_stations.query(df_grid_timestamp[['Latitude', 'Longitude']].values)

        # Get the corresponding indices from the first interval for all stations in the timestamp
        station_indices_first_timestamp = station_indices_first[station_indices]

        # Update the 'Value', 'Station_Temperature', and 'Station_Name' columns in df_grid
        corrected_data.loc[corrected_data['Datetime'] == timestamp, 'Value'] = df_stations.iloc[station_indices_first_timestamp]['Temperature'].values
        corrected_data.loc[corrected_data['Datetime'] == timestamp, 'Station_Temperature'] = df_stations.iloc[station_indices_first_timestamp]['Temperature'].values
        corrected_data.loc[corrected_data['Datetime'] == timestamp, 'Station_Name'] = df_stations.iloc[station_indices_first_timestamp]['StationName'].values

    return corrected_data