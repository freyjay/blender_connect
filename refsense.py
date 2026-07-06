# SPDX-License-Identifier: MIT
"""
blender-connect :: refsense.py -- engine v2 reference senses
The reference becomes a first-class measurable object: images are digitized
into the SAME sub-pixel silhouette structure the model uses, so both sides
meet in one data type. Doctrine (honesty-audit lesson): the reference is
re-measured every loop, never cached into constants.
"""
import bpy
import numpy as np


def _load_gray(source):
    """filepath or bpy image name -> (gray[h,w] top-down 0..1, alpha|None, name)."""
    if isinstance(source, str) and source in bpy.data.images:
        img = bpy.data.images[source]
    elif isinstance(source, str):
        img = bpy.data.images.load(source, check_existing=True)
    else:
        img = source
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]
    return px[..., :3].mean(-1), (px[..., 3] if px[..., 3].min() < 0.99 else None), img.name


def _foreground(gray, alpha):
    """Foreground-ness in [0,1]: alpha if present, else distance from
    border-sampled background."""
    if alpha is not None:
        return alpha
    border = np.concatenate([gray[0], gray[-1], gray[:, 0], gray[:, -1]])
    g = np.abs(gray - float(np.median(border)))
    m = g.max()
    return g / m if m > 0 else g


def digitize_scalar(g, threshold=0.5, flip_x=False):
    """Per-row sub-pixel L/R edges of a foreground array (top-down).
    Returns silhouette-shaped dict in PIXEL units, v up-positive."""
    h, w = g.shape
    if flip_x:
        g = g[:, ::-1]
    left, right, vs = [], [], []
    for r in range(h):
        row = g[r]
        on = row >= threshold
        vs.append(float(h - 1 - r))
        if not on.any():
            left.append(None); right.append(None)
            continue
        i0 = int(np.argmax(on))
        i1 = int(w - 1 - np.argmax(on[::-1]))
        if i0 > 0 and row[i0] != row[i0 - 1]:
            L = (i0 - 1) + (threshold - row[i0 - 1]) / (row[i0] - row[i0 - 1])
        else:
            L = float(i0)
        if i1 < w - 1 and row[i1] != row[i1 + 1]:
            R = (i1 + 1) - (threshold - row[i1 + 1]) / (row[i1] - row[i1 + 1])
        else:
            R = float(i1)
        left.append(float(L)); right.append(float(R))
    return {"left": left, "right": right, "v": vs, "w": w, "h": h,
            "coverage": round(float(np.mean(g >= threshold)), 4), "units": "pixel"}


def digitize(source, threshold=0.5, flip_x=False):
    """Image -> sub-pixel silhouette. FRONT-photo convention matches the
    model's FRONT view (+u = screen right = subject's left); flip_x if the
    photo is mirrored."""
    gray, alpha, name = _load_gray(source)
    d = digitize_scalar(_foreground(gray, alpha), threshold, flip_x)
    d["source"] = name
    return d


def preview(dig, width=64, lines=44):
    """ASCII of the digitization -- verify the instrument saw the subject,
    not the background, BEFORE trusting any comparison."""
    step = max(1, len(dig["v"]) // lines)
    out = []
    for i in range(0, len(dig["v"]), step):
        L, R = dig["left"][i], dig["right"][i]
        if L is None:
            out.append("")
            continue
        a = int(L / dig["w"] * width)
        b = int(R / dig["w"] * width)
        out.append(" " * a + "#" * max(1, b - a))
    return "\n".join(out)


def rasterize(sil, px=512, margin=0.05):
    """Ground-truth generator (calibration only): render a silhouette dict to
    a coverage-weighted grayscale array. Proves digitize() against known
    geometry before any real photo is trusted."""
    Ls = [x for x in sil["left"] if x is not None]
    Rs = [x for x in sil["right"] if x is not None]
    vs = [v for v, L in zip(sil["v"], sil["left"]) if L is not None]
    u_lo, u_hi, v_lo, v_hi = min(Ls), max(Rs), min(vs), max(vs)
    span = max(u_hi - u_lo, v_hi - v_lo) * (1 + 2 * margin)
    cu, cv = (u_lo + u_hi) / 2, (v_lo + v_hi) / 2
    pix = span / px
    vv = np.array(vs); LL = np.array(Ls); RR = np.array(Rs)
    o = np.argsort(vv)
    vv, LL, RR = vv[o], LL[o], RR[o]
    g = np.zeros((px, px), dtype=np.float32)
    for r in range(px):
        v = cv + span / 2 - (r + 0.5) * pix
        if v < vv[0] or v > vv[-1]:
            continue
        L = float(np.interp(v, vv, LL))
        R = float(np.interp(v, vv, RR))
        c0 = (L - (cu - span / 2)) / pix
        c1 = (R - (cu - span / 2)) / pix
        a, b = int(np.floor(c0)), int(np.ceil(c1)) - 1
        for c in range(max(a, 0), min(b, px - 1) + 1):
            g[r, c] = min(max(min(c + 1.0, c1) - max(float(c), c0), 0.0), 1.0)
    return {"gray": g, "pixel_size": pix, "center": (cu, cv), "span": span}
