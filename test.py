import pygmsh
import meshio
import gmsh
import json
import math
import os
import numpy as np

settings_path = "settings/settings.json"

def layercalcuations(hparts, growthrate, h1):
    nlayer = math.log(1-(hparts*(1-growthrate)/h1))/math.log(growthrate)
    nextlayer = h1 * growthrate**nlayer
    lastlayer = h1 * growthrate**(nlayer-1)
    return nlayer, nextlayer, lastlayer

def totalheightcalculation(h1, growthrate, nlayers):
    totalheight = h1* (1- growthrate**nlayers) / (1 - growthrate)
    return totalheight


def inflationcalculation(h1, growthrate, nlayers, hFence, nparts):
    heightparts = hFence /nparts
    meshdata = np.empty((nparts+1,2), dtype = object)
    totalheight = totalheightcalculation(h1, growthrate, nlayers)
    nFirstlayer, nextlayer, lastlayer = layercalcuations(heightparts, growthrate, h1)
    if h1 > heightparts: #wenn h1 direkt größer als Zaunhöhe ist
        for i in range(0,nparts):
            meshdata[i] = [1, heightparts*(1+i)]
    else: #sonst normale berechnung
        meshdata[0] = [math.ceil(nFirstlayer), lastlayer]
        for i in range(1,nparts):
            if nextlayer > heightparts:
                nextlayer = lastlayer + heightparts
                meshdata[i] = [1, nextlayer]
                lastlayer = nextlayer
            else:
                nlayer, nextlayer, lastlayer = layercalcuations(heightparts, growthrate, nextlayer)
                meshdata[i] = [math.ceil(nlayer), lastlayer]
                
    sumlayers = np.sum(meshdata[:-1,0])
    remaininglayer = nlayers - sumlayers
    toppoints = meshdata[-2][1]
    if remaininglayer > 0:
        heightlastlayer = totalheightcalculation(nextlayer, growthrate, remaininglayer)
        toppoints = heightlastlayer + nparts*heightparts
        meshdata[-1] = [remaininglayer, heightlastlayer + meshdata[-2][1]]
    else:
        meshdata = meshdata[:-1]
        
    return meshdata, toppoints, abs(toppoints - totalheight)


    
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
meshFreesize = settings["mesh_freesize"]
meshFirstlayerheight = settings["mesh_firstlayerheight"]
meshGrowthrate = settings["mesh_growthrate"]
meshNumberofinflationlayers = settings["inflation_layers"]

meshdata, toppoints, diff = inflationcalculation(meshFirstlayerheight, meshGrowthrate, meshNumberofinflationlayers, hFences, nSlits)

print(f"Meshdata for inflation layers: {meshdata} \nTop points: {toppoints} \nDifferenz to calculated inflation height: {diff}")
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
    dySlits = hFences/nSlits
    yposSlits = [j*dySlits for j in range(1,nSlits+1)]
else:
    yposSlits = [hFences]

#empty arrays for the points, lines, loops and surfaces
plane_corner = np.empty((nFences+2,2), dtype = object)
fences_slitpos = np.empty((nFences+2,nSlits), dtype = object)
vertical_lines = np.empty((nFences+2,nSlits+1), dtype = object)
horizontal_lines = np.empty((2,nFences+1), dtype = object)
plane_loops = np.empty((nFences+1), dtype = object)
plane_surfaces = np.empty((nFences+1), dtype= object)
mesh_inflation = np.empty((nFences+1), dtype = object)


#calculations for meshing

nFreebeforfirstfence = math.ceil(xfirstfence/meshFreesize)+1 
nBetweenfences = math.ceil(dxFences/meshFreesize)+1
nAbovefences = math.ceil((hChannel - hFences)/meshFreesize)+1

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


#create horizontal lines for the channel at top and bottom + create channel plane loops + create surfaces
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
    m.set_transfinite_curve(vertical_lines[i][-1], nAbovefences,"Progression", 1.1)
    for j in range(len(vertical_lines[i])-1):
        m.set_transfinite_curve(vertical_lines[i][j],10,"Progression", 1.0) 
    #here: do the adjustments for the boundary layer meshing!
    

for i in range (len(plane_surfaces)):
    m.set_transfinite_surface(plane_surfaces[i],"Left", [plane_corner[i][0], plane_corner[i+1][0], plane_corner[i+1][1], plane_corner[i][1]])


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

geo.generate_mesh(dim=2)
gmsh.write("test3.bdf")
geo.__exit__()

