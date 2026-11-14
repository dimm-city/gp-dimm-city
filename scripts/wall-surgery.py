"""Draw wall 10, a back-alley operating room's tiled wall (`@page wall-10`), as images/wall-10.png.

    python3 scripts/wall-surgery.py      (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the stains and shadows are circular
convolutions, the wall tiles are laid on the tile's own grid, and every
shape (crack, chip, droplet, run, print) is drawn with wrap-around.

What it draws, back to front:
1. The wall tiles: small square glazed tiles, CELL px on a grid, once a pale
   clinical green (the odd replacement an off-white that never matched),
   each a shade off its neighbours, with a cushioned edge lit from the upper
   left, sunk in grout. Yellowed in broad patches, greyed with grime, the
   grout darkest of all, and all of it dirtier toward the floor.
2. The damage: tiles cracked (a single break, or a star where something hit
   the wall), chipped at the corners and edges (the pale biscuit showing,
   gone dirty), a few gone altogether (the combed tile adhesive and the bare
   render behind it, a shadow under the neighbours' edges).
3. What hung there: cleaner rectangles where a cabinet and a rail were
   screwed up for years, a grime line round them, the screw holes, rust run
   down from the screws.
4. Water: tide-marked stains and faint streaks from above, rust from the
   holes.
5. The fluids: blood at three ages (fresh, a dark red; a day or two, gone
   maroon; old, gone brown and flaking, part scrubbed off but kept in the
   grout). Impact spatter (a stain and its spray of satellite droplets, each
   one elongated along its flight and tailed at its leading end, rounder
   near the source, longer further out), cast-off arcs from a swung
   instrument (a line of tailed drops along the swing), runs sliding down
   from the heavy stains (channelled by a vertical grout line when they meet
   one, wicking sideways into each horizontal joint and often stopping
   there, a bead at the end), a hand dragged down the wall, a rag's wipe,
   and the brownish tide mark of dried antiseptic.
6. Mould in the grout, worst low down and round the water.
It is then quantised to an exact palette, as the other walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is).

Scale: a tile on the wall is about 108mm (4.25in) and is drawn 0.6in, so the
wall is drawn at about 1:7, and the blood at the same scale (a hand is about
1in, most droplets a few px). At DPI (300) the tile is
18in x 12in, 30 x 20 wall tiles: wider than a spread and taller than a page,
so a spread shows no repeat. Its grid is regular, so wall-tiles.py anchors it
to the sheet (ALIGNED) and a right page carries on from the left page's
width: the joints run unbroken across the spine. Being anchored to the
sheet's top, its rows sit in the same place on every page, so the floor
grime is drawn toward the foot of the page (FLOOR); the last 0.75in of the
tile is under the ground strip or off the page, and fades back to the top.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wall_fft import irfft2, rfft2  # noqa: E402  (numpy's real FFTs, spread over the cores)

ROOT = Path(__file__).resolve().parents[1]
DPI = 300
S = DPI / 240               # every length was set in px at 240 DPI: S keeps it the same in inches
NW, NH = 18 * DPI, 12 * DPI  # px; 18in x 12in: wider than a spread and taller than a page, so a spread shows no repeat
CELL = round(0.6 * DPI)     # a wall tile with its joint, px (0.6in): 30 across, 20 down
GH = 4 * S                  # half the grout joint, px
BEVEL = 7 * S               # the glaze's cushioned edge, px
FEATURE = 1800 * S          # px (7.5in): the largest blotch of yellowing or grime
FLOOR = 2556 * S            # px from the sheet's top to the ground strip (11.25in - 0.6in): the wall's foot
SS = 2                      # the fluids are drawn at SS x and boxed down: anti-aliased droplets
SEED = 10
SHADE = 1.0

DETAIL = np.random.default_rng(SEED + 99)   # the finer half of the local noise fields

rng = np.random.default_rng(SEED)
yy, xx = np.ogrid[0:NH, 0:NW]          # a column and a row: they broadcast, so the tile-sized grids are never stored
ky = np.where(yy > NH // 2, yy - NH, yy)
kx = np.where(xx > NW // 2, xx - NW, xx)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def white_spectrum(r, h, w, base=None, fine=None):
    """The spectrum (rfft2) of white noise on an h x w grid. Its coarse part
    (every frequency a 240 DPI grid holds) is the `base`-sized field r draws,
    just as r drew it at 240 DPI, so a field keeps its shape at any DPI and r is
    left where it was; the finer frequencies come from `fine`."""
    h0, w0 = base or (round(h / S), round(w / S))
    lo = r.standard_normal((h0, w0))
    if (h0, w0) == (h, w):
        return rfft2(lo)
    F = rfft2((DETAIL if fine is None else fine).standard_normal((h, w)))
    G = rfft2(lo)
    g = math.sqrt(h * w / (h0 * w0))
    my, mx = (h0 - 1) // 2, (w0 - 1) // 2     # frequencies 0..+-my down, 0..mx across: the 240 DPI grid's
    F[:my + 1, :mx + 1] = G[:my + 1, :mx + 1] * g
    F[h - my:, :mx + 1] = G[h0 - my:, :mx + 1] * g
    return F


def noise(beta, stretch=(1.0, 1.0), seed=None, feature=FEATURE):
    """Periodic 1/f^beta noise in [0, 1]; `stretch` (sx, sy) > 1 elongates it along that axis."""
    r = np.random.default_rng(seed)
    spec = white_spectrum(r, NH, NW, fine=r)
    fy = np.fft.fftfreq(NH)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(NW)[None, :] * stretch[0]
    spec /= np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature) ** beta
    out = irfft2(spec, s=(NH, NW))
    del spec
    out -= out.min()
    out /= out.max()
    return out


def circ_conv(img, col, row):
    """img convolved on the torus with a separable kernel: the column col times the row row."""
    F = rfft2(img)
    F *= np.fft.fft(col.ravel())[:, None]
    F *= np.fft.rfft(row.ravel())[None, :]
    return irfft2(F, s=(NH, NW))


def blur(m, sigma, dx=0, dy=0):
    gy = np.exp(-((ky - dy) ** 2 / (2 * sigma * sigma)))
    gx = np.exp(-((kx - dx) ** 2 / (2 * sigma * sigma)))
    return circ_conv(m, gy / gy.sum(), gx / gx.sum())


def shift(m, dy, dx):
    """np.roll by (dy, dx) px, fractions too: linear between the whole-pixel rolls."""
    out = 0
    for oy, wy in ((math.floor(dy), 1 - dy + math.floor(dy)), (math.floor(dy) + 1, dy - math.floor(dy))):
        for ox, wx in ((math.floor(dx), 1 - dx + math.floor(dx)), (math.floor(dx) + 1, dx - math.floor(dx))):
            if wy * wx:
                out = out + wy * wx * np.roll(m, (oy, ox), (0, 1))
    return out


def drip(length, width):
    """A drip's kernel, as its column and its row: a run down from the source, narrow across."""
    return np.where(ky >= 0, np.exp(-ky / length), 0), np.exp(-(kx / width) ** 2)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    u = 3 - 2 * t
    t *= t
    t *= u
    return t


