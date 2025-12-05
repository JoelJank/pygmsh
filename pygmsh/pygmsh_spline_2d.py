import gmsh
import math
import os
import numpy as np
from utils.meshcalc_spline import infcalc_spline
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
meshGrowthAfterInflation = settings["meshgrowtrate_afterinflation"]

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

windtunnelPoints[0] = gmshm.occ.addPoint(splineX[0], splineY[0], splineZ[0], meshResolution)
windtunnelPoints[1] = gmshm.occ.addPoint(splineX[-1] , splineY[-1], splineZ[-1], meshResolution)
windtunnelPoints[2] = gmshm.occ.addPoint(splineX[-1], splineY[-1] + channelHeight, splineZ[-1], meshResolution)
windtunnelPoints[3] = gmshm.occ.addPoint(splineX[0], splineY[0] + channelHeight, splineZ[0], meshResolution)

for i in range(len(splineX)-2):
    splinePoints[i] = gmshm.occ.addPoint(
        splineX[i+1], #+1 because first is in windtunnelPoints
        splineY[i+1], 
        splineZ[i+1], 
        meshResolution)
    
splinePointComplete = [windtunnelPoints[0]] + splinePoints.tolist() + [windtunnelPoints[1]]
spline = gmshm.occ.addSpline(splinePointComplete)
gmshm.occ.synchronize()
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
        fenceLowPoints[i] = gmshm.occ.addPoint(pointsOnSpline[0], pointsOnSpline[1], pointsOnSpline[2], meshResolution)
gmshm.occ.synchronize()

spline_numbers = [spline]

for i in range(len(fenceLowPoints)):
    info = gmshm.occ.fragment([(1,spline_numbers[i])], [(0,fenceLowPoints[i])])
    print(info)
    spline_numbers.append(info[0][1][1])
windtunnelPoints[0] = splinePoints[-1]+1
windtunnelPoints[1] = splinePoints[-1]+2
    


distanceToFenceTop = np.copy(fencePointsOnSpline)
distanceToFenceTop[:,1] = distanceToFenceTop[:,1] - fencesHeight

distanceToFenceTopSorted = distanceToFenceTop[distanceToFenceTop[:,1].argsort()[::-1]]
calculateArray = np.copy(distanceToFenceTopSorted)

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
            
            


fenceAllPoints = [[] for _ in range(len(fencePoints)+2)]
print(fencePoints)

#Create Points on Fence:

for i in range (1,len(fencePoints)+1):
    currentFence = fencePoints[i-1]
    currentX = fencePointsOnSpline[i-1][0]
    for j in range(len(currentFence)):
        if currentFence[j] is not None:
            point = gmshm.occ.addPoint(currentX, currentFence[j], 0, meshResolution)
            gmshm.occ.synchronize()
            fenceAllPoints[i].append(point)
    TopEndPoint = gmshm.occ.addPoint(currentX, channelHeight, 0, meshResolution)
    fenceAllPoints[i].append(TopEndPoint)

gmshm.occ.synchronize()
fencePartPoints = np.abs(calculateArray[:,1])
fencePartPoints = [i for i in fencePartPoints if i !=0]
fencePartLengths = [fencePartPoints[0]] #WICHTIGES ARRAY!!!!
for i in range(len(fencePartPoints)-1):
    length =  fencePartPoints[i+1] - fencePartPoints[i]
    fencePartLengths.append(abs(length)) 
print(fencePartPoints)

for j in range(len(fencePartPoints)):
    if fencePartPoints[j] != 0:
        pointInlet = gmshm.occ.addPoint(splineX[0], fencePartPoints[j], 0, meshResolution)
        pointOutlet = gmshm.occ.addPoint(splineX[-1], fencePartPoints[j], 0, meshResolution)
        gmshm.occ.synchronize()
        fenceAllPoints[0].append(pointInlet)
        fenceAllPoints[-1].append(pointOutlet)
gmshm.occ.synchronize()

meshdata, toppoints, nbisoben = infcalc_spline(meshFirstLayerHeight, meshGrowthrate, meshNumLayers, channelHeight, meshGrowthAfterInflation, fencePartLengths)
meshdata[:,0] = [int(x[0]) + 1 for x in meshdata]
nbisoben[0] = int(nbisoben[0]) + 1
print(f"Height of last layer at top boundary: {nbisoben[1]}")

difftotopofinflation = toppoints - fencePartPoints[-1] 
topofinflation = []
topofinflation.append(toppoints)
for i in range (fencesNum):
    ytopofinflation = fencePoints[i][-1] + difftotopofinflation
    topofinflation.append(ytopofinflation) 
