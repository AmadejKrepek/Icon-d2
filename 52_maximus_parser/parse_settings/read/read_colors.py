def read_colors(file_path):
    color_configurations = {}

    with open(file_path, "r") as config_file:
        lines = config_file.readlines()

    for line in lines:
        line = line.strip()
        if line:
            config_name, colors = line.split(" = ")
            color_configurations[config_name] = colors.split(",")

    return color_configurations