import os
from pathlib import Path
import gmsh
import math
import numpy as np
from utils.json import json_read, save_json_to_savespace
import utils.meshcalc as meshcalc
import utils.extrude as extrude

#TODO: Maybe add option to have multiple regions in fence also in y-direction

jsonPath = os.path.join(Path(__file__).resolve().parents[1], "config/3D/")
save_json_to_savespace(jsonPath)

jsonGeneral = json_read(os.path.join(jsonPath,"general.json"))
jsonGeom = json_read(os.path.join(jsonPath, "geom.json"))
jsonMesh = json_read(os.path.join(jsonPath, "mesh.json"))

casename = jsonGeneral["casename"]
description = jsonGeneral["description"]
savespace = jsonGeneral["savespace"]

channelLength = jsonGeom["channelLength"]
channelHeight = jsonGeom["channelHeight"]
channelDepthNextToFence = jsonGeom["channelDepthNextToFence"]
fenceHeight = jsonGeom["fenceHeight"]
fenceDepth = jsonGeom["fenceDepth"]
fenceFirstPos = jsonGeom["fenceFirstPos"]
fenceNum = jsonGeom["fenceNum"]
fenceSpacing = jsonGeom["fenceSpacing"]
slitsWidth = jsonGeom["slitsWidth"]

meshXFreesize = jsonMesh["meshXFreesize"]
meshXSpacingSize = jsonMesh["meshXSpacingSize"]
meshNumSlits = jsonMesh["meshNumSlits"]
inflationFirstLayerHeight = jsonMesh["inflationFirstLayerHeight"]
inflationNumLayers = jsonMesh["inflationNumLayers"]
inflationGrowthrate = jsonMesh["inflationGrowthrate"]
meshGrowthrateAfterInflation = jsonMesh["meshGrowthrateAfterInflation"]
meshGrowthrateZDirection = jsonMesh["meshGrowthrateZDirection"]
meshFenceFirstLayerHeight = jsonMesh["firstlayerheightfence"]
meshGrowthrateXDirection = jsonMesh["meshGrowthrateXDirection"]
meshResolution = 1

meshdata, toppoints, meshNumLayersTopInflation = meshcalc.inflationcalculation(inflationFirstLayerHeight, 
                                                                               inflationGrowthrate, 
                                                                               inflationNumLayers,
                                                                               fenceHeight,
                                                                               1,
                                                                               channelHeight,
                                                                               meshGrowthrateAfterInflation)

meshdata[:,0] = [int(x[0])+1 for x in meshdata]
meshNumLayersTopInflation[0] = int(meshNumLayersTopInflation[0])+1 
pyFenceCornersZDir = [channelDepthNextToFence,
                      channelDepthNextToFence + fenceDepth]
if slitsWidth == 0:
    pyFenceSlitsZPos = np.linspace(pyFenceCornersZDir[0], pyFenceCornersZDir[1], 2)
else:
    nSlits = np.round(fenceDepth / slitsWidth)
    pyFenceSlitsZPos = np.linspace(pyFenceCornersZDir[0], pyFenceCornersZDir[1], int(nSlits)+1) 

gmshPoints = np.empty((len(pyFenceSlitsZPos)+2,4), dtype = object)

gmsh.initialize()
gmsh.model.add(casename)
gmshm = gmsh.model

gmshPoints[0][0] = gmshm.occ.addPoint(0.0, 0.0, 0.0, meshResolution)
gmshPoints[0][1] = gmshm.occ.addPoint(0.0, fenceHeight, 0.0, meshResolution)
gmshPoints[0][2] = gmshm.occ.addPoint(0.0, toppoints, 0.0, meshResolution)
gmshPoints[0][3] = gmshm.occ.addPoint(0.0, channelHeight, 0.0, meshResolution)

for i in range(1, len(pyFenceSlitsZPos)+1):
    j= i - 1
    gmshPoints[i][0] = gmshm.occ.addPoint(0.0, 0.0, pyFenceSlitsZPos[j], meshResolution)
    gmshPoints[i][1] = gmshm.occ.addPoint(0.0, fenceHeight, pyFenceSlitsZPos[j], meshResolution)
    gmshPoints[i][2] = gmshm.occ.addPoint(0.0, toppoints, pyFenceSlitsZPos[j], meshResolution)
    gmshPoints[i][3] = gmshm.occ.addPoint(0.0, channelHeight, pyFenceSlitsZPos[j], meshResolution)

