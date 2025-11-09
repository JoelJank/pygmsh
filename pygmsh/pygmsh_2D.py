import pygmsh
import gmsh
import math
import numpy as np
from utils.meshcalc import inflationcalculation
from utils.json import json_read2D

settings_path = "../config/settings.json"
    
settings = json_read2D(settings_path)

nFences =  settings["nFences"]
hFences = settings["hFences"]
dxFences = settings["dxFences"]
nSlits = settings["nSlits"]
hChannel = settings["hChannel"]
lChannel = settings["lChannel"]
xfirstfence = settings["xfirstfence"]
resolution = settings["resolution"]
meshFreesize = settings["meshFreesize"]
meshFirstlayerheight = settings["meshFirstlayerheight"]
meshGrowthrate = settings["meshGrowthrate"]
meshNumberofinflationlayers = settings["meshNumberofinflationlayers"]
meshgrowthafterinflation = settings["meshgrowthafterinflation"]
savespace = settings["savespace"]


neededwidth = 2* xfirstfence + (nFences-1)*dxFences # make safe that all fences fit in channel and that inlet is the same width as outlet
if lChannel < neededwidth:
    lChannel = neededwidth

meshdata, toppoints, nbisoben = inflationcalculation(meshFirstlayerheight, meshGrowthrate, meshNumberofinflationlayers, hFences, nSlits, hChannel, meshgrowthafterinflation)
meshdata[:,0] = [int(x[0]) + 1 for x in meshdata]
nbisoben[0] = int(nbisoben[0]) + 1
print(f"Height of last layer at top boundary: {nbisoben[1]}")
#Calculations:

#xpositions of fences:
xposFences = [xfirstfence + i*dxFences for i in range(nFences)]

#ypositions of slits in fences:
if nSlits > 1:
    dySlits = hFences/nSlits
    yposSlits = [j*dySlits for j in range(1,nSlits+1)]
else:
    yposSlits = [hFences]

#empty arrays for the points, lines, loops and surfaces
plane_corner = np.empty((nFences+2,3), dtype = object)
fences_slitpos = np.empty((nFences+2,nSlits), dtype = object)
vertical_lines = np.empty((nFences+2,nSlits+2), dtype = object)
horizontal_lines = np.empty((2,nFences+1), dtype = object)
plane_loops = np.empty((nFences+1), dtype = object)
plane_surfaces = np.empty((nFences+1), dtype= object)
mesh_inflation = np.empty((nFences+1), dtype = object)


#calculations for meshing

nFreebeforfirstfence = math.ceil(xfirstfence/meshFreesize)+1 
nBetweenfences = math.ceil(dxFences/meshFreesize)+1
nAbovefences = math.ceil((hChannel-toppoints)/meshFreesize)+1

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

#Create points for the corners of the planes
plane_corner[0][0] = m.add_point((0.0,0.0,0.0), mesh_size=resolution) # (0,0)
plane_corner[0][1] = m.add_point((0.0, toppoints,0.0), mesh_size=resolution) # (0,endofinflation)
plane_corner[0][2] = m.add_point((0.0,hChannel,0.0), mesh_size=resolution) # (0,hChannel)

for i in range(1,nFences+1):
    plane_corner[i][0] = m.add_point((xposFences[i-1],0.0,0.0), mesh_size=resolution) # (xpos of fences, 0)
    plane_corner[i][1] = m.add_point((xposFences[i-1], toppoints,0.0), mesh_size=resolution) # (0,endofinflation)
    plane_corner[i][2] = m.add_point((xposFences[i-1],hChannel,0.0), mesh_size=resolution) # (xpos of fences, hChannel)

plane_corner[nFences+1][0] = m.add_point((lChannel,0.0,0.0), mesh_size=resolution) # (lChannel,0)
plane_corner[nFences+1][1] = m.add_point((lChannel,toppoints,0.0), mesh_size=resolution) # (lChannel,endofinflation)
plane_corner[nFences+1][2] = m.add_point((lChannel,hChannel,0.0), mesh_size=resolution) # (lChannel,hChannel)


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
    vertical_lines[i][-2] = m.add_line(fences_slitpos[i][-1],plane_corner[i][1]) #linie bis end of inflation
    vertical_lines[i][-1] = m.add_line(plane_corner[i][1],plane_corner[i][2])  #linie bis top of channel von end of inflation
    
    
    # Die ersten n slits sind die Linien zwischen den slits, der letzte eintrage ist das fence top


#create horizontal lines for the channel at top and bottom + create channel plane loops + create surfaces
for i in range(nFences+1):
    horizontal_lines[0][i] = m.add_line(plane_corner[i][0], plane_corner[i+1][0])  # bottom line
    horizontal_lines[1][i] = m.add_line(plane_corner[i+1][2], plane_corner[i][2])  # top line
    plane_loops[i] = m.add_curve_loop(
        [horizontal_lines[0][i]] +
        list(vertical_lines[i+1]) +
        [horizontal_lines[1][i]] +
        [ -l for l in reversed(vertical_lines[i]) ]
    )
    plane_surfaces[i] = m.add_plane_surface(plane_loops[i])


#Meshing
#For curves at the start and end of the channel:
m.set_transfinite_curve(horizontal_lines[0][0], nFreebeforfirstfence, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[0][-1], nFreebeforfirstfence, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[1][0], nFreebeforfirstfence, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[1][-1], nFreebeforfirstfence,"Progression", 1.0)

#Curves between the fences:
for i in range(1,nFences):
    m.set_transfinite_curve(horizontal_lines[0][i], nBetweenfences,"Progression", 1.0)
    m.set_transfinite_curve(horizontal_lines[1][i], nBetweenfences,"Progression", 1.0)

#For curves above the fences + for the curves of the fences

for i in range(len(vertical_lines)):
    m.set_transfinite_curve(vertical_lines[i][-1], nbisoben[0],"Progression", meshgrowthafterinflation)
    for j in range(len(vertical_lines[i])-1):
        m.set_transfinite_curve(vertical_lines[i][j],meshdata[j][0],"Progression", meshGrowthrate) 
    

for i in range (len(plane_surfaces)):
    m.set_transfinite_surface(plane_surfaces[i],"Left", [plane_corner[i][0], plane_corner[i+1][0], plane_corner[i+1][2], plane_corner[i][2]])


m.set_recombined_surfaces([i for i in plane_surfaces])


m.synchronize()

# add physical groups
m.add_physical(plane_surfaces.tolist(), "Channel")
m.add_physical(list(vertical_lines[0]), "Inlet")
m.add_physical(list(vertical_lines[-1]), "Outlet")
m.add_physical(list(horizontal_lines[0]), "Bottom")
m.add_physical(list(horizontal_lines[1]), "Top")
for i in range(1,nFences+1):
    m.add_physical(vertical_lines[i][-1], f"FenceTop{i}")
    for j in range(len(vertical_lines[i])-1):
        m.add_physical(vertical_lines[i][j], f"z{i}s{j+1}")

geo.generate_mesh(dim=3)
gmsh.write(savespace)
geo.__exit__()

