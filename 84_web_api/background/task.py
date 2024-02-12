# cache_manager.py

from datetime import datetime, timedelta


def generate_cache_key(parameter):
    return f'{parameter}'


def store_last_records(parameter, day, agg, start_date, img_io, cache):
    cache_key = generate_cache_key(parameter)

    # Retrieve the current cache records or initialize an empty list
    current_records = cache.get(cache_key) or []

    # Check if the new data already exists in the records
    new_data_exists = any(
        record['start_date'] == start_date
        and record['parameter'] == parameter
        and record['day'] == day
        and record['agg'] == agg
        for record in current_records)

    if not new_data_exists:
        # Remove records older than 2 days
        current_records = [record for record in current_records if
                           datetime.now() - record['timestamp'] <= timedelta(days=2)]

        # Append the new record to the list
        current_records.append({'timestamp': datetime.now(), 'data': img_io, 'start_date': start_date,
                                'day': day, 'parameter': parameter, 'agg': agg})

        current_records = sorted(current_records, key=lambda x: x['start_date'])
        # Save the updated list in the cache
        cache.set(cache_key, current_records, timeout=None)  # No need to set a timeout


def get_last_records(parameter, start_date, day, agg, cache):
    cache_key = generate_cache_key(parameter)
    all_records = cache.get(cache_key) or []

    # Find the first record that matches all specified conditions
    matching_record = next(
        (record for record in all_records
         if record.get('parameter') == parameter
            and record.get('start_date') == start_date
            and record.get('day') == int(day)
            and record.get('agg') == agg),
        None  # Default value if no matching record is found
    )

    return [matching_record] if matching_record else []



