# Masterwork Ledger -- boy_v2 vs reference photos
Loop protocol: [1. compare output vs reference -> 3 distinctions with magnitudes;
2. calibrate the ENGINE for those distinctions (perceptual/geometric/both verdict);
3. adjust the MODEL with the calibrated engine; verify same windows] x 20.
Masterwork = new distinctions fall below the engine's perception floor.

## Loop 1 (of 20)
| D | Verdict | Finding | Open magnitude | Close magnitude |
|---|---|---|---|---|
| D1 | perceptual | width-curve band misregistration (bbox vs anatomical span) | false 0.51 | 0 -- engine: senses.width_bands() |
| D2 | geometric | upper skull too wide (bands 1-2) | +0.16/+0.18 | +0.13/+0.14 (carried) |
| D3 | geometric | jaw-neck seam hardness | 71.7 max | VETO at 96.8 (blend misplaced) -> repositioned, see below |

Loop 1 totals: width-curve abs error 0.75 -> 0.60. Regressions held (span 0.429).
Engine gains: width_bands() anatomical registration; graph learned JawBlend.

## Carried queue
- D2 residual: bands 1-2 (+0.13/+0.14)
- D3: seam (value below, post-reposition)

## Honesty audit (post-Loop-1)
User challenge: 'did you actually compare to the reference?' Answer: NO --
loops compared model vs CACHED derived constants; the reference images
stopped being consulted after initial digitization. Fresh look found what
the cache never contained: ear protrusion (defining trait, zero coverage
in 60+ measurements), nose too present from front, lid-over-iris beyond
blockout ceiling (logged as fidelity floor, not fixable by sphere tweak).
Then two instrument failures in the fix itself: a taper-confounded width
ratio faked a failure, causing an overshoot chase (1.14 -> 1.21 -> 1.14).
Ears now: tip 0.998, ratio 1.134 vs 1.13 target.

## Precision upgrade: 30x30 occupancy grid (per-cell, not per-band)
Sparse landmark comparison (10 bands, a dozen profile points) was the real
measuring problem -- too coarse to see localized errors. New instrument:
senses.occupancy_grid(), auto-fit to true bounding extent, dense enough to
catch what bands can't.

First pass found 3 distinctions bands never surfaced:
- rows 2-8: hair falls short 2-4 cols on the right (upper asymmetric bulge)
- rows 14-17: hair holds an unnatural flat plateau 2-3 cols too far LEFT
  while reference has already begun tapering there
- row 28: Collar alone (clean ray-ownership attribution) 3/2 cols too wide

Fixed row 28 (Collar scale 1.0->0.62): right edge now EXACT, left edge
4-off -> 1-off. Checking neighbor rows (never fix in isolation) found the
uniform scale overcorrected the torus's true equator (row 29: undershoots
[12,16] vs [10,19] target) -- filed, not buried. Hair distinctions (rows
2-8, 14-17) require pod-level edits across ~76 objects -- queued for a
dedicated pass rather than rushed this turn.

## Applied in practice (not hypothetical) -- 4 real findings, honestly tracked

1. Zone A (hair, rows 2-8 right shortfall): REAL, attributed to HairHero_1/Hair_05/
   Hair_13 via ray ownership + confirmed empty gap beyond them. Extended all three.
   Gaps closed 4->3, 2->1, 2->1, 2->1 (partial win). Row 2 (the peak) unmoved --
   HairHero_1's extension didn't reach that exact column; carried.

2. Zone B (rows 14-17, "flat plateau"): mis-attributed TWICE.
   - 1st guess (last turn): hair. Wrong -- z-band is below hair territory.
   - 2nd guess (this turn): cheek/face, based on z-height alone, NOT verified by
     attribution (SkinFused post-fuse can't attribute to sub-parts via ray-cast --
     fusion destroys that). Applied a Cheek/Face narrowing on the guess.
   - Verification: ZERO effect on the flagged rows. Regression check found real
     damage instead (eye_span diff 0.0->0.042, mouth 0.003->0.028, jaw/cheek
     0.013->0.152). REVERTED immediately.
   - Correct attribution (via stashed-part bounding-box containment, since fused
     ray-cast can't do it): EarR. The "excess" is the ear -- which was precisely
     calibrated last turn (1.134 vs 1.13 target) via a dedicated probe. Likely
     conclusion: my hand-digitized reference grid underestimated ear extent at
     this exact height -- a reference-reading limit, not a model defect. Held.

3. Discovered mid-repair: fusion (mesh_mind.fuse_group) erases original-part
   attribution for ray-based diagnosis. Bounding-box containment on the STASHED
   (hidden) parts is the correct diagnostic for post-fuse work; z-height alone
   is a guess and produced a real, damaging misfire above.

4. Discovered post-revert: the regression-check instrument itself is
   contaminated. width_at(z=-0.02), used as the W denominator for eye_span/
   mouth/jaw ratios, falls inside EarR's z-span (-0.44 to 0.16) ever since ears
   were widened. Every regression check since that fix has measured cheek+ear
   as one width. The 0.43/0.257/0.697 baseline predates the contamination --
   not wrong, but the wrong ruler now. Geometry (skin: 1 island, 0 non-manifold)
   confirmed sound; RATIO regression status is currently UNKNOWN, not passing,
   until W is redefined at a contamination-free height.

## Carried queue (honest, as of this pass)
- Redefine regression W measurement at a height outside all ear z-spans;
  re-verify true ratio status before trusting any prior "all passing" claim.
- Row 2 hair peak gap (HairHero_1 didn't move it) -- needs a different pod.
- Zone B ear-vs-reference-precision question unresolved -- do not adjust the
  ear again without a more careful direct re-look at that exact photo height.
- Collar equator (row 29) still undershoots, from two loops ago.
