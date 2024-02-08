import os
from PIL import Image
from natsort import natsorted


def create_gif_from_png(directory_path, output_filename, duration=500):
    directory_path = os.path.dirname(directory_path)

    # Get all PNG files in the specified directory
    png_files = [f for f in os.listdir(directory_path) if f.endswith('.png')]

    # Sort the files based on their names (assuming the names represent the order)
    # Use natsorted to sort the files naturally
    png_files = natsorted(png_files)

    # Create a list to store the images
    images = []

    # Read each PNG file and append it to the list
    for png_file in png_files:
        image_path = os.path.join(directory_path, png_file)
        img = Image.open(image_path)
        images.append(img)

    # Get the directory path from the output_filename
    output_directory = os.path.dirname(output_filename)

    # Save the images as a GIF file
    output_filepath = os.path.join(output_directory, 'output.gif')
    images[0].save(output_filepath, save_all=True, append_images=images[1:], duration=duration, loop=0)
