"""Draw wall 7, rusted steel plate (`@page wall-7`), as images/wall-7.png.

    python3 scripts/wall-metal.py        (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the streaks are a circular convolution,
and the plates, seams and rivets are laid on the tile's own grid.

What it draws, back to front:
1. Steel plates, two by two in a running bond (the lower row shifted half a
   plate), each a slightly different grey, brushed along its own grain.
2. Rust: a blotchy, fractal mask, heavier at the seams and the plates' feet,
   in rust browns from dark umber to orange, pitted where it is thickest.
3. Rust streaks running down from the rivets and the seams.
4. The seams (a dark groove with a lit lip above it) and the rivet heads
   (a shaded dome) along every plate's edges.
5. Grime: the plates darken a little toward their foot.
It is then quantised to an exact palette, as the stone walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is).

At DPI (240, wall-tiles.py's) the tile is 10in square and a plate 2.5in
wide, so a page shows no repeat. Each plate weathers by its own amount. Its
plate grid is regular, so wall-tiles.py anchors this wall to the sheet, not
the text area, and offsets a right page by the left page's width: a spread
is one continuous wall.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SIZE = 2400                 # px, square; 10in at 240 DPI, so a page shows no repeat
PLATES = 4                  # plates a side (each 2.5in)
SEAM = 7                    # groove width, px
RIVET_R = 9                 # rivet head radius, px
RIVET_STEP = 100            # rivet pitch along an edge, px
RIVET_IN = 26               # rivet line's distance in from the plate edge, px
SEED = 7
SHADE = 0.85                # the whole tile, darker than the stone walls; its darkest rust stays well under DriveThruRPG's 240% TAC

rng = np.random.default_rng(SEED)
N = SIZE


def noise(beta, stretch=(1.0, 1.0), seed=None):
    """Periodic 1/f^beta noise in [0, 1]. `stretch` (sx, sy) > 1 elongates it
    along that axis (brushing)."""
    r = np.random.default_rng(seed) if seed is not None else rng
    white = r.standard_normal((N, N))
    fy = np.fft.fftfreq(N)[:, None] * stretch[1]
    fx = np.fft.fftfreq(N)[None, :] * stretch[0]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    out = np.real(np.fft.ifft2(np.fft.fft2(white) / f ** beta))
    out -= out.min()
    return out / out.max()


def circ_conv(img, kernel):
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(kernel)))


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


yy, xx = np.mgrid[0:N, 0:N]
P = N // PLATES

# ── 1. plates: index of each pixel's plate, and its local coordinates ──────────
row = yy // P
shift = (row % 2) * (P // 2)
px = (xx + shift) % N
col = px // P
lx, ly = px % P, yy % P                     # position inside its plate
plate_id = row * PLATES + col

tone = rng.uniform(0.70, 0.80, PLATES * PLATES)[plate_id]
vertical = (rng.random(PLATES * PLATES) < 0.35)[plate_id]
grain_h = noise(1.2, stretch=(0.04, 1.0), seed=SEED + 1)      # long along x
grain_v = noise(1.2, stretch=(1.0, 0.04), seed=SEED + 2)      # long along y
grain = np.where(vertical, grain_v, grain_h)
mottle = noise(2.2, seed=SEED + 3)
scuff = noise(1.5, seed=SEED + 9)
steel = tone + (grain - 0.5) * 0.16 + (mottle - 0.5) * 0.16 + (scuff - 0.5) * 0.08
steel = np.stack([steel * 0.985, steel * 0.99, steel * 1.0], -1)   # a cool steel grey

# ── 2. rust mask: blotches, heavier near seams and at the plates' feet ─────────
edge = np.minimum.reduce([lx, P - lx, ly, P - ly]).astype(float)
near_edge = np.exp(-edge / 60.0)
foot = smooth(ly / P, 0.55, 1.0)
blot = noise(1.9, seed=SEED + 4)
fine = noise(1.1, seed=SEED + 5)
speck = noise(0.4, seed=SEED + 10)
weather = rng.uniform(-0.20, 0.10, PLATES * PLATES)[plate_id]   # some plates nearly clean, some eaten through
rust_field = 0.70 * blot + 0.30 * fine + 0.12 * near_edge + 0.10 * foot + weather
rust = smooth(rust_field, 0.60, 0.80)
rust = np.maximum(rust, smooth(speck, 0.80, 0.93) * 0.7)      # pinprick spots all over

# ── 3. streaks running down from rivets and seams ──────────────────────────────
sources = np.zeros((N, N))
rivets = []
for r in range(PLATES):
    for c in range(PLATES):
        x0 = (c * P - (r % 2) * (P // 2)) % N
        y0 = r * P
        for t in range(RIVET_IN, P - RIVET_IN + 1, RIVET_STEP):
            for (x, y) in ((x0 + t, y0 + RIVET_IN), (x0 + t, y0 + P - RIVET_IN),
                           (x0 + RIVET_IN, y0 + t), (x0 + P - RIVET_IN, y0 + t)):
                rivets.append((x % N, y % N))
rivets = sorted(set(rivets))
long_src = np.zeros((N, N))
for (x, y) in rivets:
    roll = rng.random()
    if roll < 0.30:
        sources[(y + RIVET_R) % N, x] += rng.uniform(0.5, 1.0)
    elif roll < 0.45:
        long_src[(y + RIVET_R) % N, x] += rng.uniform(0.5, 1.0)
seam_rows = sorted({(r * P) % N for r in range(PLATES)})
for y in seam_rows:
    for x in rng.choice(N, 10, replace=False):
        (long_src if rng.random() < 0.4 else sources)[(y + SEAM) % N, x] += rng.uniform(0.3, 0.8)
ky, kx = np.mgrid[0:N, 0:N]
ky = np.where(ky > N // 2, ky - N, ky)
kx = np.where(kx > N // 2, kx - N, kx)
def drip(length, width):
    return np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2)
streaks = circ_conv(sources, drip(60.0, 3.0)) + circ_conv(long_src, drip(220.0, 2.0))
streaks = np.clip(streaks / np.percentile(streaks[streaks > 0], 99), 0, 1)
streaks *= smooth(noise(1.0, stretch=(1.0, 0.12), seed=SEED + 6), 0.25, 0.75)
rust = np.clip(np.maximum(rust, streaks * 0.85), 0, 1)

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
colour = colour * (0.80 + 0.40 * crust)[..., None]
colour = colour * 0.85 + colour.mean(-1, keepdims=True) * 0.15
img = steel * (1 - rust[..., None]) + colour * rust[..., None]

# pitting where the rust is thick
pits = (noise(0.6, seed=SEED + 8) > 0.86) & (rust > 0.6)
img[pits] *= 0.72

# ── 4. seams and rivets ───────────────────────────────────────────────────────
def shade(mask_bool, factor):
    img[mask_bool] *= factor

for y in seam_rows:                                     # horizontal seams
    for d in range(SEAM):
        shade(yy == (y + d) % N, 0.42 + 0.04 * d)
    shade(yy == (y + SEAM) % N, 1.10)                   # lit lip under the groove
    shade(yy == (y - 1) % N, 0.85)
vseam = (px % P) < SEAM                                 # vertical seams, offset per row
img[vseam] *= (0.45 + 0.05 * (px % P)[vseam])[..., None]
img[((px % P) == SEAM)] *= 1.10

for (x, y) in rivets:
    x0, x1 = x - RIVET_R - 3, x + RIVET_R + 4
    y0, y1 = y - RIVET_R - 3, y + RIVET_R + 4
    sy, sx = np.mgrid[y0:y1, x0:x1]
    dy, dx = sy - y, sx - x
    d = np.sqrt(dx * dx + dy * dy)
    head = d <= RIVET_R
    shadow = (np.sqrt((dx - 2.5) ** 2 + (dy - 2.5) ** 2) <= RIVET_R) & ~head
    light = np.clip(1.15 - ((dx + 3) ** 2 + (dy + 3) ** 2) / (RIVET_R * RIVET_R * 2.2), 0.55, 1.15)
    ys, xs = sy % N, sx % N
    img[ys[shadow], xs[shadow]] *= 0.55
    hv = img[ys[head], xs[head]]
    img[ys[head], xs[head]] = np.clip(hv * 0.6 + 0.35 * light[head][:, None] * np.array([0.92, 0.9, 0.88]), 0, 1)

# scratches: thin straight lines at random angles, lighter or darker
for _ in range(70):
    x, y = rng.uniform(0, N, 2)
    a = rng.uniform(0, np.pi) if rng.random() < 0.4 else rng.normal(0, 0.15) + (np.pi / 2 if rng.random() < 0.5 else 0)
    L = rng.uniform(30, 160)
    t = np.linspace(0, L, int(L))
    xs = ((x + t * np.cos(a)).astype(int)) % N
    ys = ((y + t * np.sin(a)).astype(int)) % N
    img[ys, xs] *= rng.choice([0.82, 1.12])

# ── 5. grime toward each plate's foot ─────────────────────────────────────────
img *= (1 - 0.10 * smooth(ly / P, 0.6, 1.0))[..., None]

out = Image.fromarray((np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8), "RGB")
out = out.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-7.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-7.png  {SIZE}x{SIZE}  {SIZE / 240:.2f}in  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
