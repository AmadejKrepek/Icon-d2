from utils.tools import changeGroupedCoordinatesConfiguration

def extract_and_save_lat_lon(df, provider_name, model_name):
    latitude_longitude_df = df[['Latitude', 'Longitude']]
    
    output_csv_path = changeGroupedCoordinatesConfiguration(model_name)
    
    # Write the extracted DataFrame to a CSV file
    latitude_longitude_df.to_csv(output_csv_path, index=False)
    
    print(f'Latitude and Longitude data saved to {output_csv_path}')