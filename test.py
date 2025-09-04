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

#ypositions of slits in fences:
if nSlits > 1:
    dySlits = hFences/(nSlits)
    yposSlits = [j*dySlits for j in range(1,nSlits+1)]
else:
    yposSlits = [hFences]

plane_corner = np.empty((nFences+2,2), dtype = object)
fences_slitpos = np.empty((nFences+2,nSlits), dtype = object)
vertical_lines = np.empty((nFences+2,nSlits+1), dtype = object)
horizontal_lines = np.empty((2,nFences+1), dtype = object)
plane_loops = np.empty((nFences+1), dtype = object)
plane_surfaces = np.empty((nFences+1), dtype= object)

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

#Create points for the corners of the planes
plane_corner[0][0] = m.add_point((0.0,0.0,0.0), mesh_size=resolution) # (0,0)
plane_corner[0][1] = m.add_point((0.0,hChannel,0.0), mesh_size=resolution) # (0,hChannel)

for i in range(1,nFences+1):
    plane_corner[i][0] = m.add_point((xposFences[i-1],0.0,0.0), mesh_size=resolution) # (xpos of fences, 0)
    plane_corner[i][1] = m.add_point((xposFences[i-1],hChannel,0.0), mesh_size=resolution) # (xpos of fences, hChannel)

plane_corner[nFences+1][0] = m.add_point((lChannel,0.0,0.0), mesh_size=resolution) # (lChannel,0)
plane_corner[nFences+1][1] = m.add_point((lChannel,hChannel,0.0), mesh_size=resolution) # (lChannel,hChannel)


#create points for the slits of the fences:

for i in range(nSlits):
    fences_slitpos[0][i] = m.add_point((0.0,yposSlits[i],0.0),mesh_size=resolution) # (0,ypos of slits)
    fences_slitpos[nFences+1][i] = m.add_point((lChannel,yposSlits[i],0.0),mesh_size=resolution) # (lChannel,ypos of slits)

for i in range(1, nFences+1):
    for j in range(nSlits):
        fences_slitpos[i][j] = m.add_point((xposFences[i-1],yposSlits[j],0.0),mesh_size=resolution) # (xpos of fences, ypos of slits)

#create vertical lines for the channel at every fence position and at inlet / outlet

for i in range(nFences+2):
    vertical_lines[i][0] = m.add_line(plane_corner[i][0],fences_slitpos[i][0])
    for j in range(nSlits-1):
        vertical_lines[i][j+1] = m.add_line(fences_slitpos[i][j],fences_slitpos[i][j+1])
    vertical_lines[i][-1] = m.add_line(fences_slitpos[i][-1],plane_corner[i][1])
    # Die ersten n slits sind die Linien zwischen den slits, der letzte eintrage ist das fence top

print("start")
#create horizontal lines for the channel at top and bottom + create channel plane loops
for i in range(nFences+1):
    horizontal_lines[0][i] = m.add_line(plane_corner[i][0], plane_corner[i+1][0])  # bottom line
    horizontal_lines[1][i] = m.add_line(plane_corner[i+1][1], plane_corner[i][1])  # top line
    plane_loops[i] = m.add_curve_loop(
        [horizontal_lines[0][i]] +
        list(vertical_lines[i+1]) +
        [horizontal_lines[1][i]] +
        [ -l for l in reversed(vertical_lines[i]) ]
    )
    plane_surfaces[i] = m.add_plane_surface(plane_loops[i])






m.synchronize()
geo.generate_mesh(dim=2)
gmsh.write("test3.msh")
geo.__exit__()

