"""Draw wall 9, a stone wall gone to moss and fungus (`@page wall-9`), as images/wall-9.png.

    python3 scripts/wall-moss.py         (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the shadows, drips and blurs are
circular convolutions, the courses and joints are periodic curves on the
tile's own torus, and every growth is drawn with wrap-around.

What it draws, back to front:
1. The stone: roughly coursed rubble. Courses of uneven height, their beds
   wavering; in each, stones of uneven length, their joints leaning, some
   split into two (a smaller stone over a larger, or two side by side). Each
   stone is a rounded, chipped block, a little its own colour (grey, buff,
   blue-grey), with a worn face: bedding lines, pits, stains. It is lit from
   the upper left, so each stone's top-left arris catches the light and the
   joints under its foot lie in its shadow. The joints are a lime mortar,
   sandy and recessed.
2. Lichen rosettes on the faces: pale green-grey leafy ones, grey crusts
   cracked into islands, ochre crusts, each lobed at its rim and dying back
   at the centre, some with dark or rusty fruiting discs.
3. Mould: dark speckled blooms, and a green algal film where it is damp.
4. Damp streaks running down from the joints.
5. Moss: cushions, heaviest in the joints, along the stones' top edges and
   in the damp patches, bumpy and lit, olive to yellow-green (a bluer, flatter
   kind where it is wettest), with spore capsules standing up out of it.
6. Roots and creeper tendrils wandering over the stone, a few in leaf.
7. Bracket fungi in tiers, growing out of the joints: zoned fans with a
   pale rim, a dark underside and a shadow on the wall below.
8. Clusters of small mushrooms standing in the joints.
9. Grime over everything, and the whole drawn back toward a mid tone, so a
   white sheet pasted on it stays the focus.
It is then quantised to an exact palette, as the other walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is).

At DPI (300, the print bar) the tile is 18in x 12in, wider than a spread
and taller than a page, so a spread shows no repeat. No damp patch or stain
is larger than FEATURE (8in). Its courses run across the tile, so
wall-tiles.py anchors it to the sheet, not the text area, and offsets a right
page by the left page's width: a spread is one wall, its courses unbroken at
the spine.

It was first drawn at 240 DPI, and every length in it is scaled by S (300 /
240) from there, so it prints the same at the finer resolution, with finer
detail rather than an upsampled one. Only the soft edge a shape is drawn with
(a smoothstep under a pixel wide, there to antialias it) stays a pixel wide,
so edges come out crisper. The noise's coarse frequencies, all the 240 DPI
tile had, are drawn first from the same seeds as before, so the wall keeps its
layout; the new ones add only finer grain.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
DPI = 300                   # px an inch: the print bar
S = DPI / 240               # px per px of the 240 DPI tile it was first drawn at: every length below is scaled by it
NW, NH = round(18 * DPI), round(12 * DPI)   # px; 18in x 12in: wider than a spread and taller than a page, so a spread shows no repeat
NW0, NH0 = round(NW / S), round(NH / S)     # the tile at 240 DPI, where the noise's coarse frequencies are drawn
FEATURE = 8 * DPI           # px (8in): the largest damp patch or stain, whatever the tile's size
COURSE = (150 * S, 300 * S) # a course's height, px
LENGTH = (1.1, 2.7)         # a stone's length, in course heights
MORTAR = 9.0 * S            # half a joint's width, px (it varies by +-4 * S)
CSS = 4                     # the hairline cracks are drawn at CSS x and boxed down: 1.25px lines
MOSS = 0.30                 # the share of the wall under moss
SEED = 9
SHADE = 1.0                 # the whole tile; its darkest moss and shadow stay well under DriveThruRPG's 240% TAC
CALM = 0.80                 # every tone is drawn this far back toward the wall's mean: a background, not a picture

rng = np.random.default_rng(SEED)
F32 = np.float32

yy, xx = np.mgrid[0:NH, 0:NW]
FY = np.fft.fftfreq(NH).astype(F32)[:, None]
FX = np.fft.rfftfreq(NW).astype(F32)[None, :]
F2 = FX * FX + FY * FY


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], F32) / 255


def px(v):
    """A whole number of px for a length v given in 240 DPI px (a shift, a patch's reach)."""
    return int(math.floor(v * S + 0.5))


def white_spec(r):
    """The spectrum (rfft2) of white noise over the tile. Its coarse part,
    every frequency the 240 DPI tile had, is drawn first, as it was then, so a
    field keeps its layout; the finer frequencies are drawn after it."""
    coarse = np.fft.rfft2(r.standard_normal((NH0, NW0), dtype=F32)) * F32(S)   # S = sqrt(NH * NW / (NH0 * NW0)): the same power a bin
    spec = np.fft.rfft2(r.standard_normal((NH, NW), dtype=F32))
    iy = np.fft.fftfreq(NH0, 1 / NH0).astype(int) % NH
    spec[iy, :NW0 // 2 + 1] = coarse
    return spec


def noise(beta, stretch=(1.0, 1.0), seed=None, feature=FEATURE, band=None, lo=None):
    """Periodic 1/f^beta noise over the tile, as a z-score (mean 0, sd 1).
    `stretch` (sx, sy) > 1 elongates it along that axis; `band` (px) keeps
    only features near that size; `lo` (px) drops features smaller than it."""
    r = np.random.default_rng(seed)
    fy = FY * stretch[1]
    fx = FX * stretch[0]
    f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)
    spec = white_spec(r) / f ** beta
    if band:
        spec *= np.exp(-((f * band - 1) ** 2) * 3)
    if lo:
        spec *= np.exp(-(f * lo) ** 2)
    out = np.fft.irfft2(spec, s=(NH, NW)).astype(F32)
    out -= out.mean()
    return out / out.std()


def blur(m, sigma, dx=0.0, dy=0.0):
    """Gaussian blur on the torus, the result shifted by (dx, dy)."""
    k = np.exp(-2 * np.pi ** 2 * sigma * sigma * F2) * np.exp(-2j * np.pi * (FX * dx + FY * dy))
    return np.fft.irfft2(np.fft.rfft2(m) * k, s=(NH, NW)).astype(F32)


def circ_conv(img, kernel):
    return np.fft.irfft2(np.fft.rfft2(img) * np.fft.rfft2(kernel), s=(NH, NW)).astype(F32)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t, F32)
    if t.ndim == 2:
        t = t[..., None]
    return a + (b - a) * t


