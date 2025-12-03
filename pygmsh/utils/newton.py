import gmsh

def point_on_curve(spline_id, target_x, start=0.5, tol=1e-15, max_iter=50):
    t = start
    for i in range(max_iter):
        x, y, z = gmsh.model.getValue(1, spline_id, [t])
        x_eps1, _, _ = gmsh.model.getValue(1, spline_id, [t + 1e-6])
        x_eps2, _, _ = gmsh.model.getValue(1, spline_id, [t - 1e-6])
        dxdt = (x_eps1 - x_eps2) / (2e-6)
        f = x - target_x
        if abs(f) < tol:
            break
        if abs(dxdt) < 1e-12:
            raise RuntimeError("Derivative too small")
        t -= f / dxdt
        t = max(0.0, min(1.0, t)) 
    x_best, y_best, z_best = gmsh.model.getValue(1, spline_id, [t])

    return [round(x_best,5), round(y_best,5), round(z_best,5)]