gmshPoints[-1][0] = gmshm.occ.addPoint(0.0, 0.0, pyFenceSlitsZPos[-1] + channelDepthNextToFence, meshResolution)
gmshPoints[-1][1] = gmshm.occ.addPoint(0.0, fenceHeight, pyFenceSlitsZPos[-1] + channelDepthNextToFence, meshResolution)
gmshPoints[-1][2] = gmshm.occ.addPoint(0.0, toppoints, pyFenceSlitsZPos[-1] + channelDepthNextToFence, meshResolution)
gmshPoints[-1][3] = gmshm.occ.addPoint(0.0, channelHeight, pyFenceSlitsZPos[-1] + channelDepthNextToFence, meshResolution)

print(f"Fence Surfaces: {len(pyFenceSlitsZPos)-1}, Total Points: {len(gmshPoints)}") #TODO: Write this into an description output file

gmshHorLines = np.empty((len(gmshPoints)-1, 4), dtype = object)
gmshVerLines = np.empty((len(gmshPoints), 3), dtype = object)

for i in range(len(gmshHorLines)):
    gmshHorLines[i][0] = gmshm.occ.addLine(gmshPoints[i][0], gmshPoints[i+1][0])
    gmshHorLines[i][1] = gmshm.occ.addLine(gmshPoints[i][1], gmshPoints[i+1][1])
    gmshHorLines[i][2] = gmshm.occ.addLine(gmshPoints[i][2], gmshPoints[i+1][2])
    gmshHorLines[i][3] = gmshm.occ.addLine(gmshPoints[i][3], gmshPoints[i+1][3])

for i in range(len(gmshVerLines)):
    gmshVerLines[i][0] = gmshm.occ.addLine(gmshPoints[i][0], gmshPoints[i][1])
    gmshVerLines[i][1] = gmshm.occ.addLine(gmshPoints[i][1], gmshPoints[i][2])
    gmshVerLines[i][2] = gmshm.occ.addLine(gmshPoints[i][2], gmshPoints[i][3])

allCurveLoops = np.empty((3, len(gmshHorLines)), dtype = object) # allCurveLoops[0] = up to fenceHeight, allCurveLoops[1] = fenceHeight to toppoints, allCurveLoops[2] = toppoints to channelHeight
allSurfaces = np.empty((3, len(gmshHorLines)), dtype = object)

for i in range(len(gmshHorLines)):
    allCurveLoops[0][i] = gmshm.occ.addCurveLoop(
        [gmshHorLines[i][0]]+
        [gmshVerLines[i+1][0]]+
        [-gmshHorLines[i][1]]+
        [-gmshVerLines[i][0]]
    )
    allCurveLoops[1][i] = gmshm.occ.addCurveLoop(
        [gmshHorLines[i][1]]+
        [gmshVerLines[i+1][1]]+
        [-gmshHorLines[i][2]]+
        [-gmshVerLines[i][1]]
    )
    allCurveLoops[2][i] = gmshm.occ.addCurveLoop(
        [gmshHorLines[i][2]]+
        [gmshVerLines[i+1][2]]+
        [-gmshHorLines[i][3]]+
        [-gmshVerLines[i][2]]
    )
    allSurfaces[0][i] = gmshm.occ.addPlaneSurface([allCurveLoops[0][i]])
    allSurfaces[1][i] = gmshm.occ.addPlaneSurface([allCurveLoops[1][i]])
    allSurfaces[2][i] = gmshm.occ.addPlaneSurface([allCurveLoops[2][i]])
