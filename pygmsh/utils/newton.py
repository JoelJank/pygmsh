import gmsh


def _to_float(val):
    if isinstance(val, (list, tuple)):
        return float(val[0])
    return float(val)


def point_on_curve(spline_id, target_x, start=None, tol=1e-12, max_iter=50):
    umin_raw, umax_raw = gmsh.model.getParametrizationBounds(1, spline_id)
    umin = _to_float(umin_raw)
    umax = _to_float(umax_raw)

    if start is None:
        start = 0.5 * (umin + umax)

    t = max(umin, min(umax, start))
    h = 1e-6 * max(1.0, abs(umax - umin))

    for _ in range(max_iter):
        x, y, z = gmsh.model.getValue(1, spline_id, [t])
        tp = max(umin, min(umax, t + h))
        tm = max(umin, min(umax, t - h))
        xp, _, _ = gmsh.model.getValue(1, spline_id, [tp])
        xm, _, _ = gmsh.model.getValue(1, spline_id, [tm])

        dxdt = (xp - xm) / (max(1e-12, tp - tm))
        f = x - target_x

        if abs(f) < tol:
            break
        if abs(dxdt) < 1e-12:
            raise RuntimeError("Derivative too small")

        t = max(umin, min(umax, t - f / dxdt))

    x_best, y_best, z_best = gmsh.model.getValue(1, spline_id, [t])
    return [round(x_best, 5), round(y_best, 5), round(z_best, 5)]