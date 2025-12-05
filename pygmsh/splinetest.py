from utils.newton import point_on_curve
import gmsh

gmsh.initialize()
gmsh.model.add("SplineTest")
gmshm = gmsh.model


point1 = gmshm.occ.addPoint(0, 0, 0, 1)
point2 = gmshm.occ.addPoint(1, 1, 0, 1)
point3 = gmshm.occ.addPoint(2, 0, 0, 1)
spline = gmshm.occ.addSpline([point1, point2, point3])
gmshm.occ.synchronize()
target_x = 1.5
result = point_on_curve(spline, target_x, start=1.0)
print(f"Point on spline at x={target_x}: {result}")
pointoncurve = gmshm.occ.addPoint(result[0], result[1], result[2], 1)
gmshm.occ.synchronize()
gmshm.occ.fragment([(1,spline)], [(0,pointoncurve)])
gmshm.occ.synchronize()
gmshm.mesh.generate(1)
gmsh.write("spline_test.msh")