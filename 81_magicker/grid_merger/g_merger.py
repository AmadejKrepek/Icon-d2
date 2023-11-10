from retriever.grid_retriever import fetch_and_process_data
from utils.utils import establish_icon_d2_database_connection


def create_grid_with_lat_lon(table_name, start_date, end_date, model_run):
    conn_grid = establish_icon_d2_database_connection()
    df_grid = fetch_and_process_data(conn_grid, table_name, start_date, end_date, model_run)
    return df_grid
