"""Draw wall 12, a technosorcerer's lab wall (`@page wall-12`), as images/wall-12.png.

    python3 scripts/wall-techlab.py      (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

The inside wall of a lab whose sorcerer is also a lighting and electronics
tech: an old plaster wall gone back to brick in places, with the trade's
clutter and the craft's on it side by side.

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the light and stains are worked out on
the tile's torus, and every shape is drawn with wrap-around (a run of conduit
across the whole width meets itself; a thing near an edge carries on at the
other).

What it draws, back to front:
1. The wall: lime plaster, once painted, trowelled, mottled, stained by
   water from above and grimed by hands, spalled off in places down to the
   brick (a shadow inside the broken edge, the lit lip opposite), old screw
   holes and anchors, pale ghosts where things hung.
2. What is written on it: two patches of blackboard paint, ritual diagrams
   in chalk, charcoal and a rust-red chalk (rings of glyphs, inscribed
   stars, and traces running out of them like a circuit board's, bending at
   45 degrees to pads and vias, a resistor's zigzag here and there, a chip
   in the middle), and columns of glyphs. The glyphs are made up, drawn
   from a stroke grid like runes; no real script.
3. Fixed to it: a breaker panel (two columns of breakers, a directory card,
   taped toggles, a sigil chalked on its cover), a pegboard of tools
   (screwdrivers, pliers, side cutters, a C-wrench, a hammer, tape, solder,
   a multimeter), plank shelves on iron brackets, a framed schematic that
   is half wiring diagram and half summoning circle.
4. The wiring: conduit across the top and the foot of the wall and down the
   left margin, held by straps, with junction boxes, switches and outlets;
   a stapled cable down by the spine and a bundle down the right margin.
5. On the shelves: jars, vials in a rack, candles, a skull, fresnel lenses;
   pinned up, a lamp-gel swatch book fanned out; hung up, coiled extension
   leads. Cables droop between hooks along the top, tied in bundles, one of
   them hung with bunches of drying herbs.
6. The light: caged bulbs (warm amber, the chapter's rust in it) and LED
   strips (teal and electric blue), baked in as soft opaque tints on
   whatever is near them; candle flames.
Everything stands out from the wall a little and casts a soft shadow down
and to the right (the room's light is from the upper left, as on the other
walls). It is then quantised to an exact palette, as the other walls are
(one colour per tone, lossless and small; an opaque tile PDF/X carries as
is), with VIVID_COLOURS of its 160 kept for the small saturated things (the
gels, the bulbs, the LEDs, tape, liquids, flames): a median cut over the
whole tile spends almost nothing on so few pixels and greys them.

Scale: the clutter is drawn at about 1:6 (a breaker panel about 2.2in wide,
a brick 1.2in). At DPI (240, wall-tiles.py's) the tile is 18in x 12in, wider
than a spread and taller than a page, so a spread shows no repeat. Its runs
of conduit cross the sheet, so wall-tiles.py anchors it to the sheet
(ALIGNED) and a right page carries on from the left page's width: a spread
is one wall, its cables running on across the spine. Anchored so, the
margins of a spread always show the same strip of wall, and the clutter is
placed to show there: along the top, down the outer margins and either side
of the spine, along the foot. The last 0.75in is under the ground strip or
off the page, and only carries the runs round to the top.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
NW, NH = 4320, 2880         # px; 18in x 12in at 240 DPI: wider than a spread and taller than a page, so a spread shows no repeat
IN = 240                    # px per inch
FEATURE = 1680              # px (7in): the largest blotch of stain or grime
SS = 3                      # shapes are drawn at SS x and boxed down
SEED = 12
SHADE = 1.0
COLOURS, VIVID_COLOURS = 160, 40
DARKEST = 0.25              # nothing darker: DriveThruRPG's 240% TAC, and a background

rng = np.random.default_rng(SEED)
yy, xx = np.mgrid[0:NH, 0:NW].astype(np.float32)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def noise(beta, stretch=(1.0, 1.0), seed=None, feature=FEATURE):
    """Periodic 1/f^beta noise over the tile, mean 0 and sd 1. `stretch`
    (sx, sy) < 1 elongates it along that axis."""
    r = np.random.default_rng(seed)
    white = r.standard_normal((NH, NW), dtype=np.float32)
    fy = np.fft.fftfreq(NH)[:, None] * stretch[1]
    fx = np.fft.rfftfreq(NW)[None, :] * stretch[0]
    f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)
    f[0, 0] = 1.0
    out = np.fft.irfft2(np.fft.rfft2(white) / f ** beta, s=(NH, NW)).astype(np.float32)
    out -= out.mean()
    return out / out.std()


def gauss_full(m, sigma, dx=0.0, dy=0.0):
    """Gaussian blur of a tile-sized field, wrapped (circular)."""
    fy = np.fft.fftfreq(NH)[:, None].astype(np.float32)
    fx = np.fft.rfftfreq(NW)[None, :].astype(np.float32)
    H = np.exp(-2 * np.pi ** 2 * sigma ** 2 * (fx * fx + fy * fy)) * np.exp(-2j * np.pi * (fx * dx + fy * dy))
    return np.fft.irfft2(np.fft.rfft2(m) * H, s=(NH, NW)).astype(np.float32)


def lblur(a, sigma):
    """Gaussian blur of a small patch (zero outside it)."""
    if sigma <= 0:
        return a
    p = int(3 * sigma) + 1
    b = np.pad(a, p)
    h, w = b.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    H = np.exp(-2 * np.pi ** 2 * sigma ** 2 * (fx * fx + fy * fy))
    out = np.fft.irfft2(np.fft.rfft2(b) * H, s=(h, w))
    return out[p:-p, p:-p].astype(np.float32)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t, np.float32)
    if t.ndim == 2:
        t = t[..., None]
    return a + (b - a) * t


def wrapd(d, n):
    """Signed distance on a circle of length n."""
    return (d + n / 2) % n - n / 2


# ── drawing kit ──────────────────────────────────────────────────────────────
class Pen:
    """A w x h mask drawn at SS x and boxed down. With wrap, every shape is
    drawn again a period over wherever it crosses an edge."""

    def __init__(self, w, h, wrap=False, ss=SS):
        self.w, self.h, self.s, self.wrap = int(w), int(h), ss, wrap
        self.im = Image.new("L", (self.w * ss, self.h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def _offs(self, xs, ys):
        if not self.wrap:
            return [(0, 0)]
        ox = [0] + ([self.w] if min(xs) < 8 else []) + ([-self.w] if max(xs) > self.w - 8 else [])
        oy = [0] + ([self.h] if min(ys) < 8 else []) + ([-self.h] if max(ys) > self.h - 8 else [])
        return [(a, b) for a in ox for b in oy]

    def poly(self, pts, v=255):
        s = self.s
        for ox, oy in self._offs([p[0] for p in pts], [p[1] for p in pts]):
            self.d.polygon([((x + ox) * s, (y + oy) * s) for x, y in pts], fill=int(v))

    def line(self, pts, w, v=255, caps=True):
        s = self.s
        for ox, oy in self._offs([p[0] for p in pts], [p[1] for p in pts]):
            q = [((x + ox) * s, (y + oy) * s) for x, y in pts]
            self.d.line(q, fill=int(v), width=max(1, int(round(w * s))), joint="curve")
            if caps and w * s > 3:
                r = w * s / 2
                for (x, y) in (q[0], q[-1]):
                    self.d.ellipse((x - r, y - r, x + r, y + r), fill=int(v))

    def ellipse(self, cx, cy, rx, ry, v=255, width=0):
        s = self.s
        for ox, oy in self._offs([cx - rx, cx + rx], [cy - ry, cy + ry]):
            box = ((cx - rx + ox) * s, (cy - ry + oy) * s, (cx + rx + ox) * s, (cy + ry + oy) * s)
            if width:
                self.d.ellipse(box, outline=int(v), width=max(1, int(round(width * s))))
            else:
                self.d.ellipse(box, fill=int(v))

    def rect(self, x0, y0, x1, y1, r=0, v=255):
        s = self.s
        for ox, oy in self._offs([x0, x1], [y0, y1]):
            box = ((x0 + ox) * s, (y0 + oy) * s, (x1 + ox) * s - 1, (y1 + oy) * s - 1)
            if r > 0:
                self.d.rounded_rectangle(box, radius=r * s, fill=int(v))
            else:
                self.d.rectangle(box, fill=int(v))

    def get(self):
        return np.asarray(self.im.resize((self.w, self.h), Image.BOX), np.float32) / 255


def mask(w, h, fn, wrap=False, ss=SS):
    p = Pen(w, h, wrap, ss)
    fn(p)
    return p.get()


img = None                       # the wall, (NH, NW, 3) float32
VIVID = np.zeros((NH, NW), bool)  # where the palette's saturated colours go
DEFER = []                       # emissive sprites, laid after the light


class Sprite:
    """A thing drawn in its own patch at (gx, gy) on the tile: premultiplied
    colour P and coverage a, laid on the wall with wrap-around."""

    def __init__(self, gx, gy, w, h, wrap=False):
        self.gx, self.gy, self.w, self.h, self.wrap = int(round(gx)), int(round(gy)), int(w), int(h), wrap
        self.P = np.zeros((self.h, self.w, 3), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)
        self.v = np.zeros((self.h, self.w), np.float32)

    def ix(self):
        return np.ix_((np.arange(self.h) + self.gy) % NH, (np.arange(self.w) + self.gx) % NW)

    def tex(self, field):
        return field[self.ix()]

    def mask(self, fn):
        return mask(self.w, self.h, fn, self.wrap)

    def paint(self, m, c, vivid=False, alpha=1.0):
        m = np.clip(m * alpha, 0, 1)
        c = np.asarray(c, np.float32)
        if c.ndim == 1:
            c = np.broadcast_to(c, self.P.shape)
        self.P = self.P * (1 - m[..., None]) + c * m[..., None]
        self.a = self.a * (1 - m) + m
        self.v = np.maximum(self.v * (1 - m), m if vivid else 0)

    def shade(self, f):
        self.P *= np.asarray(f, np.float32)[..., None]


def place(sp, lift=(4, 5, 4.0, 0.35), defer=False):
    """Lay a sprite on the wall: first its shadow, cast down and to the right
    (`lift` = dx, dy, softness, strength), then the thing itself."""
    global img
    if defer:
        DEFER.append(sp)
        return
    ix = sp.ix()
    sub = img[ix]
    if lift:
        dx, dy, sg, st = lift
        sh = np.roll(sp.a, (int(dy), int(dx)), (0, 1))
        if sp.wrap:
            sh = lblur_wrap(sh, sg)
        else:
            sh = lblur(sh, sg)
        sub *= (1 - st * np.clip(sh, 0, 1) * (1 - sp.a))[..., None]
    sub = sub * (1 - sp.a[..., None]) + sp.P
    img[ix] = sub
    VIVID[ix] |= sp.v > 0.35


def lblur_wrap(a, sigma):
    h, w = a.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    H = np.exp(-2 * np.pi ** 2 * sigma ** 2 * (fx * fx + fy * fy))
    return np.fft.irfft2(np.fft.rfft2(a) * H, s=(h, w)).astype(np.float32)


def edges(m, b=2):
    """The lit (upper-left) and shaded (lower-right) rims of a mask."""
    lit = np.clip(m - np.roll(m, (b, b), (0, 1)), 0, 1)
    dark = np.clip(m - np.roll(m, (-b, -b), (0, 1)), 0, 1)
    return lit, dark


def bevel(sp, m, c, b=2, up=0.22, down=0.35, vivid=False, grain=None):
    """Paint a flat thing with a bevelled rim, lit from the upper left."""
    lit, dark = edges(m, b)
    c = np.asarray(c, np.float32)
    if c.ndim == 1:
        c = np.broadcast_to(c, sp.P.shape)
    f = 1 + up * lit - down * dark
    if grain is not None:
        f = f * grain
    sp.paint(m, c * f[..., None], vivid=vivid)


def offset(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def tube(sp, pts, w, col, sheen=0.3, vivid=False, dark=0.62):
    """A round thing along a path (conduit, cable): darker at its sides, a
    highlight along its upper-left, a shade along its lower-right."""
    m1 = sp.mask(lambda p: p.line(pts, w))
    m2 = sp.mask(lambda p: p.line(pts, w * 0.62))
    m3 = sp.mask(lambda p: p.line(pts, w * 0.28))
    prof = (m1 + m2 + m3) / 3
    hi = sp.mask(lambda p: p.line(offset(pts, -0.17 * w, -0.22 * w), max(1.0, w * 0.2))) * m1
    lo = sp.mask(lambda p: p.line(offset(pts, 0.2 * w, 0.26 * w), max(1.0, w * 0.3))) * m1
    col = np.asarray(col, np.float32)
    c = col * (dark + (1.08 - dark) * prof)[..., None]
    c = mix(c, np.minimum(col * 1.5 + 0.15, 0.95), hi * sheen)
    c = c * (1 - 0.28 * lo)[..., None]
    sp.paint(m1, c, vivid=vivid)
    return m1


def screw(sp, x, y, r=4.0, col=hexc("#9a9a94")):
    m = sp.mask(lambda p: p.ellipse(x, y, r, r))
    bevel(sp, m, col, b=1, up=0.35, down=0.45)
    a = rng.uniform(0, np.pi)
    s = sp.mask(lambda p: p.line([(x - r * 0.8 * math.cos(a), y - r * 0.8 * math.sin(a)),
                                  (x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a))], max(1.0, r * 0.3)))
    sp.paint(s * m, col * 0.55)


def rot(pts, cx, cy, a):
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def ell_pts(cx, cy, rx, ry, a0=0, a1=2 * np.pi, n=60, rot_a=0.0):
    ts = np.linspace(a0, a1, n)
    pts = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in ts]
    return rot(pts, cx, cy, rot_a) if rot_a else pts


# ── the light ────────────────────────────────────────────────────────────────
AMBER_M = np.array([1.10, 0.95, 0.74], np.float32)      # what a warm bulb does to a grey wall
TEAL_M = np.array([0.80, 1.00, 1.05], np.float32)       # an LED strip's teal
BLUE_M = np.array([0.80, 0.90, 1.08], np.float32)       # and its electric blue
lights = []      # (kind, geometry, colour multiplier, strength, reach)

# fields used by many things
mottle = noise(1.7, seed=SEED + 1)
fine = noise(0.6, seed=SEED + 2)
grain_h = noise(1.2, stretch=(0.05, 1.0), seed=SEED + 3, feature=600)    # along x: wood, brushed metal
grain_v = noise(1.2, stretch=(1.0, 0.05), seed=SEED + 4, feature=600)    # along y
speck = noise(0.2, seed=SEED + 5)

# ── 1. the wall ──────────────────────────────────────────────────────────────
print("wall", flush=True)
PLASTER = hexc("#bab7b0")
blot = noise(2.0, seed=SEED + 6)
trowel = noise(1.4, stretch=(0.35, 1.0), seed=SEED + 7, feature=900)
plaster = PLASTER * (1 + 0.035 * mottle + 0.018 * fine + 0.02 * trowel)[..., None]
plaster = mix(plaster, plaster * np.array([1.0, 0.97, 0.90]), np.clip(0.3 + 0.35 * blot, 0, 1) * 0.4)   # old paint, yellowed in patches

# brick: running bond under the plaster, shown where it has spalled
BW, BH, MJ = 288, 96, 7
row = (yy // BH).astype(np.int32)
bx = (xx + (row % 2) * (BW // 2)) % NW
col_ = (bx // BW).astype(np.int32)
bid = row * (NW // BW) + col_
lxb, lyb = bx % BW, yy % BH
nb = (NH // BH) * (NW // BW)
btone = rng.uniform(0.86, 1.08, nb)[bid]
bwarm = rng.uniform(-1, 1, nb)[bid]
brick_c = mix(hexc("#a07e6a"), hexc("#98887a"), (0.5 + 0.5 * bwarm))
brick = brick_c * (btone + 0.06 * fine + 0.05 * mottle)[..., None]
dmin = np.minimum.reduce([lxb, BW - lxb, lyb, BH - lyb])
bface = smooth(dmin, MJ / 2 - 1, MJ / 2 + 1.5)
mortar = hexc("#b4ac9e") * (0.92 + 0.05 * fine)[..., None]
brick = mix(mortar, brick * (1 + 0.08 * np.exp(-np.clip(dmin - MJ / 2, 0, None) / 5))[..., None] * 0.97, bface)
brick *= (1 - 0.06 * smooth(-np.minimum(BW - lxb, BH - lyb), -14, -2))[..., None]

# spalls: a few patches, kept to the plaster's weak spots
sp_n = noise(1.9, seed=SEED + 8, feature=1200)
sp_e = noise(1.5, seed=SEED + 9, feature=200)
spall = smooth(sp_n + 0.22 * sp_e, 2.05, 2.12)
img = mix(plaster, brick, spall)
sh = np.clip(gauss_full(1 - spall, 3.5, 5, 6), 0, 1) * spall          # the plaster's broken edge throws a shadow in
img *= (1 - 0.5 * sh)[..., None]
lip = np.clip(gauss_full(spall, 2.0, -3, -3) - spall, 0, 1)            # and is lit on the far side
img = mix(img, img * 1.10, lip)
ring = np.clip(gauss_full(spall, 10) - spall, 0, 1)                    # plaster loose round it, a little darker
img *= (1 - 0.10 * ring)[..., None]

# water from above: tide-marked stains and streaks, and grime
wet = noise(1.6, stretch=(0.6, 1.0), seed=SEED + 10)
tide = smooth(wet, 1.1, 1.5)
img = mix(img, img * np.array([0.95, 0.92, 0.84]), tide * 0.5)
img *= (1 - 0.05 * np.clip(np.abs(wet - 1.1) < 0.03, 0, 1))[..., None]
src = np.zeros((NH, NW), np.float32)
for _ in range(90):
    src[int(rng.uniform(0, NH)), int(rng.uniform(0, NW))] += rng.uniform(0.4, 1.0)
for y in (int(0.24 * IN) + 12, int(10.42 * IN) + 12):                 # under the conduit runs
    for x in rng.choice(NW, 26, replace=False):
        src[y, x] += rng.uniform(0.3, 1.0)
ky = np.where(yy > NH // 2, yy - NH, yy)
kx = np.where(xx > NW // 2, xx - NW, xx)
dk = np.where(ky >= 0, np.exp(-ky / 260.0), 0) * np.exp(-(kx / 4.0) ** 2)
streak = np.fft.irfft2(np.fft.rfft2(src) * np.fft.rfft2(dk), s=(NH, NW)).astype(np.float32)
streak = np.clip(streak / np.percentile(streak[streak > 1e-4], 99), 0, 1)
streak *= smooth(noise(1.0, stretch=(1.0, 0.15), seed=SEED + 11), -0.6, 0.8)
img = mix(img, img * np.array([0.90, 0.87, 0.80]), streak * 0.4)
grime = noise(1.4, seed=SEED + 12)
img *= (1 - 0.05 * smooth(grime, 0.0, 2.0) - 0.02 * smooth(speck, 1.6, 2.4))[..., None]
del brick, plaster, bid, bx, row, lxb, lyb, dmin, bface, mortar, brick_c, btone, bwarm, sh, lip, ring

# old screw holes and anchors, and the ghosts of things taken down
ghosts = [(3.0, 2.1, 1.1, 0.7), (11.9, 6.3, 0.7, 1.0), (15.2, 9.2, 1.4, 0.5), (8.9, 1.9, 0.5, 0.8), (1.9, 9.6, 0.9, 0.5)]
m = mask(NW, NH, lambda p: [p.rect(gx * IN, gy * IN, (gx + gw) * IN, (gy + gh) * IN, r=6) for gx, gy, gw, gh in ghosts], wrap=True, ss=1)
m = gauss_full(m, 3)
edge = np.abs(gauss_full(m, 6) - m)
img = mix(img, img * np.array([1.04, 1.04, 1.06]), m * 0.8)        # cleaner, paler where it hung
img *= (1 - 0.12 * np.clip(edge * 2, 0, 1))[..., None]             # and a grime line round it
holes = Pen(NW, NH, True, 2)
for _ in range(70):
    x, y, r = rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(2.0, 4.5)
    holes.ellipse(x, y, r, r)
H_ = holes.get()
img = mix(img, img * 0.62, H_)
img = mix(img, img * 1.08, np.clip(np.roll(H_, (2, 2), (0, 1)) - H_, 0, 1))
anchors, a_holes = Pen(NW, NH, True, 2), Pen(NW, NH, True, 2)
for _ in range(16):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    anchors.ellipse(x, y, 6, 6)
    a_holes.ellipse(x, y, 2.2, 2.2)
A_ = anchors.get()
img = mix(img, hexc("#b4a36a") * (0.9 + 0.1 * fine)[..., None], A_ * 0.8)     # a plastic wall plug, its screw gone
img = mix(img, img * 0.6, a_holes.get())
del H_, A_, holes, anchors, a_holes

# ── 2. what is written on it ─────────────────────────────────────────────────
print("chalk", flush=True)
GRID = [(c * 0.5, r * 0.5) for r in range(5) for c in range(3)]      # a glyph's stroke grid, 3 x 5 points in a 1 x 2 box


def make_glyph(r):
    """A made-up rune wired like a component: a stem, branches off it bent at
    45 degrees, every loose end a pad (a ring) or a via (a dot), and now and
    then a hook or a bar. Terminals and traces, not letters: no script has these."""
    prims = []
    c = r.choice([0.0, 0.5, 1.0])
    y0, y1 = (0.0, 2.0) if r.random() < 0.6 else (r.choice([0.0, 0.5]), r.choice([1.5, 2.0]))
    prims.append(("l", [(c, y0), (c, y1)]))
    ends = [(c, y0), (c, y1)]
    for _ in range(int(r.integers(1, 3))):
        yb = r.choice([0.5, 1.0, 1.5])
        side = 1 if c == 0.0 else -1 if c == 1.0 else r.choice([-1, 1])
        dx = 0.5 * side
        if r.random() < 0.5:     # out at 45 degrees, then straight down or up
            dy = 0.5 if yb < 1.25 else -0.5
            pts = [(c, yb), (c + dx, yb + dy), (c + dx, yb + 2 * dy)]
        else:                    # straight out, then bent
            pts = [(c, yb), (c + dx, yb), (c + 2 * dx if 0 <= c + 2 * dx <= 1 else c + dx, yb + r.choice([-0.5, 0.5]))]
        prims.append(("l", pts))
        ends.append(pts[-1])
    for e in ends:
        roll = r.random()
        if roll < 0.4:
            prims.append(("o", e, 0.16))
        elif roll < 0.6:
            prims.append(("d", e))
    if r.random() < 0.3:
        a0 = r.choice([0.0, np.pi])
        prims.append(("a", (c, 1.0), 0.4, a0 - 1.2, a0 + 1.2))
    if r.random() < 0.25:
        prims.append(("l", [(c - 0.25, 0.5 * r.integers(1, 4)), (c + 0.25, 0.5 * r.integers(1, 4))]))
    return prims


GLYPHS = [make_glyph(np.random.default_rng(SEED * 100 + i)) for i in range(28)]


def draw_glyph(pen, g, x, y, s, w, ang=0.0):
    """Glyph g with its top-left at (x, y), s px to the grid's unit, turned by ang about its centre."""
    cx, cy = x + 0.5 * s, y + 1.0 * s

    def T(p):
        px_, py_ = x + p[0] * s, y + p[1] * s
        return rot([(px_, py_)], cx, cy, ang)[0] if ang else (px_, py_)
    for pr in g:
        if pr[0] == "l":
            pen.line([T(p) for p in pr[1]], w)
        elif pr[0] == "o":
            c = T(pr[1])
            pen.ellipse(c[0], c[1], pr[2] * s, pr[2] * s, width=w)
        elif pr[0] == "a":
            (px_, py_), rr, a0, a1 = pr[1], pr[2], pr[3], pr[4]
            pts = [T((px_ + rr * math.cos(t), py_ + rr * math.sin(t))) for t in np.linspace(a0, a1, 16)]
            pen.line(pts, w)
        elif pr[0] == "d":
            c = T(pr[1])
            pen.ellipse(c[0], c[1], w * 0.9, w * 0.9)


