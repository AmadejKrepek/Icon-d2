# cache_manager.py

from datetime import datetime, timedelta


def generate_cache_key(parameter, day, agg, start_date):
    return f'weather_data_{parameter}_{day}_{agg}_{start_date}'


def store_last_records(parameter, day, agg, start_date, img_io, cache):
    cache_key = generate_cache_key(parameter, day, agg, start_date)

    # Retrieve the current cache records or initialize an empty list
    current_records = cache.get(cache_key) or []

    # Remove records older than 2 days
    current_records = [record for record in current_records if
                       datetime.now() - record['timestamp'] <= timedelta(days=2)]

    # Append the new record to the list
    current_records.append({'timestamp': datetime.now(), 'data': img_io})

    # Save the updated list in the cache
    cache.set(cache_key, current_records, timeout=None)  # No need to set a timeout


def get_last_records(parameter, day, agg, start_date, cache):
    cache_key = generate_cache_key(parameter, day, agg, start_date)
    return cache.get(cache_key) or []
