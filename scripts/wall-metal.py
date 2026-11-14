"""Draw wall 7, rusted steel plate (`@page wall-7`), as images/wall-7.png.

    python3 scripts/wall-metal.py        (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the streaks are a circular convolution,
and the plates, seams and rivets are laid on the tile's own grid.

What it draws, back to front:
1. Steel plates in a running bond (every other row shifted half a plate),
   each a slightly different grey, brushed along its own grain.
2. Rust: a blotchy, fractal mask, heavier at the seams and the plates' feet,
   in rust browns from dark umber to orange, pitted where it is thickest.
3. Rust streaks running down from the rivets and the seams.
4. The seams (a dark groove with a lit lip above it) and the rivet heads
   (a shaded dome) along every plate's edges.
5. The damage: dents and a shotgun's spread of small ones; bullet holes,
   singly and in bursts (a dished dent, a petalled rim round a dark hole, a
   powder halo, rust at the rim and bleeding down), glancing hits scraped
   bright; torch cuts (a kerf, dark oxide, then the steel's heat colours
   fading out from it: blue, purple, bronze, straw) and scorches; claw marks,
   three or four tapered gouges side by side, bright at the bottom.
6. Grime: the plates darken a little toward their foot.
It is then quantised to an exact palette, as the stone walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is).

At DPI (300) the tile is 17.5in x 15in and a plate 2.5in wide: wider than a
spread and taller than a page, so a spread shows no repeat (a bullet hole
that came round twice would give it away). Every length below was first
drawn at 240 DPI and is written as that many px times S (= DPI / 240), so the
wall keeps its size in inches at any DPI and only gains detail. The noise is
1/f^beta in pixel frequency, so its finest grain is always a pixel (its
coarser frequencies are the 240 DPI tile's, so the rust lies where it did); its
brushing stretch is a ratio, so a streak of a given width keeps its length in
inches. No blotch of rust or grime is larger than FEATURE (10in), whatever the
tile's size. Each plate weathers by its own amount. Its
plate grid is regular, so wall-tiles.py anchors this wall to the sheet, not
the text area, and offsets a right page by the left page's width: a spread
is one continuous wall.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DPI = 300
S = DPI / 240               # every length below was drawn at 240 DPI; this scales it
NW0, NH0 = round(17.5 * 240), round(15 * 240)   # the tile at 240 DPI, whose noise this one refines
NW, NH = round(17.5 * DPI), round(15 * DPI)   # px; 17.5in x 15in: wider than a spread and taller than a page, so a spread shows no repeat
FEATURE = 10 * DPI          # px (10in): the largest blotch of rust or grime, whatever the tile's size
P = round(2.5 * DPI)        # a plate, px (2.5in): 7 across, 6 down (an even count, so the running bond wraps)
SEAM = round(7 * S)         # groove width, px
RIVET_R = 9 * S             # rivet head radius, px
RIVET_STEP = round(100 * S) # rivet pitch along an edge, px (whole, so rivets sit evenly)
RIVET_IN = round(26 * S)    # rivet line's distance in from the plate edge, px
SEED = 7
SHADE = 0.85                # the whole tile, darker than the stone walls; its darkest rust stays well under DriveThruRPG's 240% TAC

rng = np.random.default_rng(SEED)


def white_spectrum(seed):
    """The spectrum of white noise on the tile, the same wall at any DPI: its
    frequencies up to 240 DPI's Nyquist are those of the 240 DPI tile's noise
    (so every blotch lands where it did), and only the finer ones above are new.
    Half of it (rfft2's), as the noise is real: the 240 DPI tile's Nyquist row
    and column land on one side only, so there the two halves are averaged, as
    taking the real part of the full inverse did."""
    base = np.fft.rfft2(np.random.default_rng(seed).standard_normal((NH0, NW0)))
    if (NH, NW) == (NH0, NW0):
        return base
    spec = np.fft.rfft2(np.random.default_rng([seed, DPI]).standard_normal((NH, NW)))
    base *= np.sqrt(NH * NW / (NH0 * NW0))
    hy, hx = NH0 // 2, NW0 // 2
    iy = np.round(np.fft.fftfreq(NH0) * NH0).astype(int) % NH
    za, zb = spec[NH - hy, :hx].copy(), spec[hy, :hx].copy()     # the Nyquist row (-hy) and its unpaired mirror (+hy)
    spec[iy, :hx] = base[:, :hx]
    spec[NH - hy, :hx] = (base[hy, :hx] + za) / 2
    spec[hy, :hx] = (base[hy, :hx] + zb) / 2
    fr = np.round(np.fft.fftfreq(NH) * NH).astype(int)          # the Nyquist column (+hx) and its mirror
    ok = (fr > -hy) & (fr <= hy)
    spec[ok, hx] = (spec[ok, hx] + base[fr[ok] % NH0, hx]) / 2
    return spec


def noise(beta, stretch=(1.0, 1.0), seed=None):
    """Periodic 1/f^beta noise in [0, 1]. `stretch` (sx, sy) > 1 elongates it
    along that axis (brushing)."""
    if seed is None:
        white = np.fft.rfft2(rng.standard_normal((NH, NW)))
    else:
        white = white_spectrum(seed)
    fy = np.fft.fftfreq(NH)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(NW)[None, :] * stretch[0]
    f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / FEATURE)    # no blotch larger than FEATURE
    f[0, 0] = 1.0
    white /= f ** beta
    out = np.fft.irfft2(white, s=(NH, NW))
    out -= out.min()
    out /= out.max()
    return out


def circ_conv(img, kernel):
    """A circular convolution; `kernel` is a kernel or its rfft2."""
    if kernel.dtype.kind != "c":
        kernel = np.fft.rfft2(kernel)
    return np.fft.irfft2(np.fft.rfft2(img) * kernel, s=img.shape)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def roll_f(a, s):
    """np.roll by (s, s) px, wrapped, where s need not be whole: linear between
    the two whole shifts on each axis."""
    i = int(np.floor(s))
    f = s - i
    for ax in (0, 1):
        a = (1 - f) * np.roll(a, i, ax) + f * np.roll(a, i + 1, ax)
    return a


yy, xx = np.indices((NH, NW), dtype=np.int32)
PX, PY = NW // P, NH // P

# ── 1. plates: index of each pixel's plate, and its local coordinates ──────────
row = yy // P
shift = (row % 2) * (P // 2)
px = (xx + shift) % NW
col = px // P
lx, ly = px % P, yy % P                     # position inside its plate
plate_id = row * PX + col

tone = rng.uniform(0.70, 0.80, PX * PY)[plate_id]
vertical = (rng.random(PX * PY) < 0.35)[plate_id]
grain_h = noise(1.2, stretch=(0.04, 1.0), seed=SEED + 1)      # long along x
grain_v = noise(1.2, stretch=(1.0, 0.04), seed=SEED + 2)      # long along y
grain = np.where(vertical, grain_v, grain_h)
mottle = noise(2.2, seed=SEED + 3)
scuff = noise(1.5, seed=SEED + 9)
steel = tone + (grain - 0.5) * 0.16 + (mottle - 0.5) * 0.16 + (scuff - 0.5) * 0.08
steel = np.stack([steel * 0.985, steel * 0.99, steel * 1.0], -1)   # a cool steel grey
del grain_v, grain, mottle, scuff, tone, vertical       # (the tile is big: free what is done with)

# ── 2. rust mask: blotches, heavier near seams and at the plates' feet ─────────
edge = np.minimum.reduce([lx, P - lx, ly, P - ly]).astype(float)
near_edge = np.exp(-edge / (60.0 * S))
foot = smooth(ly / P, 0.55, 1.0)
blot = noise(1.9, seed=SEED + 4)
fine = noise(1.1, seed=SEED + 5)
speck = noise(0.4, seed=SEED + 10)
weather = rng.uniform(-0.20, 0.10, PX * PY)[plate_id]   # some plates nearly clean, some eaten through
rust_field = 0.70 * blot + 0.30 * fine + 0.12 * near_edge + 0.10 * foot + weather
rust = smooth(rust_field, 0.60, 0.80)
rust = np.maximum(rust, smooth(speck, 0.80, 0.93) * 0.7)      # pinprick spots all over
del edge, near_edge, foot, blot, fine, speck, weather, rust_field, lx, xx, row, shift, col, plate_id

# ── 3. streaks running down from rivets and seams ──────────────────────────────
sources = np.zeros((NH, NW))
rivets = []
for r in range(PY):
    for c in range(PX):
        x0 = (c * P - (r % 2) * (P // 2)) % NW
        y0 = r * P
        for t in range(RIVET_IN, P - RIVET_IN + 1, RIVET_STEP):
            for (x, y) in ((x0 + t, y0 + RIVET_IN), (x0 + t, y0 + P - RIVET_IN),
                           (x0 + RIVET_IN, y0 + t), (x0 + P - RIVET_IN, y0 + t)):
                rivets.append((x % NW, y % NH))
rivets = sorted(set(rivets))
long_src = np.zeros((NH, NW))
for (x, y) in rivets:
    roll = rng.random()
    if roll < 0.30:
        sources[(y + round(RIVET_R)) % NH, x] += rng.uniform(0.5, 1.0)
    elif roll < 0.45:
        long_src[(y + round(RIVET_R)) % NH, x] += rng.uniform(0.5, 1.0)
seam_rows = sorted({(r * P) % NH for r in range(PY)})
for y in seam_rows:
    for x in rng.choice(NW, 18, replace=False):
        (long_src if rng.random() < 0.4 else sources)[(y + SEAM) % NH, x] += rng.uniform(0.3, 0.8)
ky = np.arange(NH)[:, None]                 # signed offsets, broadcast (a full grid of each costs memory)
kx = np.arange(NW)[None, :]
ky = np.where(ky > NH // 2, ky - NH, ky)
kx = np.where(kx > NW // 2, kx - NW, kx)
def drip(length, width):
    return np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2)
# (a full complex FFT here, not circ_conv's real one: the percentile below
# counts every pixel over 0, the FFT's rounding noise too, so its scale, and
# the wall, would shift a little with any other transform)
streaks = (np.real(np.fft.ifft2(np.fft.fft2(sources) * np.fft.fft2(drip(60.0 * S, 3.0 * S))))
           + np.real(np.fft.ifft2(np.fft.fft2(long_src) * np.fft.fft2(drip(220.0 * S, 2.0 * S)))))
streaks = np.clip(streaks / np.percentile(streaks[streaks > 0], 99), 0, 1)
streaks *= smooth(noise(1.0, stretch=(1.0, 0.12), seed=SEED + 6), 0.25, 0.75)
rust = np.clip(np.maximum(rust, streaks * 0.85), 0, 1)
del sources, long_src, streaks

# rust colour: umber in the thick of it, orange at the edges of a patch
umber = np.array([0x5c, 0x32, 0x1c]) / 255
rustc = np.array([0x93, 0x4a, 0x22]) / 255
ochre = np.array([0xb8, 0x74, 0x3c]) / 255
depth = noise(1.6, seed=SEED + 7)
colour = np.where((depth > 0.55)[..., None],
                  rustc + (umber - rustc) * smooth(depth, 0.55, 0.9)[..., None],
                  ochre + (rustc - ochre) * smooth(depth, 0.2, 0.55)[..., None])
# flaky crust: fine grain lightens and darkens the rust, a little muted toward grey
crust = noise(0.35, seed=SEED + 11)
colour *= (0.80 + 0.40 * crust)[..., None]
grey = colour.mean(-1, keepdims=True)
colour *= 0.85
colour += grey * 0.15
steel *= 1 - rust[..., None]
colour *= rust[..., None]
img = steel
img += colour
del steel, colour, grey, depth, crust

# pitting where the rust is thick
pits = (noise(0.6, seed=SEED + 8) > 0.86) & (rust > 0.6)
img[pits] *= 0.72
del rust, pits

# ── 4. seams and rivets ───────────────────────────────────────────────────────
for y in seam_rows:                                     # horizontal seams
    for d in range(SEAM):
        img[(y + d) % NH] *= 0.42 + 0.04 * d / S
    img[(y + SEAM) % NH] *= 1.10                         # lit lip under the groove
    img[(y - 1) % NH] *= 0.85
vseam = (px % P) < SEAM                                 # vertical seams, offset per row
img[vseam] *= (0.45 + 0.05 * (px % P)[vseam] / S)[..., None]
img[((px % P) == SEAM)] *= 1.10
del vseam, px, yy

for (x, y) in rivets:
    x0, x1 = x - int(np.ceil(RIVET_R + 3 * S)), x + int(np.ceil(RIVET_R + 4 * S))
    y0, y1 = y - int(np.ceil(RIVET_R + 3 * S)), y + int(np.ceil(RIVET_R + 4 * S))
    sy, sx = np.mgrid[y0:y1, x0:x1]
    dy, dx = sy - y, sx - x
    d = np.sqrt(dx * dx + dy * dy)
    head = d <= RIVET_R
    shadow = (np.sqrt((dx - 2.5 * S) ** 2 + (dy - 2.5 * S) ** 2) <= RIVET_R) & ~head
    light = np.clip(1.15 - ((dx + 3 * S) ** 2 + (dy + 3 * S) ** 2) / (RIVET_R * RIVET_R * 2.2), 0.55, 1.15)
    ys, xs = sy % NH, sx % NW
    img[ys[shadow], xs[shadow]] *= 0.55
    hv = img[ys[head], xs[head]]
    img[ys[head], xs[head]] = np.clip(hv * 0.6 + 0.35 * light[head][:, None] * np.array([0.92, 0.9, 0.88]), 0, 1)

# scratches: thin straight lines at random angles, lighter or darker
for _ in range(180):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    a = rng.uniform(0, np.pi) if rng.random() < 0.4 else rng.normal(0, 0.15) + (np.pi / 2 if rng.random() < 0.5 else 0)
    L = rng.uniform(30 * S, 160 * S)
    t = np.linspace(0, L, int(L))
    xs = ((x + t * np.cos(a)).astype(int)) % NW
    ys = ((y + t * np.sin(a)).astype(int)) % NH
    img[ys, xs] *= rng.choice([0.82, 1.12])

# ── 5. the damage: dents, bullet holes, torch cuts, claw marks ─────────────────
_gauss = {}


def blur(m, sigma):
    """A Gaussian blur, wrapped round `m`: the tile, or a patch with room round its shape."""
    key = sigma, m.shape
    if key not in _gauss:                   # the kernel's spectrum, once a sigma and shape
        oy, ox = (np.where(np.arange(n) > n // 2, np.arange(n) - n, np.arange(n)) for n in m.shape)
        g = np.exp(-(ox[None, :] ** 2 + oy[:, None] ** 2) / (2 * sigma * sigma))
        _gauss[key] = np.fft.rfft2(g / g.sum())
    return circ_conv(m, _gauss[key])


def wrapped(draw):
    """Draw on a tile-sized mask (0-255) through `draw(d, ox, oy)` at every wrap offset."""
    m = Image.new("L", (NW, NH), 0)
    d = ImageDraw.Draw(m)
    for ox in (-NW, 0, NW):
        for oy in (-NH, 0, NH):
            draw(d, ox, oy)
    return np.asarray(m)


def patch(x, y, R):
    """A square patch round (x, y), wrapped: its index and the offsets from the centre."""
    sy, sx = np.mgrid[int(y) - R:int(y) + R + 1, int(x) - R:int(x) + R + 1]
    return (sy % NH, sx % NW), sx - x, sy - y


def dish(x, y, R, depth):
    """A dent: a shallow dish, its upper-left side in shade and its lower-right lit."""
    ix, dx, dy = patch(x, y, int(R))
    d = np.hypot(dx, dy) / R
    bump = np.clip(1 - d * d, 0, 1) ** 1.5
    img[ix] *= (1 + depth * bump * (dx + dy) / (R * 1.41))[..., None]


crust_n = noise(0.6, seed=SEED + 21)
HOLE_C = np.array([0x38, 0x33, 0x2e]) / 255
bleed = np.zeros((NH, NW))                  # rust that runs from a hole


def bullet(x, y, r):
    """A round through the plate: a dished dent, a petalled rim pushed up round
    a dark hole, a powder halo, rust starting at the rim."""
    R = int(r * 4)
    dish(x, y, r * 3.2, 0.30)
    ix, dx, dy = patch(x, y, R)
    d = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    k, ph = int(rng.integers(5, 9)), rng.uniform(0, 2 * np.pi)
    edge = r * (1 + 0.09 * np.sin(k * th + ph) + 0.04 * np.sin(2 * k * th + ph * 2))
    rim = (d >= edge) & (d < edge + r * 0.55)
    hole = d < edge
    halo = np.exp(-((d / (r * 2.6)) ** 2))
    img[ix] *= (1 - 0.22 * halo * (d >= edge))[..., None]
    lit = np.clip(-(dx + dy) / (d + 1e-6) / 1.41, -1, 1)
    sub = img[ix]
    sub[rim] *= (1 + 0.32 * lit[rim])[:, None]
    sub[hole] = HOLE_C * (0.9 + 0.25 * np.clip((dx + dy)[hole] / (r * 1.41), 0, 1))[:, None]
    img[ix] = sub
    if rng.random() < 0.6:
        ring = (d >= edge + r * 0.4) & (d < edge + r * 1.3) & (crust_n[ix] > 0.45)
        sub = img[ix]
        sub[ring] = sub[ring] * 0.65 + rustc * 0.35
        img[ix] = sub
        bleed[int(y + r * 1.5) % NH, int(x) % NW] += rng.uniform(0.5, 1.0)


# dents, and a shotgun's spread of small ones
for _ in range(20):
    dish(rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(35 * S, 90 * S), rng.uniform(0.12, 0.22))
for _ in range(2):
    cx, cy = rng.uniform(0, NW), rng.uniform(0, NH)
    for _ in range(int(rng.integers(18, 30))):
        a, rr = rng.uniform(0, 2 * np.pi), abs(rng.normal(0, 70 * S))
        dish(cx + rr * np.cos(a), cy + rr * np.sin(a), rng.uniform(4 * S, 7 * S), 0.6)

# bullet holes: singles, and bursts of a few close together
for _ in range(28):
    bullet(rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(6 * S, 10 * S))
for _ in range(6):
    cx, cy = rng.uniform(0, NW), rng.uniform(0, NH)
    a0 = rng.uniform(0, np.pi)
    for i in range(int(rng.integers(3, 7))):
        t = rng.normal(0, 60 * S)
        bullet(cx + t * np.cos(a0) + rng.normal(0, 18 * S), cy + t * np.sin(a0) + rng.normal(0, 18 * S), rng.uniform(6 * S, 9 * S))
# glancing hits: a scraped teardrop, bright where the round skidded
for _ in range(9):
    x, y, a, L = rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, np.pi), rng.uniform(40 * S, 90 * S)
    hw = 6 * S
    gl = wrapped(lambda d, ox, oy: d.polygon([(x + ox - hw * np.sin(a), y + oy + hw * np.cos(a)), (x + ox + L * np.cos(a), y + oy + L * np.sin(a)),
                                               (x + ox + hw * np.sin(a), y + oy - hw * np.cos(a))], fill=255))
    ix, _, _ = patch(x, y, int(L + hw) + 16)          # blurred and laid on a patch round it, with room for its blur and shadow
    gl = blur(gl[ix] / 255, 0.8 * S)
    sub = img[ix]
    sub = sub * (1 - gl[..., None]) + (np.array([0.74, 0.73, 0.70]) * (0.9 + 0.2 * grain_h[ix])[..., None]) * gl[..., None]
    sub *= (1 - 0.45 * np.clip(gl - roll_f(gl, 2 * S), 0, 1))[..., None]
    img[ix] = sub
bleed_s = circ_conv(bleed, drip(45.0 * S, 2.0 * S))
if bleed_s.max() > 0:
    bleed_s = np.clip(bleed_s / np.percentile(bleed_s[bleed_s > 1e-4], 99), 0, 1)
    img *= 1 - 0.45 * bleed_s[..., None]
    img += rustc * 0.45 * bleed_s[..., None]
del bleed, bleed_s

# torch cuts: a kerf burnt through, dark oxide along it, the steel's heat
# colours fading out from it (blue, purple, bronze, straw); and two scorches
HEAT = [(0.0 * S, (0x30, 0x2d, 0x2a), 1.0),       # the kerf
        (1.0 * S, (0x30, 0x2d, 0x2a), 1.0),
        (2.6 * S, (0x4e, 0x4a, 0x46), 0.9),       # dark oxide
        (7.0 * S, (0x3e, 0x58, 0x8a), 0.8),       # blue
        (13.0 * S, (0x6c, 0x4a, 0x7c), 0.7),      # purple
        (24.0 * S, (0x8c, 0x62, 0x3e), 0.55),     # bronze
        (36.0 * S, (0xb4, 0x98, 0x5c), 0.4),      # straw
        (54.0 * S, (0xa0, 0x8a, 0x6c), 0.0)]      # gone
paths = []
for _ in range(4):
    x, y, a = rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, 2 * np.pi)
    pts = [(x, y)]
    for _ in range(int(rng.integers(12, 30))):
        a += rng.normal(0, 0.06)                                  # a hand-held torch: near straight, a little wander
        x, y = x + 20 * S * np.cos(a) + rng.normal(0, 0.8 * S), y + 20 * S * np.sin(a) + rng.normal(0, 0.8 * S)
        pts.append((x, y))
    paths.append(pts)
cut = wrapped(lambda d, ox, oy: [d.line([(px + ox, py + oy) for px, py in pts], fill=255, width=1) for pts in paths]) / 255
spots = [(rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(8 * S, 16 * S)) for _ in range(2)]
spot = wrapped(lambda d, ox, oy: [d.ellipse((x + ox - r, y + oy - r, x + ox + r, y + oy + r), fill=255) for x, y, r in spots]) / 255
SIG = 16.0 * S
heat = blur(cut, SIG)
heat = np.clip(heat / heat[cut > 0.5].mean(), 1e-9, 1)
dist = SIG * np.sqrt(-2 * np.log(heat))
heat_s = blur(spot, SIG)
heat_s = np.clip(heat_s / heat_s.max(), 1e-9, 1)
dist = np.minimum(dist, SIG * np.sqrt(-2 * np.log(heat_s)) + 3.5 * S)   # a scorch has no kerf
dist *= 0.8 + 0.4 * crust_n
del cut, spot, heat, heat_s
hd = [h[0] for h in HEAT]
tint = np.stack([np.interp(dist, hd, [h[1][i] / 255 for h in HEAT]) for i in range(3)], -1)
ta = np.interp(dist, hd, [h[2] for h in HEAT])
del dist
img *= 1 - ta[..., None]
tint *= (0.9 + 0.2 * crust_n)[..., None]
tint *= ta[..., None]
img += tint
del tint, ta, crust_n

# claw marks: three or four gouges side by side, tapered, fresh bright steel at
# the bottom of each, its upper-left wall in shade and its lower-right lit
claws = []
for _ in range(6):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    a = rng.uniform(0.6, 1.3) * rng.choice([1, -1]) + (np.pi if rng.random() < 0.3 else 0)
    L, bend, gap = rng.uniform(220 * S, 420 * S), rng.normal(0, 0.25), rng.uniform(20 * S, 30 * S)
    for k in range(int(rng.integers(3, 5))):
        o = (k - 1.5) * gap
        bx, by = x - o * np.sin(a), y + o * np.cos(a)
        L_k, w = L * rng.uniform(0.75, 1.0), rng.uniform(4.5 * S, 7.5 * S)
        side_a, side_b = [], []
        for t in np.linspace(0, 1, 40):
            aa = a + bend * (t - 0.5)
            cxp = bx + t * L_k * np.cos(a) - bend * L_k * 0.25 * (t * t - t) * np.sin(a)
            cyp = by + t * L_k * np.sin(a) + bend * L_k * 0.25 * (t * t - t) * np.cos(a)
            hw = w / 2 * np.sin(np.pi * min(1.0, t * 1.15)) ** 0.6
            side_a.append((cxp - hw * np.sin(aa), cyp + hw * np.cos(aa)))
            side_b.append((cxp + hw * np.sin(aa), cyp - hw * np.cos(aa)))
        claws.append(side_a + side_b[::-1])
G = wrapped(lambda d, ox, oy: [d.polygon([(px + ox, py + oy) for px, py in poly], fill=255) for poly in claws]) / 255
G = np.clip(blur(G, 0.7 * S), 0, 1)
fresh = np.array([0.76, 0.75, 0.72]) * (0.85 + 0.2 * grain_h)[..., None]
del grain_h
img *= 1 - 0.85 * G[..., None]
fresh *= 0.85
fresh *= G[..., None]
img += fresh
del fresh
img *= (1 - 0.55 * np.clip(G - roll_f(G, 3 * S), 0, 1))[..., None]      # the wall in shade
img *= (1 + 0.15 * np.clip(G - roll_f(G, -3 * S), 0, 1))[..., None]     # the wall lit
burr = np.clip(roll_f(G, 2 * S) - G, 0, 1)                              # metal thrown up along it
img *= (1 - 0.25 * burr)[..., None]

# ── 6. grime toward each plate's foot ─────────────────────────────────────────
img *= (1 - 0.10 * smooth(ly / P, 0.6, 1.0))[..., None]

img *= SHADE
np.clip(img, 0, 1, out=img)
img *= 255
out = Image.fromarray(img.astype(np.uint8), "RGB")
del img
out = out.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-7.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-7.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
