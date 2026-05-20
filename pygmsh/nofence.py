import pygmsh
import gmsh 
import math
import numpy as np
from utils.meshcalc import totalheightcalculation, layercalculations
from utils.jsonutil import json_read, json_write


settings_path = "../config/settings_nofence.json"

settings = json_read(settings_path)

channel_height = settings["channel_height"]
channel_width = settings["channel_width"]
mesh_freesize = settings["mesh_freesize"]
mesh_firstlayerheight = settings["mesh_firstlayerheight"]
mesh_inflationlayers = settings["mesh_inflationlayers"]
mesh_growthrate = settings["mesh_growthrate"]
mesh_growtrate_afterinflation = settings["mesh_growtrate_afterinflation"]
savespace = settings["savespace"]

jsonwritespace = savespace.replace(".msh", ".json")
json_write(settings_path, jsonwritespace)

inflation_totalheight = totalheightcalculation(mesh_firstlayerheight, mesh_growthrate, mesh_inflationlayers)
afterInflation, nextlayeroben, lastlayeroben = layercalculations(channel_height-inflation_totalheight, mesh_growtrate_afterinflation, mesh_freesize)
numberMeshX = math.ceil((channel_width) / mesh_freesize)+1

plane_corner = np.empty((2,3), dtype = object)
lines_hor = np.empty(2, dtype = object)
lines_ver = np.empty((2,2), dtype = object)
plane_loop = np.empty(1, dtype = object)
plane_surface = np.empty(1, dtype = object)

geo = pygmsh.geo.Geometry()
m = geo.__enter__()

plane_corner[0][0] = m.add_point((0.0, 0.0, 0.0))
plane_corner[0][1] = m.add_point((0.0, inflation_totalheight, 0.0))
plane_corner[0][2] = m.add_point((0.0, channel_height, 0.0))

plane_corner[1][0] = m.add_point((channel_width, 0.0, 0.0))
plane_corner[1][1] = m.add_point((channel_width, inflation_totalheight, 0.0))
plane_corner[1][2] = m.add_point((channel_width, channel_height, 0.0))

lines_hor[0] = m.add_line(plane_corner[0][0], plane_corner[1][0])
lines_hor[1] = m.add_line(plane_corner[1][2], plane_corner[0][2])

lines_ver[0][0] = m.add_line(plane_corner[0][2], plane_corner[0][1])
lines_ver[0][1] = m.add_line(plane_corner[0][1], plane_corner[0][0])
lines_ver[1][0] = m.add_line(plane_corner[1][0], plane_corner[1][1])
lines_ver[1][1] = m.add_line(plane_corner[1][1], plane_corner[1][2])

plane_loop[0] = m.add_curve_loop([lines_hor[0], lines_ver[1][0], lines_ver[1][1], 
                                  lines_hor[1], lines_ver[0][0], lines_ver[0][1]])

plane_surface[0] = m.add_plane_surface(plane_loop[0])

m.set_transfinite_curve(lines_hor[0], numberMeshX, "Progression", 1.0)
m.set_transfinite_curve(lines_hor[1], numberMeshX, "Progression", 1.0)

m.set_transfinite_curve(lines_ver[0][1], mesh_inflationlayers+1, "Progression", 1/mesh_growthrate)
m.set_transfinite_curve(lines_ver[1][0], mesh_inflationlayers+1, "Progression", mesh_growthrate)
m.set_transfinite_curve(lines_ver[0][0], math.ceil(afterInflation)+1, "Progression", 1/mesh_growtrate_afterinflation)
m.set_transfinite_curve(lines_ver[1][1], math.ceil(afterInflation)+1, "Progression", mesh_growtrate_afterinflation)

m.set_transfinite_surface(plane_surface[0],"Right", 
                          [plane_corner[0][0], plane_corner[1][0], 
                           plane_corner[1][2], plane_corner[0][2]])

m.synchronize()
m.set_recombined_surfaces([plane_surface[0]])
m.synchronize()

m.add_physical([plane_surface[0]], "Fluid")
m.add_physical([lines_hor[0]], "Bottom")
m.add_physical([lines_hor[1]], "Top")
m.add_physical([lines_ver[0][0], lines_ver[0][1]], "Inlet")
m.add_physical([lines_ver[1][0], lines_ver[1][1]], "Outlet")

geo.generate_mesh(dim=2)
gmsh.option.setNumber("Geometry.Tolerance", 1e-8)  
gmsh.model.mesh.removeDuplicateNodes()
gmsh.write(savespace)
geo.__exit__()
print(lastlayeroben)

#Extend this to a "3D" for OpenFOAM by extending one mesh zell in z direction