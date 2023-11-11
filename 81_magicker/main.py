from datetime import datetime, timedelta

import pytz

from station_latitude_merger.sl_merger import create_stations_with_lat_lon
from grid_merger.g_merger import create_grid_with_lat_lon
from filter.filter_stations import filter_hourly_intervals
from correction.correct import correct_data
from validation.compare import compare_values
from generate_maps.plot import create_plot
from intervaler.interval import create_interval
from aggregates.aggregate import create_agregates
from dotenv import load_dotenv

load_dotenv()

# Specify start_date and end_date in Europe/Ljubljana timezone
local_tz = pytz.timezone('Europe/Ljubljana')
start_date = local_tz.localize(datetime(2023, 11, 1, 00, 00, 00))
end_date = start_date + timedelta(days=2)
model_run = "0"

df_stations = create_stations_with_lat_lon(start_date, end_date)

df_grid = create_grid_with_lat_lon("2_metre_temperature_icond2", start_date, end_date, model_run)

df_stations_filtered = filter_hourly_intervals(df_stations)

df_corrected_grid = correct_data(df_stations_filtered, df_grid)

df_grid.to_csv('original.csv')
df_corrected_grid.to_csv('corrected_original.csv')

# Only change grid there
df_grid_selected_date = create_interval(start_date, df_corrected_grid)

df_grid_create_aggregate = create_agregates(df_grid_selected_date, 'max')

create_plot(model_run, df_grid_create_aggregate, start_date, end_date, start_date)
# compare_values(df_grid, df_corrected_grid)
print('test')
