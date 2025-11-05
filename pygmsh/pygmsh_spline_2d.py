import pygmsh
import gmsh
import math
import numpy as np
from utils.meshcalc import inflationcalculation
from utils.json import json_read
from utils.splineread import read_height_file
from utils.newton import point_on_curve


settings_path = "../config/settings.json"

settings = json_read(settings_path)
splie_data_path = "../config/height.dat"

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

spline_data = read_height_file(splie_data_path)
if spline_data[0] != [0,0,0]:
    spline_data = spline_data[1:]
    spline_data.insert(0, [0,0,0])
if spline_data[-1][0] < lChannel:
    spline_data.append([lChannel,0,0])

meshdata, toppoints, nbisoben = inflationcalculation(meshFirstlayerheight, meshGrowthrate, meshNumberofinflationlayers, hFences, nSlits, hChannel, meshgrowthafterinflation)
meshdata[:,0] = [int(x[0]) + 1 for x in meshdata]
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

plane_corner = np.empty((nFences+2,3), dtype = object)
fences_slitpos = np.empty((nFences+2,nSlits), dtype = object)
vertical_lines = np.empty((nFences+2,nSlits+2), dtype = object)
horizontal_lines = np.empty((2,nFences+1), dtype = object)
plane_loops = np.empty((nFences+1), dtype = object)
plane_surfaces = np.empty((nFences+1), dtype= object)
mesh_inflation = np.empty((nFences+1), dtype = object)

nFreebeforfirstfence = math.ceil(xfirstfence/meshFreesize)+1 
nBetweenfences = math.ceil(dxFences/meshFreesize)+1
nAbovefences = math.ceil((hChannel-toppoints)/meshFreesize)+1

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

spline_points = np.empty((len(spline_data)), dtype=object)


#create spline for the bottom boundary to later determine corners for the surfaces from the spline
for i in range(len(spline_data)):
    spline_points[i] = m.add_point((spline_data[i][0], spline_data[i][1], spline_data[i][2]))
spline_curve = m.add_spline(spline_points)
m.synchronize()
spline_id = gmsh.model.getEntities(1)[-1][1]
#Create points for the corners of the planes

#Inlet points

plane_corner[0][0] = m.add_point((spline_data[0][0],0.0,0.0)) # (0,0)
plane_corner[0][1] = m.add_point((spline_data[0][0], toppoints, 0.0))
plane_corner[0][2] = m.add_point((spline_data[0][0], hChannel, 0.0))
#Points at fences
fence_bottompoints = np.empty((nFences), dtype=object)
for i in range(1,nFences+1):
    x_target = xposFences[i-1]
    point_on_spline = point_on_curve(spline_id, x_target, start=0.5) # (x-position of fence, y-position from spline)
    fence_bottompoints[i-1] = point_on_spline[1]
    plane_corner[i][0] = m.add_point((point_on_spline[0], point_on_spline[1], point_on_spline[2]))
    plane_corner[i][1] = m.add_point((point_on_spline[0], point_on_spline[1]+toppoints, 0.0)) #watch for addition of the height of the current bottom
    plane_corner[i][2] = m.add_point((point_on_spline[0], hChannel, 0.0))

#Points at outlet
if spline_data[-1][0] != lChannel:
    plane_corner[nFences+1][0] = m.add_point((lChannel,0.0,0.0)) # (lChannel,0)
    plane_corner[nFences+1][1] = m.add_point((lChannel,toppoints,0.0)) # (lChannel,endofinflation)
    plane_corner[nFences+1][2] = m.add_point((lChannel,hChannel,0.0)) # (lChannel,hChannel)
else:
    plane_corner[nFences+1][0] = spline_points[-1]
    plane_corner[nFences+1][1] = m.add_point((spline_data[-1][0], toppoints, 0.0))
    plane_corner[nFences+1][2] = m.add_point((spline_data[-1][0], hChannel, 0.0))

print(fence_bottompoints)

#create points for the slits of the fences:


m.synchronize()
geo.generate_mesh(dim=2)
gmsh.write(savespace)
geo.__exit__()






