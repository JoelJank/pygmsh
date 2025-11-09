import pygmsh
import gmsh
import math
import numpy as np
import utils.meshcalc as utils
from utils.json import json_read_3D

settings_path = "../config/settings_3d.json"

settings = json_read_3D(settings_path)
#Erstmal ist das Skript nur für 1 Zaun und vertikale Schlitze ausgelegt, 50% porosity

# Informations about fences and channel
height_fence = settings["height_of_fences"]
depth_fence = settings["depth_fence"]
xpos_fence = settings["xpos_firstfence"]
width_slits = settings["width_of_slits"]
height_channel = settings["height_of_channel"]
length_channel = settings["length_of_channel"]
depth_channel = settings["depth_of_channel"]

#Informations about meshing#
mesh_freesize_xdirection = settings["mesh_freesize_xdirection"]
mesh_freesize_zdirection = settings["mesh_freesize_zdirection"]
mesh_between_slits = settings["resolution_between_slits"]
mesh_firstlayerheight = settings["mesh_firstlayerheight"]
mesh_growthrate = settings["mesh_growthrate"]
mesh_numberofinflationlayers = settings["inflation_layers"]
meshgrowthafterinflation = settings["meshgrowtrate_afterinflation"]

#Savespace
savespace = settings["savespace"]
meshresolution = 1


meshdata, toppoints, nbisoben = utils.inflationcalculation(mesh_firstlayerheight, mesh_growthrate, mesh_numberofinflationlayers, height_fence, 1, height_channel, meshgrowthafterinflation)
meshdata[:,0] = [int(x[0]) + 1 for x in meshdata] #Wichtig, damit wirklich die anzahl an layern genommen wird und gmsh rechnet mit eckpunkten
nbisoben[0] = int(nbisoben[0]) + 1
#Berechnungen für punkte der slits
corner_fence = depth_fence/2
nSlits =  depth_fence / width_slits
zpos_slits = [-round(corner_fence - i * width_slits, 2) for i in range(int(nSlits)+2)]
endofz = corner_fence+depth_fence
frontofz = -endofz

corners_surfaces = np.empty((len(zpos_slits)+2,4), dtype = object) # 0 is bottom, 1 is end of slits in y direction, 2 is end of inflation, 3 is top
horedges_surfaces = np.empty((len(zpos_slits)+1,4), dtype = object) # 0 is bottom, 1 is height fence, 2 is end of inflation, 3 is top
veredges_bottomsurfaces = np.empty((len(zpos_slits)+2), dtype = object) # from bottom to top part of fence
veredges_inflationsurfaces = np.empty((len(zpos_slits)+2), dtype = object) # from end of fence to end of inflation front and back
verdeges_topsurfaces = np.empty((len(zpos_slits)+2), dtype = object) # from end of inflation to top front and back
bottom_loops = np.empty(len(zpos_slits)+1, dtype = object)
bottom_surfaces = np.empty(len(zpos_slits)+1, dtype = object)
inflation_loops = np.empty(len(zpos_slits)+1, dtype = object)
inflation_surfaces = np.empty(len(zpos_slits)+1, dtype = object)
top_loops = np.empty(len(zpos_slits)+1, dtype = object)
top_surfaces = np.empty(len(zpos_slits)+1, dtype = object)
geo = pygmsh.geo.Geometry()
m = geo.__enter__()

#Create Points:

#Points front edge
corners_surfaces[0][0] = m.add_point((0.0, 0.0, frontofz), mesh_size = 1)
corners_surfaces[0][1] = m.add_point((0.0, height_fence, frontofz), mesh_size = 1)
corners_surfaces[0][2] = m.add_point((0.0, toppoints, frontofz), mesh_size = 1)
corners_surfaces[0][3] = m.add_point((0.0, height_channel, frontofz), mesh_size = 1)

#Point at slits

for i in range(1, len(zpos_slits)+1):
    corners_surfaces[i][0] = m.add_point((0.0, 0.0, zpos_slits[i-1]), mesh_size = 1)
    corners_surfaces[i][1] = m.add_point((0.0, height_fence, zpos_slits[i-1]), mesh_size = 1)
    corners_surfaces[i][2] = m.add_point((0.0, toppoints, zpos_slits[i-1]), mesh_size = 1)
    corners_surfaces[i][3] = m.add_point((0.0, height_channel, zpos_slits[i-1]), mesh_size = 1)
    
#Points back edge

corners_surfaces[-1][0] = m.add_point((0.0, 0.0, endofz), mesh_size = 1)
corners_surfaces[-1][1] = m.add_point((0.0, height_fence, endofz), mesh_size = 1)
corners_surfaces[-1][2] = m.add_point((0.0, toppoints, endofz), mesh_size = 1)
corners_surfaces[-1][3] = m.add_point((0.0, height_channel, endofz), mesh_size = 1)

