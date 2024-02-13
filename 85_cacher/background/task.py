import base64
from datetime import timedelta, datetime
from io import BytesIO


def generate_cache_key(parameter):
    return f'{parameter}'


async def store_last_records(parameter, day, agg, start_date, img_io, cache):
    cache_key = generate_cache_key(parameter)
    # await cache.delete(cache_key)
    # await cache.clear()
    # Retrieve the current cache records or initialize an empty list
    current_records = await cache.get(cache_key) or []

    # Check if the new data already exists in the records
    new_data_exists = any(
        record['start_date'] == start_date
        and record['parameter'] == parameter
        and record['day'] == day
        and record['agg'] == agg
        for record in current_records)

    if not new_data_exists:
        current_records = [
            record for record in current_records
            if datetime.now() - datetime.strptime(record['start_date'], '%Y-%m-%d %H:%M:%S') <= timedelta(days=2)
        ]

        # Convert bytes to string using base64 encoding
        img_data_str = base64.b64encode(img_io.getvalue()).decode('utf-8')
        # Append the new record to the list
        current_records.append({'data': img_data_str, 'start_date': start_date,
                                'day': day, 'parameter': parameter, 'agg': agg})

        current_records = sorted(current_records, key=lambda x: x['start_date'])

        # Save the updated list in the cache
        await cache.set(cache_key, current_records, timeout=None)  # No need to set a timeout


async def get_last_records(parameter, start_date, day, agg, cache):
    cache_key = generate_cache_key(parameter)

    # Retrieve the serialized data from the cache
    all_records = await cache.get(cache_key) or []

    # Find the first record that matches all specified conditions
    matching_record = next(
        (record for record in all_records
         if record.get('parameter') == parameter
         and record.get('start_date') == start_date
         and record.get('day') == int(day)
         and record.get('agg') == agg),
        None  # Default value if no matching record is found
    )

    if matching_record:
        img_data_str = matching_record.get('data')
        img_data_bytes = base64.b64decode(img_data_str)
        img_io = BytesIO(img_data_bytes)
        matching_record['data'] = img_io

    return [matching_record] if matching_record else []