def mix(a, b, t):
    t = np.asarray(t)
    if t.ndim == 2:
        t = t[..., None]
    d = np.subtract(b, a)          # a + (b - a) * t, in the one new buffer where its shape and type allow
    inplace = d.shape == np.broadcast_shapes(d.shape, t.shape) and np.result_type(d, t) == d.dtype
    d = np.multiply(d, t, out=d if inplace else None)
    d += a
    return d


def jag(a, b, rough, r, step=5):
    """A jagged line from a to b: midpoint displacement, kept near the chord."""
    pts = [np.array(a, float), np.array(b, float)]
    while True:
        out, split = [pts[0]], False
        for p, q in zip(pts, pts[1:]):
            d = q - p
            L = np.hypot(*d)
            if L > step:
                n = np.array([-d[1], d[0]]) / L
                out.append((p + q) / 2 + n * r.normal(0, rough * L))
                split = True
            out.append(q)
        pts = out
        if not split:
            return pts


class Layer:
    """A tile-sized mask drawn at SS x with wrap-around; shapes are queued and
    drawn lightest first, so a dense stain is never overwritten by a thin one."""

    def __init__(self):
        self.q = []

    def poly(self, pts, v):
        self.q.append(("p", [(float(x), float(y)) for x, y in pts], v))

    def ellipse(self, x, y, rx, ry, v):
        self.q.append(("e", (x - rx, y - ry, x + rx, y + ry), v))

    def line(self, pts, w, v):
        self.q.append(("l", [(float(x), float(y)) for x, y in pts], v, w))

    def render(self):
        im = Image.new("L", (NW * SS, NH * SS), 0)
        d = ImageDraw.Draw(im)
        for item in sorted(self.q, key=lambda it: it[2]):
            kind, geo, v = item[0], item[1], int(round(255 * min(1, max(0, item[2]))))
            if kind == "e":
                xs, ys = (geo[0], geo[2]), (geo[1], geo[3])
            else:
                xs, ys = [p[0] for p in geo], [p[1] for p in geo]
            for ox in (-NW, 0, NW):
                if max(xs) + ox < -8 * S or min(xs) + ox > NW + 8 * S:
                    continue
                for oy in (-NH, 0, NH):
                    if max(ys) + oy < -8 * S or min(ys) + oy > NH + 8 * S:
                        continue
                    if kind == "p":
                        d.polygon([((x + ox) * SS, (y + oy) * SS) for x, y in geo], fill=v)
                    elif kind == "e":
                        d.ellipse([(geo[0] + ox) * SS, (geo[1] + oy) * SS, (geo[2] + ox) * SS, (geo[3] + oy) * SS], fill=v)
                    else:
                        d.line([((x + ox) * SS, (y + oy) * SS) for x, y in geo], fill=v, width=max(1, int(round(item[3] * SS))), joint="curve")
        return np.asarray(im.resize((NW, NH), Image.BOX), float) / 255


def put(field, x0, y0, patch, how="max"):
    """Lay a local patch onto a tile-sized field at (x0, y0), wrapped."""
    h, w = patch.shape
    iy = (np.arange(h) + int(y0)) % NH
    ix = (np.arange(w) + int(x0)) % NW
    sub = field[np.ix_(iy, ix)]
    field[np.ix_(iy, ix)] = np.maximum(sub, patch) if how == "max" else sub + patch


def local_noise(h, w, beta, r, stretch=(1.0, 1.0), base=None):
    """`base`: its size at 240 DPI, when h x w over S does not round to it."""
    spec = white_spectrum(r, h, w, base)
    fy = np.fft.fftfreq(h)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(w)[None, :] * stretch[0]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    out = irfft2(spec / f ** beta, s=(h, w))
    out -= out.min()
    return out / out.max()


# ── 1. the wall tiles ───────────────────────────────────────────────────────────
print("tiles", flush=True)
TX, TY = NW // CELL, NH // CELL
col, row = xx // CELL, yy // CELL
tid = row * TX + col
lx, ly = xx % CELL, yy % CELL
# distance in from each side of the tile's face (the joint is centred on the cell line)
dl, dr = lx - GH + 0.5, CELL - GH - lx - 0.5
dt, db = ly - GH + 0.5, CELL - GH - ly - 0.5
dmin = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))           # in from the nearest side
face = np.clip(dmin + 0.5, 0, 1)     # 1 on the tile's face, 0 in the joint, AA between

floor = smooth(yy, 900 * S, FLOOR) * (1 - smooth(yy, FLOOR + 80 * S, NH))   # 0 at the top, 1 at the wall's foot, back to 0 out of sight

n_t = TX * TY
odd = rng.random(n_t) < 0.10                                          # replacements that never matched
green = hexc("#b5bbaf")
white = hexc("#bfbcb0")
base = np.where(odd[:, None], white, green) * rng.uniform(0.975, 1.025, (n_t, 1))
base = base * (1 + rng.normal(0, 0.008, (n_t, 3)))                     # each a shade off its neighbours
tile = base[tid]
tilt = rng.normal(0, 1, (n_t, 2))[tid]                                 # each sits a hair out of plane: a faint gradient
tile *= (1 + 0.012 * (tilt[..., 0] * (lx / CELL - 0.5) + tilt[..., 1] * (ly / CELL - 0.5)))[..., None]
del tid, tilt
mottle = noise(1.7, seed=SEED + 1)
fine = noise(0.6, seed=SEED + 2)
tile *= (1 + 0.05 * (mottle - 0.5) + 0.025 * (fine - 0.5))[..., None]


