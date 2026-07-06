# SPDX-License-Identifier: MIT
"""
blender-connect :: senses.py -- v0.3 "curriculum" senses pack
Five-stage perception upgrade (proportion -> angle -> rotation -> hardness -> parts).

1. proportions()    -- 2D silhouette analysis: width profile, ratios, symmetry
2. contour_angles() -- sub-pixel silhouette tracing, tangent angles, corner count
3. turntable()      -- form metrics at fixed rotation intervals (default 18 deg = 5%)
4. render_hardness()-- sharp-vs-soft perception via normal gradients
5. Doctrine: inspect part by part (every function takes frame=[names]).
"""

import math
import bpy
from mathutils import Vector
from eye import _basis, _targets, _bounds

_H_RAMP = " .:-=+*#%@"


def _caster(frame):
    """v0.2: pass-through occlusion -- a hit outside `frame` peels through
    (up to 8 bounces) instead of reporting a miss. Fixes false silhouette
    breaks where hair/eyes shadow skin."""
    deps = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    objs = _targets(frame)
    names = {o.name for o in objs} if frame else None

    def cast(origin, direction, _bounces=0):
        hit, loc, nrm, _i, obj, _m = scene.ray_cast(deps, origin, direction)
        if not hit:
            return None
        if names and obj.name not in names:
            if _bounces >= 8:
                return None
            nudged = loc + direction.normalized() * 1e-4
            return cast(nudged, direction, _bounces + 1)
        return loc, nrm, obj.name
    return cast, objs

def _edge_bisect(cast, forward, right, up_s, v, u_in, u_out, start, iters=7):
    """Sub-pixel silhouette edge: bisect between a hitting u and a missing u."""
    for _ in range(iters):
        um = (u_in + u_out) / 2
        if cast(-forward * start + right * um + up_s * v, forward):
            u_in = um
        else:
            u_out = um
    return (u_in + u_out) / 2


def silhouette(view="RIGHT", frame=None, rows=64):
    """Outer silhouette as sub-pixel (u,v) edge points per row. Returns
    dict with left[], right[] edge arrays (None where empty row)."""
    forward, right, up_s = _basis(view)
    cast, objs = _caster(frame)
    cu, cv, eu, ev = _bounds(objs, right, up_s)
    start = max(eu, ev) * 6 + 20.0
    scan_n = 72
    left, right_e, vs = [], [], []
    for r in range(rows):
        v = cv + ev - (r + 0.5) * (2 * ev / rows)
        us = [cu - eu + (i + 0.5) * (2 * eu / scan_n) for i in range(scan_n)]
        hits = [bool(cast(-forward * start + right * u + up_s * v, forward)) for u in us]
        vs.append(v)
        if not any(hits):
            left.append(None); right_e.append(None)
            continue
        i_first = hits.index(True)
        i_last = len(hits) - 1 - hits[::-1].index(True)
        uL = us[i_first] if i_first == 0 else _edge_bisect(
            cast, forward, right, up_s, v, us[i_first], us[i_first - 1], start)
        uR = us[i_last] if i_last == scan_n - 1 else _edge_bisect(
            cast, forward, right, up_s, v, us[i_last], us[i_last + 1], start)
        left.append(uL); right_e.append(uR)
    return {"v": vs, "left": left, "right": right_e,
            "center_u": cu, "extent": (eu, ev)}