def trace_out(pen, r, x, y, a, L, w):
    """A circuit trace from (x, y) heading a: straight, a 45-degree bend or two,
    a component on the way now and then, a pad or a via at the end."""
    pts = [(x, y)]
    for k in range(int(r.integers(1, 3))):
        seg = L * r.uniform(0.3, 0.6)
        x, y = x + seg * math.cos(a), y + seg * math.sin(a)
        pts.append((x, y))
        a += r.choice([-1, 1]) * np.pi / 4
    seg = L * r.uniform(0.25, 0.5)
    roll = r.random()
    if roll < 0.18:                                   # a resistor's zigzag on the last leg
        n = 6
        ux, uy = math.cos(a), math.sin(a)
        for i in range(1, n + 1):
            t = seg * i / (n + 1)
            o = (6 if i % 2 else -6) * w / 3
            pts.append((x + t * ux - o * uy, y + t * uy + o * ux))
        x, y = x + seg * ux, y + seg * uy
        pts.append((x, y))
        pen.line(pts, w)
    elif roll < 0.3:                                  # a capacitor: two plates across it
        x2, y2 = x + seg * 0.45 * math.cos(a), y + seg * 0.45 * math.sin(a)
        pts.append((x2, y2))
        pen.line(pts, w)
        nx, ny = -math.sin(a) * 9 * w / 3, math.cos(a) * 9 * w / 3
        x3, y3 = x2 + 5 * math.cos(a) * w / 3, y2 + 5 * math.sin(a) * w / 3
        pen.line([(x2 - nx, y2 - ny), (x2 + nx, y2 + ny)], w)
        pen.line([(x3 - nx, y3 - ny), (x3 + nx, y3 + ny)], w)
        x, y = x + seg * math.cos(a), y + seg * math.sin(a)
        pen.line([(x3, y3), (x, y)], w)
    else:
        x, y = x + seg * math.cos(a), y + seg * math.sin(a)
        pts.append((x, y))
        pen.line(pts, w)
    rr = r.uniform(2.2, 3.4) * w
    if r.random() < 0.5:
        pen.ellipse(x, y, rr, rr)
    else:
        pen.ellipse(x, y, rr, rr, width=w)


