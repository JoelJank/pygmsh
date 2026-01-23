import pygmsh
import gmsh 
import math
import numpy as np
from utils.meshcalc import inflationcalculation,inflationlayernumber, totalheightcalculation
from utils.json import json_read as json_read2D

settings_path = "../config/settings.json"

settings = json_read2D(settings_path)

fenceHeight = settings["height_of_fences"]
fencexPos = settings["xpos_firstfence"]
fenceNumSlits = settings["number_of_slits"]
channelHeight = settings["height_of_channel"]
widthChannel = settings["width_of_channel"]
meshFreesize = settings["mesh_freesize"]
meshFirstLayerHeight = settings["mesh_firstlayerheight"]
meshInflationLayer = settings["inflation_layers"]
meshGrowthrate = settings["mesh_growthrate"]
meshGrowthAfterInflation = settings["meshgrowtrate_afterinflation"]
meshXDirectionFirstLayerHeight = settings["meshXDirectionFirstLayerHeight"]
meshXDirectionGrowthRate = settings["meshXDirectionGrowthRate"]
savespace = settings["savespace"]



meshdataY, toppointsY, nbisobenY = inflationcalculation(meshFirstLayerHeight, meshGrowthrate, meshInflationLayer, fenceHeight, fenceNumSlits, channelHeight, meshGrowthAfterInflation)
meshdataY[:,0] = [int(x[0])+1 for x in meshdataY]
nbisobenY[0] = int(nbisobenY[0])+1
meshNumNextToFenceInflation = math.ceil(inflationlayernumber(meshXDirectionFirstLayerHeight, meshXDirectionGrowthRate, meshFreesize))+1
Xinflationheight = totalheightcalculation(meshXDirectionFirstLayerHeight, meshXDirectionGrowthRate, meshNumNextToFenceInflation)
meshdataX, toppointsX, nbisobenX = inflationcalculation(meshXDirectionFirstLayerHeight, 
                                                        meshXDirectionGrowthRate,
                                                        meshNumNextToFenceInflation,
                                                        Xinflationheight,
                                                        1,
                                                        widthChannel/2,
                                                        1.1)
meshdataX[:,0] = [int(x[0])+1 for x in meshdataX]
nbisobenX[0] = int(nbisobenX[0])+1
print(f"Height of last layer at top boundary in Y direction: {nbisobenY[1]}")

if fenceNumSlits > 1:
    dySlits = fenceHeight / fenceNumSlits
    yposSlits = [j*dySlits for j in range(1, fenceNumSlits+1)]
else:
    yposSlits = [fenceHeight]

plane_corner = np.empty((5,3), dtype = object)
fences_slitpos = np.empty((5, fenceNumSlits), dtype = object)
vertical_lines = np.empty((5, fenceNumSlits+2), dtype = object)
horizontal_lines = np.empty((2,4), dtype = object)
plane_loops = np.empty((4), dtype = object)
plane_surfaces = np.empty((4), dtype = object)

nFreeMesh = math.ceil((fencexPos-Xinflationheight)/meshFreesize)+1

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

plane_corner[0][0] = m.add_point((0.0, 0.0, 0.0))
plane_corner[0][1] = m.add_point((0.0, toppointsY, 0.0))
plane_corner[0][2] = m.add_point((0.0, channelHeight, 0.0))

plane_corner[1][0] = m.add_point((fencexPos-Xinflationheight, 0.0, 0.0))
plane_corner[1][1] = m.add_point((fencexPos-Xinflationheight, toppointsY, 0.0))
plane_corner[1][2] = m.add_point((fencexPos-Xinflationheight, channelHeight, 0.0))  

plane_corner[2][0] = m.add_point((fencexPos, 0.0, 0.0))
plane_corner[2][1] = m.add_point((fencexPos, toppointsY, 0.0))
plane_corner[2][2] = m.add_point((fencexPos, channelHeight, 0.0))

plane_corner[3][0] = m.add_point((fencexPos+Xinflationheight, 0.0, 0.0))
plane_corner[3][1] = m.add_point((fencexPos+Xinflationheight, toppointsY, 0.0))
plane_corner[3][2] = m.add_point((fencexPos+Xinflationheight, channelHeight, 0.0))