#All points created!!!
#Create lines 
#Horizontal lines
for i in range(len(corners_surfaces)-1):
    horedges_surfaces[i][0] = m.add_line(corners_surfaces[i][0], corners_surfaces[i+1][0]) #bottom
    horedges_surfaces[i][1] = m.add_line(corners_surfaces[i][1], corners_surfaces[i+1][1]) #height fence
    horedges_surfaces[i][2] = m.add_line(corners_surfaces[i][2], corners_surfaces[i+1][2]) #end of inflation
    horedges_surfaces[i][3] = m.add_line(corners_surfaces[i][3], corners_surfaces[i+1][3]) #top

# Vertical lines

for i in range(len(corners_surfaces)):
    veredges_bottomsurfaces[i] = m.add_line(corners_surfaces[i][0], corners_surfaces[i][1]) #from bottom to top part of fence
    veredges_inflationsurfaces[i] = m.add_line(corners_surfaces[i][1], corners_surfaces[i][2]) #from end of fence to end of inflation front
    verdeges_topsurfaces[i] = m.add_line(corners_surfaces[i][2], corners_surfaces[i][3]) #from end of inflation to top front
#ALL LINES CREATED!!!

#Bottom surfaces
for i in range(len(bottom_surfaces)):
    bottom_loops[i] = m.add_curve_loop(
        [horedges_surfaces[i][0]]+
        [veredges_bottomsurfaces[i+1]]+
        [-horedges_surfaces[i][1]]+
        [-veredges_bottomsurfaces[i]]
    )
    bottom_surfaces[i] = m.add_plane_surface(bottom_loops[i])
    
    inflation_loops[i] = m.add_curve_loop(
        [horedges_surfaces[i][1]]+
        [veredges_inflationsurfaces[i+1]]+
        [-horedges_surfaces[i][2]]+
        [-veredges_inflationsurfaces[i]]
    )
    inflation_surfaces[i] = m.add_plane_surface(inflation_loops[i])
    
    top_loops[i] = m.add_curve_loop(
        [horedges_surfaces[i][2]]+
        [verdeges_topsurfaces[i+1]]+
        [-horedges_surfaces[i][3]]+
        [-verdeges_topsurfaces[i]]
    )
    top_surfaces[i] = m.add_plane_surface(top_loops[i])
#Meshing
#Transfinite Curves for horizontal edges
#links und rechts vom zaun
nleftright = math.ceil((depth_fence)/mesh_freesize_zdirection)+1
nbetweenslits = math.ceil((width_slits)/mesh_between_slits)+1
nzdirection,_,_  = utils.layercalcuations(depth_fence, mesh_growthrate, mesh_between_slits)
nzdirection = math.ceil(nzdirection)+1


for i in range(4):
    m.set_transfinite_curve(-horedges_surfaces[0][i], nzdirection, "Progression", 1/mesh_growthrate)
    m.set_transfinite_curve(horedges_surfaces[-1][i], nzdirection, "Progression", mesh_growthrate)
    #zwischen den slits
    for j in range(1, len(horedges_surfaces)-1):
        m.set_transfinite_curve(horedges_surfaces[j][i], nbetweenslits, "Progression", 1.0)

#Transfinite Curves for vertical edges

for i in range(len(veredges_bottomsurfaces)):
    m.set_transfinite_curve(veredges_bottomsurfaces[i], meshdata[0][0], "Progression", mesh_growthrate)
    m.set_transfinite_curve(veredges_inflationsurfaces[i], meshdata[1][0], "Progression", mesh_growthrate)
    m.set_transfinite_curve(verdeges_topsurfaces[i], nbisoben[0], "Progression", meshgrowthafterinflation)

for i in range(len(bottom_surfaces)):
    m.set_transfinite_surface(bottom_surfaces[i], "Left", [corners_surfaces[i][0], corners_surfaces[i+1][0], corners_surfaces[i+1][1], corners_surfaces[i][1]])
    m.set_transfinite_surface(inflation_surfaces[i], "Left", [corners_surfaces[i][1], corners_surfaces[i+1][1], corners_surfaces[i+1][2], corners_surfaces[i][2]])
    m.set_transfinite_surface(top_surfaces[i], "Left", [corners_surfaces[i][2], corners_surfaces[i+1][2], corners_surfaces[i+1][3], corners_surfaces[i][3]])

m.set_recombined_surfaces([i for i in bottom_surfaces])
m.set_recombined_surfaces([i for i in inflation_surfaces])
m.set_recombined_surfaces([i for i in top_surfaces])

extrusions_bottom = []
extrusions_inflation = []
extrusions_top = []

xnumlayer = xpos_fence / mesh_freesize_xdirection
xnumlayer = math.ceil(xnumlayer)+1

for i in range(len(bottom_surfaces)):
    extrusions_bottom.append(m.extrude(bottom_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))
    extrusions_inflation.append(m.extrude(inflation_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))
    extrusions_top.append(m.extrude(top_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))


all_volumes = []
all_bottom = []
all_back = []
all_front = []
all_top = []
fence_slits = []
fence_letthrough = []

for items in extrusions_bottom:
    all_volumes.append(items[0])
for items in extrusions_inflation:
    all_volumes.append(items[0])
for items in extrusions_top:
    all_volumes.append(items[0])

volume_physical_group = m.add_physical(all_volumes, "Volume_1")





m.synchronize()
geo.generate_mesh(dim=2)
gmsh.write(savespace)
geo.__exit__()





    