def sigil(pen, r, cx, cy, R, w):
    """A ritual diagram wired like a board: rings, a ring of glyphs, an
    inscribed star, a chip at the heart, traces running out to pads."""
    # rings, some broken
    for k, f in enumerate((1.0, 0.86, 0.36)):
        if r.random() < 0.35 and k < 2:
            a0 = r.uniform(0, 2 * np.pi)
            pen.line(ell_pts(cx, cy, R * f, R * f, a0, a0 + r.uniform(4.6, 5.9), 90), w)
        else:
            pen.ellipse(cx, cy, R * f, R * f, width=w)
    # glyphs between the outer rings
    gs = R * 0.07
    n = int(2 * np.pi * R * 0.93 / (gs * 1.9))
    for i in range(n):
        t = 2 * np.pi * i / n
        gx, gy = cx + R * 0.93 * math.cos(t), cy + R * 0.93 * math.sin(t)
        draw_glyph(pen, GLYPHS[r.integers(len(GLYPHS))], gx - 0.5 * gs, gy - gs, gs, max(1.5, w * 0.6), ang=t + np.pi / 2)
    # an inscribed star
    k, step = [(7, 2), (7, 3), (8, 3), (9, 2), (9, 4)][r.integers(5)]
    a0 = r.uniform(0, 2 * np.pi)
    vs = [(cx + R * 0.86 * math.cos(a0 + 2 * np.pi * i / k), cy + R * 0.86 * math.sin(a0 + 2 * np.pi * i / k)) for i in range(k)]
    order = [vs[(i * step) % k] for i in range(k + 1)]
    pen.line(order, w)
    for v in vs:
        pen.ellipse(v[0], v[1], w * 2.2, w * 2.2)
    # the chip at its heart, pins and all
    c = R * 0.17
    pen.line([(cx - c, cy - c), (cx + c, cy - c), (cx + c, cy + c), (cx - c, cy + c), (cx - c, cy - c)], w)
    for i in range(4):
        t = -c + (i + 0.5) * 2 * c / 4
        for sx in (-1, 1):
            pen.line([(cx + sx * c, cy + t), (cx + sx * (c + R * 0.07), cy + t)], max(1.5, w * 0.7))
            pen.line([(cx + t, cy + sx * c), (cx + t, cy + sx * (c + R * 0.07))], max(1.5, w * 0.7))
    pen.ellipse(cx - c * 0.6, cy - c * 0.6, w, w)
    # traces out from the outer ring
    for i in range(int(r.integers(7, 12))):
        t = r.uniform(0, 2 * np.pi)
        trace_out(pen, r, cx + R * math.cos(t), cy + R * math.sin(t), t, R * r.uniform(0.5, 1.0), w)
    # ticks round the outside
    for i in range(36):
        t = 2 * np.pi * i / 36
        L = R * (0.06 if i % 3 else 0.11)
        pen.line([(cx + R * math.cos(t), cy + R * math.sin(t)), (cx + (R + L) * math.cos(t), cy + (R + L) * math.sin(t))], max(1.5, w * 0.6))


def glyph_column(pen, r, x, y0, y1, s, w, horizontal=False):
    """A run of glyphs down (or along) the wall, a gap now and then."""
    t = y0
    while t < y1:
        if r.random() < 0.12:
            t += s * 1.5
            continue
        g = GLYPHS[r.integers(len(GLYPHS))]
        if horizontal:
            draw_glyph(pen, g, t, x, s, w)
            t += s * 1.55
        else:
            draw_glyph(pen, g, x, t, s, w)
            t += s * 2.5


def chalky(m, seed, strength=1.0):
    """Break a line mask up like chalk dragged over plaster."""
    g = noise(0.25, seed=seed, feature=400)
    return np.clip(m * (0.62 + 0.4 * smooth(g, -1.2, 1.2)) * strength, 0, 1)


# blackboard paint: two patches, scuffed thin at the edges
BOARD = hexc("#5c625c")
boards = [(1.25, 4.55, 4.6, 8.05), (14.15, 4.75, 16.45, 6.15)]
bm = mask(NW, NH, lambda p: [p.rect(a * IN, b * IN, c * IN, d * IN, r=4) for a, b, c, d in boards], wrap=True)
bm *= np.clip(0.88 + 0.3 * smooth(noise(1.0, seed=SEED + 13, feature=500), -1.5, 0.5), 0, 1)
bwash = smooth(noise(0.6, seed=SEED + 14, feature=300), -2.0, 1.5)
img = mix(img, BOARD * (0.93 + 0.08 * fine + 0.06 * bwash)[..., None], bm)
# old erased chalk on it: a grey haze
haze = gauss_full(bm * smooth(noise(1.3, seed=SEED + 15, feature=500), 0.0, 1.8), 12)
img = mix(img, img * 1.0 + 0.10, np.clip(haze * 0.6, 0, 1) * bm)

r = np.random.default_rng(SEED + 20)
white_p, char_p, rust_p = Pen(NW, NH, True, 2), Pen(NW, NH, True, 2), Pen(NW, NH, True, 2)
sigil(white_p, r, 2.92 * IN, 6.3 * IN, 1.18 * IN, 4.5)
glyph_column(white_p, r, 1.45 * IN, 4.75 * IN, 7.9 * IN, 15, 3.2)
glyph_column(white_p, r, 4.3 * IN, 4.75 * IN, 7.9 * IN, 15, 3.2)
glyph_column(white_p, r, 4.95 * IN, 14.35 * IN, 16.3 * IN, 18, 3.4, horizontal=True)
glyph_column(white_p, r, 5.6 * IN, 14.35 * IN, 16.3 * IN, 14, 3.0, horizontal=True)
sigil(char_p, r, 2.35 * IN, 1.95 * IN, 0.72 * IN, 3.8)
sigil(char_p, r, 10.75 * IN, 7.45 * IN, 1.05 * IN, 4.0)
sigil(char_p, r, 2.25 * IN, 9.45 * IN, 0.62 * IN, 3.6)
sigil(rust_p, r, 6.45 * IN, 2.35 * IN, 0.95 * IN, 4.4)
sigil(rust_p, r, 11.55 * IN, 2.7 * IN, 1.0 * IN, 4.4)
sigil(rust_p, r, 15.2 * IN, 8.95 * IN, 0.55 * IN, 3.6)
glyph_column(char_p, r, 0.47 * IN, 1.0 * IN, 10.0 * IN, 13, 2.8)          # the left margin
glyph_column(char_p, r, 16.72 * IN, 0.9 * IN, 10.0 * IN, 13, 2.8)         # the right margin
glyph_column(rust_p, r, 8.48 * IN, 1.0 * IN, 9.8 * IN, 12, 2.6)           # either side of the spine
glyph_column(char_p, r, 9.2 * IN, 5.2 * IN, 9.9 * IN, 12, 2.6)
glyph_column(rust_p, r, 0.75 * IN, 0.6 * IN, 17.0 * IN, 11, 2.4, horizontal=True)      # along the top, under the conduit
glyph_column(char_p, r, 10.12 * IN, 0.3 * IN, 17.0 * IN, 12, 2.4, horizontal=True)      # and along the foot
# chalked arrows and tally marks, a measuring line
for _ in range(20):
    x, y = rng.uniform(0, NW), rng.uniform(0, NH)
    n = int(rng.integers(3, 7))
    for i in range(n):
        char_p.line([(x + i * 9, y), (x + i * 9 + 2, y + 34)], 2.6)
    if n == 5 or rng.random() < 0.3:
        char_p.line([(x - 6, y + 26), (x + n * 9, y + 6)], 2.6)
W_ = chalky(white_p.get(), SEED + 21)
C_ = chalky(char_p.get(), SEED + 22, 0.9)
R_ = chalky(rust_p.get(), SEED + 23)
del white_p, char_p, rust_p
CHALK = hexc("#e2ded4")
img = mix(img, img + 0.06, np.clip(gauss_full(W_, 7) * 0.5, 0, 1))               # the smear round chalk
img = mix(img, CHALK * (0.94 + 0.05 * fine)[..., None], W_ * 0.85)
img = mix(img, img * 0.9, np.clip(gauss_full(C_, 6) * 0.4, 0, 1))
img = mix(img, hexc("#5a5650"), C_ * 0.72)
RUSTCH = hexc("#a8582c")
img = mix(img, img * np.array([1.0, 0.92, 0.84]), np.clip(gauss_full(R_, 6) * 0.5, 0, 1))
img = mix(img, RUSTCH * (0.95 + 0.06 * fine)[..., None], R_ * 0.72)
VIVID |= R_ > 0.35
del W_, C_, R_, haze, bm, bwash


# ── 3. fixed to it ───────────────────────────────────────────────────────────
STEEL = hexc("#a9aaa5")
GALV = hexc("#b0b1ab")
IRON = hexc("#55524e")
WOOD = hexc("#97826a")
BLACK = hexc("#46443f")


def shelf(x0, x1, y, depth=26):
    """A plank on two iron brackets; y is its top."""
    w, h = int(x1 - x0) + 40, depth + 90
    sp = Sprite(x0 - 20, y - 10, w, h)
    # brackets under it
    for bxx in (34, w - 52):
        m = sp.mask(lambda p: p.rect(bxx, 10 + depth, bxx + 14, 10 + depth + 74, r=2))
        brace = sp.mask(lambda p: p.line([(bxx + 7, 10 + depth + 62), (bxx + 7 + (46 if bxx < w / 2 else -46), 10 + depth + 4)], 6))
        bevel(sp, np.clip(m + brace, 0, 1), IRON, b=2, up=0.3, down=0.3)
        screw(sp, bxx + 7, 10 + depth + 56, 3.2, IRON * 1.3)
    plank = sp.mask(lambda p: p.rect(20, 10, w - 20, 10 + depth, r=2))
    g = (1 + 0.06 * sp.tex(grain_h) + 0.03 * sp.tex(fine))
    face = WOOD * g[..., None]
    t = np.arange(h, dtype=np.float32)[:, None]
    face = face * (1 + 0.16 * smooth(-t, -16, -10) - 0.18 * smooth(t, 10 + depth - 6, 10 + depth))[..., None]   # top edge lit, underside dark
    sp.paint(plank, face)
    place(sp, (5, 9, 6.0, 0.45))
    return y


def jar(x, ybase, w, h, content, fill=0.7, lid=hexc("#6e6a62"), kind="liquid"):
    """A glass jar standing on a shelf at ybase: contents, glass, a lid, a highlight."""
    W_, H_ = int(w + 16), int(h + 24)
    sp = Sprite(x - 8, ybase - h - 16, W_, H_)
    x0, y0, x1, y1 = 8, 16 + h * 0.08, 8 + w, 16 + h
    body = sp.mask(lambda p: p.rect(x0, y0, x1, y1, r=w * 0.18))
    sp.paint(body, hexc("#c4cfc6"), alpha=0.32)                                      # the glass, seen through
    lvl = y1 - (y1 - y0) * fill
    cont = sp.mask(lambda p: p.rect(x0 + 3, lvl, x1 - 3, y1 - 3, r=w * 0.14))
    xs = np.arange(W_, dtype=np.float32)[None, :]
    roundness = 0.78 + 0.3 * np.sin(np.clip((xs - x0) / w, 0, 1) * np.pi)
    if kind == "liquid":
        c = np.asarray(content, np.float32) * roundness[..., None]
        sp.paint(cont, c * np.ones((H_, 1, 1), np.float32), vivid=True)
        sp.paint(cont * sp.mask(lambda p: p.rect(x0 + 3, lvl, x1 - 3, lvl + 3)), np.minimum(np.asarray(content) * 1.35, 1))
    else:                                                  # specimens, herbs, bolts: lumps
        sp.paint(cont, np.asarray(content, np.float32) * 0.8 * roundness[..., None] * np.ones((H_, 1, 1), np.float32))
        lumps = Pen(W_, H_)
        rr = np.random.default_rng(int(x))
        for _ in range(int(w * h / 90)):
            px_, py_ = rr.uniform(x0 + 4, x1 - 4), rr.uniform(lvl, y1 - 4)
            lumps.ellipse(px_, py_, rr.uniform(2, 6), rr.uniform(2, 5))
        lm = lumps.get() * cont
        sp.paint(lm, np.asarray(content, np.float32) * 1.15 * roundness[..., None] * np.ones((H_, 1, 1), np.float32))
        sp.paint(np.clip(np.roll(lm, (2, 2), (0, 1)) - lm, 0, 1) * cont, np.asarray(content, np.float32) * 0.6)
    edge = np.clip(body - lblur(body, 1.6) * 0.0 - sp.mask(lambda p: p.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, r=w * 0.16)), 0, 1)
    sp.paint(edge, hexc("#7e8a84"), alpha=0.7)
    hl = sp.mask(lambda p: p.rect(x0 + w * 0.16, y0 + h * 0.12, x0 + w * 0.16 + max(3, w * 0.09), y1 - h * 0.15, r=2))
    sp.paint(hl, hexc("#eef2ee"), alpha=0.75)
    if lid is not None:
        lm_ = sp.mask(lambda p: p.rect(x0 - 1, 16 - 4, x1 + 1, y0 + 4, r=3))
        bevel(sp, lm_, np.asarray(lid) * (1 + 0.08 * sp.tex(grain_h))[..., None], b=2, up=0.3, down=0.3)
    place(sp, (5, 4, 4.0, 0.35))


