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
