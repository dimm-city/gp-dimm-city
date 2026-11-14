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
    print(f"  {len(shards)} shards  void {int((1 - outside).sum())} px", flush=True)

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