def cushion(d):
    return np.clip(1 - d / BEVEL, 0, 1) ** 2


light = 0.08 * (cushion(dl) + cushion(dt)) - 0.10 * (cushion(dr) + cushion(db))
tile *= (1 + light)[..., None]
del light

# the grout: recessed, grey, dirty; the side under a tile's lower/right edge in shade
grout_n = noise(1.0, seed=SEED + 3)
grout = hexc("#97938a") * (0.88 + 0.20 * grout_n - 0.14 * floor)[..., None]
in_shade = ((lx >= CELL - GH) & (lx < CELL)) | ((ly >= CELL - GH) & (ly < CELL))
grout *= np.where(in_shade, 0.87, 1.0)[..., None]
img = mix(grout, tile, face)
del grout, grout_n, in_shade

# yellowing and grime, broad and blotchy, and heavier toward the floor
yellow = noise(2.0, seed=SEED + 4)
y_amt = smooth(yellow, 0.35, 0.85) * 0.55 + 0.25 * floor + 0.12
img = mix(img, img * np.array([1.0, 0.95, 0.80]), y_amt)
del yellow, y_amt
grime = noise(1.5, seed=SEED + 5)
grime2 = noise(1.2, seed=SEED + 12)
splash = noise(0.9, stretch=(0.35, 1.0), seed=SEED + 13)                # dirty water, splashed and run
edge = np.exp(-np.clip(dmin, 0, None) / (14.0 * S))
dirt = (0.12 * smooth(grime, 0.40, 0.90) + 0.06 * smooth(grime2, 0.5, 0.85) + 0.16 * floor
        + 0.10 * floor * smooth(splash, 0.45, 0.8) + 0.05 * edge * (0.5 + grime) + 0.04 * (fine - 0.5))
img *= (1 - dirt)[..., None]
lum = img.mean(-1, keepdims=True)
img = mix(img, lum * np.array([1.01, 1.0, 0.97]), 0.40)               # greyed: the green half gone
del grime2, splash, edge, lum

# crazing: a net of hairline cracks in the glaze of some tiles, dirt worked into it
# (the edges of a Voronoi net, warped a little: crazing breaks the glaze into cells)
craze = np.zeros((NH, NW))
gy, gx = np.mgrid[0:CELL, 0:CELL].astype(float)
for t in np.flatnonzero(rng.random(n_t) < 0.30):
    c, r = t % TX, t // TX
    pts = rng.uniform(-12 * S, CELL + 12 * S, (int(rng.integers(12, 30)), 2))
    wx = gx + 8 * S * (local_noise(CELL, CELL, 2.2, rng) - 0.5)
    wy = gy + 8 * S * (local_noise(CELL, CELL, 2.2, rng) - 0.5)
    d = np.sort(np.hypot(wx[..., None] - pts[:, 0], wy[..., None] - pts[:, 1]), -1)
    net = np.clip(1 - (d[..., 1] - d[..., 0]) / (1.3 * S), 0, 1)
    net *= smooth(local_noise(CELL, CELL, 1.6, rng), 0.25, 0.55)          # in places only
    craze[r * CELL:(r + 1) * CELL, c * CELL:(c + 1) * CELL] = net * rng.uniform(0.5, 1.0)
craze *= face
img *= (1 - 0.16 * craze)[..., None]
del craze

# dirty water run down from the joints, and fly-specks
dsrc = np.zeros((NH, NW))
for _ in range(260):
    c, r = rng.integers(TX), rng.integers(TY)
    dsrc[int(r * CELL + GH + S) % NH, int(c * CELL + rng.uniform(10 * S, CELL - 10 * S)) % NW] += rng.uniform(0.3, 1.0)
dstreak = circ_conv(dsrc, *drip(60.0 * S, 3.5 * S))
dstreak = np.clip(dstreak / np.percentile(dstreak[dstreak > 1e-4], 99.5), 0, 1)
img = mix(img, img * np.array([0.86, 0.84, 0.78]), dstreak * 0.35 * face)
fly = noise(0.15, seed=SEED + 15)
specks = smooth(fly, 0.80, 0.86) * (0.3 + floor + smooth(grime, 0.5, 0.9))
img *= (1 - 0.30 * np.clip(specks, 0, 1))[..., None]
img = mix(img, img * 0.88, (1 - face) * (0.3 + 0.4 * smooth(grime, 0.3, 0.8)))     # grime packs the joints
del dsrc, dstreak, fly, specks, grime

# ── 2. the damage ─────────────────────────────────────────────────────────────
print("damage", flush=True)
cells = [(c, r) for r in range(TY) for c in range(TX)]
BISCUIT = hexc("#b9b19e")
ADHESIVE = hexc("#8c887e")
RENDER = hexc("#9c978b")

# tiles gone altogether: combed adhesive on bare render, broken joints round them
gone = Layer()
shards = Layer()
missing = [cells[i] for i in rng.choice(len(cells), 5, replace=False)]
missing.append(((missing[0][0] + 1) % TX, missing[0][1]))             # a pair together
missing.append(((missing[1][0]), (missing[1][1] + 1) % TY))
for (c, r) in missing:
    x0, y0 = c * CELL, r * CELL
    pts = []
    for (ax, ay), (bx, by) in (((0, 0), (CELL, 0)), ((CELL, 0), (CELL, CELL)), ((CELL, CELL), (0, CELL)), ((0, CELL), (0, 0))):
        for t in np.linspace(0, 1, 14, endpoint=False):
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            inset = rng.uniform(-1.0 * S, 3.5 * S)                             # the joint broken back in places, left on in others
            nx, ny = (0.5 * CELL - px), (0.5 * CELL - py)
            L = math.hypot(nx, ny)
            pts.append((x0 + px + nx / L * inset, y0 + py + ny / L * inset))
    gone.poly(pts, 1.0)
    if rng.random() < 0.6:                                              # a shard of the tile still stuck in a corner
        cx, cy = x0 + rng.choice([GH, CELL - GH]), y0 + rng.choice([GH, CELL - GH])
        sx, sy = (1 if cx < x0 + CELL / 2 else -1), (1 if cy < y0 + CELL / 2 else -1)
        a, b = rng.uniform(20 * S, 60 * S), rng.uniform(20 * S, 60 * S)
        shards.poly([(cx, cy), (cx + sx * a, cy), (cx + sx * a * 0.6, cy + sy * b * 0.5), (cx, cy + sy * b)], 1.0)
