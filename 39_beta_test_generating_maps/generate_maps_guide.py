from create_dynamic_maps import create_maps
import os

storage_directory = './data'

base_path = os.path.join(storage_directory, 'output')

create_maps(input_filename)