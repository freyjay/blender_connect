# TODO -- blender_connect

## Now
- [ ] Demo: render calibration rig via eye.py (FRONT 64x32, id + depth), verify vs human
- [ ] Character-aspect auto-correction in render_ascii

## Next
- [ ] Cross-section slicer (planar cut -> 2D coordinate profile)
- [ ] Silhouette / edge chars in renders
- [ ] Curve inspector (Bezier control points, curvature sampling)
- [ ] Perspective mode + arbitrary view directions
- [ ] Auto-calibration self-test scene (asserts, not eyeballs)

## Done
- [x] Patch MCP addon sendall truncation (issue #21) -- see PATCHES.md
- [x] Diagnose screenshot pipeline (PNG, 786KB budget, iterative downscale)
- [x] v0.1 eye.py: ray-cast ASCII renderer + scanline probe
- [x] Calibration round 1: scanline matched human front-view observation