def proportions(view="FRONT", frame=None, rows=64):
    """Stage 1: read the form 2-dimensionally. Width profile + ratios + symmetry."""
    s = silhouette(view, frame, rows)
    widths, mids = [], []
    for L, R in zip(s["left"], s["right"]):
        if L is None:
            widths.append(0.0); mids.append(None)
        else:
            widths.append(R - L); mids.append((R + L) / 2)
    occupied = [i for i, w in enumerate(widths) if w > 0]
    if not occupied:
        return {"empty": True}
    top, bot = occupied[0], occupied[-1]
    H = s["v"][top] - s["v"][bot]
    W = max(widths)
    widest_at = widths.index(W)
    valid_mids = [m for m in mids if m is not None]
    sym_err = (sum(abs(m - s["center_u"]) for m in valid_mids)
               / len(valid_mids)) / (W or 1)
    prof = [round(widths[top + int(k * (bot - top) / 9)] / W, 2) for k in range(10)]
    return {
        "H": round(H, 3), "W": round(W, 3), "W_over_H": round(W / H, 3),
        "widest_at_height_frac": round(1 - (widest_at - top) / max(1, bot - top), 2),
        "symmetry_error": round(sym_err, 3),
        "width_profile_top_to_bottom": prof,
    }


def contour_angles(view="RIGHT", frame=None, rows=64, corner_deg=25.0):
    """Stage 2: tangent angle along each silhouette edge; smoothness + corners."""
    s = silhouette(view, frame, rows)
    out = {}
    for side in ("left", "right"):
        pts = [(u, v) for u, v in zip(s[side], s["v"]) if u is not None]
        if len(pts) < 3:
            out[side] = {"n": len(pts)}
            continue
        angs = [math.degrees(math.atan2(pts[i + 1][1] - pts[i][1],
                                        pts[i + 1][0] - pts[i][0]))
                for i in range(len(pts) - 1)]
        deltas = []
        for a, b in zip(angs, angs[1:]):
            d = (b - a + 180) % 360 - 180
            deltas.append(abs(d))
        out[side] = {
            "n_points": len(pts),
            "mean_turn_deg": round(sum(deltas) / len(deltas), 2),
            "max_turn_deg": round(max(deltas), 1),
            "corners_over_{:g}deg".format(corner_deg):
                sum(1 for d in deltas if d > corner_deg),
        }
    return out


def turntable(step_deg=18.0, frame=None, rows=40):
    """Stage 3: rotate the viewpoint around Z at fixed intervals; track the form."""
    table = []
    a = 0.0
    while a < 360.0 - 1e-6:
        r = math.radians(a)
        view = (math.sin(r), math.cos(r), 0.0)
        p = proportions(view, frame, rows)
        table.append({"deg": round(a, 1), "W": p.get("W"), "H": p.get("H"),
                      "widest_frac": p.get("widest_at_height_frac")})
        a += step_deg
    ws = [t["W"] for t in table]
    jumps = [round(abs(b - a), 3) for a, b in zip(ws, ws[1:] + ws[:1])]
    return {"steps": table, "max_W_jump_between_steps": max(jumps),
            "continuity_ok": max(jumps) < 0.35 * max(ws)}


def render_hardness(view="RIGHT", frame=None, width=56, height=None, aspect=0.5):
    """Stage 4: sharp vs soft. Char density = normal gradient (deg) to neighbors;
    silhouette boundary forced hard. Soft curvature reads light, creases dense."""
    forward, right, up_s = _basis(view)
    cast, objs = _caster(frame)
    cu, cv, eu, ev = _bounds(objs, right, up_s)
    if height is None:
        height = max(4, min(56, round(width * (ev / eu) * aspect)))
    start = max(eu, ev) * 6 + 20.0
    du, dv = 2 * eu / width, 2 * ev / height
    grid = []
    for r in range(height):
        v = cv + ev - (r + 0.5) * dv
        row = []
        for c in range(width):
            u = cu - eu + (c + 0.5) * du
            h = cast(-forward * start + right * u + up_s * v, forward)
            row.append(h[1].normalized() if h else None)
        grid.append(row)
    rows_out = []
    for r in range(height):
        line = []
        for c in range(width):
            n = grid[r][c]
            if n is None:
                line.append(" ")
                continue
            worst = 0.0
            boundary = False
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < height and 0 <= cc < width and grid[rr][cc] is not None:
                    ang = math.degrees(n.angle(grid[rr][cc]))
                    worst = max(worst, ang)
                else:
                    boundary = True
            k = len(_H_RAMP) - 1 if boundary else min(
                int(worst / 60.0 * (len(_H_RAMP) - 1)), len(_H_RAMP) - 1)
            line.append(_H_RAMP[k])
        rows_out.append("".join(line))
    header = "[hardness {} | {}x{} | 60deg=full | boundary=@]".format(
        view if isinstance(view, str) else "custom", width, height)
    return chr(10).join([header] + rows_out)


