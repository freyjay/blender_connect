# SPDX-License-Identifier: MIT
"""
blender-connect :: eye.py -- v0.1
A text-based vision system for AI agents driving Blender over MCP.

Pixels get destroyed by size budgets and downscalers; text always survives.
So this eye renders the scene as CHARACTERS: an orthographic ray-cast grid
where each object is a letter (id mode) or a depth gradient (depth mode).
Mathematically exact, resolution-independent, transport-safe.

Usage (inside Blender):
    from eye import render_ascii, scanline
    print(render_ascii(view="FRONT", width=64, height=32, mode="id"))
"""

import bpy
from mathutils import Vector

_VIEWS = {
    # view: (forward, screen_up)   -- Blender conventions
    "FRONT": (Vector((0, 1, 0)), Vector((0, 0, 1))),   # looking from -Y
    "BACK":  (Vector((0, -1, 0)), Vector((0, 0, 1))),
    "RIGHT": (Vector((-1, 0, 0)), Vector((0, 0, 1))),  # looking from +X
    "LEFT":  (Vector((1, 0, 0)), Vector((0, 0, 1))),
    "TOP":   (Vector((0, 0, -1)), Vector((0, 1, 0))),  # looking down -Z
    "BOTTOM": (Vector((0, 0, 1)), Vector((0, 1, 0))),
}

_DEPTH_RAMP = "@%#*+=-:. "  # near -> far (dense to sparse), miss = space


def _scene_bounds(right, up_s):
    """Project all visible mesh bounding boxes onto screen axes."""
    us, vs = [], []
    for obj in bpy.context.visible_objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            us.append(w.dot(right))
            vs.append(w.dot(up_s))
    if not us:
        return 0.0, 0.0, 5.0, 5.0
    cu, cv = (min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2
    eu = max((max(us) - min(us)) / 2, 0.1) * 1.15
    ev = max((max(vs) - min(vs)) / 2, 0.1) * 1.15
    return cu, cv, eu, ev


def render_ascii(view="FRONT", width=64, height=32, mode="id",
                 center=None, extent=None):
    """
    Render an orthographic character image of the scene.

    view   -- one of FRONT/BACK/RIGHT/LEFT/TOP/BOTTOM
    mode   -- "id" (letter per object + legend) or "depth" (gradient by distance)
    center -- optional (u, v) world-units center of frame on screen axes
    extent -- optional (eu, ev) world-units half-size of frame

    Tip: characters are ~2x taller than wide, so width ~= 2*height gives a
    roughly undistorted world aspect.
    Returns a single string (rows top to bottom).
    """
    forward, up_hint = _VIEWS[view.upper()]
    right = forward.cross(up_hint).normalized() * -1  # screen +u to the right
    # Re-derive exact screen-up (orthogonal)
    up_s = right.cross(forward).normalized()

    if center is None or extent is None:
        cu, cv, eu, ev = _scene_bounds(right, up_s)
        if center is not None:
            cu, cv = center
        if extent is not None:
            eu, ev = extent
    else:
        (cu, cv), (eu, ev) = center, extent

    deps = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    start_dist = max(eu, ev) * 6 + 20.0

    # Assign a letter per mesh object
    letters = {}
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for i, obj in enumerate([o for o in bpy.context.visible_objects if o.type == "MESH"]):
        letters[obj.name] = alphabet[i % len(alphabet)]

    hits_depth = []
    rows = []
    for r in range(height):
        v = cv + ev * (1 - 2 * (r + 0.5) / height)   # top row = +v
        row = []
        for c in range(width):
            u = cu + eu * (2 * (c + 0.5) / width - 1)
            origin = -forward * start_dist + right * u + up_s * v
            hit, loc, _n, _i, obj, _m = scene.ray_cast(deps, origin, forward)
            if not hit:
                row.append((" ", None))
            else:
                d = (loc - origin).length
                hits_depth.append(d)
                row.append((letters.get(obj.name, "?"), d))
        rows.append(row)

    if mode == "depth" and hits_depth:
        dmin, dmax = min(hits_depth), max(hits_depth)
        span = (dmax - dmin) or 1.0
        out_rows = ["".join(
            " " if d is None else _DEPTH_RAMP[
                min(int((d - dmin) / span * (len(_DEPTH_RAMP) - 2)), len(_DEPTH_RAMP) - 2)]
            for (_ch, d) in row) for row in rows]
    else:
        out_rows = ["".join(ch for (ch, _d) in row) for row in rows]

    header = "[{} | {}x{} | u:[{:.2f},{:.2f}] v:[{:.2f},{:.2f}] | {:.3f} units/char]".format(
        view.upper(), width, height, cu - eu, cu + eu, cv - ev, cv + ev, (2 * eu) / width)
    legend = "  ".join("{}={}".format(l, n) for n, l in sorted(letters.items(), key=lambda x: x[1]))
    return header + chr(10) + (legend + chr(10) if mode == "id" else "") + chr(10).join(out_rows)


def scanline(view="FRONT", axis_value=0.0, lo=-2.0, hi=2.0, step=0.1):
    """1-D probe: march rays along one screen axis, report first hit per sample."""
    forward, up_hint = _VIEWS[view.upper()]
    right = forward.cross(up_hint).normalized() * -1
    up_s = right.cross(forward).normalized()
    deps = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    out = []
    v = lo
    while v <= hi + 1e-9:
        origin = -forward * 50.0 + right * axis_value + up_s * v
        hit, loc, _n, _i, obj, _m = scene.ray_cast(deps, origin, forward)
        out.append((round(v, 3), obj.name if hit else None,
                    round((loc - origin).length, 3) if hit else None))
        v += step
    return out
