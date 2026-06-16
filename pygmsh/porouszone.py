import pygmsh
import gmsh 
import math
import numpy as np
from utils.meshcalc import inflationcalculation,inflationlayernumber, totalheightcalculation
from utils.jsonutil import json_write,json_read as json_read2D

settings_path = "../config/settings.json"

settings = json_read2D(settings_path)

fenceNumber = settings["number_of_fences"]
fenceHeight = settings["height_of_fences"]
fencexPos = settings["xpos_firstfence"]
fenceNumSlits = settings["number_of_slits"]
fenceThickness = settings["fence_thickness"]
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

savepath_json = savespace[:-4]+".json"
json_write(settings_path, savepath_json)

fence_front = fencexPos - fenceThickness/2
fence_back = fencexPos + fenceThickness/2

if meshGrowthAfterInflation == 1 or meshGrowthAfterInflation == 0:
    meshGrowthAfterInflationCalc = 1.05
    meshdataY, toppointsY, nbisobenY = inflationcalculation(meshFirstLayerHeight, meshGrowthrate, meshInflationLayer, fenceHeight,
                                                            fenceNumSlits, channelHeight, meshGrowthAfterInflationCalc)
else:
    meshdataY, toppointsY, nbisobenY = inflationcalculation(meshFirstLayerHeight, meshGrowthrate, meshInflationLayer, fenceHeight,
                                                            fenceNumSlits, channelHeight, meshGrowthAfterInflation)
meshdataY[:,0] = [int(x[0])+1 for x in meshdataY]
nbisobenY[0] = int(nbisobenY[0])+1
meshNumNextToFenceInflation = math.ceil(inflationlayernumber(meshXDirectionFirstLayerHeight, meshXDirectionGrowthRate, meshFreesize))+1 
#Dont forget: We now have a porous zone. The fence itself has a thickness. So later we need to add the thickness of the fence to the x-Position
Xinflationheight = totalheightcalculation(meshXDirectionFirstLayerHeight, meshXDirectionGrowthRate, meshNumNextToFenceInflation)
meshdataX, toppointsX, nbisobenX = inflationcalculation(meshXDirectionFirstLayerHeight,
                                                        meshXDirectionGrowthRate,
                                                        meshNumNextToFenceInflation,
                                                        Xinflationheight,
                                                        1,
                                                        widthChannel-(fencexPos + fenceThickness/2),
                                                        1.1)
meshdataX[:,0] = [int(x[0])+1 for x in meshdataX]
nbisobenX[0] = int(nbisobenX[0])+1
print(f"Height of last layer at top boundary in Y direction: {nbisobenY[1]}")

if fenceNumSlits > 1:
    dySlits = fenceHeight / fenceNumSlits
    yposSlits = [j*dySlits for j in range(1, fenceNumSlits+1)]
else:
    yposSlits = [fenceHeight]

points = np.empty((6,fenceNumSlits+3), dtype = object)
horizontal_lines = np.empty((3,5), dtype = object)
vertical_lines = np.empty((6,fenceNumSlits+2), dtype = object)
plane_loops = np.empty((2,5), dtype = object)
plane_surfaces = np.empty((2,5), dtype = object)


nFenceMesh = math.ceil(fenceThickness/meshXDirectionFirstLayerHeight)+1
nFreeMesh = math.ceil((fencexPos + fenceThickness/2 - Xinflationheight)/meshFreesize)+1

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

x_Positions = [0.0, fence_front-Xinflationheight, fence_front, fence_back, fence_back+Xinflationheight, widthChannel]

for i in range(6):
    for j in range(fenceNumSlits+3):
        if j == 0:
            points[i][j] = m.add_point((x_Positions[i], 0.0, 0.0))
        elif j == fenceNumSlits+1:
            points[i][j] = m.add_point((x_Positions[i], toppointsY, 0.0))
        elif j == fenceNumSlits+2:
            points[i][j] = m.add_point((x_Positions[i], channelHeight, 0.0))
        else:
            points[i][j] = m.add_point((x_Positions[i], yposSlits[j-1], 0.0))

