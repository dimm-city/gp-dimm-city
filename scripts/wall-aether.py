"""Draw wall 11, a wall torn into the aether (`@page wall-11`), as images/wall-11.png.

    python3 scripts/wall-aether.py       (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

The Etherlock's wall: rough stone and riveted metal, torn open in a few places
where the aether is pulling it through.

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the shadows and streaks are circular
convolutions, the courses, plates and cracks are laid on the tile's torus,
and each rift is worked in its own window, read and written with wrap-around.

What it draws, back to front:
1. Masonry: rough, rock-faced stones in uneven courses (each course its own
   height, each stone its own length, tone and warmth, some split into two,
   one on the other), their outlines wobbled by noise and their joints
   leaning, pitched faces with flat chisel facets, mortar in recessed joints.
2. Metal over it: patches bolted or riveted over the rock, two panels of a
   few plates lapped together, a column of lapped plates up the wall and two
   iron bands right across it (one through a rift), brushed, rusted at the
   edges, rust running down from the rivets.
3. Light from the upper left over one height field (stone, mortar, plates,
   rivets): faces shaded by their slope, cast shadows, dark joints. Then
   grime (before the rifts, so a shard carries its own).
4. The rifts (RIFTS: four, of different sizes): each a jagged tear with
   splinters off its sides. Round it the wall is drawn toward the tear and
   swirled about it, then broken into shards along its own joints and plate
   edges and across them, finer nearer the tear; each shard pulled toward it,
   turned, shrunk, stretched along the pull, lifted (a shadow under it),
   lit on the side that faces the tear and fading into the aether; some gone
   already, leaving the wall's dark broken core between them. Crumbs drift
   in and over the tear. The tear shows the aether: deep indigo with
   swirling violet and teal bands, faint stars and broken rings of
   glyph-like arcs. Its light is drawn in flat opaque bands, not a glow: a
   teal edge inside the tear, an amber lip (Etherlock's gold) outside it,
   then a lavender band fading out over the wall. Hairline cracks run out
   from it, the near ones lit violet from within.
5. The marks, drawn at the page's scale (0.5in to 2.5in across), each of its
   own kind and placed at random and kept apart, on a random stream of their
   own, so the wall above is unchanged by them. The surface itself is warped
   toward each rift (courses and plate edges bowed, the far side lit and the
   near side shaded). Occult circles, chiselled (short cuts, a drilled dot)
   or scratched, with invented signs between two rings and a figure inside.
   Violet where the aether touched: forking burns (a charred fern of a track,
   the stone scorched round it, a blister and sparks' pits) and stains seeped
   from a joint and run down below it. Ash, which is a powder and drawn as grains: low drifts heaped on
   the ledges with cinders in them and specks sifted down the wall below, and
   dry streaks smeared across it by a paw or something broad.
It is then quantised to an exact palette, as the other walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is), with
AETHER_COLOURS of its 160 kept for the tears and their light: a median cut
over the whole tile spends almost nothing on so few pixels and greys them.

At DPI (300) the tile is 18in x 12in, wider than a spread
and taller than a page, so a spread shows no repeat. No blotch is larger
than FEATURE (8in). The voids are its darkest colours and are kept small and
inside DriveThruRPG's 240% TAC. Its courses run across the sheet, so
wall-tiles.py anchors it to the sheet, not the text area, and offsets a right
page by the left page's width: a rift the spine cuts carries on across the
spread.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wall_fft import fft2, ifft2, irfft2, rfft2  # noqa: E402  (numpy's real FFTs, spread over the cores)

ROOT = Path(__file__).resolve().parents[1]
DPI = 300
S = DPI / 240               # every length was set in px at 240 DPI: S keeps it the same in inches
NW, NH = 18 * DPI, 12 * DPI  # px; 18in x 12in: wider than a spread and taller than a page, so a spread shows no repeat
FEATURE = 8 * DPI           # px (8in): the largest blotch of grime or rust, whatever the tile's size
SEED = 11
SHADE = 1.0                 # the whole tile
SS = 4                      # the tears are drawn at SS x and boxed down
AETHER_COLOURS = 28         # of the palette's 160, kept for the tears and their light

# the rifts: (centre x, y, half-length, half-width at the widest, px), spread
# over the tile so that a page shows one or two and a spread three or four.
# The voids are the darkest thing on the wall, so they are kept small
RIFTS = [tuple(v * S for v in rift) for rift in
         [(700, 1650, 320, 54), (2050, 560, 250, 44), (3020, 2080, 195, 36), (3880, 980, 140, 27)]]

rng = np.random.default_rng(SEED)
yy = np.arange(NH, dtype=np.float32)[:, None]   # a column and a row: they broadcast, so the tile-sized grids are never stored
xx = np.arange(NW, dtype=np.float32)[None, :]


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def white_noise(r, h, w):
    """White noise on an h x w grid. Its coarse part (every frequency a 240 DPI
    grid holds) is the field r draws at 240 DPI, so a field keeps its shape at
    any DPI; the finer frequencies come after it."""
    h0, w0 = round(h / S), round(w / S)
    lo = r.standard_normal((h0, w0), dtype=np.float32)
    if (h0, w0) == (h, w):
        return lo
    F = fft2(r.standard_normal((h, w), dtype=np.float32))
    G = fft2(lo)
    g = math.sqrt(h * w / (h0 * w0))
    my, mx = (h0 - 1) // 2, (w0 - 1) // 2     # frequencies 0..+-my down, 0..+-mx across: the 240 DPI grid's
    for ty, sy in ((slice(0, my + 1), slice(0, my + 1)), (slice(h - my, h), slice(h0 - my, h0))):
        for tx, sx in ((slice(0, mx + 1), slice(0, mx + 1)), (slice(w - mx, w), slice(w0 - mx, w0))):
            F[ty, tx] = G[sy, sx] * g
    return np.real(ifft2(F)).astype(np.float32)


def noise(beta, stretch=(1.0, 1.0), seed=None, feature=FEATURE):
    """Periodic 1/f^beta noise over the tile, normalised to mean 0 and sd 1.
    `stretch` (sx, sy) < 1 elongates it along that axis."""
    r = np.random.default_rng(seed)
    white = white_noise(r, NH, NW)
    fy = np.fft.fftfreq(NH)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(NW)[None, :] * stretch[0]
    f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)       # no blotch larger than FEATURE
    f[0, 0] = 1.0
    out = irfft2(rfft2(white) / f ** beta, s=(NH, NW)).astype(np.float32)
    out -= out.mean()
    out /= out.std()
    return out


ky = np.where(yy > NH // 2, yy - NH, yy)     # signed offsets round the torus: a column and a row
kx = np.where(xx > NW // 2, xx - NW, xx)


def circ_conv(img, kernel):
    return irfft2(rfft2(img) * rfft2(kernel), s=(NH, NW)).astype(np.float32)


def gauss_kernel(sigma, dx=0.0, dy=0.0):
    k = np.exp(-(((kx - dx) ** 2 + (ky - dy) ** 2) / (2 * sigma * sigma)))
    return k / k.sum()


def blur(m, sigma, dx=0.0, dy=0.0):
    return circ_conv(m, gauss_kernel(sigma, dx, dy))


def shift(m, dy, dx):
    """np.roll by (dy, dx) px, fractions too: linear between the whole-pixel rolls."""
    out = 0
    for oy, wy in ((math.floor(dy), 1 - dy + math.floor(dy)), (math.floor(dy) + 1, dy - math.floor(dy))):
        for ox, wx in ((math.floor(dx), 1 - dx + math.floor(dx)), (math.floor(dx) + 1, dx - math.floor(dx))):
            if wy * wx:
                out = out + wy * wx * np.roll(m, (oy, ox), (0, 1))
    return out


def drip(length, width):
    return np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    u = 3 - 2 * t
    t *= t
    t *= u
    return t


def mix(a, b, t):
    t = np.asarray(t, np.float32)
    if t.ndim == 2:
        t = t[..., None]
    d = np.subtract(b, a)          # a + (b - a) * t, in the one new buffer where its shape and type allow
    inplace = d.shape == np.broadcast_shapes(d.shape, t.shape) and np.result_type(d, t) == d.dtype
    d = np.multiply(d, t, out=d if inplace else None)
    d += a
    return d


def jag(pts, rough, r, step=5):
    """A jagged fracture through `pts`: midpoint displacement, kept near each chord."""
    pts = [np.array(p, float) for p in pts]
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


def partition(total, lo, hi, r):
    """Cut `total` px into pieces between about lo and hi: the cut positions."""
    sizes, s = [], 0.0
    while s < total:
        v = r.uniform(lo, hi)
        sizes.append(v)
        s += v
    if s - total > sizes[-1] / 2 and len(sizes) > 1:
        s -= sizes.pop()
    sizes = np.array(sizes) * total / s
    edges = np.round(np.concatenate([[0], np.cumsum(sizes)])).astype(int)
    edges[-1] = total
    return edges


# ── where the rifts are: a few, spread out on the tile's torus ────────────────
rifts = []
for i, (cx, cy, L, w0) in enumerate(RIFTS):
    ang = float(rng.choice([-1, 1]) * rng.uniform(0.25, 1.35))     # never quite level
    rifts.append(dict(cx=float(cx + rng.normal(0, 40 * S)), cy=float(cy + rng.normal(0, 40 * S)), L=L, w0=w0, ang=ang,
                      spin=float(rng.choice([-1, 1])), Z=0.42 * L + 70 * S, seed=SEED * 100 + i))

# ── global fields (all periodic) ───────────────────────────────────────────────
print("fields", flush=True)
warp_x = noise(1.9, seed=SEED + 1) * (7 * S) + noise(1.0, seed=SEED + 2) * (2.0 * S)
warp_y = noise(1.9, seed=SEED + 3) * (7 * S) + noise(1.0, seed=SEED + 4) * (2.0 * S)
lump = noise(1.6, seed=SEED + 5, feature=300 * S)                    # pitched rock faces
rough = noise(0.9, seed=SEED + 6)                                # the rock's surface
speck = noise(0.3, seed=SEED + 7)                                # grain in the stone
mottle = noise(1.8, seed=SEED + 8)
grime = noise(1.9, seed=SEED + 9)
sand = noise(0.5, seed=SEED + 10)
jointn = noise(1.3, seed=SEED + 11, feature=400 * S)
rustn = noise(1.7, seed=SEED + 12)
rustf = noise(1.0, seed=SEED + 13)
grain_h = noise(1.2, stretch=(0.04, 1.0), seed=SEED + 14)        # brushing, long along x
grain_v = noise(1.2, stretch=(1.0, 0.04), seed=SEED + 15)        # long along y
crust = noise(0.4, seed=SEED + 16)
streakn = noise(1.0, stretch=(1.0, 0.12), seed=SEED + 17)
bandn = noise(1.4, seed=SEED + 18, feature=500 * S)                  # the aether's swirl, and the light's wobble
soft = noise(2.6, seed=SEED + 22, feature=600 * S)                   # the reach of a rift's pull: smooth, no speckle

# ── 1. masonry: rough stones in uneven courses ─────────────────────────────────
print("masonry", flush=True)
WX = (xx + warp_x) % NW
WY = (yy + warp_y) % NH
row_edges = partition(NH, 125 * S, 290 * S, rng)
slant = noise(1.6, seed=SEED + 19, feature=700 * S) * 0.09         # the joints lean, each its own way
unit = np.zeros((NH, NW), np.int32)          # which stone or plate each pixel belongs to
e_st = np.zeros((NH, NW), np.float32)        # distance in from the stone's edge (rounded corners)
row = np.clip(np.searchsorted(row_edges, WY, "right") - 1, 0, len(row_edges) - 2)
n_units = 0
stone_tone, stone_warm = [], []
for r in range(len(row_edges) - 1):
    sel = row == r
    h = float(row_edges[r + 1] - row_edges[r])
    ly = WY[sel] - row_edges[r]
    ce = partition(NW, 150 * S, 520 * S, rng)
    off = rng.uniform(0, NW)
    X = (WX[sel] - off + slant[sel] * (ly - h / 2)) % NW
    col = np.clip(np.searchsorted(ce, X, "right") - 1, 0, len(ce) - 2)
    lx = X - ce[col]
    w = (ce[col + 1] - ce[col]).astype(np.float32)
    nc = len(ce) - 1
    split = rng.random(nc) < 0.24                     # two smaller stones, one on the other
    sy = (rng.uniform(0.35, 0.65, nc) * h)[col]
    dsplit = np.where(split[col], np.abs(ly - sy), 1e4)
    K = 7.0 * S                               # soft minimum: the corners rounded off
    d = np.stack([lx, w - lx, ly, h - ly, dsplit])
    e_st[sel] = -K * np.log(np.exp(-d / K).sum(0))
    unit[sel] = n_units + 2 * col + (split[col] & (ly < sy))
    stone_tone += list(np.clip(rng.normal(1.0, 0.04, 2 * nc), 0.90, 1.09))
    stone_warm += list(rng.uniform(-0.6, 0.6, 2 * nc))
    n_units += 2 * nc
del row, WX, WY, slant
stone_tone = np.array(stone_tone, np.float32)
stone_warm = np.array(stone_warm, np.float32)


def facets(s, seed):
    """Periodic jittered-grid Voronoi cells of s px (s divides NW and NH): the
    chisel's flat faces on the rock."""
    r = np.random.default_rng(seed)
    nx, ny = NW // s, NH // s
    jit = r.uniform(0.05, 0.95, (ny, nx, 2)).astype(np.float32)
    gx_, gy_ = (xx[0] // s).astype(np.int32), (yy[:, 0] // s).astype(np.int32)   # each column's cell, each row's
    best = np.full((NH, NW), 1e9)
    bid = np.zeros((NH, NW), np.int32)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            cx_, cy_ = gx_ + ox, gy_ + oy
            wx_, wy_ = cx_ % nx, cy_ % ny
            # a distance's x part depends only on the column and the row of cells,
            # its y part on the row and the column of cells: worked out small, then spread
            d = ((xx[0] - (cx_ + jit[:, wx_, 0]) * s) ** 2)[wy_]
            d += ((yy[:, 0, None] - (cy_[:, None] + jit[wy_, :, 1]) * s) ** 2)[:, wx_]
            closer = d < best
            np.copyto(best, d, where=closer)
            np.copyto(bid, wy_[:, None] * nx + wx_, where=closer)
    return bid


fid = facets(round(48 * S), SEED + 20)
ftab = np.random.default_rng(SEED + 21).normal(0, 1, 8191).astype(np.float32)
fshade = ftab[(fid.astype(np.int64) * 7919 + unit.astype(np.int64) * 104729) % 8191]
del fid

jw = np.clip(3.8 + 1.6 * jointn, 2.0, 7.0) * S               # half the joint's width
t_in = e_st - jw
stone_a = np.clip(t_in + 0.5, 0, 1)
H = np.where(t_in > 0,
             (5 * smooth(t_in, 0, 7 * S) + 7 * smooth(t_in, 5 * S, 45 * S) * (0.5 + 0.5 * np.tanh(lump))) * S,
             1.2 * S * sand).astype(np.float32)
STONE = hexc("#b1aea6")
WARM = np.array([0.020, 0.006, -0.018], np.float32)
tone = stone_tone[unit] * (1 + 0.03 * mottle + 0.006 * speck) * (1 + 0.038 * np.tanh(fshade) * smooth(t_in, 2 * S, 8 * S))
img = STONE * tone[..., None] + WARM * stone_warm[unit][..., None]
del fshade
img *= (1 - 0.18 * smooth(speck, 2.1, 2.7))[..., None]           # dark flecks
MORTAR = hexc("#99938a")
img = mix(MORTAR * (0.97 + 0.02 * sand)[..., None], img, stone_a)
del t_in, e_st

# ── 2. metal: patches, a column of lapped plates, two bands ───────────────────
print("metal", flush=True)
STEEL = {"steel": hexc("#a4a8a9"), "iron": hexc("#939593"), "brass": hexc("#a7a18c")}
RUST = (hexc("#6b4632"), hexc("#946044"), hexc("#ad8361"))
plates = []
for _ in range(10):                          # patches bolted or riveted over the rock
    plates.append(dict(cx=rng.uniform(0, NW), cy=rng.uniform(0, NH), w=rng.uniform(200 * S, 540 * S), h=rng.uniform(150 * S, 400 * S),
                       ang=float(rng.normal(0, 0.035)), kind=str(rng.choice(["steel", "iron", "brass"], p=[0.5, 0.35, 0.15])),
                       fix=str(rng.choice(["rivet", "bolt"])), cham=rng.uniform(0, 14 * S)))
col_x = 1400.0 * S                             # a column of lapped plates, the tile's full height
for y0, y1 in zip(*(lambda e: (e[:-1], e[1:]))(partition(NH, 380 * S, 620 * S, rng))):
    plates.append(dict(cx=col_x + rng.normal(0, 5 * S), cy=(y0 + y1) / 2 + 6 * S, w=470 * S + rng.normal(0, 6 * S), h=(y1 - y0) + 16 * S,
                       ang=float(rng.normal(0, 0.006)), kind="steel" if rng.random() < 0.6 else "iron", fix="rivet", cham=0.0))
for x0, y0, nx, ny in ((2330, 1060, 2, 2), (3450, 2420, 3, 1)):    # panels: a few plates lapped together
    pw, ph = rng.uniform(300 * S, 380 * S), rng.uniform(260 * S, 320 * S)
    for j in range(ny):
        for i in range(nx):
            plates.append(dict(cx=x0 * S + i * (pw - 14 * S) + rng.normal(0, 4 * S), cy=y0 * S + j * (ph - 14 * S) + rng.normal(0, 4 * S),
                               w=pw + rng.normal(0, 6 * S), h=ph + rng.normal(0, 6 * S), ang=float(rng.normal(0, 0.008)),
                               kind=str(rng.choice(["steel", "iron"])), fix="rivet", cham=0.0))
for y in (640, 2110):                        # bands right across it, one through a rift
    plates.append(dict(cx=0.0, cy=y * S + rng.normal(0, 10 * S), w=None, h=rng.uniform(56 * S, 74 * S), ang=0.0, kind="iron", fix="rivet", cham=0.0))
rust_src = np.zeros((NH, NW), np.float32)

for k, p in enumerate(plates):
    uid = n_units + k
    weather = rng.uniform(-0.5, 0.6)
    if p["w"] is None:                       # a band: the tile's full width
        rows_ = np.arange(int(p["cy"] - p["h"] / 2 - 10 * S), int(p["cy"] + p["h"] / 2 + 12 * S)) % NH
        cols_ = np.arange(NW)
        V = (np.arange(len(rows_)) + int(p["cy"] - p["h"] / 2 - 10 * S) - p["cy"])[:, None].astype(np.float32) * np.ones((1, NW), np.float32)
        U = np.broadcast_to(np.arange(NW, dtype=np.float32)[None, :], V.shape)
        e = p["h"] / 2 - np.abs(V)
        ex = None
    else:
        R = int(math.hypot(p["w"], p["h"]) / 2 + 14 * S)
        rows_ = np.arange(int(p["cy"]) - R, int(p["cy"]) + R + 1) % NH
        cols_ = np.arange(int(p["cx"]) - R, int(p["cx"]) + R + 1) % NW
        dy, dx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
        dy += int(p["cy"]) - p["cy"]
        dx += int(p["cx"]) - p["cx"]
        ca, sa = math.cos(p["ang"]), math.sin(p["ang"])
        U = dx * ca + dy * sa
        V = -dx * sa + dy * ca
        ex = p["w"] / 2 - np.abs(U)
        ey = p["h"] / 2 - np.abs(V)
        e = np.minimum(ex, ey)
        if p["cham"] > 0:
            e = np.minimum(e, (ex + ey) / math.sqrt(2) - p["cham"] * 0.3)
    ix = np.ix_(rows_, cols_)
    a = np.clip(e + 0.5, 0, 1)
    grain = grain_v[ix] if abs(p["ang"]) > 0.7 else grain_h[ix]
    base = STEEL[p["kind"]] * rng.uniform(0.95, 1.04)
    met = base * (1 + 0.05 * grain + 0.04 * mottle[ix] + 0.015 * crust[ix])[..., None]
    near = np.exp(-np.maximum(e, 0) / (28 * S))
    rf = 0.55 * rustn[ix] + 0.35 * rustf[ix] + 1.4 * near + weather
    rust = smooth(rf, 1.0, 1.9)
    rust = np.maximum(rust, 0.7 * smooth(crust[ix], 2.2, 2.9))
    depth = smooth(rustf[ix], -0.4, 1.4)[..., None]
    rcol = mix(mix(RUST[2], RUST[1], smooth(rustf[ix], -1.0, 0.4)), RUST[0], depth)
    rcol = rcol * (0.88 + 0.12 * crust[ix])[..., None]
    rcol = rcol * 0.8 + rcol.mean(-1, keepdims=True) * 0.2                       # muted: a background
    met = mix(met, rcol, rust * 0.85)
    Hp = (15 + 3 * smooth(e, 0, 5 * S) + 0.4 * grain) * S
    # rivets or bolts along the edges
    heads = []
    if p["w"] is None:
        off = rng.uniform(0, 90 * S)
        for t in np.arange(off, NW + off, 90 * S):
            for s in (-1, 1):
                heads.append((t % NW, s * (p["h"] / 2 - 14 * S), 7.0 * S))
    elif p["fix"] == "rivet":
        for (L_, side) in ((p["w"], "h"), (p["h"], "v")):
            n = max(2, int(L_ / (70 * S)))
            for t in np.linspace(-L_ / 2 + 18 * S, L_ / 2 - 18 * S, n):
                for s in (-1, 1):
                    if side == "h":
                        heads.append((t, s * (p["h"] / 2 - 16 * S), 6.5 * S))
                    else:
                        heads.append((s * (p["w"] / 2 - 16 * S), t, 6.5 * S))
    else:
        for sx in (-1, 1):
            for sy in (-1, 1):
                heads.append((sx * (p["w"] / 2 - 20 * S), sy * (p["h"] / 2 - 20 * S), 10.0 * S))
        if p["w"] > 380 * S:
            heads += [(0.0, s * (p["h"] / 2 - 20 * S), 10.0 * S) for s in (-1, 1)]
    hd = np.full(U.shape, 1e9, np.float32)
    hr = np.zeros(U.shape, np.float32)
    for (hu, hv, r_) in heads:
        du = U - hu
        if p["w"] is None:
            du = (du + NW / 2) % NW - NW / 2
        dd = np.hypot(du, V - hv) / r_
        closer = dd < hd
        hd = np.where(closer, dd, hd)
        hr = np.where(closer, r_, hr)
        if p["w"] is None:
            gx_, gy_ = hu, p["cy"] + hv
        else:
            gx_ = p["cx"] + hu * math.cos(p["ang"]) - hv * math.sin(p["ang"])
            gy_ = p["cy"] + hu * math.sin(p["ang"]) + hv * math.cos(p["ang"])
        if rng.random() < 0.35:
            rust_src[int(gy_ + r_) % NH, int(gx_) % NW] += rng.uniform(0.4, 1.0)
    dome = np.sqrt(np.clip(1 - hd * hd, 0, 1))
    if p["fix"] == "bolt" and p["w"] is not None:
        dome = np.where(hd < 1, 0.55 + 0.45 * smooth(1 - hd, 0, 0.25), 0)        # a hex-ish bolt: flat topped
    Hp = Hp + 5.5 * S * dome * (hr / (7 * S))
    met = mix(met, met * 1.04, (hd < 1).astype(np.float32) * 0.6)
    # the foot of the plate: a few drips where it sits on the rock
    if p["w"] is not None:
        for _ in range(int(rng.integers(1, 4))):
            t = rng.uniform(-0.45, 0.45) * p["w"]
            gx_ = p["cx"] + t * math.cos(p["ang"]) - (p["h"] / 2) * math.sin(p["ang"])
            gy_ = p["cy"] + t * math.sin(p["ang"]) + (p["h"] / 2) * math.cos(p["ang"])
            rust_src[int(gy_ + 2 * S) % NH, int(gx_) % NW] += rng.uniform(0.3, 0.8)
    img[ix] = mix(img[ix], met, a)
    H[ix] = np.where(a > 0, H[ix] * (1 - a) + Hp * a, H[ix])
    unit[ix] = np.where(a > 0.5, uid, unit[ix])
n_units += len(plates)

streaks = circ_conv(rust_src, drip(150.0 * S, 2.5 * S))
streaks = np.clip(streaks / np.percentile(streaks[streaks > 1e-4], 99), 0, 1)
streaks *= smooth(streakn, -0.6, 0.8)
img = mix(img, img * np.array([0.84, 0.76, 0.68], np.float32), streaks * 0.55)
del rust_src, streaks

# ── hairline cracks: out of the rifts, and a few elsewhere ────────────────────
crack_l = Image.new("L", (NW * SS, NH * SS), 0)            # drawn at SS x and boxed down: S px wide
crack_d = ImageDraw.Draw(crack_l)


def wall_crack(x, y, heading, length, width, r):
    pts, a = [(x, y)], heading
    while length > 0:
        step = r.uniform(7 * S, 18 * S)
        a += r.normal(0, 0.22)
        x, y = x + step * math.cos(a), y + step * math.sin(a)
        pts.append((x, y))
        length -= step
        if r.random() < 0.07:
            wall_crack(x, y, a + r.choice([-1, 1]) * r.uniform(0.5, 1.1), length * 0.55, max(S, width - S), r)
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            crack_d.line([((px + ox) * SS, (py + oy) * SS) for px, py in pts], fill=255, width=round(width * SS), joint="curve")


for rf in rifts:
    for _ in range(int(rng.integers(3, 5))):
        a = rng.uniform(0, 2 * math.pi)
        reach = rf["Z"] * rng.uniform(0.9, 1.3)
        x = rf["cx"] + math.cos(a) * reach + math.cos(rf["ang"]) * rng.uniform(-1, 1) * rf["L"] * 0.5
        y = rf["cy"] + math.sin(a) * reach + math.sin(rf["ang"]) * rng.uniform(-1, 1) * rf["L"] * 0.5
        wall_crack(x, y, a, rng.uniform(90 * S, 240 * S), S, rng)
for _ in range(8):
    wall_crack(rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, 2 * math.pi), rng.uniform(60 * S, 200 * S), S, rng)
