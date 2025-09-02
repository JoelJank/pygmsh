import pygmsh
import meshio
import gmsh
import json
import math
import os
import numpy as np

settings_path = "settings/settings.json"

with open(settings_path, 'r') as f:
    settings = json.load(f)

nFences =  settings["number_of_fences"]
hFences = settings["height_of_fences"]
dxFences = settings["distance_of_fences"]
nSlits = settings["number_of_slits"]
hChannel = settings["height_of_channel"]
lChannel = settings["width_of_channel"]
xfirstfence = settings["xpos_firstfence"]
resolution = settings["mesh_resolution"]

# Checks on parameters
if hChannel > 10*hFences:
    hChannel = 10*hFences

neededwidth = 2* xfirstfence + (nFences-1)*dxFences # make safe that all fences fit in channel and that inlet is the same width as outlet
if lChannel < neededwidth:
    lChannel = neededwidth


#Calculations:

#xpositions of fences:
xposFences = [xfirstfence + i*dxFences for i in range(nFences)]






geo = pygmsh.geo.Geometry()
m = geo.__enter__()

pointsChannel = [
    m.add_point((0.0,0.0,0.0), mesh_size=resolution),
    m.add_point((lChannel,0.0,0.0), mesh_size=resolution),
    m.add_point((lChannel,hChannel,0.0), mesh_size=resolution),
    m.add_point((0.0,hChannel,0.0), mesh_size=resolution)
] +[
    m.add_point((xposFences[i],0.0,0.0), mesh_size=resolution) for i in range(nFences)
] +[
    m.add_point((xposFences[i],hChannel,0.0),mesh_size=resolution) for i in range(nFences)
]


m.synchronize()
geo.generate_mesh(dim=2)
gmsh.write("test2.msh")
geo.__exit__()

