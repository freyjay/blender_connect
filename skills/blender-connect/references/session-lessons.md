# Session Lessons -- the case studies behind the doctrine

## The three vetoes (why "a veto is a win")
1. Wrong height: thigh blend at z=1.70 changed nothing (max 82->86 deg). The
   close-up showed the crease at z 1.2-1.4. Re-measured, moved, improved.
2. Method floor: after correct placement, max stuck ~74-86 deg. Overlapping
   primitives have a hardness floor (normals jump at intersections). Fix was
   a METHOD change: duplicate -> join -> voxel remesh = one skin. Junction max
   82 -> 47.5 deg; crease 86.5 -> 35.7; hard cells -66% / -83%.
3. Stale data: pre-fusion bbox ratios (0.68) drove a slimming edit; fused
   silhouette was already 0.643 (on target). Overshoot to 0.602; corrected by
   computed factor x1.225 -> 0.626 vs target 0.63.

## Hardness discrimination (loop 4)
Fusion softened the face too. Raising hardness at the muzzle (+24% hard cells)
was CORRECT there: chin, cleft, brow are anatomy. Same instrument, opposite
prescription. Ask: is this hardness a seam or a feature?

## The 180-degree lesson (eye v0.1 -> v0.2)
A single sign error (right = f x up * -1) rotated every render 180 deg. The
calibration rig (unique shape per axis: +X sphere, +Y cube, +Z cone, origin
torus) exposed it instantly. Always verify a new instrument on a rig with
known asymmetric ground truth before trusting it on real work.

## Transport truth
Blender MCP screenshots: PNG, ~786KB budget (1MB msg * 3/4 b64), HiDPI halved,
then downscaled iteratively -- complex content arrives illegible. Socket bug
upstream (#21): sendall on non-blocking socket truncates large sends on macOS;
patched locally with a blocking-send helper (see repo PATCHES.md). Conclusion
that built this system: text always survives; make the math speak text.

## API archaeology pattern (SketchUp, 3 probes)
1. dir() the entities/classes for candidate methods.
2. Try-ladder constructor variants; read tracebacks as documentation
   ("missing 1 required positional argument: vertex1_index" IS the spec).
3. Verify via authoritative counters (get_num_edges) not assumptions.
