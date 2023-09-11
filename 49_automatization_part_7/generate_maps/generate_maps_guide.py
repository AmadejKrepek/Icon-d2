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

def generate_fancy_maps(base_path, output_directory, color_configuration, custom_font):
    current_path = base_path
    selected_items = []
    provider_directory = None
    model_directory = None

    while True:
        selected_item = list_and_select(current_path, "item")
        selected_items.append(selected_item)

        # Check if we've reached the end of the directory structure
        if os.path.isfile(os.path.join(current_path, selected_item)):
            break

        # Check if the selected item is the provider or model directory
        if selected_item in ["DWD", "ARSO"]:  # Adjust these values to match your provider names
            provider_directory = selected_item
        elif selected_item in ["IconD2", "Aladin"]:  # Adjust these values to match your model names
            model_directory = selected_item

        current_path = os.path.join(current_path, selected_item)

    # Combine the provider and model directories with the output_directory
    if provider_directory and model_directory:
        output_directory = os.path.join(output_directory, provider_directory, model_directory)

    # Construct input_filename based on user selections
    input_filename = construct_input_filename(base_path, *selected_items)
    
    # Now you can use the input_filename to perform further operations
    print(f"Constructed input filename: {input_filename}")

    create_maps(input_filename, output_directory, color_configuration, custom_font)


