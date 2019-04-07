import json
import os


def write_data_in_file(data, file_name):
    if file_name:
        with open(file_name, "w") as file:
            json.dump(data, file, indent=2)
            return True
    return False


def read_data_from_file(file_name):
    if file_name and os.path.isfile(file_name):
        with open(file_name, "r") as file:
            return json.load(file)
    return None
