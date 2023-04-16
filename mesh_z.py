import os
import json

def import_from_object_directory_path(directory_path):
    object_json_path = os.path.join(directory_path, 'object.json')
    with open(object_json_path, 'r') as object_json_file:
        object_json = json.load(object_json_file)
    print(object_json)
