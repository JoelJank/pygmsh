import json
import os
from pathlib import Path


def json_read(file_path):
    """Function to read json files

    Args:
        file_path (string): File Path to the json file

    Returns:
        dict: Parsed JSON data
    """
    with open(file_path, 'r') as f:
        file = json.load(f)
    return file

def save_json_to_savespace(jsonPath):
    """Saves the json file used to create the case in the same folder the mesh is saved

    Args:
        jsonPath (string): Absolute Path to the json file

    Raises:
        ValueError: Missing savespace information in general.json file
        ValueError: Missing casename information in general.json file
    """
    general = json.load(open(os.path.join(jsonPath, "general.json")))
    geom = json.load(open(os.path.join(jsonPath, "geom.json")))
    mesh = json.load(open(os.path.join(jsonPath, "mesh.json")))

    savepath = general.get("savespace")
    os.makedirs(savepath, exist_ok=True)
    name_settings = general.get("casename")
    generalName = name_settings + "_general.json"
    geomName = name_settings + "_geom.json"
    meshName = name_settings + "_mesh.json"

    files = [[general, generalName], [geom, geomName], [mesh, meshName]]

    if not savepath:
        raise ValueError("No 'savespace' key found in the JSON file.")
    if not name_settings:
        raise ValueError("No 'casename' key found in the JSON file.")
    for i in range(3):

        file_paths = os.path.join(savepath, files[i][1])
        with open(file_paths, 'w') as f:
            json.dump(files[i][0], f, indent = 4)


    
    