plane_corner[4][0] = m.add_point((widthChannel, 0.0, 0.0))
plane_corner[4][1] = m.add_point((widthChannel, toppointsY, 0.0))
plane_corner[4][2] = m.add_point((widthChannel, channelHeight, 0.0))

for i in range(fenceNumSlits):
    fences_slitpos[0][i] = m.add_point((0.0, yposSlits[i], 0.0))
    fences_slitpos[1][i] = m.add_point((fencexPos-Xinflationheight, yposSlits[i], 0.0))
    fences_slitpos[2][i] = m.add_point((fencexPos, yposSlits[i], 0.0))
    fences_slitpos[3][i] = m.add_point((fencexPos+Xinflationheight, yposSlits[i], 0.0))
    fences_slitpos[4][i] = m.add_point((widthChannel, yposSlits[i], 0.0))


for i in range(5):
    vertical_lines[i][0] = m.add_line(plane_corner[i][0], fences_slitpos[i][0])
    for j in range(fenceNumSlits-1):
        vertical_lines[i][j+1] = m.add_line(fences_slitpos[i][j], fences_slitpos[i][j+1])
    vertical_lines[i][-2] = m.add_line(fences_slitpos[i][-1], plane_corner[i][1])
    vertical_lines[i][-1] = m.add_line(plane_corner[i][1], plane_corner[i][2])

for i in range(4):
    horizontal_lines[0][i] = m.add_line(plane_corner[i][0], plane_corner[i+1][0])
    horizontal_lines[1][i] = m.add_line(plane_corner[i+1][2], plane_corner[i][2])
    plane_loops[i] = m.add_curve_loop(
        [horizontal_lines[0][i]]+
        list(vertical_lines[i+1])+
        [horizontal_lines[1][i]]+
        [-l for l in reversed(vertical_lines[i])]
    )
    plane_surfaces[i] = m.add_plane_surface(plane_loops[i])

m.set_transfinite_curve(horizontal_lines[0][0], nFreeMesh, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[0][-1], nFreeMesh, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[1][0], nFreeMesh, "Progression", 1.0)
m.set_transfinite_curve(horizontal_lines[1][-1], nFreeMesh, "Progression", 1.0)

m.set_transfinite_curve(horizontal_lines[0][1], meshdataX[0][0], "Progression", 1/meshXDirectionGrowthRate)
m.set_transfinite_curve(horizontal_lines[1][1], meshdataX[0][0], "Progression", meshXDirectionGrowthRate)

m.set_transfinite_curve(horizontal_lines[0][2], meshdataX[0][0], "Progression", meshXDirectionGrowthRate)
m.set_transfinite_curve(horizontal_lines[1][2], meshdataX[0][0], "Progression", 1/meshXDirectionGrowthRate)

print(len(vertical_lines[i])-1)
for i in range(len(vertical_lines)):
    m.set_transfinite_curve(vertical_lines[i][-1], nbisobenY[0], "Progression", meshGrowthAfterInflation)
    for j in range(len(vertical_lines[0])-1):
        m.set_transfinite_curve(vertical_lines[i][j], meshdataY[j][0], "Progression", meshGrowthrate)

for i in range(len(plane_surfaces)):
    m.set_transfinite_surface(plane_surfaces[i],"Left", [plane_corner[i][0], plane_corner[i+1][0], plane_corner[i+1][2], plane_corner[i][2]])

m.set_recombined_surfaces([i for i in plane_surfaces])

m.synchronize()

m.add_physical(plane_surfaces.tolist(), "Channel")
m.add_physical(list(vertical_lines[0]), "Inlet")
m.add_physical(list(vertical_lines[-1]), "Outlet")
m.add_physical(list(horizontal_lines[0]), "Bottom")
m.add_physical(list(horizontal_lines[1]), "Top")

m.add_physical(vertical_lines[2][-1], "FenceTop")

even = []
odd = []
for j in range(len(vertical_lines[2])-2):
    if j % 2 == 0:
        even.append(vertical_lines[2][j])
    else:
        odd.append(vertical_lines[2][j])
if len(even) > 0:
    m.add_physical(even, "slits1")
if len(odd) > 0:
    m.add_physical(odd, "slits2")

geo.generate_mesh(dim=3)
gmsh.write(savespace)
geo.__exit__()


        