G = gone.render()
SHD = shards.render() * G
comb_a = rng.uniform(-0.3, 0.3)
phase = 2 * np.pi * (xx * math.sin(comb_a) + yy * math.cos(comb_a) + 30 * S * (mottle - 0.5)) / (20.0 * S)
comb = np.cos(phase)                                                   # the notched trowel's ridges, lit on their upper side
blob = noise(1.5, seed=SEED + 6)
adh = smooth(blob, 0.35, 0.50)                                         # where the adhesive stayed
recess = mix(RENDER * (0.9 + 0.2 * fine)[..., None], ADHESIVE * (0.95 + 0.07 * comb * smooth(blob, 0.4, 0.6) - 0.06 * np.abs(np.sin(phase)) ** 8 + 0.12 * (fine - 0.5))[..., None], adh)
recess *= (1 - 0.15 * floor)[..., None]
img = mix(img, recess, G)
sh = np.clip(blur(1 - G, 3.0 * S, 3 * S, 3 * S), 0, 1) * G                          # the neighbours' edges throw a shadow in
img *= (1 - 0.45 * sh)[..., None]
lit = np.clip(blur(1 - G, 2.0 * S, -2 * S, -2 * S), 0, 1) * G                       # the broken face of the joint at the foot/right
img = mix(img, img * 1.12, lit * 0.5)
img = mix(img, tile * (1 - dirt)[..., None] * 0.97, SHD)               # the stuck shard
del SHD, phase, comb, blob, adh, recess, sh, lit, tile, dirt, mottle

# chips: shell-shaped flakes off the corners and edges, the biscuit showing
chips = Layer()
for _ in range(70):
    c, r = cells[rng.integers(len(cells))]
    x0, y0 = c * CELL, r * CELL
    if rng.random() < 0.6:                                              # a corner
        cx, cy = x0 + rng.choice([GH, CELL - GH]), y0 + rng.choice([GH, CELL - GH])
    else:                                                               # an edge
        if rng.random() < 0.5:
            cx, cy = x0 + rng.uniform(20 * S, CELL - 20 * S), y0 + rng.choice([GH, CELL - GH])
        else:
            cx, cy = x0 + rng.choice([GH, CELL - GH]), y0 + rng.uniform(20 * S, CELL - 20 * S)
    R = rng.lognormal(math.log(9 * S), 0.5)
    k = int(rng.integers(5, 9))
    th = np.linspace(0, 2 * np.pi, k, endpoint=False) + rng.uniform(0, 1)
    rr = R * rng.uniform(0.55, 1.15, k)
    chips.poly([(cx + a * math.cos(t), cy + a * math.sin(t)) for a, t in zip(rr, th)], 1.0)
C = chips.render() * face * (1 - G)
chip_c = BISCUIT * (0.80 + 0.2 * fine - 0.12 * floor)[..., None]
img = mix(img, chip_c, C)
img *= (1 - 0.35 * np.clip(shift(C, -2 * S, -2 * S) - C, 0, 1))[..., None]   # the chip's upper-left wall in shade
img = mix(img, img * 1.10, np.clip(C - shift(C, 2 * S, 2 * S), 0, 1) * 0.6)
del C

# cracks: single breaks running across a few tiles, and stars where the wall was struck
cracks = Layer()
lips = []
for _ in range(14):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    a = rng.uniform(0, np.pi)
    L = rng.uniform(80 * S, 420 * S)
    pts = jag((x, y), (x + L * math.cos(a), y + L * math.sin(a)), 0.035, rng, step=7 * S)
    cracks.line(pts, 1.1 * S, 1.0)
    lips.append(pts)
for _ in range(4):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    a0 = rng.uniform(0, 2 * np.pi)
    arms = int(rng.integers(4, 7))
    for k in range(arms):
        a = a0 + 2 * np.pi * k / arms + rng.normal(0, 0.25)
        L = rng.uniform(25 * S, 120 * S)
        pts = jag((x, y), (x + L * math.cos(a), y + L * math.sin(a)), 0.04, rng, step=6 * S)
        cracks.line(pts, (1.4 if L > 80 * S else 1.0) * S, 0.9)
    chips.q = []
    for k in range(int(rng.integers(3, 6))):                            # the glaze spalled round the blow
        a, rr = rng.uniform(0, 2 * np.pi), rng.uniform(2 * S, 10 * S)
        R = rng.uniform(4 * S, 9 * S)
        th = np.linspace(0, 2 * np.pi, 7, endpoint=False)
        chips.poly([(x + rr * math.cos(a) + R * rng.uniform(0.5, 1.1) * math.cos(t),
                     y + rr * math.sin(a) + R * rng.uniform(0.5, 1.1) * math.sin(t)) for t in th], 1.0)
    Cs = chips.render() * (1 - G)
    img = mix(img, chip_c, Cs)
    img *= (1 - 0.3 * np.clip(shift(Cs, -2 * S, -2 * S) - Cs, 0, 1))[..., None]
K = cracks.render() * (1 - G)
img = mix(img, img * 1.08, np.clip(shift(K, S, S) - K, 0, 1) * 0.6)    # the crack's lit lip
img *= (1 - 0.55 * K)[..., None]
del K, Cs

# ── 3. what hung there: cleaner rectangles, a grime line round them, screw holes ──
print("ghosts", flush=True)
holes = Layer()
rust_src = np.zeros((NH, NW))
clean = np.zeros((NH, NW))
ghosts = [(rng.uniform(0, NW), rng.uniform(0, NH), 540 * S, 400 * S),        # a cabinet
          (rng.uniform(0, NW), rng.uniform(0, NH), 1050 * S, 70 * S),        # an instrument rail
          (rng.uniform(0, NW), rng.uniform(0, NH), 210 * S, 300 * S)]        # a dispenser
hole_at = []
for gx, gy, w, h in ghosts:
    m = Layer()
    m.poly([(gx, gy), (gx + w, gy), (gx + w, gy + h), (gx, gy + h)], 1.0)
    M = m.render()
    clean = np.maximum(clean, blur(M, 5.0 * S))
    inset = (24 if h > 100 * S else 18) * S
    xs = [gx + inset, gx + w - inset] if w < 800 * S else list(np.linspace(gx + inset, gx + w - inset, 5))
    ys = [gy + inset, gy + h - inset] if h > 100 * S else [gy + h / 2]
    for x in xs:
        for y in ys:
            hole_at.append((x + rng.normal(0, 1.5 * S), y + rng.normal(0, 1.5 * S)))
