
import os

def removeDirectories(deleted_directory):
    while os.path.basename(deleted_directory) != "downloaded_grib_files":
        os.rmdir(deleted_directory)
        deleted_directory = os.path.dirname(deleted_directory)