def wave(n, amp, r, kmax=9):
    """A periodic wobble of length n: a few sines at whole frequencies."""
    t = np.arange(n) / n
    out = np.zeros(n)
    for k in range(1, kmax + 1):
        out += r.normal() / k ** 1.3 * np.sin(2 * np.pi * k * t + r.uniform(0, 2 * np.pi))
    return (amp * out / out.std()).astype(F32)


def relief(h, k):
    """Light from the upper left on a height field: > 1 lit, < 1 in shade.
    The slope is taken over 2px, so k carries an S: the same slope per inch."""
    gx = np.roll(h, 1, 1) - np.roll(h, -1, 1)
    gy = np.roll(h, 1, 0) - np.roll(h, -1, 0)
    return 1 + k * (gx + gy)


# ── 1. the stone: courses, stones, joints ──────────────────────────────────────
heights = []
while sum(heights) < NH:
    heights.append(rng.uniform(*COURSE))
heights = np.array(heights) * NH / sum(heights)
tops = np.concatenate([[0], np.cumsum(heights)])[:-1]
K = len(heights)
beds = [tops[k] + np.clip(wave(NW, 11 * S, rng), -40 * S, 40 * S) for k in range(K)]   # each course's bed line, y(x)

E = np.full((NH, NW), -99 * S, F32)       # distance in from the stone's edge (its rounded box), px
DT = np.zeros((NH, NW), F32)          # distance down from the stone's top edge, px
SID = np.zeros((NH, NW), np.int32)    # which stone
x = np.arange(NW)[None, :].astype(F32)
n_ids = 0
bed_lines = []                        # (y(x) of the top of the stones under it, for mushrooms)
for k in range(K):
    top = beds[k]
    bot = beds[(k + 1) % K] + (NH if k + 1 == K else 0)
    hk = heights[k]
    widths = []
    while sum(widths) < NW:
        widths.append(rng.uniform(*LENGTH) * hk)
    widths = np.array(widths) * NW / sum(widths)
    jx = (np.concatenate([[0], np.cumsum(widths)])[:-1] + rng.uniform(0, NW)) % NW
    J = len(jx)
    slant = rng.normal(0, 0.14, J) * hk
    split = rng.random(J) < 0.30                       # a stone in two, one over the other
    vsp = rng.uniform(0.38, 0.62, J)
    vtilt = rng.normal(0, 0.10, J)
    split2 = split & (rng.random(J) < 0.45)            # and its upper part in two again, side by side
    usp = rng.uniform(0.35, 0.65, J)
    y0, y1 = int(tops[k]) - px(48), int(tops[k] + hk) + px(48)
    ya = np.arange(y0, y1)[:, None].astype(F32)
    inside = (ya >= top[None, :]) & (ya < bot[None, :])
    hh = (bot - top)[None, :]
    vp = ya - top[None, :]
    v = vp / hh
    d = np.empty((J, len(ya), NW), F32)
    for j in range(J):
        p = jx[j] + slant[j] * (v - 0.5)
        d[j] = (x - p + NW / 2) % NW - NW / 2
    dl_all = np.where(d >= 0, d, np.inf)
    s = np.argmin(dl_all, 0)
    dl = np.take_along_axis(dl_all, s[None], 0)[0]
    dr = np.where(d < 0, -d, np.inf).min(0)
    del d, dl_all
    u = dl / (dl + dr)
    dt, db = vp.copy() * np.ones_like(u), (hh - vp) * np.ones_like(u)
    sub = np.zeros_like(s)
    ysp = (vsp[s] + vtilt[s] * (u - 0.5)) * hh
    sp = split[s]
    upper = sp & (vp < ysp)
    lower = sp & ~upper
    db = np.where(upper, ysp - vp, db)
    dt = np.where(lower, vp - ysp, dt)
    sub = np.where(lower, 1, sub)
    sp2 = split2[s] & upper
    xs = usp[s] * (dl + dr)
    left = sp2 & (dl < xs)
    dr = np.where(left, xs - dl, dr)
    dl = np.where(sp2 & ~left, dl - xs, dl)
    sub = np.where(sp2 & ~left, 2, sub)
    kk = 16.0 * S                                       # corner rounding, px
    m = np.minimum.reduce([dl, dr, dt, db])
    e = m - kk * np.log(np.exp(-(dl - m) / kk) + np.exp(-(dr - m) / kk) + np.exp(-(dt - m) / kk) + np.exp(-(db - m) / kk))
    rows = (np.arange(y0, y1) % NH)[:, None] * np.ones((1, NW), int)
    cols = np.ones((y1 - y0, 1), int) * np.arange(NW)[None, :]
    E[rows[inside], cols[inside]] = e[inside]
    DT[rows[inside], cols[inside]] = dt[inside]
    SID[rows[inside], cols[inside]] = (n_ids + s * 3 + sub)[inside]
    n_ids += J * 3
    bed_lines.append(top)
    print(f"  course {k + 1}/{K}  {J} stones", flush=True)