cracks = np.asarray(crack_l.resize((NW, NH), Image.BOX), np.float32) / 255
del crack_l, crack_d
H -= 4 * S * cracks

# ── 3. light from the upper left ───────────────────────────────────────────────
print("light", flush=True)
gx = (np.roll(H, -1, 1) - np.roll(H, 1, 1)) / 2
gy = (np.roll(H, -1, 0) - np.roll(H, 1, 0)) / 2
lit = np.clip((gx + gy) / math.sqrt(2), -1.5, 1.5)
img *= (1 + 0.26 * np.tanh(lit * 0.8))[..., None]
cast = np.clip(shift(H, 4 * S, 4 * S) - H - 1.5 * S, 0, 10 * S) / (10 * S)
cast = np.clip(blur(cast, 1.8 * S), 0, 1)
img *= (1 - 0.32 * cast)[..., None]
ao = np.clip(blur(H, 7 * S) - H, 0, 8 * S) / (8 * S)
img *= (1 - 0.22 * ao)[..., None]
del gx, gy, lit, cast, ao

# ── grime (before the rifts: a shard carries its own) ─────────────────────────
img *= (1 - 0.07 * smooth(grime, -0.3, 1.8) - 0.02 * sand)[..., None]
img *= (1 - 0.05 * smooth(streakn, 0.3, 1.8))[..., None]

