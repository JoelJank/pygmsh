import pygmsh
import gmsh
import math
import os
import numpy as np
from utils.meshcalc import inflationcalculation
from utils.json import json_read
from utils.splineread import read_height_file
from utils.newton import point_on_curve
from utils.search import search_spline


settings_path = "../config/settings.json"

settings = json_read(settings_path)
spline_data_path = "../config/height.dat"

#FENCES SETTINGS
fencesNum = settings["number_of_fences"]
fencesHeight = settings["height_of_fences"]
fencesDistance = settings["distance_of_fences"]
fencesFirstPosX = settings["xpos_firstfence"]

#CHANNEL
channelHeight = settings["height_of_channel"]
channelWidth = settings["width_of_channel"]

#MESH SETTINGS
meshFreesize = settings["mesh_freesize"]
meshFirstLayerHeight = settings["mesh_firstlayerheight"]
meshGrowthrate = settings["mesh_growthrate"]
meshNumLayers = settings["inflation_layers"]
meshResolution = settings["mesh_resolution"]

#Savespace
savespace = settings["savespace"]
name = settings["name"]

os.makedirs(os.path.dirname(savespace), exist_ok=True)

#READ SPLINE DATA
splineData, data  = read_height_file(spline_data_path)
splineX = [point[0] for point in splineData]
splineY = [point[1] for point in splineData]
splineZ = [point[2] for point in splineData]

dunesHeightdiff = max(splineY) - min(splineY)
if dunesHeightdiff > fencesHeight:
    channelHeight = 10*dunesHeightdiff
else:
    channelHeight = 10*fencesHeight
#python arrays:
fencePointsOnSpline = np.empty((fencesNum,2), dtype = float)





#Gmsh model parts
windtunnelPoints = np.empty(4,dtype = object) #4 points for windtunnel rectangle
splinePoints = np.empty(len(splineX)-2, dtype = object) # points for spline 
fenceLowPoints = np.empty(fencesNum,  dtype = object) #2 points per fence (x and y position since on spline)


gmsh.initialize()
gmsh.model.add("Spline2DModel")
gmshm = gmsh.model

windtunnelPoints[0] = gmshm.geo.addPoint(splineX[0], splineY[0], splineZ[0], meshResolution)
windtunnelPoints[1] = gmshm.geo.addPoint(splineX[-1] , splineY[-1], splineZ[-1], meshResolution)
windtunnelPoints[2] = gmshm.geo.addPoint(splineX[-1], splineY[-1] + channelHeight, splineZ[-1], meshResolution)
windtunnelPoints[3] = gmshm.geo.addPoint(splineX[0], splineY[0] + channelHeight, splineZ[0], meshResolution)

for i in range(len(splineX)-2):
    splinePoints[i] = gmshm.geo.addPoint(
        splineX[i+1], #+1 because first is in windtunnelPoints
        splineY[i+1], 
        splineZ[i+1], 
        meshResolution)
    
splinePointComplete = [windtunnelPoints[0]] + splinePoints.tolist() + [windtunnelPoints[1]]
spline = gmshm.geo.add_spline(splinePointComplete)
gmshm.occ.synchronize()
gmshm.geo.synchronize()
fencesLastFenceX = fencesFirstPosX + (fencesNum - 1) * fencesDistance
splineLastFence = fencesLastFenceX / channelWidth

for i in range(fencesNum):
    targetX = fencesFirstPosX + i * fencesDistance
    pointsOnSpline = point_on_curve(spline, targetX, start = 0.6)
    fencePointsOnSpline[i] = [pointsOnSpline[0], pointsOnSpline[1]]
    print(f"Fence: {i+1}: TargetX: {targetX}; FoundX: {pointsOnSpline[0]}")
    compareSplinePoints = search_spline(splineX, pointsOnSpline[0])
    if compareSplinePoints is not None:
        fenceLowPoints[i] = splinePointComplete[compareSplinePoints]
    else:
        fenceLowPoints[i] = gmshm.geo.addPoint(pointsOnSpline[0], pointsOnSpline[1], pointsOnSpline[2], meshResolution)
gmshm.geo.synchronize()

distanceToFenceTop = np.copy(fencePointsOnSpline)
distanceToFenceTop[:,1] = distanceToFenceTop[:,1] - fencesHeight

distanceToFenceTopSorted = distanceToFenceTop[distanceToFenceTop[:,1].argsort()[::-1]] # sort by Y values

fencePoints = [[] for _ in range(len(distanceToFenceTopSorted))]
manipulatePointsOnSpline = np.copy(fencePointsOnSpline)


for i in range(len(distanceToFenceTopSorted)):
    currentPoints = []
    
    currentDistance = distanceToFenceTopSorted[i]
    if currentDistance[1] >= 0:
        for inner_list in fencePoints:
            inner_list.append(None)
    else:
        manipulatePointsOnSpline[:,1] += abs(currentDistance[1])
        distanceToFenceTopSorted[:,1] += abs(currentDistance[1])
        j = 0
        for inner_list in fencePoints:
            inner_list.append(round(manipulatePointsOnSpline[j][1],5))
            j+=1

print(fencePointsOnSpline)
print(fencePoints)
        
#Hier weiter machen nach Skizze die ich fotografiert habe



#DRAN DENKEN: GEOMETRIE MUSS NOCH GETEILT WERDEN!!!!! mit occ. arbeiten maybe
"""
geo = pygmsh.geo.Geometry()
m = geo.__enter__()


windtunnelPoints[0] = m.add_point([splineX[0], splineY[0], splineZ[0]], meshResolution)
windtunnelPoints[1] = m.add_point([splineX[-1] , splineY[-1], splineZ[-1]], meshResolution)
windtunnelPoints[2] = m.add_point([splineX[-1], splineY[-1] + channelHeight, splineZ[-1]], meshResolution)
windtunnelPoints[3] = m.add_point([splineX[0], splineY[0] + channelHeight, splineZ[0]], meshResolution)

for i in range(len(splineX)-2): #until -2 because first and last are in windtunnelPoints
    splinePoints[i] = m.add_point(
        [splineX[i+1], #+1 because first is in windtunnelPoints
         splineY[i+1], 
         splineZ[i+1]], 
         meshResolution)
    
spline = m.add_spline([windtunnelPoints[0]] + splinePoints.tolist() + [windtunnelPoints[1]])
m.synchronize()
splineID = gmshm.getEntities(1)[0][0]
print(splineID)

fencesLastFenceX = fencesFirstPosX + (fencesNum - 1) * fencesDistance
splineLastFence = fencesLastFenceX / fencesLastFenceX
print(splineLastFence)

for i in range(fencesNum):
    targetX = fencesFirstPosX + i * fencesDistance
    pointsOnSpline = point_on_curve(splineID, targetX, start = splineLastFence)
    print(f"Fence: {i+1}: TargetX: {targetX}; FoundX: {pointsOnSpline[0]}")
    fenceLowPoints[i] = m.add_point([pointsOnSpline[0], pointsOnSpline[1], pointsOnSpline[2]], meshResolution)


m.synchronize()
gmshm.geo.splitCurve

gmshm.geo.synchronize()
gmshm.mesh.generate(2)
gmsh.write(savespace)
"""






