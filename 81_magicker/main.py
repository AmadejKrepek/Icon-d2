from datetime import datetime, timedelta

import pytz

from station_latitude_merger.sl_merger import create_stations_with_lat_lon
from grid_merger.g_merger import create_grid_with_lat_lon
from filter.filter_stations import filter_hourly_intervals
from dotenv import load_dotenv

load_dotenv()

# Specify start_date and end_date in Europe/Ljubljana timezone
local_tz = pytz.timezone('Europe/Ljubljana')
start_date = local_tz.localize(datetime(2023, 11, 1, 00, 00, 00))
end_date = start_date + timedelta(days=2)
model_run = "0"

df_stations = create_stations_with_lat_lon(start_date, end_date)
df_grid = create_grid_with_lat_lon("2_metre_temperature_icond2", start_date, end_date, model_run)
filter_hourly_intervals(df_stations)
print('test')