# ── 4. the rifts ──────────────────────────────────────────────────────────────
VOID_DEEP = hexc("#2f2950")
VOID = hexc("#3a3264")
VIOLET = hexc("#4f4180")
VIOLET_L = hexc("#6a5a9c")
TEAL = hexc("#2e5866")
TEAL_L = hexc("#4f9692")
AMBER_L = hexc("#e2c784")
AMBER = hexc("#bd9a52")
LAVENDER = hexc("#a99cc8")
CORE = hexc("#625d68")
STAR = (hexc("#d6d0ee"), hexc("#b4e2dc"), hexc("#ecd8a4"))


def seg_dist(X, Y, segs, dmax, D):
    """min(D, distance to the segments), each worked only within dmax of it."""
    hgt, wid = D.shape
    for (ax, ay), (bx, by) in segs:
        x0, x1 = int(max(0, min(ax, bx) - dmax)), int(min(wid, max(ax, bx) + dmax + 1))
        y0, y1 = int(max(0, min(ay, by) - dmax)), int(min(hgt, max(ay, by) + dmax + 1))
        if x0 >= x1 or y0 >= y1:
            continue
        px, py = X[y0:y1, x0:x1] - ax, Y[y0:y1, x0:x1] - ay
        vx, vy = bx - ax, by - ay
        L2 = vx * vx + vy * vy
        t = np.clip((px * vx + py * vy) / L2, 0, 1) if L2 > 0 else 0
        d = np.hypot(px - t * vx, py - t * vy)
        np.minimum(D[y0:y1, x0:x1], d, out=D[y0:y1, x0:x1])
    return D


def worley(X, Y, s, r):
    """Jittered-grid Voronoi cells of about s px: each pixel's cell id."""
    gx_, gy_ = np.floor(X / s).astype(int), np.floor(Y / s).astype(int)
    nx, ny = gx_.max() + 3, gy_.max() + 3
    jit = r.uniform(0.1, 0.9, (ny, nx, 2))
    cy_, cx_ = np.mgrid[0:ny, 0:nx]
    px, py = ((cx_ + jit[..., 0]) * s).ravel(), ((cy_ + jit[..., 1]) * s).ravel()   # each cell's point, by cell id
    rows = [np.clip(gy_ + o, 0, ny - 1) * nx for o in (-1, 0, 1)]
    cols = [np.clip(gx_ + o, 0, nx - 1) for o in (-1, 0, 1)]
    del gx_, gy_
    best = np.full(X.shape, 1e9)
    bid = np.zeros(X.shape, np.int64)
    for row in rows:
        for col in cols:
            c = row + col
            d = (X - px[c]) ** 2 + (Y - py[c]) ** 2
            closer = d < best
            np.copyto(best, d, where=closer)
            np.copyto(bid, c, where=closer)
    return bid


def wblur(a, sigma):
    """Gaussian blur of a window (its edges wrap, which nothing near them minds)."""
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    g = np.exp(-2 * (math.pi * sigma) ** 2 * (fx * fx + fy * fy))
    return irfft2(rfft2(a) * g, s=(h, w)).astype(np.float32)


def sample(src, Y, X):
    """Bilinear, wrapped on the tile."""
    x0, y0 = np.floor(X), np.floor(Y)
    fx, fy = (X - x0)[..., None], (Y - y0)[..., None]
    x0, y0 = x0.astype(int) % NW, y0.astype(int) % NH
    x1, y1 = (x0 + 1) % NW, (y0 + 1) % NH
    return ((src[y0, x0] * (1 - fx) + src[y0, x1] * fx) * (1 - fy) +
            (src[y1, x0] * (1 - fx) + src[y1, x1] * fx) * fy)


def tear_outline(rf, r):
    """The tear in the rift's own frame (u along it, v across): a jagged
    outline with splinters off its sides, and its coarse outline."""
    L, w0 = rf["L"], rf["w0"]
    bend = r.normal(0, 0.10) * L
    ph = r.uniform(0, 2 * math.pi)

    def centre(t):
        return bend * math.sin(math.pi * t * 0.9 + ph) * (1 - t * t) ** 0.5

    sides = []
    for s in (1, -1):
        ts, t = [], -1.0
        while t < 1.0:
            ts.append(t)
            t += r.uniform(14 * S, 34 * S) / L
        ts.append(1.0)
        pts = []
        for t in ts:
            hw = w0 * max(0.0, 1 - abs(t) ** 1.7) ** 0.75
            f = r.uniform(0.55, 1.12)
            if r.random() < 0.12:
                f *= r.uniform(0.25, 0.5)             # a notch
            elif r.random() < 0.10:
                f *= r.uniform(1.25, 1.5)             # a tooth
            pts.append((t * L, centre(t) + s * hw * f))
        # splinters off this side: narrow spikes out into the wall
        out = [pts[0]]
        for i in range(1, len(pts)):
            p0, p1 = pts[i - 1], pts[i]
            if abs(p1[0]) < 0.7 * L and r.random() < 0.13:
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                ln = r.uniform(25 * S, 95 * S) * (w0 / (40 * S)) ** 0.5
                a = math.pi / 2 * s + r.normal(0, 0.45)
                tip = (mx + ln * math.cos(a), my + ln * math.sin(a))
                out += [(mx - 3 * S + ln * 0.45 * math.cos(a) - 2 * S * s, my + ln * 0.45 * math.sin(a)), tip,
                        (mx + 3 * S + ln * 0.45 * math.cos(a) + 2 * S * s, my + ln * 0.45 * math.sin(a))]
            out.append(p1)
        sides.append(out)
    # the ends run out into thin cracks
    tipA = (-L - r.uniform(20 * S, 60 * S), centre(-1.0) + r.normal(0, 8 * S))
    tipB = (L + r.uniform(20 * S, 60 * S), centre(1.0) + r.normal(0, 8 * S))
    coarse = [tipA] + sides[0][1:-1] + [tipB] + sides[1][::-1][1:-1]
    fine = jag(coarse + [coarse[0]], 0.16, r, step=4 * S)[:-1]
    return coarse, fine


def splat(a, y, x, c, f):
    """A dot S px square from (y, x) mixed into `a`, the pixels it half covers
    in part: a star the same size at any DPI."""
    for py in range(int(y), math.ceil(y + S)):
        fy = min(py + 1, y + S) - max(py, y)
        for px in range(int(x), math.ceil(x + S)):
            fx = min(px + 1, x + S) - max(px, x)
            a[py, px] = mix(a[py, px], c, f * fy * fx)


def to_window(pts, rf, R):
    ca, sa = math.cos(rf["ang"]), math.sin(rf["ang"])
    return [(R + u * ca - v * sa, R + u * sa + v * ca) for u, v in pts]