for i in range(5):
    horizontal_lines[0][i] = m.add_line(points[i][0], points[i+1][0])
    horizontal_lines[1][i] = m.add_line(points[i][fenceNumSlits], points[i+1][fenceNumSlits])
    horizontal_lines[2][i] = m.add_line(points[i][fenceNumSlits+2], points[i+1][fenceNumSlits+2])

for i in range(6):
    for j in range(fenceNumSlits+2):
        vertical_lines[i][j] = m.add_line(points[i][j], points[i][j+1])

for i in range(5):
    plane_loops[0][i] = m.add_curve_loop([horizontal_lines[0][i]] + list(vertical_lines[i+1][0:fenceNumSlits]) + 
                                    [-horizontal_lines[1][i]] + [-l for l in reversed(vertical_lines[i][0:fenceNumSlits])])
    plane_surfaces[0][i] = m.add_plane_surface(plane_loops[0][i])


for i in range(5):
    plane_loops[1][i] = m.add_curve_loop([horizontal_lines[1][i]] + list(vertical_lines[i+1][fenceNumSlits:fenceNumSlits+2])+
                                         [-horizontal_lines[2][i]] + 
                                         [-l for l in reversed(vertical_lines[i][fenceNumSlits:fenceNumSlits+2])])
    plane_surfaces[1][i] = m.add_plane_surface(plane_loops[1][i])

for i in range(3):
    m.set_transfinite_curve(horizontal_lines[i][0], nFreeMesh, "Progression", 1.0)
    m.set_transfinite_curve(horizontal_lines[i][-1], nFreeMesh, "Progression", 1.0)
    m.set_transfinite_curve(horizontal_lines[i][1], meshdataX[0][0], "Progression", 1/meshXDirectionGrowthRate)
    m.set_transfinite_curve(horizontal_lines[i][-2], meshdataX[0][0], "Progression", meshXDirectionGrowthRate)
    m.set_transfinite_curve(horizontal_lines[i][2], nFenceMesh, "Progression", 1.0)

for i in range(6):
    if meshGrowthAfterInflation == 1 or meshGrowthAfterInflation == 0:
        nFreeMeshOben = math.ceil((channelHeight-toppointsY)/meshFreesize)+1
        m.set_transfinite_curve(vertical_lines[i][-1], nFreeMeshOben, "Progression", 1.0)
    else:
        m.set_transfinite_curve(vertical_lines[i][-1], nbisobenY[0], "Progression", meshGrowthAfterInflation)
    for j in range(len(vertical_lines[0])-1):
        m.set_transfinite_curve(vertical_lines[i][j], meshdataY[j][0], "Progression", meshGrowthrate)

for i in range(5):
    m.set_transfinite_surface(plane_surfaces[0][i], "Left", [points[i][0], points[i+1][0], 
                                                             points[i+1][fenceNumSlits], points[i][fenceNumSlits]])
    m.set_transfinite_surface(plane_surfaces[1][i], "Left", [points[i][fenceNumSlits], points[i+1][fenceNumSlits], 
                                                             points[i+1][fenceNumSlits+2], points[i][fenceNumSlits+2]])

m.synchronize()
m.set_recombined_surfaces(plane_surfaces.flatten().tolist())
m.synchronize()

m.add_physical(plane_surfaces[0][2], "Fence")
m.add_physical(list(plane_surfaces[0][0:2])+list(plane_surfaces[0][3:])+list(plane_surfaces[1]), "Fluid")
m.add_physical(list(vertical_lines[0]), "Inlet")
m.add_physical(list(vertical_lines[-1]),"Outlet")
m.add_physical(list(horizontal_lines[0]), "Bottom")
m.add_physical(list(horizontal_lines[2]), "Top")
geo.generate_mesh(dim=2)
gmsh.option.setNumber("Geometry.Tolerance", 1e-8)  
gmsh.model.mesh.removeDuplicateNodes()
gmsh.write(savespace)