def vial_rack(x, ybase, n, cols):
    w = n * 26 + 20
    sp = Sprite(x, ybase - 140, w, 150)
    for i in range(n):
        cx = 16 + i * 26
        top = 30 + (i * 7) % 18
        body = sp.mask(lambda p: p.rect(cx - 7, top, cx + 7, 136, r=7))
        sp.paint(body, hexc("#c8d2cc"), alpha=0.32)
        lvl = top + 30 + ((i * 13) % 40)
        liq = sp.mask(lambda p: p.rect(cx - 5, lvl, cx + 5, 133, r=5))
        sp.paint(liq, cols[i % len(cols)], vivid=True)
        sp.paint(sp.mask(lambda p: p.rect(cx - 4, top + 4, cx - 1, 126)), hexc("#eef2ee"), alpha=0.6)
        cork = sp.mask(lambda p: p.rect(cx - 6, top - 12, cx + 6, top + 4, r=2))
        bevel(sp, cork, hexc("#a88a64"), b=2)
    rack = sp.mask(lambda p: p.rect(2, 94, w - 2, 110, r=2))
    bevel(sp, rack, WOOD * 0.92, b=2)
    rack2 = sp.mask(lambda p: [p.rect(2, 110, 10, 148), p.rect(w - 10, 110, w - 2, 148)])
    bevel(sp, rack2, WOOD * 0.85, b=2)
    place(sp, (5, 4, 4.0, 0.35))


def candle(x, ybase, w, h, wax=hexc("#d6ccb2"), lit_=True):
    sp = Sprite(x - w, ybase - h - 70, w * 3, h + 80)
    cx = w * 1.5
    top = 70
    body = sp.mask(lambda p: p.rect(cx - w / 2, top, cx + w / 2, top + h + 4, r=3))
    xs = np.arange(sp.w, dtype=np.float32)[None, :]
    rnd = 0.78 + 0.3 * np.sin(np.clip((xs - (cx - w / 2)) / w, 0, 1) * np.pi)
    sp.paint(body, wax * rnd[..., None] * np.ones((sp.h, 1, 1), np.float32))
    rr = np.random.default_rng(int(x * 3 + h))
    drips = Pen(sp.w, sp.h)
    for _ in range(int(rr.integers(2, 5))):
        dx = rr.uniform(-w / 2 + 3, w / 2 - 3)
        L = rr.uniform(8, h * 0.6)
        drips.line([(cx + dx, top + 2), (cx + dx, top + L)], rr.uniform(3, 6))
        drips.ellipse(cx + dx, top + L, 3.5, 4)
    dm = drips.get()
    sp.paint(dm, wax * 1.06 * rnd[..., None] * np.ones((sp.h, 1, 1), np.float32))
    sp.paint(np.clip(np.roll(dm, (0, 2), (0, 1)) - dm, 0, 1) * body, wax * 0.75)
    rim = sp.mask(lambda p: p.ellipse(cx, top + 1, w / 2, 3.5))
    sp.paint(rim, wax * 1.1)
    wick = sp.mask(lambda p: p.line([(cx, top), (cx + 1, top - 9)], 2.2))
    sp.paint(wick, hexc("#4a443c"))
    dish = sp.mask(lambda p: p.ellipse(cx, top + h + 4, w * 0.95, 5))
    bevel(sp, dish, hexc("#8c857a"), b=1)
    place(sp, (5, 4, 4.0, 0.3))
    if lit_:
        f = Sprite(x - w, ybase - h - 70, w * 3, h + 80)
        out = lblur(f.mask(lambda p: p.ellipse(cx, top - 24, 6.5, 17)), 1.0)
        core = lblur(f.mask(lambda p: p.ellipse(cx, top - 21, 3.2, 9)), 0.8)
        f.paint(out, hexc("#f0a850"), vivid=True)
        f.paint(core, hexc("#fff4d0"), vivid=True)
        f.paint(f.mask(lambda p: p.ellipse(cx, top - 13, 2.4, 3.5)), hexc("#8098c8"), vivid=True, alpha=0.5)
        place(f, None, defer=True)
        lights.append(("pt", (x + cx - w, ybase - h - 30), AMBER_M, 0.4, 0.4 * IN))


def skull(x, ybase, s=1.0):
    """A skull on a shelf, three-quarter front, shaded from the upper left."""
    W_, H_ = int(130 * s), int(140 * s)
    sp = Sprite(x, ybase - H_, W_, H_)
    cx = W_ / 2
    BONE = hexc("#cdc2a6")
    head = sp.mask(lambda p: p.ellipse(cx, 52 * s, 52 * s, 50 * s))
    jaw = sp.mask(lambda p: p.rect(cx - 33 * s, 70 * s, cx + 33 * s, 128 * s, r=16 * s))
    cheek = sp.mask(lambda p: p.ellipse(cx, 84 * s, 46 * s, 24 * s))
    m = np.clip(head + jaw + cheek, 0, 1)
    ys, xs = np.mgrid[0:H_, 0:W_].astype(np.float32)
    lightf = 1.08 - 0.32 * np.clip(((xs - cx + 20 * s) ** 2 + (ys - 40 * s) ** 2) / (70 * s) ** 2, 0, 1.4)
    sp.paint(m, BONE * (lightf * (1 + 0.04 * sp.tex(fine)))[..., None])
    sock = sp.mask(lambda p: [p.ellipse(cx - 20 * s, 66 * s, 15 * s, 13 * s), p.ellipse(cx + 20 * s, 66 * s, 15 * s, 13 * s)])
    sp.paint(lblur(sock, 1.5 * s), hexc("#4c463e"))
    sp.paint(np.clip(np.roll(sock, (int(3 * s), int(3 * s)), (0, 1)) - sock, 0, 1), BONE * 0.7)
    nose = sp.mask(lambda p: p.poly([(cx, 76 * s), (cx - 8 * s, 96 * s), (cx + 8 * s, 96 * s)]))
    sp.paint(lblur(nose, 1.0), hexc("#544c42"))
    teeth = sp.mask(lambda p: p.rect(cx - 24 * s, 104 * s, cx + 24 * s, 120 * s, r=4 * s))
    sp.paint(teeth, BONE * 0.95)
    for i in range(7):
        tx = cx - 21 * s + i * 7 * s
        sp.paint(sp.mask(lambda p: p.line([(tx, 104 * s), (tx, 120 * s)], 1.6)), hexc("#6a604e"))
    sp.paint(sp.mask(lambda p: p.line([(cx - 24 * s, 112 * s), (cx + 24 * s, 112 * s)], 1.6)), hexc("#6a604e"))
    crack = sp.mask(lambda p: p.line([(cx + 10 * s, 6 * s), (cx + 16 * s, 18 * s), (cx + 12 * s, 28 * s), (cx + 20 * s, 40 * s)], 1.5))
    sp.paint(crack, hexc("#7a6e58"))
    place(sp, (6, 4, 5.0, 0.4))


def fresnel(cx, cy, R, holder=True):
    """A fresnel lens: stepped glass rings, a little green, in a black ring."""
    sp = Sprite(cx - R - 8, cy - R - 8, 2 * R + 16, 2 * R + 16)
    c = R + 8
    ys, xs = np.mgrid[0:sp.h, 0:sp.w].astype(np.float32)
    d = np.hypot(xs - c, ys - c)
    disc = sp.mask(lambda p: p.ellipse(c, c, R, R))
    rings = (d / (R / 9.5)) % 1.0
    ang = np.arctan2(ys - c, xs - c)
    glint = 0.5 + 0.5 * np.cos(ang + 2.4)
    col = hexc("#b6c4be") * (0.86 + 0.16 * rings * glint + 0.04 * sp.tex(fine))[..., None]
    col = mix(col, hexc("#8a9894"), (rings > 0.86) * 0.6)
    sp.paint(disc, col, alpha=0.85)
    hl = sp.mask(lambda p: p.line(ell_pts(c, c, R * 0.7, R * 0.7, 3.4, 4.2, 12), max(2, R * 0.06)))
    sp.paint(hl, hexc("#f0f4f2"), alpha=0.7)
    if holder:
        ring = sp.mask(lambda p: p.ellipse(c, c, R + 4, R + 4, width=8))
        bevel(sp, ring, BLACK * 1.05, b=2, up=0.45, down=0.3)
        for t in (0.6, 2.7, 4.8):
            screw(sp, c + (R + 0) * math.cos(t), c + (R + 0) * math.sin(t), 2.6, STEEL * 0.9)
    place(sp, (6, 5, 5.0, 0.38))


def junction_box(cx, cy, s=110, kind="blank", col=GALV):
    """A steel box on the wall: a cover, its screws; or a switch, or an outlet."""
    w, h = (s, s) if kind == "blank" else (int(s * 0.62), s)
    sp = Sprite(cx - w / 2 - 6, cy - h / 2 - 6, w + 12, h + 12)
    m = sp.mask(lambda p: p.rect(6, 6, 6 + w, 6 + h, r=5))
    g = 1 + 0.05 * sp.tex(grain_h) + 0.03 * sp.tex(fine)
    bevel(sp, m, col, b=3, up=0.25, down=0.4, grain=g)
    inner = sp.mask(lambda p: p.rect(13, 13, w - 1, h - 1, r=3))
    lit, dark = edges(inner, 2)
    sp.shade(1 + 0.12 * dark - 0.14 * lit)
    if kind == "blank":
        for (x, y) in ((18, 18), (w - 6, h - 6)):
            screw(sp, x, y, 4.2)
    elif kind == "switch":
        tog = sp.mask(lambda p: p.rect(6 + w / 2 - 6, 6 + h / 2 - 22, 6 + w / 2 + 6, 6 + h / 2 + 4, r=4))
        bevel(sp, tog, hexc("#d8d2c4"), b=2, up=0.2, down=0.45)
        slot = sp.mask(lambda p: p.rect(6 + w / 2 - 9, 6 + h / 2 - 4, 6 + w / 2 + 9, 6 + h / 2 + 8, r=2))
        sp.paint(slot, col * 0.55)
        screw(sp, 6 + w / 2, 16, 3.4)
        screw(sp, 6 + w / 2, h - 4, 3.4)
    else:                    # a duplex outlet
        for oy in (h * 0.3, h * 0.7):
            face = sp.mask(lambda p: p.ellipse(6 + w / 2, 6 + oy, w * 0.3, h * 0.16))
            bevel(sp, face, hexc("#d0cabc"), b=2, up=0.2, down=0.35)
            sl = sp.mask(lambda p: [p.rect(6 + w / 2 - 9, 6 + oy - 8, 6 + w / 2 - 6, 6 + oy + 2),
                                     p.rect(6 + w / 2 + 6, 6 + oy - 8, 6 + w / 2 + 9, 6 + oy + 2),
                                     p.ellipse(6 + w / 2, 6 + oy + 8, 3, 3)])
            sp.paint(sl, hexc("#4a4640"))
        screw(sp, 6 + w / 2, 6 + h / 2, 3.4)
    place(sp, (4, 5, 4.0, 0.4))


def strap(sp, x, y, d, horizontal=True, col=GALV):
    """A one-hole conduit strap over a tube of diameter d at (x, y) in the sprite."""
    if horizontal:
        band = sp.mask(lambda p: p.rect(x - 7, y - d / 2 - 3, x + 7, y + d / 2 + 3, r=3))
        foot = sp.mask(lambda p: p.rect(x - 9, y - d / 2 - 15, x + 9, y - d / 2 - 1, r=3))
        bevel(sp, np.clip(band + foot, 0, 1), col * 1.02, b=2, up=0.3, down=0.35)
        screw(sp, x, y - d / 2 - 8, 3.2)
    else:
        band = sp.mask(lambda p: p.rect(x - d / 2 - 3, y - 7, x + d / 2 + 3, y + 7, r=3))
        foot = sp.mask(lambda p: p.rect(x + d / 2 + 1, y - 9, x + d / 2 + 15, y + 9, r=3))
        bevel(sp, np.clip(band + foot, 0, 1), col * 1.02, b=2, up=0.3, down=0.35)
        screw(sp, x + d / 2 + 8, y, 3.2)