# the edges: irregular, chipped at the arrises
lump = noise(2.4, seed=SEED + 1, feature=220 * S, lo=14 * S)         # an outline that wanders: rubble, not ashlar
edge_n = noise(1.2, seed=SEED + 24, lo=2.5 * S)
chip_n = noise(1.4, seed=SEED + 2, feature=90 * S, lo=5 * S)         # bites out of the arris
E = E + (9.0 * lump + 1.3 * edge_n - 12.0 * smooth(chip_n, 1.3, 2.3) * np.exp(-np.maximum(E - MORTAR, 0) / (18 * S))) * S
MW = MORTAR + 4.0 * S * noise(1.8, seed=SEED + 3, feature=600 * S)
stone = smooth(E, MW - 0.8, MW + 0.8)                   # antialiased over 1.6px
inset = E - MW                                          # px in from the stone's visible edge

# each stone its own colour and weathering
STONES = [hexc(c) for c in ("#b4afa3", "#aeaca4", "#b9ad96", "#a8a59c", "#b1aa9b", "#a9aba6", "#b6b0a2")]
pick = rng.integers(0, len(STONES), n_ids)
tone = rng.uniform(0.93, 1.05, n_ids).astype(F32)
colours = np.stack([STONES[i] for i in pick]) * tone[:, None]
base = colours[SID]

mottle = noise(2.0, seed=SEED + 4)
strata = noise(1.3, stretch=(1.0, 0.08), seed=SEED + 5, feature=400 * S, lo=5 * S)   # bedding, along the course
grain = noise(0.5, seed=SEED + 6)
pits_n = noise(0.3, seed=SEED + 7)
face_n = noise(1.8, seed=SEED + 8, feature=300 * S, lo=10 * S)
stain = noise(1.9, seed=SEED + 9)
face = 1 + 0.035 * mottle + 0.015 * strata + 0.02 * grain + 0.03 * stain
face *= 1 - 0.18 * smooth(pits_n, 2.0, 2.8)

# a dome on each stone, worn round at the arris, bumped by its face
H = np.sqrt(smooth(inset, 0, 40 * S)) + 0.12 * face_n * smooth(inset, 0, 20 * S)
H = np.where(stone > 0.5, H, -0.15 + 0.02 * grain)
lit = np.clip(relief(H.astype(F32), 2.2 * S), 0.72, 1.22)
img = base * (face * lit)[..., None]

# the joints: lime mortar, sandy, recessed, in the shadow of the stones above-left
MORTAR_C = hexc("#a39c8c")
sand = noise(0.2, seed=SEED + 10)
mortar = MORTAR_C * (0.94 + 0.05 * sand + 0.03 * mottle)[..., None]
cast = blur(stone, 3.0 * S, 5 * S, 6 * S)
mortar *= (1 - 0.30 * np.clip(cast - stone, 0, 1) - 0.10 * smooth(-inset, 0, 6 * S))[..., None]
img = mix(mortar, img, stone)
del base, mortar, lit, face, cast

# a few cracks across the faces
crack_m = Image.new("L", (NW * CSS, NH * CSS), 0)
cd = ImageDraw.Draw(crack_m)
for _ in range(26):
    px_, py_, a = rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, 2 * np.pi)
    pts = [(px_, py_)]
    for _ in range(int(rng.integers(5, 16))):
        a += rng.normal(0, 0.45)
        px_, py_ = px_ + rng.uniform(6 * S, 14 * S) * np.cos(a), py_ + rng.uniform(6 * S, 14 * S) * np.sin(a)
        pts.append((px_, py_))
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            cd.line([((p + ox) * CSS, (q + oy) * CSS) for p, q in pts], fill=255, width=round(S * CSS))
cr = np.asarray(crack_m.resize((NW, NH), Image.BOX), F32) / 255 * stone
img *= (1 - 0.30 * cr + 0.08 * np.clip(np.roll(cr, (1, 1), (0, 1)) - cr, 0, 1))[..., None]
del crack_m, cr

# ── fields the growth follows ────────────────────────────────────────────────────
damp = noise(2.1, seed=SEED + 11)                       # wet patches, z-score
joint = 1 - smooth(inset, -2 * S, 26 * S)               # 1 in a joint, fading over the stone's edge
topedge = stone * np.exp(-np.maximum(DT - MW, 0) / (34 * S))  # a stone's top edge: a ledge that holds water
footedge = stone * smooth(inset, 0, 8 * S) * (1 - smooth(inset, 8 * S, 30 * S)) * (DT > 60 * S)
fine = noise(0.8, seed=SEED + 12)
clump2 = noise(1.4, seed=SEED + 18, feature=260 * S)


# ── drawing helpers: a small patch round a point, on the torus ──────────────────
def patch(x0, y0, rx, ry=None):
    ry = rx if ry is None else ry
    sy, sx = np.mgrid[int(y0) - ry:int(y0) + ry + 1, int(x0) - rx:int(x0) + rx + 1]
    return (sy % NH, sx % NW), (sx - x0).astype(F32), (sy - y0).astype(F32)


