---
name: blender-connect
description: Calibrated 3D modeling, verification, and math-to-drawing through Blender MCP with a text-based vision system (eye.py/senses.py). Make sure to use this skill whenever the user mentions Blender, modeling or sculpting anything in 3D via MCP, verifying or measuring geometry, rendering scenes as ASCII/text, silhouette or proportion analysis, calibrating against reference images, iterative refine loops on a model, or exporting geometry as a drawing (gesture/construction/contour) to any canvas -- even if they never say the word "skill" or "eye". Also applies when Blender screenshots are unreliable and a text-based verification path is needed.
compatibility: Requires the Blender MCP connector with the official addon running (localhost:9876) and the toolkit repo at ~/Developer/blender_connect (eye.py, senses.py).
---

# blender-connect: Calibrated Modeling

**First action on trigger:** read references/toolkit-api.md, then save the .blend before any operation.

Screenshots over MCP are lossy; math rendered as text always arrives. This
skill fuses the classical atelier curriculum, a math-native vision toolkit,
and a calibration doctrine proven across many verification loops into one
modeling method. Read references/toolkit-api.md before first tool use;
read references/session-lessons.md when a loop stalls or a metric floors.

## The Interconnection Map

| Atelier stage | Math instrument | Doctrine | Blender practice |
|---|---|---|---|
| 1. Proportion (see 2D) | senses.proportions() | Measure, don't remember | Reference images non-negotiable |
| 2. Line and angle | senses.contour_angles() | Flowing ~11 deg/step vs featured ~16 | Start from nearest primitive |
| 3. Rotation | senses.turntable() 18-deg sweeps | continuity_ok through all angles | Form must survive every view |
| 4. Value: sharp vs soft | render_hardness() + shade | Hardness is anatomical or accidental | Soften seams, keep features |
| 5. Parts before whole | frame=[names] everywhere | Part-by-part reveals what averages hide | Stash parts, re-fuse skin |
| 6. Drawing output | silhouette() -> 3 layers | Math becomes drawing | Export point sets to any canvas |

## Calibration Doctrine

1. Adjust -> verify in the SAME window (view, center, extent). No verification, no adjustment.
2. Measure, don't remember -- stale numbers cause overshoots.
3. When a metric floors, change METHOD, not effort (e.g. primitives -> voxel-fuse).
4. Never guess what you cannot see; say so, then build an instrument.
5. Enumerate APIs (dir(), probe ladders); never guess signatures.
6. A veto from the math is a win.

## Standard Workflow

1. Save the .blend. Fresh-import eye+senses (purge sys.modules first).
2. Blockout with primitives at reference-derived ratios; verify ratios immediately.
3. Look (render_ascii shade + edges); critique like a sculptor before touching anything.
4. Loop: score -> adjust parts -> re-score same window. Iterate until synced.
5. Fuse ladder: duplicate parts -> join -> voxel remesh 0.06 -> 0.05; keep part stash hidden.
6. Detail passes part-by-part; wanted hardness = definition.
7. Close: proportions vs targets, turntable continuity, human audit.

When anything here is insufficient: references/toolkit-api.md has full
signatures, examples, and pitfalls; references/session-lessons.md has the
case studies behind every doctrine line.
