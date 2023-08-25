from generate_maps import generate_plots

# Define your input and output directories
input_directory = '../38_automatization_part_2/data/output/2_metre_temperature/max/2023/08/25/12z/'
output_directory = '../38_automatization_part_2/data/public/plots/'

# Define the variables and settings
variables_and_settings = [
    ("2 metre temperature", "najvišja temperatura zraka", "temperatura [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
    ("2 metre dewpoint temperature", "najvišja temperatura rosišča", "temperatura rosišča [°C]", cmap_temperature, list(range(-20, 40, 1)), (-20, 40)),
]

# Call the generate_plots function to generate and save the plots
generate_plots(variables_and_settings, input_directory, output_directory)