def conduit_h(y, d=22, x0=None, x1=None, col=GALV, step=330, phase=0):
    """A run of conduit across the wall (the whole width, wrapped, if no ends)."""
    full = x0 is None
    if full:
        sp = Sprite(0, y - 40, NW, 80, wrap=True)
        pts = [(-20, 40), (NW + 20, 40)]
        xs = range(phase, NW, step)
    else:
        sp = Sprite(x0 - 10, y - 40, x1 - x0 + 20, 80)
        pts = [(10, 40), (x1 - x0 + 10, 40)]
        xs = range(phase + 40, int(x1 - x0) - 20, step)
    m = tube(sp, pts, d, col * (1 + 0.04 * sp.tex(grain_h))[..., None], sheen=0.45, dark=0.68)
    for x in xs:                                    # couplings every so often, straps between
        if (x // step) % 3 == 0:
            cm = sp.mask(lambda p: p.rect(x + 60, 40 - d / 2 - 2, x + 84, 40 + d / 2 + 2, r=2))
            bevel(sp, cm, col * 1.03, b=2, up=0.3, down=0.3)
        strap(sp, x + (0 if full else 10), 40, d, True, col)
    place(sp, (4, 6, 4.0, 0.4))


def conduit_v(x, d=22, y0=None, y1=None, col=GALV, step=330, phase=0):
    full = y0 is None
    if full:
        sp = Sprite(x - 40, 0, 80, NH, wrap=True)
        pts = [(40, -20), (40, NH + 20)]
        ys = range(phase, NH, step)
    else:
        sp = Sprite(x - 40, y0 - 10, 80, y1 - y0 + 20)
        pts = [(40, 10), (40, y1 - y0 + 10)]
        ys = range(phase + 40, int(y1 - y0) - 20, step)
    tube(sp, pts, d, col * (1 + 0.04 * sp.tex(grain_v))[..., None], sheen=0.45, dark=0.68)
    for yv in ys:
        if (yv // step) % 3 == 1:
            cm = sp.mask(lambda p: p.rect(40 - d / 2 - 2, yv + 60, 40 + d / 2 + 2, yv + 84, r=2))
            bevel(sp, cm, col * 1.03, b=2, up=0.3, down=0.3)
        strap(sp, 40, yv + (0 if full else 10), d, False, col)
    place(sp, (5, 4, 4.0, 0.4))


def cable_run(pts, w, col, staples=0, wrap=False, gx=0, gy=0, sw=None, sh_=None, lift=(5, 7, 5.0, 0.3), vivid=False):
    """A cable along a path; with staples, held to the wall by them."""
    if sw is None:
        xs_, ys_ = [p[0] for p in pts], [p[1] for p in pts]
        gx, gy = min(xs_) - 30, min(ys_) - 30
        sw, sh_ = max(xs_) - gx + 30, max(ys_) - gy + 30
        pts = [(x - gx, y - gy) for x, y in pts]
    sp = Sprite(gx, gy, sw, sh_, wrap=wrap)
    tube(sp, pts, w, col, sheen=0.35, vivid=vivid)
    if staples:
        # along the path, every `staples` px
        P_ = np.array(pts, float)
        seg = np.hypot(*np.diff(P_, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        for t in np.arange(staples / 2, cum[-1], staples):
            i = min(np.searchsorted(cum, t) - 1, len(seg) - 1)
            f = (t - cum[i]) / max(seg[i], 1e-6)
            x, y = P_[i] + f * (P_[i + 1] - P_[i])
            dx, dy = (P_[i + 1] - P_[i]) / max(seg[i], 1e-6)
            nx, ny = -dy, dx
            a = (x - nx * (w / 2 + 3) - dx * 3, y - ny * (w / 2 + 3) - dy * 3)
            b = (x + nx * (w / 2 + 3) - dx * 3, y + ny * (w / 2 + 3) - dy * 3)
            m = sp.mask(lambda p: p.line([a, b], 3.2))
            bevel(sp, m, hexc("#c8c8c2"), b=1, up=0.3, down=0.4)
    place(sp, lift)
    return sp


def caged_bulb(cx, cy, R=34, wall=True, cord_from=None):
    """A bulb in a wire cage: a cast base on the wall (or a socket on a cord),
    the bulb lit warm, the cage's bars over it."""
    if cord_from is not None:
        cable_run([cord_from, (cx + 2, (cord_from[1] + cy) / 2), (cx, cy - R - 30)], 9, BLACK, lift=(9, 12, 6.0, 0.25))
        so = Sprite(cx - 20, cy - R - 40, 40, 34)
        m = so.mask(lambda p: p.rect(6, 4, 34, 32, r=4))
        bevel(so, m, hexc("#6a6660") * (1 + 0.06 * so.tex(grain_v))[..., None], b=3, up=0.35, down=0.35)
        place(so, (8, 10, 5.0, 0.3))
    else:
        base = Sprite(cx - R - 22, cy - R - 22, 2 * R + 44, 2 * R + 44)
        c = R + 22
        m = base.mask(lambda p: p.ellipse(c, c, R + 18, R + 18))
        bevel(base, m, hexc("#7c7870") * (1 + 0.05 * base.tex(fine))[..., None], b=4, up=0.3, down=0.4)
        for t in (0.8, 2.9, 5.0):
            screw(base, c + (R + 11) * math.cos(t), c + (R + 11) * math.sin(t), 3.2)
        place(base, (6, 7, 6.0, 0.45))
    # the bulb (lit: laid after the light)
    b = Sprite(cx - R - 14, cy - R - 14, 2 * R + 28, 2 * R + 28)
    c = R + 14
    ys, xs = np.mgrid[0:b.h, 0:b.w].astype(np.float32)
    d = np.hypot((xs - c) / R, (ys - c) / (R * 1.12))
    glass = b.mask(lambda p: p.ellipse(c, c, R, R * 1.12))
    gcol = mix(hexc("#fff0c4"), hexc("#e49a4e"), smooth(d, 0.2, 1.0))
    b.paint(glass, gcol, vivid=True)
    fil = b.mask(lambda p: p.line([(c - 10, c + 10), (c - 7, c - 2), (c - 3, c + 4), (c, c - 4), (c + 3, c + 4), (c + 7, c - 2), (c + 10, c + 10)], 1.8))
    b.paint(fil, hexc("#fffbe8"), vivid=True)
    # the cage: a ring and bars, dark wire lit on its upper side
    cage = b.mask(lambda p: [p.ellipse(c, c, R + 7, R * 1.12 + 7, width=3.2)]
                  + [p.line([(c + (R + 6) * math.sin(t), c - (R * 1.12 + 6) * math.cos(t) * 1.0), (c + (R + 6) * math.sin(t), c + (R * 1.12 + 6) * math.cos(t))], 2.8) for t in (-1.0, -0.35, 0.35, 1.0)]
                  + [p.line([(c - R - 6, c), (c + R + 6, c)], 2.8)])
    wl, wd = edges(cage, 1)
    b.paint(cage, IRON * (1 + 0.5 * wl - 0.2 * wd)[..., None])
    place(b, None, defer=True)
    lights.append(("pt", (cx, cy), AMBER_M, 0.62, 1.55 * IN))


def led(x0, y0, x1, y1, colm=TEAL_M, emit=(hexc("#e0fbff"), hexc("#68cbd6")), reach=0.9 * IN, strength=0.5, side=None):
    """An LED strip in an aluminium channel, its diffuser lit; it washes the wall."""
    horiz = abs(x1 - x0) > abs(y1 - y0)
    if horiz:
        sp = Sprite(x0 - 10, y0 - 14, x1 - x0 + 20, 28)
        ch = sp.mask(lambda p: p.rect(10, 4, x1 - x0 + 10, 24, r=2))
        dif = sp.mask(lambda p: p.rect(12, 10, x1 - x0 + 8, 18, r=2))
        prof = smooth(np.abs(np.arange(sp.h, dtype=np.float32)[:, None] - 14), 4, 0) * np.ones((1, sp.w), np.float32)
    else:
        sp = Sprite(x0 - 14, y0 - 10, 28, y1 - y0 + 20)
        ch = sp.mask(lambda p: p.rect(4, 10, 24, y1 - y0 + 10, r=2))
        dif = sp.mask(lambda p: p.rect(10, 12, 18, y1 - y0 + 8, r=2))
        prof = smooth(np.abs(np.arange(sp.w, dtype=np.float32)[None, :] - 14), 4, 0) * np.ones((sp.h, 1), np.float32)
    g = sp.tex(grain_h if horiz else grain_v)
    bevel(sp, ch, hexc("#bfc2c0") * (1 + 0.05 * g)[..., None], b=2, up=0.35, down=0.4)
    place(sp, (3, 4, 3.0, 0.35))
    e = Sprite(sp.gx, sp.gy, sp.w, sp.h)
    e.paint(dif, mix(np.broadcast_to(emit[1], e.P.shape), np.broadcast_to(emit[0], e.P.shape), prof), vivid=True)
    # its little SMD beads
    beads = e.mask(lambda p: [p.rect(t - 3, 11, t + 3, 17) if horiz else p.rect(11, t - 3, 17, t + 3)
                              for t in range(18, int(max(x1 - x0, y1 - y0)), 24)])
    e.paint(beads * dif, hexc("#ffffff"), vivid=True, alpha=0.8)
    place(e, None, defer=True)
    lights.append(("seg", (x0, y0, x1, y1, side), colm, strength, reach))


def hook(sp, x, y, s=1.0):
    m = sp.mask(lambda p: p.line(ell_pts(x, y + 6 * s, 6 * s, 7 * s, -0.3, np.pi + 0.6, 14), 3.2 * s))
    m2 = sp.mask(lambda p: p.ellipse(x - 6 * s, y - 2 * s, 4 * s, 4 * s))
    bevel(sp, np.clip(m + m2, 0, 1), STEEL * 0.85, b=1, up=0.4, down=0.4)


def droop(x0, y0, x1, y1, sag, n=0):
    """Points on a cable hung from (x0, y0) to (x1, y1), sagging `sag` px at its middle."""
    n = n or max(12, int(abs(x1 - x0) / 20))
    t = np.linspace(0, 1, n)
    return [(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s + sag * 4 * s * (1 - s)) for s in t]


def bundle(x0, x1, y, sag, cables, herbs=0, seed=0):
    """Cables hung between hooks, tied together here and there; with herbs
    hung off them to dry."""
    r = np.random.default_rng(SEED * 7 + seed)
    pad = 60 + (230 if herbs else 0)
    gx, gy = x0 - 40, y - 40
    sw, sh_ = int(x1 - x0 + 80), int(sag + 70 + pad)
    sp = Sprite(gx, gy, sw, sh_)
    hook(sp, 40, 34)
    hook(sp, sw - 40, 34)
    paths = []
    for k, (col, w) in enumerate(cables):
        s_ = sag * (0.84 + 0.1 * k) + r.uniform(-6, 6)
        pts = droop(40, 40 + k * 3, sw - 40, 40 + k * 3, s_)
        paths.append(pts)
        tube(sp, pts, w, col, sheen=0.35, vivid=k == 1 and col[0] > col[2] + 0.15)
    for t in np.linspace(0.15, 0.85, 4)[1:-1] if len(cables) > 1 else []:      # zip ties
        i = int(t * (len(paths[0]) - 1))
        xs_ = [p[i][0] for p in paths]
        ys_ = [p[i][1] for p in paths]
        m = sp.mask(lambda p: p.line([(np.mean(xs_) - 1, min(ys_) - 8), (np.mean(xs_) + 1, max(ys_) + 8)], 4))
        bevel(sp, m, hexc("#3e3c38"), b=1, up=0.5, down=0.2)
    place(sp, (8, 12, 7.0, 0.3))
    if herbs:
        main = paths[0]
        n_ = len(main)
        for i in range(herbs):
            t = (i + 0.7) / (herbs + 0.4)
            j = int(t * (n_ - 1))
            hx, hy = main[j][0] + gx, main[j][1] + gy + 4
            herb_bunch(hx, hy, r)


HERB_COLS = [hexc("#8a9070"), hexc("#7e7468"), hexc("#9a7a52"), hexc("#86788c"), hexc("#a39a6a")]


def herb_bunch(x, y, r):
    """A bunch of herbs hung head down to dry: a string, a tie, the stems, the leaves."""
    L = r.uniform(110, 190)
    s_len = r.uniform(18, 46)
    sp = Sprite(x - 80, y - 10, 160, int(L + s_len + 50))
    cx, top = 80, 10
    string = sp.mask(lambda p: p.line([(cx, top), (cx + r.uniform(-3, 3), top + s_len)], 2))
    sp.paint(string, hexc("#b8aa88"))
    ty = top + s_len
    col = HERB_COLS[r.integers(len(HERB_COLS))]
    stems = Pen(sp.w, sp.h)
    leaves = Pen(sp.w, sp.h)
    heads = Pen(sp.w, sp.h)
    n = int(r.integers(9, 16))
    flower = r.random() < 0.4
    for k in range(n):
        a = np.pi / 2 + r.normal(0, 0.13)
        l = L * r.uniform(0.5, 1.0)
        bend = r.normal(0, 0.15)
        pts = []
        for s in np.linspace(0, 1, 10):
            aa = a + bend * s
            pts.append((cx + (k - n / 2) * 0.8 + s * l * math.cos(aa), ty + 6 + s * l * math.sin(aa)))
        stems.line(pts, 1.6)
        for s in np.linspace(0.35, 1.0, int(r.integers(3, 7))):
            px_, py_ = pts[min(9, int(s * 9))]
            for side in (-1, 1):
                if r.random() < 0.25:
                    continue
                la = np.pi / 2 + side * r.uniform(0.2, 0.75) + r.normal(0, 0.2)
                ll, lw = r.uniform(10, 20), r.uniform(2.5, 4.5)
                leaf = [(px_, py_), (px_ + ll * 0.5 * math.cos(la) - lw * math.sin(la), py_ + ll * 0.5 * math.sin(la) + lw * math.cos(la)),
                        (px_ + ll * math.cos(la), py_ + ll * math.sin(la)),
                        (px_ + ll * 0.5 * math.cos(la) + lw * math.sin(la), py_ + ll * 0.5 * math.sin(la) - lw * math.cos(la))]
                leaves.poly(leaf)
        if flower:
            ex, ey = pts[-1]
            for j in range(6):
                heads.ellipse(ex + r.normal(0, 3), ey - j * 5, 3.5, 3.0)
    lm = leaves.get()
    sm = stems.get()
    lit, dark = edges(lm, 1)
    tone = (0.92 + 0.12 * sp.tex(fine))
    sp.paint(sm, col * 0.8)
    sp.paint(lm, col * (tone * (1 + 0.2 * lit - 0.3 * dark))[..., None])
    if flower:
        hm = heads.get()
        sp.paint(hm, hexc("#8e7a9a") * (1 + 0.2 * edges(hm, 1)[0])[..., None], vivid=True)
    tie = sp.mask(lambda p: p.rect(cx - 10, ty, cx + 10, ty + 9, r=3))
    bevel(sp, tie, hexc("#a8885a"), b=1)
    place(sp, (8, 12, 6.0, 0.28))


def coil(hx, hy, col, loops=7, rx=82, ry=118, plug=True, seed=0, vivid=False):
    """An extension lead coiled and hung from a hook, its plug hanging below."""
    r = np.random.default_rng(SEED * 13 + seed)
    W_, H_ = int(2 * rx + 120), int(2 * ry + 230)
    sp = Sprite(hx - W_ / 2, hy - 30, W_, H_)
    cx, top = W_ / 2, 30
    hook(sp, cx, top - 8, 1.4)
    for k in range(loops):
        rxk, ryk = rx * r.uniform(0.88, 1.06), ry * r.uniform(0.92, 1.04)
        tilt = r.normal(0, 0.06)
        pts = ell_pts(cx + r.normal(0, 4), top + ryk, rxk, ryk, -np.pi / 2, 3 * np.pi / 2, 90, rot_a=tilt)
        pts = rot(pts, cx, top, tilt)
        tube(sp, pts, 11, col, sheen=0.35, vivid=vivid)
    if plug:
        y0 = top + 2 * ry - 10
        tail = [(cx + rx * 0.4, y0), (cx + rx * 0.55, y0 + 60), (cx + rx * 0.45, y0 + 120)]
        tube(sp, tail, 11, col, sheen=0.35, vivid=vivid)
        pb = sp.mask(lambda p: p.rect(tail[-1][0] - 16, tail[-1][1], tail[-1][0] + 16, tail[-1][1] + 44, r=6))
        bevel(sp, pb, col * 0.9, b=3, up=0.3, down=0.4, vivid=vivid)
        prong = sp.mask(lambda p: [p.rect(tail[-1][0] - 9, tail[-1][1] + 44, tail[-1][0] - 5, tail[-1][1] + 62),
                                   p.rect(tail[-1][0] + 5, tail[-1][1] + 44, tail[-1][0] + 9, tail[-1][1] + 62)])
        bevel(sp, prong, hexc("#c8b070"), b=1)
    # a tie round the coil
    tie = sp.mask(lambda p: p.rect(cx - rx - 6, top + ry - 8, cx - rx + 18, top + ry + 8, r=3))
    bevel(sp, tie, hexc("#3e3c38"), b=1)
    place(sp, (9, 12, 7.0, 0.32))


def swatch_book(px_, py_, n=14, L=170, w=26):
    """A lamp-gel swatch book, pinned at its rivet and fanned out down the wall."""
    GELS = ["#e8a040", "#e0c070", "#d87858", "#c85868", "#c870a0", "#9a78b8", "#6a82c0", "#4aa0c8",
            "#58b8b0", "#78b070", "#b8c060", "#d86040", "#b04848", "#f0d8a0", "#a0b8d8", "#c89060"]
    sp = Sprite(px_ - L - 30, py_ - 30, 2 * L + 60, L + 70)
    cx, cy = L + 30, 30
    angs = np.linspace(-0.62, 0.48, n)
    for k, a in enumerate(angs):
        pts = rot([(cx - w / 2, cy - 10), (cx + w / 2, cy - 10), (cx + w / 2, cy + L), (cx - w / 2, cy + L)], cx, cy, a)
        m = sp.mask(lambda p: p.poly(pts))
        gel = hexc(GELS[(k * 5) % len(GELS)])
        sp.paint(m, gel * (0.97 + 0.04 * (1 - np.arange(sp.h, dtype=np.float32) / sp.h))[:, None, None] * np.ones((1, sp.w, 1), np.float32), vivid=True)
        lab = rot([(cx - w / 2, cy + L - 34), (cx + w / 2, cy + L - 34), (cx + w / 2, cy + L), (cx - w / 2, cy + L)], cx, cy, a)
        lm = sp.mask(lambda p: p.poly(lab))
        sp.paint(lm, hexc("#e6e2d8"))
        sq = rot([(cx - 6, cy + L - 26), (cx + 7, cy + L - 26)], cx, cy, a)
        sq2 = rot([(cx - 7, cy + L - 16), (cx + 4, cy + L - 16)], cx, cy, a)
        sp.paint(sp.mask(lambda p: [p.line(sq, 1.6), p.line(sq2, 1.6)]), hexc("#7a766e"))
        edge = np.clip(m - np.roll(m, (1, 2), (0, 1)), 0, 1)
        sp.paint(edge, gel * 0.7, vivid=True)
    rv = sp.mask(lambda p: p.ellipse(cx, cy, 7, 7))
    bevel(sp, rv, hexc("#c0c0b8"), b=1, up=0.4, down=0.4)
    pin = sp.mask(lambda p: p.ellipse(cx, cy - 2, 10, 10))
    bevel(sp, pin, hexc("#b84a36"), b=2, up=0.4, down=0.4, vivid=True)
    place(sp, (5, 7, 5.0, 0.35))


def frame_schematic(x0, y0, w, h):
    """A framed drawing: a wiring diagram on the left running into a summoning
    circle on the right, on old paper, behind a moulded frame."""
    w, h = int(w), int(h)
    sp = Sprite(x0, y0, w, h)
    fw = 28
    outer = sp.mask(lambda p: p.rect(0, 0, w, h, r=3))
    paper = sp.mask(lambda p: p.rect(fw, fw, w - fw, h - fw))
    g = 1 + 0.12 * sp.tex(grain_h) * 0.5 + 0.1 * sp.tex(grain_v) * 0.5
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dfr = np.minimum.reduce([xs, w - xs, ys, h - ys])
    mould = 1 + 0.25 * np.cos(np.clip(dfr / fw, 0, 1) * np.pi * 1.5) * 0.5
    bevel(sp, outer, hexc("#7c5e42") * (g * mould)[..., None], b=3, up=0.3, down=0.4)
    inner_sh = np.clip(paper - np.roll(paper, (6, 6), (0, 1)), 0, 1)
    PAPER = hexc("#d6ccb2")
    foxing = smooth(sp.tex(blot), 0.6, 1.6)
    pc = PAPER * (1 - 0.08 * foxing - 0.03 * sp.tex(fine) - 0.06 * smooth(np.minimum.reduce([xs - fw, w - fw - xs, ys - fw, h - fw - ys]), 30, 0))[..., None]
    sp.paint(paper, pc)
    sp.shade(1 - 0.3 * lblur(inner_sh, 2))
    ink = Pen(w, h)
    r = np.random.default_rng(SEED + 40)
    # the circle, right of centre
    ccx, ccy, R = w * 0.64, h * 0.52, min(w, h) * 0.27
    sigil(ink, r, ccx, ccy, R, 2.2)
    # the wiring diagram, left: bus lines, components, joined into the circle's traces
    lx0, lx1 = fw + 26, ccx - R - 14
    for k in range(6):
        yv = fw + 40 + k * (h - 2 * fw - 80) / 5
        pts = [(lx0, yv), (lx0 + (lx1 - lx0) * r.uniform(0.3, 0.6), yv)]
        ang = math.atan2(ccy - yv, ccx - lx1)
        pts.append((lx1, yv + (ccy - yv) * 0.25))
        pts.append((ccx - R * math.cos(ang), ccy - R * math.sin(ang) * 0.9))
        ink.line(pts, 2.0)
        mx = lx0 + (lx1 - lx0) * r.uniform(0.1, 0.25)
        kind = k % 3
        if kind == 0:     # resistor
            zz = [(mx + i * 5, yv + (6 if i % 2 else -6)) for i in range(7)]
            ink.line([(mx - 4, yv)] + zz + [(mx + 34, yv)], 2.0)
        elif kind == 1:   # a diode: a triangle and a bar
            ink.poly([(mx, yv - 8), (mx, yv + 8), (mx + 14, yv)], 255)
            ink.line([(mx + 15, yv - 9), (mx + 15, yv + 9)], 2.2)
        else:             # a coil
            ink.line([(mx + i * 1.0, yv - 7 * abs(math.sin(i * 0.25))) for i in range(40)], 2.0)
        ink.ellipse(lx0, yv, 4, 4)
    ink.line([(lx0, fw + 40), (lx0, h - fw - 40)], 2.2)             # the bus
    for k in range(3):                                               # ground symbols
        gx_ = lx0 + 30 + k * 40
        gy_ = h - fw - 26
        ink.line([(gx_, gy_ - 16), (gx_, gy_)], 2)
        for j, ww in enumerate((12, 8, 4)):
            ink.line([(gx_ - ww, gy_ + j * 4), (gx_ + ww, gy_ + j * 4)], 1.8)
    im_ = ink.get() * paper
    sp.paint(im_, hexc("#5a4c44"), alpha=0.85)
    # a few lines in red ink
    red = Pen(w, h)
    red.ellipse(ccx, ccy, R * 1.12, R * 1.12, width=2.4)
    draw_glyph(red, GLYPHS[3], fw + 30, fw + 14, 9, 1.8)
    draw_glyph(red, GLYPHS[7], fw + 50, fw + 14, 9, 1.8)
    sp.paint(red.get() * paper, hexc("#a24a30"), vivid=True, alpha=0.9)
    # glass glare across a corner
    glare = sp.mask(lambda p: p.poly([(fw, fw + h * 0.2), (fw + w * 0.25, fw), (fw + w * 0.32, fw), (fw, fw + h * 0.3)]))
    sp.paint(glare * paper, hexc("#f2f0ea"), alpha=0.28)
    place(sp, (6, 8, 6.0, 0.45))
    nail = Sprite(x0 + w / 2 - 40, y0 - 60, 80, 70)
    wire = nail.mask(lambda p: p.line([(6, 64), (40, 12), (74, 64)], 2))
    nail.paint(wire, STEEL * 0.8)
    nm = nail.mask(lambda p: p.ellipse(40, 10, 5, 5))
    bevel(nail, nm, STEEL, b=1)
    place(nail, (3, 4, 3.0, 0.3))


def pegboard(x0, y0, w, h):
    """A board of hardboard on battens, its holes in a grid, and the tools hung on it."""
    w, h = int(w), int(h)
    sp = Sprite(x0, y0, w, h)
    m = sp.mask(lambda p: p.rect(0, 0, w, h, r=2))
    PB = hexc("#a69882")
    tone = 1 + 0.035 * sp.tex(mottle) + 0.02 * sp.tex(fine) + 0.03 * sp.tex(grain_h)
    bevel(sp, m, PB * tone[..., None], b=3, up=0.25, down=0.4)
    holes = Pen(w, h)
    for yh in range(20, h - 10, 40):
        for xh in range(20, w - 10, 40):
            holes.ellipse(xh, yh, 4.2, 4.2)
    hm = holes.get()
    sp.paint(hm, PB * 0.52)
    sp.paint(np.clip(np.roll(hm, (2, 2), (0, 1)) - hm, 0, 1), PB * 1.12, alpha=0.6)
    for (xs_, ys_) in ((14, 14), (w - 14, 14), (14, h - 14), (w - 14, h - 14), (w // 2, 14), (w // 2, h - 14)):
        screw(sp, xs_, ys_, 4.0)
    place(sp, (6, 7, 6.0, 0.45))


def peg(x, y):
    sp = Sprite(x - 12, y - 12, 34, 30)
    m = sp.mask(lambda p: p.line([(12, 12), (24, 14), (28, 8)], 3.4))
    bevel(sp, m, STEEL * 0.9, b=1, up=0.4, down=0.4)
    place(sp, (3, 4, 2.0, 0.3))


def screwdriver(x, y, L, hcol, flat=True):
    """Hung handle up from a peg at (x, y)."""
    sp = Sprite(x - 20, y, 40, L + 10)
    hl = L * 0.42
    hm = sp.mask(lambda p: p.rect(8, 0, 32, hl, r=9))
    xs = np.arange(40, dtype=np.float32)[None, :]
    rnd = 0.7 + 0.42 * np.clip(np.sin(np.clip((xs - 8) / 24, 0, 1) * np.pi), 0, 1) ** 0.7
    sp.paint(hm, hcol * (rnd * np.ones((sp.h, 1), np.float32))[..., None], vivid=True)
    for k in range(3):
        g = sp.mask(lambda p: p.line([(14 + k * 6, 8), (14 + k * 6, hl - 10)], 1.8))
        sp.paint(g * hm, hcol * 0.62)
    hi = sp.mask(lambda p: p.rect(12, 4, 15, hl - 6, r=1))
    sp.paint(hi, np.minimum(hcol * 1.45 + 0.1, 1.0), alpha=0.6)
    tube(sp, [(20, hl), (20, L - 6)], 7, STEEL * 1.05, sheen=0.6)
    tip = sp.mask(lambda p: p.poly([(16, L - 8), (24, L - 8), (22 if flat else 20, L + 2), (18 if flat else 20, L + 2)]))
    sp.paint(tip, STEEL * 0.85)
    place(sp, (5, 6, 4.0, 0.38))


def pliers(x, y, L, gcol, cutters=False):
    """Hung jaws up by the joint."""
    sp = Sprite(x - 50, y - 40, 100, L + 50)
    cx, jy = 50, 40 + L * 0.26
    jaws = sp.mask(lambda p: p.poly([(cx - 9, jy), (cx - 3, 40 - (0 if cutters else 0)), (cx + 3, 40), (cx + 9, jy)]
                                    if not cutters else [(cx - 12, jy), (cx - 8, 52), (cx, 44), (cx + 8, 52), (cx + 12, jy)]))
    bevel(sp, jaws, STEEL * 0.78 * (1 + 0.05 * sp.tex(grain_v))[..., None], b=2, up=0.35, down=0.35)
    sp.paint(sp.mask(lambda p: p.line([(cx, 46), (cx, jy - 4)], 1.4)), STEEL * 0.45)
    for sgn in (-1, 1):
        hpts = [(cx + sgn * 6, jy + 6), (cx + sgn * 16, jy + L * 0.3), (cx + sgn * 22, 40 + L - 6)]
        tube(sp, hpts, 13, gcol, sheen=0.3, vivid=True)
        tube(sp, [(cx + sgn * 6, jy - 2), (cx + sgn * 9, jy + 14)], 9, STEEL * 0.8, sheen=0.5)
    jm = sp.mask(lambda p: p.ellipse(cx, jy, 10, 10))
    bevel(sp, jm, STEEL * 0.9, b=2, up=0.4, down=0.4)
    screw(sp, cx, jy, 4.0, STEEL * 0.9)
    place(sp, (5, 6, 4.0, 0.38))


def c_wrench(x, y, L):
    """An adjustable spanner, hung by the hole in its handle: a lighting tech's C-wrench."""
    sp = Sprite(x - 40, y - 12, 80, L + 70)
    cx = 40
    hm = sp.mask(lambda p: p.rect(cx - 9, 0, cx + 9, L, r=9))
    head = sp.mask(lambda p: p.ellipse(cx, L + 22, 30, 32))
    jaw = sp.mask(lambda p: p.rect(cx - 9, L + 26, cx + 9, L + 62))
    hole = sp.mask(lambda p: p.ellipse(cx, 14, 5, 5))
    m = np.clip(hm + head - jaw - hole, 0, 1)
    bevel(sp, m, hexc("#b4b4ae") * (1 + 0.06 * sp.tex(grain_v))[..., None], b=2, up=0.35, down=0.4)
    worm = sp.mask(lambda p: p.rect(cx + 12, L + 2, cx + 24, L + 22, r=3))
    sp.paint(worm, STEEL * 0.7)
    for k in range(5):
        sp.paint(sp.mask(lambda p: p.line([(cx + 12, L + 5 + k * 4), (cx + 24, L + 5 + k * 4)], 1.2)), STEEL * 0.5)
    tape = sp.mask(lambda p: p.rect(cx - 9, L * 0.45, cx + 9, L * 0.45 + 22))
    sp.paint(tape * m, hexc("#c06a34"), vivid=True)     # the owner's tape
    place(sp, (5, 6, 4.0, 0.4))


def hammer(x, y, L):
    sp = Sprite(x - 50, y - 6, 100, L + 20)
    cx = 50
    hm = sp.mask(lambda p: p.rect(cx - 8, 20, cx + 8, L, r=6))
    sp.paint(hm, WOOD * 1.05 * (1 + 0.08 * sp.tex(grain_v))[..., None])
    sp.shade(1 + 0.1 * edges(hm, 2)[0] - 0.2 * edges(hm, 2)[1])
    head = sp.mask(lambda p: p.poly([(cx - 40, 8), (cx + 26, 8), (cx + 38, 14), (cx + 26, 32), (cx - 40, 32)]))
    bevel(sp, head, hexc("#6e6c66") * (1 + 0.05 * sp.tex(grain_h))[..., None], b=3, up=0.3, down=0.4)
    place(sp, (6, 6, 4.0, 0.4))


def tape_rolls(x, y, cols):
    sp = Sprite(x - 40, y - 10, 80, 60 + 26 * len(cols))
    for k, c in enumerate(cols):
        cy = 46 + k * 22
        m = sp.mask(lambda p: p.ellipse(40, cy, 32, 30))
        hole_ = sp.mask(lambda p: p.ellipse(40, cy - 12, 17, 16))
        rr = np.clip(m - hole_, 0, 1)
        bevel(sp, rr, c, b=2, up=0.35, down=0.4, vivid=True)
        sp.paint(hole_ * m * 0 + np.clip(hole_ - sp.mask(lambda p: p.ellipse(40, cy - 12, 13, 12)), 0, 1), hexc("#c8bca0"))
    place(sp, (5, 6, 4.0, 0.38))


def multimeter(x, y):
    sp = Sprite(x - 50, y - 10, 100, 330)
    m = sp.mask(lambda p: p.rect(6, 10, 94, 170, r=12))
    bevel(sp, m, hexc("#c8a648") * (1 + 0.04 * sp.tex(fine))[..., None], b=4, up=0.3, down=0.4, vivid=True)
    face = sp.mask(lambda p: p.rect(16, 20, 84, 160, r=6))
    sp.paint(face, hexc("#5a5a56"))
    lcd = sp.mask(lambda p: p.rect(24, 28, 76, 58, r=2))
    sp.paint(lcd, hexc("#a8b49a"))
    for k in range(3):
        sp.paint(sp.mask(lambda p: p.rect(32 + k * 14, 36, 42 + k * 14, 50)), hexc("#5e6658"), alpha=0.7)
    dial = sp.mask(lambda p: p.ellipse(50, 104, 22, 22))
    bevel(sp, dial, hexc("#4e4e4a"), b=2, up=0.5, down=0.3)
    sp.paint(sp.mask(lambda p: p.line([(50, 104), (62, 88)], 3)), hexc("#d8d4c8"))
    for k, c in enumerate((hexc("#c0503c"), BLACK, BLACK)):
        jx = 28 + k * 22
        jm = sp.mask(lambda p: p.ellipse(jx, 146, 5, 5))
        sp.paint(jm, c * 1.1)
    tube(sp, [(28, 150), (22, 220), (34, 290), (30, 320)], 6, hexc("#b44a38"), sheen=0.3, vivid=True)
    tube(sp, [(50, 150), (58, 210), (52, 280), (60, 316)], 6, BLACK, sheen=0.3)
    place(sp, (6, 7, 5.0, 0.42))


def solder_spool(x, y):
    sp = Sprite(x - 40, y - 10, 80, 80)
    m = sp.mask(lambda p: p.ellipse(40, 42, 34, 34))
    bevel(sp, m, hexc("#4a4c58"), b=3, up=0.3, down=0.4)
    w_ = sp.mask(lambda p: p.ellipse(40, 42, 27, 27))
    ys, xs = np.mgrid[0:80, 0:80].astype(np.float32)
    rings = 0.85 + 0.25 * (np.hypot(xs - 40, ys - 42) % 3 < 1.5)
    sp.paint(w_, hexc("#b8b8b2") * rings[..., None])
    hub = sp.mask(lambda p: p.ellipse(40, 42, 10, 10))
    bevel(sp, hub, hexc("#5a5c66"), b=2)
    sp.paint(sp.mask(lambda p: p.ellipse(40, 42, 5, 5)), PB_HOLE)
    tube(sp, [(66, 46), (72, 60), (70, 76)], 2.4, hexc("#b8b8b2"), sheen=0.6)
    place(sp, (5, 6, 4.0, 0.38))


PB_HOLE = hexc("#5a4c3c")


def breaker_panel(x0, y0, w, h):
    """A panelboard: a steel cover, a dead-front with two columns of breakers,
    a main at the top, a directory card, taped toggles, a sigil chalked on it."""
    w, h = int(w), int(h)
    sp = Sprite(x0, y0, w, h)
    m = sp.mask(lambda p: p.rect(0, 0, w, h, r=6))
    g = 1 + 0.012 * sp.tex(grain_v) + 0.03 * sp.tex(mottle) + 0.02 * sp.tex(fine)
    bevel(sp, m, hexc("#acaea8") * g[..., None], b=5, up=0.25, down=0.4)
    inner = sp.mask(lambda p: p.rect(28, 28, w - 28, h - 28, r=4))
    lit, dark = edges(inner, 3)
    sp.shade(1 - 0.18 * lit + 0.12 * dark)
    # the opening in the dead-front and the breakers in it
    op = sp.mask(lambda p: p.rect(w * 0.2, 120, w * 0.8, h - 210, r=3))
    sp.paint(op, hexc("#8e908a"))
    lit, dark = edges(op, 3)
    sp.shade(1 - 0.35 * lit * 0 - 0.2 * lit + 0.0 * dark)
    r = np.random.default_rng(SEED + 50)
    main = sp.mask(lambda p: p.rect(w * 0.32, 70, w * 0.68, 112, r=3))
    bevel(sp, main, hexc("#4e4e4a"), b=2, up=0.4, down=0.3)
    mt = sp.mask(lambda p: p.rect(w * 0.42, 80, w * 0.58, 102, r=3))
    bevel(sp, mt, hexc("#3c3c38") * 1.2, b=2, up=0.6, down=0.3)
    n_rows = int((h - 210 - 130) / 46)
    bw = w * 0.6 / 2 - 6
    for c in range(2):
        for k in range(n_rows):
            bx0 = w * 0.2 + 4 + c * (bw + 4)
            by0 = 126 + k * 46
            bm = sp.mask(lambda p: p.rect(bx0, by0, bx0 + bw, by0 + 42, r=2))
            bevel(sp, bm, hexc("#74746e"), b=2, up=0.35, down=0.3)
            on = r.random() < 0.8
            tx = bx0 + (bw * 0.6 if c == 0 else bw * 0.14)
            slot = sp.mask(lambda p: p.rect(tx - 4, by0 + 10, tx + bw * 0.26 + 4, by0 + 32, r=2))
            sp.paint(slot, hexc("#55554f"))
            tg = sp.mask(lambda p: p.rect(tx + (bw * 0.13 if on else 0), by0 + 12, tx + bw * 0.13 + (bw * 0.13 if on else 0), by0 + 30, r=2))
            bevel(sp, tg, hexc("#9a9a92"), b=1, up=0.5, down=0.4)
            lab = sp.mask(lambda p: p.rect(bx0 + (6 if c == 0 else bw * 0.52), by0 + 16, bx0 + (bw * 0.42 if c == 0 else bw - 6), by0 + 26))
            sp.paint(lab, hexc("#d4d0c4"), alpha=0.8)
            if r.random() < 0.18:      # a coloured tape flag on it
                tc = hexc(["#c8503c", "#d0a040", "#4a8ec0", "#5aa070"][r.integers(4)])
                tf = sp.mask(lambda p: p.rect(bx0 + bw * (0.05 if c == 0 else 0.5), by0 + 6, bx0 + bw * (0.45 if c == 0 else 0.92), by0 + 36))
                sp.paint(tf, tc, vivid=True, alpha=0.9)
    # the directory card, ruled, filled in with marks that are not words
    card = sp.mask(lambda p: p.rect(w * 0.2, h - 196, w * 0.8, h - 60, r=2))
    sp.paint(card, hexc("#d6d0c0") * (1 - 0.06 * smooth(sp.tex(blot), 0.5, 1.5))[..., None])
    ink = Pen(w, h)
    for k in range(9):
        yv = h - 186 + k * 14
        ink.line([(w * 0.21, yv), (w * 0.79, yv)], 0.9)
        x = w * 0.23
        while x < w * 0.74 and r.random() < 0.85:
            L = r.uniform(10, 40)
            pts = [(x + t, yv - 4 - 3 * math.sin(t * 0.7 + k)) for t in np.linspace(0, L, 8)]
            ink.line(pts, 1.4)
            x += L + r.uniform(8, 18)
    ink.line([(w * 0.5, h - 192), (w * 0.5, h - 62)], 0.9)
    sp.paint(ink.get() * card, hexc("#5e5850"), alpha=0.8)
    # screws, a latch, knockouts in the top
    for (xs_, ys_) in ((16, 16), (w - 16, 16), (16, h - 16), (w - 16, h - 16)):
        screw(sp, xs_, ys_, 5.0)
    lt = sp.mask(lambda p: p.rect(w - 22, h / 2 - 30, w - 10, h / 2 + 30, r=3))
    bevel(sp, lt, hexc("#8c8e88"), b=2)
    # a sigil chalked on the cover, half rubbed off
    ch = Pen(w, h)
    sigil(ch, r, w * 0.5, 0 + 50, 34, 2.4)
    draw_glyph(ch, GLYPHS[11], w * 0.08, h * 0.3, 16, 3)
    draw_glyph(ch, GLYPHS[19], w * 0.08, h * 0.45, 16, 3)
    draw_glyph(ch, GLYPHS[2], w * 0.86, h * 0.62, 16, 3)
    cm = ch.get() * smooth(sp.tex(blot) + 0.4 * sp.tex(fine), -0.8, 0.6)
    sp.paint(cm, hexc("#e2ded4"), alpha=0.8)
    # the warning sticker: a lightning flash in a triangle (a sign, not words)
    tri = sp.mask(lambda p: p.poly([(w * 0.5, h - 48), (w * 0.5 - 24, h - 10 - 0), (w * 0.5 + 24, h - 10)]))
    sp.paint(tri, hexc("#d4b048"), vivid=True)
    fl = sp.mask(lambda p: p.poly([(w * 0.5 + 3, h - 40), (w * 0.5 - 7, h - 24), (w * 0.5, h - 24), (w * 0.5 - 4, h - 14), (w * 0.5 + 7, h - 29), (w * 0.5, h - 29)]))
    sp.paint(fl, hexc("#4a4640"))
    place(sp, (7, 9, 7.0, 0.45))


# ── lay it all out ───────────────────────────────────────────────────────────
print("fixtures", flush=True)
I_ = IN
breaker_panel(13.5 * I_, 0.42 * I_, 2.2 * I_, 3.9 * I_)
pegboard(12.95 * I_, 6.45 * I_, 3.3 * I_, 3.35 * I_)
frame_schematic(5.25 * I_, 4.3 * I_, 2.2 * I_, 2.55 * I_)
shelf(1.15 * I_, 4.35 * I_, 3.38 * I_)
shelf(9.55 * I_, 12.5 * I_, 4.55 * I_)
shelf(5.1 * I_, 7.95 * I_, 9.72 * I_)

print("wiring", flush=True)
# conduit along the top and the foot, and down the left margin; drops into the panel
conduit_h(int(0.24 * IN), 24, phase=60)
conduit_h(int(10.42 * IN), 24, phase=200)
conduit_v(int(0.27 * IN), 22, phase=150)
for k, xd in enumerate((13.85, 14.25, 14.65)):
    conduit_v(int(xd * IN), 18, int(0.24 * IN), int(0.44 * IN) + 30, step=1000)
conduit_v(int(16.25 * IN), 16, int(0.24 * IN), int(0.95 * IN), step=1000)
# junction boxes on the runs, switches and outlets along the foot
for x in (2.25, 6.65, 9.35, 12.4, 17.6):
    junction_box(x * IN, 0.24 * IN, 100)
junction_box(0.27 * IN, 0.24 * IN, 104)                 # where the margin's run tees off the top one
junction_box(0.27 * IN, 10.42 * IN, 104)                # and meets the foot's
junction_box(0.27 * IN, 2.95 * IN, 96)
junction_box(0.27 * IN, 8.25 * IN, 96)
for x, kind in ((1.35, "outlet"), (3.6, "switch"), (4.9, "outlet"), (7.35, "switch"), (8.6, "outlet"),
                (10.15, "outlet"), (11.0, "switch"), (12.9, "outlet"), (15.85, "switch"), (16.45, "outlet")):
    junction_box(x * IN, 10.42 * IN, 128, kind)
# a stapled cable down the left of the spine, a bundle down the right margin
cable_run([(40, -20), (40, NH + 20)], 10, BLACK, staples=150, wrap=True, gx=8.33 * IN - 40, gy=0, sw=80, sh_=NH)
for k, (cc, xo) in enumerate(((BLACK, 0), (hexc("#8a8c88"), 13), (hexc("#a85a34"), 26))):
    cable_run([(40 + xo, -20), (40 + xo, NH + 20)], 11, cc, staples=0, wrap=True, gx=16.88 * IN - 40, gy=0, sw=110, sh_=NH, vivid=k == 2)
bt = Sprite(16.88 * IN - 40, 0, 110, NH, wrap=True)
for yv in range(80, NH, 260):
    m = bt.mask(lambda p: p.rect(30, yv, 86, yv + 6, r=2))
    bevel(bt, m, hexc("#3e3c38"), b=1, up=0.5)
    clip = bt.mask(lambda p: p.rect(86, yv - 8, 100, yv + 14, r=3))
    bevel(bt, clip, GALV, b=1)
place(bt, (3, 4, 3.0, 0.3))
# a cord from an outlet up to the bench light, another round to the shelf

print("lights", flush=True)
led(9.5 * IN, 0.66 * IN, 12.85 * IN, 0.66 * IN, TEAL_M, reach=0.6 * IN, strength=0.4)
led(9.75 * IN, 4.75 * IN, 12.3 * IN, 4.75 * IN, BLUE_M, emit=(hexc("#e4f0ff"), hexc("#6a9ae0")), reach=1.0 * IN, strength=0.42, side=1)
led(8.88 * IN, 0.95 * IN, 8.88 * IN, 9.95 * IN, TEAL_M, reach=0.42 * IN, strength=0.36)
led(0.62 * IN, 10.08 * IN, 3.2 * IN, 10.08 * IN, BLUE_M, emit=(hexc("#e4f0ff"), hexc("#6a9ae0")), reach=0.45 * IN, strength=0.36)
led(16.62 * IN, 9.0 * IN, 16.62 * IN, 10.2 * IN, TEAL_M, reach=0.38 * IN, strength=0.34)
caged_bulb(1.55 * IN, 0.95 * IN, 34)
caged_bulb(16.25 * IN, 0.95 * IN, 34)
caged_bulb(0.27 * IN, 5.6 * IN, 30)
caged_bulb(16.95 * IN, 7.4 * IN, 30)
caged_bulb(7.45 * IN, 1.45 * IN, 32, wall=False, cord_from=(7.45 * IN, 0.24 * IN + 12))
caged_bulb(4.2 * IN, 10.42 * IN, 28)

print("clutter", flush=True)
# shelf A: jars, the skull, candles, vials
y = 3.38 * IN
jar(1.3 * IN, y, 64, 92, hexc("#8a9a5a"), 0.75, kind="lumps")
jar(1.62 * IN, y, 52, 70, hexc("#a8582c"), 0.6)
skull(1.92 * IN, y, 0.85)
candle(2.55 * IN, y, 22, 74)
candle(2.72 * IN, y, 18, 46)
vial_rack(2.92 * IN, y, 5, [hexc("#4aa8b0"), hexc("#b8603a"), hexc("#7a8ac8"), hexc("#88b060"), hexc("#c89a48")])
jar(3.65 * IN, y, 70, 110, hexc("#c4b48c"), 0.8, kind="lumps", lid=hexc("#8a5a3a"))
# shelf B (lit from under by its strip): lenses, a jar, a candle, vials, a transformer
y = 4.55 * IN
fresnel(10.0 * IN, y - 76, 72)
fresnel(10.55 * IN, y - 56, 52)
jar(10.85 * IN, y, 56, 84, hexc("#4a98a8"), 0.55)
candle(11.25 * IN, y, 20, 58)
vial_rack(11.45 * IN, y, 3, [hexc("#c87a3a"), hexc("#6a5aa0"), hexc("#4aa8b0")])
tr = Sprite(11.98 * IN, y - 72, 90, 76)
m = tr.mask(lambda p: p.rect(8, 10, 82, 72, r=4))
bevel(tr, m, hexc("#6a6460"), b=3, up=0.3, down=0.4)
co = tr.mask(lambda p: p.rect(20, 20, 70, 62, r=8))
bevel(tr, co, hexc("#b0703c"), b=3, up=0.35, down=0.4, vivid=True)
for k in range(8):
    tr.paint(tr.mask(lambda p: p.line([(20, 24 + k * 5), (70, 24 + k * 5)], 1.3)) * co, hexc("#7a4a28"))
place(tr, (5, 4, 4.0, 0.35))
# shelf C, low: candles, a lens, a jar, a skull's worth of bones
y = 9.72 * IN
candle(5.35 * IN, y, 26, 96)
candle(5.55 * IN, y, 20, 62)
candle(5.72 * IN, y, 16, 38, lit_=False)
fresnel(6.25 * IN, y - 64, 60)
jar(6.75 * IN, y, 60, 96, hexc("#6a7a9a"), 0.5)
jar(7.15 * IN, y, 48, 64, hexc("#b88a4a"), 0.7, kind="lumps")
candle(7.6 * IN, y, 22, 70)

# the gel book under the strip, the lead coils, the pegboard's tools
swatch_book(10.05 * IN, 0.98 * IN)
coil(6.4 * IN, 7.3 * IN, hexc("#c07438"), loops=7, seed=1, vivid=True)
coil(12.15 * IN, 7.7 * IN, hexc("#4a6a8c"), loops=6, rx=70, ry=104, seed=2)
coil(3.5 * IN, 8.45 * IN, BLACK * 1.1, loops=5, rx=60, ry=86, plug=False, seed=3)
px0, py0 = 12.95 * IN, 6.45 * IN


def P(c, r_):
    return px0 + 20 + 40 * c, py0 + 20 + 40 * r_


for c in (1, 2, 3, 6, 8, 10, 12, 14, 15, 17):
    peg(*P(c, 1))
screwdriver(*P(1, 1), 250, hexc("#b05040"))
screwdriver(*P(2, 1), 220, hexc("#c0a050"), flat=False)
screwdriver(*P(3, 1), 190, hexc("#4c78a0"))
pliers(*P(6, 1), 220, hexc("#b05040"))
pliers(*P(8, 1), 200, hexc("#c8a850"), cutters=True)
c_wrench(*P(10, 1), 230)
hammer(*P(12, 1) if False else (P(12, 1)[0] + 20, P(12, 1)[1]), 260)
tape_rolls(*P(15, 1), [hexc("#4a4844"), hexc("#b05040"), hexc("#4a70a0"), hexc("#c8b050")])
multimeter(*P(17, 1))
for c in (1, 6, 10, 14, 17):
    peg(*P(c, 9))
screwdriver(*P(1, 9), 200, hexc("#5a9068"))
pliers(*P(6, 9), 190, hexc("#4a70a0"))
c_wrench(*P(10, 9), 170)
solder_spool(*P(14, 9))
tape_rolls(*P(17, 9), [hexc("#5a9068"), hexc("#dcdad2")])
coil(P(3, 12)[0] + 10, P(3, 12)[1], hexc("#8a8c88"), loops=4, rx=40, ry=58, plug=False, seed=4)

# cables hung between hooks along the top, one hung with herbs
print("cables", flush=True)
bundle(0.75 * IN, 3.05 * IN, 0.42 * IN, 0.45 * IN, [(BLACK, 11), (hexc("#8a8c88"), 9)], seed=1)
bundle(3.05 * IN, 6.0 * IN, 0.42 * IN, 0.38 * IN, [(hexc("#5a5048"), 10)], herbs=6, seed=2)
bundle(6.0 * IN, 9.4 * IN, 0.42 * IN, 0.62 * IN, [(BLACK, 12), (hexc("#c07438"), 11), (hexc("#4a6a8c"), 10)], seed=3)
bundle(12.95 * IN, 13.45 * IN, 0.42 * IN, 0.18 * IN, [(BLACK, 10)], seed=4)
bundle(15.7 * IN, 18.75 * IN, 0.42 * IN, 0.5 * IN, [(BLACK, 11), (hexc("#b84838"), 9)], seed=5)

# ── 6. the light ─────────────────────────────────────────────────────────────
print("light", flush=True)
acc = np.zeros((NH, NW, 3), np.float32)
wsum = np.zeros((NH, NW), np.float32)
for kind, geo, cm, st, reach in lights:
    if kind == "pt":
        dx = wrapd(xx - geo[0], NW)
        dy = wrapd(yy - geo[1], NH)
        d2 = (dx * dx + dy * dy) / (reach * reach)
    else:
        x0, y0, x1, y1, side = geo
        if abs(x1 - x0) >= abs(y1 - y0):
            dx = np.maximum(0, np.maximum(x0 - xx, xx - x1))
            dy = wrapd(yy - y0, NH)
            if side == 1:
                dy = np.where(dy < 0, dy * 4, dy)        # under a shelf: it lights downward
        else:
            dy = np.maximum(0, np.maximum(y0 - yy, yy - y1))
            dx = wrapd(xx - x0, NW)
        d2 = (dx * dx + dy * dy) / (reach * reach)
    f = st * np.exp(-d2 * 2.0) + st * 0.08 * np.exp(-d2 * 0.5)
    acc += f[..., None] * (cm - 1)
    wsum += f
img = img * (1 + acc) + np.clip(wsum, 0, 1)[..., None] * 0.05
del acc, wsum

# the emissive things, over the light
for sp in DEFER:
    place(sp, None)

# ── finish: no colour too dark to print, and the palette ─────────────────────
img = np.maximum(img, 0)
img = np.where(img < 2 * DARKEST, DARKEST + img * img / (4 * DARKEST), img)      # a soft toe: nothing under DARKEST
rgb = (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)
del img
pal = []
for sel, n in ((~VIVID, COLOURS - VIVID_COLOURS), (VIVID, VIVID_COLOURS)):
    px = rgb[sel][None]
    q = Image.fromarray(px, "RGB").quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal += q.getpalette()[:3 * n]
palimg = Image.new("P", (1, 1))
palimg.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
out = Image.fromarray(rgb, "RGB").quantize(palette=palimg, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-12.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-12.png  {NW}x{NH}  {NW / IN:.2f}x{NH / IN:.2f}in  vivid {VIVID.mean():.1%}  "
      f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
