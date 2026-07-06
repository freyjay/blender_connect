# SPDX-License-Identifier: MIT
"""
blender-connect :: engine2.py -- v2: direct reference -> product translation
Pipeline: sub-pixel silhouettes on BOTH sides -> canonical registration
(solved, never assumed) -> continuous signed error field -> clusters above a
MEASURED combined floor become the distinctions -> prescription translates
each into owning parts + world-unit magnitudes -> verify_pass re-measures the
identical field after edits. v1 (eye/senses) remains the substrate; v2
replaces landmark spot-checks with error fields and cached constants with
re-measurable references. Masterwork check is a boolean, not a vibe.
"""
import bpy
import numpy as np


def _nan_max(a):
    a = a[~np.isnan(a)]
    return float(np.max(a)) if a.size else 0.0


def canonicalize(sil, v_top=None, v_bot=None, u_mid=None):
    """Solve registration: crown->bottom span maps to [-1, +1]; u centered on
    the median midline of the central 60% of occupied rows (hair spikes and
    collars excluded from the vote). D1 doctrine: same span, always."""
    occ = [(L, R, v) for L, R, v in zip(sil["left"], sil["right"], sil["v"])
           if L is not None]
    if not occ:
        return None
    vs = [v for _, _, v in occ]
    top = v_top if v_top is not None else max(vs)
    bot = v_bot if v_bot is not None else min(vs)
    s = (top - bot) / 2.0
    v0 = (top + bot) / 2.0
    if u_mid is None:
        k = len(occ)
        mids = sorted((L + R) / 2 for L, R, _ in occ[int(k * 0.2):int(k * 0.8)])
        u0 = mids[len(mids) // 2] if mids else 0.0
    else:
        u0 = u_mid
    return {"L": [(l - u0) / s for l, _, _ in occ],
            "R": [(r - u0) / s for _, r, _ in occ],
            "v": [(v - v0) / s for _, _, v in occ],
            "transform": {"u0": round(u0, 4), "v0": round(v0, 4), "s": round(s, 5)},
            "units": sil.get("units", "world")}


def resample(canon, K=96, lo=-0.98, hi=0.98):
    """Common canonical row grid; linear interpolation; NaN outside data."""
    v = np.array(canon["v"], dtype=float)
    L = np.array(canon["L"], dtype=float)
    R = np.array(canon["R"], dtype=float)
    o = np.argsort(v)
    v, L, R = v[o], L[o], R[o]
    grid = np.linspace(lo, hi, K)
    return {"v": grid,
            "L": np.interp(grid, v, L, left=np.nan, right=np.nan),
            "R": np.interp(grid, v, R, left=np.nan, right=np.nan)}


def _mk_cluster(side, idxs, e, v):
    vals = e[idxs]
    mean = float(np.mean(vals))
    dv = float(v[1] - v[0]) if len(v) > 1 else 1.0
    excess = (mean > 0) if side == "right" else (mean < 0)
    return {"side": side,
            "v_range": (round(float(v[idxs[0]]), 3), round(float(v[idxs[-1]]), 3)),
            "rows": len(idxs), "mean_err": round(mean, 4),
            "max_err": round(float(vals[np.argmax(np.abs(vals))]), 4),
            "area": round(float(np.sum(np.abs(vals)) * dv), 5),
            "direction": "excess (pull in)" if excess else "deficit (push out)"}


def error_field(model_canon, ref_canon, K=96, floor=None):
    """Signed sub-pixel error at K canonical heights, both edges.
    e = model - ref. Right edge: e>0 = excess. Left edge: e<0 = excess.
    With floor: contiguous |e|>floor runs become ranked clusters -- the
    distinctions, generated instead of eyeballed."""
    m = resample(model_canon, K)
    r = resample(ref_canon, K)
    eL = m["L"] - r["L"]
    eR = m["R"] - r["R"]
    rows = [{"v": round(float(v), 4),
             "eL": None if np.isnan(a) else round(float(a), 4),
             "eR": None if np.isnan(b) else round(float(b), 4)}
            for v, a, b in zip(m["v"], eL, eR)]
    field = {"rows": rows, "K": K,
             "abs_sum": round(float(np.nansum(np.abs(eL)) + np.nansum(np.abs(eR))), 4),
             "abs_max": round(max(_nan_max(np.abs(eL)), _nan_max(np.abs(eR))), 4)}
    if floor is None:
        return field
    if isinstance(floor, dict):
        fr = np.array(floor["per_row"], dtype=float)
        field["floor"] = {"median": floor["median"], "p90": floor["p90"],
                          "max": floor["max"]}
    else:
        fr = np.full(K, float(floor))
        field["floor"] = float(floor)
    clusters = []
    for side, e in (("left", eL), ("right", eR)):
        run = []
        for i, val in enumerate(e):
            if (not np.isnan(val)) and abs(val) > fr[i]:
                run.append(i)
            elif run:
                clusters.append(_mk_cluster(side, run, e, m["v"]))
                run = []
        if run:
            clusters.append(_mk_cluster(side, run, e, m["v"]))
    clusters.sort(key=lambda c: -c["area"])
    field["clusters"] = clusters
    return field


def floor2(view="FRONT", frame=None, rows=128, ref_dig=None, K=96):
    """Combined v2 floor as a FIELD, not a scalar. Per-canonical-row model
    wobble (three row densities, elementwise max, running-max smoothed,
    floored at its own median), doubled when a digitized reference is in
    play (both sides suffer the same slope-driven sampling ambiguity), plus
    the reference half-pixel term. Smooth regions get a tight floor;
    ambiguous rows (hair crevices, near-horizontal silhouette) get an honest
    loose one -- one bad row no longer taxes the whole figure."""
    import senses
    base = canonicalize(senses.silhouette(view, frame, rows))
    alts = [canonicalize(senses.silhouette(view, frame, rows + d))
            for d in (17, -17)]
    rb = resample(base, K)
    wob = np.zeros(K)
    for a in alts:
        ra = resample(a, K)
        for side in ("L", "R"):
            d = np.abs(rb[side] - ra[side])
            d[np.isnan(d)] = 0.0
            wob = np.maximum(wob, d)
    sm = wob.copy()
    sm[1:] = np.maximum(sm[1:], wob[:-1])
    sm[:-1] = np.maximum(sm[:-1], wob[1:])
    pos = sm[sm > 0]
    med = float(np.median(pos)) if pos.size else 0.0
    sm = np.maximum(sm, med)
    ref_term = 0.0
    mult = 1.0
    if ref_dig is not None:
        ref_term = 0.5 / canonicalize(ref_dig)["transform"]["s"]
        mult = 2.0
    per_row = mult * sm + ref_term
    return {"per_row": [round(float(x), 5) for x in per_row],
            "median": round(float(np.median(per_row)), 5),
            "p90": round(float(np.percentile(per_row, 90)), 5),
            "max": round(float(per_row.max()), 5),
            "ref_term": round(ref_term, 5), "K": K}

def prescribe(field, model_canon, view="FRONT", stash=None, margin=0.02, top=6):
    """Translate top clusters into a worklist: owning stashed parts, world
    coordinates, world-unit magnitudes, direction. The reference speaking
    in edit units."""
    import eye
    from mathutils import Vector
    t = model_canon["transform"]
    _f, right, up_s = eye._basis(view)
    if stash is None:
        stash = [o.name for o in bpy.data.objects
                 if o.type == "MESH" and o.hide_get()]
    boxes = {}
    for name in stash:
        o = bpy.data.objects.get(name)
        if not o:
            continue
        us, vs = [], []
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            us.append(w.dot(right)); vs.append(w.dot(up_s))
        boxes[name] = (min(us), max(us), min(vs), max(vs))
    m = resample(model_canon, field["K"])
    out = []
    for cl in field.get("clusters", [])[:top]:
        v_mid = (cl["v_range"][0] + cl["v_range"][1]) / 2
        i = int(np.argmin(np.abs(m["v"] - v_mid)))
        u_c = m["L"][i] if cl["side"] == "left" else m["R"][i]
        if np.isnan(u_c):
            continue
        u_w = float(u_c) * t["s"] + t["u0"]
        v_w = v_mid * t["s"] + t["v0"]
        owners = []
        for name, (u0, u1, v0, v1) in boxes.items():
            inside = (u0 - margin <= u_w <= u1 + margin) and \
                     (v0 - margin <= v_w <= v1 + margin)
            du = max(u0 - u_w, u_w - u1, 0.0)
            dv = max(v0 - v_w, v_w - v1, 0.0)
            d = (du * du + dv * dv) ** 0.5
            if inside or d < 0.15:
                owners.append((0 if inside else 1, round(d, 4), name))
        owners.sort()
        out.append({"cluster": cl,
                    "world": {"u": round(u_w, 4), "v": round(v_w, 4),
                              "v_span": (round(cl["v_range"][0] * t["s"] + t["v0"], 3),
                                         round(cl["v_range"][1] * t["s"] + t["v0"], 3)),
                              "mean_err": round(cl["mean_err"] * t["s"], 4),
                              "max_err": round(cl["max_err"] * t["s"], 4)},
                    "owners": [{"part": n, "inside": f == 0, "gap": d}
                               for f, d, n in owners[:3]]})
    return out


def compare(ref_dig, view="FRONT", frame=None, rows=128, K=96, stash=None):
    """THE v2 entry point: digitized reference -> registration -> error field
    -> ranked clusters -> prescription. Re-measures BOTH sides fresh every
    call. masterwork == True when zero clusters clear the floor."""
    import senses
    mc = canonicalize(senses.silhouette(view, frame, rows))
    rc = canonicalize(ref_dig)
    fl = floor2(view, frame, rows, ref_dig, K)
    field = error_field(mc, rc, K, floor=fl)
    s = mc["transform"]["s"]
    return {"floor": {"median": fl["median"], "p90": fl["p90"],
                      "max": fl["max"], "ref_term": fl["ref_term"],
                      "median_world": round(fl["median"] * s, 5),
                      "p90_world": round(fl["p90"] * s, 5)},
            "field_abs_max": field["abs_max"],
            "field_abs_max_world": round(field["abs_max"] * s, 4),
            "n_clusters_above_floor": len(field.get("clusters", [])),
            "clusters": field.get("clusters", []),
            "prescriptions": prescribe(field, mc, view=view, stash=stash),
            "masterwork": len(field.get("clusters", [])) == 0,
            "model_transform": mc["transform"],
            "field": field}


def verify_pass(ref_dig, pre, view="FRONT", frame=None, rows=128, K=96):
    """Same-field re-measure after edits: per-cluster deltas (matched by
    side + v-mid), new clusters, resolved clusters, registration drift.
    A fix that grows other clusters is a regression, not a fix."""
    post = compare(ref_dig, view, frame, rows, K)
    drift = {k: round(post["model_transform"][k] - pre["model_transform"][k], 5)
             for k in ("u0", "v0", "s")}
    def key(c):
        return (c["side"], round((c["v_range"][0] + c["v_range"][1]) / 2, 1))
    pre_map = {key(c): c for c in pre["clusters"]}
    post_keys = {key(c) for c in post["clusters"]}
    matched, new = [], []
    for c in post["clusters"]:
        k = key(c)
        if k in pre_map:
            matched.append({"side": c["side"], "v_mid": k[1],
                            "area_pre": pre_map[k]["area"],
                            "area_post": c["area"],
                            "delta": round(c["area"] - pre_map[k]["area"], 5)})
        else:
            new.append(c)
    return {"registration_drift": drift, "matched": matched,
            "new_clusters": new,
            "resolved": [k for k in pre_map if k not in post_keys],
            "post": post}


def overlay(model_canon, ref_canon, width=64, K=48):
    """ASCII overlay in the canonical frame: '#' both, 'M' model-only,
    'R' reference-only. The direct comparison, human-verifiable."""
    m = resample(model_canon, K)
    r = resample(ref_canon, K)
    lo = np.nanmin([np.nanmin(m["L"]), np.nanmin(r["L"])])
    hi = np.nanmax([np.nanmax(m["R"]), np.nanmax(r["R"])])
    out = []
    for i in range(K - 1, -1, -1):
        line = []
        for c in range(width):
            u = lo + (c + 0.5) * (hi - lo) / width
            inm = (not np.isnan(m["L"][i])) and m["L"][i] <= u <= m["R"][i]
            inr = (not np.isnan(r["L"][i])) and r["L"][i] <= u <= r["R"][i]
            line.append("#" if (inm and inr) else "M" if inm else "R" if inr else " ")
        out.append("".join(line))
    return "\n".join(out)
