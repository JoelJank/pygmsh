import pygmsh
import gmsh 
import math
import numpy as np
from utils.meshcalc import inflationcalculation,inflationlayernumber, totalheightcalculation
from utils.jsonutil import json_write,json_read as json_read2D

#this is directly taken from onefencepygmsh_2D.py


settings_path = "../config/settings.json"

settings = json_read2D(settings_path)

fenceNumber = settings["number_of_fences"]
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
extrusion_height = settings["extrusion_height"]
num_layers_z = settings["num_layers_extrusion"]

savespace = settings["savespace"]

savepath_json = savespace[:-4]+".json"
json_write(settings_path, savepath_json)



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

print(toppointsY)
geo = pygmsh.geo.Geometry()
m = geo.__enter__()

plane_corner[0][0] = m.add_point((0.0, 0.0, 0.0))
plane_corner[0][1] = m.add_point((0.0, toppointsY, 0.0))
plane_corner[0][2] = m.add_point((0.0, channelHeight, 0.0))

if fenceNumber == 0:
    plane_corner[1][0] = m.add_point((fencexPos-meshFreesize, 0.0, 0.0))
    plane_corner[1][1] = m.add_point((fencexPos-meshFreesize, toppointsY, 0.0))
    plane_corner[1][2] = m.add_point((fencexPos-meshFreesize, channelHeight, 0.0))
else:
    plane_corner[1][0] = m.add_point((fencexPos-Xinflationheight, 0.0, 0.0))
    plane_corner[1][1] = m.add_point((fencexPos-Xinflationheight, toppointsY, 0.0))
    plane_corner[1][2] = m.add_point((fencexPos-Xinflationheight, channelHeight, 0.0))  

plane_corner[2][0] = m.add_point((fencexPos, 0.0, 0.0))
plane_corner[2][1] = m.add_point((fencexPos, toppointsY, 0.0))
plane_corner[2][2] = m.add_point((fencexPos, channelHeight, 0.0))

if fenceNumber == 0:
    plane_corner[3][0] = m.add_point((fencexPos+meshFreesize, 0.0, 0.0))
    plane_corner[3][1] = m.add_point((fencexPos+meshFreesize, toppointsY, 0.0))
    plane_corner[3][2] = m.add_point((fencexPos+meshFreesize, channelHeight, 0.0))
else:
    plane_corner[3][0] = m.add_point((fencexPos+Xinflationheight, 0.0, 0.0))
    plane_corner[3][1] = m.add_point((fencexPos+Xinflationheight, toppointsY, 0.0))
    plane_corner[3][2] = m.add_point((fencexPos+Xinflationheight, channelHeight, 0.0))


plane_corner[4][0] = m.add_point((widthChannel, 0.0, 0.0))
plane_corner[4][1] = m.add_point((widthChannel, toppointsY, 0.0))
plane_corner[4][2] = m.add_point((widthChannel, channelHeight, 0.0))

for i in range(fenceNumSlits):
    fences_slitpos[0][i] = m.add_point((0.0, yposSlits[i], 0.0))
    if fenceNumber == 0:
        fences_slitpos[1][i] = m.add_point((fencexPos-meshFreesize, yposSlits[i], 0.0))
        fences_slitpos[3][i] = m.add_point((fencexPos+meshFreesize, yposSlits[i], 0.0))
    else:
        fences_slitpos[1][i] = m.add_point((fencexPos-Xinflationheight, yposSlits[i], 0.0))
        fences_slitpos[3][i] = m.add_point((fencexPos+Xinflationheight, yposSlits[i], 0.0))
    fences_slitpos[2][i] = m.add_point((fencexPos, yposSlits[i], 0.0))
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

if fenceNumber == 0:
    m.set_transfinite_curve(horizontal_lines[0][1], 1, "Progression", 1.0)
    m.set_transfinite_curve(horizontal_lines[1][1], 1, "Progression", 1.0)

    m.set_transfinite_curve(horizontal_lines[0][2], 1, "Progression", 1.0)
    m.set_transfinite_curve(horizontal_lines[1][2], 1, "Progression", 1.0)
else:

    m.set_transfinite_curve(horizontal_lines[0][1], meshdataX[0][0], "Progression", 1/meshXDirectionGrowthRate)
    m.set_transfinite_curve(horizontal_lines[1][1], meshdataX[0][0], "Progression", meshXDirectionGrowthRate)

    m.set_transfinite_curve(horizontal_lines[0][2], meshdataX[0][0], "Progression", meshXDirectionGrowthRate)
    m.set_transfinite_curve(horizontal_lines[1][2], meshdataX[0][0], "Progression", 1/meshXDirectionGrowthRate)


for i in range(len(vertical_lines)):
    m.set_transfinite_curve(vertical_lines[i][-1], nbisobenY[0], "Progression", meshGrowthAfterInflation)
    for j in range(len(vertical_lines[0])-1):
        m.set_transfinite_curve(vertical_lines[i][j], meshdataY[j][0], "Progression", meshGrowthrate)

for i in range(len(plane_surfaces)):
    m.set_transfinite_surface(plane_surfaces[i],"Left", [plane_corner[i][0], plane_corner[i+1][0], plane_corner[i+1][2], plane_corner[i][2]])

m.synchronize()

m.set_recombined_surfaces([i for i in plane_surfaces])


m.synchronize()

extruded_volumes = []

for surface in plane_surfaces:
    extruded = m.extrude(surface, translation_axis = (0,0, extrusion_height), num_layers = num_layers_z, recombine = True)
    extruded_volumes.append(extruded)
m.synchronize()


volume_channel = []
surface_front = []
surface_top = []
surface_bottom = []

surface_inlet = extruded_volumes[0][2][5:8]
surface_outlet = extruded_volumes[-1][2][1:4]
surface_fence = [extruded_volumes[1][2][1]]
surface_fencetop = extruded_volumes[1][2][2:4]

for i in range(len(extruded_volumes)):
    volume_channel.append(extruded_volumes[i][1])
    surface_front.append(extruded_volumes[i][0])
    surface_top.append(extruded_volumes[i][2][4])
    surface_bottom.append(extruded_volumes[i][2][0])

surface_back_flatten = plane_surfaces.flatten().tolist()
m.add_physical(volume_channel, "channel")
m.add_physical(surface_back_flatten, "back")
m.add_physical(surface_front, "front")
m.add_physical(surface_top, "top")
m.add_physical(surface_bottom, "bottom")
m.add_physical(surface_inlet, "inlet")
m.add_physical(surface_outlet, "outlet")
m.add_physical(surface_fence, "fence")
m.add_physical(surface_fencetop, "fencetop")

geo.generate_mesh(dim=3)
gmsh.option.setNumber("Geometry.Tolerance", 1e-8)  
gmsh.model.mesh.removeDuplicateNodes()
m.synchronize()

gmsh.write(savespace)
geo.__exit__()



        