def get_latitudes_and_longitudes(provider_id, model_id, conn):
    try:
        # Create a cursor object
        cursor = conn.cursor()

        # Query the latitudes and longitudes based on provider_id and model_id from the lat_lon_schema table
        cursor.execute("SELECT latitudes, longitudes FROM lat_lon_schema WHERE provider_id = %s AND model_id = %s",
                       (provider_id, model_id))

        # Fetch the row
        row = cursor.fetchone()

        if row:
            latitudes, longitudes = row
            return latitudes, longitudes
        else:
            print(f"No latitudes and longitudes found for provider_id {provider_id} and model_id {model_id}.")
            return None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None