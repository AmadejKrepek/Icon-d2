import os


def removeDirectories(deleted_directory):
    while os.path.basename(deleted_directory) != "downloaded_grib_files":
        try:
            if os.path.exists(deleted_directory) and os.path.isdir(deleted_directory):
                print(f"It exists: {deleted_directory}")
                os.rmdir(deleted_directory)
        except OSError:
            print("An error occurred while removing the directory.")

        deleted_directory = os.path.dirname(deleted_directory)
        print(f"Next deleted directory: {deleted_directory}")
