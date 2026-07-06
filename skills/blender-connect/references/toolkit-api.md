# Toolkit API -- eye.py / senses.py

Load pattern (Blender Python, avoids stale-module bugs):

    import sys, os
    p = os.path.expanduser("~/Developer/blender_connect")
    for m in ("eye", "senses"): sys.modules.pop(m, None)
    sys.path.insert(0, p)
    import eye, senses

## eye.py
- render_ascii(view="FRONT", width=72, height=None, mode="id", frame=None,
  aspect=0.5, aa=False, center=None, extent=None) -> str
  - view: FRONT/BACK/RIGHT/LEFT/TOP/BOTTOM or (x,y,z) direction vector
  - mode: id (letter per object + legend) | edges (UPPER=silhouette, lower=fill)
          | depth (near=dense) | shade (normal-facing ramp -- reveals curvature)
  - camera moves: center=(u,v) pans, extent=(eu,ev) zooms, frame=[names] isolates
- scanline(view, axis_value, lo, hi, step) -> [(pos, obj_name|None, depth)]

## senses.py
- proportions(view, frame, rows) -> H, W, W_over_H, widest_at_height_frac,
  symmetry_error, width_profile_top_to_bottom (10 samples)
- contour_angles(view, frame, rows, corner_deg=25) -> per edge:
  mean_turn_deg, max_turn_deg, corners_over_25deg
- turntable(step_deg=18, frame, rows) -> per-angle W/H table,
  max_W_jump_between_steps, continuity_ok
- render_hardness(view, frame, width) -> str; ramp by neighbor-normal angle,
  60deg=full, boundary forced hard
- silhouette(view, frame, rows) -> sub-pixel left/right edge arrays per row
  (bisection-refined; basis of proportions, contour_angles, drawing export)

## Inline hardness_score (calibration probe -- copy into build code)
Cast an n x n grid in a window; mean/max neighbor-normal angle + count > 25 deg.
Compare BEFORE and AFTER in the same window. See session-lessons for usage.

## Pitfalls
- sys.modules caching serves stale code after edits -- always purge before import.
- Voxel remesh erodes thin tips (ears); silhouette-check after every fuse.
- Part bounding-box ratios and fused silhouette ratios disagree; trust silhouette.
- First MCP command after a fresh connection sometimes fails; retry once.
- ray_cast respects visibility: hide the part stash so senses see only the skin.
- Characters are ~2x tall: width ~= 2x height for square world aspect.

## Drawing export (math -> drawing)
1. s = senses.silhouette("RIGHT", rows=72); downsample edges to ~36 pts each.
2. Gesture = every 4th contour point + authored curves (e.g. tail).
3. Construction = part spheres projected to view plane as (center, radius).
4. Contour = full edge chains.
5. Map world units -> canvas units; flip vertical axis when canvas y grows down.
Platform notes: SketchUp MCP edges go through GeometryInput.add_vertex ->
add_edge(i, j) (vertex INDICES) -> group.get_entities().fill(); color after fill
via edge.set_color(SUColor). Sandbox is an allowlist: no imports, no any().

- cavity_probe(center, rim_radius, rim_z, n, frame) -> holds_liquid,
  max/mean_depth, volume_units3. Use for any vessel/container BEFORE declaring done.
