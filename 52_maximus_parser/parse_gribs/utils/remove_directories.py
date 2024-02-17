import os


def removeDirectories(deleted_directory):
    while os.path.basename(deleted_directory) != "downloaded_grib_files":
        try:
            os.rmdir(deleted_directory)
        except OSError:
            print(f"COntinue there?")
            pass  # Continue the loop even if an OSError occurs
        deleted_directory = os.path.dirname(deleted_directory)
        print(f"NExt deleted directory: {deleted_directory}")
