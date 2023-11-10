from latituder.latitude import get_lat_lon_from_basic
from retriever.retriever import get_tables_with_prefix
from utils.utils import establish_database_connection

# Get tables with the specified prefixes
prefixes = ['auto', 'obs']


def create_stations_with_lat_lon():
    conn_stations = establish_database_connection()
    station_names = get_station_names(conn_stations)
    data = get_lat_lon(conn_stations, station_names)
    print('test')


def get_station_names(conn):
    station_names = []
    for prefix in prefixes:
        station_name = get_tables_with_prefix(conn, prefix)
        station_names.extend(station_name)  # Use extend instead of append
    return station_names


def get_lat_lon(conn, station_names):
    data = []
    for name in station_names:
        latitude, longitude = get_lat_lon_from_basic(conn, name)
        print(latitude, longitude)
        data.append([latitude, longitude])
    return data
