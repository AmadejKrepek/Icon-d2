import pandas as pd

from features.data_management.data_management import convert_data, createAgregates
from features.filter.filter import filterSpecificDate
from features.merger.merge import merge_lat_lon_with_grid_data
from features.split.splitter import split_data


def extract_coordinates(coord_str):
    # Extract latitude and longitude from the coordinate string
    coord_str = coord_str.strip('()')
    lat, lon = map(float, coord_str.split(', '))
    return lat, lon


def write_data_to_csv_with_coordinates(selected_start_date, selected_end_date, selected_model_run, date_choice,
                                       table_name, output_file, provider_id, model_id, conn, sort_interval, agg_function, end_date):
    try:

        csv_data, interval = merge_lat_lon_with_grid_data(conn, table_name, selected_start_date, selected_end_date, selected_model_run, provider_id, model_id)

        if csv_data is None:
            print(f"No data found in table '{table_name}'.")
            return ValueError("Wrong")

        if interval is None:
            print(f"Interval is not correct.")
            return ValueError("Interval is not correct.")

        if sort_interval == "1":
            agg_name = 'animation' + '_' + table_name
        else:
            agg_name = agg_function + '_' + table_name
        df = pd.DataFrame(csv_data, columns=['Datetime', agg_name, 'Latitude', 'Longitude'])

        df, selected_date = filterSpecificDate(df, date_choice, end_date)
        df.to_csv('test.csv')

        df = convert_data(df, agg_name)
        if sort_interval == "0":
            df_array = [createAgregates(df, agg_function, table_name)]
        else:
            df_array = split_data(df, interval)
        conn.close()

        return df_array, selected_date

    except Exception as e:
        print(f"Error: {e}")