gmshm.occ.synchronize()
#Transfinite Mesh
#Horizontal Lines
meshSizeBetweenSlits = round( slitsWidth/ meshNumSlits, 6)
meshNumSlits = meshNumSlits + 1
meshNumNextToFence,_,_ = meshcalc.layercalculations(channelDepthNextToFence, meshGrowthrateZDirection, meshSizeBetweenSlits)
meshNumNextToFence = math.ceil(meshNumNextToFence) + 1
print(f"Number mesh layer in z-Direction: {meshNumNextToFence}, Growthrate z-Direction: {meshGrowthrateZDirection}")
gmshm.occ.synchronize()
for i in range(4):
    gmshm.mesh.setTransfiniteCurve(gmshHorLines[0][i], meshNumNextToFence, "Progression", 1/meshGrowthrateZDirection)
    gmshm.mesh.setTransfiniteCurve(gmshHorLines[-1][i], meshNumNextToFence, "Progression", meshGrowthrateZDirection)

    for j in range(1, len(gmshHorLines)-1):
        gmshm.mesh.setTransfiniteCurve(gmshHorLines[j][i],meshNumSlits, "Progression", 1)

for i in range(len(gmshVerLines)):
    gmshm.mesh.setTransfiniteCurve(gmshVerLines[i][0], meshdata[0][0], "Progression", inflationGrowthrate)
    gmshm.mesh.setTransfiniteCurve(gmshVerLines[i][1], meshdata[1][0], "Progression", inflationGrowthrate)
    gmshm.mesh.setTransfiniteCurve(gmshVerLines[i][2], meshNumLayersTopInflation[0], "Progression", meshGrowthrateAfterInflation)

for i in range(len(allSurfaces[0])):
    gmshm.mesh.setTransfiniteSurface(allSurfaces[0][i], "Left", [gmshPoints[i][0], gmshPoints[i+1][0], gmshPoints[i+1][1], gmshPoints[i][1]])
    gmshm.mesh.setRecombine(2, allSurfaces[0][i])
    gmshm.mesh.setTransfiniteSurface(allSurfaces[1][i], "Left", [gmshPoints[i][1], gmshPoints[i+1][1], gmshPoints[i+1][2], gmshPoints[i][2]])
    gmshm.mesh.setRecombine(2, allSurfaces[1][i])
    gmshm.mesh.setTransfiniteSurface(allSurfaces[2][i], "Left", [gmshPoints[i][2], gmshPoints[i+1][2], gmshPoints[i+1][3], gmshPoints[i][3]])
    gmshm.mesh.setRecombine(2, allSurfaces[2][i])

gmsh.model.occ.synchronize()

if fenceNum != 1: #TODO: MULTIPLE FENCES -> Make growth in x-direction to middle of the spacing between the fences and then reverse growth?
    print("Currently only one fence is supported in this version.") #Define how all extrusions work so that later behind os.sync same logic can be used

else:
    allExtrusions = np.empty((4, 3, len(allSurfaces[0])), dtype = object) #allExtrusions[0] = inflation after fence, allExtrusions[1] = inflation before fence
    _, ehafterFence, totalheight = extrude.extrude_calc(xgrowthrate=meshGrowthrateXDirection, 
                                            meshXFreesize = meshXFreesize, 
                                           firstlayerheight = meshFenceFirstLayerHeight, 
                                           fencespacing = fenceSpacing)
    numAfterXInflation = math.ceil((channelLength/2 - totalheight) / meshXFreesize)+1
    print(f"Anzahl an Layern nach Inflation {numAfterXInflation}")
    volumesAfterFence = []
    volumesBeforeFence = []
    for i in range(len(allSurfaces[0])): 
        for j in range(len(allExtrusions[0])):

            # 1. Inflation in direction of +x and -x with inflation growing from fence surface
            extrupos  = gmshm.occ.extrude([(2, allSurfaces[j][i])],
                                         totalheight, 0, 0,
                                         numElements=ehafterFence[0],
                                         heights=ehafterFence[1],
                                         recombine=True)
            extruneg = gmshm.occ.extrude([(2, allSurfaces[j][i])],
                                         -totalheight, 0, 0,
                                         numElements=ehafterFence[0],
                                         heights=ehafterFence[1],
                                         recombine=True)
           
            allExtrusions[0][j][i] = extrupos
            allExtrusions[1][j][i] = extruneg
            volumesAfterFence.append(extrupos[1][1])
            volumesBeforeFence.append(extruneg[1][1])



    gmshm.occ.synchronize()
    for i in range(len(allSurfaces[0])):
        for j in range(len(allExtrusions[0])):
            # 2. Extrusion in direction of +x and -x to complete the channel length 
            extrupos = gmshm.occ.extrude([allExtrusions[0][j][i][0]],
                                                    channelLength/2 - totalheight, 0, 0,
                                                    numElements = [numAfterXInflation],
                                                    recombine = True)
            extruneg = gmshm.occ.extrude([allExtrusions[1][j][i][0]],
                                                    -channelLength/2 + totalheight, 0,0,
                                                    numElements = [numAfterXInflation],
                                                    recombine = True)
            allExtrusions[2][j][i] = extrupos
            allExtrusions[3][j][i] = extruneg
            volumesAfterFence.append(extrupos[1][1])
            volumesBeforeFence.append(extruneg[1][1])

