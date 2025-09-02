import pygmsh
import meshio
import gmsh
import json
import math
import os
import numpy as np

settings_path = "settings/settings.json"

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
    dySlits = hFences/(nSlits)
    yposSlits = [j*dySlits for j in range(1,nSlits+1)]
else:
    yposSlits = [hFences]


geo = pygmsh.geo.Geometry()
m = geo.__enter__()

pointsChannel = [
    m.add_point((0.0,0.0,0.0), mesh_size=resolution) # (0,0)
] + [
    m.add_point((xposFences[i],0.0,0.0), mesh_size=resolution) for i in range(nFences) # xpos of fences at bottom
] + [
    m.add_point((lChannel,0.0,0.0), mesh_size=resolution) # (lChannel,0)
] + [
    m.add_point((lChannel,yposSlits[j],0.0),mesh_size=resolution) for j in range(nSlits) # (xpos of fences, ypos of slits)
] + [
    m.add_point((lChannel,hChannel,0.0), mesh_size=resolution) # (lChannel,hChannel)
] + [
    m.add_point((xposFences[i],hChannel,0.0),mesh_size=resolution) for i in range(nFences) # xpos of fences at top
] + [
    m.add_point((0.0,hChannel,0.0), mesh_size=resolution) # (0,hChannel)
] + [
    m.add_point((0.0,yposSlits[j],0.0),mesh_size=resolution) for j in range(nSlits) # (xpos of fences, ypos of slits)
]

channel_lines = [
    m.add_line(pointsChannel[i],pointsChannel[i+1]) for i in range(-1, len(pointsChannel)-1)
]

#Problem: lines are not in correct order for line loop bzw. dann kann man die Planes nicht so einfach erstellen. Lösung finden!
#idee: vielleicht kann man hingehen und für jeden Plane eine eigene Linie erstellen, die dann nur die Punkte verbindet, die für den Plane gebraucht werden.
#Ich glaub das ist das beste vorgehen.


channel_lines =[
]
m.synchronize()
geo.generate_mesh(dim=2)
gmsh.write("test3.msh")
geo.__exit__()

