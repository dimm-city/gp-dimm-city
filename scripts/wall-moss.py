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
9. The loud marks. All of the above is drawn at the wall's scale (about 1:7)
   and is texture at the size of a page; these are drawn at the page's scale,
   most of them half an inch to three inches across, so they read from across
   a spread. Each kind is made its own way, no two of a kind are alike, and
   they fall where they fall, clear of each other:
   - seeping damp: water out of a bed joint, running down the face in tongues;
     the stone darker where it is wet, a tide line at its edge, glints on it,
     trickles running on to a bead;
   - root fractures: a jagged gap forced open across the stones, side cracks
     and flaked scars beside it, the root lying in it and breaking out to
     hang and fork down the wall;
   - claw gouges: three to five furrows raked side by side through stone and
     moss, deep where the claws landed, the stone bruised pale round them;
   - slime trails: a pale, patchy, glinting ribbon wandering over the wall,
     and at the fresh end of each the slug that left it;
   - more fungus, of four more kinds: toadstools with warted caps, shaggy ink
     caps dripping black, puffballs (some spent, their spores smoked down the
     wall), rashes of orange cups; and the bracket again, three times the
     size, in sulphur yellow;
   - ivy: woody shoots climbing from the wall's foot (one creeping along from
     a joint), a lobed, veined leaf on a stalk every inch or so.
10. Grime over everything, and the whole drawn back toward a mid tone, so a
    white sheet pasted on it stays the focus.
It is then quantised to an exact palette, as the other walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is). The wall
keeps the colours it had before the marks, and where no mark falls the tile
is what it was, pixel for pixel; the marks get colours of their own.

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
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wall_fft import irfft2, rfft2  # noqa: E402  (numpy's real FFTs, spread over the cores)

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

yy, xx = np.ogrid[0:NH, 0:NW]          # a column and a row: they broadcast, so the tile-sized grids are never stored
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
    coarse = rfft2(r.standard_normal((NH0, NW0), dtype=F32)) * F32(S)   # S = sqrt(NH * NW / (NH0 * NW0)): the same power a bin
    spec = rfft2(r.standard_normal((NH, NW), dtype=F32))
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
    out = irfft2(spec, s=(NH, NW)).astype(F32)
    out -= out.mean()
    return out / out.std()


def blur(m, sigma, dx=0.0, dy=0.0):
    """Gaussian blur on the torus, the result shifted by (dx, dy)."""
    k = np.exp(-2 * np.pi ** 2 * sigma * sigma * F2)
    if dx or dy:
        k = k * np.exp(-2j * np.pi * (FX * dx + FY * dy))
    return irfft2(rfft2(m) * k, s=(NH, NW)).astype(F32)


def circ_conv(img, kernel):
    return irfft2(rfft2(img) * rfft2(kernel), s=(NH, NW)).astype(F32)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    u = 3 - 2 * t
    t *= t
    t *= u
    return t


def mix(a, b, t):
    t = np.asarray(t, F32)
    if t.ndim == 2:
        t = t[..., None]
    d = np.subtract(b, a)          # a + (b - a) * t, in the one new buffer where its shape and type allow
    inplace = d.shape == np.broadcast_shapes(d.shape, t.shape) and np.result_type(d, t) == d.dtype
    d = np.multiply(d, t, out=d if inplace else None)
    d += a
    return d


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
        t = x - (jx[j] + slant[j] * (v - 0.5))
        t += NW / 2
        np.remainder(t, NW, out=t)
        t -= NW / 2
        d[j] = t
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
    rows = np.arange(y0, y1) % NH
    E[rows] = np.where(inside, e, E[rows])
    DT[rows] = np.where(inside, dt, DT[rows])
    SID[rows] = np.where(inside, n_ids + s * 3 + sub, SID[rows])
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
del lump, edge_n, chip_n, E

# each stone its own colour and weathering
STONES = [hexc(c) for c in ("#b4afa3", "#aeaca4", "#b9ad96", "#a8a59c", "#b1aa9b", "#a9aba6", "#b6b0a2")]
pick = rng.integers(0, len(STONES), n_ids)
tone = rng.uniform(0.93, 1.05, n_ids).astype(F32)
colours = np.stack([STONES[i] for i in pick]) * tone[:, None]
base = colours[SID]
del SID

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
del strata, grain, pits_n, face_n, stain, H

# the joints: lime mortar, sandy, recessed, in the shadow of the stones above-left
MORTAR_C = hexc("#a39c8c")
sand = noise(0.2, seed=SEED + 10)
mortar = MORTAR_C * (0.94 + 0.05 * sand + 0.03 * mottle)[..., None]
cast = blur(stone, 3.0 * S, 5 * S, 6 * S)
mortar *= (1 - 0.30 * np.clip(cast - stone, 0, 1) - 0.10 * smooth(-inset, 0, 6 * S))[..., None]
img = mix(mortar, img, stone)
del base, mortar, lit, face, cast, sand, mottle

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


def shelf(cx, cy, w, dep, pal, ang, r=rng):
    """One shelf seen from a little above: a fan below its line of attachment,
    zoned in arcs parallel to its margin, a pale rim, a dark underside lip."""
    zones, rim, under = pal
    rx, ry = int(w / 2) + px(16), int(dep) + px(18)
    ix, dx, dy = patch(cx, cy + dep / 2, rx, ry)
    dy = dy + dep / 2                                   # from the attachment line
    ca, sa = np.cos(ang), np.sin(ang)
    X, Y = dx * ca + dy * sa, -dx * sa + dy * ca
    th = np.arctan2(Y, X / (w / (2 * dep)))
    lob = 1 + 0.05 * np.sin(int(r.integers(3, 7)) * th + r.uniform(0, 6)) + 0.03 * np.sin(11 * th + r.uniform(0, 6))
    rho = np.hypot(X / (w / 2), Y / dep) / lob
    top = smooth((1 - rho) * dep, -0.8, 0.8) * smooth(Y, -1.0, 1.0)
    lip_rho = np.hypot(X / (w / 2), (Y - 5 * S) / dep) / lob
    lip = smooth((1 - lip_rho) * dep, -0.8, 0.8) * smooth(Y - 5 * S, -1.0, 1.0)
    # cast shadow on the wall below and to the right
    shadow = lblur(lshift(np.maximum(top, lip), px(6), px(9)), 4.0 * S)
    img[ix] *= (1 - 0.40 * shadow)[..., None]
    put(ix, lip, under * (0.9 + 0.15 * smooth(-X / (w / 2), -1, 1))[..., None])
    nz = int(r.integers(4, 8))
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

# ── 9. the loud marks ──────────────────────────────────────────────────────────
# Everything above is drawn at the wall's scale (about 1:7) and reads, at the
# size of a page, as texture. These are drawn at the page's scale, so they read
# from across a spread: seeping damp, roots that have split the stone, claw
# gouges, slime trails, four more kinds of fungus, ivy, and the slugs. They have
# a random stream of their own (`more`), so the wall above stays as it was, and
# they fall where they fall (`place`), clear of each other. Each kind is made
# its own way, and no two of a kind are alike.
print("marks", flush=True)
plain = img.copy()                       # the wall without them: its mean and its palette are taken from it (see below)
more = np.random.default_rng(SEED + 70)
IN = DPI                                 # px an inch: the marks are sized in inches of page
FLOOR = 10.65 * IN                       # px from the sheet's top to the ground strip (11.25in - 0.6in): the wall's foot
GLINT = hexc("#eef1ea")                  # wet catching the light (nothing glows in print: it is only pale)
WETTED = np.array([0.63, 0.67, 0.65], F32)   # what water does to the stone's colour
taken = []                               # (x, y, reach) of every mark placed so far


