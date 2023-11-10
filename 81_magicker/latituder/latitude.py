

def get_lat_lon_from_basic(conn_stations, station_table):
    try:
        cursor = conn_stations.cursor()
        cursor.execute("SELECT latitude, longitude FROM basic WHERE station_name = %s", (station_table,))
        row = cursor.fetchone()

        if row:
            latitude, longitude = row
            return latitude, longitude
        else:
            print(f"No latitude and longitude found for station {station_table}.")
            return None, None
    except Exception as e:
        print(f"Error getting latitude and longitude: {e}")
        return None, None