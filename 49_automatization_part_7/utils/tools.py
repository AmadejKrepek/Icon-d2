import sys

def changeCoordinatesConfiguration(model_directory):
    if model_directory == "IconD2":
        return "./configuration/coordinates/icon_d2_lat_lon.csv"
    elif model_directory == "Aladin":
        return "./configuration/coordinates/aladin_lat_lon.csv"
    else:
        print("Invalid configuration coordinates for this model. Exiting.")
        sys.exit(1)
        
def changeGroupedCoordinatesConfiguration(model_directory):
    if model_directory == "IconD2":
        return "./configuration/coordinates/grouped/icon_d2_lat_lon_grouped.csv"
    elif model_directory == "Aladin":
        return "./configuration/coordinates/grouped/aladin_lat_lon_grouped.csv"
    else:
        print("Invalid configuration coordinates for this model. Exiting.")
        sys.exit(1)