for _ in range(5):                                                     # stray holes
    hole_at.append((rng.uniform(0, NW), rng.uniform(0, NH)))
img = mix(img, img * np.array([1.04, 1.045, 1.07]), clean * 0.6 * (1 - G))   # under it the yellow and the grime never reached
rim = np.clip(blur(clean, 6.0 * S) - clean, 0, 1)                           # the dust that banked against its edges
img *= (1 - 0.45 * rim)[..., None]
del clean, rim, M
for (x, y) in hole_at:
    holes.ellipse(x, y, rng.uniform(4.5 * S, 6.0 * S), rng.uniform(4.5 * S, 6.0 * S), 1.0)
    rust_src[int(y + 6 * S) % NH, int(x) % NW] += rng.uniform(0.3, 1.0) if rng.random() < 0.7 else 0
Hc = holes.render()
ring = np.clip(blur(Hc, 3.0 * S) * 2.5 - Hc, 0, 1)                          # the glaze cracked off round the drill
img = mix(img, chip_c, ring * 0.7 * (1 - G))
img = mix(img, hexc("#3c3934") * np.ones(3), Hc)
del Hc, ring, chip_c

# ── 4. water and rust ─────────────────────────────────────────────────────────
print("water", flush=True)
RUST = hexc("#8a5a34")
rs = circ_conv(rust_src, *drip(90.0 * S, 2.5 * S))
rs = np.clip(rs / max(1e-6, np.percentile(rs[rs > 1e-4], 99)), 0, 1)
rs *= 0.6 + 0.4 * fine
img = mix(img, img * (RUST / RUST.max()), rs * 0.55)
del rust_src

wsrc = np.zeros((NH, NW))
for _ in range(26):
    wsrc[int(rng.uniform(0, NH)), int(rng.uniform(0, NW))] += rng.uniform(0.4, 1.0)
streak_n = noise(1.0, stretch=(0.1, 1.0), seed=SEED + 7)
ws = circ_conv(wsrc, *drip(520.0 * S, 14.0 * S))
ws = np.clip(ws / np.percentile(ws[ws > 1e-5], 99), 0, 1) * smooth(streak_n, 0.25, 0.75)
img = mix(img, img * np.array([0.93, 0.88, 0.76]), ws * 0.55)
del wsrc, streak_n

# tide marks: a blotch with dark rings at its old edges, one inside another
tide = np.zeros((NH, NW))
tide_in = np.zeros((NH, NW))
for _ in range(3):
    R0 = int(rng.uniform(180, 320))                                     # px at 240 DPI
    R = round(R0 * S)
    n = local_noise(2 * R, 2 * R, 2.2, rng, base=(2 * R0, 2 * R0))
    vy, vx = np.mgrid[-R:R, -R:R]
    d = np.hypot(vx / R, vy / (R * 1.25)) + 0.55 * (n - 0.5)             # taller than wide: it ran
    fld = np.zeros_like(d)
    for lev, s in ((0.80, 1.0), (0.62, 0.6), (0.45, 0.45)):
        fld = np.maximum(fld, s * np.exp(-((d - lev) / 0.02) ** 2))
    x0, y0 = rng.uniform(0, NW), rng.uniform(0, NH)
    put(tide, x0, y0, fld)
    put(tide_in, x0, y0, smooth(-d, -0.82, -0.6))
tide = blur(tide, 0.8 * S)
img = mix(img, img * np.array([0.95, 0.92, 0.84]), tide_in * 0.6)
img = mix(img, img * np.array([0.80, 0.72, 0.58]), np.clip(tide, 0, 1) * 0.35)
del tide_in

# ── 5. the fluids ─────────────────────────────────────────────────────────────
print("blood", flush=True)
rng = np.random.default_rng(SEED + 50)                                 # its own stream: the fluids stay put while the wall is tuned
AGES = ("fresh", "mid", "old")
L = {a: Layer() for a in AGES}
runs = []                                       # (x, y, width, volume, age): run starts, drawn after the stains