aether = np.zeros((NH, NW), bool)            # the tears and their light: a palette of their own
for ri, rf in enumerate(rifts):
    print(f"rift {ri + 1}/{len(rifts)} at ({rf['cx']:.0f}, {rf['cy']:.0f})", flush=True)
    r = np.random.default_rng(rf["seed"])
    L, w0, Z, spin = rf["L"], rf["w0"], rf["Z"], rf["spin"]
    R = int(L + Z + 320 * S)
    SW = 2 * R + 1
    gx0, gy0 = int(rf["cx"]) - R, int(rf["cy"]) - R
    rows_ = np.arange(gy0, gy0 + SW) % NH
    cols_ = np.arange(gx0, gx0 + SW) % NW
    ix = np.ix_(rows_, cols_)
    Y, X = np.mgrid[0:SW, 0:SW].astype(np.float32)
    ca, sa = math.cos(rf["ang"]), math.sin(rf["ang"])
    Uc, Vc = (X - R) * ca + (Y - R) * sa, -(X - R) * sa + (Y - R) * ca     # the rift's frame

    coarse, fine = tear_outline(rf, r)
    cw, fw = to_window(coarse, rf, R), to_window(fine, rf, R)
    m = Image.new("L", (SW * SS, SW * SS), 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in fw], fill=255)
    inside = np.asarray(m.resize((SW, SW), Image.BOX), np.float32) / 255
    del m
    D = np.full((SW, SW), 1e6, np.float32)
    seg_dist(X, Y, list(zip(cw, cw[1:] + cw[:1])), SW, D)
    Df = np.full((SW, SW), 1e6, np.float32)
    seg_dist(X, Y, list(zip(fw, fw[1:] + fw[:1])), 64 * S, Df)
    dist = np.where(Df < 60 * S, Df, D)                    # to the tear's edge, fine near it
    del Df
    outside = inside < 0.5
    dT = np.where(outside, dist, 0)                    # out from the tear
    dI = np.where(outside, 0, dist)                    # in from its edge

    # how strongly each point is pulled: 1 at the tear, 0 at the zone's edge;
    # the zone reaches furthest from the tear's middle
    tpos = np.clip(np.abs(Uc) / (L + Z), 0, 1)
    Zloc = Z * (0.45 + 0.55 * (1 - tpos ** 2)) * np.clip(0.8 + 0.25 * soft[ix], 0.55, 1.3)
    k = np.clip(1 - dT / Zloc, 0, 1) * outside
    edge_taper = smooth(R - np.maximum(np.abs(X - R), np.abs(Y - R)), 0, 90 * S)

    # the wall drawn toward the tear and swirled about it (beyond the shards too)
    gyy, gxx = np.gradient(wblur(np.where(outside, D, -D), 14 * S))      # smooth: no flips at the outline's notches
    gn = np.hypot(gxx, gyy) + 1e-6
    ax_, ay_ = gxx / gn * np.where(outside, 1, -1), gyy / gn * np.where(outside, 1, -1)   # away from the tear
    rx, ry = X - R, Y - R
    pull = np.exp(-dT / (0.9 * Z)) * edge_taper
    m_away = 46 * S * pull
    theta = spin * (0.22 * L + 10 * S) / (0.7 * L) * (1 - smooth(dT, 0, Z + 90 * S)) ** 1.6 * edge_taper   # turned about its centre
    ct, st = np.cos(theta), np.sin(theta)
    SX = gx0 + R + ct * rx + st * ry + ax_ * m_away
    SY = gy0 + R - st * rx + ct * ry + ay_ * m_away
    del ct, st
    src = sample(img, SY, SX).astype(np.float32)
    src_u = unit[(SY.round().astype(int)) % NH, (SX.round().astype(int)) % NW]
    src_c = sample(cracks[..., None], SY, SX)[..., 0]
    del SX, SY, gyy, gxx, gn, D

    # light seeping through the cracks near the tear
    near_c = smooth(k, 0.0, 0.6)
    src = mix(src, mix(src * 0.55, VIOLET_L, 0.5 * near_c), np.clip(src_c * 1.2, 0, 1))
    src = mix(src, src * 1.08, np.clip(shift(src_c, S, S) - src_c, 0, 1) * 0.5)

    # shards: the wall's own stones and plates, cut finer toward the tear. The
    # finer cuts are laid in the tear's frame (along it, and out from it), long
    # in the direction of the pull: splinters pointing at the tear. Each cell
    # is cut finer or not as a whole, so the cracks run along cell edges and
    # never round the tear in rings
    kk = np.clip(k + 0.12 * soft[ix], 0, 1)
    along = Uc + L + Z + 50 * S
    across = np.where(Vc >= 0, 1, -1) * dT + Z + 50 * S
    cells = []
    for s, el in ((140 * S, 0), (60 * S, 1.9), (34 * S, 2.3), (20 * S, 2.6)):
        if el:
            cells.append(worley(along + 0.3 * s * np.sin(across / (s * 0.9)), across / el, s, r))
        else:                                          # the outer cracks: plain polygons
            cells.append(worley(X, Y, s, r))

    def cell_mean(c, v):
        _, inv = np.unique(c, return_inverse=True)
        inv = inv.reshape(c.shape)
        return (np.bincount(inv.ravel(), v.ravel()) / np.bincount(inv.ravel()))[inv]

    zone = (cell_mean(cells[0], k) > 0.03) & outside
    band = np.full((SW, SW), 3, np.int64)
    for b, lim in enumerate((0.30, 0.58, 0.80)):
        band = np.where((band == 3) & (cell_mean(cells[b], kk) < lim), b, band)
    cell = np.choose(band, cells)
    del cells
    lab = np.where(zone, (src_u.astype(np.int64) * 8 + band) * 200000 + cell, -1)
    del cell
    out = src.copy()
    # the wall's broken core where shards have gone: its stone, darker, lit violet nearer the tear
    core = mix(src.mean(-1, keepdims=True) * 0.25 + CORE * 0.75, VIOLET, 0.6 * smooth(k, 0.75, 1.0))
    core *= (0.95 + 0.05 * np.tanh(bandn[ix] * 2))[..., None]
    out[zone] = core[zone]
    frag = np.zeros((SW, SW), np.float32)               # shards that drifted over the void

    flat = lab[zone]
    zy, zx = np.nonzero(zone)
    order = np.argsort(flat, kind="stable")
    flat_s = flat[order]
    starts = np.r_[0, np.nonzero(np.diff(flat_s))[0] + 1, len(flat_s)]
    shards = []
    for i0, i1 in zip(starts[:-1], starts[1:]):
        if i1 - i0 < 2 * S * S:
            continue
        idx = order[i0:i1]
        ys, xs = zy[idx], zx[idx]
        cy_, cx_ = ys.mean(), xs.mean()
        kc = float(k[int(cy_), int(cx_)])
        shards.append((kc, flat_s[i0], ys, xs, cy_, cx_))
    shards.sort(key=lambda s: s[0])
    for (kc, labv, ys, xs, cy_, cx_) in shards:
        if kc > 0.62 and r.random() < 0.55 * (kc - 0.55):
            continue                                  # already gone
        iy, ixx = int(cy_), int(cx_)
        tx, ty = -ax_[iy, ixx], -ay_[iy, ixx]         # toward the tear
        nxv, nyv = -ty, tx
        dcen = float(dT[iy, ixx])
        kp = kc ** 1.4
        zl = float(Zloc[iy, ixx])
        a_mag = 0.5 * zl * kc ** 2.5 + (r.uniform(0.3, 1.3) * dcen if kc > 0.82 and r.random() < 0.2 else 0)
        b_mag = 0.3 * zl * kc ** 2.5 * r.uniform(0.5, 1.4)
        swx, swy = -(cy_ - R) * spin, (cx_ - R) * spin
        swn = math.hypot(swx, swy) + 1e-6
        dx_ = tx * a_mag + swx / swn * b_mag
        dy_ = ty * a_mag + swy / swn * b_mag
        sc = 0.992 - 0.03 * kc - 0.47 * kc ** 2
        s_al, s_pp = sc * (1 + 0.45 * kc ** 2), sc * (1 - 0.15 * kc)
        th = spin * kc ** 2 * r.uniform(0.15, 0.8) + r.normal(0, 0.02 + 0.12 * kc ** 2)
        A = np.array([[tx, nxv], [ty, nyv]]) @ np.diag([s_al, s_pp]) @ np.array([[tx, ty], [nxv, nyv]])
        Rm = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
        A = Rm @ A                                    # acts on (x, y)
        Ai = np.linalg.inv(A)
        corners = np.array([[xs.min(), ys.min()], [xs.max(), ys.min()], [xs.min(), ys.max()], [xs.max(), ys.max()]], float)
        dc = (corners - [cx_, cy_]) @ A.T + [cx_ + dx_, cy_ + dy_]
        bx0, by0 = int(max(0, dc[:, 0].min() - 3 * S)), int(max(0, dc[:, 1].min() - 3 * S))
        bx1, by1 = int(min(SW, dc[:, 0].max() + 4 * S)), int(min(SW, dc[:, 1].max() + 4 * S))
        if bx0 >= bx1 or by0 >= by1:
            continue
        DY, DX = np.mgrid[by0:by1, bx0:bx1].astype(np.float32)
        qx, qy = DX - cx_ - dx_, DY - cy_ - dy_
        sxp = Ai[0, 0] * qx + Ai[0, 1] * qy + cx_
        syp = Ai[1, 0] * qx + Ai[1, 1] * qy + cy_
        sxi, syi = np.round(sxp).astype(int), np.round(syp).astype(int)
        ok = (sxi >= 0) & (sxi < SW) & (syi >= 0) & (syi < SW)
        M = np.zeros(DX.shape, bool)
        M[ok] = lab[syi[ok], sxi[ok]] == labv
        if not M.any():
            continue
        col = np.zeros(DX.shape + (3,), np.float32)
        col[M] = src[syi[M], sxi[M]]
        # lifted: a shadow on what is under it, further off the more it is lifted
        o = int(round((1 + 11 * kc ** 1.5) * S)) if len(ys) > 40 * S * S and kc > 0.15 else 0
        sh_y, sh_x = np.nonzero(M)
        sy2, sx2 = sh_y + by0 + o, sh_x + bx0 + o
        okk = (sy2 < SW) & (sx2 < SW)
        if o:
            out[sy2[okk], sx2[okk]] *= 0.76
        # fading into the aether, lit on the side that faces the tear, dark on the far side
        col = mix(col, VIOLET_L, 0.3 * smooth(kc, 0.8, 1.0))
        sxs, sys_ = int(round(2.2 * S * tx)), int(round(2.2 * S * ty))
        lit_e = M & ~np.roll(M, (-sys_, -sxs), (0, 1))
        back = M & ~np.roll(M, (sys_, sxs), (0, 1))
        if len(ys) > 30 * S * S and kc > 0.4:
            col[lit_e] = mix(col[lit_e], AMBER_L, 0.3 + 0.5 * kc)
            col[back & ~lit_e] *= 0.75
        out[by0:by1, bx0:bx1][M] = col[M]
        if kc > 0.7:
            frag[by0:by1, bx0:bx1][M] = 1

    # the aether in the tear: deep indigo, swirling bands of violet and teal
    a_ = Uc / L * 2.6
    b_ = Vc / (w0 * 1.15)
    rho = np.hypot(a_, b_) + 1e-3
    phi = np.arctan2(b_, a_)
    phase = 2 * phi + spin * 3.2 * np.log(rho + 0.2) + 0.9 * bandn[ix] + 0.4 * np.tanh(rough[ix])
    sw = np.cos(phase)
    deep = smooth(dI, 2 * S, w0 * 0.9)
    vcol = mix(VIOLET, VOID, smooth(dI, S, w0 * 0.45))
    vcol = mix(vcol, VOID_DEEP, deep * smooth(-sw, -0.6, 0.2))
    vcol = mix(vcol, VIOLET, (sw > 0.72).astype(np.float32) * 0.8)
    vcol = mix(vcol, VIOLET_L, (sw > 0.95).astype(np.float32) * 0.5 * (1 - deep * 0.5))
    vcol = mix(vcol, TEAL, ((sw < -0.45) & (sw > -0.65)).astype(np.float32) * 0.8)
    # glyph-like arcs: broken rings about the rift's centre, with ticks
    GS = 8                                             # drawn at GS x and boxed down
    g = Image.new("L", (SW * GS, SW * GS), 0)
    gd = ImageDraw.Draw(g)
    for _ in range(int(r.integers(2, 4))):
        rx_, ry_ = L * r.uniform(0.35, 0.95), w0 * r.uniform(0.35, 0.8)
        a0 = r.uniform(0, 2 * math.pi)
        span = r.uniform(1.2, 3.6)
        ts = np.linspace(a0, a0 + span, 140)
        dashes = np.cumsum(r.random(len(ts)) < 0.09) % 2 == 0
        prev = None
        for t, on in zip(ts, dashes):
            u, v = rx_ * math.cos(t), ry_ * math.sin(t)
            P = (GS * (R + u * ca - v * sa), GS * (R + u * sa + v * ca))
            if on and prev is not None:
                gd.line([prev, P], fill=255, width=round(1.5 * S * GS))
                if r.random() < 0.12:              # a tick across the ring
                    nu, nv = math.cos(t) / rx_, math.sin(t) / ry_
                    nn = math.hypot(nu, nv)
                    nu, nv = nu / nn * 7 * S, nv / nn * 7 * S
                    gd.line([(P[0] - GS * (nu * ca - nv * sa), P[1] - GS * (nu * sa + nv * ca)),
                             (P[0] + GS * (nu * ca - nv * sa), P[1] + GS * (nu * sa + nv * ca))], fill=255, width=round(S * GS))
            prev = P if on else None
    glyph = np.asarray(g.resize((SW, SW), Image.BOX), np.float32) / 255
    del g
    gcol = TEAL_L if r.random() < 0.5 else AMBER
    vcol = mix(vcol, gcol, glyph * 0.7 * smooth(dI, 2 * S, 6 * S))
    # stars
    n_st = int((1 - outside).sum() / (480 * S * S))
    for _ in range(n_st):
        x, y = int(r.uniform(0, SW)), int(r.uniform(0, SW))
        if inside[y, x] < 1 or dI[y, x] < 3 * S:
            continue
        c = STAR[int(r.choice(3, p=[0.6, 0.25, 0.15]))]
        f = r.uniform(0.35, 0.8)
        splat(vcol, y, x, c, f)
        if r.random() < 0.18:
            for (oy, ox) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                splat(vcol, y + oy * S, x + ox * S, c, f * 0.5)
    # its light inside the edge: teal, then violet
    t1 = (1.2 + 1.5 * (bandn[ix] > 0)) * S
    vcol = mix(vcol, TEAL_L, (dI < t1).astype(np.float32) * 0.7)
    # fragments that drifted over the void: fainter the deeper they are
    over = frag * inside
    fcol = mix(out, VOID, 0.5 + 0.4 * smooth(dI, 0, w0 * 0.6))
    vcol = mix(vcol, fcol, over)
    out = mix(out, vcol, inside)

    # crumbs breaking off the lip, drifting in: smaller and fainter inward
    cr = Image.new("L", (SW * SS, SW * SS), 0)
    cd = ImageDraw.Draw(cr)
    crumbs = []
    for _ in range(int(L / S * 0.7)):
        t = r.uniform(-0.9, 0.9)
        side = r.choice([-1, 1])
        hw = w0 * max(0.0, 1 - abs(t) ** 1.7) ** 0.75
        vv = side * hw * r.uniform(-0.2, 1.9)
        u = t * L
        x, y = R + u * ca - vv * sa, R + u * sa + vv * ca
        xi, yi = int(x), int(y)
        if not (0 <= xi < SW and 0 <= yi < SW):
            continue
        depth_ = float(dI[yi, xi]) / w0 if inside[yi, xi] > 0.5 else -float(dT[yi, xi]) / w0
        sz = np.clip(5.5 - 6 * depth_, 1.6, 8) * S * r.uniform(0.6, 1.2)
        nv_ = int(r.integers(3, 6))
        a0 = r.uniform(0, 2 * math.pi)
        poly = [((x + sz * r.uniform(0.6, 1.2) * math.cos(a0 + 2 * math.pi * j / nv_)) * SS,
                 (y + sz * r.uniform(0.6, 1.2) * math.sin(a0 + 2 * math.pi * j / nv_)) * SS) for j in range(nv_)]
        crumbs.append((poly, max(0.0, depth_)))
    crumbs.sort(key=lambda c: c[1])
    for poly, dp in crumbs:
        cd.polygon(poly, fill=int(40 + 215 * (1 - min(1, dp))))
    cmask = np.asarray(cr.resize((SW, SW), Image.BOX), np.float32) / 255
    del cr, cd
    ccol = mix(src * 1.05, VOID, 0.25 + 0.6 * smooth(dI, 0, w0 * 0.8))
    ccol = mix(ccol, AMBER_L, 0.25 * (1 - smooth(dI, 0, 6 * S)))
    cov = np.clip(cmask * 2.2, 0, 1)
    out = mix(out, ccol, cov * (cmask > 0.05))

    # its light out over the wall, in flat opaque bands: amber lip, gold, lavender
    wob = 0.5 + 0.5 * np.tanh(bandn[ix] * 1.3)
    b1 = (1.2 + 2.0 * wob) * S * (np.tanh(bandn[ix] * 3 + 1.2) > -0.5)  # broken here and there
    b2 = b1 + (1.5 + 2.5 * wob) * S
    b3 = b2 + (4.0 + 7.0 * wob) * S
    b4 = b3 + (6.0 + 10.0 * wob) * S
    o_ = outside.astype(np.float32)
    out = mix(out, AMBER_L, o_ * (dT < b1) * 0.85)
    out = mix(out, mix(out, AMBER, 0.6), o_ * ((dT >= b1) & (dT < b2)))
    out = mix(out, mix(out, LAVENDER, 0.24), o_ * ((dT >= b2) & (dT < b3)))
    out = mix(out, mix(out, LAVENDER, 0.09), o_ * ((dT >= b3) & (dT < b4)))
    img[ix] = out
    aether[ix] |= (inside > 0) | (o_ * (dT < b3) > 0)
    rf.update(R=R, dT=dT, Zloc=Zloc)             # kept for the warp (5)
    print(f"  {len(shards)} shards  void {int((1 - outside).sum())} px", flush=True)