def cavity_probe(center=(0.0, 0.0), rim_radius=0.7, rim_z=2.1, n=14, frame=None):
    """Function-not-form probe: vertical rays down into a vessel.
    Returns holds_liquid, max/mean interior depth below rim, volume held.
    Born from a human audit: a mug modeled solid scored perfectly on every
    surface sense. Surface senses do not see cavities; this one does."""
    deps = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    down = Vector((0, 0, -1))
    cast, _ = _caster(frame)
    cell = (2.0 * rim_radius / n) ** 2
    depths = []
    for i in range(n):
        for j in range(n):
            x = center[0] - rim_radius + (i + 0.5) * 2 * rim_radius / n
            y = center[1] - rim_radius + (j + 0.5) * 2 * rim_radius / n
            if (x - center[0]) ** 2 + (y - center[1]) ** 2 > rim_radius ** 2:
                continue
            h = cast(Vector((x, y, rim_z + 5.0)), down)
            if h:
                depths.append(max(0.0, rim_z - h[0].z))
    if not depths:
        return {"holds_liquid": False, "max_depth": 0.0, "volume_units3": 0.0}
    vol = sum(d * cell for d in depths)
    mx = max(depths)
    return {"holds_liquid": mx > 0.3, "max_depth": round(mx, 2),
            "mean_depth": round(sum(depths) / len(depths), 2),
            "volume_units3": round(vol, 2)}


def width_bands(view="FRONT", frame=None, z_top=1.10, z_bot=-1.15, bands=10, rows=64):
    """Anatomical-span width curve (crown->chin), normalized to max width.
    Registration matters: never compare curves normalized over different spans."""
    s = silhouette(view, frame, rows)
    out = []
    for k in range(bands):
        z = z_top - (k + 0.5) * (z_top - z_bot) / bands
        best, bw = None, 0.0
        for L, R, v in zip(s["left"], s["right"], s["v"]):
            if L is None:
                continue
            if best is None or abs(v - z) < abs(best - z):
                best, bw = v, R - L
        out.append(bw)
    m = max(out) or 1.0
    return [round(w / m, 3) for w in out]


def occupancy_grid(view="FRONT", n=30, frame=None):
    """Auto-fit n x n occupancy grid over ALL visible mesh (or frame). Row 0/col 0
    = top-left of the true bounding extent; each cell 1 if any surface is hit.
    Precision instrument: dense enough to catch what sparse landmarks miss
    (asymmetric bulges, unnatural flat plateaus, isolated single-part errors)."""
    import bpy
    from mathutils import Vector
    objs = _targets(frame)
    xs, zs = [], []
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x); zs.append(w.z)
    if not xs:
        return {"grid": [], "center": (0,0), "extent": (0,0)}
    cu, cv = (min(xs)+max(xs))/2, (min(zs)+max(zs))/2
    eu, ev = (max(xs)-min(xs))/2*1.03, (max(zs)-min(zs))/2*1.03
    import eye
    g = eye.render_ascii(view=view, width=n, height=n, mode="id",
                         center=(cu, cv), extent=(eu, ev), frame=frame)
    rows = g.split(chr(10))[2 if frame is None else 1:]
    grid = [[1 if ch != " " else 0 for ch in row] for row in rows if row]
    return {"grid": grid, "center": (round(cu,3), round(cv,3)),
            "extent": (round(eu,3), round(ev,3))}