def put(ix, a, col):
    sub = img[ix]
    img[ix] = sub + (col - sub) * a[..., None]


def lblur(a, r):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), F32) / 255


def lshift(a, dx, dy):
    return np.roll(a, (dy, dx), (0, 1))


# galletting: small stones pressed into the wide joints
PEBBLES = [hexc(c) for c in ("#a9a497", "#b3ac9c", "#9f9d95", "#b0a690")]
wide = np.flatnonzero((inset[::3, ::3] < -7 * S) & (inset[::3, ::3] > -60 * S))
n_peb = 0
for c in rng.choice(wide, min(len(wide), 1400), replace=False):
    sy_, sx_ = divmod(c, (NW + 2) // 3)
    x0, y0 = sx_ * 3 + rng.uniform(0, 3), sy_ * 3 + rng.uniform(0, 3)
    r = rng.uniform(3.5 * S, 8.5 * S) * min(1.0, -float(inset[int(y0) % NH, int(x0) % NW]) / (10 * S))
    if r < 3 * S:
        continue
    ix, dx, dy = patch(x0, y0, int(r * 1.6) + px(4))
    ang, el = rng.uniform(0, np.pi), rng.uniform(0.6, 1.0)
    X = (dx * np.cos(ang) + dy * np.sin(ang)) / r
    Y = (-dx * np.sin(ang) + dy * np.cos(ang)) / (r * el)
    rr = X * X + Y * Y
    a = smooth((1 - np.sqrt(rr)) * r * el, -0.7, 0.7) * (1 - stone[ix])
    sh = lblur(lshift(a, px(2), px(2)), 1.2 * S)
    img[ix] *= (1 - 0.35 * sh * (1 - a))[..., None]
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    lit = 0.80 + 0.35 * np.clip((-dx - dy) / (r * 1.41) * 0.6 + nz * 0.5, 0, 1)
    put(ix, a, PEBBLES[int(rng.integers(0, len(PEBBLES)))] * rng.uniform(0.92, 1.04) * lit[..., None])
    n_peb += 1
print(f"  {n_peb} pebbles", flush=True)

# ── 2. lichen rosettes on the faces ─────────────────────────────────────────────
LICHENS = {   # kind: (centre, body, rim, fruit), weight
    "leafy": ((hexc("#a3a88f"), hexc("#b3b99c"), hexc("#c3c7ad"), hexc("#7e7a5c")), 0.34),
    "grey": ((hexc("#aeaca2"), hexc("#bdbcb2"), hexc("#cac8bd"), hexc("#5f5b52")), 0.30),
    "ochre": ((hexc("#b39a63"), hexc("#bfa66d"), hexc("#c9b483"), hexc("#8d6a3e")), 0.22),
    "sage": ((hexc("#98a08a"), hexc("#a6ad94"), hexc("#b4b9a2"), hexc("#6c6b55")), 0.14),
}
kinds = list(LICHENS)
kw = np.array([LICHENS[k][1] for k in kinds])
lichen_n = noise(1.2, seed=SEED + 13, feature=60 * S, lo=3 * S)
areole = noise(0.6, seed=SEED + 14, band=7 * S)


def rosette(x0, y0, R, kind):
    (cc, cb, crm, cf), _ = LICHENS[kind]
    Rb = int(R * 1.35) + px(3)
    ix, dx, dy = patch(x0, y0, Rb)
    d = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    k = int(rng.integers(7, 15))
    ph = rng.uniform(0, 2 * np.pi, 3)
    edge = R * (1 + 0.10 * np.sin(k * th + ph[0]) + 0.05 * np.sin(2 * k * th + ph[1]) + 0.08 * np.sin(2 * th + ph[2])) \
        + 0.10 * R * lichen_n[ix]
    sdf = edge - d
    a = smooth(sdf, -0.8, 0.8) * stone[ix]
    t = d / np.maximum(edge, 1)
    col = mix(cc, cb, smooth(t, 0.2, 0.6))
    col = mix(col, crm, smooth(t, 0.78, 0.97))
    if kind in ("grey", "ochre"):                       # a crust, cracked into islands
        col *= (1 - 0.12 * smooth(-areole[ix], 0.9, 1.6))[..., None]
    else:                                               # leafy: each lobe lit along its crest, ridged in rings
        col *= (1 + 0.06 * np.sin(k * th + ph[0]) * smooth(t, 0.45, 0.95) + 0.03 * np.sin(2 * np.pi * 4 * t + ph[1]))[..., None]
    if R > 22 * S and rng.random() < 0.55:              # old centre dying back
        a *= 1 - smooth(0.42 - t + 0.15 * lichen_n[ix], 0.0, 0.12) * 0.85
    a *= 0.88
    put(ix, a, col)
    rim = smooth(sdf, -0.5, 0.5) * (1 - smooth(sdf, 1.0 * S, 2.2 * S)) * stone[ix]
    img[ix] *= (1 - 0.12 * rim)[..., None]
    if rng.random() < 0.6:                              # fruiting discs
        for _ in range(int(rng.integers(3, 3 + R // (4 * S)))):
            rr, aa = R * 0.6 * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
            fx, fy = rr * np.cos(aa), rr * np.sin(aa)
            fr = rng.uniform(1.6 * S, 3.4 * S)
            disc = smooth(fr - np.hypot(dx - fx, dy - fy), -0.6, 0.6) * a
            put(ix, disc * 0.9, cf)


face_ok = (stone > 0.9) & (inset > 6 * S)
n_lichen = 0
for _ in range(2600):
    if n_lichen >= 700:
        break
    if rng.random() < 0.35 and n_lichen:                # colonies: next to the last one
        x0, y0 = lx + rng.normal(0, 40 * S), ly + rng.normal(0, 40 * S)
    else:
        x0, y0 = rng.uniform(0, NW), rng.uniform(0, NH)
    xi, yi = int(x0) % NW, int(y0) % NH
    if not face_ok[yi, xi] or damp[yi, xi] > 1.0:
        continue
    R = float(np.clip(rng.lognormal(np.log(20 * S), 0.5), 5 * S, 75 * S))
    rosette(x0, y0, R, kinds[rng.choice(len(kinds), p=kw / kw.sum())])
    lx, ly = x0, y0
    n_lichen += 1
print(f"  {n_lichen} lichens", flush=True)

# ── 3. mould: dark speckled blooms; a green algal film where it is damp ─────────
mould_n = noise(1.5, seed=SEED + 15, feature=500 * S)
speck = noise(0.25, seed=SEED + 16)
bloom = smooth(mould_n, 1.1, 2.1) * smooth(speck + 0.8 * mould_n - 1.2, -0.4, 0.8)
dots = smooth(speck, 2.3, 2.9) * smooth(mould_n, 0.6, 1.4)
mould = np.clip(bloom + dots, 0, 1)
img = mix(img, img * hexc("#6f7166") / hexc("#b0ae9f"), mould * 0.60)
film = smooth(damp, 0.8, 2.0) * smooth(clump2, -0.6, 0.8)
img = mix(img, img * hexc("#9aa48a") / hexc("#b0ae9f"), film * 0.35)
del bloom, dots

# ── 4. moss mask (needed by the damp streaks), then the streaks ─────────────────
clump = noise(1.2, seed=SEED + 17, band=70 * S)
mfield = 1.15 * joint + 0.75 * topedge + 0.15 * footedge + 0.55 * damp + 0.35 * clump + 0.30 * clump2 + 0.10 * fine
T = np.quantile(mfield[::4, ::4], 1 - MOSS)
moss = smooth(mfield, T - 0.06, T + 0.10)

streakn = noise(1.0, stretch=(0.10, 1.0), seed=SEED + 19)   # long down the wall
src = np.zeros((NH, NW), F32)
cand = np.flatnonzero((moss[::3, ::3] > 0.6) & (joint[::3, ::3] > 0.8))
for c in rng.choice(cand, 260, replace=False):
    sy_, sx_ = divmod(c, (NW + 2) // 3)
    src[(sy_ * 3) % NH, (sx_ * 3) % NW] += rng.uniform(0.4, 1.0)
ky = np.where(yy > NH // 2, yy - NH, yy).astype(F32)
kx = np.where(xx > NW // 2, xx - NW, xx).astype(F32)


def drip(length, width):
    return (np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2)).astype(F32)


streaks = circ_conv(src, drip(170.0 * S, 5.0 * S)) + circ_conv(src, drip(60.0 * S, 12.0 * S)) * 0.6
streaks = np.clip(streaks / np.percentile(streaks[streaks > 1e-4], 99), 0, 1)
streaks *= smooth(streakn, -0.6, 0.9) * (0.7 + 0.3 * stone)
img = mix(img, img * hexc("#8a8a76") / hexc("#b0ae9f"), streaks * 0.50)
del src

# ── 5. moss: cushions, bumpy and lit ────────────────────────────────────────────
bumps = noise(0.8, seed=SEED + 20, band=7 * S)
bumps2 = noise(0.8, seed=SEED + 21, band=4 * S)
cush = np.sqrt(np.clip(moss, 0, 1))
cushions = noise(1.0, seed=SEED + 25, band=40 * S)          # one cushion beside another, a crevice between
cpart = smooth(cushions, -0.9, 0.6)
MH = blur(moss, 6.0 * S) * (0.55 + 0.45 * cpart) + 0.06 * bumps * cush + 0.03 * bumps2 * cush   # domed cushions, finely bumped
mlit = np.clip(relief(MH.astype(F32), 1.5 * S), 0.80, 1.20)
wet = smooth(damp, 0.6, 1.6)                            # the wettest: a bluer, flatter moss
MLO, MMID, MHI = hexc("#7a8160"), hexc("#8d936a"), hexc("#a3a578")
WLO, WMID = hexc("#777f6d"), hexc("#8b9282")
hue = smooth(clump2 + 0.6 * clump, -1.2, 1.4)
mc = mix(MLO, MMID, hue)
mc = mix(mc, MHI, smooth(bumps + 0.5 * clump, 0.8, 2.2) * 0.8)       # yellow-green tips
mc = mix(mc, mix(WLO, WMID, hue), wet * 0.8)
mc *= (mlit * (0.90 + 0.12 * smooth(cush, 0.3, 1.0)) * (0.88 + 0.12 * cpart))[..., None]
ma = smooth(moss, 0.05, 0.35) * (0.80 + 0.20 * smooth(bumps2, -1.5, 0.5))  # ragged, thin at the edges
img *= (1 - 0.18 * np.clip(blur(ma, 3.0 * S, 3 * S, 4 * S) - ma, 0, 1))[..., None]  # the cushion's shadow
img = mix(img, mc, ma)
del mc, mlit, MH, bumps2

# spore capsules standing up out of the moss: a hair-thin seta, a rusty capsule
cap_m = Image.new("L", (NW, NH), 0)
seta_m = Image.new("L", (NW, NH), 0)
cdraw, sdraw = ImageDraw.Draw(cap_m), ImageDraw.Draw(seta_m)
cand = np.flatnonzero(((moss > 0.85) & (clump2 > 0.4))[::2, ::2])
for c in rng.choice(cand, 2600, replace=False):
    sy_, sx_ = divmod(c, NW // 2)
    x0, y0 = sx_ * 2 + rng.uniform(0, 2), sy_ * 2 + rng.uniform(0, 2)
    L, a = rng.uniform(7 * S, 16 * S), rng.normal(-np.pi / 2, 0.25)
    x1, y1 = x0 + L * np.cos(a), y0 + L * np.sin(a)
    r = rng.uniform(1.2 * S, 2.0 * S)
    for ox in ((-NW, 0, NW) if x0 < 30 * S or x0 > NW - 30 * S else (0,)):
        for oy in ((-NH, 0, NH) if y0 < 30 * S or y0 > NH - 30 * S else (0,)):
            sdraw.line([(x0 + ox, y0 + oy), (x1 + ox, y1 + oy)], fill=200, width=1)
            cdraw.ellipse((x1 + ox - r, y1 + oy - r * 1.3, x1 + ox + r, y1 + oy + r * 1.3), fill=255)
seta = np.asarray(seta_m, F32) / 255
capm = np.asarray(cap_m, F32) / 255
img = mix(img, hexc("#8a6e48"), seta * 0.45)
img = mix(img, hexc("#7f5a3c") * (0.9 + 0.2 * smooth(fine, -1, 1))[..., None], capm * 0.85)
del cap_m, seta_m, seta, capm

# ── 6. roots and creeper tendrils ──────────────────────────────────────────────
root_m = Image.new("L", (NW, NH), 0)
leaf_m = Image.new("L", (NW, NH), 0)
rdraw, ldraw = ImageDraw.Draw(root_m), ImageDraw.Draw(leaf_m)
leaf_vein = Image.new("L", (NW, NH), 0)
vdraw = ImageDraw.Draw(leaf_vein)


def wrapped_line(draw, pts, width, fill=255):
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            draw.line([(p + ox, q + oy) for p, q in pts], fill=fill, width=width, joint="curve")


def tendril(x0, y0, a, length, w0, leafy, depth=0):
    pts, w = [(x0, y0)], w0
    step = 5.0 * S
    n = int(length / step)
    turn = rng.normal(0, 0.02)
    pull = 0.012 if leafy else 0.05                     # a root hangs; a creeper wanders
    for i in range(n):
        turn = 0.80 * turn + rng.normal(0, 0.025)
        a += turn - pull * np.sin(a - np.pi / 2)
        x0, y0 = x0 + step * np.cos(a), y0 + step * np.sin(a)
        pts.append((x0, y0))
        if i % 3 == 2:
            wi = max(1, round(w0 * (1 - i / n) ** 0.8 + 0.6 * S))
            wrapped_line(rdraw, pts[-4:], wi)
        if depth < 2 and rng.random() < 0.012:
            tendril(x0, y0, a + rng.choice([-1, 1]) * rng.uniform(0.5, 1.1), length * (1 - i / n) * rng.uniform(0.3, 0.6),
                    max(1.5 * S, w0 * (1 - i / n) * 0.6), leafy, depth + 1)
        if leafy and i % int(rng.integers(5, 9)) == 0 and i > 3:
            side = rng.choice([-1, 1])
            la = a + side * rng.uniform(0.6, 1.3)
            Ls, Ws = rng.uniform(9 * S, 18 * S), rng.uniform(4 * S, 7 * S)
            bx, by = x0 + 2 * S * np.cos(la), y0 + 2 * S * np.sin(la)
            tt = np.linspace(0, 1, 14)
            half = Ws * np.sin(np.pi * tt) ** 0.8 * (1 - 0.3 * tt)
            ca, sa = np.cos(la), np.sin(la)
            left = [(bx + Ls * t * ca - h * sa, by + Ls * t * sa + h * ca) for t, h in zip(tt, half)]
            right = [(bx + Ls * t * ca + h * sa, by + Ls * t * sa - h * ca) for t, h in zip(tt, half)]
            poly = left + right[::-1]
            fill = int(rng.integers(150, 256))
            for ox in (-NW, 0, NW):
                for oy in (-NH, 0, NH):
                    ldraw.polygon([(p + ox, q + oy) for p, q in poly], fill=fill)
            wrapped_line(vdraw, [(bx, by), (bx + Ls * 0.8 * ca, by + Ls * 0.8 * sa)], 1)


for i in range(14):
    leafy = i < 6
    tendril(rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, 2 * np.pi) if leafy else rng.normal(np.pi / 2, 0.6),
            rng.uniform(500 * S, 1300 * S), rng.uniform(4.0 * S, 7.5 * S), leafy)
root = lblur(np.asarray(root_m, F32) / 255, 0.6 * S)
leaf = np.asarray(leaf_m, F32) / 255
leafa = smooth(leaf, 0.02, 0.2)
vein = np.asarray(leaf_vein, F32) / 255 * leafa
img *= (1 - 0.30 * np.clip(blur(np.maximum(root, leafa), 1.6 * S, 3 * S, 4 * S) - np.maximum(root, leafa), 0, 1))[..., None]
rootc = hexc("#73654f") * (0.95 + 0.10 * smooth(fine, -1, 1))[..., None]
rootc = rootc * (1 + 0.20 * np.clip(np.roll(root, (1, 1), (0, 1)) - np.roll(root, (-1, -1), (0, 1)), -1, 1))[..., None]   # lit on its upper left
img = mix(img, rootc, root * 0.92)
leafc = mix(hexc("#6f7d55"), hexc("#94a06c"), leaf)       # each leaf its own shade
leafc *= (1 + 0.15 * np.clip(np.roll(leafa, (px(2), px(2)), (0, 1)) - leafa, 0, 1) - 0.15 * np.clip(np.roll(leafa, (-px(2), -px(2)), (0, 1)) - leafa, 0, 1))[..., None]
img = mix(img, leafc, leafa * 0.95)
img *= (1 - 0.18 * vein)[..., None]
del root_m, leaf_m, leaf_vein, root, leaf, leafa, vein, rootc, leafc

# ── 7. bracket fungi in tiers, out of the joints ───────────────────────────────
BRACKETS = [   # zones (dark, mid, light), rim, underside
    ((hexc("#7c6852"), hexc("#9c8566"), hexc("#b9a888")), hexc("#d4c9ad"), hexc("#6b5a47")),   # brown, banded
    ((hexc("#7f7e78"), hexc("#99978e"), hexc("#b3b0a5")), hexc("#d0ccbe"), hexc("#6a675f")),   # grey turkey-tail
    ((hexc("#a17f4c"), hexc("#b5995f"), hexc("#c8b27c")), hexc("#d8cba1"), hexc("#86683e")),   # ochre shelf
    ((hexc("#8a7660"), hexc("#a48f74"), hexc("#bfb096")), hexc("#d7cfba"), hexc("#73624f")),   # tan
]
fib_n = noise(0.7, seed=SEED + 22, band=5 * S)


def shelf(cx, cy, w, dep, pal, ang):
    """One shelf seen from a little above: a fan below its line of attachment,
    zoned in arcs parallel to its margin, a pale rim, a dark underside lip."""
    zones, rim, under = pal
    rx, ry = int(w / 2) + px(16), int(dep) + px(18)
    ix, dx, dy = patch(cx, cy + dep / 2, rx, ry)
    dy = dy + dep / 2                                   # from the attachment line
    ca, sa = np.cos(ang), np.sin(ang)
    X, Y = dx * ca + dy * sa, -dx * sa + dy * ca
    th = np.arctan2(Y, X / (w / (2 * dep)))
    lob = 1 + 0.05 * np.sin(int(rng.integers(3, 7)) * th + rng.uniform(0, 6)) + 0.03 * np.sin(11 * th + rng.uniform(0, 6))
    rho = np.hypot(X / (w / 2), Y / dep) / lob
    top = smooth((1 - rho) * dep, -0.8, 0.8) * smooth(Y, -1.0, 1.0)
    lip_rho = np.hypot(X / (w / 2), (Y - 5 * S) / dep) / lob
    lip = smooth((1 - lip_rho) * dep, -0.8, 0.8) * smooth(Y - 5 * S, -1.0, 1.0)
    # cast shadow on the wall below and to the right
    shadow = lblur(lshift(np.maximum(top, lip), px(6), px(9)), 4.0 * S)
    img[ix] *= (1 - 0.40 * shadow)[..., None]
    put(ix, lip, under * (0.9 + 0.15 * smooth(-X / (w / 2), -1, 1))[..., None])
    nz = int(rng.integers(4, 8))
    z = rho * nz + 0.10 * fib_n[ix] + 0.15 * np.sin(th * 3)
    band = 0.5 + 0.5 * np.sin(2 * np.pi * z)
    zc = mix(zones[0], zones[1], smooth(band, 0.0, 0.5))
    zc = mix(zc, zones[2], smooth(band, 0.6, 1.0) * smooth(rho, 0.2, 0.9))
    zc = mix(zc, rim, smooth(rho, 0.86, 0.95))
    zc *= (1 + 0.03 * fib_n[ix] * smooth(rho, 0.1, 0.8) + 0.10 * (1 - rho) - 0.06 * (X / (w / 2)))[..., None]
    zc *= (1 - 0.25 * smooth(0.18 - rho, 0, 0.18))[..., None]  # where it goes into the wall
    put(ix, top, zc)
    edge = top * (1 - smooth((1 - rho) * dep, 0.6 * S, 1.8 * S))
    img[ix] *= (1 - 0.25 * edge * smooth(Y, 0, 4 * S))[..., None]


n_br = 0
for _ in range(400):
    if n_br >= 26:
        break
    k = int(rng.integers(0, K))
    x0 = rng.uniform(0, NW)
    y0 = float(bed_lines[k][int(x0) % NW])
    if moss[int(y0) % NH, int(x0) % NW] < 0.3 and rng.random() < 0.6:
        continue
    pal = BRACKETS[int(rng.choice(len(BRACKETS), p=[0.35, 0.15, 0.2, 0.3]))]
    W0 = rng.uniform(90 * S, 200 * S)
    tiers = int(rng.integers(1, 5))
    specs = []
    for t in range(tiers):
        w = W0 * rng.uniform(0.6, 1.0) * (1 - 0.12 * t)
        specs.append((x0 + rng.normal(0, W0 * 0.25), y0 + t * W0 * rng.uniform(0.28, 0.42) - rng.uniform(0, 8 * S), w,
                      w * rng.uniform(0.32, 0.46), rng.normal(0, 0.08)))
    for (cx, cy, w, dep, ang) in sorted(specs, key=lambda s: -s[1]):  # the lowest first: a shelf above overlaps it
        shelf(cx, cy, w, dep, pal, ang)
    n_br += 1
print(f"  {n_br} bracket clusters", flush=True)

# ── 8. clusters of small mushrooms standing in the joints ───────────────────────
MUSH = [   # cap, cap's dark, stem
    (hexc("#a8906c"), hexc("#7d6a50"), hexc("#c4baa2")),
    (hexc("#9c7254"), hexc("#74533d"), hexc("#c2b69c")),
    (hexc("#bcb092"), hexc("#918568"), hexc("#c8bfa8")),
    (hexc("#8e8270"), hexc("#6b6152"), hexc("#bdb4a0")),
    (hexc("#b39a5e"), hexc("#86703f"), hexc("#c5bb9e")),
]
L3 = np.array([-0.55, 0.55, 0.63])                   # the light: left, up, out (x right, y up, z out)
L3 /= np.linalg.norm(L3)


def mushroom(bx, by, h, cw, lean, pal, spots):
    cap, capd, stem = pal
    R = int(max(h + cw * 0.7, cw)) + px(14)
    ix, dx, dy = patch(bx, by - h / 2, R)
    X, Y = dx, -(dy - h / 2)                           # from the base, y up
    tY = np.clip(Y / h, 0, 1)
    cx = lean * h * tY ** 2
    sw = (cw * 0.10 + 2.0 * S) * (1.25 - 0.35 * tY)
    sdf_s = np.minimum(sw - np.abs(X - cx), np.minimum(Y + 1.5 * S, h - Y + 2 * S))
    sa = smooth(sdf_s, -0.7, 0.7)
    a, b = cw / 2, cw * rng.uniform(0.38, 0.62)
    capx, capy = lean * h, h - cw * 0.06
    nx, ny = (X - capx) / a, (Y - capy) / b
    rr = nx * nx + ny * ny
    sdf_c = (1 - np.sqrt(rr)) * min(a, b)
    ca_ = smooth(sdf_c, -0.7, 0.7) * smooth(Y - capy, -0.7, 0.7)
    gill = smooth((1 - np.sqrt(nx * nx + ((Y - capy) / (b * 0.22)) ** 2)) * a * 0.3, -0.5, 0.5) * smooth(capy - Y, -0.7, 0.7)
    sil = np.maximum(np.maximum(sa, ca_), gill)
    shadow = lblur(lshift(sil, px(5), px(4)), 3.0 * S)
    img[ix] *= (1 - 0.40 * shadow * (1 - sil))[..., None]
    # stem: a lit cylinder
    snx = np.clip((X - cx) / sw, -1, 1)
    sl = np.clip(-snx * L3[0] + np.sqrt(1 - snx * snx) * L3[2], 0, 1)
    put(ix, sa, stem * (0.72 + 0.36 * sl)[..., None])
    put(ix, gill, capd * 0.85)
    # cap: a lit half-ellipsoid
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    cl = np.clip(nx * L3[0] + ny * L3[1] + nz * L3[2], 0, 1)
    cc = mix(capd, cap, smooth(cl, 0.15, 0.75)) * (0.88 + 0.22 * cl)[..., None]
    cc = mix(cc, cap * 1.12, smooth(cl, 0.85, 1.0) * 0.6)
    if spots:
        sp = smooth(np.sin(nx * 9 + spots) * np.sin(ny * 7 + spots * 2), 0.82, 0.95)
        cc = mix(cc, hexc("#dcd4c0"), sp * 0.7)
    put(ix, ca_, cc)
    out = sil * (1 - smooth(np.maximum(np.maximum(sdf_s, sdf_c), 0), 0.4 * S, 1.4 * S))
    img[ix] *= (1 - 0.22 * out)[..., None]


n_mu = 0
for _ in range(600):
    if n_mu >= 32:
        break
    k = int(rng.integers(0, K))
    x0 = rng.uniform(0, NW)
    if moss[int(bed_lines[k][int(x0) % NW]) % NH, int(x0) % NW] < 0.4:
        continue
    pal = MUSH[int(rng.integers(0, len(MUSH)))]
    n = int(rng.integers(2, 10))
    size = rng.uniform(22 * S, 50 * S)
    spots = rng.uniform(0, 6) if rng.random() < 0.2 else 0
    items = []
    for _ in range(n):
        bx = x0 + rng.normal(0, size * 0.75)
        by = float(bed_lines[k][int(bx) % NW]) + rng.uniform(-2 * S, 8 * S)
        cw = size * rng.uniform(0.5, 1.3)
        h = cw * rng.uniform(0.8, 1.8)
        items.append((by, bx, h, cw, rng.normal(0, 0.18)))
    for (by, bx, h, cw, lean) in sorted(items, key=lambda s: (s[0], s[3])):
        mushroom(bx, by, h, cw, lean, pal, spots)
    n_mu += 1
print(f"  {n_mu} mushroom clusters", flush=True)

# ── 9. grime, and the whole drawn back toward its mean ─────────────────────────
grime = noise(1.9, seed=SEED + 23)
img *= (1 - 0.05 * smooth(grime, 0.0, 2.0) - 0.02 * fine)[..., None]
mean = img.reshape(-1, 3).mean(0)
img = mean + (img - mean) * CALM

out = Image.fromarray((np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8), "RGB")
out = out.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-9.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-9.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  {n_lichen} lichens  {n_br} brackets  {n_mu} mushroom clusters"
      f"  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