def place(reach, lo=0.5, hi=9.6, course=False):
    """A place for a mark that reaches `reach` px from its middle, drawn at random
    between lo and hi inches down the wall and clear of the marks already there
    (as clear as the wall allows: the room it asks for shrinks as the tries run
    out). With `course` it sits on a bed joint, and that course's number is
    returned with it."""
    for t in range(3000):
        x0, y0, k = more.uniform(0, NW), more.uniform(lo, hi) * IN, None
        if course:
            k = int(np.argmin(np.abs(tops - y0)))
            y0 = float(bed_lines[k][int(x0) % NW])
        room = 1 - t / 3000
        if all(min(abs(x0 - a), NW - abs(x0 - a)) ** 2 + min(abs(y0 - b), NH - abs(y0 - b)) ** 2 >= (room * (reach + c)) ** 2 for a, b, c in taken):
            break
    taken.append((x0, y0, reach))
    return (x0, y0, k) if course else (x0, y0)


def soft(m, sigma, dx=0.0, dy=0.0):
    """blur() for a mark's mask: exactly nothing where the mask is not, so the wall away from the marks is untouched."""
    b = blur(m, sigma, dx, dy)
    b[b < 1 / 256] = 0
    return b


def canvas():
    im = Image.new("L", (NW, NH), 0)
    return im, ImageDraw.Draw(im)


def wrapped_poly(draw, pts, fill=255):
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            draw.polygon([(p + ox, q + oy) for p, q in pts], fill=fill)


def wrapped_dot(draw, x0, y0, rx, ry, fill=255):
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            draw.ellipse((x0 + ox - rx, y0 + oy - ry, x0 + ox + rx, y0 + oy + ry), fill=fill)


def mask(im, r=0.7):
    """A drawn canvas as a 0..1 field, its edges antialiased (a blur under a pixel wide, on the torus)."""
    a = Image.fromarray(np.pad(np.asarray(im), 4, mode="wrap")).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(a, F32)[4:-4, 4:-4] / 255


def strip(pts, widths):
    """The outline of a ribbon along pts, widths[i] wide at pts[i]."""
    p = np.asarray(pts, float)
    d = np.gradient(p, axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], 1) / np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-6)[:, None]
    h = np.asarray(widths, float)[:, None] / 2
    return [tuple(q) for q in p + n * h] + [tuple(q) for q in (p - n * h)[::-1]]


def jink(x0, y0, a, length, r, lo=22, hi=80, sd=0.5):
    """A fracture's line: straight runs that jink, never far from its heading."""
    pts, dev, run = [(x0, y0)], 0.0, 0.0
    while run < length:
        dev = 0.3 * dev + r.normal(0, sd)
        s = r.uniform(lo, hi) * S
        x0, y0, run = x0 + s * math.cos(a + dev), y0 + s * math.sin(a + dev), run + s
        pts.append((x0, y0))
    return pts


# The ivy is drawn last but its ground is taken first, as it is the largest of
# them: two plants climbing from the wall's foot, and one creeping along from a
# joint half way up. (its foot, how many shoots, how far they run in inches, the way they head)
IVIES = []
for lo, hi, shoots, tall, aim in ((FLOOR / IN + 0.1, FLOOR / IN + 0.2, int(more.integers(3, 5)), more.uniform(4.5, 7.5), -np.pi / 2),
                                  (FLOOR / IN + 0.1, FLOOR / IN + 0.2, int(more.integers(2, 4)), more.uniform(2.2, 4.0), -np.pi / 2),
                                  (3.0, 6.5, 2, more.uniform(2.5, 4.5), more.choice([0.0, np.pi]) + more.normal(0, 0.3))):
    x0, y0 = place(0.8 * IN, lo, hi)
    taken.append((x0 + 0.45 * tall * IN * math.cos(aim), y0 + 0.45 * tall * IN * math.sin(aim), 1.2 * IN))
    IVIES.append((x0, y0, shoots, tall, aim))

TA, TH, TM = (np.zeros((NH, NW), F32) for _ in range(3))    # a tube's cover, its height above the wall (px), and a saddle on it


def tube(pts, radii, saddle=False):
    """Stamp a round-backed tube (a root, a slug) along pts into TA and TH; with `saddle`, into TM too."""
    for (x0, y0), r_ in zip(pts, radii):
        if r_ < 0.6:
            continue
        ix, dx, dy = patch(x0, y0, int(r_) + 2)
        d2 = dx * dx + dy * dy
        TA[ix] = np.maximum(TA[ix], smooth(r_ - np.sqrt(d2), -0.7, 0.7))
        TH[ix] = np.maximum(TH[ix], np.sqrt(np.clip(r_ * r_ - d2, 0, None)))
        if saddle:
            TM[ix] = np.maximum(TM[ix], smooth(r_ * 0.90 - np.sqrt(d2), -0.7, 0.7))


def lambert(h, flat=1.0):
    """How a height field (px) takes the light from the upper left: 0 turned away, 0.63 flat to the wall, 1 square on."""
    hx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * (0.5 * flat)
    hy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * (0.5 * flat)
    return np.clip((0.55 * hx + 0.55 * hy + 0.63) / np.sqrt(1 + hx * hx + hy * hy), 0, 1)


def tubes(dark, mid_, light, shadow=0.45, flat=1.0, shine=0.0, spots=None):
    """Paint what tube() stamped: its shadow on the wall to the lower right, then the
    tube itself, round and lit; `shine` is how wet it is; then clear the stamps."""
    global img
    sh = soft(TA, 3.0 * S, 5 * S, 7 * S)
    img *= (1 - shadow * np.clip(sh - TA, 0, 1))[..., None]
    lam = lambert(TH, flat)
    c = mix(dark, mid_, smooth(lam, 0.05, 0.62))
    c = mix(c, light, smooth(lam, 0.68, 0.92) * 0.85)
    c *= (1 + 0.05 * fib_n)[..., None]
    if spots is not None:
        c = mix(c, dark * 0.8, spots)
    c = mix(c, np.clip(c * 1.22 + 0.04, 0, 1), TM * 0.85)                      # the saddle: paler, its far edge in its own shade
    c *= (1 - 0.35 * np.clip(TM - np.roll(TM, (px(2), px(2)), (0, 1)), 0, 1) - 0.25 * np.clip(np.roll(TM, (-px(3), -px(3)), (0, 1)) - TM, 0, 1) * TA)[..., None]
    if shine:
        c = mix(c, GLINT, smooth(lam, 0.90, 0.985) * shine)
    img = mix(img, c, TA)
    TA[:] = 0
    TH[:] = 0
    TM[:] = 0


# seeping damp: water coming out of a bed joint and running down the face. It is
# the old damp-streak convolution with the gain turned up: each seep is a row of
# springs along the joint, each spring's strength sets how far its tongue runs,
# and where the flow is over a threshold the stone is wet: darker, with a tide
# line where the wet stops, glints on it, and trickles running on from the
# longest tongues to a bead. One kind runs fast and narrow, the other slow and broad.
SEEP = ((230 * S, 30 * S), (130 * S, 54 * S))    # (how far it runs, how wide a tongue), px


def tongue(length, width):
    """drip(), narrowing as it runs: one spring's wet, a tongue that tapers to its tip."""
    return (np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2 * (1 + 2.5 * np.maximum(ky, 0) / length))).astype(F32)


src = [np.zeros((NH, NW), F32) for _ in SEEP]
springs = []
for i in range(5):
    x0, y0, k = place(1.1 * IN, 0.5, 7.4, course=True)
    span = more.uniform(0.6, 2.3) * IN
    for _ in range(int(more.integers(4, 12))):
        sx_ = x0 + more.uniform(-span / 2, span / 2)
        sy_ = float(bed_lines[k][int(sx_) % NW]) + more.uniform(2 * S, 12 * S)
        src[i % 2][int(sy_) % NH, int(sx_) % NW] += math.exp(more.uniform(0.4, 2.1))
        springs.append((sx_, sy_))