topofinflation.append(toppoints)

inflationPointsFences =  []

point = gmshm.occ.addPoint(splineX[0], topofinflation[0], 0, meshResolution)
fenceAllPoints[0].append(point)
for i in range (1, len(topofinflation)-1):
    point = gmshm.occ.addPoint(fencePointsOnSpline[i-1][0], topofinflation[i], 0, meshResolution)
    inflationPointsFences.append(point)
point = gmshm.occ.addPoint(splineX[-1], topofinflation[-1], 0, meshResolution)
fenceAllPoints[-1].append(point)
gmshm.occ.synchronize()

#Create all lines and inner line loops and surface to then fragment 

linesInlet = []
linesOutlet = []
linesTop = []
linesFences = []

outletLine1 = gmshm.occ.addLine(windtunnelPoints[1], fenceAllPoints[-1][0])
linesOutlet.append(outletLine1)
for i in range(len(fenceAllPoints[-1])-1):
    line = gmshm.occ.addLine(fenceAllPoints[-1][i], fenceAllPoints[-1][i+1])
    linesOutlet.append(line)
outletLineLast = gmshm.occ.addLine(fenceAllPoints[-1][-1], windtunnelPoints[2])
linesOutlet.append(outletLineLast)

inletLineLast = gmshm.occ.addLine(windtunnelPoints[3], fenceAllPoints[0][-1])
linesInlet.append(inletLineLast)
for i in range(len(fenceAllPoints[0])-1,0,-1):
    line = gmshm.occ.addLine(fenceAllPoints[0][i], fenceAllPoints[0][i-1])
    linesInlet.append(line)
inletLine1 = gmshm.occ.addLine(fenceAllPoints[0][0], windtunnelPoints[0])
linesInlet.append(inletLine1)

topLineLast = gmshm.occ.addLine(windtunnelPoints[2], fenceAllPoints[-2][-1])
linesTop.append(topLineLast)
for i in range(len(fenceAllPoints)-2,1,-1):
    line = gmshm.occ.addLine(fenceAllPoints[i][-1], fenceAllPoints[i-1][-1])
    linesTop.append(line)
topLine1 = gmshm.occ.addLine(fenceAllPoints[1][-1], windtunnelPoints[3])
linesTop.append(topLine1)

#Create Fence vertical lines
fencesLines = [[] for _ in range(fencesNum)]

for i in range (fencesNum):
    j = i+1
    currentPointOnSpline = fenceLowPoints[i]
    currentInflationPoint = inflationPointsFences[i]
    currentFencePoints = fenceAllPoints[j]
    line = gmshm.occ.addLine(currentPointOnSpline, currentFencePoints[0])
    fencesLines[i].append(line)
    for k in range(len(currentFencePoints)-2):
        line = gmshm.occ.addLine(currentFencePoints[k], currentFencePoints[k+1])
        fencesLines[i].append(line)
    line = gmshm.occ.addLine(currentFencePoints[-2], currentInflationPoint)
    fencesLines[i].append(line)
    line = gmshm.occ.addLine(currentInflationPoint, currentFencePoints[-1])
    fencesLines[i].append(line)
gmshm.occ.synchronize()
print(linesTop[0])
#Create Surface Loops
surfaceLoops = [[] for _ in range(fencesNum+1)]
surfaces = [[] for _ in range(fencesNum+1)]
#First surface loop (between inlet and first fence)
surfaceLoops[0] = gmshm.occ.addCurveLoop([spline_numbers[0]]+fencesLines[0]+[linesTop[-1]]+linesInlet)
surfaces[0] = gmshm.occ.addPlaneSurface([surfaceLoops[0]])
#Surfaces between fences
for i in range(1,fencesNum):
    surfaceLoops[i] = gmshm.occ.addCurveLoop(
        [spline_numbers[i]]+
        fencesLines[i]+
        [linesTop[-i-1]]+
        [-l for l in reversed(fencesLines[i-1])]
    )
    surfaces[i] = gmshm.occ.addPlaneSurface([surfaceLoops[i]])

surfaceLoops[-1] = gmshm.occ.addCurveLoop(
    [spline_numbers[-1]]+
    linesOutlet+
    [linesTop[0]]+
    [-l for l in reversed(fencesLines[-1])]
)
surfaces[-1] = gmshm.occ.addPlaneSurface([surfaceLoops[-1]])
gmshm.occ.synchronize()
#Meshing -> Set transfinite curves

