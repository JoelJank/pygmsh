import pygmsh
import gmsh
import math
import numpy as np



corners = np.empty((4), dtype = object)
lines = np.empty((4), dtype = object)
loops = np.empty((1), dtype = object)
surfaces = np.empty((1), dtype = object)
geo = pygmsh.geo.Geometry()
m = geo.__enter__()
corners[0] = m.add_point((0.0, 0.0, 0.0), mesh_size = 1)
corners[1] = m.add_point((0.0, 0.0 , 5.0), mesh_size = 1)
corners[2] = m.add_point((0.0, 5.0, 5.0), mesh_size = 1)
corners[3] = m.add_point((0.0, 5.0, 0.0), mesh_size = 1)

lines[0] = m.add_line(corners[0], corners[1])
lines[1] = m.add_line(corners[1], corners[2])
lines[2] = m.add_line(corners[2], corners[3])
lines[3] = m.add_line(corners[3], corners[0])

loops[0] = m.add_curve_loop(lines)
surfaces[0] = m.add_plane_surface(loops[0])
m.set_transfinite_surface(surfaces[0], "Left", corners)
m.set_recombined_surfaces([surfaces[0]])


test_extrusion = m.extrude(surfaces[0], [10,0,0], num_layers=5, recombine=True)
print(test_extrusion)
m.add_physical(surfaces[0], "Inlet")
m.add_physical(test_extrusion[1], "Outlet")
m.add_physical(test_extrusion[2][0], "Bottom")
m.add_physical(test_extrusion[2][1], "Front")
m.add_physical(test_extrusion[2][2], "Top")
m.add_physical(test_extrusion[2][3], "Back")
m.add_physical
m.synchronize()
geo.generate_mesh(dim=3)
gmsh.write("mesh2.msh")
geo.__exit__()



