import os
from .general.create_dynamic_maps import create_maps

def choose_directory(options, item_type):
    print(f"Select a {item_type}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    choice = int(input(f"Enter the number of your choice: "))
    return options[choice - 1]

def construct_input_filename(base_path, *components):
    return os.path.join(base_path, *components).replace('\\', '/')

def list_and_select(base_path, item_type):
    items = os.listdir(base_path)
    selected_item = choose_directory(items, item_type)
    return selected_item

def generate_fancy_maps(base_path, output_directory, color_configuration, coordinates_configuration, custom_font):
    current_path = base_path
    selected_items = []

    while True:
        selected_item = list_and_select(current_path, "item")
        selected_items.append(selected_item)
        
        if selected_item.endswith(".csv"):
            break
        
        current_path = os.path.join(current_path, selected_item)

    # Construct input_filename based on user selections
    input_filename = construct_input_filename(base_path, *selected_items)
    
    # Now you can use the input_filename to perform further operations
    print(f"Constructed input filename: {input_filename}")

    create_maps(input_filename, output_directory, color_configuration, coordinates_configuration, custom_font)