for i in range(len(linesInlet)-1):
    j= i+1
    gmshm.mesh.setTransfiniteCurve(linesInlet[-j], meshdata[i][0], "Progression", 1/meshGrowthrate)
    gmshm.mesh.setTransfiniteCurve(linesOutlet[i], meshdata[i][0], "Progression", meshGrowthrate)
    for j in range(len(fencesLines)):
        gmshm.mesh.setTransfiniteCurve(fencesLines[j][i], meshdata[i][0], "Progression", meshGrowthrate)

gmshm.mesh.setTransfiniteCurve(linesInlet[0], nbisoben[0], "Progression", 1/meshGrowthAfterInflation)
gmshm.mesh.setTransfiniteCurve(linesOutlet[-1], nbisoben[0], "Progression", meshGrowthAfterInflation)
for j in range(len(fencesLines)):
    gmshm.mesh.setTransfiniteCurve(fencesLines[j][-1], nbisoben[0], "Progression", meshGrowthAfterInflation)

nBefore = math.ceil(fencesFirstPosX / meshFreesize)+1
nBetween = math.ceil(fencesDistance / meshFreesize)+1
for i in range(1,len(spline_numbers)-1):
    j = i+1
    gmshm.mesh.setTransfiniteCurve(spline_numbers[i], nBetween, "Progression", 1.0)
    gmshm.mesh.setTransfiniteCurve(linesTop[-j], nBetween, "Progression", 1.0)
gmshm.mesh.setTransfiniteCurve(spline_numbers[0], nBefore, "Progression", 1.0)
gmshm.mesh.setTransfiniteCurve(linesTop[-1], nBefore, "Progression", 1.0)
gmshm.mesh.setTransfiniteCurve(spline_numbers[-1], nBefore, "Progression", 1.0)
gmshm.mesh.setTransfiniteCurve(linesTop[0], nBefore, "Progression", 1.0)        

for i in range(1,len(surfaces)-1):
    gmshm.mesh.setTransfiniteSurface(surfaces[i], "Right", [fenceLowPoints[i-1], fenceLowPoints[i], fenceAllPoints[i+1][-1], fenceAllPoints[i][-1]])
    gmshm.mesh.setRecombine(2,surfaces[i])
gmshm.mesh.setTransfiniteSurface(surfaces[0], "Right", [windtunnelPoints[0], fenceLowPoints[0], fenceAllPoints[1][-1], windtunnelPoints[3]])
gmshm.mesh.setRecombine(2,surfaces[0])
gmshm.mesh.setTransfiniteSurface(surfaces[-1], "Right", [fenceLowPoints[-1], windtunnelPoints[1], windtunnelPoints[2], fenceAllPoints[-2][-1]])
gmshm.mesh.setRecombine(2,surfaces[-1])
gmshm.occ.synchronize()

lettrough_all = []
for i in range(len(fencesLines)):
    fencelines = []
    letthroughlines = []
    currentPoints = fencePoints[i]
    j = 0
    while currentPoints[j] <= fencesHeight:
        fencelines.append(fencesLines[i][j])
        j+=1
        if j >= len(currentPoints):
            break
    gmshm.addPhysicalGroup(1, fencelines, i+1)
    gmshm.setPhysicalName(1, i+1, f"Fence{i+1}")
    letthroughlines = fencesLines[i][j:]
    lettrough_all.append(letthroughlines)

flat_lettrough = [element for sublist in lettrough_all for element in sublist]
gmshm.addPhysicalGroup(1, flat_lettrough, fencesNum + 1)
gmshm.setPhysicalName(1, fencesNum + 1, "Letthroughs")



num = fencesNum + 1
gmshm.addPhysicalGroup(1, linesInlet,num+1)
gmshm.setPhysicalName(1, num+1, "Inlet")
gmshm.addPhysicalGroup(1, linesOutlet,num+2)
gmshm.setPhysicalName(1, num+2, "Outlet")
gmshm.addPhysicalGroup(1, linesTop,num+3)
gmshm.setPhysicalName(1, num+3, "Top")
gmshm.addPhysicalGroup(1, spline_numbers,num+4)
gmshm.setPhysicalName(1, num+4, "Bottom")
gmshm.addPhysicalGroup(2, surfaces,num+5)
gmshm.setPhysicalName(2, num+5, "Channel")
print(meshdata)

gmsh.model.occ.synchronize()
gmshm.mesh.generate(3)
gmsh.write(savespace)