def drop(layer, x, y, a, length, width, v, tail=0.0, scallop=0.0, r=rng):
    """One droplet stain: an ellipse along its flight `a`, tailed at its leading end."""
    n = 28
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ex = length / 2 * np.cos(t) + tail * np.clip(np.cos(t), 0, 1) ** 10
    ey = width / 2 * np.sin(t) * (1 - 0.5 * np.clip(np.cos(t), 0, 1) ** 10 * (tail > 0))
    if scallop:
        k = int(r.integers(7, 13))
        w = 1 + scallop * np.clip(np.sin(k * t + r.uniform(0, 6)), 0, 1) ** 3 * r.uniform(0.4, 1.0, n)
        ex, ey = ex * w, ey * w
    ca, sa = math.cos(a), math.sin(a)
    layer.poly([(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in zip(ex, ey)], v)


def spatter(age, cx, cy, R, count, spread, aim, cone, standoff, nruns=(2, 4), r=rng):
    """An impact: a central stain and a spray of satellites flung out from it, round
    near the source (they struck square on), longer and tailed further out."""
    lay = L[age]
    drop(lay, cx, cy, r.uniform(0, np.pi), R * 2.0, R * 1.6, 1.0, scallop=0.35, r=r)
    for _ in range(int(r.integers(3, 6))):                               # lobes of the central stain
        a = r.uniform(0, 2 * np.pi)
        rr = R * r.uniform(0.5, 1.0)
        drop(lay, cx + rr * math.cos(a), cy + rr * math.sin(a), a, R * r.uniform(0.8, 1.3), R * r.uniform(0.5, 0.9), 0.95, scallop=0.25, r=r)
    for _ in range(count):
        a = aim + r.normal(0, cone)
        d = R * 0.8 + r.exponential(spread)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        y += 0.012 * d * d / spread                                      # long flights droop a little
        size = max(0.8 * S, r.lognormal(math.log(2.3 * S), 0.55) * (1.3 - 0.7 * min(1.0, d / (3 * spread))))
        alpha = math.atan2(standoff, d)                                  # the angle it struck at
        el = min(1 / max(math.sin(alpha), 0.2), 4.5) * r.uniform(0.9, 1.15)
        tail = size * el * r.uniform(0.25, 0.8) if el > 1.5 else 0.0
        drop(lay, x, y, a, size * el, size, r.uniform(0.55, 0.95) * min(1, 0.5 + size / (5 * S)), tail=tail, scallop=0.15 if size > 3.5 * S else 0, r=r)
        if el > 2.2 and r.random() < 0.25:                               # the exclamation mark's dot
            dd = size * el * 0.6 + tail + r.uniform(2 * S, 7 * S)
            drop(lay, x + dd * math.cos(a), y + dd * math.sin(a), a, size * 0.9, size * 0.5, 0.7, r=r)
    for _ in range(int(r.integers(*nruns))):                             # runs from the heavy stain
        runs.append((cx + r.normal(0, R * 0.5), cy + R * r.uniform(0.4, 0.8), r.uniform(2.6 * S, 4.2 * S), r.uniform(150 * S, 520 * S), age))


def castoff(age, cx, cy, R, a0, a1, count, r=rng):
    """Drops thrown off a swung instrument along an arc, tailed in the swing's direction,
    heavier where the swing began and thinning out along it."""
    lay = L[age]
    sgn = 1 if a1 > a0 else -1
    ts = np.sort(r.uniform(0, 1, count) ** 1.3)
    for t in ts:
        a = a0 + (a1 - a0) * t
        rr = R + r.normal(0, 4 * S)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        heading = a + sgn * np.pi / 2 + r.normal(0, 0.04)
        size = max(0.9 * S, r.lognormal(math.log(2.8 * S), 0.35) * (1.25 - 0.75 * t))
        el = r.uniform(2.4, 4.5)
        drop(lay, x, y, heading, size * el, size, r.uniform(0.7, 0.95), tail=size * el * r.uniform(0.3, 0.9), r=r)
        if size > 3.4 * S and r.random() < 0.15:
            runs.append((x, y + size, size * 0.7, r.uniform(80 * S, 260 * S), age))


def run(age, x, y, w, vol, r=rng):
    """A run: down the wall, wandering a little, channelled by a vertical joint it
    meets, wicking into each horizontal joint (and often stopping there), a bead at its foot."""
    lay = L[age]
    left, right = [], []
    drift = 0.0
    while vol > 0 and w > 0.8 * S:
        g = round(x / CELL) * CELL                                       # the nearest vertical joint
        if abs(x - g) < GH + w / 2 + 1.5 * S:
            x += (g - x) * 0.2
        else:
            drift = 0.97 * drift + r.normal(0, 0.03 * S)
            x += drift
        ww = w * (1 + 0.12 * math.sin(y / r.uniform(9 * S, 15 * S)))              # its width wavers
        left.append((x - ww / 2, y))
        right.append((x + ww / 2, y))
        y += 2 * S
        vol -= w * 0.9
        if (y % CELL) >= CELL - GH and ((y - 2 * S) % CELL) < CELL - GH:       # reached a horizontal joint
            sl, sr = r.uniform(1 * S, 9 * S), r.uniform(1 * S, 9 * S)
            gy = y - y % CELL + CELL                                     # the joint's centre line
            lay.ellipse(x - (sl - sr) / 2, gy - GH / 2, (sl + sr) / 2 + w / 2, GH * 0.6, 0.55)
            vol -= (sl + sr) * 4
            if r.random() < 0.45 or vol <= 0:
                break
            w *= 0.85                                                    # what got past the joint is thinner
    if len(left) > 1:
        lay.poly(left + right[::-1], 0.85)
        bx, by = left[-1][0] + w / 2, left[-1][1]
        lay.ellipse(bx, by, w * 0.7, w * 0.9, 0.95)                      # the bead


# where things happened: spaced out round the torus
def spaced(n, sep, r=rng):
    pts = []
    while len(pts) < n:
        x, y = r.uniform(0, NW), r.uniform(150 * S, FLOOR - 300 * S)
        if all(min(abs(x - px), NW - abs(x - px)) ** 2 + min(abs(y - py), NH - abs(y - py)) ** 2 >= sep * sep for px, py in pts):
            pts.append((x, y))
    return pts


E = spaced(8, 950 * S)
# 1: a fresh impact, and an old one beside it, half scrubbed off
spatter("fresh", *E[0], R=14 * S, count=320, spread=150 * S, aim=rng.uniform(-np.pi, 0), cone=0.9, standoff=170 * S)
spatter("old", E[0][0] + 340 * S, E[0][1] - 160 * S, R=12 * S, count=200, spread=150 * S, aim=rng.uniform(-np.pi, 0), cone=1.1, standoff=200 * S)
# 2: cast-off, fresh and old
castoff("fresh", E[1][0], E[1][1] + 950 * S, 950 * S, -np.pi / 2 - 0.55, -np.pi / 2 + 0.35, 46)
castoff("old", E[2][0] - 900 * S, E[2][1] + 200 * S, 1000 * S, -0.55, 0.25, 36)
castoff("mid", E[2][0] - 870 * S, E[2][1] + 230 * S, 980 * S, -0.40, 0.18, 22)
# 3: a smaller impact, a day or two old
spatter("mid", *E[3], R=9 * S, count=160, spread=120 * S, aim=rng.uniform(0, 2 * np.pi), cone=1.6, standoff=140 * S)
# 4: lone drips from above, and a few stray drops
for _ in range(2):
    x, y = E[4][0] + rng.normal(0, 260 * S), E[4][1] + rng.normal(0, 120 * S)
    a = rng.choice(AGES, p=[0.5, 0.3, 0.2])
    drop(L[a], x, y, rng.uniform(0, np.pi), 7 * S, 6 * S, 0.95, scallop=0.3)
    runs.append((x, y + 2 * S, rng.uniform(2.6 * S, 3.6 * S), rng.uniform(150 * S, 450 * S), a))
for _ in range(40):
    a = rng.choice(AGES, p=[0.3, 0.3, 0.4])
    s = rng.lognormal(math.log(2.6 * S), 0.4)
    drop(L[a], rng.uniform(0, NW), rng.uniform(0, FLOOR), rng.uniform(0, 2 * np.pi), s * rng.uniform(1, 2.5), s, rng.uniform(0.6, 0.9))

for x, y, w, vol, age in runs:
    run(age, x, y, w, vol)

blood = {a: L[a].render() for a in AGES}


def hand(r, scale):
    """A hand, palm flat, fingers up and a little spread, in a local canvas: (mask, W, H).
    The pads, the finger joints and the heel of the palm take the blood; the palm's
    hollow and the creases barely touch."""
    s0 = 13.5 * scale                                                    # px per cm at 1:7, at 240 DPI
    s = s0 * S
    W0, H0 = int(16 * s0), int(21 * s0)                                  # its canvas at 240 DPI
    W, H = round(W0 * S), round(H0 * S)
    im = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(im)
    cx, top, foot = W * 0.52, H * 0.42, H * 0.95
    Z = lambda pts: [(px * SS, py * SS) for px, py in pts]
    d.polygon(Z([(cx - 4.3 * s, top), (cx + 4.3 * s, top + 0.3 * s), (cx + 4.0 * s, foot - 2.5 * s),
                 (cx + 2.2 * s, foot), (cx - 2.0 * s, foot), (cx - 3.9 * s, foot - 3.0 * s)]), fill=190)
    for (ox, ln, wd, ang) in ((-3.2, 6.4, 1.6, -0.22), (-1.1, 7.6, 1.75, -0.07), (1.05, 7.2, 1.7, 0.06), (3.05, 5.6, 1.5, 0.2)):
        bx, by = cx + ox * s, top + 0.4 * s + abs(ox) * 0.12 * s
        ca, sa = math.cos(ang), math.sin(ang)
        tip = lambda t, side: (bx + sa * t * ln * s + ca * side * wd * s / 2 * (1 - 0.15 * t),
                               by - ca * t * ln * s + sa * side * wd * s / 2 * (1 - 0.15 * t))
        d.polygon(Z([tip(0, -1), tip(0.93, -1), tip(0.93, 1), tip(0, 1)]), fill=205)
        tx, ty = tip(0.9, 0)
        rr = wd * s * 0.45
        d.ellipse(Z([(tx - rr, ty - rr * 1.2), (tx + rr, ty + rr * 1.2)]), fill=230)            # the pad
        for t in (0.38, 0.66):                                           # the creases at the joints
            d.line(Z([tip(t, -1.1), tip(t, 1.1)]), fill=40, width=int(0.28 * s * SS))
    d.ellipse(Z([(cx - 5.4 * s, foot - 6.4 * s), (cx - 2.4 * s, foot - 0.6 * s)]), fill=200)   # the ball of the thumb
    ta = -0.95                                                           # the thumb, out to the side and up
    bx, by = cx - 3.9 * s, foot - 3.8 * s
    ex, ey = bx + math.sin(ta) * 5.2 * s, by - math.cos(ta) * 5.2 * s
    d.line(Z([(bx, by), (ex, ey)]), fill=200, width=int(2.0 * s * SS))
    d.ellipse(Z([(ex - 1.0 * s, ey - 1.2 * s), (ex + 1.0 * s, ey + 1.2 * s)]), fill=240)
    mx, my = (bx + ex) / 2, (by + ey) / 2
    d.line(Z([(mx - 1.1 * s * math.cos(ta), my - 1.1 * s * math.sin(ta)), (mx + 1.1 * s * math.cos(ta), my + 1.1 * s * math.sin(ta))]),
           fill=40, width=int(0.28 * s * SS))
    shape = im.point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.GaussianBlur(0.45 * s * SS))
    level = im.filter(ImageFilter.GaussianBlur(0.45 * s * SS))
    shape = np.asarray(shape.resize((W, H), Image.BOX), float) / 255
    level = np.asarray(level.resize((W, H), Image.BOX), float) / 255
    m = smooth(shape, 0.35, 0.65) * level / np.maximum(shape, 1e-3)      # the outline rounded, as flesh is
    hy, hx = np.mgrid[0:H, 0:W]
    hollow = np.exp(-(((hx - cx) / (2.0 * s)) ** 2 + ((hy - (top + foot) / 2 + 0.6 * s) / (2.2 * s)) ** 2))
    return m * (1 - 0.8 * hollow * smooth(local_noise(H, W, 1.4, r, base=(H0, W0)), 0.2, 0.6)), W, H, (H0, W0)