# ── 5. the marks ──────────────────────────────────────────────────────────────
# Drawn at the page's scale, not the wall's (most are 0.5in to 2.5in across), so
# they read from across a spread. They have a random stream of their own (`more`),
# so the wall above stays as it was.
print("marks", flush=True)
more = np.random.default_rng(SEED + 70)
IN = DPI
wall0 = (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)   # the wall before the marks: its palette is cut from this, as it always was


def window(x0, y0, w, h):
    """The tile's rows and columns under a w x h window at (x0, y0), wrapped."""
    return np.ix_(np.arange(int(y0), int(y0) + h) % NH, np.arange(int(x0), int(x0) + w) % NW)


def lnoise(h, w, beta, r, stretch=(1.0, 1.0)):
    """1/f^beta noise in a window, scaled to 0..1 (it wraps at the window's edges)."""
    fy = np.fft.fftfreq(h)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(w)[None, :] * stretch[0]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    out = irfft2(rfft2(white_noise(r, h, w)) / f ** beta, s=(h, w)).astype(np.float32)
    out -= out.min()
    return out / out.max()


# the warp: round each rift the wall's own surface is drawn in toward it, the
# courses and the plates' edges bowed and a little turned, most a short way out
# from the shards and less from there to `reach`. The tear, its light and its
# shards stay where they are. The surface dishes toward the rift: its far side
# catches the light, its near side is in shade.
rift_reach = []
pulled = np.zeros((NH, NW), np.float32)        # how far the warp has moved each point of the wall, px
for rf in rifts:
    L = rf["L"]
    reach = 1.3 * L + 1.0 * IN
    amp = 0.36 * L + 0.2 * IN
    RW = int(0.85 * L + reach) + 2
    SW = 2 * RW + 1
    gx0, gy0 = int(rf["cx"]) - RW, int(rf["cy"]) - RW
    ix = window(gx0, gy0, SW, SW)
    Y, X = np.mgrid[0:SW, 0:SW].astype(np.float32)
    rx, ry = X - RW, Y - RW
    ca, sa = math.cos(rf["ang"]), math.sin(rf["ang"])
    U, V = rx * ca + ry * sa, -rx * sa + ry * ca
    du = U - np.clip(U, -0.85 * L, 0.85 * L)
    d = np.hypot(du, V) + 1e-6                                # from the rift's spine
    nx, ny = (du * ca - V * sa) / d, (du * sa + V * ca) / d    # away from it
    e = np.full((SW, SW), 1e6, np.float32)                     # out from the shards
    R = rf["R"]
    o, c = max(0, RW - R), max(0, R - RW)
    n = min(SW, 2 * R + 1)
    e[o:o + n, o:o + n] = (rf["dT"] - 0.7 * rf["Zloc"])[c:c + n, c:c + n]
    w = smooth(e, 0, 1.2 * IN) * (1 - smooth(d, 0, reach))
    tongue = 0.45 + 0.75 * lnoise(SW, SW, 2.6, more)          # it pulls harder here than there
    m = amp * w * tongue
    theta = rf["spin"] * 0.16 * w
    ct, st = np.cos(theta), np.sin(theta)
    SX = gx0 + RW + ct * rx + st * ry + nx * m
    SY = gy0 + RW - st * rx + ct * ry + ny * m
    moved = m > 0.02
    pulled[ix] = np.maximum(pulled[ix], np.where(e < 0.5 * IN, 1e3, np.hypot(SX - gx0 - X, SY - gy0 - Y)))     # the tear and its shards count as moved
    hgt = -wblur(m, 6 * S)                                      # the dish
    gy_, gx_ = np.gradient(hgt)
    lit = 1 + 0.5 * np.tanh((gx_ + gy_) / math.sqrt(2) * 1.6)[..., None] * 0.2
    img[ix] = np.where(moved[..., None], sample(img, SY, SX) * lit, img[ix])
    iy_, ix_ = SY.round().astype(int) % NH, SX.round().astype(int) % NW
    unit[ix] = unit[iy_, ix_]
    stone_a[ix] = stone_a[iy_, ix_]
    rift_reach.append((rf, reach))
    del X, Y, rx, ry, U, V, du, d, nx, ny, e, w, tongue, m, theta, ct, st, SX, SY, hgt, gx_, gy_, lit, iy_, ix_

# where the marks go: drawn at random and kept apart, not set by hand
n_stone = n_units - len(plates)              # units below this are stones, from it up plates
kind = np.zeros((NH, NW), np.uint8)          # what marks each pixel: 1 violet, 3 ash and cuts (each has colours of its own)
taken = []                                   # (x, y, radius) of every mark placed


def away(x, y, px, py):
    dx, dy = abs(x - px), abs(y - py)
    return math.hypot(min(dx, NW - dx), min(dy, NH - dy))


def rift_clear(x, y):
    """How far (x, y) lies outside the ground the rifts have warped (negative: inside it)."""
    out_ = 1e9
    for rf_, reach_ in rift_reach:
        dx, dy = (x - rf_["cx"] + NW / 2) % NW - NW / 2, (y - rf_["cy"] + NH / 2) % NH - NH / 2
        ca_, sa_ = math.cos(rf_["ang"]), math.sin(rf_["ang"])
        u, v = dx * ca_ + dy * sa_, -dx * sa_ + dy * ca_
        out_ = min(out_, math.hypot(u - min(max(u, -0.85 * rf_["L"]), 0.85 * rf_["L"]), v) - reach_)
    return out_


def free(x, y, radius):
    return all(away(x, y, px, py) >= radius + pr for px, py, pr in taken)


