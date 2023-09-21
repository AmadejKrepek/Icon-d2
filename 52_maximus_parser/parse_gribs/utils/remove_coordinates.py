def delete_coordinates(df):
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df = df.drop(['Latitude', 'Longitude'], axis=1)
    return df