def smear(age, x, y, drag, angle, r=rng):
    """A bloody hand put to the wall and dragged down it: the print, patchy where the
    skin barely touched, then the fingers' trails, streaked along the drag."""
    m, W, H, (H0, W0) = hand(r, r.uniform(0.95, 1.05))
    side = round(20 * S)
    pad = int(drag) + side
    P = np.zeros((H + pad, W + 2 * side))
    P[:H, side:side + W] = m
    base = (H0 + int(drag / S + 1e-9) + 20, W0 + 40)                    # its size at 240 DPI
    n = local_noise(*P.shape, 0.9, r, base=base)
    stri = local_noise(*P.shape, 1.0, r, stretch=(0.03, 1.0), base=base)   # streaks along the drag
    trail = np.zeros_like(P)
    for k in range(2, int(drag), 2):
        wgt = (1 - k / drag) ** 1.2
        trail = np.maximum(trail, np.roll(P, k, 0) * wgt)
    print_ = P * smooth(n, 0.22, 0.55)
    out = np.maximum(print_ * 0.65, trail * smooth(stri, 0.3, 0.7) * 0.7)
    if angle:
        out = np.asarray(Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).rotate(math.degrees(angle), Image.BICUBIC, expand=True), float) / 255
    put(blood[age], x, y, out)
    for _ in range(int(r.integers(2, 4))):
        runs_late.append((x + r.uniform(0.3, 0.6) * out.shape[1], y + H * r.uniform(0.75, 0.9), r.uniform(2.4 * S, 3.2 * S), r.uniform(120 * S, 380 * S), age))


def wipe(age, x, y, length, width, bend, r=rng):
    """A rag pulled across the wall in an arc: a broad, streaked, thin film."""
    h, w = int(width * 2 + abs(bend) + 40 * S), int(length + 40 * S)
    ph, pw = np.mgrid[0:h, 0:w]
    t = (pw - 20 * S) / length
    centre = 20 * S + width + bend * 4 * t * (1 - t)
    band = smooth(1 - np.abs(ph - centre) / width, 0.0, 0.35) * smooth(t, -0.02, 0.15) * smooth(1 - t, -0.02, 0.4)
    stri = local_noise(h, w, 1.0, r, stretch=(1.0, 0.02))
    blot = local_noise(h, w, 1.8, r)
    put(blood[age], x, y, band * (0.10 + 0.40 * smooth(stri, 0.3, 0.8)) * (0.4 + 0.6 * blot) * (1 - 0.8 * t))


