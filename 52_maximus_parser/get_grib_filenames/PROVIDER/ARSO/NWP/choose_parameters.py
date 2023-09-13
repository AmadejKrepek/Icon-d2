from .find_latest.find_latest_model_run import get_latest_model_run_filenames
from datetime import datetime

def getGribFileNames():
    print("Script started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    base_url = "https://meteo.arso.gov.si/uploads/probase/www/model/data/"
    filenames = get_latest_model_run_filenames(base_url)

    if not filenames:
        print("No filenames available for the selected parameters.")

    print("Script finished at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return filenames
