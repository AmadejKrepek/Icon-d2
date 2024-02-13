import os


def get_cache_data(directory_path, encodings=None):
    if encodings is None:
        encodings = ['utf-8', 'latin-1']
    cache_data = {}

    if not os.path.exists(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return cache_data

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path):
            decoded_data = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        # Try to read and store the cache data from the file
                        decoded_data = file.read()
                        break  # If successful, break out of the loop
                except UnicodeDecodeError:
                    continue  # Try the next encoding if decoding fails

            if decoded_data is not None:
                cache_data[filename] = decoded_data
            else:
                print(f"Error decoding file '{filename}': Unable to decode with the specified encodings")

    return cache_data