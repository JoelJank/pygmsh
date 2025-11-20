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

extrusions_bottom_before = []
extrusions_inflation_before = []
extrusions_top_before = []
extrusions_bottom_after = []
extrusions_inflation_after = []
extrusions_top_after = []

xnumlayer = math.ceil(xpos_fence / mesh_freesize_xdirection)

top_surf = []
bottom_surf = []
volumes_before = []
front_surf = []
back_surf = []
fence_1 = [] #abwechselende Latten -> Hier verfeinern um auch andere porosities zu bekommen
fence_2 = [] # abwechselande Latten
middle_interior_bottom = []
middle_interior_inflation = []
middle_interior_top = []
volumes_after = []
outlets = []

for i in range(len(bottom_surfaces)):
    extrusions_bottom_before.append(m.extrude(bottom_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))
    bottom_surf.append(extrusions_bottom_before[i][2][0])
    extrusions_inflation_before.append(m.extrude(inflation_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))
    extrusions_top_before.append(m.extrude(top_surfaces[i], translation_axis = [xpos_fence, 0, 0], num_layers = xnumlayer, recombine = True))
    top_surf.append(extrusions_top_before[i][2][2])
    volumes_before.append(extrusions_bottom_before[i][1])
    volumes_before.append(extrusions_inflation_before[i][1])
    volumes_before.append(extrusions_top_before[i][1])
    
front_surf.append(extrusions_bottom_before[0][2][3])
front_surf.append(extrusions_inflation_before[0][2][3])
front_surf.append(extrusions_top_before[0][2][3])

back_surf.append(extrusions_bottom_before[-1][2][1])
back_surf.append(extrusions_inflation_before[-1][2][1])
back_surf.append(extrusions_top_before[-1][2][1])

middle_interior_bottom.append(extrusions_bottom_before[0][0])
middle_interior_bottom.append(extrusions_bottom_before[-1][0])

for i in range(1, len(bottom_surfaces)-1):
    if i % 2 == 1:
        fence_1.append(extrusions_bottom_before[i][0])
    else:
        fence_2.append(extrusions_bottom_before[i][0])
        

for i in range(len(extrusions_inflation_before)):
    middle_interior_inflation.append(extrusions_inflation_before[i][0])
    middle_interior_top.append(extrusions_top_before[i][0])

#ALL surfaces in lists up until the fence
#after fence
x_afterfence = length_channel - xpos_fence
xnumlayer_after = math.ceil(x_afterfence / mesh_freesize_xdirection)
extrusions_bottom_after.append(m.extrude(middle_interior_bottom[0], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))

for i in range(len(fence_1)): #VORSICHTIG: GEHT NUR WENN DIM(FNACE_1) == DIM(FENCE_2) 
    extrusions_bottom_after.append(m.extrude(fence_1[i], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))
    extrusions_bottom_after.append(m.extrude(fence_2[i], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))

extrusions_bottom_after.append(m.extrude(middle_interior_bottom[1], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))
for item in extrusions_bottom_after:
    bottom_surf.append(item[2][1])
    volumes_after.append(item[1])
    outlets.append(item[0])


for i in range(len(middle_interior_inflation)):
    extrusions_inflation_after.append(m.extrude(middle_interior_inflation[i], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))
    extrusions_top_after.append(m.extrude(middle_interior_top[i], translation_axis = [x_afterfence, 0, 0], num_layers = xnumlayer_after, recombine = True))
    top_surf.append(extrusions_top_after[i][2][2])
    outlets.append(extrusions_inflation_after[i][0])
    outlets.append(extrusions_top_after[i][0])
    volumes_after.append(extrusions_inflation_after[i][1])
    volumes_after.append(extrusions_top_after[i][1])

#All surfaces extruded after fence
front_surf.append(extrusions_bottom_after[0][2][3])
front_surf.append(extrusions_inflation_after[0][2][3])
front_surf.append(extrusions_top_after[0][2][3])
back_surf.append(extrusions_bottom_after[-1][2][1])
back_surf.append(extrusions_inflation_after[-1][2][1])
back_surf.append(extrusions_top_after[-1][2][1])




m.add_physical(list(bottom_surfaces)+list(inflation_surfaces)+list(top_surfaces), "Inlet")
m.add_physical(fence_1, "Fences_Parts1")
m.add_physical(fence_2, "Fences_Parts2")
m.add_physical(middle_interior_bottom+middle_interior_inflation+middle_interior_top, "Interior_Parts")
m.add_physical(outlets, "Outlets")
m.add_physical(bottom_surf, "Bottom_Surfaces")
m.add_physical(top_surf, "Top_Surfaces")
m.add_physical(front_surf, "Front_Surfaces")
m.add_physical(back_surf, "Back_Surfaces")
m.add_physical(volumes_before, "Volume 1")
m.add_physical(volumes_after, "Volume 2")







m.synchronize()
geo.generate_mesh(dim=3)
gmsh.write(savespace)
geo.__exit__()





    