flow = sum(circ_conv(s_, tongue(*kern)) for s_, kern in zip(src, SEEP))
flow *= np.exp(0.22 * clump + 0.07 * lichen_n)              # the wet's edge wanders with the stone
WET = smooth(flow, 1.0, 1.1)
img = mix(img, img * WETTED, WET * np.clip(0.62 + 0.36 * smooth(flow, 1.0, 3.5) + 0.07 * streakn, 0, 1))     # wettest under the joint, streaked as it runs
img = mix(img, img * 0.76, np.clip((WET - soft(WET, 3.0 * S)) * 2.4, 0, 1))      # the tide line
glisten = noise(0.5, stretch=(0.2, 1.0), seed=SEED + 71, band=28 * S)            # short dashes, long down the wall
img = mix(img, GLINT, WET * smooth(flow, 1.25, 1.8) * smooth(glisten, 1.75, 2.25) * 0.8)
tim, td = canvas()
him, hd = canvas()
for sx_, sy_ in springs:
    col = flow[(int(sy_) + np.arange(NH // 2)) % NH, int(sx_) % NW]
    reach = int(np.argmax(col < 1.0))                       # how far down the wet runs under this spring
    if reach > 60 * S and more.random() < 0.7:              # a thread of running water down the tongue, catching the light
        for q in np.arange(sy_ + more.uniform(0, 30 * S), sy_ + reach * 0.9, 34 * S):
            if more.random() < 0.6:
                wrapped_line(hd, [(sx_ + more.normal(0, S), q), (sx_ + more.normal(0, S), q + more.uniform(8, 26) * S)], max(1, round(1.6 * S)))
    if reach > 40 * S and more.random() < 0.6:              # the trickle that runs on past the wet, to a bead
        w = more.uniform(3.2, 6.0) * S
        pts = [(sx_, sy_ + reach - 24 * S)]
        for _ in range(int(more.uniform(0.25, 1.5) * IN / (6 * S))):
            pts.append((pts[-1][0] + more.normal(0, 0.9 * S), pts[-1][1] + 6 * S))
        wrapped_line(td, pts, round(w))
        wrapped_line(hd, [(p - w * 0.22, q) for p, q in pts[4:]], max(1, round(w * 0.3)))
        bx, by = pts[-1]
        wrapped_dot(td, bx, by, w * 1.1, w * 1.7)
        wrapped_dot(hd, bx - w * 0.35, by - w * 0.5, w * 0.38, w * 0.5)
TR = mask(tim)
img = mix(img, img * WETTED, TR * 0.9)
img = mix(img, GLINT, mask(him) * 0.8)
del src, flow, glisten, tim, him, TR

# root fractures: a root has grown through the wall and split it. The fracture
# is a jagged gap, wide in the middle and run out to a hair at each end, with
# short side cracks and the pale scars where the face flaked off beside it; the
# root lies in the gap, as thick as the gap is wide, and breaks out of it in two
# to four places to hang and fork down the wall.
ROOTS = (hexc("#3b3027"), hexc("#665340"), hexc("#a08a68"))     # bark: in shade, across, lit
GAP = hexc("#35312b")                                           # the dark inside a fracture
FRESH = hexc("#cbc5b3")                                         # stone newly broken: paler than the weathered face
cim, cd = canvas()
sim_, sd = canvas()


def root(x0, y0, a, length, r0, r, depth=0):
    """A root over the wall: it wanders, hangs, knots, thins to a thread and forks."""
    step, turn, pts, rad = 2.0, 0.0, [], []
    n = int(length / step)
    k0, kf = r.uniform(0, 6.3), r.uniform(0.03, 0.07)
    for i in range(n):
        t = i / n
        turn = 0.96 * turn + r.normal(0, 0.0035)
        a += turn - 0.005 * math.sin(a - np.pi / 2)
        x0, y0 = x0 + step * math.cos(a), y0 + step * math.sin(a)
        pts.append((x0, y0))
        rad.append(max(1.3 * S, r0 * (1 - t) ** 0.8 * (1 + 0.12 * math.sin(k0 + kf * i))))
        if depth < 2 and r.random() < 0.004 * (1.3 - t):
            root(x0, y0, a + r.choice([-1, 1]) * r.uniform(0.35, 1.0), length * (1 - t) * r.uniform(0.35, 0.75), rad[-1] * r.uniform(0.5, 0.8), r, depth + 1)
    tube(pts, rad)


def fracture(x0, y0, r):
    a = r.uniform(0, np.pi)                                 # any way: a root does not care for the courses
    length, wmax = r.uniform(2.4, 5.2) * IN, r.uniform(22, 40) * S
    ca, sa = math.cos(a), math.sin(a)
    mid = jink(x0 - length / 2 * ca, y0 - length / 2 * sa, a, length, r)
    n = len(mid)
    w = [wmax * max(0.0, math.sin(np.pi * i / (n - 1))) ** 0.6 * r.uniform(0.5, 1.3) + 1.2 * S for i in range(n)]
    lean = r.uniform(0.25, 0.75, n)                         # the gap opens unevenly either side of its line
    left = [(p - sa * w_ * l_, q + ca * w_ * l_) for (p, q), w_, l_ in zip(mid, w, lean)]
    right = [(p + sa * w_ * (1 - l_), q - ca * w_ * (1 - l_)) for (p, q), w_, l_ in zip(mid, w, lean)]
    wrapped_poly(cd, left + right[::-1])
    for _ in range(int(r.integers(3, 8))):                  # side cracks, run out to nothing
        i = int(r.integers(1, n - 1))
        b = a + r.choice([-1, 1]) * r.uniform(0.5, 1.3) + (np.pi if r.random() < 0.5 else 0)
        pts = jink(*mid[i], b, r.uniform(0.4, 1.5) * IN, r, 14, 50, 0.45)
        wrapped_poly(cd, strip(pts, np.linspace(max(4 * S, w[i] * 0.5), 0.8, len(pts))))
    for _ in range(int(r.integers(4, 9))):                  # scars: an angular flake gone from the face beside the gap
        i = int(r.integers(1, n - 2))
        edge, way = (left, 1) if r.random() < 0.5 else (right, -1)
        (p0, q0), (p1, q1) = edge[i], edge[i + 1]
        flake = [(p0, q0)]
        for f in sorted(r.uniform(0.1, 0.9, int(r.integers(1, 3)))):
            out_ = way * r.uniform(16, 62) * S
            flake.append((p0 + (p1 - p0) * f - sa * out_, q0 + (q1 - q0) * f + ca * out_))
        wrapped_poly(sd, flake + [(p1, q1)])
    i0, i1 = int(n * r.uniform(0.15, 0.32)), int(n * r.uniform(0.68, 0.85))     # the root in the gap
    cx_ = np.array([p - sa * w_ * (l_ - 0.5) for (p, q), w_, l_ in zip(mid, w, lean)][i0:i1 + 1])
    cy_ = np.array([q + ca * w_ * (l_ - 0.5) for (p, q), w_, l_ in zip(mid, w, lean)][i0:i1 + 1])
    run = np.concatenate([[0], np.cumsum(np.hypot(np.diff(cx_), np.diff(cy_)))])
    at = np.arange(0, run[-1], 2.0)
    box = np.ones(31) / 31                                  # a root does not jink: its line is the gap's, smoothed
    ease = lambda v: np.convolve(np.pad(np.interp(at, run, v), 15, mode="edge"), box, "valid")
    rx_, ry_ = ease(cx_), ease(cy_)
    rr_ = np.clip(ease(np.array(w[i0:i1 + 1])) * 0.42, 7 * S, 17 * S) * np.clip(np.minimum(at, at[-1] - at) / (0.15 * at[-1]), 0.25, 1)
    tube(zip(rx_, ry_), rr_)
    for _ in range(int(r.integers(2, 5))):                  # and where it breaks out
        j = int(r.integers(len(at) // 8, len(at) * 7 // 8))
        root(rx_[j], ry_[j], a + r.choice([-1, 1]) * np.pi / 2 + r.normal(0, 0.5), r.uniform(1.2, 3.6) * IN, rr_[j] * r.uniform(0.8, 1.05), r)


for _ in range(4):
    fracture(*place(1.5 * IN, 0.8, 8.6), more)
CR = mask(cim)
SC = mask(sim_) * (1 - CR)
img = mix(img, FRESH * (1 + 0.03 * fine + 0.03 * lichen_n)[..., None], SC * 0.55)
img *= (1 - 0.35 * np.clip(SC - np.roll(SC, (px(3), px(3)), (0, 1)), 0, 1))[..., None]      # the old face's shadow on the scar
img = mix(img, np.clip(img * 1.22 + 0.04, 0, 1), np.clip(np.roll(CR, (px(2), px(2)), (0, 1)) - CR, 0, 1) * 0.7)   # the gap's lit lip
img = mix(img, GAP * (1 + 0.06 * fine)[..., None], CR * 0.95)
tubes(*ROOTS)
del cim, sim_, CR, SC

# claw gouges: something raked the wall. Three to five furrows side by side,
# the middle claws leading, all swung on the one curve; each bites deep where
# it lands and runs out to a scratch. The furrow is cut as a groove (its upper
# wall in shadow, its lower wall lit), its edges chipped, and round it the
# stone is bruised pale and the moss torn off.
gim, gd = canvas()
for _ in range(8):
    x0, y0 = place(1.0 * IN, 0.4, 9.8)
    n = int(more.choice([3, 4, 4, 5]))
    a = more.normal(np.pi / 2, 0.9) + (np.pi if more.random() < 0.15 else 0)   # mostly raked downward
    length, gap, swing, wmax = more.uniform(1.4, 3.3) * IN, more.uniform(34, 64) * S, more.normal(0, 0.5), more.uniform(11, 21) * S
    for j in range(n):
        off = j - (n - 1) / 2
        lj = length * more.uniform(0.7, 1.05) * (1 - 0.07 * abs(off))
        wj = wmax * more.uniform(0.7, 1.1)
        lead = -length / 2 + abs(off) * gap * more.uniform(0.3, 0.9) + more.normal(0, 12 * S)
        b = a - swing / 2 + more.normal(0, 0.03)
        gx_ = x0 + lead * math.cos(a) - off * gap * math.sin(a)
        gy_ = y0 + lead * math.sin(a) + off * gap * math.cos(a)
        skip = more.uniform(0.35, 0.7) if more.random() < 0.25 else None        # where the claw lifted and bit again
        pts, ws = [], []
        for i in range(49):
            t = i / 48
            b += swing / 48 + more.normal(0, 0.012)
            gx_, gy_ = gx_ + lj / 48 * math.cos(b), gy_ + lj / 48 * math.sin(b)
            pts.append((gx_, gy_))
            ws.append(wj * min(1, t / 0.05) ** 0.5 * (1 - t) ** 0.6 * (1 - 0.85 * math.exp(-((t - skip) / 0.05) ** 2) if skip else 1) + 0.6)
        wrapped_poly(gd, strip(pts, ws))
G = mask(gim, 1.0)
edge = soft(G, 2.5 * S)
G = np.maximum(G, smooth(edge + lichen_n * edge * (1 - edge), 0.42, 0.58))    # the edges chipped
bruise = smooth(soft(G, 7.0 * S) * (1 + 0.3 * lichen_n), 0.07, 0.30)
img = mix(img, FRESH * (1 + 0.04 * fine)[..., None], bruise * (0.38 + 0.50 * ma))
depth = soft(G, 2.2 * S)
slope = (np.roll(depth, 1, 1) - np.roll(depth, -1, 1)) + (np.roll(depth, 1, 0) - np.roll(depth, -1, 0))   # > 0 on the wall that faces the light
img = mix(img, mix(hexc("#3f3b34"), hexc("#ddd8c8"), smooth(slope, -0.10, 0.28)), G * 0.94)
del gim, G, edge, bruise, depth, slope

# slime trails: where a slug went, over stone and moss alike. A ribbon of dried
# slime, a pale patchy film that swells and narrows, a darker line along its
# edges, points of light all over it; old where it starts (thin, broken) and
# fresh at the slug.
SLIME = hexc("#dfe5d8")
rim_, rd = canvas()
eim, ed = canvas()
trails = []
for i in range(5):
    x0, y0 = place(0.5 * IN, 0.5, 9.3)
    a, w = more.uniform(0, 2 * np.pi), more.uniform(26, 44) * S
    wander = more.uniform(0.001, 0.003)
    n = int(more.uniform(4.5, 13) * IN / 3)
    pts, turn = [], 0.0
    for _ in range(n):
        turn = 0.985 * turn + more.normal(0, wander)
        a += turn
        x0, y0 = x0 + 3 * math.cos(a), y0 + 3 * math.sin(a)
        pts.append((x0, y0))
    trails.append((pts, w))
    p = np.asarray(pts)
    d = np.gradient(p, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1) / 3
    wide = w * (1 + 0.16 * np.sin(np.arange(n) / more.uniform(9, 16) + more.uniform(0, 6.3)) + 0.10 * np.sin(np.arange(n) / more.uniform(3, 6) + more.uniform(0, 6.3)))   # it swells and narrows as the slug did
    gone = 0
    for j in range(0, n - 8, 8):
        t = j / n
        if gone <= 0 and more.random() < 0.10 * (1 - 1.6 * t):                  # the old end is broken: stretches of it are gone
            gone = int(more.integers(2, 9))
        gone -= 1
        if gone > 0:
            continue
        v = int(255 * (0.35 + 0.65 * t ** 0.8))
        wrapped_poly(rd, strip(p[j:j + 10], wide[j:j + 10]), fill=v)
        for side in (-1, 1):
            if more.random() < 0.75:                                            # its edges, where the slime lay thickest: a darker line, not all the way
                wrapped_line(ed, [tuple(q) for q in p[j:j + 10] + side * nrm[j:j + 10] * (wide[j:j + 10, None] / 2 - 1.5 * S)], max(2, round(2.0 * S)), fill=v)
SL = mask(rim_)
sparkle = noise(0.3, seed=SEED + 72, band=4.5 * S)                               # points of light on it, not lines
img = mix(img, SLIME, SL * np.clip(0.56 + 0.16 * lichen_n + 0.10 * fine, 0.25, 0.85))    # a film, patchy
img = mix(img, img * np.array([0.62, 0.67, 0.63], F32), mask(eim) * 0.8)
img = mix(img, GLINT, SL * smooth(sparkle, 1.3, 1.8) * 0.9)
del rim_, eim, SL, sparkle

# more fungus, and of four more kinds, each a colony on a bed joint. The first
# is the old bracket drawn three times the size, in a sulphur yellow; the others
# are new: toadstools with warted caps, shaggy ink caps gone to black drip at
# the hem, puffballs (some ripe, some spent and smoking their spores down the
# wall), and a rash of orange cups on the stone.
SULPHUR = ((hexc("#9a6c2e"), hexc("#bd8f3d"), hexc("#d6b765")), hexc("#e6d6a2"), hexc("#765a2c"))
for _ in range(3):
    x0, y0, k = place(0.9 * IN, 0.5, 9.0, course=True)
    w0 = more.uniform(230, 400) * S
    specs = []
    for t in range(int(more.integers(2, 7))):
        w = w0 * more.uniform(0.55, 1.0) * (1 - 0.08 * t)
        specs.append((x0 + more.normal(0, w0 * 0.22), y0 + t * w0 * more.uniform(0.24, 0.38) - more.uniform(0, 8 * S), w,
                      w * more.uniform(0.30, 0.44), more.normal(0, 0.10)))
    for (cx, cy, w, dep, ang) in sorted(specs, key=lambda s: -s[1]):
        shelf(cx, cy, w, dep, SULPHUR, ang, more)

TOADS = [   # cap, cap's dark, stem, warts
    (hexc("#9c3f2e"), hexc("#5d2821"), hexc("#d8cfb8"), hexc("#ebe4cf")),      # ox-blood
    (hexc("#b06a2c"), hexc("#74431f"), hexc("#d6ccb2"), hexc("#ece3c8")),      # tawny
    (hexc("#7d7a45"), hexc("#55532f"), hexc("#d2ceb6"), hexc("#e4e0c8")),      # a sick olive
]


def toadstool(bx, by, h, cw, lean, pal, r):
    """A big toadstool, side on: a thick stem with a swollen foot and a skirt, a
    broad cap scattered with pale warts, its gills showing under the brim."""
    cap, capd, stem, wart = pal
    R = int(max(h + cw * 0.7, cw)) + px(18)
    ix, dx, dy = patch(bx, by - h / 2, R)
    X, Y = dx, -(dy - h / 2)                           # from the base, y up
    tY = np.clip(Y / h, 0, 1)
    cx = lean * h * tY ** 2
    sw = cw * 0.075 * (1 + 1.1 * (1 - tY) ** 3) + 2.0 * S
    sdf_s = np.minimum(sw - np.abs(X - cx), np.minimum(Y + 2 * S, h - Y + 2 * S))
    sa = smooth(sdf_s, -0.7, 0.7)
    a, b = cw / 2, cw * r.uniform(0.26, 0.52)
    capx, capy = lean * h, h - cw * 0.05
    nx, ny = (X - capx) / a, (Y - capy) / b
    rr = nx * nx + ny * ny
    sdf_c = (1 - np.sqrt(rr)) * min(a, b)
    ca_ = smooth(sdf_c, -0.7, 0.7) * smooth(Y - capy, -0.7, 0.7)
    gill = smooth((1 - np.sqrt(nx * nx + ((Y - capy) / (b * 0.30)) ** 2)) * a * 0.3, -0.5, 0.5) * smooth(capy - Y, -0.7, 0.7)
    ys, sh_ = h * r.uniform(0.52, 0.68), cw * r.uniform(0.09, 0.14)             # the skirt: a little cone round the stem
    tS = (ys - Y) / sh_
    skirt = smooth(np.minimum(sw * (1.0 + 1.3 * tS) - np.abs(X - cx), np.minimum(tS, 1 - tS) * sh_), -0.7, 0.7)
    sil = np.maximum(np.maximum(sa, ca_), np.maximum(gill, skirt))
    shadow = lblur(lshift(sil, px(8), px(7)), 5.0 * S)
    img[ix] *= (1 - 0.42 * shadow * (1 - sil))[..., None]
    snx = np.clip((X - cx) / sw, -1, 1)
    sl = np.clip(snx * L3[0] + np.sqrt(1 - snx * snx) * L3[2], 0, 1)
    under = 1 - 0.30 * smooth(Y, h - cw * 0.30, h - cw * 0.05) - 0.22 * smooth(tS, 1.0, 1.6) * smooth(tS, 3.0, 1.6)   # in the cap's shade, and the skirt's
    put(ix, sa, stem * ((0.70 + 0.38 * sl) * under)[..., None])
    put(ix, skirt, stem * (0.80 + 0.30 * sl * (1 - 0.3 * np.clip(tS, 0, 1)))[..., None])
    put(ix, gill, mix(capd, stem, 0.55) * (0.86 + 0.10 * np.sin(nx * a / (2.2 * S)))[..., None])
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    cl = np.clip(nx * L3[0] + ny * L3[1] + nz * L3[2], 0, 1)
    cc = mix(capd, cap, smooth(cl, 0.12, 0.72)) * (0.88 + 0.22 * cl)[..., None]
    cc = mix(cc, cap * 1.18, smooth(cl, 0.85, 1.0) * 0.6)
    warts = np.zeros_like(X)
    for _ in range(int(r.integers(8, 30))):
        th, rad = r.uniform(0.06, 0.94) * np.pi, 0.94 * math.sqrt(r.random())
        s = cw * r.uniform(0.030, 0.075) * (1 - 0.45 * rad)
        wa = r.uniform(0, np.pi)
        u = (X - capx - rad * math.cos(th) * a), (Y - capy - rad * math.sin(th) * b)
        warts = np.maximum(warts, smooth(s - np.hypot((u[0] * math.cos(wa) + u[1] * math.sin(wa)), (-u[0] * math.sin(wa) + u[1] * math.cos(wa)) * r.uniform(1.2, 2.0)), -0.7, 0.7))
    cc = mix(cc, wart * (0.82 + 0.22 * cl)[..., None], warts * 0.92)
    put(ix, ca_, cc)
    out = sil * (1 - smooth(np.maximum(np.maximum(sdf_s, sdf_c), 0), 0.5 * S, 1.8 * S))
    img[ix] *= (1 - 0.25 * out * (1 - warts))[..., None]


for i in range(4):
    x0, y0, k = place(0.75 * IN, 0.6, 9.2, course=True)
    pal = TOADS[int(more.integers(0, len(TOADS)))]
    size = more.uniform(105, 190) * S
    items = []
    for _ in range(int(more.integers(1, 6))):
        bx = x0 + more.normal(0, size * 0.8)
        cw = size * more.uniform(0.45, 1.15)
        items.append((float(bed_lines[k][int(bx) % NW]) + more.uniform(-2 * S, 10 * S), bx, cw * more.uniform(0.75, 1.5), cw, more.normal(0, 0.16)))
    for (by, bx, h, cw, lean) in sorted(items, key=lambda s: (s[0], s[3])):
        toadstool(bx, by, h, cw, lean, pal, more)

INK = hexc("#2b2826")


def inkcap(bx, by, h, cw, lean, age, r):
    """A shaggy ink cap: a tall bell on a thin stem, shaggy with upturned scales,
    its hem gone to black ink that drips. `age` 0 is a closed cylinder, 1 a
    flared bell, most of it ink."""
    R = int(h * 1.05 + cw) + px(12)
    ix, dx, dy = patch(bx, by - h / 2, R)
    X, Y = dx, -(dy - h / 2)
    tY = np.clip(Y / h, 0, 1)
    cx = lean * h * tY ** 2
    sw = cw * 0.07 + 1.6 * S
    sa = smooth(np.minimum(sw - np.abs(X - cx), np.minimum(Y + 2 * S, h - Y)), -0.7, 0.7)
    ch = min(h * 0.86, cw * (2.3 - 1.1 * age) * r.uniform(0.85, 1.1))          # the cap's height: it shortens as it melts
    v = (h - Y) / ch                                                           # 0 at its crown, 1 at its hem
    vc = np.clip(v, 0, 1)
    hw = (cw / 2) * np.sqrt(np.clip(1 - (1 - np.minimum(vc * 2.2, 1)) ** 2, 0, 1)) * (0.80 + 0.20 * vc + 0.75 * age * vc ** 3)
    ph = r.uniform(0, 6.3, 3)
    rag = 0.06 * np.sin(X / (5.0 * S) + ph[0]) + 0.05 * np.sin(X / (2.3 * S) + ph[1]) + 0.04 * fib_n[ix]    # the hem, tattered
    capx = lean * h * (np.clip(Y, 0, h) / h) ** 2
    sdf_c = np.minimum(hw - np.abs(X - capx), np.minimum((1 + rag - v) * ch, v * ch + 1))
    ca_ = smooth(sdf_c, -0.7, 0.7)
    drips = np.zeros_like(X)
    hem = h - ch
    for _ in range(int(r.integers(1, 3 + int(4 * age)))):
        xd = lean * h * (hem / h) ** 2 + r.uniform(-0.9, 0.9) * (cw / 2) * (1 + 0.75 * age)
        ld_, wd = r.uniform(0.15, 0.85) * hem, r.uniform(1.5, 2.8) * S
        drips = np.maximum(drips, smooth(np.minimum(wd - np.abs(X - xd), np.minimum(hem + 4 * S - Y, Y - (hem - ld_))), -0.7, 0.7))
        drips = np.maximum(drips, smooth(wd * 1.9 - np.hypot(X - xd, (Y - (hem - ld_)) * 0.7), -0.7, 0.7))
    sil = np.maximum(np.maximum(sa, ca_), drips)
    shadow = lblur(lshift(sil, px(7), px(6)), 4.0 * S)
    img[ix] *= (1 - 0.40 * shadow * (1 - sil))[..., None]
    snx = np.clip((X - cx) / sw, -1, 1)
    sl = np.clip(snx * L3[0] + np.sqrt(1 - snx * snx) * L3[2], 0, 1)
    put(ix, sa, hexc("#d9d2be") * (0.70 + 0.38 * sl)[..., None])
    put(ix, drips, INK)
    cnx = np.clip((X - capx) / np.maximum(hw, 1), -1, 1)
    cl = np.clip(cnx * L3[0] + np.sqrt(1 - cnx * cnx) * L3[2] + 0.25 * (1 - vc) * L3[1], 0, 1)
    cc = mix(hexc("#b59a70"), hexc("#dcd5c1"), smooth(vc, 0.02, 0.22))         # a tan crown on a pale bell
    scales = smooth(fib_n[ix] + 0.7 * np.sin(v * ch / (4.5 * S) + 3 * cnx + ph[2]), 0.9, 1.5) * smooth(vc, 0.1, 0.3)
    cc = mix(cc, hexc("#a18c68"), scales * 0.75)                               # the shag
    cc = cc * (0.66 + 0.42 * cl)[..., None]
    inked = smooth(v + 0.5 * rag, 1 - (0.22 + 0.5 * age), 1.0 - 0.08 * age)
    cc = mix(cc, INK * (0.9 + 0.5 * cl)[..., None], inked)
    put(ix, ca_, cc)
    img[ix] *= (1 - 0.25 * ca_ * (1 - smooth(sdf_c, 0.5 * S, 1.8 * S)))[..., None]


for i in range(4):
    x0, y0, k = place(0.7 * IN, 0.8, 9.2, course=True)
    size = more.uniform(55, 95) * S
    items = []
    for _ in range(int(more.integers(3, 9))):
        bx = x0 + more.normal(0, size * 1.3)
        cw = size * more.uniform(0.6, 1.15)
        items.append((float(bed_lines[k][int(bx) % NW]) + more.uniform(-2 * S, 8 * S), bx, cw * more.uniform(2.4, 3.8), cw, more.normal(0, 0.10), more.random() ** 1.3))
    for (by, bx, h, cw, lean, age) in sorted(items, key=lambda s: (s[0], s[3])):
        inkcap(bx, by, h, cw, lean, age, more)

PUFFS = [(hexc("#e0d9c4"), hexc("#a49a80")), (hexc("#c9b68e"), hexc("#8c7a58")), (hexc("#9a8662"), hexc("#5e5140"))]   # young, ripe, spent: (lit, shade)
SPORE = hexc("#5a4c36")


def puffball(bx, by, rad, age, r):
    """A puffball sat in the joint: a warty ball, lit as one. A ripe one (age 1)
    has a pore at its crown; a spent one (2) is torn open, and has smoked its
    spores down the wall below it."""
    lit, shade = PUFFS[age]
    if age == 2:
        for _ in range(int(r.uniform(180, 420))):                              # the spores first: the ball stands in front of them
            px_, py_ = bx + r.normal(0.3 * rad, 0.75 * rad), by - rad + abs(r.normal(0, 1.9 * rad)) + rad * 0.4
            s = max(0.9 * S, r.lognormal(math.log(1.8 * S), 0.5))
            jx, ddx, ddy = patch(px_, py_, int(s) + 2)
            put(jx, smooth(s - np.hypot(ddx, ddy), -0.7, 0.7) * r.uniform(0.35, 0.85), SPORE)
    R = int(rad * 1.25) + px(14)
    ix, dx, dy = patch(bx, by - rad * 0.8, R)
    a, b = rad, rad * r.uniform(0.80, 1.0)
    nx, ny = dx / a, -dy / b
    rr = nx * nx + ny * ny
    sil = smooth((1 - np.sqrt(rr)) * b, -0.7, 0.7)
    shadow = lblur(lshift(sil, px(7), px(6)), 4.0 * S)
    img[ix] *= (1 - 0.42 * shadow * (1 - sil))[..., None]
    nz = np.sqrt(np.clip(1 - rr, 0, 1))
    cl = np.clip(nx * L3[0] + ny * L3[1] + nz * L3[2], 0, 1)
    cc = mix(shade, lit, smooth(cl, 0.10, 0.80))
    cc = mix(cc, lit * 1.08, smooth(cl, 0.88, 1.0) * 0.6)
    cc *= (1 - 0.16 * smooth(fib_n[ix], 0.7, 1.5) * nz)[..., None]             # its warts
    if age == 1:
        cc = mix(cc, SPORE * 0.8, smooth(0.15 - np.hypot(nx + 0.08, (ny - 0.72) * 1.6), -0.03, 0.03))
    if age == 2:
        ph = r.uniform(0, 6.3, 2)
        tear = ny - (0.30 + 0.14 * np.sin(7 * nx + ph[0]) + 0.10 * np.sin(13 * nx + ph[1]))
        cc = mix(cc, SPORE * (0.62 + 0.5 * np.clip(-nx - ny + 1, 0, 1))[..., None], smooth(tear, 0.0, 0.05))
        cc = mix(cc, lit, smooth(tear, -0.07, 0.0) * smooth(tear, 0.04, 0.0) * 0.6)    # the torn lip
    put(ix, sil, cc)
    img[ix] *= (1 - 0.25 * sil * (1 - smooth((1 - np.sqrt(rr)) * b, 0.5 * S, 1.8 * S)))[..., None]


for i in range(5):
    x0, y0, k = place(0.6 * IN, 0.6, 9.4, course=True)
    size = more.uniform(34, 70) * S
    items = []
    for _ in range(int(more.integers(2, 9))):
        bx = x0 + more.normal(0, size * 1.6)
        items.append((float(bed_lines[k][int(bx) % NW]) + more.uniform(-3 * S, 14 * S), bx, size * more.uniform(0.45, 1.2), int(more.choice([0, 0, 1, 1, 2]))))
    for (by, bx, rad, age) in sorted(items, key=lambda s: s[0]):
        puffball(bx, by, rad, age, more)

CUPS = [   # hollow in shade, cup, hollow lit, rim
    (hexc("#7a3319"), hexc("#b9562a"), hexc("#dc8e52"), hexc("#e6bd90")),
    (hexc("#7d5a1c"), hexc("#b98a2c"), hexc("#dcb85c"), hexc("#ead9a4")),
    (hexc("#6e2a26"), hexc("#a23e34"), hexc("#cf7460"), hexc("#e2b4a0")),
]


def cup(x0, y0, rad, pal, r):
    """An elf cup: a little bowl on the stone, its rim pale and wavy, its hollow
    in shade on the side the light comes from and lit on the far side."""
    dark, mid_, light, rimc = pal
    ix, dx, dy = patch(x0, y0, int(rad * 1.25) + px(7))
    ang, el = r.uniform(0, np.pi), r.uniform(0.72, 1.0)
    X = (dx * math.cos(ang) + dy * math.sin(ang)) / rad
    Y = (-dx * math.sin(ang) + dy * math.cos(ang)) / (rad * el)
    th = np.arctan2(Y, X)
    rho = np.hypot(X, Y) / (1 + 0.08 * np.sin(3 * th + r.uniform(0, 6.3)) + 0.05 * np.sin(5 * th + r.uniform(0, 6.3)))
    a = smooth((1 - rho) * rad * el, -0.7, 0.7)
    shadow = lblur(lshift(a, px(3), px(3)), 2.0 * S)
    img[ix] *= (1 - 0.40 * shadow * (1 - a))[..., None]
    s = (dx + dy) / (rad * 1.41) * smooth(rho, 0.0, 0.7)                        # > 0 on the hollow's far side, which faces the light
    c = mix(dark, mid_, smooth(s, -0.75, 0.05))
    c = mix(c, light, smooth(s, 0.15, 0.75) * 0.8)
    c = mix(c, rimc * (1 - 0.18 * np.clip(s, 0, 1))[..., None], smooth(rho, 0.74, 0.86))
    put(ix, a, c)
    img[ix] *= (1 - 0.22 * a * smooth(rho, 0.93, 1.0))[..., None]


for i in range(5):
    x0, y0, k = place(0.55 * IN, 0.5, 9.4, course=True)
    pal = CUPS[int(more.integers(0, len(CUPS)))]
    sx_, sy_ = more.uniform(45, 110) * S, more.uniform(30, 75) * S
    for rad in sorted(np.clip(more.lognormal(math.log(15 * S), 0.5, int(more.integers(12, 46))), 6 * S, 38 * S), reverse=True):
        cup(x0 + more.normal(0, sx_), y0 + sy_ * 0.8 + more.normal(0, sy_), rad, pal, more)

# ivy: woody stems climbing from the wall's foot (and one creeping along from a
# joint half way up), forking, a leaf on a stalk every inch or so, to one side
# then the other. Each leaf is drawn on its own: three or five pointed lobes
# round a heart-shaped base, pale veins from the stalk to each point, folded
# along its midrib so one half takes the light; smaller and paler toward the
# shoot's tip, a few yellowed or gone brown, a few with a bite out of them.
IVY = [   # in shade, in the light, its gloss, its veins
    (hexc("#34492c"), hexc("#4a6639"), hexc("#7f9a62"), hexc("#b5c398")),
    (hexc("#3a4a2a"), hexc("#566b38"), hexc("#8a9c5e"), hexc("#bcc694")),
    (hexc("#2f4a33"), hexc("#44664a"), hexc("#779a78"), hexc("#b0c6a8")),
]
TURNED = [   # the leaves that have turned
    (hexc("#6f6a30"), hexc("#99913f"), hexc("#bdb469"), hexc("#d6d09c")),      # yellowed
    (hexc("#5f3526"), hexc("#874a32"), hexc("#ad7150"), hexc("#d0a888")),      # red
    (hexc("#4f3f2c"), hexc("#72593c"), hexc("#94795a"), hexc("#b8a586")),      # dead
]
LSS = 3                                  # a leaf's outline is drawn at LSS x and boxed down
vim, vd_ = canvas()
shoot, leaves = [], []                   # one plant's leaves as its shoots put them out; every plant's, with their colours


def ivy_outline(R, r, lobes):
    """An ivy leaf's outline in its own frame, the stalk at the back of the
    origin and the tip along +u: ([(u, v)], the points the veins run to)."""
    def half(side):
        n1, s1, n2 = r.uniform(0.50, 0.66), r.uniform(0.74, 0.92), r.uniform(0.46, 0.56)
        b1 = r.uniform(0.54, 0.72) if lobes == 5 else n2 * 1.03
        keys = [(0, 1.0), (r.uniform(28, 36), n1), (r.uniform(56, 68), s1), (r.uniform(94, 104), n2), (r.uniform(122, 134), b1),
                (158, r.uniform(0.38, 0.46)), (180, 0.10)]
        pts = []
        for (d0, r0), (d1, r1) in zip(keys, keys[1:]):
            pts += [(d0, r0), ((d0 + d1) / 2, (r0 + r1) / 2 * 1.07)]          # each lobe's side bows out a little
        pts.append(keys[-1])
        xy = [(R * q * math.cos(math.radians(d) * side), R * q * math.sin(math.radians(d) * side)) for d, q in pts]
        return xy, [xy[4], xy[8]] if lobes == 5 else [xy[4]]
    (p, tp), (m, tm) = half(1), half(-1)
    return p + m[-2:0:-1], [((R, 0.0), 0.034)] + [(t, 0.026) for t in tp + tm]


def ivy_leaf(x0, y0, ang, R, pal, r):
    dark, mid_, light, veinc = pal
    out_, tips = ivy_outline(R, r, 5 if r.random() < 0.7 else 3)
    Rb = int(R * 1.08) + px(8)
    ix, dx, dy = patch(x0, y0, Rb)
    n = 2 * Rb + 1
    ca, sa = math.cos(ang), math.sin(ang)
    fx, fy = x0 - int(x0) + Rb + 0.5, y0 - int(y0) + Rb + 0.5
    Z = lambda u, v: ((u * ca - v * sa + fx) * LSS, (u * sa + v * ca + fy) * LSS)
    im = Image.new("L", (n * LSS, n * LSS), 0)
    d = ImageDraw.Draw(im)
    d.polygon([Z(u, v) for u, v in out_], fill=255)
    if r.random() < 0.22:                                                      # something has been at it
        for _ in range(int(r.integers(1, 4))):
            th, q, br = r.uniform(-2.4, 2.4), R * r.uniform(0.55, 0.95), R * r.uniform(0.07, 0.17) * LSS
            bx, by = Z(q * math.cos(th), q * math.sin(th))
            d.ellipse((bx - br, by - br, bx + br, by + br), fill=0)
    vm = Image.new("L", (n * LSS, n * LSS), 0)
    vd = ImageDraw.Draw(vm)
    u0 = -0.10 * R
    for (tu, tv), wt in tips:
        vd.line([Z(u0, 0), Z(u0 + (tu - u0) * 0.9, tv * 0.9)], fill=255, width=max(2, round(R * wt * LSS)))
        for f in (0.35, 0.6):                                                  # and the side veins off each
            mu, mv = u0 + (tu - u0) * f, tv * f
            for side in (-1, 1):
                va = math.atan2(tv, tu - u0) + side * 0.75
                vd.line([Z(mu, mv), Z(mu + 0.2 * R * (1 - f) * math.cos(va), mv + 0.2 * R * (1 - f) * math.sin(va))], fill=170, width=max(1, round(R * 0.012 * LSS)))
    a = np.asarray(im.resize((n, n), Image.BOX), F32) / 255
    veins = np.asarray(vm.resize((n, n), Image.BOX), F32) / 255 * a
    U, V = dx * ca + dy * sa, -dx * sa + dy * ca
    face = (0.707 * sa - 0.707 * ca) * np.tanh(V / (0.07 * R))                 # folded along the midrib: > 0 on the half that takes the light
    c = mix(dark, mid_, smooth(face, -0.6, 0.5) * 0.75 + 0.25 * r.random())
    c = mix(c, light, 0.6 * smooth(face, 0.1, 0.7) * np.exp(-((U - 0.4 * R) ** 2 + (np.abs(V) - 0.22 * R) ** 2) / (0.34 * R) ** 2))
    c *= (1 + 0.05 * fib_n[ix])[..., None]
    c = mix(c, veinc, veins * 0.8)
    shadow = lblur(lshift(a, px(5), px(6)), 3.0 * S)
    img[ix] *= (1 - 0.42 * shadow * (1 - a))[..., None]
    put(ix, a, c)
    img[ix] *= (1 - 0.5 * np.clip(a - lblur(a, 1.5 * S), 0, 1))[..., None]      # a darker margin


def ivy(x0, y0, a, length, w0, aim, r, depth=0):
    """One shoot: it wanders toward `aim`, forks, and leaves a leaf to one side then the other."""
    step, turn, pts = 4.0, 0.0, [(x0, y0)]
    n = int(length / step)
    side, due = r.choice([-1, 1]), r.uniform(20, 60) * S
    for i in range(n):
        t = i / n
        turn = 0.94 * turn + r.normal(0, 0.011)
        a += turn - 0.022 * math.sin(a - aim)
        x0, y0 = x0 + step * math.cos(a), y0 + step * math.sin(a)
        pts.append((x0, y0))
        if i % 4 == 3:
            wrapped_line(vd_, pts[-6:], max(2, round(w0 * (1 - t) ** 0.7 + 1.5 * S)))
        due -= step
        if due <= 0:
            side, due = -side, r.uniform(30, 68) * S * (1 - 0.3 * t)
            la = a + side * r.uniform(0.6, 1.4)
            stalk = r.uniform(14, 42) * S * (1 - 0.4 * t)
            lx, ly = x0 + stalk * math.cos(la), y0 + stalk * math.sin(la)
            wrapped_line(vd_, [(x0, y0), (lx, ly)], max(2, round(2.2 * S)))
            R = r.uniform(36, 66) * S * (1 - 0.55 * t) * (0.85 if depth else 1)
            shoot.append((lx, ly, la + 0.4 * math.sin(np.pi / 2 - la) + r.normal(0, 0.3), R))   # the leaf hangs a little from its stalk's line
        if depth < 2 and r.random() < 0.007:
            ivy(x0, y0, a + r.choice([-1, 1]) * r.uniform(0.5, 1.1), length * (1 - t) * r.uniform(0.4, 0.8), max(3 * S, w0 * (1 - t) * 0.7), aim, r, depth + 1)


for x0, y0, shoots, tall, aim in IVIES:
    pal = IVY[int(more.integers(0, len(IVY)))]
    for _ in range(shoots):
        ivy(x0 + more.normal(0, 30 * S), y0, aim + more.normal(0, 0.4), tall * IN * more.uniform(0.6, 1.0), more.uniform(8, 13) * S, aim, more)
    leaves += [(lx, ly, la, R, TURNED[int(more.integers(0, len(TURNED)))] if more.random() < 0.13 else pal) for lx, ly, la, R in shoot]
    shoot.clear()
VN = mask(vim)
img *= (1 - 0.35 * np.clip(soft(VN, 2.0 * S, 3 * S, 4 * S) - VN, 0, 1))[..., None]
vc = hexc("#5c4a36") * (1 + 0.30 * np.clip(np.roll(VN, (-1, -1), (0, 1)) - np.roll(VN, (1, 1), (0, 1)), -1, 1) + 0.06 * fib_n)[..., None]   # woody, lit on its upper left
img = mix(img, vc, VN * 0.95)
del vim, VN, vc
for lx, ly, la, R, pal in leaves:
    ivy_leaf(lx, ly, la, R, pal, more)

# and the slugs, each at the fresh end of its trail: a round-backed, tapered
# body lying along the trail's last bend, the mantle a saddle behind the head,
# two long eye stalks and two short feelers, wet enough to shine.
SLUGS = [   # in shade, across, lit, blotched?
    (hexc("#2c2722"), hexc("#4b4137"), hexc("#857a6a"), False),                # black
    (hexc("#5f351d"), hexc("#96572b"), hexc("#cf9258"), False),                # rust
    (hexc("#4f4b28"), hexc("#868040"), hexc("#bdb678"), False),                # olive
    (hexc("#4c463b"), hexc("#8b806a"), hexc("#bdb39b"), True),                 # leopard
]
n_slugs = 0
for (pts, w), kind in zip(trails, more.permutation(len(trails))):
    dark, mid_, light, blotched = SLUGS[kind % len(SLUGS)]  # every trail has its slug: it is the slug that says what the trail is
    fat = w * more.uniform(0.55, 0.68)                      # half its width: it is as wide as its road, and a little over
    long_ = fat * more.uniform(8.5, 11.5)
    p = np.asarray(pts[-int(long_ / 3) - 2:])
    at = np.arange(0, long_, 1.5)
    bx, by = np.interp(at, np.arange(len(p)) * 3.0, p[:, 0]), np.interp(at, np.arange(len(p)) * 3.0, p[:, 1])
    s = at / long_                                          # 0 at the tail, 1 at the head
    rad = fat * np.minimum(1, s / 0.5) ** 0.55 * np.sqrt(np.clip(1 - np.clip((s - 0.90) / 0.10, 0, 1) ** 2, 0, 1))
    tube(zip(bx, by), rad)
    m = (s > 0.52) & (s < 0.86)                             # the mantle, a saddle behind the head
    tube(zip(bx[m], by[m]), rad[m] * 1.07 * np.sin(np.pi * (s[m] - 0.52) / 0.34) ** 0.35, saddle=True)
    hx, hy, ha = bx[-8], by[-8], math.atan2(by[-1] - by[-12], bx[-1] - bx[-12])
    for da, ln, r0 in ((0.38, 0.26, 3.8), (-0.38, 0.26, 3.8), (0.95, 0.08, 2.6), (-0.95, 0.08, 2.6)):
        ta = ha + da + more.normal(0, 0.12)
        q = np.arange(0, ln * long_ * more.uniform(0.8, 1.15), 1.5)
        bend = more.normal(0, 0.15)
        tx, ty = hx + q * np.cos(ta + bend * q / max(q[-1], 1)), hy + q * np.sin(ta + bend * q / max(q[-1], 1))
        tube(zip(tx, ty), np.linspace(r0 * S, r0 * 0.7 * S, len(q)))
        tube([(tx[-1], ty[-1])], [r0 * 1.45 * S])
    tubes(dark, mid_, light, shadow=0.42, flat=0.8, shine=0.85, spots=smooth(lichen_n, 0.3, 0.8) * 0.8 if blotched else None)
    n_slugs += 1
print(f"  {len(taken)} places  {len(leaves)} ivy leaves  {n_slugs} slugs", flush=True)
del TA, TH, TM

# ── 10. grime, and the whole drawn back toward its mean ────────────────────────
# The wall's mean is taken from the wall without the marks, so the wall is drawn
# back exactly as it was before there were any.
grime = noise(1.9, seed=SEED + 23)
grime = (1 - 0.05 * smooth(grime, 0.0, 2.0) - 0.02 * fine)[..., None]
plain *= grime
img *= grime
mean = plain.reshape(-1, 3).mean(0)
plain = mean + (plain - mean) * CALM
img = mean + (img - mean) * CALM

# ── the palette ────────────────────────────────────────────────────────────────
# Quantised in two parts. The wall without the marks gets the WALL_COLOURS it
# always had, cut as it always was, and every pixel no mark touched keeps the
# colour that gave it: away from the marks the tile is what it was, pixel for
# pixel. The pixels the marks changed get the rest of the palette, cut from
# their own colours (a median cut over the whole tile would give the ivy, the
# caps and the slugs a handful of greys between them).
WALL_COLOURS, COLOURS = 160, 256
wall8 = (np.clip(plain * SHADE, 0, 1) * 255).astype(np.uint8)
rgb8 = (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)
del plain, img
marked = (rgb8 != wall8).any(-1)
wall = Image.fromarray(wall8, "RGB").quantize(colors=WALL_COLOURS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
pal = wall.getpalette()[:3 * WALL_COLOURS]
pal += Image.fromarray(rgb8[marked].reshape(1, -1, 3)).quantize(colors=COLOURS - WALL_COLOURS, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * (COLOURS - WALL_COLOURS)]
ref = Image.new("P", (1, 1))
ref.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
both = Image.fromarray(rgb8, "RGB").quantize(palette=ref, dither=Image.Dither.NONE)
out = Image.fromarray(np.where(marked, np.asarray(both), np.asarray(wall)).astype(np.uint8), "P")
out.putpalette(pal)
out.save(ROOT / "images/wall-9.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-9.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  {n_lichen} lichens  {n_br} brackets  {n_mu} mushroom clusters"
      f"  {marked.mean():.1%} under the marks  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
