import pandas as pd

def add_lat_lon_columns_from_configuration_file(df, configuration_file):
    # Load the configuration file
    config_df = pd.read_csv(configuration_file)
    # Get the latitude and longitude values from the configuration file
    latitudes = config_df['Latitude']
    longitudes = config_df['Longitude']
    # Add the latitude and longitude values to the DataFrame
    df['Latitude'] = latitudes
    df['Longitude'] = longitudes
    return df