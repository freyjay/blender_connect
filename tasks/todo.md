# TODO -- blender_connect

## Now
- [ ] Perspective projection mode
- [ ] Auto-calibration self-test scene (asserts, not eyeballs)
- [ ] Curve inspector (Bezier control points, curvature sampling)

## Next
- [ ] Ordered cross-section loops (connect edge pairs into polylines)
- [ ] Diff renders (before/after an edit, changed cells highlighted)
- [ ] Multi-view composite report (TOP+FRONT+RIGHT in one call)

## Done
- [x] Patch MCP addon sendall truncation (issue #21) -- see PATCHES.md
- [x] Diagnose screenshot pipeline (PNG, 786KB budget, iterative downscale)
- [x] v0.1 eye.py: ray-cast ASCII renderer + scanline probe
- [x] Calibration round 1: scanline matched human front-view observation
- [x] v0.2: basis handedness fix (v0.1 rendered 180-deg rotated -- caught by rig)
- [x] v0.2: aspect-true auto-framing, arbitrary view vectors, frame= targeting
- [x] v0.2: edges mode (uppercase silhouettes), shade mode (curvature perception)
- [x] v0.2: 2x2 supersampling option, cross-section slicer
- [x] Calibration round 2: v0.2 FRONT render verified (cone top/apex-up, sphere right, cube peek)