runs_late = []
smear("mid", E[5][0], E[5][1], drag=190 * S, angle=rng.choice([-1, 1]) * rng.uniform(0.2, 0.4))
wipe("old", E[6][0], E[6][1], 520 * S, 55 * S, -120 * S)
wipe("old", E[0][0] + 150 * S, E[0][1] - 300 * S, 380 * S, 40 * S, -90 * S)                 # the scrubbing at the old impact
late = {a: Layer() for a in AGES}
L = late
for x, y, w, vol, age in runs_late:
    run(age, x, y, w, vol)
for a in AGES:
    blood[a] = np.maximum(blood[a], late[a].render())

# composite: thin film tints the tile (its texture shows through), thick goes opaque.
# Blood soaks into the joints: once there it stays darker, and long after the
# wall is scrubbed, a stain stays in the grout.
grout = 1 - face
for a in AGES:
    blood[a] = np.clip(blood[a] * (1 + 0.15 * grout), 0, 1)
old_ghost = np.clip(blur(blood["old"] + 0.6 * blood["mid"], 25.0 * S) * 4, 0, 1) * grout
img = mix(img, img * np.array([0.78, 0.66, 0.60]), old_ghost * 0.6)
del old_ghost, grout

flake = noise(0.5, seed=SEED + 8)
crust = noise(1.0, seed=SEED + 9)
TINT = {   # multiply at full cover: thin film, then thick
    "fresh": (np.array([0.66, 0.35, 0.33]), hexc("#662826")),
    "mid": (np.array([0.62, 0.36, 0.33]), hexc("#5e2c26")),
    "old": (np.array([0.74, 0.56, 0.46]), hexc("#6c4a3a")),
}
for a in AGES:
    b = blood[a]
    if a == "old":
        b = b * (0.45 + 0.55 * crust) * (flake < 0.82)                  # scrubbed and flaking
    elif a == "mid":
        b = b * (0.75 + 0.25 * crust)
    ring_ = np.clip(b - blur(b, 1.2 * S), 0, 1)                             # the darker rim a drop dries to
    thick = smooth(b, 0.55, 1.0) + 0.6 * ring_
    thin, deep = TINT[a]
    film = img * mix(np.ones(3), thin, smooth(b, 0.0, 0.6))
    img = mix(film, deep * (0.95 + 0.1 * crust)[..., None], np.clip(thick, 0, 1) * 0.85)
del b, ring_, thick, film, flake, crust

# a dried antiseptic splash: orange-brown, tide-marked at its edge, a run or two
ANTI = np.zeros((NH, NW))
for _ in range(2):
    R0 = int(rng.uniform(60, 110))                                      # px at 240 DPI
    R = round(R0 * S)
    n = local_noise(2 * R, 2 * R, 2.0, rng, base=(2 * R0, 2 * R0))
    vy, vx = np.mgrid[-R:R, -R:R]
    d = np.hypot(vx, vy) / R + 0.6 * (n - 0.5)
    patch = smooth(-d, -0.8, -0.7) * 0.35 + 0.65 * np.exp(-((d - 0.78) / 0.03) ** 2)
    x0, y0 = rng.uniform(0, NW), rng.uniform(200 * S, FLOOR - 400 * S)
    put(ANTI, x0, y0, patch)
    src = np.zeros((NH, NW))
    for _ in range(int(rng.integers(1, 3))):
        src[int(y0 + R * 1.6) % NH, int(x0 + R + rng.normal(0, R * 0.4)) % NW] = 1
    dr_ = circ_conv(src, *drip(160.0 * S, 2.2 * S))
    ANTI = np.maximum(ANTI, np.clip(dr_ / dr_.max(), 0, 1) * 0.6)
img = mix(img, img * np.array([0.86, 0.66, 0.42]), np.clip(ANTI, 0, 1) * 0.65)
del src, dr_

# ── 6. mould in the joints, worst low down and round the wet ────────────────
print("mould", flush=True)
mn = noise(1.1, seed=SEED + 10)
speck = noise(0.3, seed=SEED + 11)
wet = np.clip(0.3 * floor + 0.9 * blur(G, 40 * S) * 6 + 0.8 * ws + 0.6 * np.clip(blur(tide, 30 * S) * 8, 0, 1), 0, 1)
near_joint = np.exp(-np.clip(dmin, 0, None) / (5.0 * S))   # 1 in the joint, creeping onto the glaze
colony = smooth(mn + 0.45 * wet, 0.62, 0.9)
mould = colony * near_joint * smooth(speck, 0.62 - 0.22 * colony, 0.72)      # spotty, and denser where it has taken hold
del mn, speck, wet, near_joint, colony, G, ws, tide, dmin
img = mix(img, img * np.array([0.90, 0.93, 0.84]), np.clip(blur(mould, 5.0 * S) * 2, 0, 1) * 0.5)   # the stain round a colony
img = mix(img, hexc("#3e4636") * (0.9 + 0.2 * fine)[..., None], np.clip(mould, 0, 1) * 0.85)

# Quantised in two parts: the fluids are a sliver of the tile, and a median cut
# over the whole of it gives them a handful of browns; so the wall gets WALL_COLOURS
# and the stains the rest, cut from their own pixels.
WALL_COLOURS, COLOURS = 124, 160
rgb8 = (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)
del img, mould, face, fine
stained = (sum(blood.values()) + ANTI + rs) > 0.06


def cut(px, n):
    return Image.fromarray(px.reshape(1, -1, 3)).quantize(colors=n, method=Image.Quantize.MEDIANCUT).getpalette()[:3 * n]


pal = cut(rgb8[~stained], WALL_COLOURS) + cut(rgb8[stained], COLOURS - WALL_COLOURS)
ref = Image.new("P", (1, 1))
ref.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
out = Image.fromarray(rgb8, "RGB").quantize(palette=ref, dither=Image.Dither.NONE)
out.putpalette(pal)
out.save(ROOT / "images/wall-10.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-10.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  {TX}x{TY} tiles  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
print("events", [(int(x), int(y)) for x, y in E])
