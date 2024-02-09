import pandas as pd

from features.choicer.choice import getChosenDate, getPredefinedDates
from features.coordinates.getProviderModel import getProviderModel
from features.data_management.data_management import convert_data, createAgregates
from features.database.db_connector import create_db_connection
from features.filter.filter import filterSpecificDate
from features.merger.merge import merge_lat_lon_with_grid_data
from features.split.splitter import split_data


def fetch_data(data, parameter, day, agg):
    try:
        table_name = 'Data'
        conn = create_db_connection()
        provider_id, model_id = getProviderModel(parameter)
        csv_data, interval = merge_lat_lon_with_grid_data(conn, provider_id, model_id, data)
        if csv_data is None:
            return None
        df = pd.DataFrame(csv_data, columns=['Datetime', table_name, 'Latitude', 'Longitude'])
        date_choice = int(day)
        predefinedDates = getPredefinedDates(data['start_date'], data['end_date'])
        df, selected_date = filterSpecificDate(df, date_choice, predefinedDates)
        df = convert_data(df, table_name)
        if agg == "max" or agg == "min":
            aggregatedParameter = agg + "_" + parameter
            df.rename(columns={table_name: aggregatedParameter}, inplace=True)
            df_array = [createAgregates(df, agg, aggregatedParameter)]
        else:
            df_array = split_data(df, interval)
    except Exception as e:
        print(f"Error while fetching data: {e}")
        return None
    return df_array, selected_date
