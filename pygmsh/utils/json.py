import json
import os


def json_read_2D(file_path):
    with open(file_path, 'r') as f:
        file = json.load(f)
    
    data_dict ={
        "nFences": file["number_of_fences"],
        "hFences": file["height_of_fences"],
        "dxFences": file["distance_of_fences"],
        "nSlits": file["number_of_slits"],
        "hChannel": file["height_of_channel"],
        "lChannel": file["width_of_channel"],
        "xfirstfence": file["xpos_firstfence"],
        "resolution": file["mesh_resolution"],
        "meshFreesize": file["mesh_freesize"],
        "meshFirstlayerheight": file["mesh_firstlayerheight"],
        "meshGrowthrate": file["mesh_growthrate"],
        "meshNumberofinflationlayers": file["inflation_layers"],
        "meshgrowthafterinflation": file["meshgrowtrate_afterinflation"],
        "savespace": file["savespace"]
    }
    return data_dict


def json_read_3D(file_path):
    with open(file_path, 'r') as f:
        file = json.load(f)
    return file

def save_json_to_savespace(file_path):
    data = json_read_3D(file_path)

    save_path = data.get("savespace")
    name_settings = data.get("name")
    if not save_path:
        raise ValueError("No 'savespace' key found in the JSON file.")
    if not name_settings:
        raise ValueError("No 'name_settings' key found in the JSON file.")
    
    save_dir = os.path.dirname(save_path)
    new_file_path = f"{save_dir}/{name_settings}.json"
    os.makedirs(save_dir, exist_ok=True)
    
    with open(new_file_path, 'w') as f:
        json.dump(data, f, indent = 4)


    
    