def place(radius, clear):
    """A place for a mark of this radius, `clear` px outside the warped ground
    (negative: that far into it), and clear of the marks already placed."""
    tries = 0
    while True:
        x, y = more.uniform(0, NW), more.uniform(0.5 * IN, 10.2 * IN)
        tries += 1
        if rift_clear(x, y) >= clear and free(x, y, radius * 0.9 ** (tries // 3000)):     # crowded: let them closer
            taken.append((x, y, radius))
            return x, y


def ledge(half, radius, drop=0.0):
    """A place on the top edge of a plate or a band with `half` px of it clear
    either side, stone above it, where the warp has not moved the wall: where ash can
    lie. `drop`: how far below the edge the mark's middle is."""
    lens = np.array([0.2 * NW if p["w"] is None else max(0.0, p["w"] - 2 * half - 50 * S) for p in plates])
    tries = 0
    while True:
        tries += 1
        k = int(more.choice(len(plates), p=lens / lens.sum()))
        p = plates[k]
        if p["w"] is None:
            x, y = more.uniform(0, NW), p["cy"] - p["h"] / 2
        elif lens[k] <= 0:
            continue
        else:
            t = more.uniform(-0.5, 0.5) * lens[k]
            x = p["cx"] + t * math.cos(p["ang"]) + p["h"] / 2 * math.sin(p["ang"])
            y = p["cy"] + t * math.sin(p["ang"]) - p["h"] / 2 * math.cos(p["ang"])
        x, y = x % NW, y % NH
        xs = np.arange(int(x - half), int(x + half)) % NW
        if not 0.8 * IN < y < 9.6 * IN or pulled[int(y) % NH, xs].max() > 3 * S or not free(x, y + drop, radius * 0.9 ** (tries // 3000)):
            continue
        if (unit[int(y + 8 * S) % NH, xs] == n_stone + k).all() and (unit[int(y - 10 * S) % NH, xs] < n_stone).all():
            taken.append((x, y + drop, radius))
            return x, y


def canvas(side_w, side_h):
    """A window's drawing at SS x: the image and its pen."""
    im = Image.new("L", (side_w * SS, side_h * SS), 0)
    return im, ImageDraw.Draw(im)


def boxed(im):
    return np.asarray(im.resize((im.width // SS, im.height // SS), Image.BOX), np.float32) / 255


# the ledge marks first (they have the fewest places to go), then the largest
# Candle wax was drawn here and taken out (owner, 2026-11-14). Its places are
# still drawn and left empty, so every other mark keeps the place it was given.
WAX_LEDGE = [ledge(sp + 0.3 * IN, 0.9 * IN, 0.4 * IN) + (sp,) for sp in more.uniform(0.2, 0.6, 3) * IN]
ASH_LEDGE = [ledge(hf, 0.9 * IN, 0.2 * IN) + (0.92 * hf,) for hf in more.uniform(1.0, 1.8, 4) * IN]
CIRCLES = sorted((more.uniform(0.75, 1.3) * IN for _ in range(5)), reverse=True)
CIRCLES = [place(R_ + 0.1 * IN, -0.5 * IN) + (R_,) for R_ in CIRCLES]
WAX_WALL = [place(0.8 * IN, 0.3 * IN) for _ in range(2)]
BURNS = sorted((more.uniform(0.5, 1.25) * IN for _ in range(5)), reverse=True)
BURNS = [place(R_ * 0.75, -1.0 * IN) + (R_,) for R_ in BURNS]
SEEPS = sorted((more.uniform(0.5, 1.0) * IN for _ in range(5)), reverse=True)
SEEPS = [place(R_ * 0.8, -0.8 * IN) + (R_,) for R_ in SEEPS]
SMEARS = [place(0.6 * IN, -0.3 * IN) for _ in range(4)]

# occult circles: summoning circles cut into the wall, some chiselled (short
# straight cuts, each a little off the last, a pit drilled for a dot) and some
# scratched (thin, wavering, gone over twice). Two rings with a band of invented
# signs between them, and a figure of its own inside each. The signs are built
# of open rings, squiggles, combs, dots and ticks: no letter, numeral or known symbol.
print("circles", flush=True)
TAU = 2 * math.pi


def arc(cx, cy, rad, a0=0.0, a1=TAU):
    return [(cx + rad * math.cos(a), cy + rad * math.sin(a)) for a in np.linspace(a0, a1, max(6, int(abs(a1 - a0) * rad / (4 * S)) + 2))]


def glyph(r):
    """An invented sign in a unit box, as (strokes, dots)."""
    def uarc(cx, cy, rad, a0, a1):
        return [(cx + rad * math.cos(a), cy + rad * math.sin(a)) for a in np.linspace(a0, a1, 14)]

    strokes, dots = [], []
    base = int(r.integers(0, 5))
    a0 = r.uniform(0, TAU)
    if base == 0:                                 # an open ring round a dot
        strokes.append(uarc(0, 0, 0.34, a0, a0 + r.uniform(3.4, 5.2)))
        dots.append((0.0, 0.0))
    elif base == 1:                               # a small ring, an arc cupping it
        strokes += [uarc(0, 0, 0.14, 0, TAU), uarc(0, 0, 0.36, a0, a0 + r.uniform(2.0, 3.2))]
    elif base == 2:                               # two open rings, one in the other, facing apart
        strokes += [uarc(0, 0, 0.36, a0, a0 + r.uniform(3.0, 4.0)), uarc(0, 0, 0.17, a0 + math.pi, a0 + math.pi + r.uniform(3.2, 4.4))]
    elif base == 3:                               # a squiggle dying away: three humps, each smaller
        strokes.append(uarc(-0.26, 0, 0.18, math.pi, TAU) + uarc(0.04, 0, 0.12, math.pi, 0)[1:] + uarc(0.23, 0, 0.07, math.pi, TAU)[1:])
    else:                                         # a comb: an arc with teeth out of its back
        sw = r.uniform(2.0, 3.0)
        strokes.append(uarc(0, 0.1, 0.26, a0, a0 + sw))
        for a in np.linspace(a0 + 0.2, a0 + sw - 0.2, int(r.integers(3, 6))):
            strokes.append([(0.26 * math.cos(a), 0.1 + 0.26 * math.sin(a)), (0.46 * math.cos(a), 0.1 + 0.46 * math.sin(a))])
    for _ in range(int(r.integers(1, 3))):
        a, k = r.uniform(0, TAU), int(r.integers(0, 4))
        if k == 0 and base == 2:
            dots.append((0.0, 0.0))
        elif k == 1:
            dots.append((0.47 * math.cos(a), 0.47 * math.sin(a)))
        elif k == 2:                              # a pair of ticks across it
            for o in (-0.05, 0.05):
                c, s_ = math.cos(a), math.sin(a)
                strokes.append([(0.22 * c - o * s_, 0.22 * s_ + o * c), (0.46 * c - o * s_, 0.46 * s_ + o * c)])
        else:
            strokes.append(uarc(0.44 * math.cos(a), 0.44 * math.sin(a), 0.07, 0, TAU))
    rot = r.uniform(0, TAU)
    c, s_ = math.cos(rot), math.sin(rot)
    turn = lambda p: (p[0] * c - p[1] * s_, p[0] * s_ + p[1] * c)
    return [[turn(p) for p in st] for st in strokes], [turn(p) for p in dots]


def circle_figure(R, motif, r):
    """A circle's strokes and dots, about its centre: (points, weight) and (x, y)."""
    strokes, dots = [], []
    r1, r2 = R, R * r.uniform(0.66, 0.74)
    strokes += [(arc(0, 0, r1), 1.0), (arc(0, 0, r2), 0.85)]
    g = (r1 - r2) * 0.7                          # a sign's size
    rm = (r1 + r2) / 2
    n = max(5, int(TAU * rm / ((r1 - r2) * r.uniform(1.1, 1.5))))
    th0 = r.uniform(0, TAU)
    for i in range(n):
        th = th0 + TAU * (i + r.normal(0, 0.05)) / n
        c, s_ = math.cos(th), math.sin(th)
        if r.random() < 0.12:                     # a divider, not a sign
            strokes.append(([(r2 * c, r2 * s_), (r1 * c, r1 * s_)], 0.8))
            continue
        put_ = lambda p: (rm * c + g * (-p[0] * s_ + p[1] * c), rm * s_ + g * (p[0] * c + p[1] * s_))
        gs, gd = glyph(r)
        strokes += [([put_(p) for p in st], 0.7) for st in gs]
        dots += [put_(p) for p in gd]
    ri = r2 * r.uniform(0.82, 0.9)
    a0, spin = r.uniform(0, TAU), float(r.choice([-1, 1]))
    if motif == 0:                                # the tear itself: a jagged slit, rays of uneven length round it
        hh, ww = 0.36 * ri, 0.085 * ri
        c, s_ = math.cos(a0), math.sin(a0)
        side = lambda sg: [(sg * ww * max(0.0, 1 - t * t) ** 0.8 * r.uniform(0.55, 1.4), t * hh) for t in np.linspace(-1, 1, 11)]
        slit = side(1) + side(-1)[::-1]
        strokes.append(([(x * c - y * s_, x * s_ + y * c) for x, y in slit + slit[:1]], 1.0))
        strokes.append((arc(0, 0, 0.46 * ri), 0.8))
        for i in range(int(r.integers(8, 14))):
            a = a0 + TAU * (i + r.uniform(-0.25, 0.25)) / 11
            e = ri * r.uniform(0.62, 1.0)
            strokes.append(([(0.52 * ri * math.cos(a), 0.52 * ri * math.sin(a)), (e * math.cos(a), e * math.sin(a))], 0.8))
            if r.random() < 0.4:
                dots.append(((e + 0.07 * ri) * math.cos(a), (e + 0.07 * ri) * math.sin(a)))
    elif motif == 1:                              # small rings on an orbit, each on a curved arm from the middle
        strokes.append((arc(0, 0, 0.11 * ri), 0.9))
        k = int(r.integers(3, 6))
        for i in range(k):
            a = a0 + TAU * (i + r.uniform(-0.2, 0.2)) / k
            rs, ro = ri * r.uniform(0.12, 0.2), ri * r.uniform(0.6, 0.74)
            strokes.append((arc(ro * math.cos(a), ro * math.sin(a), rs), 0.9))
            dots.append((ro * math.cos(a), ro * math.sin(a)))
            ts = np.linspace(0, 1, 24)
            strokes.append(([((0.11 * ri + t * (ro - rs - 0.11 * ri)) * math.cos(a - spin * (1 - t) * 1.5),
                              (0.11 * ri + t * (ro - rs - 0.11 * ri)) * math.sin(a - spin * (1 - t) * 1.5)) for t in ts], 0.8))
    elif motif == 2:                              # a spiral, ticked across, dots where it ends
        turns = r.uniform(2.2, 3.2)
        ts = np.linspace(0.04, 1, int(turns * 60))
        sp = [(0.92 * ri * t * math.cos(a0 + spin * t * turns * TAU), 0.92 * ri * t * math.sin(a0 + spin * t * turns * TAU)) for t in ts]
        strokes.append((sp, 1.0))
        for t in np.arange(0.3, 0.97, r.uniform(0.045, 0.08)):
            a, rad = a0 + spin * t * turns * TAU, 0.92 * ri * t
            strokes.append(([((rad - 0.05 * ri) * math.cos(a), (rad - 0.05 * ri) * math.sin(a)), ((rad + 0.05 * ri) * math.cos(a), (rad + 0.05 * ri) * math.sin(a))], 0.7))
        a = a0 + spin * turns * TAU
        dots += [(ri * 0.92 * math.cos(a + spin * d_), ri * 0.92 * math.sin(a + spin * d_)) for d_ in (0.14, 0.26, 0.38)]
    elif motif == 3:                              # shells: rings one in the other, all touching at one side, a bar through them
        c, s_ = math.cos(a0), math.sin(a0)
        for f in (1.0, r.uniform(0.66, 0.76), r.uniform(0.42, 0.52), r.uniform(0.2, 0.28)):
            strokes.append((arc((ri - ri * f) * c, (ri - ri * f) * s_, ri * f), 0.9))
        strokes.append(([(-ri * 0.86 * c, -ri * 0.86 * s_), (ri * 0.7 * c, ri * 0.7 * s_)], 0.8))
        dots.append((-ri * 0.93 * c, -ri * 0.93 * s_))
        for a in np.arange(a0 + 1.0, a0 + TAU - 1.0, r.uniform(0.22, 0.34)):
            strokes.append(([(0.92 * ri * math.cos(a), 0.92 * ri * math.sin(a)), (1.0 * ri * math.cos(a), 1.0 * ri * math.sin(a))], 0.7))
    else:                                         # a web: uneven points round it joined by bowed sides, a ring at each
        k = int(r.integers(5, 8))
        angs = sorted(a0 + TAU * (i + r.uniform(-0.3, 0.3)) / k for i in range(k))
        P = [(0.8 * ri * math.cos(a), 0.8 * ri * math.sin(a)) for a in angs]
        for (ax, ay), (bx, by) in zip(P, P[1:] + P[:1]):
            mx, my = (ax + bx) * r.uniform(0.18, 0.3), (ay + by) * r.uniform(0.18, 0.3)       # bowed in toward the middle
            strokes.append(([((1 - t) ** 2 * ax + 2 * t * (1 - t) * mx + t * t * bx, (1 - t) ** 2 * ay + 2 * t * (1 - t) * my + t * t * by) for t in np.linspace(0, 1, 20)], 0.9))
        for (ax, ay) in P:
            strokes.append((arc(ax * 1.14, ay * 1.14, 0.09 * ri), 0.8))
        strokes.append((arc(0, 0, 0.14 * ri), 0.9))
        dots.append((0.0, 0.0))
    if r.random() < 0.7:                          # small rings outside it, where things stood
        for a in np.sort(r.uniform(0, TAU, int(r.integers(2, 6)))):
            strokes.append((arc(1.13 * R * math.cos(a), 1.13 * R * math.sin(a), R * r.uniform(0.06, 0.1)), 0.8))
    return strokes, dots


def cut_line(d, pts, width, chisel, r):
    """A stroke cut along pts (window px) into the pen d."""
    pts = np.array(pts, float)
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    total = s[-1]
    if total < 1:
        return
    at = lambda t: np.stack([np.interp(t, s, pts[:, 0]), np.interp(t, s, pts[:, 1])], -1)
    if chisel:
        t = 0.0
        while t < total:
            t1 = min(total, t + min(r.uniform(11, 24) * S, total / 6))
            if r.random() > 0.05:                 # a cut missed here and there
                p, q = at(t) + r.normal(0, 0.9 * S, 2), at(t1) + r.normal(0, 0.9 * S, 2)
                d.line([tuple(p * SS), tuple(q * SS)], fill=255, width=max(1, round(width * r.uniform(0.75, 1.25) * SS)))
            if t1 >= total:
                break
            t = t1 - r.uniform(0, 0.2) * (t1 - t)
        return
    for k in range(2):                            # scratched: gone over twice, never quite on the first line
        lo, hi = (0.0, total) if k == 0 else sorted(r.uniform(0, total, 2))
        ts = np.arange(lo, hi, 5 * S)
        if len(ts) < 3:
            continue
        p = at(ts)
        tx, ty = np.gradient(p[:, 0]), np.gradient(p[:, 1])
        tn = np.hypot(tx, ty) + 1e-6
        wob = sum(r.uniform(0.6, 1.8) * S * np.sin(ts / (r.uniform(25, 110) * S) + r.uniform(0, TAU)) for _ in range(3)) + (r.normal(0, 1.6 * S) if k else 0)
        p = p + np.stack([-ty / tn, tx / tn], -1) * wob[:, None]
        d.line([tuple(q * SS) for q in p], fill=255 if k == 0 else 190, width=max(1, round(width * r.uniform(0.8, 1.1) * SS)), joint="curve")


for i, ((x, y, R_), motif) in enumerate(zip(CIRCLES, more.permutation(5))):
    chisel = i % 2 == 0
    width = (more.uniform(5.5, 7.5) if chisel else more.uniform(3.0, 3.8)) * S
    half = int(R_ * 1.28) + 8
    side_ = 2 * half
    im, d = canvas(side_, side_)
    strokes, dots = circle_figure(R_, int(motif), more)
    for pts, wt in strokes:
        cut_line(d, [(px + half, py + half) for px, py in pts], width * wt, chisel, more)
    for px, py in dots:
        rr = width * (0.95 if chisel else 1.3)
        if chisel:                                # a pit drilled
            d.ellipse([(px + half - rr) * SS, (py + half - rr) * SS, (px + half + rr) * SS, (py + half + rr) * SS], fill=255)
        else:                                     # a tight scribble
            cut_line(d, [(px + half + rr * t / 9 * math.cos(t), py + half + rr * t / 9 * math.sin(t)) for t in np.linspace(0, 9, 24)], width * 0.8, False, more)
    C = boxed(im)
    del im, d
    worn = lnoise(side_, side_, 2.2, more)        # worn off or spalled away in places
    C *= smooth(worn, *((0.1, 0.3) if chisel else (0.18, 0.4)))
    ix = window(x - half, y - half, side_, side_)
    sub = img[ix]
    lip = np.clip(shift(C, 1.5 * S, 1.5 * S) - C, 0, 1)        # the cut's far lip catches the light
    sub = mix(sub, np.clip(sub * 1.2 + 0.04, 0, 1), lip * 0.75)
    if chisel:                                    # a groove: dirt in its floor, its near wall in deeper shade
        Cb = wblur(C, 0.8 * S)
        gy_, gx_ = np.gradient(Cb)
        sub = sub * ((1 - 0.52 * Cb) * (1 - 0.3 * np.clip((gx_ + gy_) * 3, 0, 1)))[..., None]
    else:                                         # a scratch: dark with dirt
        sub = sub * (1 - 0.55 * C)[..., None]
    img[ix] = sub
    kind[ix] = np.where((C > 0.04) | (shift(C, 1.3 * S, 1.3 * S) > 0.04), 3, kind[ix])
    del C, sub, worn

# violet, where the aether touched the wall, two ways. Burns: a discharge struck
# the wall and forked across it, a charred track that branches and thins like a
# fern, the stone scorched violet close round it, a blistered spot where it
# struck and pits where sparks flew. Stains: aether seeped out of the joints
# (the mortar, a plate's edge) and soaked down the wall below them: a curtain of
# stain hanging from a stretch of joint, deepest in the joint, its foot ragged,
# dried to a darker rim, a few runs on from it ending in beads.
print("violet", flush=True)
BURN = hexc("#352c56")
SCORCH = np.array([0.68, 0.60, 0.86], np.float32)     # what the heat left of the stone's colour
FILM = np.array([0.72, 0.62, 0.94], np.float32)       # the seep's thin stain


def burn(x, y, R, r):
    half = int(R * 1.15 + 30 * S)
    side_ = 2 * half
    im, d = canvas(side_, side_)

    def branch(px, py, a, length, width, depth):
        full = length
        while length > 0:
            step = r.uniform(6, 13) * S
            out_ = math.atan2(py - half, px - half) if depth or length < full else a      # it runs outward, on the whole
            a += r.normal(0, 0.24) + 0.14 * ((out_ - a + math.pi) % TAU - math.pi)
            qx, qy = px + step * math.cos(a), py + step * math.sin(a)
            w_ = max(1.1 * S, width * (0.25 + 0.75 * length / full))
            d.line([(px * SS, py * SS), (qx * SS, qy * SS)], fill=255, width=max(1, round(w_ * SS)))
            d.ellipse([(qx - w_ / 2) * SS, (qy - w_ / 2) * SS, (qx + w_ / 2) * SS, (qy + w_ / 2) * SS], fill=255)
            px, py = qx, qy
            length -= step
            if depth < 4 and r.random() < 0.21:
                branch(px, py, a + r.choice([-1, 1]) * r.uniform(0.35, 1.1), length * r.uniform(0.4, 0.8), w_ * 0.75, depth + 1)

    a0, span = r.uniform(0, TAU), r.uniform(1.6, TAU)      # it forks over part of the round, or all of it
    arms = int(r.integers(3, 8))
    for i in range(arms):
        branch(half, half, a0 + span * (i + r.uniform(-0.3, 0.3)) / arms, R * r.uniform(0.45, 1.0), r.uniform(4.5, 8.5) * S, 0)
    rr = r.uniform(10, 22) * S                             # where it struck: a ragged blot
    d.polygon([((half + rr * r.uniform(0.6, 1.25) * math.cos(t)) * SS, (half + rr * r.uniform(0.6, 1.25) * math.sin(t)) * SS)
               for t in np.linspace(0, TAU, 18, endpoint=False)], fill=255)
    for _ in range(int(r.integers(15, 50))):               # pits where sparks flew
        a, dist, pr = a0 + r.uniform(-0.2, span + 0.2), R * r.uniform(0.1, 1.0), r.uniform(1.2, 3.2) * S
        px, py = half + dist * math.cos(a), half + dist * math.sin(a)
        d.ellipse([(px - pr) * SS, (py - pr) * SS, (px + pr) * SS, (py + pr) * SS], fill=255)
    core = boxed(im)
    del im, d
    n_ = lnoise(side_, side_, 1.6, r)
    halo = smooth(wblur(core, 7 * S) + 0.07 * (n_ - 0.5), 0.05, 0.075)    # scorched round the track: flat, hard-edged
    inner = smooth(wblur(core, 2.2 * S), 0.2, 0.3)
    ix = window(x - half, y - half, side_, side_)
    sub = img[ix]
    sub = sub * mix(np.ones(3, np.float32), SCORCH, halo)
    sub = mix(sub, VIOLET_L * 0.92, inner * 0.55)
    sub = mix(sub, BURN * (0.94 + 0.12 * n_)[..., None], np.clip(core * 1.4, 0, 1) * 0.93)
    yy_, xx_ = np.mgrid[0:side_, 0:side_]
    blister = smooth(0.45 * rr - np.hypot(xx_ - half, yy_ - half) + 3 * S * (n_ - 0.5), 0, 1.5 * S)
    sub = mix(sub, LAVENDER * 0.9, blister * 0.8)          # the blister at its heart: ashen, paler
    img[ix] = sub
    kind[ix] = np.where(halo > 0.03, 1, kind[ix])


def seep(x, y, R, r):
    half, below = int(R * 1.4), int(1.7 * IN)
    w, h = 2 * half, 2 * half + below
    ix = window(x - half, y - half, w, h)
    u = unit[ix]
    edge = ((u != np.roll(u, 1, 0)) | (u != np.roll(u, 1, 1))).astype(np.float32)
    edge[0, :] = edge[:, 0] = 0
    J = np.clip((1 - stone_a[ix]) * (u < n_stone) + wblur(edge, 1.5 * S) * 2.5, 0, 1)      # the joints, and the plates' edges
    vy, vx = np.mgrid[0:h, 0:w].astype(np.float32)
    vx -= half
    vy -= half
    en, gate, fing = lnoise(h, w, 2.2, r), lnoise(h, w, 1.8, r), lnoise(h, w, 1.5, r, stretch=(1.0, 0.2))
    B = smooth(0.9 - np.hypot(vx * r.uniform(0.7, 1.0), vy) / R - 0.9 * (en - 0.5), 0.0, 0.5)   # where it came through, most at the middle,
    src = J * B * smooth(gate, 0.42, 0.6)                                                  # from this stretch of joint and not that
    hang = np.exp(-np.arange(h, dtype=np.float32) / (r.uniform(45, 105) * S))              # and soaked down the wall below each joint
    soak = wblur(np.fft.irfft(np.fft.rfft(src, axis=0) * np.fft.rfft(hang)[:, None], n=h, axis=0).astype(np.float32), 2 * S)
    stain = smooth(soak / (11 * S) + 0.5 * (fing - 0.5), 0.3, 0.36)                        # a curtain with a ragged foot
    im, d = canvas(w, h)
    foot = np.argwhere((stain > 0.5) & (np.roll(stain, -round(8 * S), 0) < 0.5) & (vy < half + 0.4 * IN))
    foot = foot[r.choice(len(foot), min(len(foot), int(r.integers(3, 10))), replace=False)] if len(foot) else []
    for py, px in foot:                                    # and ran on from it here and there, each run ending in a bead
        length = min(h - py - 30 * S, r.lognormal(math.log(100 * S), 0.7))
        wd = r.uniform(3.5, 6.5) * S
        qx, qy = float(px), float(py) - 6 * S
        while qy < py + length:
            nx_, ny_ = qx + r.normal(0, 0.5 * S), qy + 8 * S
            w_ = wd * (1 - 0.45 * max(0.0, qy - py) / max(length, 1))
            d.line([(qx * SS, qy * SS), (nx_ * SS, ny_ * SS)], fill=255, width=max(1, round(w_ * SS)))
            qx, qy = nx_, ny_
        br = wd * r.uniform(0.6, 0.85)
        d.ellipse([(qx - br) * SS, (qy - br * 1.3) * SS, (qx + br) * SS, (qy + br * 1.1) * SS], fill=255)
    runs_ = boxed(im)
    del im, d
    stain = np.maximum(stain, runs_)
    rim = np.clip(stain - wblur(stain, 2.2 * S), 0, 1)
    sub = img[ix] * mix(np.ones(3, np.float32), FILM, stain * (0.75 + 0.25 * fing))
    sub = mix(sub, VIOLET, np.clip(smooth(wblur(src, 1.5 * S), 0.1, 0.5) * 0.7 + runs_ * 0.5, 0, 0.8))   # deepest in the joint it came out of
    sub = mix(sub, VIOLET * 0.9, np.clip(rim * 2.4, 0, 1) * 0.6)                           # and dried to a darker rim
    img[ix] = sub
    kind[ix] = np.where(stain > 0.03, 1, kind[ix])


for x, y, R_ in BURNS:
    burn(x, y, R_, more)
for x, y, R_ in SEEPS:
    seep(x, y, R_, more)

# ash, which is a powder and is drawn as one: grains, not a film. Heaped on the
# ledges: a low drift of several humps, grey with a paler crust where the light
# falls, flecked black and white, charred bits in it, and what sifted off the
# edge caught on the wall below in specks and trails. And smeared: dragged
# across the wall by a paw (four toes' streaks from where the pads pressed) or
# rubbed with something broad, in dry streaks of charcoal and pale ash.
print("ash", flush=True)
ASH = (hexc("#d0cdc6"), hexc("#8a8782"), hexc("#494644"))      # pale ash, grey ash, charcoal


def grains(h, w, r, beta=0.25, stretch=(1.0, 1.0)):
    """Noise in a window with mean 0 and sd 1: the fine sort, for powder."""
    g_ = lnoise(h, w, beta, r, stretch)
    return (g_ - g_.mean()) / g_.std()


def ash_heap(x, y, half, r):
    """Ash heaped on the ledge at (x, y), `half` px either way: a low drift, and
    what sifted off the edge."""
    halfw, top, below = int(half + 0.3 * IN), int(1.0 * IN), int(1.8 * IN)
    w, h = 2 * halfw, top + below
    px = np.arange(w, dtype=np.float32) - halfw
    q = (top - np.arange(h, dtype=np.float32))[:, None]          # up from the ledge
    hp = np.zeros(w, np.float32)
    for _ in range(int(r.integers(2, 6))):                       # its humps: low and round, ash will not stand steep
        hp += r.uniform(0.35, 1.0) * np.exp(-((px - r.uniform(-0.55, 0.55) * half) / (r.uniform(0.28, 0.55) * half)) ** 2)
    hp *= np.clip(1 - (px / half) ** 2, 0, 1) ** 0.8
    hp /= hp.max()
    lump, patch = lnoise(h, w, 1.7, r), lnoise(h, w, 1.4, r)
    g1, g2 = grains(h, w, r, 0.3), grains(h, w, r, 0.9)
    surf = hp[None, :] * half * r.uniform(0.3, 0.42) + 7 * S * (lump - 0.5)
    lip = hp[None, :] ** 0.7 * r.uniform(5, 16) * S * (0.3 + 1.4 * patch)       # a little of it hangs over the edge
    heap = smooth(surf - q + 2.2 * S * g1, 0, 2 * S) * smooth(q + lip + 2.2 * S * g1, 0, 2 * S) * (hp[None, :] > 0.02)   # a grainy edge: it is powder
    up = np.clip(q / np.maximum(surf, 1), 0, 1)
    gy_, gx_ = np.gradient(wblur(lump, 2 * S) * 50 * S + surf * 0.5)
    pale = np.clip(0.25 + 0.5 * smooth(up, 0.2, 0.9) + 0.5 * smooth(np.gradient(hp)[None, :] * half, -0.5, 0.4) - 0.7 * smooth(patch, 0.45, 0.7), 0, 1)
    col = mix(ASH[1], ASH[0], pale)                              # grey ash and pale, paler on top and toward the light
    col = col * ((1 + 0.09 * np.tanh((gx_ + gy_) * 0.9)) * (1 + 0.05 * g1))[..., None]
    col = mix(col, ASH[2], smooth(g2, 1.25, 1.6) * 0.9)          # flecked with cinders
    col = mix(col, ASH[0] * 1.06, smooth(-g2, 1.4, 1.8) * 0.9)   # and with white
    im, d = canvas(w, h)                                          # and a few charred bits in it
    for _ in range(int(r.integers(5, 14))):
        bx = r.uniform(-0.8, 0.8) * half
        by = top - float(np.interp(bx, px, surf[top])) * r.uniform(0.1, 0.85)
        a, ln, th = r.uniform(0, math.pi), r.uniform(2, 6) * S, r.uniform(1.5, 3.5) * S
        c, s_ = math.cos(a), math.sin(a)
        d.polygon([((bx + halfw + u * c - v * s_) * SS, (by + u * s_ + v * c) * SS)
                   for u, v in ((-ln, -th * r.uniform(0.5, 1)), (ln, -th * r.uniform(0.5, 1)), (ln * r.uniform(0.6, 1), th), (-ln * r.uniform(0.6, 1), th))], fill=255)
    col = mix(col, ASH[2] * 0.9, boxed(im))
    del im, d
    # what sifted off the edge: specks down the wall under it, thick at the edge, thinning, in trails
    reach_ = wblur(np.tile(hp ** 0.5, (8, 1)), 14 * S)[0][None, :]
    dens = reach_ * np.exp(-np.clip(-q, 0, None) / (r.uniform(90, 230) * S)) * (q < 0) * (0.3 + 1.4 * lnoise(h, w, 1.3, r, stretch=(1.0, 0.05)))
    fall = smooth(g2 - 2.2 + 2.6 * np.clip(dens, 0, 1), 0, 0.3) * (dens > 0.03)
    ix = window(x - halfw, y - top, w, h)
    sub = img[ix]
    sub = sub * (1 - 0.25 * np.clip(wblur(shift(heap, 4 * S, 4 * S), 1.2 * S) - heap, 0, 1))[..., None]      # its shade on the wall
    sub = mix(sub, np.where((g1 > 0.9)[..., None], ASH[2], ASH[0]), fall * 0.8)
    img[ix] = mix(sub, col, heap)
    kind[ix] = np.where((heap > 0.02) | (fall > 0.05), 3, kind[ix])


def ash_smear(x, y, paw, r):
    """Ash smeared on the wall about (x, y): a paw pressed there and dragged
    along an arc, or something broad rubbed to and fro."""
    length = r.uniform(1.0, 2.2) * IN
    half = int(length * 0.7 + 0.5 * IN)
    side_ = 2 * half
    PY, PX = np.mgrid[0:side_, 0:side_].astype(np.float32)
    tw, tl = round(300 * S), int(length + 200 * S)
    oval = lambda s, t, s0, t0, ls, lt: np.exp(-(((s - s0) / ls) ** 2 + ((t - t0) / lt) ** 2) ** 2)

    def drag(sx, sy, a0, bend, sgn):
        """Where each point lies along (s) and across (t) an arc from (sx, sy) heading a0, and the dry streaks along it (0..1)."""
        rho = length / bend
        cx_, cy_ = sx - sgn * rho * math.sin(a0), sy + sgn * rho * math.cos(a0)
        s = (((np.arctan2(PY - cy_, PX - cx_) - math.atan2(sy - cy_, sx - cx_)) * sgn + math.pi) % TAU - math.pi) * rho
        t = (np.hypot(PX - cx_, PY - cy_) - rho) * sgn
        tex = grains(tw, tl, r, 0.9, stretch=(0.03, 1.0))
        return s, t, np.clip(0.5 + 0.3 * tex[np.clip(t + tw / 2, 0, tw - 1).astype(int), np.clip(s + 90 * S, 0, tl - 1).astype(int)], 0, 1)

    a0 = r.uniform(0, TAU)
    dark, pale = (np.zeros((side_, side_), np.float32) for _ in range(2))
    g1 = grains(side_, side_, r, 0.6)
    if paw:                                       # the big pad and its heel, four toes ahead of it, a streak dragged from each
        s, t, st = drag(half - length / 2 * math.cos(a0), half - length / 2 * math.sin(a0), a0, r.uniform(0.25, 1.2), float(r.choice([-1, 1])))
        gap = r.uniform(25, 32) * S
        press = oval(s, t, -2.45 * gap, 0, 0.72 * gap, 1.15 * gap)
        for lobe in (-1, 0, 1):
            press += oval(s, t, -3.05 * gap, lobe * 0.78 * gap, 0.45 * gap, 0.45 * gap)
        dens = 0.0
        for i in range(4):
            ti, wd = (i - 1.5) * gap + r.normal(0, 1.5 * S), r.uniform(6.5, 9) * S
            s0, ln = -0.55 * gap * abs(i - 1.5) ** 1.6 + r.uniform(0, 4 * S), length * r.uniform(0.5, 1.0)
            press += oval(s, t, s0, ti, 0.55 * gap, 0.4 * gap)
            dens = dens + np.exp(-((t - ti) / wd) ** 4) * smooth(s - s0, 0, 0.4 * gap) * np.clip(1 - (s - s0) / ln, 0, 1) ** 1.4
        dark = np.maximum(smooth(dens * (0.1 + 1.6 * st), 0.38, 0.52), smooth(np.clip(press, 0, 1) * (0.78 + 0.1 * g1), 0.5, 0.62))
        pale = smooth(dens * (1.7 - 1.6 * st), 0.5, 0.7) * (1 - dark)
    else:
        sx, sy = half - length / 2 * math.cos(a0), half - length / 2 * math.sin(a0)
        for k in range(int(r.integers(3, 6))):    # to and fro, each pass a little off the last
            s, t, st = drag(sx + r.normal(0, 14 * S), sy + r.normal(0, 14 * S), a0 + r.normal(0, 0.12), r.uniform(0.2, 0.9), float(r.choice([-1, 1])))
            wd, ln = r.uniform(26, 48) * S, length * r.uniform(0.55, 1.0)
            dens = np.exp(-(t / wd) ** 4) * smooth(s, 0, 30 * S) * np.clip(1 - s / ln, 0, 1) ** 0.8
            dark = np.maximum(dark, smooth(dens * (0.1 + 1.6 * st), 0.42, 0.56))
            pale = np.maximum(pale, smooth(dens * (1.7 - 1.6 * st), 0.5, 0.7))
            sx, sy, a0 = sx + ln * math.cos(a0), sy + ln * math.sin(a0), a0 + math.pi + r.normal(0, 0.18)   # and back
        pale *= 1 - dark
    ix = window(x - half, y - half, side_, side_)
    sub = mix(img[ix], ASH[2] * (1 + 0.05 * g1)[..., None], dark * (0.66 + 0.1 * np.clip(g1, -1, 1)))
    img[ix] = mix(sub, ASH[0], pale * 0.55)
    kind[ix] = np.where((dark > 0.03) | (pale > 0.03), 3, kind[ix])


for x, y, half in ASH_LEDGE:
    ash_heap(x, y, half, more)
for i, (x, y) in enumerate(SMEARS):
    ash_smear(x, y, i % 2 == 0, more)

# MARKS-END
# an exact palette, no dither: the wall's tones, and the aether's apart from
# them (a median cut over the whole tile spends nothing on so few pixels)
rgb = (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)
del img
pal = []
for sel, n in ((~aether, 160 - AETHER_COLOURS), (aether, AETHER_COLOURS)):
    px = rgb[sel][None]
    q = Image.fromarray(px, "RGB").quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal += q.getpalette()[:3 * n]
palimg = Image.new("P", (1, 1))
palimg.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
out = Image.fromarray(rgb, "RGB").quantize(palette=palimg, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-11.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-11.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  {len(rifts)} rifts  "
      f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