gmsh.model.occ.synchronize()
allOutlets = [allExtrusions[2][j][i][0][1] for i in range(len(allSurfaces[0])) for j in range(len(allExtrusions[2]))]
allInlets = [allExtrusions[3][j][i][0][1] for i in range(len(allSurfaces[0])) for j in range(len(allExtrusions[3]))]
allFront = [allExtrusions[k][j][0][5][1] for k in range(len(allExtrusions)) for j in range(len(allExtrusions[0]))]
allBack = [allExtrusions[k][j][-1][3][1] for k in range(len(allExtrusions)) for j in range(len(allExtrusions[0]))]
allTop = [allExtrusions[k][-1][j][4][1] for k in range(len(allExtrusions)) for j in range(len(allExtrusions[0][0]))]
allBottom = [allExtrusions[k][0][j][2][1] for k in range(len(allExtrusions)) for j in range(len(allExtrusions[0][0]))]
allFenceSurfaces1 = [allSurfaces[0][i] for i in range(1, len(allSurfaces[0])-1, 2)]
allFenceSurfaces2 = [allSurfaces[0][i] for i in range(2, len(allSurfaces[0]), 2)]
allFenceFlowTroughs = [allSurfaces[0][0]] + [allSurfaces[0][-1]] + [allSurfaces[i][j] for i in range(1, len(allSurfaces)) for j in range(len(allSurfaces[0]))]

# Interior Surfaces automatisch finden
gmsh.model.occ.synchronize()

# Alle Surfaces holen
all_surfaces = gmshm.getEntities(2)

# Boundary Surfaces sammeln
boundary_surfaces = set(allOutlets + allInlets + allFront + allBack + allTop + allBottom + 
                       allFenceSurfaces1 + allFenceSurfaces2 + allFenceFlowTroughs)

# Interior = Alle Surfaces minus Boundary
allInteriorSurfaces = [surf for surf in all_surfaces if surf[1] not in boundary_surfaces]

print(f"Total surfaces: {len(all_surfaces)}, Boundary: {len(boundary_surfaces)}, Interior: {len(allInteriorSurfaces)}")

gmshm.occ.synchronize()

gmshm.addPhysicalGroup(2, allOutlets, tag = -1, name = "Outlet")
gmshm.addPhysicalGroup(2, allInlets, tag = -1, name = "Inlet")
gmshm.addPhysicalGroup(2, allFront, tag = -1, name = "Front")
gmshm.addPhysicalGroup(2, allBack, tag = -1, name = "Back")
gmshm.addPhysicalGroup(2, allTop, tag = -1, name = "Top")
gmshm.addPhysicalGroup(2, allBottom, tag = -1, name = "Bottom")
#gmshm.addPhysicalGroup(2, [s[1] for s in allInteriorSurfaces], tag = -1, name = "Interior")
gmshm.addPhysicalGroup(2, allFenceSurfaces1, tag = -1, name = "Fence1")
gmshm.addPhysicalGroup(2, allFenceSurfaces2, tag = -1, name = "Fence2")
gmshm.addPhysicalGroup(2, allFenceFlowTroughs, tag = -1, name = "FenceFlowTroughs")
gmshm.addPhysicalGroup(3, volumesAfterFence, tag = -1, name = "Volumes_After_Fence")
gmshm.addPhysicalGroup(3, volumesBeforeFence, tag = -1, name = "Volumes_Before_Fence")



gmsh.model.occ.synchronize()
gmsh.option.setNumber("General.Terminal",0)
gmshm.mesh.removeDuplicateNodes()
gmshm.mesh.generate(3)
gmshm.mesh.removeDuplicateNodes()
gmsh.write(os.path.join(savespace, casename + ".msh"))

