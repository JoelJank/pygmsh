import json


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
    
    