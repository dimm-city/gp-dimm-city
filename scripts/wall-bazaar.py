"""Draw wall 13, the back wall of an open-air street market (`@page wall-13`), as images/wall-13.png.

    python3 scripts/wall-bazaar.py       (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the shadows and glows are circular
convolutions, the brick is laid on the tile's own grid, and every object is
a sprite stamped with wrap-around.

What it draws, back to front:
1. The old wall: lime plaster gone patchy and yellow, a faded green dado
   along its foot, spalled off here and there down to the brick (the
   broken edge lit, the brick under it in shade), cracked, streaked from
   above, grimy toward the street; a ghost sign of huge faded glyphs high up.
2. On the wall: posters and bills pasted over each other, torn, faded and
   peeling at a corner; glyph graffiti (fat outlined tags with drips, and
   marker scrawl); the scraps of older bills.
3. The fixtures: rails on brackets, pegboards, a conduit with its junction
   boxes, hand-painted signs (a painted board, chipped to the wood, its
   words in the city's own glyphs: no real script, no brands).
4. The goods, a different trade to every stall: strings of dried chillies
   and garlic braids and herbs, hanging baskets, pots, pans, kettles and
   ladles, kilim rugs and draped cloth and bolts, cable coils and bundles,
   circuit boards, fans, gears, valves and old screens, cages (one with a
   tenant), charm strings, lanterns; price tags on strings.
5. The foot of the wall: wooden and plastic crates stacked as counters,
   their slats stencilled, burlap sacks rolled open on heaps of spice,
   baskets of produce, buckets.
6. The stalls: poles lashed with rope, and over each a sagging canvas
   awning or tarp, faded stripes or plain, patched and stained, with a
   scalloped or plain valance, grommets, tears; ropes tying them off.
7. Strings of bare bulbs swagged between the poles, a few lit, and lanterns.
8. The Streetwarden's marks (the wall is the Streetwarden's page: the city's
   tracker, scout and beast-friend), drawn at the page's scale, not the
   wall's, so they read from across a spread, each kind made its own way
   and no two of a kind alike:
   - claw marks: three to five gouges raked together into the plaster,
     through the posters and into the faces of the crates;
   - muddy paw prints: the trails of four beasts over the wall and the
     crates, each its own foot and gait, the mud wearing off as it goes;
   - trail signs: a tracker's way-marks scratched into the plaster (arrows,
     counts of notches, pictographs: an eye, a den, a horned head, a track),
     not the city's script and not paint;
   - growth: new cracks, moss in every crack and along the broken edges of
     the plaster, creepers up the wall, down it, and round two poles.
   Those on the wall lie under what hangs in front of it, in its shadow.
Each layer throws a soft shadow down and to the right onto what is behind
it. It is then drawn back toward its mean (a background, not a picture) and
quantised to an exact palette: the wall's tones, and apart from them the
few saturated things (chillies, spice, boards, lit bulbs), which a median
cut over the whole tile would turn grey; and then the marks' own colours,
used only where a mark is. The marks have a random stream, a mean and a
palette apart from the wall's, so away from a mark the tile is, px for px,
the wall without them.

At DPI (300) the tile is 18in x 12in, wider than a spread
and taller than a page, so a spread shows no repeat. It is anchored to the
sheet (ALIGNED), so the stalls stand on the street on every page: the
awnings and bulbs along the top, the crates and sacks along the foot
(FLOOR); the last 0.75in of the tile is under the ground strip or off the
page, and fades back to the top.

Lengths are written in units of 1/240in (a px at 240 DPI, the DPI it was
first drawn at): the sprites and layers lay them down at S = DPI / 240 px to
the unit, so every length scales with DPI, and so does nothing else.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wall_fft import irfft2, rfft2  # noqa: E402  (numpy's real FFTs, spread over the cores)

ROOT = Path(__file__).resolve().parents[1]
DPI = 300                   # px per inch
S = DPI / 240               # px per unit: lengths are in units of 1/240in, laid down at S px each
NW, NH = 18 * 240, 12 * 240                 # units; 18in x 12in: wider than a spread and taller than a page, so a spread shows no repeat
PW, PH = round(18 * DPI), round(12 * DPI)   # px: the tile's size in inches x DPI
FLOOR = 2560                # units from the sheet's top to the ground strip (11.25in - 0.6in, rounded): the wall's foot
FEATURE = 1800 * S          # px (7.5in): the largest blotch of damp or grime
SS = 4                      # shapes are drawn at SS x and boxed down: anti-aliased
SEED = 13
CALM = 0.84                 # every tone is drawn this far back toward the tile's mean
SHADE = 1.03                # lifted a touch, toward the other walls
ACCENT_COLOURS = 40         # of 160: the saturated sliver (chillies, spice, boards, bulbs) gets its own
MARK_COLOURS = 64           # and the marks theirs, over and above the 160

rng = np.random.default_rng(SEED)
f32 = np.float32
LIGHT = np.array([-0.45, -0.62, 0.64])
LIGHT /= np.linalg.norm(LIGHT)

yy = (np.arange(PH, dtype=f32) / S)[:, None]     # every px's place on the tile, in units: a column and a row, which broadcast
xx = (np.arange(PW, dtype=f32) / S)[None, :]
iy_, ix_ = np.arange(PH), np.arange(PW)
ky = (np.where(iy_ > PH // 2, iy_ - PH, iy_) / S).astype(f32)[:, None]    # signed offsets round the torus, in units
kx = (np.where(ix_ > PW // 2, ix_ - PW, ix_) / S).astype(f32)[None, :]


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], f32) / 255


def noise(beta, stretch=(1.0, 1.0), seed=None, feature=FEATURE):
    """Periodic 1/f^beta noise in [0, 1] over the tile's px; `stretch` (sx, sy) > 1 elongates it along that axis."""
    def field(h, w, spec, cap):
        fy = np.fft.fftfreq(h)[:, None] * stretch[1]
        fx = np.fft.rfftfreq(w)[None, :] * stretch[0]
        f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / cap)
        return irfft2(spec / f ** beta, s=(h, w))
    spec, base = white_spectrum(seed)
    ref = field(NH, NW, base, feature / S)    # the field as a 240 DPI tile has it, scaled to [0, 1]
    ref -= ref.min()
    ref /= ref.max()
    if (PH, PW) == (NH, NW):
        return ref.astype(f32)
    out = field(PH, PW, spec, feature)        # and with the finer detail: given the same mean and spread
    out = ref.mean() + (out - out.mean()) * (ref.std() / out.std())
    return np.clip(out, 0, 1).astype(f32)


def white_spectrum(seed):
    """The spectra of white noise over the tile at px, and at 240 DPI. The
    frequencies a 240 DPI tile has (in cycles per tile, so per inch) come from
    the same draw at any DPI, so the damp, spalls and grain land where they
    did; the finer ones the extra px add are drawn fresh."""
    base = rfft2(np.random.default_rng(seed).standard_normal((NH, NW)))
    if (PH, PW) == (NH, NW):
        return base, base
    spec = rfft2(np.random.default_rng([seed if seed is not None else 0, DPI]).standard_normal((PH, PW)))
    k, k2 = NH // 2 - 1, NW // 2 - 1          # rows +-k and columns 0..k2: below the 240 DPI tile's Nyquist
    g = math.sqrt(PH * PW / (NH * NW))        # white noise's spectrum grows with the number of samples
    spec[:k + 1, :k2 + 1] = base[:k + 1, :k2 + 1] * g
    spec[PH - k:, :k2 + 1] = base[NH - k:, :k2 + 1] * g
    return spec, base


def circ_conv(a, kernel):
    return irfft2(rfft2(a) * rfft2(kernel), s=(PH, PW)).astype(f32)


def blur(m, sigma, dx=0, dy=0):
    """A wrapped gaussian blur of a tile-sized field; sigma and the offset in units."""
    g = np.exp(-(((kx - dx) ** 2 + (ky - dy) ** 2) / (2 * sigma * sigma)))
    return circ_conv(m, g / g.sum())


def shift(a, dy, dx):
    """np.roll by (dy, dx) px, which need not be whole: a fractional shift is
    the blend of the two whole ones either side of it."""
    out = 0
    y0, x0 = math.floor(dy), math.floor(dx)
    fy, fx = dy - y0, dx - x0
    for oy, wy in ((y0, 1 - fy), (y0 + 1, fy)):
        for ox, wx in ((x0, 1 - fx), (x0 + 1, fx)):
            if wy * wx > 1e-6:
                out = out + (wy * wx) * np.roll(a, (oy, ox), (0, 1))
    return np.asarray(out, f32)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    u = 3 - 2 * t
    t *= t
    t *= u
    return t


def mix(a, b, t):
    t = np.asarray(t, f32)
    if t.ndim == 2:
        t = t[..., None]
    d = np.subtract(b, a)          # a + (b - a) * t, in the one new buffer where its shape and type allow
    inplace = d.shape == np.broadcast_shapes(d.shape, t.shape) and np.result_type(d, t) == d.dtype
    d = np.multiply(d, t, out=d if inplace else None)
    d += a
    return d


def jag(a, b, rough, r, step=6):
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
            return [tuple(p) for p in pts]


# Global textures, sampled anywhere at a random offset: wood grain, mottle, weave.
print("textures", flush=True)
TEX = {
    "mott": noise(2.0, seed=SEED + 1),
    "fine": noise(1.0, seed=SEED + 2),
    "gh": noise(1.15, stretch=(0.05, 1.0), seed=SEED + 3),      # grain along x
    "gv": noise(1.15, stretch=(1.0, 0.05), seed=SEED + 4),      # grain along y
    "speck": noise(0.45, seed=SEED + 5),
}


def tex(name, Y, X, off):
    """A global texture at (Y, X), offset by off (all in units), read at every px."""
    iy = np.rint((np.asarray(Y) + off[0]) * S).astype(np.int64) % PH
    ix = np.rint((np.asarray(X) + off[1]) * S).astype(np.int64) % PW
    return TEX[name][iy, ix]


def toff(r):
    return int(r.integers(NH)), int(r.integers(NW))


# ── sprites: local RGBA patches, stamped onto the tile with wrap-around ─────────
class Spr:
    """A sprite w x h units: everything drawn on it is placed and sized in
    units, and laid down at S px to the unit. Its arrays are at px; w and h
    are its size in units, pw and ph in px."""

    def __init__(self, w, h, px=False):
        if px:
            self.pw, self.ph = int(w), int(h)
        else:
            self.pw, self.ph = int(math.ceil(w * S - 1e-6)), int(math.ceil(h * S - 1e-6))
        self.w, self.h = self.pw / S, self.ph / S
        self.rgb = np.zeros((self.ph, self.pw, 3), f32)
        self.a = np.zeros((self.ph, self.pw), f32)
        self.acc = np.zeros((self.ph, self.pw), bool)

    def grid(self, y0=0, x0=0, h=None, w=None):
        """Y, X: where each px (of the box at px y0, x0, h x w) is on the sprite, in units."""
        h = self.ph if h is None else h
        w = self.pw if w is None else w
        Y, X = np.mgrid[y0:y0 + h, x0:x0 + w].astype(f32)
        return Y / S, X / S

    def _box(self, xs, ys, pad):
        """The px box round px coordinates xs, ys."""
        x0 = max(0, int(math.floor(min(xs) - pad)))
        y0 = max(0, int(math.floor(min(ys) - pad)))
        x1 = min(self.pw, int(math.ceil(max(xs) + pad)) + 1)
        y1 = min(self.ph, int(math.ceil(max(ys) + pad)) + 1)
        return x0, y0, x1, y1

    def mpoly(self, polys):
        polys = [[(x * S, y * S) for x, y in poly] for poly in polys]
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        x0, y0, x1, y1 = self._box(xs, ys, 2)
        if x1 <= x0 or y1 <= y0:
            return None
        im = Image.new("L", ((x1 - x0) * SS, (y1 - y0) * SS), 0)
        d = ImageDraw.Draw(im)
        for poly in polys:
            d.polygon([((x - x0) * SS, (y - y0) * SS) for x, y in poly], fill=255)
        return y0, x0, np.asarray(im.resize((x1 - x0, y1 - y0), Image.BOX), f32) / 255

    def mlines(self, lines, width, caps=True):
        lines = [[(x * S, y * S) for x, y in ln] for ln in lines]
        width = width * S
        xs = [p[0] for ln in lines for p in ln]
        ys = [p[1] for ln in lines for p in ln]
        x0, y0, x1, y1 = self._box(xs, ys, width + 2)
        if x1 <= x0 or y1 <= y0:
            return None
        im = Image.new("L", ((x1 - x0) * SS, (y1 - y0) * SS), 0)
        d = ImageDraw.Draw(im)
        w = max(1, int(round(width * SS)))
        for ln in lines:
            pts = [((x - x0) * SS, (y - y0) * SS) for x, y in ln]
            if len(pts) > 1:
                d.line(pts, fill=255, width=w, joint="curve")
            if caps and width * SS > 3:
                for (px, py) in (pts[0], pts[-1]):
                    d.ellipse((px - w / 2, py - w / 2, px + w / 2, py + w / 2), fill=255)
        return y0, x0, np.asarray(im.resize((x1 - x0, y1 - y0), Image.BOX), f32) / 255

    def mell(self, cx, cy, rx, ry):
        cx, cy, rx, ry = cx * S, cy * S, rx * S, ry * S
        x0, y0, x1, y1 = self._box([cx - rx, cx + rx], [cy - ry, cy + ry], 2)
        if x1 <= x0 or y1 <= y0:
            return None
        Y, X = np.mgrid[y0:y1, x0:x1].astype(f32)
        d = np.sqrt(((X + 0.5 - cx) / rx) ** 2 + ((Y + 0.5 - cy) / ry) ** 2)
        return y0, x0, np.clip((1 - d) * min(rx, ry) + 0.5, 0, 1).astype(f32)

    def put(self, m, col, alpha=1.0, acc=False):
        """Paint `col` (a colour, an (h, w, 3) array, or fn(Y, X, m) -> colours, Y and X in units) through mask m."""
        if m is None:
            return
        y0, x0, mk = m
        h, w = mk.shape
        sl = (slice(y0, y0 + h), slice(x0, x0 + w))
        if callable(col):
            Y, X = self.grid(y0, x0, h, w)
            col = col(Y, X, mk)
        a = (mk * alpha)[..., None]
        self.rgb[sl] = self.rgb[sl] * (1 - a) + np.asarray(col, f32) * a
        self.a[sl] = self.a[sl] + a[..., 0] * (1 - self.a[sl])
        if acc:
            self.acc[sl] |= a[..., 0] > 0.4

    def shade(self, m, factor):
        """Multiply what is painted under mask m by `factor` (a number or fn(Y, X, m))."""
        if m is None:
            return
        y0, x0, mk = m
        h, w = mk.shape
        sl = (slice(y0, y0 + h), slice(x0, x0 + w))
        if callable(factor):
            Y, X = self.grid(y0, x0, h, w)
            factor = factor(Y, X, mk)
        f = np.asarray(factor, f32)
        if f.ndim == 2:
            f = f[..., None]
        self.rgb[sl] *= 1 - mk[..., None] * (1 - f)

    def cut(self, m):
        """Erase through mask m (a tear, a hole)."""
        if m is None:
            return
        y0, x0, mk = m
        h, w = mk.shape
        self.a[y0:y0 + h, x0:x0 + w] *= 1 - mk

    # conveniences
    def poly(self, pts, col, alpha=1.0, acc=False):
        self.put(self.mpoly([pts]), col, alpha, acc)

    def ell(self, cx, cy, rx, ry, col, alpha=1.0, acc=False):
        self.put(self.mell(cx, cy, rx, ry), col, alpha, acc)

    def line(self, pts, width, col, alpha=1.0, acc=False):
        self.put(self.mlines([pts], width), col, alpha, acc)

    def blit(self, o, X, Y):
        """Lay another sprite o into this one at (X, Y) units, clipped."""
        X, Y = int(round(X * S)), int(round(Y * S))
        x0, y0 = max(0, X), max(0, Y)
        x1, y1 = min(self.pw, X + o.pw), min(self.ph, Y + o.ph)
        if x1 <= x0 or y1 <= y0:
            return
        so = (slice(y0 - Y, y1 - Y), slice(x0 - X, x1 - X))
        sl = (slice(y0, y1), slice(x0, x1))
        a = o.a[so][..., None]
        self.rgb[sl] = self.rgb[sl] * (1 - a) + o.rgb[so] * a
        self.a[sl] = self.a[sl] + o.a[so] * (1 - self.a[sl])
        self.acc[sl] |= o.acc[so]


def rotate(s, deg):
    """A sprite turned by deg (counter-clockwise), on a canvas grown to fit."""
    if abs(deg) < 0.05:
        return s
    chans = [s.rgb[..., i] * s.a for i in range(3)] + [s.a]
    out = [np.asarray(Image.fromarray(c.astype(np.float32), "F").rotate(deg, Image.BICUBIC, expand=True), f32) for c in chans]
    acc = np.asarray(Image.fromarray(s.acc.astype(np.uint8) * 255).rotate(deg, Image.NEAREST, expand=True)) > 127
    a = np.clip(out[3], 0, 1)
    n = Spr(a.shape[1], a.shape[0], px=True)
    n.a = a
    n.rgb = np.clip(np.stack(out[:3], -1) / np.maximum(a, 1e-4)[..., None], 0, 1)
    n.acc = acc
    return n


def sphere(cx, cy, rx, ry, base, amb=0.5, spec=0.0, gloss=18):
    base = np.asarray(base, f32)

    def fn(Y, X, m):
        nx, ny = (X + 0.5 - cx) / rx, (Y + 0.5 - cy) / ry
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        d = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
        out = base * (amb + (1 - amb) * d)[..., None]
        if spec:
            out = out + spec * (d ** gloss)[..., None]
        return np.clip(out, 0, 1)
    return fn


def cylv(cx, rx, base, amb=0.55, spec=0.0, texf=None):
    """A vertical cylinder's shading across x (a pole, a pot, a bolt of cloth)."""
    base = np.asarray(base, f32)

    def fn(Y, X, m):
        nx = np.clip((X + 0.5 - cx) / rx, -1, 1)
        nz = np.sqrt(1 - nx * nx)
        d = np.clip(nx * LIGHT[0] + nz * (LIGHT[2] + 0.35), 0, 1.2) / 1.2
        out = base * (amb + (1 - amb) * d)[..., None]
        if spec:
            out = out + spec * np.exp(-((nx + 0.45) / 0.12) ** 2)[..., None]
        if texf is not None:
            out = out * texf(Y, X)[..., None]
        return np.clip(out, 0, 1)
    return fn


def flat(base, r=None, amt=0.06, name="fine"):
    """A flat colour with a little texture."""
    base = np.asarray(base, f32)
    off = toff(r if r is not None else rng)

    def fn(Y, X, m):
        t = tex(name, Y, X, off)
        return np.clip(base * (1 - amt + 2 * amt * t)[..., None], 0, 1)
    return fn


def jit(c, r, k=0.05):
    return np.clip(np.asarray(c, f32) * (1 + r.normal(0, k, 3)).astype(f32), 0, 1)


# ── layers: each throws its shadow on what is already drawn, then is laid on ───
img = None
accent = np.zeros((PH, PW), bool)


class Layer:
    """Sprites laid together, throwing one shadow (offset dx, dy and softness sigma, in units; strength k)."""

    def __init__(self, name, dx, dy, sigma, k):
        self.name, self.dx, self.dy, self.sigma, self.k = name, dx, dy, sigma, k
        self.items = []

    def add(self, s, X, Y):
        """Lay sprite s at (X, Y) units."""
        self.items.append((s, int(round(X * S)), int(round(Y * S))))

    def flush(self, vis=None, lit=None):
        """Lay it down. `vis` and `lit` are for a layer that lies on a surface
        already under others (the marks on the wall): how much of that surface
        shows, and the shadow already on it."""
        global img
        if self.k > 0 and self.items:
            A = np.zeros((PH, PW), f32)
            for s, X, Y in self.items:
                iy, ix = (np.arange(s.ph) + Y) % PH, (np.arange(s.pw) + X) % PW
                A[np.ix_(iy, ix)] = np.maximum(A[np.ix_(iy, ix)], s.a)
            sh = np.clip(blur(A, self.sigma, self.dx, self.dy), 0, 1)
            if vis is None:
                img *= (1 - self.k * sh)[..., None]
                self.covers(A, sh)
            else:
                img *= (1 - self.k * sh * vis)[..., None]
        for s, X, Y in self.items:
            iy, ix = (np.arange(s.ph) + Y) % PH, (np.arange(s.pw) + X) % PW
            g = np.ix_(iy, ix)
            a = s.a[..., None]
            if vis is not None:
                a = a * vis[g][..., None]
                img[g] = img[g] * (1 - a) + s.rgb * lit[g][..., None] * a
                continue
            img[g] = img[g] * (1 - a) + s.rgb * a
            accent[g] = np.where(s.a > 0.5, s.acc, accent[g])
        print(f"  {self.name}: {len(self.items)}", flush=True)
        self.items = []

    def covers(self, A, sh):
        """Keep count, for the marks, of how much of each surface still shows
        (SHOWS) and of the shadow that has fallen on it (LIT), as this layer
        (its cover A, its shadow sh) is laid over them."""
        for m in SHOWS.values():
            m *= 1 - A
        for m in LIT.values():
            m *= 1 - self.k * sh
        key = SURFACE.get(self.name)
        if key == "paper":                              # the wall and its paper are one surface: all of it shows, so far
            SHOWS["paper"], SHOWS["wall"], LIT["wall"] = A, np.ones((PH, PW), f32), np.ones((PH, PW), f32)
        elif key == "stack":
            np.maximum(SHOWS["stack"], A, out=SHOWS["stack"])
            LIT["stack"] = LIT["stack"] * (1 - A) + A
            for s, X, Y in self.items:                  # a crate's face shows, less what was then put on it
                g = np.ix_((np.arange(s.ph) + Y) % PH, (np.arange(s.pw) + X) % PW)
                SHOWS["wood"][g] = np.maximum(SHOWS["wood"][g] * (1 - s.a), s.a * getattr(s, "wood", False))


SURFACE = {"posters, graffiti": "paper", "stacks against the wall": "stack", "front row": "stack"}
SHOWS = {k: np.zeros((PH, PW), f32) for k in ("stack", "wood")}     # and "paper", "wall": see covers
LIT = {"stack": np.ones((PH, PW), f32)}                             # and "wall"


# ── glyphs: the city's own script, no real letters ───────────────────────────
def alphabet(n, seed):
    r = np.random.default_rng(seed)
    anc = [(x, y) for y in (0, 0.5, 1) for x in (0, 0.5, 1)]
    out = []
    for _ in range(n):
        strokes = []
        for _ in range(int(r.integers(2, 4))):
            t = r.random()
            if t < 0.55:
                i, j = r.choice(9, 2, replace=False)
                strokes.append([anc[i], anc[j]])
            elif t < 0.85:
                cx, cy = anc[int(r.integers(9))]
                rad = r.choice([0.5, 0.5, 0.35])
                a0 = r.uniform(0, 2 * np.pi)
                ext = r.uniform(1.4, 3.6)
                pts = [(cx + rad * np.cos(a0 + ext * k / 10), cy + rad * np.sin(a0 + ext * k / 10)) for k in range(11)]
                strokes.append([(min(1, max(0, x)), min(1, max(0, y))) for x, y in pts])
            else:
                x, y = anc[int(r.integers(9))]
                strokes.append([(x, y), (x + 0.02, y + 0.02)])
        out.append(strokes)
    return out


GLYPHS = alphabet(36, SEED + 100)


def glyph_lines(x, y, size, nglyphs, r, words=True, wobble=0.04, aspect=0.75, max_w=None):
    """Polylines for a run of glyphs starting at (x, y) (top-left), glyph height `size`."""
    lines, cx = [], x
    gw = size * aspect
    k = 0
    while k < nglyphs:
        if max_w is not None and cx + gw > x + max_w:
            break
        g = GLYPHS[int(r.integers(len(GLYPHS)))]
        for st in g:
            lines.append([(cx + (px + r.normal(0, wobble)) * gw, y + (py + r.normal(0, wobble)) * size) for px, py in st])
        cx += gw * 1.35
        k += 1
        if words and r.random() < 0.22:
            cx += gw * 0.8
    return lines, cx - x


# ── 1. the wall ─────────────────────────────────────────────────────────────
print("wall", flush=True)
mott, fine, speck = TEX["mott"], TEX["fine"], TEX["speck"]
damp = noise(2.3, seed=SEED + 6)
PLASTER = hexc("#cdc6b5")
plaster = PLASTER * (0.90 + 0.12 * mott + 0.05 * fine + 0.02 * speck)[..., None]
plaster = mix(plaster, hexc("#cbbb9c") * (0.95 + 0.05 * fine)[..., None], smooth(damp, 0.45, 0.8) * 0.4)
# a faded green dado along the foot, worn back to the plaster
dado_top = 1860 + 14 * np.sin(xx / NW * 2 * np.pi * 3 + 1.0) + 10 * (fine - 0.5)
dado = smooth(yy - dado_top, -1, 1)
worn = smooth(0.6 * noise(1.7, seed=SEED + 7) + 0.4 * speck + 0.12 * (yy > 2350), 0.56, 0.585)
paint = hexc("#a2a796") * (0.93 + 0.1 * mott + 0.04 * fine)[..., None]
img = mix(plaster, paint, dado * (1 - worn))
band = np.clip(1 - np.abs(yy - dado_top - 8) / 6, 0, 1) * (1 - worn)
img = mix(img, hexc("#8d6e60"), band * 0.6)
del paint, plaster, band

# brick behind the plaster: running bond on the tile's grid (30 x 60 courses)
BW, BH, BJ = 144, 48, 5
course = (yy // BH).astype(np.int32)
bx = (xx + (course % 2) * (BW // 2)) % NW
bid = (course * (NW // BW) + bx // BW).astype(np.int32)
lxb, lyb = bx % BW, yy % BH
BRICKS = np.array([hexc(c) for c in ("#9c6c58", "#a67a62", "#8f6b5a", "#ad8869", "#977062", "#a28a72")])
btone = rng.uniform(0.9, 1.06, bid.max() + 1).astype(f32)
bcol = BRICKS[rng.integers(0, len(BRICKS), bid.max() + 1)][bid] * btone[bid][..., None]
bcol = bcol * (0.88 + 0.16 * TEX["gh"] + 0.06 * fine)[..., None]
bedge = np.minimum(np.minimum(lxb, BW - lxb), np.minimum(lyb, BH - lyb)).astype(f32)
joint = smooth(BJ - bedge, -0.5, 0.8)
brick = mix(bcol, hexc("#b0a693") * (0.9 + 0.1 * fine)[..., None], joint)
brick *= (1 - 0.18 * smooth(3 - np.abs(lyb - BJ - 1.0), 0, 2) * (lyb > BJ))[..., None]     # each brick's top in the joint's shade
del bcol, bedge, joint
spall_n = noise(1.8, seed=SEED + 8)
low = smooth(yy, 1900, 2500)
SP = smooth(spall_n + 0.10 * low + 0.05 * fine + 0.06 * smooth(damp, 0.5, 0.9), 0.715, 0.725)
PAINTED = dado * (1 - worn) * (1 - SP)     # where the dado's paint still is (the marks scrape it off)
inside = np.clip(SP * (1 - shift(SP, 8 * S, 8 * S)), 0, 1)
lit = np.clip((1 - SP) * shift(SP, 4 * S, 4 * S), 0, 1)
brick *= (1 - 0.35 * blur(inside, 2.0))[..., None]
img = mix(img, brick, SP)
img *= (1 + 0.16 * lit)[..., None]
img *= (1 - 0.10 * np.clip(shift(SP, -2 * S, -2 * S) - SP, 0, 1))[..., None]
del brick, inside, lit, course, bx, bid, lxb, lyb

# ghost sign: huge faded glyphs painted high up, mostly under the awnings
gs = Spr(NW, 360)
for gx0 in (80, 2300):
    gs.poly([(gx0, 40), (gx0 + 1900, 40), (gx0 + 1900, 330), (gx0, 330)], hexc("#d8ccb0"), 0.35)
    ln, _ = glyph_lines(gx0 + 70, 80, 200, 9, np.random.default_rng(SEED + 9 + gx0), words=True, aspect=0.8, max_w=1760)
    gs.put(gs.mlines(ln, 26), hexc("#7f6a5c"), 0.45)
gs.a *= smooth(TEX["mott"][:gs.ph] * 0.6 + TEX["fine"][:gs.ph] * 0.4, 0.38, 0.62)
g = gs.a[..., None]
img[:gs.ph] = img[:gs.ph] * (1 - g) + gs.rgb * g
del gs

# cracks, running from the spalls and from nowhere
cr = Spr(NW, NH)
for _ in range(26):
    x, y = rng.uniform(0, NW), rng.uniform(300, 2500)
    a = rng.uniform(0.9, 2.2) * rng.choice([1, -1])
    L = rng.uniform(80, 340)
    pts = jag((x, y), (x + L * np.cos(a), y + abs(L * np.sin(a))), 0.18, rng)
    cr.line(pts, rng.uniform(1.2, 2.4), hexc("#6a6258"), 0.7)
g = cr.a[..., None]
img = img * (1 - g) + cr.rgb * g
CRACK = cr.a                               # kept: moss grows in them
del cr

# damp streaks down from the top, rising damp and grime at the foot
top_ = np.broadcast_to(yy < 700, (PH, PW))
DRIP_EVERY = 5390           # units^2 (0.094in^2) of the top band to a drip: the brightest specks, as many to the inch at any DPI
src = (speck >= np.quantile(speck[top_], 1 - 1 / (DRIP_EVERY * S * S))).astype(f32) * top_ * smooth(damp, 0.4, 0.7)
drip = np.where(ky >= 0, np.exp(-ky / 260.0), 0) * np.exp(-(kx / 2.5) ** 2)
streak = circ_conv(src, drip.astype(f32))
streak = np.clip(streak / np.percentile(streak[streak > 1e-3], 99), 0, 1) * smooth(noise(1.0, stretch=(1, 0.1), seed=SEED + 10), 0.3, 0.7)
img *= (1 - 0.13 * streak)[..., None]
rise = smooth(yy - (2280 - 120 * damp), -40, 40)
img *= (1 - 0.06 * rise - 0.10 * smooth(yy, 2150, FLOOR) - 0.05 * smooth(damp, 0.5, 0.8))[..., None]
img = mix(img, img * hexc("#e6dcc4"), np.clip(1 - np.abs(yy - (2280 - 120 * damp)) / 10, 0, 1) * 0.6)   # the tide mark
del src, drip, streak, rise, worn, spall_n, low, top_

L_FLAT = Layer("posters, graffiti", 2, 3, 2.0, 0.12)
L_FIX = Layer("fixtures", 6, 8, 4.0, 0.30)
L_GOODS = Layer("goods on the wall", 10, 14, 7.0, 0.32)
L_BACK = Layer("stacks against the wall", 12, 10, 10.0, 0.30)
L_FRONT = Layer("front row", 14, 6, 9.0, 0.30)
L_POLE = Layer("poles", 16, 10, 8.0, 0.25)
L_AWN = Layer("awnings", 6, 46, 26.0, 0.40)
L_HANG = Layer("hung from the awnings", 14, 22, 10.0, 0.28)
L_TOP = Layer("ropes and bulbs", 14, 26, 9.0, 0.22)
GLOWS = []


# ── 2. paper and paint on the wall ──────────────────────────────────────────
PAPERS = ["#ddd4bf", "#d6c79f", "#d9bfae", "#bfcac4", "#d2cbb2", "#c7bfa6", "#e0d8c8"]
INKS = ["#6a5c58", "#8a4f45", "#4f6168", "#5d6b4f", "#7a6648", "#6d5470"]


def poster(w, h, r):
    s = Spr(w + 4, h + 4)
    paper = jit(hexc(r.choice(PAPERS)), r, 0.03)
    ink, ink2 = hexc(r.choice(INKS)), hexc(r.choice(INKS))
    s.poly([(2, 2), (w + 2, 2), (w + 2, h + 2), (2, h + 2)], flat(paper, r, 0.05))
    layout = r.choice(5, p=[0.22, 0.14, 0.26, 0.2, 0.18])
    m = 2 + w * 0.08
    if layout == 0:                                  # headline, a figure, small text
        ln, _ = glyph_lines(m, 2 + h * 0.07, h * 0.11, 5, r, aspect=0.7, max_w=w - 2 * m)
        s.put(s.mlines(ln, max(2.5, h * 0.018)), ink)
        cx, cy, rr = 2 + w / 2, 2 + h * 0.46, min(w, h) * 0.24
        s.ell(cx, cy, rr, rr, ink2, 0.85)
        s.ell(cx, cy, rr * 0.55, rr * 0.4, paper)
        s.ell(cx, cy, rr * 0.22, rr * 0.22, ink)
        for k in range(4):
            ln, _ = glyph_lines(m, 2 + h * (0.72 + k * 0.055), h * 0.032, 30, r, max_w=w - 2 * m)
            s.put(s.mlines(ln, 1.6), ink, 0.85)
    elif layout == 1:                                # a band of colour, a creature, a date line
        s.poly([(2, 2), (w + 2, 2), (w + 2, 2 + h * 0.3), (2, 2 + h * 0.3)], ink2, 0.8)
        ln, _ = glyph_lines(m, 2 + h * 0.06, h * 0.15, 4, r, aspect=0.75, max_w=w - 2 * m)
        s.put(s.mlines(ln, max(3, h * 0.022)), paper)
        bx, by = 2 + w * 0.5, 2 + h * 0.58
        tall = r.uniform(0.12, 0.2)
        s.ell(bx, by, w * r.uniform(0.15, 0.26), h * tall, ink, 0.8)                     # a body
        eyes = [[0], [-1, 1], [-1, 0, 1]][int(r.integers(3))]
        for e in eyes:
            s.ell(bx + e * w * 0.09, by - h * 0.04, w * 0.05, w * 0.05, paper)          # eyes
            s.ell(bx + e * w * 0.09, by - h * 0.04, w * 0.02, w * 0.02, ink)
        if r.random() < 0.6:
            for e in (-1, 1):
                s.line([(bx + e * w * 0.1, by - h * tall * 0.8), (bx + e * w * 0.2, by - h * (tall + 0.08))], 3, ink, 0.8)
        else:
            for k in range(-2, 3):
                s.line([(bx + k * w * 0.06, by + h * tall * 0.8), (bx + k * w * 0.09, by + h * (tall + 0.06))], 3, ink, 0.8)
        ln, _ = glyph_lines(m, 2 + h * 0.84, h * 0.06, 12, r, max_w=w - 2 * m)
        s.put(s.mlines(ln, 2.2), ink)
    elif layout == 3:                                # shapes: a big sign of a thing, and a line of words
        for k in range(int(r.integers(2, 5))):
            cx_, cy_ = 2 + w * r.uniform(0.25, 0.75), 2 + h * r.uniform(0.2, 0.6)
            rr = min(w, h) * r.uniform(0.12, 0.3)
            c = ink if k % 2 else ink2
            if r.random() < 0.5:
                s.ell(cx_, cy_, rr, rr, c, 0.75)
            else:
                a0 = r.uniform(0, 2 * np.pi)
                s.poly([(cx_ + rr * np.cos(a0 + j * 2.094), cy_ + rr * np.sin(a0 + j * 2.094)) for j in range(3)], c, 0.75)
        ln, _ = glyph_lines(m, 2 + h * 0.8, h * 0.1, 6, r, aspect=0.7, max_w=w - 2 * m)
        s.put(s.mlines(ln, max(2.5, h * 0.016)), ink)
    elif layout == 4:                                # wanted: a frame, a head and shoulders, words under it
        s.put(s.mlines([[(m, m), (w + 4 - m, m), (w + 4 - m, h * 0.62), (m, h * 0.62), (m, m)]], 2.5), ink, 0.8)
        hx, hy = 2 + w / 2, 2 + h * 0.3
        s.poly([(hx - w * 0.3, h * 0.62), (hx - w * 0.22, hy + h * 0.14), (hx + w * 0.22, hy + h * 0.14), (hx + w * 0.3, h * 0.62)], ink2, 0.75)
        s.ell(hx, hy, w * 0.15, h * 0.13, ink2, 0.8)
        if r.random() < 0.5:
            for e in (-1, 1):
                s.poly([(hx + e * w * 0.08, hy - h * 0.08), (hx + e * w * 0.2, hy - h * 0.2), (hx + e * w * 0.13, hy - h * 0.05)], ink2, 0.8)
        ln, _ = glyph_lines(m, 2 + h * 0.67, h * 0.09, 5, r, aspect=0.7, max_w=w - 2 * m)
        s.put(s.mlines(ln, max(2.5, h * 0.016)), ink)
        for k in range(3):
            ln, _ = glyph_lines(m, 2 + h * (0.8 + k * 0.05), h * 0.03, 30, r, max_w=w - 2 * m)
            s.put(s.mlines(ln, 1.5), ink, 0.85)
    else:                                            # text all over: a bill
        y = 2 + h * 0.06
        while y < h * 0.92:
            sz = h * (0.07 if y < h * 0.2 else r.choice([0.03, 0.035, 0.05]))
            ln, _ = glyph_lines(m, y, sz, 40, r, max_w=w - 2 * m)
            s.put(s.mlines(ln, max(1.5, sz * 0.14)), ink if r.random() < 0.7 else ink2, 0.9)
            y += sz * 1.6
        if r.random() < 0.6:
            s.poly([(2, h * 0.9), (w + 2, h * 0.9), (w + 2, h + 2), (2, h + 2)], ink2, 0.7)
    # weather: bleached, rain-streaked, grimed at the foot
    Y, X = s.grid()
    off = toff(r)
    st = tex("gv", Y, X, off)
    s.rgb = mix(s.rgb, paper * 0.95, 0.25 + 0.25 * smooth(st, 0.3, 0.8))
    s.rgb *= (1 - 0.10 * smooth(Y / s.h, 0.6, 1.0) - 0.06 * tex("mott", Y, X, off))[..., None]
    # torn: a bite out of one edge, and the paper worn through in patches
    if r.random() < 0.7:
        side = r.integers(4)
        cx = r.uniform(0.2, 0.8) * w
        cy = r.uniform(0.2, 0.8) * h
        R = r.uniform(0.15, 0.4) * min(w, h)
        P = [(cx if side in (0, 1) else (0 if side == 2 else w + 4), cy if side in (2, 3) else (0 if side == 0 else h + 4))]
        bite = [(P[0][0] + R * 1.3 * np.cos(t) + r.normal(0, R * 0.08), P[0][1] + R * np.sin(t) + r.normal(0, R * 0.08))
                for t in np.linspace(0, 2 * np.pi, 22)]
        s.cut(s.mpoly([bite]))
    worn = smooth(tex("mott", Y, X, off) * 0.7 + tex("fine", Y, X, off) * 0.3, 0.68, 0.74)
    s.a *= 1 - worn
    # a corner peeling: the flap turned over, its back pale, a shadow under it
    if r.random() < 0.75:
        c = r.integers(4)
        sx, sy = (0 if c in (0, 2) else s.w), (0 if c in (0, 1) else s.h)
        fx, fy = (1 if sx == 0 else -1), (1 if sy == 0 else -1)
        L1, L2 = r.uniform(0.18, 0.35) * w, r.uniform(0.18, 0.35) * h
        A, B = (sx + fx * L1, sy), (sx, sy + fy * L2)
        s.cut(s.mpoly([[(sx, sy), A, B]]))
        # the flap: the corner reflected over the fold line A-B, pulled off the wall a little
        ax, ay = A
        bx_, by_ = B
        dx, dy = bx_ - ax, by_ - ay
        t = ((sx - ax) * dx + (sy - ay) * dy) / (dx * dx + dy * dy)
        px, py = ax + t * dx, ay + t * dy
        rx, ry = 2 * px - sx, 2 * py - sy
        rx, ry = px + (rx - px) * 0.8, py + (ry - py) * 0.8
        s.put(s.mpoly([[(ax + fx * 3, ay + fy * 6), (bx_ + fx * 6, by_ + fy * 3), (rx + 8, ry + 10)]]), hexc("#4a443e"), 0.25)
        s.poly([A, B, (rx, ry)], lambda Y, X, m: mix(np.broadcast_to(hexc("#e2dccd"), Y.shape + (3,)), hexc("#b6ae9c"),
                                                      np.clip(((X - ax) * (rx - ax) + (Y - ay) * (ry - ay)) / ((rx - ax) ** 2 + (ry - ay) ** 2 + 1), 0, 1)))
    return s


def scraps(w, h, r):
    """The torn remains of older bills: pale shreds, a few with a scrap of print."""
    s = Spr(w, h)
    for _ in range(int(r.integers(5, 12))):
        x, y = r.uniform(0, w * 0.8), r.uniform(0, h * 0.8)
        sw, sh = r.uniform(20, 90), r.uniform(15, 70)
        pts = [(x + sw * np.cos(t) * r.uniform(0.6, 1.1) + sw, y + sh * np.sin(t) * r.uniform(0.6, 1.1) + sh)
               for t in np.linspace(0, 2 * np.pi, 9)[:-1]]
        col = jit(hexc(r.choice(PAPERS)), r, 0.04)
        s.poly(pts, flat(col, r), r.uniform(0.6, 0.9))
        if r.random() < 0.5:
            ln, _ = glyph_lines(x + sw * 0.6, y + sh * 0.8, 14, 4, r)
            s.put(s.mlines(ln, 1.6), hexc(r.choice(INKS)), 0.6)
    return s


GRAF = ["#8aa395", "#b8796a", "#8e88a8", "#d5cdb8", "#a8a26a", "#7b9a7a"]


def graffiti(w, h, r, fat=True):
    s = Spr(w, h)
    n = int(r.integers(3, 6))
    size = h * 0.62
    gw = (w - 40) / (n * 1.25)
    ln = []
    cx = 20
    for k in range(n):
        g = GLYPHS[int(r.integers(len(GLYPHS)))]
        sl = r.normal(0, 0.15)
        y0 = h * 0.18 + r.normal(0, h * 0.04)
        for st in g:
            ln.append([(cx + (px + sl * (1 - py)) * gw + r.normal(0, 2), y0 + py * size + r.normal(0, 2)) for px, py in st])
        cx += gw * 1.25
    col = jit(hexc(r.choice(GRAF)), r, 0.04)
    if fat:
        wid = r.uniform(14, 22)
        out = hexc("#55504c")
        s.put(s.mlines(ln, wid + 8), out, 0.75)
        s.put(s.mlines(ln, wid), flat(col, r, 0.08), 0.95)
        s.put(s.mlines([[(p[0] - 2, p[1] - 2) for p in l] for l in ln], wid * 0.3), np.clip(col * 1.15, 0, 1), 0.5)
        drips = []
        for l in ln:
            for (px, py) in l[::max(1, len(l) // 2)]:
                if r.random() < 0.25:
                    drips.append([(px, py), (px + r.normal(0, 0.5), py + r.uniform(20, 70))])
        s.put(s.mlines(drips, 3.5), col, 0.85)
    else:
        s.put(s.mlines(ln, r.uniform(3, 5)), hexc(r.choice(["#4f4a4c", "#6b4e5a", "#45566a"])), 0.8)
    Y, X = s.grid()
    s.a *= 0.55 + 0.4 * smooth(tex("mott", Y, X, toff(r)), 0.25, 0.65)
    return s


# ── 3. fixtures ─────────────────────────────────────────────────────────────
WOOD = ["#9d8f78", "#a39580", "#8f826e", "#aa9b80", "#968b7a", "#a69a86"]
METAL = hexc("#8e8b84")
DARKMETAL = hexc("#5c5852")
ROPE = hexc("#b7a47c")
TWINE = hexc("#a8977a")


def wood_fn(base, r, along="x", amt=0.22):
    off = toff(r)
    base = np.asarray(base, f32)
    name = "gh" if along == "x" else "gv"

    def fn(Y, X, m):
        g = tex(name, Y, X, off)
        f = tex("fine", Y, X, off)
        return np.clip(base * (1 - amt + 2 * amt * g + 0.06 * (f - 0.5))[..., None], 0, 1)
    return fn


def rail(w, r):
    s = Spr(w, 40)
    for bxp in (14, w - 26):
        s.poly([(bxp, 14), (bxp + 12, 14), (bxp + 12, 38), (bxp, 38)], DARKMETAL * 1.1)
        s.ell(bxp + 6, 32, 2.5, 2.5, DARKMETAL * 0.8)
    s.poly([(0, 8), (w, 8), (w, 18), (0, 18)], cylh(13, 5, METAL * 0.95, spec=0.15))
    return s


def cylh(cy, ry, base, amb=0.55, spec=0.0):
    """A horizontal cylinder's shading across y (a rail, a rod, a wire)."""
    base = np.asarray(base, f32)

    def fn(Y, X, m):
        ny = np.clip((Y + 0.5 - cy) / ry, -1, 1)
        nz = np.sqrt(1 - ny * ny)
        d = np.clip(ny * LIGHT[1] + nz * (LIGHT[2] + 0.35), 0, 1.2) / 1.2
        out = base * (amb + (1 - amb) * d)[..., None]
        if spec:
            out = out + spec * np.exp(-((ny + 0.5) / 0.15) ** 2)[..., None]
        return np.clip(out, 0, 1)
    return fn


def pegboard(w, h, r):
    s = Spr(w, h)
    base = jit(hexc("#a28a68"), r, 0.04)
    s.poly([(0, 0), (w, 0), (w, h), (0, h)], wood_fn(base, r, "x", 0.08))
    s.put(s.mlines([[(2, 2), (w - 2, 2), (w - 2, h - 2), (2, h - 2), (2, 2)]], 5), base * 0.82)
    holes = []
    for y in range(20, h - 10, 24):
        for x in range(20, w - 10, 24):
            holes.append((x, y))
    for (x, y) in holes:
        s.ell(x, y, 3.2, 3.2, base * 0.45)
    for (x, y) in ((10, 10), (w - 10, 10), (10, h - 10), (w - 10, h - 10)):
        s.ell(x, y, 4, 4, METAL)
    return s


def sign(w, h, r, style=None):
    style = style if style is not None else int(r.integers(3))
    s = Spr(w, h)
    paint = jit(hexc(r.choice(["#c9c0a2", "#9fb39a", "#c99f7c", "#aebfc1", "#d6c483", "#a89cae", "#7f9a74"])), r, 0.04)
    ink = hexc(r.choice(["#5a4a44", "#7c3e36", "#3f5560", "#4b5e3e", "#e6dcc4"]))
    if np.mean(ink) > 0.7 and np.mean(paint) > 0.65:
        ink = hexc("#5a4a44")
    if style == 2:                                       # a tin sheet, rusting
        s.poly([(0, 0), (w, 0), (w, h), (0, h)], flat(paint, r, 0.08, "mott"))
    else:                                                # planks
        nplank = max(1, int(round(h / 70)))
        ph = h / nplank
        for k in range(nplank):
            s.poly([(0, k * ph + 1), (w, k * ph + 1 + r.normal(0, 1)), (w, (k + 1) * ph - 1), (0, (k + 1) * ph - 1)],
                   wood_fn(jit(hexc(r.choice(WOOD)), r), r, "x"))
        s.poly([(4, 4), (w - 4, 4), (w - 4, h - 4), (4, h - 4)], flat(paint, r, 0.06, "mott"))
    # border and words
    s.put(s.mlines([[(10, 10), (w - 10, 10), (w - 10, h - 10), (10, h - 10), (10, 10)]], 3.5), ink, 0.8)
    nl = 1 if h < 120 else 2
    for k in range(nl):
        sz = (h - 34) / nl * 0.72
        n = max(2, int((w - 40) / (sz * 0.75 * 1.35)))
        n = int(r.integers(max(2, n - 2), n + 1))
        ln, tw = glyph_lines(0, 0, sz, n, r, words=False, wobble=0.05)
        ox = (w - tw) / 2 + sz * 0.15
        oy = 17 + k * (h - 34) / nl + ((h - 34) / nl - sz) / 2
        ln = [[(x + ox, y + oy) for x, y in l] for l in ln]
        s.put(s.mlines(ln, max(3, sz * 0.13)), ink, 0.92)
    # chipped back to the wood or the tin, rust at the edges of a tin sign
    Y, X = s.grid()
    off = toff(r)
    edge = np.minimum.reduce([X, w - 1 - X, Y, h - 1 - Y]).astype(f32)
    chip = smooth(tex("fine", Y, X, off) * 0.6 + tex("speck", Y, X, off) * 0.4 + 0.12 * np.exp(-edge / 12), 0.66, 0.70)
    under = hexc("#9a6a4c") if style == 2 else np.clip(hexc("#9d8a6c") * (0.85 + 0.3 * tex("gh", Y, X, off))[..., None], 0, 1)
    s.rgb = mix(s.rgb, under, chip * 0.85)
    s.rgb *= (0.92 + 0.1 * tex("mott", Y, X, off))[..., None]
    s.rgb = mix(s.rgb, s.rgb.mean(-1, keepdims=True), 0.15)
    for (x, y) in ((8, 8), (w - 8, 8), (8, h - 8), (w - 8, h - 8)):
        s.ell(x, y, 3, 3, DARKMETAL)
    return s


def hung(s, wire_h, r, two=True):
    """A sign or board on a wire: a canvas taller by wire_h, the wire running up to a nail."""
    o = Spr(s.w, s.h + wire_h)
    nx = s.w / 2 + r.normal(0, 6)
    if two:
        o.put(o.mlines([[(10, wire_h + 8), (nx, 2), (s.w - 10, wire_h + 8)]], 2.0), DARKMETAL)
    else:
        o.line([(nx, 2), (nx, wire_h + 6)], 2.0, DARKMETAL)
    o.ell(nx, 3, 3, 3, DARKMETAL * 0.8)
    o.blit(s, 0, wire_h)
    return o


def conduit(w, r):
    """A run of conduit with junction boxes and a spill of wires out of one."""
    s = Spr(w, 120)
    s.poly([(0, 40), (w, 40), (w, 56), (0, 56)], cylh(48, 8, hexc("#9a978e"), spec=0.12))
    for x in range(int(r.uniform(40, 120)), w, int(r.uniform(260, 420))):
        s.poly([(x - 4, 36), (x + 8, 36), (x + 8, 60), (x - 4, 60)], DARKMETAL * 1.2)
    for x in r.uniform(60, w - 120, 2):
        s.poly([(x, 22), (x + 70, 22), (x + 70, 76), (x, 76)], flat(hexc("#8d8a80"), r, 0.06))
        s.put(s.mlines([[(x + 3, 24), (x + 67, 24)]], 2), hexc("#b5b1a6"))
        s.put(s.mlines([[(x + 3, 74), (x + 67, 74), (x + 67, 24)]], 2), hexc("#6a665f"))
        for k in range(int(r.integers(2, 5))):
            col = hexc(r.choice(["#55524d", "#8a5a4a", "#6b7b62", "#b39a5a", "#5f6d7a"]))
            x0 = x + 10 + k * 12
            pts = [(x0, 76), (x0 + r.normal(0, 10), 92), (x0 + r.normal(0, 30), 110 + r.uniform(0, 8))]
            s.line(pts, 3, col)
    return s


# ── 4. goods ────────────────────────────────────────────────────────────────
CHILLI = ["#a2402e", "#9a3a2c", "#b0533a", "#8a3a2c", "#a64b36", "#7c3a2e", "#b2643e"]


def chilli_string(L, r, kind="chilli"):
    W = 120
    s = Spr(W, L + 70)
    cx = W / 2
    s.line([(cx, 0), (cx + r.normal(0, 2), L + 30)], 2.5, TWINE)
    n = int(L / (7 if kind == "chilli" else 10))
    order = list(range(n))
    r.shuffle(order)
    for i in order:
        y = 16 + i * L / n + r.normal(0, 3)
        side = r.choice([-1, 1])
        ang = np.radians(side * r.uniform(10, 65))
        length = r.uniform(34, 52) if kind == "chilli" else r.uniform(26, 36)
        wid = r.uniform(9, 13) if kind == "chilli" else r.uniform(14, 18)
        bend = r.normal(0, 0.25)
        d = np.array([np.sin(ang), np.cos(ang)])
        nrm = np.array([-d[1], d[0]])
        sx, sy = cx + side * r.uniform(0, 6), y
        left, right, mid = [], [], []
        for t in np.linspace(0, 1, 14):
            c = np.array([sx, sy]) + d * t * length + nrm * bend * length * t * t
            hw = wid / 2 * min(1, (t + 0.1) / 0.25) * (1 - t) ** (0.6 if kind == "chilli" else 1.4)
            left.append(tuple(c + nrm * hw))
            right.append(tuple(c - nrm * hw))
            mid.append(c)
        if kind == "chilli":
            base = jit(hexc(r.choice(CHILLI)), r, 0.05)
        else:                                       # dried okra / pods: dusty green-brown
            base = jit(hexc(r.choice(["#8a8a5a", "#7d7a50", "#958c5c", "#6f7450"])), r, 0.05)
        lit = -(nrm[0] * LIGHT[0] + nrm[1] * LIGHT[1])

        def fn(Y, X, m, sx=sx, sy=sy, nrm=nrm, wid=wid, base=base, lit=lit):
            u = ((X - sx) * nrm[0] + (Y - sy) * nrm[1]) / (wid / 2)
            v = 0.72 + 0.25 * np.clip(-u * np.sign(lit) * 0.5 + 0.5, 0, 1) + 0.18 * np.exp(-((u * np.sign(lit) + 0.45) / 0.18) ** 2)
            return np.clip(base * v[..., None], 0, 1)
        s.poly(left + right[::-1], fn, acc=True)
        s.line([(sx, sy - 4), (sx + d[0] * 6, sy + d[1] * 6)], 4, hexc("#6d6a44"))
    return s


def garlic_braid(L, r):
    W = 110
    s = Spr(W, L + 50)
    cx = W / 2
    straw = hexc("#bfa97a")
    for k in range(int(L / 14)):
        y = k * 14
        e = 1 if k % 2 else -1
        s.line([(cx - 12 * e, y), (cx + 12 * e, y + 18)], 7, straw * (0.92 + 0.08 * e))
        s.line([(cx - 12 * e, y), (cx + 12 * e, y + 18)], 1.5, straw * 0.75, 0.6)
    n = int(L / 30)
    for i in range(n):
        y = 18 + i * L / n + r.normal(0, 3)
        x = cx + (1 if i % 2 else -1) * r.uniform(10, 20)
        rx, ry = r.uniform(17, 21), r.uniform(15, 19)
        base = jit(hexc(r.choice(["#ddd4c2", "#d8ccbc", "#e0d6ca", "#d6c8c0"])), r, 0.02)
        s.ell(x, y, rx, ry, sphere(x - rx * 0.1, y, rx, ry, base, 0.55))
        for k in (-0.5, 0, 0.5):                       # the cloves' seams
            pts = [(x + k * rx * np.sqrt(max(0, 1 - t * t)) * 1.0, y + t * ry * 0.95) for t in np.linspace(-0.9, 0.9, 9)]
            s.line(pts, 1.4, hexc("#a8909a"), 0.55)
        s.line([(x, y - ry), (x - (x - cx) * 0.5, y - ry - 10)], 5, straw * 0.95)
        s.put(s.mlines([[(x + j, y + ry - 1), (x + j * 2, y + ry + 6)] for j in (-4, -1, 2, 5)], 1.2), hexc("#9c8c70"), 0.7)
    return s


def herb_bunch(r):
    """A bundle of dried herbs hung head-down."""
    w, h = int(r.uniform(60, 90)), int(r.uniform(120, 170))
    s = Spr(w, h + 20)
    cx = w / 2
    base = jit(hexc(r.choice(["#8a8f62", "#7f8a66", "#9a9068", "#7c7f5e"])), r, 0.05)
    s.line([(cx, 0), (cx, 22)], 2.0, TWINE)
    for _ in range(40):
        t = r.uniform(-1, 1)
        ex, ey = cx + t * w * 0.45, h - r.uniform(0, 40)
        s.line([(cx + t * 6, 20), (cx + t * 14, 50), (ex, ey)], r.uniform(1.5, 3), base * r.uniform(0.75, 1.1))
    for _ in range(70):
        t = r.uniform(-1, 1)
        x, y = cx + t * w * 0.42 * r.uniform(0.4, 1), r.uniform(50, h - 5)
        s.ell(x, y, r.uniform(3, 6), r.uniform(2, 4), base * r.uniform(0.7, 1.15))
    s.poly([(cx - 9, 16), (cx + 9, 16), (cx + 8, 30), (cx - 8, 30)], TWINE * 0.85)
    return s


def basket(w, h, r, handle=True, contents=None):
    hh = h * 0.6 if handle else 0
    s = Spr(w + 10, h + hh + 10)
    base = jit(hexc(r.choice(["#b8975e", "#a88a5c", "#c2a571", "#9c8058"])), r, 0.04)
    top = hh + 6
    cx = s.w / 2
    if handle:
        pts = [(cx + (w * 0.42) * np.cos(t), top + 4 - hh * np.sin(t)) for t in np.linspace(0, np.pi, 30)]
        s.line(pts, 9, cylh(0, 1, base * 0.9))
        s.line(pts, 3, base * 1.1, 0.5)
    if contents is not None:
        for _ in range(int(w / 9)):
            fx = cx + r.uniform(-w * 0.42, w * 0.42)
            fr = r.uniform(11, 17)
            col = jit(contents, r, 0.06)
            s.ell(fx, top + r.uniform(-fr * 0.6, fr * 0.2), fr, fr * 0.95, sphere(fx, top, fr, fr, col, 0.5, 0.06), acc=True)
    body = [(cx - w / 2, top)]
    for t in np.linspace(0, 1, 16):
        body.append((cx - w / 2 + w * 0.15 * t ** 2, top + h * t))
    for t in np.linspace(1, 0, 16):
        body.append((cx + w / 2 - w * 0.15 * t ** 2, top + h * t))
    off = toff(r)

    def weave(Y, X, m):
        u, v = (X - cx) / 11, (Y - top) / 9
        chk = ((np.floor(u) + np.floor(v)) % 2).astype(f32)
        strand = 0.86 + 0.14 * np.cos(np.pi * (v - np.floor(v) - 0.5) * 2) * (chk * 2 - 1) * 0.5 + 0.07 * chk
        nx = np.clip((X - cx) / (w / 2), -1, 1)
        cyl = 0.65 + 0.35 * np.sqrt(1 - nx * nx) - 0.12 * nx
        return np.clip(base * (strand * cyl * (0.95 + 0.1 * tex("fine", Y, X, off)))[..., None], 0, 1)
    s.poly(body, weave)
    s.poly([(cx - w / 2 - 3, top - 5), (cx + w / 2 + 3, top - 5), (cx + w / 2 + 3, top + 9), (cx - w / 2 - 3, top + 9)], cylh(top + 2, 7, base * 0.95))
    for x in np.arange(cx - w / 2, cx + w / 2, 8):
        s.line([(x, top - 4), (x + 6, top + 8)], 1.4, base * 0.7, 0.6)
    return s


POT_METALS = {"copper": "#ad7d5e", "alu": "#aeaea8", "enamel": "#8ea2ae", "enamel2": "#c9c2ae", "iron": "#7a7670"}


def pot(w, h, r, metal=None):
    metal = metal or r.choice(list(POT_METALS))
    base = jit(hexc(POT_METALS[metal]), r, 0.03)
    s = Spr(w + 40, h + 40)
    cx, top = s.w / 2, 26
    # the bail handle up to the hook
    s.line([(cx - w / 2 + 4, top + 10), (cx, 2), (cx + w / 2 - 4, top + 10)], 3, DARKMETAL)
    body = [(cx - w / 2, top)] + [(cx - w / 2 - 3 * np.sin(np.pi * t), top + h * t) for t in np.linspace(0, 1, 10)] + \
           [(cx - w / 2 + w * 0.08 * (t ** 2), top + h + 6 * t) for t in np.linspace(0, 1, 5)] + \
           [(cx + w / 2 - w * 0.08 * (t ** 2), top + h + 6 * t) for t in np.linspace(1, 0, 5)] + \
           [(cx + w / 2 + 3 * np.sin(np.pi * t), top + h * t) for t in np.linspace(1, 0, 10)]
    spec = 0.12 if metal in ("alu", "copper") else 0.05
    s.poly(body, cylv(cx, w / 2 + 3, base, 0.5, spec))
    s.poly([(cx - w / 2 - 5, top - 4), (cx + w / 2 + 5, top - 4), (cx + w / 2 + 5, top + 6), (cx - w / 2 - 5, top + 6)], cylv(cx, w / 2 + 5, base * 1.05, 0.55, spec))
    for e in (-1, 1):
        s.line([(cx + e * (w / 2 + 2), top + 12), (cx + e * (w / 2 + 12), top + 14), (cx + e * (w / 2 + 2), top + 24)], 4, base * 0.7)
    if metal.startswith("enamel"):
        for _ in range(int(r.integers(2, 6))):
            x, y = cx + r.uniform(-w / 2.4, w / 2.4), top + r.uniform(8, h)
            s.ell(x, y, r.uniform(2, 6), r.uniform(2, 5), hexc("#4f4b48"))
        s.put(s.mlines([[(cx - w / 2, top + 1), (cx + w / 2, top + 1)]], 4), hexc("#5c6670"))
    Y, X = s.grid()
    s.rgb *= (0.92 + 0.1 * tex("mott", Y, X, toff(r)))[..., None]
    return s


def pan(R, r, metal=None):
    metal = metal or r.choice(["iron", "alu", "copper", "iron"])
    base = jit(hexc(POT_METALS[metal]), r, 0.03)
    hl = R * 1.5
    s = Spr(2 * R + 10, 2 * R + hl + 10)
    cx, cy = s.w / 2, hl + R + 4
    s.poly([(cx - 7, 6), (cx + 7, 6), (cx + 6, cy - R + 6), (cx - 6, cy - R + 6)], cylv(cx, 7, base * 0.8))
    s.ell(cx, 14, 4, 5, hexc("#4a4642"))
    s.ell(cx, cy, R, R, sphere(cx, cy, R * 1.2, R * 1.2, base, 0.6, 0.06))
    s.ell(cx, cy, R * 0.84, R * 0.84, lambda Y, X, m: np.clip(base * (0.78 + 0.18 * np.clip(((X - cx) - (Y - cy)) / (R * 1.6) + 0.5, 0, 1))[..., None], 0, 1))
    if metal == "iron":
        Y, X = s.grid()
        s.rgb = mix(s.rgb, hexc("#8a6248"), smooth(tex("mott", Y, X, toff(r)), 0.6, 0.75) * 0.5 * (s.a > 0))
    return s


def ladle(r):
    L = r.uniform(140, 200)
    s = Spr(50, L + 40)
    base = hexc(r.choice(["#aeaea8", "#9e9a92", "#ad7d5e"]))
    s.ell(25, 8, 5, 5, DARKMETAL)
    s.line([(25, 10), (25, L)], 5, cylv(25, 3, base))
    if r.random() < 0.5:
        s.ell(25, L + 14, 20, 16, sphere(25, L + 14, 20, 16, base, 0.55, 0.08))
    else:
        s.poly([(10, L), (40, L), (40, L + 34), (10, L + 34)], base * 0.9)
        for k in range(4):
            s.line([(14 + k * 7, L + 4), (14 + k * 7, L + 30)], 2, base * 0.6)
    return s


def kettle(w, r):
    h = w * 0.8
    base = jit(hexc(r.choice(["#ad7d5e", "#aeaea8", "#8ea2ae", "#a98c5a"])), r, 0.03)
    s = Spr(w * 1.6, h + 60)
    cx, cy = s.w / 2, 40 + h * 0.55
    s.line([(cx - w * 0.35, cy - h * 0.25), (cx - w * 0.2, 14), (cx + w * 0.2, 14), (cx + w * 0.35, cy - h * 0.25)], 5, base * 0.7)
    s.poly([(cx + w * 0.35, cy), (cx + w * 0.75, cy - h * 0.45), (cx + w * 0.8, cy - h * 0.4), (cx + w * 0.42, cy + h * 0.15)], base * 0.85)
    s.ell(cx, cy, w / 2, h / 2, sphere(cx, cy, w / 2, h / 2, base, 0.5, 0.12))
    s.ell(cx, cy - h / 2, w * 0.15, 6, base * 0.7)
    return s


CABLE = ["#4f4c48", "#5a5752", "#a8743f", "#b5a04e", "#5b6f86", "#8e5048", "#6e8a5c", "#c8c2b0", "#55504a"]


def cable_coil(R, r, col=None, tail=True):
    col = hexc(col or r.choice(CABLE))
    cw = r.uniform(5, 8)
    pad = cw + 14
    tl = r.uniform(R * 1.5, R * 3.2) if tail else 0
    s = Spr(2 * R * 1.25 + 2 * pad, 2 * R * 1.2 + 2 * pad + tl)
    cx, cy = s.w / 2, pad + R * 1.15
    loops = []
    for k in range(int(r.integers(6, 12))):
        rx, ry = R * r.uniform(0.85, 1.08), R * r.uniform(0.95, 1.15)
        ox, oy = r.normal(0, R * 0.05), r.normal(0, R * 0.04) + (ry - R)
        ph = r.uniform(0, 2 * np.pi)
        loops.append([(cx + ox + rx * np.sin(t), cy + oy - ry * np.cos(t)) for t in np.linspace(ph, ph + 2 * np.pi, 60)])
    for ln in loops:
        s.put(s.mlines([ln], cw + 2.5), col * 0.6)
        s.put(s.mlines([ln], cw), col)
        s.put(s.mlines([[(x - cw * 0.22, y - cw * 0.22) for x, y in ln]], cw * 0.3), np.clip(col * 1.35 + 0.05, 0, 1), 0.6)
    if tail:
        x0, y0 = cx + R * 0.6, cy + R * 0.9
        pts = [(x0 + r.normal(0, 4) * k * 0.4 + 6 * np.sin(k * 0.7), y0 + k * tl / 10) for k in range(11)]
        s.put(s.mlines([pts], cw + 2.5), col * 0.6)
        s.put(s.mlines([pts], cw), col)
        s.ell(*pts[-1], cw * 0.9, cw * 1.4, hexc("#8a8478"))
    s.poly([(cx - 9, cy - R * 1.15 - 8), (cx + 9, cy - R * 1.15 - 8), (cx + 9, cy - R * 1.15 + 10), (cx - 9, cy - R * 1.15 + 10)], hexc(r.choice(["#b5a04e", "#8a8478", "#8e5048"])))
    return s


def cable_bundle(L, r):
    """Loose lengths of wire hung over a nail, falling straight."""
    s = Spr(90, L + 20)
    for k in range(int(r.integers(6, 14))):
        col = hexc(r.choice(CABLE))
        x0 = 45 + r.normal(0, 4)
        x1 = 45 + r.normal(0, 18)
        l = L * r.uniform(0.55, 1.0)
        pts = [(x0 + (x1 - x0) * t + 3 * np.sin(t * 9 + k), 6 + l * t) for t in np.linspace(0, 1, 16)]
        w = r.uniform(3, 6)
        s.put(s.mlines([pts], w + 1.5), col * 0.6)
        s.put(s.mlines([pts], w), col)
    for y in (20, L * 0.35):
        s.poly([(30, y), (60, y), (60, y + 8), (30, y + 8)], hexc("#3f3c39"))
    return s


def board(w, h, r):
    """A salvaged circuit board."""
    kind = r.choice(["green", "green", "blue", "brown", "red"])
    base = jit(hexc({"green": "#6a8263", "blue": "#68797f", "brown": "#a38a5c", "red": "#8d6156"}[kind]), r, 0.04)
    s = Spr(w, h)
    s.poly([(0, 0), (w, 0), (w, h), (0, h)], flat(base, r, 0.06, "mott"))
    trace = np.clip(base * 1.25 + 0.03, 0, 1)
    lines = []
    for _ in range(int(w * h / 900)):
        x, y = r.uniform(6, w - 6), r.uniform(6, h - 6)
        pts = [(x, y)]
        for _ in range(int(r.integers(2, 5))):
            if r.random() < 0.5:
                x = np.clip(x + r.normal(0, w * 0.25), 5, w - 5)
            else:
                y = np.clip(y + r.normal(0, h * 0.25), 5, h - 5)
            pts.append((x, y))
        lines.append(pts)
    s.put(s.mlines(lines, 1.8, caps=False), trace, 0.8)
    for pts in lines:
        s.ell(*pts[-1], 2.6, 2.6, hexc("#c4b07a"))
    for _ in range(int(w * h / 5000) + 1):                      # chips
        cw_, ch_ = r.uniform(18, 50), r.uniform(12, 30)
        x, y = r.uniform(4, max(5, w - cw_ - 4)), r.uniform(4, max(5, h - ch_ - 4))
        for k in np.arange(x + 3, x + cw_ - 2, 5):
            s.poly([(k, y - 3), (k + 2, y - 3), (k + 2, y + ch_ + 3), (k, y + ch_ + 3)], hexc("#b8b4aa"))
        s.poly([(x, y), (x + cw_, y), (x + cw_, y + ch_), (x, y + ch_)], hexc("#4c4a48"))
        s.put(s.mlines([[(x + 1, y + 1), (x + cw_ - 1, y + 1)]], 1.2), hexc("#6a6866"))
        if r.random() < 0.5:
            ln, _ = glyph_lines(x + 4, y + ch_ * 0.35, ch_ * 0.3, 4, r, words=False)
            s.put(s.mlines(ln, 1.0), hexc("#8a8884"), 0.7)
    for _ in range(int(w * h / 3000) + 1):                      # capacitors and resistors
        x, y = r.uniform(8, w - 8), r.uniform(8, h - 8)
        if r.random() < 0.5:
            rr = r.uniform(4, 9)
            col = hexc(r.choice(["#4e5f78", "#3f3f40", "#7a6a3a", "#5d7a4a"]))
            s.ell(x, y, rr, rr, sphere(x, y, rr, rr, col, 0.55, 0.15))
        else:
            s.poly([(x, y), (x + 14, y), (x + 14, y + 5), (x, y + 5)], hexc("#c4b090"))
            for k in (3, 7, 10):
                s.line([(x + k, y), (x + k, y + 5)], 1.2, hexc(r.choice(["#8a3f35", "#3f3f40", "#a8743f"])))
    if r.random() < 0.6:                                        # gold fingers along one edge
        for k in np.arange(8, w - 8, 7):
            s.poly([(k, h - 14), (k + 4, h - 14), (k + 4, h - 2), (k, h - 2)], hexc("#b9a062"))
    for (x, y) in ((7, 7), (w - 7, 7), (7, h - 7), (w - 7, h - 7)):
        s.ell(x, y, 3.5, 3.5, hexc("#3e3c3a"))
    s.put(s.mlines([[(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1), (0, 0)]], 2), base * 0.7)
    s.acc |= s.a > 0.5
    return s


def fan(R, r):
    s = Spr(2 * R + 10, 2 * R + 10)
    c = s.w / 2
    frame = jit(hexc(r.choice(["#8e8b84", "#4e4c4a", "#b0aa98"])), r, 0.04)
    s.poly([(4, 4), (s.w - 4, 4), (s.w - 4, s.h - 4), (4, s.h - 4)], flat(frame, r, 0.05))
    s.ell(c, c, R * 0.92, R * 0.92, hexc("#4c4a47"))
    ph = r.uniform(0, 2 * np.pi)
    for k in range(int(r.integers(3, 8))):
        a = ph + k * 2 * np.pi / 7
        pts = [(c + R * 0.2 * np.cos(a), c + R * 0.2 * np.sin(a)), (c + R * 0.88 * np.cos(a - 0.15), c + R * 0.88 * np.sin(a - 0.15)),
               (c + R * 0.88 * np.cos(a + 0.35), c + R * 0.88 * np.sin(a + 0.35))]
        s.poly(pts, frame * 0.85)
    s.ell(c, c, R * 0.24, R * 0.24, sphere(c, c, R * 0.24, R * 0.24, frame * 0.9, 0.5))
    for k in range(1, 5):
        rr = R * k / 4.4
        s.put(s.mlines([[(c + rr * np.cos(t), c + rr * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 48)]], 1.5), METAL, 0.8)
    for (x, y) in ((12, 12), (s.w - 12, 12), (12, s.h - 12), (s.w - 12, s.h - 12)):
        s.ell(x, y, 4, 4, hexc("#3e3c3a"))
    return s


def gear(R, r):
    s = Spr(2 * R + 16, 2 * R + 16)
    c = s.w / 2
    base = jit(hexc(r.choice(["#8e8b84", "#9a8a6a", "#7a7670"])), r, 0.04)
    nt = int(R / 7)
    pts = []
    for k in range(nt * 4):
        a = k * 2 * np.pi / (nt * 4)
        rr = R + (7 if (k % 4) in (1, 2) else 0)
        pts.append((c + rr * np.cos(a), c + rr * np.sin(a)))
    s.poly(pts, sphere(c, c, R * 1.6, R * 1.6, base, 0.65))
    s.ell(c, c, R * 0.62, R * 0.62, base * 0.85)
    s.ell(c, c, R * 0.22, R * 0.22, hexc("#4a4642"))
    Y, X = s.grid()
    s.rgb = mix(s.rgb, hexc("#8f6146"), smooth(tex("mott", Y, X, toff(r)), 0.55, 0.75) * 0.6)
    return s


def valve(r):
    w, h = r.uniform(26, 34), r.uniform(60, 80)
    s = Spr(w + 10, h + 40)
    cx = s.w / 2
    s.line([(cx, 0), (cx, 14)], 2, TWINE)
    s.poly([(cx - w / 2, 14), (cx + w / 2, 14), (cx + w / 2, 30), (cx - w / 2, 30)], hexc("#45423f"))
    glass = hexc("#c4c6bc")
    s.poly([(cx - w / 2, 30)] + [(cx - w / 2 + 0, 30 + t * h) for t in np.linspace(0, 1, 4)] +
           [(cx + w / 2 * np.cos(a), 30 + h + w / 2 * np.sin(a) * 0.9) for a in np.linspace(np.pi, 0, 10)] +
           [(cx + w / 2, 30)], glass, 0.75)
    s.poly([(cx - w * 0.25, 40), (cx + w * 0.25, 40), (cx + w * 0.25, 30 + h * 0.75), (cx - w * 0.25, 30 + h * 0.75)], hexc("#6e6a64"), 0.85)
    s.line([(cx - w * 0.32, 34), (cx - w * 0.32, 30 + h)], 2.5, hexc("#f0ece0"), 0.7)
    return s


def screen(w, h, r):
    """An old monitor's front, the tube dead."""
    s = Spr(w, h)
    bez = jit(hexc(r.choice(["#b9b3a2", "#8e8b84", "#a8a08a"])), r, 0.03)
    s.poly([(0, 6), (6, 0), (w - 6, 0), (w, 6), (w, h - 6), (w - 6, h), (6, h), (0, h - 6)], flat(bez, r, 0.05, "mott"))
    m = w * 0.1
    sc = [(m, m), (w - m, m), (w - m, h - m * 1.8), (m, h - m * 1.8)]
    s.poly(sc, lambda Y, X, mk: np.clip(hexc("#5f6a62") * (0.85 + 0.25 * np.clip(1 - np.hypot(X - w * 0.4, Y - h * 0.35) / w, 0, 1))[..., None], 0, 1))
    s.line([(w * 0.25, m + 8), (w * 0.45, h * 0.55)], 6, hexc("#9aa49a"), 0.35)
    if r.random() < 0.6:                                         # a crack across the glass
        s.line(jag((m + 10, h * 0.3), (w - m - 6, h * 0.6), 0.1, r), 1.5, hexc("#c8ccc2"), 0.8)
    for k in range(3):
        s.ell(w - m - 10 - k * 18, h - m * 0.9, 4, 4, hexc("#55524d"))
    ln, _ = glyph_lines(m, h - m * 1.2, m * 0.5, 4, r, words=False)
    s.put(s.mlines(ln, 1.5), hexc("#6a665f"), 0.7)
    return s


def headphones(r):
    s = Spr(110, 120)
    col = hexc(r.choice(["#4e4c4a", "#8e5048", "#8a8478"]))
    s.line([(18, 78), (20, 30), (55, 8), (90, 30), (92, 78)], 7, col)
    for x in (18, 92):
        s.ell(x, 86, 16, 22, sphere(x, 86, 16, 22, col * 1.2, 0.5, 0.06))
        s.ell(x, 86, 9, 14, col * 0.7)
    return s


def rug(w, h, r):
    s = Spr(w, h + 50)
    pals = [("#9a5a4c", "#4f5b70", "#c3a36a", "#d8ccb4"), ("#5b6e5a", "#9a5a4c", "#c7b48a", "#d6cbb3"),
            ("#4f5b70", "#a8846a", "#cbb98f", "#d9cfba"), ("#8a5a62", "#5e7466", "#c4a46e", "#d4c8b0"),
            ("#6f8a5e", "#7a4e44", "#c9b07c", "#ddd2bb")]
    field, border, acc_, light = (hexc(c) for c in pals[int(r.integers(len(pals)))])
    K = int(r.choice([5, 6]))                                     # a knot cell, units: the pattern is stepped like weaving
    gw, gh = w // K + 1, h // K + 1
    v, u = np.mgrid[0:gh, 0:gw].astype(f32)
    u, v = u / (gw - 1), v / (gh - 1)
    pat = np.zeros((gh, gw), np.int32)                           # 0 field, 1 border, 2 accent, 3 light
    bw = r.uniform(0.09, 0.14)
    ub = np.minimum(u, 1 - u) * w / h
    vb = np.minimum(v, 1 - v)
    edge = np.minimum(ub, vb)
    pat[edge < bw * 0.8] = 1
    pat[(edge < bw * 0.8) & (edge > bw * 0.25) & (((np.round(u * gw / 2) + np.round(v * gh / 2)) % 4) == 0)] = 2
    pat[(np.abs(edge - bw * 0.85) < 0.012)] = 3
    style = r.integers(2)
    if style == 0:                                               # medallions down the field
        nmed = int(r.integers(1, 4))
        for k in range(nmed):
            cy = 0.5 + (k - (nmed - 1) / 2) * 0.62 / max(1, nmed)
            d = np.abs(u - 0.5) / 0.28 + np.abs(v - cy) / (0.26 / nmed + 0.06)
            pat[(d < 1) & (edge >= bw)] = 2
            pat[(d < 0.62) & (edge >= bw)] = 3
            pat[(d < 0.3) & (edge >= bw)] = 1
            pat[(np.abs(d - 1.15) < 0.06) & (edge >= bw)] = 3
    else:                                                        # bands of zigzag
        nb = int(r.integers(4, 8))
        zig = np.abs(((u * 6) % 2) - 1) * 0.04
        band = ((v - zig) * nb) % 1
        pat[(band < 0.18) & (edge >= bw)] = 2
        pat[(band > 0.45) & (band < 0.55) & (edge >= bw)] = 3
    cols = np.stack([field, border, acc_, light])
    hp = int(round(h * S))                                       # the rug's rows, px (the fringe is below them)
    Y, X = s.grid(h=hp)
    img_ = cols[pat[(Y // K).astype(np.int64), (X // K).astype(np.int64)]]
    off = toff(r)
    img_ = mix(img_, light, 0.18 + 0.15 * tex("mott", Y, X, off))              # faded in the sun
    img_ = img_ * (0.93 + 0.1 * tex("fine", Y, X, off))[..., None]
    knots = (0.95 + 0.05 * ((X // 2 + Y // 3) % 2))
    img_ = img_ * knots[..., None]
    # folds: it hangs from clips, so it bells between them and creases down
    ph1, ph2, p1, p2 = r.uniform(0, 6.3), r.uniform(0, 6.3), r.uniform(60, 110), r.uniform(25, 45)
    f = np.cos(2 * np.pi * X / p1 + ph1) + 0.5 * np.cos(2 * np.pi * X / p2 + ph2)
    img_ = img_ * (1 + (0.05 + 0.05 * (1 - Y / h)) * f)[..., None]
    sag = 6 * np.abs(np.sin(np.pi * X / (w / 3)))
    m = (Y >= sag).astype(f32)
    s.rgb[:hp], s.a[:hp] = img_, m
    # fringe
    for x in np.arange(3, w - 3, 4):
        L = r.uniform(18, 32)
        s.line([(x, h - 2), (x + r.normal(0, 2), h + L)], 2, light * r.uniform(0.85, 1.0))
    s.acc[:hp] = False
    return s


def drape(w, h, r):
    """A length of cloth hung over a rail, folded down in front."""
    s = Spr(w, h)
    col = jit(hexc(r.choice(["#7f9a74", "#a87a6a", "#8a8fb0", "#c9b07c", "#9e6a6e", "#6f8a7a", "#c7c0a8", "#5f7a58"])), r, 0.05)
    p, ph = r.uniform(18, 32), r.uniform(0, 6.3)
    pts = [(0, 0), (w, 0)] + [(w - k * w / 8, h - (r.uniform(0, 0.15) * h if k % 2 else r.uniform(0.0, 0.05) * h)) for k in range(9)]
    stripe = r.random() < 0.5
    sc = jit(hexc(r.choice(["#d6cbb3", "#5b5f6a", "#b5a04e"])), r)

    def fn(Y, X, m):
        f = np.cos(2 * np.pi * X / p + ph + 0.3 * np.sin(Y / 40))
        out = col * (0.85 + 0.15 * f)[..., None]
        if stripe:
            st = (np.abs(((X + 4 * np.sin(Y / 30)) % (w / 3)) - w / 6) < 4)
            out = np.where(st[..., None], sc * (0.85 + 0.15 * f)[..., None], out)
        return np.clip(out, 0, 1)
    s.poly(pts, fn)
    s.put(s.mlines([[(0, 8), (w, 8)]], 5), col * 0.7)
    return s


def bolt(w, h, r, lying=False):
    """A bolt of cloth: a roll, its end showing the turns."""
    col = jit(hexc(r.choice(["#7f9a74", "#a87a6a", "#8a8fb0", "#c9b07c", "#9e6a6e", "#c7c0a8", "#b9a57a", "#6f8a7a"])), r, 0.05)
    if lying:
        s = Spr(h + 20, w + 4)
        c = s.h / 2
        s.poly([(10, 2), (h + 10, 2), (h + 10, w + 2), (10, w + 2)], cylh(c, w / 2, col, 0.55))
        s.ell(h + 10, c, 8, w / 2, col * 0.8)
        for k in range(1, 4):
            s.put(s.mlines([[(h + 10 + 8 * k / 4 * np.cos(t), c + w / 2 * k / 4 * np.sin(t)) for t in np.linspace(-1.5, 1.5, 12)]], 1.2), col * 0.6)
        return s
    s = Spr(w + 4, h + 16)
    c = s.w / 2
    s.poly([(2, 8), (w + 2, 8), (w + 2, h + 8), (2, h + 8)], cylv(c, w / 2, col, 0.5))
    s.ell(c, 8, w / 2, 7, col * 1.05)
    for k in range(1, 4):
        s.put(s.mlines([[(c + w / 2 * k / 4 * np.cos(t), 8 + 7 * k / 4 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 20)]], 1.2), col * 0.75)
    return s


def cage(w, h, r, tenant=True):
    s = Spr(w + 10, h + 50)
    cx = s.w / 2
    top = 40
    dome = w * 0.35
    metal = jit(hexc(r.choice(["#5c5852", "#8a7a52", "#6a5e4e"])), r, 0.04)
    s.line([(cx, 0), (cx, top - dome + 4)], 2.5, metal)
    s.put(s.mlines([[(cx + 7 * np.cos(t), top - dome - 2 + 7 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 20)]], 2.5), metal)
    if tenant:                                                   # a small round creature on its perch
        by = top + h * 0.55
        bc = jit(hexc(r.choice(["#8a7a6a", "#7a8a7a", "#9a8a9a", "#a08a6a"])), r, 0.05)
        s.line([(cx - w * 0.35, by + 22), (cx + w * 0.35, by + 22)], 4, hexc("#8a7458"))
        s.ell(cx, by, w * 0.2, w * 0.18, sphere(cx, by, w * 0.2, w * 0.18, bc, 0.5))
        for e in (-1, 1):
            ex = cx + e * w * 0.075
            s.ell(ex, by - w * 0.04, w * 0.055, w * 0.06, hexc("#e2dcc8"))
            s.ell(ex + 1, by - w * 0.035, w * 0.026, w * 0.03, hexc("#3a3634"))
            s.line([(cx + e * w * 0.12, by - w * 0.14), (cx + e * w * 0.2, by - w * 0.26)], 3, bc * 0.8)
        s.line([(cx - 6, by + w * 0.16), (cx - 6, by + 22)], 2, hexc("#8a7458"))
        s.line([(cx + 6, by + w * 0.16), (cx + 6, by + 22)], 2, hexc("#8a7458"))
    bars = []
    nb = int(w / 13)
    for k in range(nb + 1):
        t = k / nb * 2 - 1
        x = cx + t * w / 2
        dome_pts = [(cx + t * w / 2 * np.cos(a), top - dome * np.sin(a) * np.sqrt(max(0, 1 - 0.0 * t * t))) for a in np.linspace(0, np.pi / 2, 10)]
        dome_pts = [(cx + t * w / 2 * np.cos(a), top - dome * np.sin(a)) for a in np.linspace(0, np.pi / 2, 10)]
        bars.append(dome_pts[::-1] + [(x, top + h)])
    s.put(s.mlines(bars, 2.2, caps=False), metal)
    rings = [[(cx - w / 2, top + f * h), (cx + w / 2, top + f * h)] for f in (0.0, 0.33)]
    s.put(s.mlines(rings, 3), metal * 1.1)
    s.poly([(cx - w / 2 - 4, top + h - 4), (cx + w / 2 + 4, top + h - 4), (cx + w / 2 + 2, top + h + 14), (cx - w / 2 - 2, top + h + 14)], cylv(cx, w / 2 + 4, metal * 1.1, 0.5, 0.06))
    return s


def charm_string(L, r):
    s = Spr(70, L + 40)
    cx = 35
    s.line([(cx, 0), (cx + r.normal(0, 2), L)], 1.8, TWINE * 0.9)
    y = 20
    while y < L:
        k = r.integers(7)
        x = cx + r.normal(0, 1.5)
        if k == 0:                                         # an eye bead
            R = r.uniform(9, 14)
            s.ell(x, y + R, R, R, sphere(x, y + R, R, R, hexc("#5f7f9c"), 0.55, 0.12), acc=True)
            s.ell(x, y + R, R * 0.6, R * 0.6, hexc("#dcd8cc"))
            s.ell(x, y + R, R * 0.35, R * 0.35, hexc("#6f9ab0"), acc=True)
            s.ell(x, y + R, R * 0.16, R * 0.16, hexc("#2f3236"))
            y += 2 * R + 8
        elif k == 1:                                       # a coin
            R = r.uniform(8, 12)
            s.ell(x, y + R, R, R, sphere(x, y + R, R, R, hexc("#b39a5a"), 0.55, 0.15))
            s.ell(x, y + R, 2.5, 2.5, hexc("#4a4642"))
            y += 2 * R + 6
        elif k == 2:                                       # a little hand
            w_, h_ = 22, 30
            col = hexc(r.choice(["#b39a5a", "#aeaea8", "#7f9aa0"]))
            pts = [(x - w_ / 2, y + h_ * 0.4)] + [(x - w_ / 2 + w_ * f, y + (0 if 0.2 < f < 0.8 else h_ * 0.2)) for f in (0.1, 0.3, 0.5, 0.7, 0.9)] + \
                  [(x + w_ / 2, y + h_ * 0.4), (x + w_ * 0.4, y + h_), (x - w_ * 0.4, y + h_)]
            s.poly(pts, sphere(x, y + h_ / 2, w_, h_, col, 0.6, 0.1))
            s.ell(x, y + h_ * 0.6, 4, 4, hexc("#5f7f9c"))
            y += h_ + 8
        elif k == 3:                                       # beads
            for j in range(int(r.integers(3, 7))):
                R = r.uniform(4, 6)
                col = hexc(r.choice(["#b06a4e", "#c4a46a", "#6f8a7a", "#dcd4c0", "#8a5a62"]))
                s.ell(x, y + R, R, R, sphere(x, y + R, R, R, col, 0.55, 0.12), acc=True)
                y += 2 * R
            y += 4
        elif k == 4:                                       # a key
            s.ell(x, y + 8, 7, 7, hexc("#a8925c"))
            s.ell(x, y + 8, 3, 3, hexc("#5a564f"))
            s.line([(x, y + 14), (x, y + 44)], 3.5, hexc("#a8925c"))
            s.line([(x, y + 38), (x + 8, y + 38)], 3, hexc("#a8925c"))
            y += 50
        elif k == 5:                                       # a tassel
            col = jit(hexc(r.choice(["#9a5a4c", "#6f8a5e", "#c4a46a", "#5f7a9c"])), r)
            s.ell(x, y + 6, 6, 6, col)
            for j in range(9):
                s.line([(x, y + 8), (x - 9 + j * 2.2, y + 40 + r.uniform(0, 6))], 1.5, col * r.uniform(0.8, 1.1))
            y += 50
        else:                                              # a small bone
            s.line([(x, y + 4), (x, y + 30)], 5, hexc("#d6ccb4"))
            for yy_ in (y + 4, y + 30):
                s.ell(x - 3, yy_, 4, 4, hexc("#d6ccb4"))
                s.ell(x + 3, yy_, 4, 4, hexc("#d6ccb4"))
            y += 40
    return s


def lantern(r, kind=None, lit=False):
    kind = kind or r.choice(["tin", "paper"])
    if kind == "paper":
        w, h = r.uniform(70, 100), r.uniform(80, 120)
        s = Spr(w + 10, h + 80)
        cx = s.w / 2
        col = jit(hexc(r.choice(["#b06a56", "#c4a46a", "#7f9a74", "#d2c6a8", "#a07a8a"])), r, 0.04)
        s.line([(cx, 0), (cx, 22)], 2, DARKMETAL)
        cy = 22 + h / 2 + 6
        glow = 0.25 if lit else 0.0
        s.ell(cx, cy, w / 2, h / 2, sphere(cx, cy, w / 2, h / 2, np.clip(col * (1 + glow), 0, 1), 0.6 + glow), acc=lit)
        for k in range(1, 6):
            yk = cy - h / 2 + h * k / 6
            half = w / 2 * np.sqrt(max(0, 1 - ((yk - cy) / (h / 2)) ** 2))
            s.line([(cx - half, yk), (cx + half, yk)], 1.3, col * 0.7, 0.8)
        for yk in (cy - h / 2 + 2, cy + h / 2 - 2):
            s.poly([(cx - w * 0.22, yk - 6), (cx + w * 0.22, yk - 6), (cx + w * 0.22, yk + 6), (cx - w * 0.22, yk + 6)], hexc("#4f4b46"))
        for j in range(7):
            s.line([(cx, cy + h / 2 + 6), (cx - 6 + j * 2, cy + h / 2 + 40)], 1.4, col * 0.85)
        return s, (cx, cy) if lit else None
    w, h = r.uniform(44, 60), r.uniform(70, 90)
    s = Spr(w + 20, h + 60)
    cx = s.w / 2
    tin = jit(hexc(r.choice(["#7a7670", "#8a7a52", "#5c5852"])), r, 0.04)
    s.put(s.mlines([[(cx + 6 * np.cos(t), 10 + 6 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 20)]], 2.5), tin)
    s.poly([(cx - 8, 16), (cx + 8, 16), (cx + w / 2 + 6, 34), (cx - w / 2 - 6, 34)], cylv(cx, w / 2 + 6, tin, 0.5, 0.08))
    glass = hexc("#e7dcae") if lit else hexc("#a9ada4")
    s.poly([(cx - w / 2, 34), (cx + w / 2, 34), (cx + w / 2, 34 + h), (cx - w / 2, 34 + h)], cylv(cx, w / 2, glass, 0.75 if lit else 0.55, 0.1), acc=lit)
    if lit:
        s.ell(cx, 34 + h * 0.55, 5, 10, hexc("#f4e8b8"), acc=True)
    for x in (cx - w / 2, cx, cx + w / 2):
        s.line([(x, 34), (x, 34 + h)], 3, tin * 0.9)
    s.poly([(cx - w / 2 - 4, 34 + h), (cx + w / 2 + 4, 34 + h), (cx + w / 2 + 4, 46 + h), (cx - w / 2 - 4, 46 + h)], cylv(cx, w / 2 + 4, tin, 0.5))
    return s, (cx, 34 + h * 0.55) if lit else None


def tag(r, string=40):
    """A price tag on a string, scribbled."""
    w, h = r.uniform(24, 34), r.uniform(36, 48)
    s = Spr(w + 6, h + string + 4)
    cx = s.w / 2
    s.line([(cx + r.normal(0, 3), 0), (cx, string + 6)], 1.2, TWINE * 0.8)
    y0 = string
    pts = [(cx - w / 2 + 6, y0), (cx + w / 2 - 6, y0), (cx + w / 2, y0 + 6), (cx + w / 2, y0 + h), (cx - w / 2, y0 + h), (cx - w / 2, y0 + 6)]
    col = jit(hexc(r.choice(["#d6c79f", "#ddd4bf", "#c9b98e", "#d8c4a8"])), r, 0.03)
    s.poly(pts, flat(col, r, 0.05))
    s.ell(cx, y0 + 7, 2.5, 2.5, col * 0.6)
    ln, _ = glyph_lines(cx - w / 2 + 4, y0 + 15, 10, int(r.integers(2, 4)), r, words=False, aspect=0.6, wobble=0.1)
    s.put(s.mlines(ln, 1.5), hexc(r.choice(["#4a4440", "#7c3e36", "#3f5560"])), 0.9)
    ln, _ = glyph_lines(cx - w / 2 + 4, y0 + 29, 7, int(r.integers(2, 4)), r, words=False, aspect=0.6, wobble=0.1)
    s.put(s.mlines(ln, 1.2), hexc("#5a524c"), 0.8)
    return rotate(s, r.normal(0, 8))


# ── 5. the foot of the wall ──────────────────────────────────────────────────
def crate(w, h, r, kind=None, stencil=True):
    kind = kind or r.choice(["wood", "wood", "wood", "plastic"])
    s = Spr(w, h)
    if kind == "plastic":
        col = jit(hexc(r.choice(["#8a989c", "#a8807a", "#8a9a80", "#b5a87a", "#959089", "#8394a0"])), r, 0.04)
        s.poly([(0, 4), (4, 0), (w - 4, 0), (w, 4), (w, h), (0, h)], flat(col, r, 0.05, "mott"))
        s.poly([(0, 0), (w, 0), (w, 14), (0, 14)], cylh(7, 8, col * 1.05, 0.6))
        hx0, cw_ = 14, (w - 28) / max(3, int((w - 28) / 34))
        n = int(round((w - 28) / cw_))
        for i in range(n):
            for j in range(int((h - 40) / 38)):
                x, y = hx0 + i * cw_ + 4, 24 + j * 38
                s.poly([(x, y), (x + cw_ - 8, y), (x + cw_ - 8, y + 28), (x, y + 28)], col * 0.55)
                s.poly([(x, y + 22), (x + cw_ - 8, y + 22), (x + cw_ - 8, y + 28), (x, y + 28)], col * 0.8, 0.6)
        s.poly([(w * 0.35, 18), (w * 0.65, 18), (w * 0.65, 28), (w * 0.35, 28)], col * 0.45)
        Y, X = s.grid()
        s.rgb *= (0.88 + 0.12 * tex("mott", Y, X, toff(r)) - 0.08 * Y / h)[..., None]
        s.wood = True
        return s
    nsl = int(r.integers(3, 5))
    post = r.uniform(18, 26)
    gap = r.uniform(7, 14)
    sh = (h - gap * (nsl - 1)) / nsl
    s.poly([(0, 0), (w, 0), (w, h), (0, h)], hexc("#5f564c"))                  # the dark inside, through the gaps
    tone = jit(hexc(r.choice(WOOD)), r, 0.04)
    for k in range(nsl):
        y0 = k * (sh + gap)
        c = jit(tone, r, 0.03)
        s.poly([(0, y0), (w, y0 + r.normal(0, 1)), (w, y0 + sh), (0, y0 + sh)], wood_fn(c, r, "x", 0.3))
        s.put(s.mlines([[(0, y0 + 1), (w, y0 + 1)]], 1.5), np.clip(c * 1.15, 0, 1), 0.8)
        s.put(s.mlines([[(0, y0 + sh - 1), (w, y0 + sh - 1)]], 2), c * 0.7, 0.8)
    if r.random() < 0.1:                                           # something living in it, looking out
        k = int(r.integers(nsl - 1))
        ex, ey = r.uniform(post + 20, w - post - 40), (k + 1) * sh + k * gap + gap / 2
        for e in (0, 1):
            s.ell(ex + e * 16, ey, 4.5, min(4.5, gap * 0.4), hexc("#d8cc8a"), acc=True)
            s.ell(ex + e * 16 + 1, ey, 1.6, min(3, gap * 0.3), hexc("#3a3430"))
    for x0 in (0, w - post):
        s.poly([(x0, 0), (x0 + post, 0), (x0 + post, h), (x0, h)], wood_fn(jit(tone, r, 0.05) * 0.94, r, "y"))
        s.put(s.mlines([[(x0 + post - 1, 0), (x0 + post - 1, h)]], 2), tone * 0.7)
        for k in range(nsl):
            y0 = k * (sh + gap) + sh / 2
            s.ell(x0 + post / 2, y0, 2.5, 2.5, hexc("#4f4842"))
            s.ell(x0 + post / 2 + 1, y0 + 3, 1, 4, hexc("#8a6248"), 0.5)
    if stencil:
        ink = hexc(r.choice(["#4f4842", "#7c4a3e", "#4a5a62"]))
        sz = sh * 0.6
        ln, tw = glyph_lines(0, 0, sz, int(r.integers(2, 5)), r, words=False, aspect=0.7)
        ox, oy = post + (w - 2 * post - tw) / 2, (sh - sz) / 2 + (sh + gap) * int(r.integers(nsl))
        m = s.mlines([[(x + ox, y + oy) for x, y in l] for l in ln], max(3, sz * 0.14))
        if m is not None and r.random() < 0.6:
            y0, x0, mk = m
            mk = mk * (((np.arange(mk.shape[1]) + x0) / S) % 9 > 1)[None, :]     # the stencil's bridges
            m = (y0, x0, mk)
        s.put(m, ink, 0.55)
    Y, X = s.grid()
    s.rgb *= (0.9 + 0.12 * tex("mott", Y, X, toff(r)))[..., None]
    s.wood = True                                                  # the marks: claws rake a crate's face
    return s


def heap(w, r, kind):
    """What shows over a crate's rim: produce, parts, cable, boards."""
    s = Spr(w, 120)
    if kind == "produce":
        col = hexc(r.choice(["#c08a4e", "#9aa064", "#b0604a", "#c9b06a", "#8a5a62", "#a8a050"]))
        for _ in range(int(w / 12)):
            x = r.uniform(14, w - 14)
            R = r.uniform(13, 19)
            y = 120 - R * 0.5 - r.uniform(0, 26) * (1 - abs(x / w - 0.5) * 1.6)
            c = jit(col, r, 0.07)
            s.ell(x, y, R, R * 0.95, sphere(x, y, R, R, c, 0.5, 0.07), acc=True)
    elif kind == "parts":
        for _ in range(int(w / 30)):
            x = r.uniform(10, w - 40)
            g = gear(r.uniform(14, 26), r) if r.random() < 0.5 else valve(r)
            s.blit(g, x, 120 - g.h * r.uniform(0.4, 0.8))
    elif kind == "boards":
        for _ in range(int(w / 50) + 1):
            b = rotate(board(int(r.uniform(60, 110)), int(r.uniform(80, 120)), r), r.normal(0, 12))
            s.blit(b, r.uniform(0, w - b.w), 120 - b.h * r.uniform(0.5, 0.8))
    else:
        for _ in range(2):
            c = cable_coil(r.uniform(26, 40), r, tail=False)
            s.blit(c, r.uniform(0, w - c.w), 120 - c.h * 0.55)
    return s


SPICE = ["#c4a04a", "#b2603e", "#8a5a50", "#7d8a52", "#a0763e", "#c8b070", "#9a4a3a", "#6f6a5a", "#b88a4a"]


def sack(w, h, r, spice=None, open_=True):
    """A burlap sack slumped on the street: open, its neck rolled down on a heap of
    spice, or tied shut."""
    s = Spr(w * 1.25 + 20, h + 110)
    cx = s.w / 2
    top = 100
    burlap = jit(hexc(r.choice(["#ad9670", "#a38c68", "#b8a27c", "#9c8a6c"])), r, 0.04)
    off = toff(r)
    ph = r.uniform(0, 6.3)

    def cloth(Y, X, m, k=1.0):
        wv = 0.92 + 0.08 * (np.sin(X * 2 * np.pi / 5) * np.sin(Y * 2 * np.pi / 5))
        nx = np.clip((X - cx) / (w * 0.58), -1, 1)
        cyl = 0.62 + 0.38 * np.sqrt(1 - nx * nx) - 0.12 * nx
        crease = 1 - 0.10 * np.exp(-((X - cx - 0.25 * w * np.sin((Y - top) / h * 3 + ph)) / 7) ** 2) \
                   - 0.08 * np.exp(-((X - cx + 0.3 * w * np.sin((Y - top) / h * 2 + ph * 2)) / 5) ** 2)
        foot = 1 - 0.2 * smooth((Y - top) / h, 0.78, 1.0)
        return np.clip(burlap * k * (wv * cyl * crease * foot * (0.93 + 0.12 * tex("fine", Y, X, off)))[..., None], 0, 1)
    rim = top + 20
    # the body: narrow at the neck, slumped and wide at the foot, its outline lumpy
    lump = r.normal(0, 1, 6)
    body = []
    for t in np.linspace(0, 1, 24):
        half = w / 2 * (0.88 + 0.22 * smooth(t, 0.1, 0.8) - 0.05 * smooth(t, 0.92, 1.0)) * (1 + 0.025 * np.sin(t * 7 + lump[0]))
        body.append((cx - half, rim + (h - 20) * t))
    for t in np.linspace(1, 0, 24):
        half = w / 2 * (0.88 + 0.22 * smooth(t, 0.1, 0.8) - 0.05 * smooth(t, 0.92, 1.0)) * (1 + 0.025 * np.sin(t * 6 + lump[1]))
        body.append((cx + half, rim + (h - 20) * t))
    if open_:
        spice = spice if spice is not None else r.choice(SPICE)
        sc = jit(hexc(spice), r, 0.04)
        hh = r.uniform(48, 80)
        # the inside of the far rim, then the heap, then the near rim rolled down over it
        s.poly([(cx - w * 0.47, rim + 4)] + [(cx + w * 0.47 * np.cos(a), rim + 4 - 16 * np.sin(a)) for a in np.linspace(np.pi, 0, 20)],
               lambda Y, X, m: cloth(Y, X, m, 0.72))
        prof = r.normal(0, 1, 4)
        mound = [(cx - w * 0.45, rim + 8)]
        for a in np.linspace(np.pi, 0, 30):
            bump = 1 + 0.06 * np.sin(3 * a + prof[0]) + 0.04 * np.sin(7 * a + prof[1])
            mound.append((cx + w * 0.45 * np.cos(a), rim + 8 - hh * np.sin(a) ** 0.7 * bump))

        def grain(Y, X, m):
            g = tex("speck", Y, X, off)
            nx = np.clip((X - cx) / (w * 0.45), -1, 1)
            ny = np.clip((rim + 8 - Y) / hh, 0, 1)
            lit_ = 0.78 + 0.22 * (-nx * 0.6 + 0.4) + 0.14 * ny
            return np.clip(sc * (lit_ * (0.86 + 0.28 * g))[..., None], 0, 1)
        s.poly(mound, grain, acc=True)
        if r.random() < 0.5:                                   # a scoop stuck in it
            sx_ = cx + r.uniform(-0.15, 0.15) * w
            s.line([(sx_, rim - hh * 0.55), (sx_ + w * 0.22, rim - hh - 50)], 5, hexc("#9a8458"))
            s.ell(sx_ - 2, rim - hh * 0.45, 15, 9, sphere(sx_ - 2, rim - hh * 0.45, 15, 9, hexc("#aeaea8"), 0.55, 0.1))
        s.poly(body, cloth)
        # the rolled neck: a fat band, wavy, folded
        wav = r.uniform(0, 6.3)
        roll = [(cx - w * 0.5 + 4 * np.sin(wav), rim + 2)] + \
               [(cx + w * 0.5 * u_, rim - 2 + 5 * np.sin(u_ * 5 + wav)) for u_ in np.linspace(-1, 1, 20)] + \
               [(cx + w * 0.52, rim + 26)] + [(cx + w * 0.52 * u_, rim + 26 + 4 * np.sin(u_ * 4 + wav)) for u_ in np.linspace(1, -1, 20)]
        s.poly(roll, lambda Y, X, m: np.clip(cloth(Y, X, m) * (0.92 + 0.14 * np.cos((Y - rim - 12) / 14 * np.pi)
                                                             * (0.8 + 0.2 * np.cos(X / 9)))[..., None], 0, 1))
        s.put(s.mlines([[(cx + w * 0.5 * u_, rim + 26 + 4 * np.sin(u_ * 4 + wav)) for u_ in np.linspace(-1, 1, 20)]], 2.5), burlap * 0.55, 0.8)
        if r.random() < 0.6:
            s.blit(tag(r, string=10), cx - w * 0.38, rim - hh * 0.3)
    else:
        neck = [(cx - w * 0.12, top - 10), (cx + w * 0.12, top - 10), (cx + w * 0.42, rim + 40), (cx - w * 0.42, rim + 40)]
        s.poly(neck, cloth)
        s.poly(body, cloth)
        s.poly([(cx - w * 0.14, top - 14), (cx + w * 0.14, top - 14), (cx + w * 0.14, top - 2), (cx - w * 0.14, top - 2)], TWINE * 0.85)
        s.poly([(cx - w * 0.17, top - 12), (cx - w * 0.12, top - 50), (cx + w * 0.08, top - 54), (cx + w * 0.18, top - 12)], cloth)
    # a stencil on the cloth
    if r.random() < 0.7:
        sz = h * 0.13
        ln, tw = glyph_lines(cx - w * 0.3, rim + h * 0.32, sz, int(r.integers(2, 4)), r, words=False)
        s.put(s.mlines(ln, max(3, sz * 0.15)), hexc(r.choice(["#5a4a44", "#7c4a3e", "#4a5a62"])), 0.45)
        if r.random() < 0.5:
            s.put(s.mlines([[(cx - w * 0.32, rim + h * 0.32 + sz * 1.5), (cx + w * 0.3, rim + h * 0.32 + sz * 1.5)]], 3), hexc("#7c4a3e"), 0.4)
    return s


def bucket(w, h, r):
    s = Spr(w + 30, h + 50)
    cx = s.w / 2
    top = 40
    col = jit(hexc(r.choice(["#8e8b84", "#7f949c", "#a8706a", "#9a9a90"])), r, 0.04)
    s.line([(cx - w / 2, top + 6), (cx, 4), (cx + w / 2, top + 6)], 3, DARKMETAL)
    s.poly([(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.4, top + h), (cx - w * 0.4, top + h)], cylv(cx, w / 2, col, 0.5, 0.08))
    for f in (0.3, 0.7):
        s.put(s.mlines([[(cx - w / 2 + w * 0.1 * f, top + h * f), (cx + w / 2 - w * 0.1 * f, top + h * f)]], 3), col * 0.8)
    s.poly([(cx - w / 2 - 3, top - 4), (cx + w / 2 + 3, top - 4), (cx + w / 2 + 3, top + 5), (cx - w / 2 - 3, top + 5)], col * 1.08)
    return s


def jar(r):
    w, h = r.uniform(30, 46), r.uniform(44, 70)
    s = Spr(w + 6, h + 14)
    cx = s.w / 2
    fill = jit(hexc(r.choice(SPICE + ["#c9b06a", "#a85a3c", "#d0c8b0"])), r, 0.05)
    s.poly([(cx - w / 2, 14), (cx + w / 2, 14), (cx + w / 2, h + 12), (cx - w / 2, h + 12)], cylv(cx, w / 2, fill, 0.6), acc=True)
    s.poly([(cx - w / 2, 14), (cx + w / 2, 14), (cx + w / 2, 14 + h * 0.2), (cx - w / 2, 14 + h * 0.2)], hexc("#c8c8c0"), 0.5)
    s.line([(cx - w * 0.3, 18), (cx - w * 0.3, h + 8)], 3, hexc("#f0ece4"), 0.4)
    s.poly([(cx - w * 0.42, 2), (cx + w * 0.42, 2), (cx + w * 0.42, 14), (cx - w * 0.42, 14)], cylv(cx, w * 0.42, hexc(r.choice(["#a8925c", "#8e8b84", "#8e5048"])), 0.55, 0.1))
    return s


def plank(w, r, h=30):
    s = Spr(w, h)
    c = jit(hexc(r.choice(WOOD)), r, 0.05)
    s.poly([(0, 0), (w, 0), (w, h), (0, h)], wood_fn(c, r, "x"))
    s.put(s.mlines([[(0, 1), (w, 1)]], 2), np.clip(c * 1.18, 0, 1))
    s.put(s.mlines([[(0, h - 2), (w, h - 2)]], 3), c * 0.65)
    return s


# ── 6. the stalls: poles, awnings, ropes ─────────────────────────────────────
def pole(h, r, kind=None):
    kind = kind or r.choice(["wood", "wood", "pipe"])
    w = r.uniform(20, 28)
    s = Spr(w + 16, h)
    cx = s.w / 2
    if kind == "wood":
        c = jit(hexc(r.choice(["#8f7d64", "#9a8668", "#857560"])), r, 0.04)
        off = toff(r)
        s.poly([(cx - w / 2, 0), (cx + w / 2, 0), (cx + w / 2 + 1, h), (cx - w / 2 - 1, h)],
               cylv(cx, w / 2, c, 0.5, 0.0, lambda Y, X: 0.82 + 0.3 * tex("gv", Y, X, off)))
    else:
        c = jit(hexc(r.choice(["#8e8b84", "#7a7670"])), r, 0.04)
        s.poly([(cx - w / 2, 0), (cx + w / 2, 0), (cx + w / 2, h), (cx - w / 2, h)], cylv(cx, w / 2, c, 0.5, 0.1))
        Y, X = s.grid()
        s.rgb = mix(s.rgb, hexc("#8f6146"), smooth(tex("mott", Y, X, toff(r)), 0.55, 0.72) * 0.6 * (s.a > 0))
        for y in r.uniform(100, h - 100, 2):
            s.poly([(cx - w / 2 - 4, y), (cx + w / 2 + 4, y), (cx + w / 2 + 4, y + 22), (cx - w / 2 - 4, y + 22)], cylv(cx, w / 2 + 4, c * 0.95, 0.5, 0.1))
    return s


def lashing(s, cx, y, w, r, n=None):
    """Rope wound round a pole at y."""
    n = n or int(r.integers(4, 8))
    for k in range(n):
        yy_ = y + k * 6
        s.line([(cx - w / 2 - 2, yy_ + 3), (cx + w / 2 + 2, yy_)], 6, ROPE * 0.65)
        s.line([(cx - w / 2 - 2, yy_ + 2), (cx + w / 2 + 2, yy_ - 1)], 4, ROPE * (0.95 - 0.08 * (k % 2)))


def rope(pts, r, width=6, col=None):
    """A twisted rope along pts (absolute tile coordinates); returns (sprite, X, Y)."""
    col = col if col is not None else jit(ROPE, r, 0.04)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    X0, Y0 = int(min(xs)) - 12, int(min(ys)) - 12
    s = Spr(max(xs) - X0 + 12, max(ys) - Y0 + 12)
    lp = [(x - X0, y - Y0) for x, y in pts]
    s.put(s.mlines([lp], width + 2), col * 0.6)
    s.put(s.mlines([lp], width), col)
    # the twist: short dark diagonals along it
    dense = []
    for (a, b) in zip(lp, lp[1:]):
        L = np.hypot(b[0] - a[0], b[1] - a[1])
        for t in np.arange(0, L, width * 0.9):
            dense.append((a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L, (b[0] - a[0]) / L, (b[1] - a[1]) / L))
    hatch = [[(x - ny * width * 0.45 + dx * width * 0.35, y + nx * width * 0.45 + dy * width * 0.35),
              (x + ny * width * 0.45 - dx * width * 0.35, y - nx * width * 0.45 - dy * width * 0.35)]
             for x, y, dx, dy in dense for nx, ny in [(dy, -dx)]]
    s.put(s.mlines(hatch, 1.3, caps=False), col * 0.62, 0.8)
    return s, X0, Y0


def sagline(a, b, sag, n=30):
    return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)) for t in np.linspace(0, 1, n)]


AWNING_STYLES = {
    "rust":   (["#a9705a", "#d4c9b0"], 64),
    "green":  (["#6e8f5f", "#d6ccb4"], 58),
    "ochre":  (["#c2a464", "#d8cfb8", "#c2a464", "#8a9a86"], 30),
    "maroon": (["#8f5c5a", "#d6ccb4", "#6e8f5f", "#d6ccb4"], 44),
    "blue":   (["#7f949c", "#d8d0bc"], 50),
    "olive":  (["#8a8a62", "#cfc6ae"], 72),
}
TARPS = {"canvas-rust": "#a88472", "tarp-blue": "#7d98a6", "tarp-green": "#6f8a68", "tarp-olive": "#8a8762", "canvas-green": "#6f8f60", "canvas-ochre": "#bda56e"}


def awning(W, ytop, supports, val_h, style, r, hem="scallop"):
    """A canvas or a tarp, seen flat on, from the wall at ytop to its front edge,
    which sags between `supports` [(x, y), ...] (local x, tile y). Returns the sprite
    (placed at y = ytop) and the front edge's y at every unit of x."""
    sx = np.array([p[0] for p in supports], f32)
    sy = np.array([p[1] for p in supports], f32)
    sags = r.uniform(18, 46, len(supports) - 1)

    def front(X):
        yb = np.interp(X, sx, sy)
        for k in range(len(supports) - 1):
            t = np.clip((X - sx[k]) / (sx[k + 1] - sx[k]), 0, 1)
            inside = (X >= sx[k]) & (X <= sx[k + 1])
            yb += np.where(inside, sags[k] * 4 * t * (1 - t), 0)
        return yb
    yb = front(np.arange(W, dtype=f32))
    yb_l = yb - ytop
    H = int(yb_l.max() + val_h + 40)
    s = Spr(W, H)
    Y, Xg = s.grid()
    X = Xg[0]                                                   # every px column, in units
    edge = (front(X) - ytop)[None, :]
    tarp = style in TARPS
    # folds, stronger toward the sag
    f = np.zeros(X.shape, f32)
    df = np.zeros(X.shape, f32)
    for k in range(4):
        p, ph, a = r.uniform(40, 160), r.uniform(0, 6.3), r.uniform(0.4, 1.0)
        f += a * np.sin(2 * np.pi * X / p + ph)
        df += a * np.cos(2 * np.pi * X / p + ph) * 40 / p
    disp = 6 * f[None, :] * (Y / np.maximum(edge, 1))
    # it runs out from the wall toward us, so it widens from its top down to its front edge
    inset = r.uniform(0.045, 0.075) * W
    v0 = np.clip(Y / np.maximum(edge, 1), 0, 1)
    xl = inset * (1 - v0)
    Xn = (Xg - xl) * W / (W - 2 * xl)
    if tarp:
        base = hexc(TARPS[style])
        col = np.broadcast_to(base, (s.ph, s.pw, 3)).copy()
    else:
        cols, sw = AWNING_STYLES[style]
        cols = np.stack([hexc(c) for c in cols])
        idx = (np.floor((Xn + disp) / sw).astype(np.int64)) % len(cols)
        col = cols[idx]
    off = toff(r)
    Xi = np.floor(Xg)
    mt, fn_ = tex("mott", Y, Xg, off), tex("fine", Y, Xg, off)
    v = np.clip(Y / np.maximum(edge, 1), 0, 1)
    light = (1.0 + 0.06 * (1 - v) - 0.07 * v * v + (0.05 + 0.08 * v) * np.clip(df[None, :], -1.5, 1.5) / 1.5)
    tt = np.clip((Xg - sx[0]) / max(1, sx[-1] - sx[0]), 0, 1)
    light *= 1 - 0.05 * 4 * tt * (1 - tt) * v * v                              # the belly sags into shade
    col = col * light[..., None]
    col = mix(col, hexc("#ddd4c0"), (0.22 + 0.22 * mt) * (1 - 0.5 * v))         # sun-bleached, most at the top
    col = col * (0.95 + 0.07 * fn_)[..., None]
    canvas = np.clip((edge - Y) * S + 0.5, 0, 1) * np.clip((Xg - xl) * S + 0.5, 0, 1) * np.clip((W - xl - Xg) * S + 0.5, 0, 1)
    side = np.exp(-((Xg - xl) / 3.0) ** 2) + np.exp(-((W - xl - Xg) / 3.0) ** 2)
    col = col * (1 - 0.18 * np.clip(side, 0, 1) * (Y < edge))[..., None]
    # the valance: a flap hanging from the front edge, in shade, with a hem
    if hem == "scallop":
        swl = r.uniform(70, 100)
        u = ((Xg + r.uniform(0, swl)) % swl) / swl
        bottom = edge + val_h - val_h * 0.35 + val_h * 0.35 * np.sqrt(np.clip(1 - (2 * u - 1) ** 2, 0, 1))
    elif hem == "zigzag":
        swl = r.uniform(40, 60)
        u = ((Xg + r.uniform(0, swl)) % swl) / swl
        bottom = edge + val_h - val_h * 0.3 * np.abs(2 * u - 1)
    else:
        bottom = edge + val_h + 3 * np.sin(Xg / 23)
    val = np.clip((bottom - Y) * S + 0.5, 0, 1) * (Y >= edge - 0.5 / S)
    vcol = col * (0.84 + 0.06 * np.sin(2 * np.pi * Xg / r.uniform(30, 50)))[..., None]
    if tarp:
        vcol = col * 0.9
    out = np.where((Y < edge)[..., None], col, vcol)
    crease = np.exp(-((Y - edge) / 2.0) ** 2)
    out = out * (1 - 0.25 * crease)[..., None] * (1 + 0.1 * np.exp(-((Y - edge + 4) / 2.0) ** 2))[..., None]
    hemline = (np.abs(Y - (bottom - 7)) < 1.0) & ((Xi // 7) % 2 == 0)
    out = np.where(hemline[..., None], out * 1.12, out)
    out = np.where((np.abs(Y - (edge + 5)) < 1.0)[..., None] & ((Xi // 7) % 2 == 0)[..., None], out * 1.12, out)
    a = np.maximum(canvas, val)
    # stains: tide marks where the rain sat
    ring = np.exp(-((mt - 0.62) / 0.008) ** 2) * smooth(v, 0.3, 0.9)
    out = out * (1 - 0.12 * ring - 0.06 * smooth(mt, 0.62, 0.7) * v)[..., None]
    s.rgb, s.a = np.clip(out, 0, 1).astype(f32), a.astype(f32)
    # patches: a square of other cloth stitched over a tear
    for _ in range(int(r.integers(1, 4))):
        pw, ph_ = r.uniform(50, 130), r.uniform(40, 110)
        px = r.uniform(10, W - pw - 10)
        ex = int(min(W - 1, max(0, px + pw / 2)))
        py = r.uniform(max(5, yb_l[ex] * 0.25), max(10, yb_l[ex] - ph_ - 5))
        if style in TARPS:
            pc = hexc(r.choice(["#9a9890", "#8e8b84", "#a8a59a"]))           # tape
        else:
            pc = jit(hexc(r.choice(["#a9705a", "#6e8f5f", "#c2a464", "#7f949c", "#d6ccb4", "#8f5c5a"])), r, 0.04)
            pc = mix(pc, hexc("#ddd4c0"), 0.25)
        ang = r.normal(0, 0.06)
        cs, sn = np.cos(ang), np.sin(ang)
        quad = [(px + dx * cs - dy * sn, py + dx * sn + dy * cs) for dx, dy in ((0, 0), (pw, 0), (pw, ph_), (0, ph_))]
        s.poly(quad, flat(pc, r, 0.06, "mott"))
        s.put(s.mlines([quad + [quad[0]]], 2.5), pc * 0.75)
        if style not in TARPS:
            inner = [(x + (px + pw / 2 - x) * 0.12, y + (py + ph_ / 2 - y) * 0.12) for x, y in quad]
            dash = []
            for (p, q) in zip(inner, inner[1:] + inner[:1]):
                L = np.hypot(q[0] - p[0], q[1] - p[1])
                for t in np.arange(0, L - 4, 9):
                    dash.append([(p[0] + (q[0] - p[0]) * t / L, p[1] + (q[1] - p[1]) * t / L),
                                 (p[0] + (q[0] - p[0]) * (t + 5) / L, p[1] + (q[1] - p[1]) * (t + 5) / L)])
            s.put(s.mlines(dash, 1.4, caps=False), np.clip(pc * 1.25, 0, 1), 0.9)
    # grommets on a tarp, creases pulled from them
    if tarp:
        for x in np.arange(r.uniform(20, 50), W - 10, r.uniform(70, 110)):
            ex = int(x)
            y = yb_l[ex] + val_h * 0.5
            for k in range(3):
                s.line([(x, y), (x + r.normal(0, 40), y - r.uniform(50, 160))], 2.5, base * 0.78, 0.55)
            s.ell(x, y, 7, 7, METAL * 1.1)
            s.ell(x, y, 3.5, 3.5, hexc("#4a4642"))
    # tears: a few rips in the valance, showing what is behind
    for _ in range(int(r.integers(0, 3))):
        x = r.uniform(20, W - 20)
        y = yb_l[int(x)] + val_h * r.uniform(0.3, 0.8)
        L = r.uniform(12, 30)
        s.cut(s.mpoly([[(x, y - L * 0.6), (x + 6, y), (x + 2, y + L), (x - 5, y + 2)]]))
    return s, yb


# ── layout: seven stalls along the wall, each a different trade ──────────────
print("stalls", flush=True)
BOUNDS = [0, 620, 1250, 1760, 2380, 2990, 3560, 4320]
TYPES = ["spice", "boards", "baskets", "cloth", "pots", "cages", "salvage"]
AWN = [  # style, top of the awning (0: it runs off the top of the sheet), valance, hem
    ("rust", 0, 70, "scallop"),
    ("tarp-blue", 0, 26, "straight"),
    ("ochre", 150, 56, "zigzag"),
    ("green", 0, 74, "scallop"),
    ("canvas-rust", 0, 50, "straight"),
    ("maroon", 140, 60, "scallop"),
    ("tarp-olive", 0, 28, "straight"),
]

pole_x = []
POLES = []                  # (the pole's middle, its top, its width): vines climb them
fronts = {}
for i, (a, b) in enumerate(zip(BOUNDS, BOUNDS[1:])):
    r = np.random.default_rng(SEED * 100 + i)
    style, ytop, vh, hem = AWN[i]
    over = 26
    x0, W = a - over, b - a + 2 * over
    ys = [r.uniform(380, 470) if ytop == 0 else r.uniform(480, 540) for _ in range(3)]
    sup = [(over, ys[0]), ((b - a) / 2 + over + r.normal(0, 40), ys[1] + r.uniform(-20, 20)), (W - over, ys[2])]
    if (b - a) < 600:
        sup = [sup[0], sup[2]]
    s, yb = awning(W, ytop, sup, vh, style, r, hem)
    L_AWN.add(s, x0, ytop)
    fronts[i] = (x0, yb, vh)
    # the batten an awning hangs from, when it hangs from the wall below the top
    if ytop > 0:
        bt = plank(W + 20, r, 26)
        L_FIX.add(bt, x0 - 10, ytop - 16)
        for k in np.linspace(30, W - 10, 5):
            L_FIX.add(rope(sagline((x0 + k, ytop + 4), (x0 + k + r.normal(0, 8), ytop - 6), 0, 3), r, 5)[0], x0 + k - 12, ytop - 18)
    pole_x.append(a)

# poles at the stalls' corners, from the awnings' front edge down to the street
for i, px in enumerate(pole_x):
    r = np.random.default_rng(int(px) + 7)
    x0, yb, vh = fronts[i]
    xp, ybp, _ = fronts[(i - 1) % len(fronts)]
    top = int(min(yb[int(px - x0)], ybp[int((px - xp) % NW)]) - 24)
    p = pole(FLOOR + 30 - top, r)
    lashing(p, p.w / 2, 26 + r.uniform(0, 20), 24, r)
    lashing(p, p.w / 2, 700 + r.uniform(0, 500), 24, r, 3)
    X = px - p.w / 2 + r.normal(0, 4)
    L_POLE.add(p, X, top)
    POLES.append((X + p.w / 2, top, p.w - 16))

# ── what each stall sells ───────────────────────────────────────────────────


def hooks_rail(a, b, y, r):
    L_FIX.add(rail(b - a, r), a, y)


def dress_spice(a, b, r):
    yv = 560
    hooks_rail(a + 20, b - 20, yv, r)
    # chillies, garlic, herbs along the rail, a long chilli string over the margin
    L_GOODS.add(chilli_string(900, r), a + 40, yv + 10)
    L_GOODS.add(garlic_braid(560, r), a + 130, yv + 10)
    L_GOODS.add(chilli_string(520, r, "pod"), a + 220, yv + 10)
    for k in range(3):
        L_GOODS.add(herb_bunch(r), a + 320 + k * 70, yv + 14)
    L_GOODS.add(chilli_string(700, r), b - 130, yv + 10)
    L_GOODS.add(garlic_braid(380, r), b - 60, yv + 10)
    L_GOODS.add(hung(sign(220, 90, r, 0), 40, r), a + 300, yv + 260)
    L_GOODS.add(basket(110, 70, r, handle=True), a + 330, 1320)
    # the counter: crates under a plank, jars on it; open sacks along the foot
    cx = a + 30
    while cx < b - 160:
        cw_ = r.uniform(170, 220)
        L_BACK.add(crate(int(cw_), int(r.uniform(190, 230)), r), cx, 1700)
        L_BACK.add(crate(int(cw_), int(r.uniform(190, 230)), r), cx, 1700 + 220)
        cx += cw_ + r.uniform(4, 14)
    L_BACK.add(plank(b - a - 30, r, 34), a + 15, 1670)
    x = a + 30
    while x < b - 70:
        j = jar(r)
        L_BACK.add(j, x, 1670 - j.h + 4)
        x += j.w + r.uniform(4, 16)
    x = a + 10
    while x < b - 100:
        w = r.uniform(160, 210)
        s = sack(int(w), int(r.uniform(200, 250)), r)
        L_FRONT.add(s, x - w * 0.12, FLOOR + 14 - s.h)
        x += w * r.uniform(0.95, 1.08)


def dress_boards(a, b, r):
    pb = pegboard(b - a - 70, 820, r)
    L_FIX.add(pb, a + 35, 560)
    x0, y0 = a + 55, 600
    for row in range(5):
        x = x0 + r.uniform(0, 30)
        while x < b - 120:
            w, h = int(r.uniform(90, 190)), int(r.uniform(70, 140))
            bd = rotate(board(w, h, r), r.normal(0, 5))
            L_GOODS.add(bd, x, y0 + row * 160 + r.normal(0, 8))
            x += bd.w + r.uniform(10, 40)
    for k in range(3):
        L_GOODS.add(cable_coil(r.uniform(45, 70), r), a + 40 + k * 190, 470)
    L_GOODS.add(cable_bundle(780, r), b - 100, 520)
    L_GOODS.add(hung(sign(200, 80, r, 2), 30, r), a + 120, 1420)
    # crates of boards and parts at the foot
    x = a + 15
    while x < b - 120:
        w = int(r.uniform(180, 240))
        h = int(r.uniform(180, 230))
        L_BACK.add(heap(w, r, r.choice(["boards", "parts", "cable"])), x, FLOOR - 2 * h - 90)
        L_BACK.add(crate(w, h, r), x, FLOOR - 2 * h + 10)
        L_FRONT.add(crate(w, h, r, "plastic" if r.random() < 0.5 else None), x + r.uniform(-20, 20), FLOOR - h + 14)
        x += w + r.uniform(6, 24)
    sc = screen(200, 160, r)
    L_FRONT.add(sc, a + 220, FLOOR - 230 - 160 + 20)


def dress_baskets(a, b, r):
    yv = 640
    L_FIX.add(hung(sign(300, 110, r, 1), 60, r), a + 90, 10)
    hooks_rail(a + 10, b - 10, yv, r)
    x = a + 30
    while x < b - 100:
        w = r.uniform(90, 150)
        bk = basket(int(w), int(w * r.uniform(0.5, 0.75)), r)
        L_GOODS.add(bk, x, yv + 10)
        if r.random() < 0.6:
            bk2 = basket(int(w * 0.8), int(w * 0.5), r, handle=False)
            L_GOODS.add(bk2, x + 10, yv + 10 + bk.h + r.uniform(30, 120))
        x += w + r.uniform(20, 40)
    for k in range(2):                                              # brooms against the wall
        x = a + 150 + k * 220
        s = Spr(80, 900)
        s.line([(40, 0), (40, 640)], 9, cylv(40, 5, hexc("#a08a6a")))
        s.poly([(22, 620), (58, 620), (78, 900), (2, 900)], flat(hexc("#c4ad78"), r, 0.12, "gv"))
        s.put(s.mlines([[(22, 650), (58, 650)], [(18, 690), (62, 690)]], 4), hexc("#8e5048"))
        L_BACK.add(rotate(s, r.uniform(-6, 6)), x, FLOOR - 920)
    x = a + 20
    while x < b - 120:
        w = r.uniform(150, 220)
        bk = basket(int(w), int(w * 0.55), r, handle=r.random() < 0.4, contents=hexc(r.choice(["#c08a4e", "#9aa064", "#b0604a", "#c9b06a"])))
        L_FRONT.add(bk, x, FLOOR + 10 - bk.h)
        x += w + r.uniform(5, 30)
    for k in range(2):
        L_BACK.add(crate(220, 200, r, "plastic"), a + 40 + k * 260, FLOOR - 380)


def dress_cloth(a, b, r):
    yv = 560
    hooks_rail(a + 10, b - 10, yv, r)
    # the big rug hangs over the spine; draped lengths either side
    mid = 2070
    rg = rug(360, 1000, r)
    L_GOODS.add(rg, mid - 180, yv + 20)
    L_GOODS.add(rug(200, 620, r), a + 30, yv + 20)
    x = mid + 200
    while x < b - 60:
        w = int(r.uniform(70, 110))
        L_GOODS.add(drape(w, int(r.uniform(380, 640)), r), x, yv + 6)
        x += w * 0.75
    L_GOODS.add(drape(80, 520, r), a + 235, yv + 6)
    # bolts stood on end and lying on the crates
    x = a + 20
    while x < b - 220:
        w = int(r.uniform(200, 240))
        L_BACK.add(crate(w, 200, r), x, FLOOR - 200 + 10)
        for k in range(3):
            L_BACK.add(bolt(46, w - 30, r, lying=True), x + 5, FLOOR - 200 - 52 * (k + 1) + 10)
        x += w + 10
    x = a + 5
    while x < b - 50:
        bw = int(r.uniform(44, 60))
        L_FRONT.add(bolt(bw, int(r.uniform(300, 460)), r), x, FLOOR + 10 - 470 + r.uniform(0, 140))
        x += bw * r.uniform(0.9, 1.6) + (r.uniform(150, 260) if r.random() < 0.15 else 0)


def dress_pots(a, b, r):
    yv = 520
    hooks_rail(a + 10, b - 10, yv, r)
    hooks_rail(a + 10, b - 10, yv + 380, r)
    x = a + 30
    for row, yr in enumerate((yv, yv + 380)):
        x = a + 25 + row * 40
        while x < b - 80:
            k = r.random()
            if k < 0.35:
                it = pot(int(r.uniform(80, 130)), int(r.uniform(60, 100)), r)
            elif k < 0.6:
                it = pan(int(r.uniform(45, 75)), r)
            elif k < 0.8:
                it = ladle(r)
            else:
                it = kettle(int(r.uniform(70, 100)), r)
            L_GOODS.add(it, x, yr + 10)
            if r.random() < 0.35:
                L_GOODS.add(tag(r, 30), x + it.w * 0.6, yr + 14)
            x += it.w + r.uniform(0, 20)
    L_GOODS.add(hung(sign(240, 90, r, 0), 40, r), a + 200, yv + 760)
    # buckets and stacked pots at the foot, on crates
    x = a + 20
    while x < b - 160:
        w = int(r.uniform(190, 230))
        L_BACK.add(crate(w, 210, r), x, FLOOR - 410)
        p = pot(int(w * 0.6), int(r.uniform(70, 100)), r)
        L_BACK.add(p, x + 20, FLOOR - 410 - p.h + 30)
        L_FRONT.add(crate(w, 200, r), x, FLOOR - 200 + 14)
        x += w + r.uniform(6, 20)
    for k in range(3):
        bk = bucket(int(r.uniform(90, 120)), int(r.uniform(90, 120)), r)
        L_FRONT.add(bk, a + 60 + k * 170 + r.uniform(-20, 20), FLOOR + 12 - bk.h)


def dress_cages(a, b, r):
    yv = 620
    L_FIX.add(hung(sign(280, 100, r, 2), 50, r), a + 150, 0)
    hooks_rail(a + 10, b - 10, yv, r)
    x = a + 30
    for k in range(4):
        w = int(r.uniform(110, 160))
        L_GOODS.add(cage(w, int(w * r.uniform(1.0, 1.3)), r, tenant=(k % 2 == 0)), x, yv + 10 + r.uniform(0, 140))
        x += w + r.uniform(20, 50)
        if x > b - 140:
            break
    for k in range(6):
        L_GOODS.add(charm_string(int(r.uniform(300, 520)), r), a + 40 + k * 85, yv + 380)
    for k in range(2):
        lt, glow = lantern(r, "tin")
        L_GOODS.add(lt, a + 90 + k * 300, yv + 820)
    # cages stacked on crates at the foot
    x = a + 20
    while x < b - 160:
        w = int(r.uniform(180, 230))
        L_BACK.add(crate(w, 220, r), x, FLOOR - 220 + 10)
        if r.random() < 0.7:
            cg = cage(int(w * 0.6), int(w * 0.5), r, tenant=r.random() < 0.5)
            L_BACK.add(cg, x + w * 0.2, FLOOR - 220 - cg.h + 22)
        x += w + r.uniform(4, 20)
    s = sack(150, 200, r, open_=False)
    L_FRONT.add(s, b - 200, FLOOR + 12 - s.h)


def dress_salvage(a, b, r):
    yv = 500
    L_FIX.add(pegboard(380, 520, r), a + 40, 560)
    for k in range(4):
        it = [fan(int(r.uniform(50, 70)), r), gear(int(r.uniform(30, 55)), r), headphones(r), valve(r)][k]
        L_GOODS.add(it, a + 60 + (k % 2) * 170, 600 + (k // 2) * 220)
    for k in range(3):
        L_GOODS.add(board(int(r.uniform(90, 140)), int(r.uniform(70, 110)), r), a + 260 + r.uniform(-10, 10), 600 + k * 150)
    hooks_rail(a + 420, b - 10, yv, r)
    x = a + 440
    while x < b - 60:
        L_GOODS.add(cable_coil(r.uniform(40, 62), r), x, yv + 10)
        x += r.uniform(100, 140)
    L_GOODS.add(cable_bundle(1000, r), b - 270, yv + 20)
    L_GOODS.add(cable_coil(55, r), b - 190, yv + 260)
    L_GOODS.add(hung(sign(260, 100, r, 1), 40, r), a + 100, 1150)
    # screens, crates of parts, a coil on the street
    x = a + 15
    while x < b - 150:
        w = int(r.uniform(190, 240))
        h = int(r.uniform(190, 230))
        L_BACK.add(heap(w, r, r.choice(["parts", "cable", "boards"])), x, FLOOR - 2 * h - 90)
        L_BACK.add(crate(w, h, r), x, FLOOR - 2 * h + 10)
        L_FRONT.add(crate(w, h, r), x + r.uniform(-15, 15), FLOOR - h + 14)
        x += w + r.uniform(6, 20)
    for k in range(2):
        sc = screen(int(r.uniform(160, 210)), int(r.uniform(130, 160)), r)
        L_FRONT.add(sc, a + 80 + k * 360, FLOOR - 230 - sc.h + 30)


DRESS = {"spice": dress_spice, "boards": dress_boards, "baskets": dress_baskets, "cloth": dress_cloth,
         "pots": dress_pots, "cages": dress_cages, "salvage": dress_salvage}
for i, (a, b) in enumerate(zip(BOUNDS, BOUNDS[1:])):
    DRESS[TYPES[i]](a, b, np.random.default_rng(SEED * 1000 + i))

# goods hung from the awnings' front edges: chillies, lanterns, charms, tags
for i, (x0, yb, vh) in fronts.items():
    r = np.random.default_rng(SEED * 77 + i)
    W = len(yb)
    for x in np.arange(r.uniform(60, 140), W - 60, r.uniform(150, 260)):
        y = yb[int(x)] + vh - 10
        k = r.random()
        if k < 0.35:
            lt, glow = lantern(r, lit=r.random() < 0.5)
            L_HANG.add(lt, x0 + x - lt.w / 2, y)
            if glow:
                GLOWS.append((x0 + x - lt.w / 2 + glow[0], y + glow[1], 1.0))
        elif k < 0.55 and TYPES[i] in ("spice", "baskets", "cloth"):
            L_HANG.add(chilli_string(int(r.uniform(200, 360)), r), x0 + x - 60, y)
        elif k < 0.75:
            L_HANG.add(charm_string(int(r.uniform(160, 300)), r), x0 + x - 35, y)
        else:
            for j in range(int(r.integers(1, 4))):
                L_HANG.add(tag(r, int(r.uniform(20, 60))), x0 + x + j * 30, y)

# ropes: from the awnings' corners down to the poles, and to rings in the wall
for i, (x0, yb, vh) in fronts.items():
    r = np.random.default_rng(SEED * 31 + i)
    W = len(yb)
    for side in (0, 1):
        x = 10 if side == 0 else W - 10
        y = yb[int(x)] + vh * 0.5
        dx = (-1 if side == 0 else 1) * r.uniform(30, 90)
        tgt = (x0 + x + dx, y + r.uniform(160, 320))
        pts = sagline((x0 + x, y), tgt, r.uniform(10, 30), 16)
        s, X0, Y0 = rope(pts, r, r.uniform(5, 7))
        L_TOP.add(s, X0, Y0)
        ring = Spr(36, 36)                         # tied off to a ring in the wall
        ring.ell(18, 18, 9, 9, DARKMETAL * 1.2)
        ring.put(ring.mlines([[(18 + 11 * np.cos(t), 20 + 13 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 24)]], 3), METAL * 0.9)
        L_FIX.add(ring, tgt[0] - 18, tgt[1] - 18)
    if r.random() < 0.7:                          # a guy line off the top, slack
        x = r.uniform(80, W - 80)
        y = yb[int(x)]
        pts = sagline((x0 + x, y), (x0 + x + r.uniform(-160, 160), max(10, y - 300)), r.uniform(-40, -10), 16)
        s, X0, Y0 = rope(pts, r, 4.5)
        L_TOP.add(s, X0, Y0)

# ── 7. the bulb strings, swagged between the poles ───────────────────────────
print("bulbs", flush=True)


def bulb_run(anchors, r, spacing, lit_p=0.35, wire=hexc("#4a4640")):
    for (p, q) in zip(anchors, anchors[1:]):
        sag = r.uniform(70, 150)
        pts = sagline(p, q, sag, 40)
        X0 = int(min(p[0], q[0])) - 30
        Y0 = int(min(p[1], q[1])) - 20
        s = Spr(abs(q[0] - p[0]) + 60, max(p[1], q[1]) + sag + 120 - Y0)
        lp = [(x - X0, y - Y0) for x, y in pts]
        s.put(s.mlines([lp], 3.0), wire)
        s.put(s.mlines([[(x - 0.8, y - 1) for x, y in lp]], 1.0), wire * 1.6, 0.5)
        L = sum(np.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(lp, lp[1:]))
        xs_ = np.array([pp[0] for pp in lp])
        ys_ = np.array([pp[1] for pp in lp])
        for x in np.arange(lp[0][0] + spacing * r.uniform(0.3, 0.8), lp[-1][0] - 10, spacing):
            y = float(np.interp(x, xs_, ys_))
            drop = r.uniform(6, 16)
            s.line([(x, y), (x, y + drop)], 2, wire)
            s.poly([(x - 6, y + drop), (x + 6, y + drop), (x + 5, y + drop + 15), (x - 5, y + drop + 15)], cylv(x, 6, hexc("#5a5650"), 0.5, 0.1))
            by = y + drop + 15 + 11
            k = r.random()
            if k < lit_p:
                s.ell(x, by, 10, 13, sphere(x, by, 10, 13, hexc("#f4ebc6"), 0.85, 0.15), acc=True)
                s.ell(x, by + 2, 3, 5, hexc("#fff8dc"), 0.9, acc=True)
                GLOWS.append((X0 + x, Y0 + by, 0.6))
            elif k < 0.92:
                s.ell(x, by, 10, 13, sphere(x, by, 10, 13, hexc("#cfcabb"), 0.55, 0.25))
                s.line([(x, by - 5), (x, by + 4)], 1.2, hexc("#8a8478"), 0.7)
            else:                                    # broken: the filament stem and a shard
                s.line([(x, by - 10), (x, by + 2)], 1.5, hexc("#6a665f"))
                s.poly([(x - 9, by - 8), (x - 2, by - 8), (x - 6, by + 4)], hexc("#c8c6bc"), 0.7)
        L_TOP.add(s, X0, Y0)


r = np.random.default_rng(SEED + 500)
# one run high across the whole tile, one lower, wrapping round
anchor_x = sorted(set(int(x) for x in pole_x))
hi = [(x, r.uniform(60, 130)) for x in anchor_x]
hi = hi + [(hi[0][0] + NW, hi[0][1])]
bulb_run(hi, r, 66, 0.3)
lo_x = [x + r.uniform(-30, 30) for x in BOUNDS[:-1]][::2]
lo = [(x, r.uniform(280, 360)) for x in lo_x] + [(lo_x[0] + NW, 0)]
lo[-1] = (lo[-1][0], lo[0][1])
bulb_run(lo, r, 84, 0.4)

# ── what is pasted and painted on the wall ───────────────────────────────────
print("paper and paint", flush=True)
r = np.random.default_rng(SEED + 600)
spots = []
for (a, b) in zip(BOUNDS, BOUNDS[1:]):
    for _ in range(int(r.integers(3, 6))):
        spots.append((r.uniform(a, b - 150), r.uniform(560, 2100)))
# a few where they show: high in the gaps and low at the foot
spots += [(1290, 220), (3020, 230), (1980, 2180), (3990, 2240), (60, 2120), (2330, 1260), (3700, 1400)]
for (x, y) in spots:
    if r.random() < 0.3:
        L_FLAT.add(scraps(int(r.uniform(150, 300)), int(r.uniform(120, 260)), r), x - 40, y - 30)
    w = int(r.uniform(150, 280))
    h = int(w * r.uniform(1.25, 1.5))
    L_FLAT.add(rotate(poster(w, h, r), r.normal(0, 1.8)), x, y)
    if r.random() < 0.4:                       # pasted over by another
        w2 = int(w * r.uniform(0.7, 1.0))
        L_FLAT.add(rotate(poster(w2, int(w2 * r.uniform(1.2, 1.45)), r), r.normal(0, 2.5)), x + r.uniform(-60, 80), y + r.uniform(-40, 90))
for (x, y, w, h, fat) in [(1310, 2180, 420, 170, True), (3060, 2120, 380, 160, True), (2240, 230, 260, 120, False),
                          (3500, 2200, 260, 120, False), (300, 2050, 300, 140, True), (1050, 1500, 300, 140, False),
                          (2620, 1600, 360, 150, True), (60, 1450, 180, 100, False), (4060, 1850, 240, 120, False),
                          (1890, 1980, 240, 110, False)]:
    L_FLAT.add(graffiti(w, h, r, fat), x, y)
L_FIX.add(conduit(1200, r), 1180, 70)
L_FIX.add(conduit(800, r), 2900, 60)

# ── lay it all down, back to front ───────────────────────────────────────────
for layer in (L_FLAT, L_FIX, L_GOODS, L_BACK, L_FRONT, L_AWN, L_POLE, L_HANG, L_TOP):
    layer.flush()

# ── 8. the Streetwarden's marks ──────────────────────────────────────────────
# What a tracker and the beasts left on the wall, drawn at the page's scale,
# not the wall's, so they read from across a spread. They have a stream of
# their own (`more`), and the wall under them is finished without them (`plain`:
# its mean and its palette are the unmarked wall's), so away from a mark the
# tile is, px for px, the wall as it was. Marks on the wall lie under what
# hangs in front of it (SHOWS, LIT); marks on the crates lie on the crates.
# They fall where they fall: places are drawn at random, where the surface a
# mark needs shows, and clear of each other.
print("marks", flush=True)
plain, accent0 = img.copy(), accent.copy()
more = np.random.default_rng(SEED + 70)
WALL, PAPER, STACK, WOOD = SHOWS["wall"], SHOWS["paper"], SHOWS["stack"], SHOWS["wood"]
B = 8                       # units to a cell of the maps the places are chosen on


def coarse(a):
    b = round(B * S)
    return a[:PH // b * b, :PW // b * b].reshape(PH // b, b, PW // b, b).mean((1, 3))


def seen(m, x, y, w, h):
    """How much of the box w x h round (x, y) the coarse map m gives, round the tile."""
    iy = np.arange(int((y - h / 2) // B), int((y + h / 2) // B) + 1) % m.shape[0]
    ix = np.arange(int((x - w / 2) // B), int((x + w / 2) // B) + 1) % m.shape[1]
    return float(m[np.ix_(iy, ix)].mean())


WALL_, BARE_, PAPER_, STACK_, WOOD_ = coarse(WALL), coarse(WALL * (1 - PAPER)), coarse(PAPER), coarse(STACK), coarse(WOOD)
TAKEN = []


def apart(x, y, pts, sep):
    return all(min(abs(x - px), NW - abs(x - px)) ** 2 + (y - py) ** 2 >= sep * sep for px, py in pts)


def spot(fits, sep, lo=600, hi=FLOOR - 100, tries=4000):
    """A place drawn at random where fits(x, y) holds, sep clear of every mark
    placed so far; None when the wall has no such place left."""
    for _ in range(tries):
        x, y = more.uniform(0, NW), more.uniform(lo, hi)
        if apart(x, y, TAKEN, sep) and fits(x, y):
            TAKEN.append((x, y))
            return x, y
    return None


class Mask:
    """A tile-sized mask of shapes (in units), queued and then drawn at SS x
    with wrap-around, the lightest first, so a heavy mark is never overwritten
    by a faint one."""

    def __init__(self):
        self.q = []

    def poly(self, pts, v=1.0):
        self.q.append((v, 0, [(float(x), float(y)) for x, y in pts]))

    def line(self, pts, w, v=1.0):
        self.q.append((v, w, [(float(x), float(y)) for x, y in pts]))

    def render(self):
        k = S * SS
        im = Image.new("L", (PW * SS, PH * SS), 0)
        d = ImageDraw.Draw(im)
        for v, w, geo in sorted(self.q, key=lambda it: it[0]):
            fill = int(round(255 * min(1.0, max(0.0, v))))
            xs, ys = [p[0] for p in geo], [p[1] for p in geo]
            for ox in (-NW, 0, NW):
                if max(xs) + ox < -w - 2 or min(xs) + ox > NW + w + 2:
                    continue
                for oy in (-NH, 0, NH):
                    if max(ys) + oy < -w - 2 or min(ys) + oy > NH + w + 2:
                        continue
                    pts = [((x + ox) * k, (y + oy) * k) for x, y in geo]
                    if not w:
                        d.polygon(pts, fill=fill)
                        continue
                    wd = max(1, int(round(w * k)))
                    d.line(pts, fill=fill, width=wd, joint="curve")
                    for px, py in (pts[0], pts[-1]):
                        d.ellipse((px - wd / 2, py - wd / 2, px + wd / 2, py + wd / 2), fill=fill)
        return np.asarray(im.resize((PW, PH), Image.BOX), f32) / 255


def relief(h, d):
    """How a height field h catches the light from the upper left: above 0 on
    the slopes that face it, below on those that face away; d in units."""
    return shift(h, -d * S, -d * S) - shift(h, d * S, d * S)


def daub(colour, m, vis, lit):
    """Paint colour (one, or a field of them) through mask m onto a surface that shows by vis, in the shadow lit."""
    global img
    img = mix(img, np.asarray(colour, f32) * lit[..., None], m * vis)


def tone(f, m, vis):
    """Multiply what is under mask m by f."""
    global img
    img *= 1 - (m * vis)[..., None] * (1 - np.asarray(f, f32))


def needle(M, a, b, w, v=1.0):
    """A stroke from a to b, widest in the middle and pointed at both ends."""
    (ax, ay), (bx, by) = a, b
    d = math.hypot(bx - ax, by - ay)
    if d < 0.5:
        return
    nx, ny = -(by - ay) / d, (bx - ax) / d
    ts = np.linspace(0, 1, 9)
    half = [w / 2 * math.sin(np.pi * t) ** 0.4 for t in ts]
    mid = [(ax + (bx - ax) * t, ay + (by - ay) * t) for t in ts]
    M.poly([(px + nx * h, py + ny * h) for (px, py), h in zip(mid, half)] + [(px - nx * h, py - ny * h) for (px, py), h in zip(mid[::-1], half[::-1])], v)


# trail signs: a tracker's way-marks, scratched into the plaster with a claw or
# a knife point. Not the city's script and not paint: pictographs an inch or so
# high, every curve a run of straight cuts, every cut struck one to three times
# and never twice along the same line, overshooting its corners. On the plaster
# a cut is a dirty groove with a pale burr on its lit side; on the dado it took
# the paint off in flakes, down to the plaster.
def chords(cx, cy, rx, ry, a0, a1, n):
    return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(a0, a1, n + 1)]


def peck(x, y, d=0.035):
    """A dot, as a point makes one: two or three short cuts on one spot."""
    return [[(x - d, y - d * 0.3), (x + d, y + d * 0.4)], [(x - d * 0.8, y + d * 0.5), (x + d * 0.9, y - d * 0.5)]]


def s_arrow(r):                 # the way: a shaft and two barbs, and up to three notches cut across the shaft
    out = [[(0.5, 0.97), (0.5, 0.04)], [(0.5, 0.04), (0.22, 0.34)], [(0.5, 0.04), (0.78, 0.34)]]
    return out + [[(0.36, 0.67 + 0.11 * k), (0.64, 0.57 + 0.11 * k)] for k in range(int(r.integers(0, 4)))]


def s_turn(r):                  # the way turns
    return [[(0.18, 0.96), (0.18, 0.32), (0.9, 0.32)], [(0.9, 0.32), (0.66, 0.12)], [(0.9, 0.32), (0.66, 0.52)]]


def s_count(r):                 # a count: notches of uneven length standing on a line, one cut long
    n = int(r.integers(3, 7))
    long_ = int(r.integers(n))
    return [[(0.02, 0.8), (0.98, 0.74)]] + [[(0.18 + 0.72 * k / (n - 1), 0.04 if k == long_ else r.uniform(0.25, 0.45)), (0.09 + 0.72 * k / (n - 1), 0.92)] for k in range(n)]


def s_track(r):                 # a beast's track: the pad a chevron, three or four toes
    return [[(0.22, 0.94), (0.5, 0.64), (0.78, 0.94)]] + [[(0.5 + 0.2 * math.sin(a), 0.52 - 0.2 * math.cos(a)), (0.5 + 0.52 * math.sin(a), 0.52 - 0.5 * math.cos(a))]
                                                         for a in np.linspace(-0.8, 0.8, int(r.integers(3, 5)))]


def s_eye(r):                   # watched: an eye, its pupil, the lashes under it
    return ([chords(0.5, 0.74, 0.55, 0.5, np.pi * 1.18, np.pi * 1.82, 4), chords(0.5, 0.18, 0.55, 0.5, np.pi * 0.18, np.pi * 0.82, 4)] + peck(0.5, 0.46)
            + [[(x, 0.74), (x + (x - 0.5) * 0.4, 0.96)] for x in (0.3, 0.5, 0.7)])


def s_den(r):                   # shelter: an arch on a ground line, something in it
    return [chords(0.5, 0.85, 0.38, 0.72, np.pi, 2 * np.pi, 5), [(0.0, 0.87), (1.0, 0.83)]] + peck(0.5, 0.58)


def s_water(r):                 # water: two or three waves
    n = int(r.integers(2, 4))
    return [[(0.02 + 0.96 * i / 20, 0.5 + 0.24 * (k - (n - 1) / 2) - 0.08 * math.sin(i * np.pi / 4)) for i in range(21)] for k in range(n)]


def s_beast(r):                 # a horned head: a wedge of a skull, two horns, the eyes pecked
    return ([[(0.3, 0.4), (0.5, 0.98), (0.7, 0.4), (0.3, 0.4)], [(0.3, 0.4), (0.1, 0.22), (0.15, 0.02)], [(0.7, 0.4), (0.9, 0.22), (0.85, 0.02)]]
            + peck(0.42, 0.54, 0.025) + peck(0.58, 0.54, 0.025))


def s_fangs(r):                 # danger: a jaw line and the teeth hanging from it
    n = int(r.integers(2, 5))
    xs = [0.2 + 0.6 * k / (n - 1) for k in range(n)]
    return [[(0.03, 0.2), (0.5, 0.3), (0.97, 0.2)]] + [[(x - 0.08, 0.29), (x, 0.92 - 0.5 * abs(x - 0.5)), (x + 0.08, 0.29)] for x in xs]


def s_sun(r):                   # by day: a ring and the rays over it
    a0 = r.uniform(0, 1)
    return [chords(0.5, 0.64, 0.26, 0.26, a0, a0 + 2 * np.pi, 8)] + [[(0.5 + 0.34 * math.cos(a), 0.64 + 0.34 * math.sin(a)), (0.5 + 0.56 * math.cos(a), 0.64 + 0.56 * math.sin(a))]
                                                                    for a in np.linspace(-np.pi * 0.95, -np.pi * 0.05, int(r.integers(4, 7)))]


def s_coil(r):                  # a coil, wound outward
    a0 = r.uniform(0, 2 * np.pi)
    return [[(0.5 + (0.05 + 0.43 * t) * math.cos(a0 + 4.3 * np.pi * t), 0.5 + (0.05 + 0.43 * t) * math.sin(a0 + 4.3 * np.pi * t)) for t in np.linspace(0, 1, 19)]]


WAYS, SIGNS = [s_arrow, s_arrow, s_turn], [s_count, s_track, s_eye, s_den, s_water, s_beast, s_fangs, s_sun, s_coil]
SCR = Mask()


def scratch(lines, x, y, size, rot, w):
    """Cut a sign's strokes (given in its unit box) size high at (x, y), turned by rot."""
    ca, sa = math.cos(rot), math.sin(rot)
    for ln in lines:
        P = [(x + size * ((px - 0.5) * ca - (py - 0.5) * sa), y + size * ((px - 0.5) * sa + (py - 0.5) * ca)) for px, py in ln]
        for (px, py), (qx, qy) in zip(P, P[1:]):
            d = math.hypot(qx - px, qy - py)
            ux, uy = (qx - px) / d, (qy - py) / d
            short = min(1.0, d / (0.3 * size))                    # a short cut is struck less wildly
            for k in range(int(more.integers(1, 4)) if short == 1 else int(more.integers(1, 3))):
                o0, o1 = more.uniform(0.01, 0.07, 2) * size * short + 0.1 * d
                j = more.normal(0, 0.011 * size, 4)
                needle(SCR, (px - ux * o0 + j[0], py - uy * o0 + j[1]), (qx + ux * o1 + j[2], qy + uy * o1 + j[3]), w * more.uniform(0.75, 1.15) * (1.0 if k == 0 else 0.7))


deck = [SIGNS[i] for i in more.permutation(len(SIGNS))] * 2
for _ in range(9):
    n = int(more.choice([1, 2, 2, 3]))
    sizes = more.uniform(200, 320, n)
    stacked = n > 1 and more.random() < 0.3
    bw, bh = (sizes.max(), sizes.sum() * 1.2) if stacked else (sizes.sum() * 1.2, sizes.max())
    p = spot(lambda x, y: seen(BARE_, x, y, bw + 40, bh + 40) > 0.92, 330 + max(bw, bh) / 2, lo=640, hi=FLOOR - 260)
    if p is None:
        continue
    TAKEN.pop()                                                  # each sign takes its own place, not the row's middle
    tilt, w = more.normal(0, 0.07), more.uniform(4.6, 6.4)
    at = -(sizes.sum() * 1.2) / 2
    for i, size in enumerate(sizes):
        way = i == 0 and more.random() < 0.6
        sign = WAYS[int(more.integers(len(WAYS)))] if way else deck.pop()
        at += size * 0.6
        dx, dy = (0, at) if stacked else (at, 0)
        sx, sy = p[0] + dx * math.cos(tilt) - dy * math.sin(tilt) + more.normal(0, 8), p[1] + dx * math.sin(tilt) + dy * math.cos(tilt) + more.normal(0, 12)
        scratch(sign(more), sx, sy, size * 0.92, tilt + (more.uniform(0, 2 * np.pi) if way else more.normal(0, 0.1)), w)
        TAKEN.append((sx, sy))
        at += size * 0.6

# claw marks: three to five claws drawn down the wall together. Each digs in
# blunt and trails off to a point; the middle claws reach furthest; they fan a
# little, share the turn of the swipe, and now and then one skips. Raked into
# the plaster (a dark gouge, its edge broken back to pale fresh plaster),
# through the posters (the paper torn white along the slit), and into the
# faces of the crates (raw pale wood, a dark line at the deepest).
CLAW = {"wall": Mask(), "wood": Mask()}


def rake(M, x, y, a, length, n, gap, wmax):
    turn, fan = more.normal(0, 0.22), more.normal(0, 0.02)
    for i in range(n):
        u = (i - (n - 1) / 2) / ((n - 1) / 2)                    # -1 .. 1 across the paw
        ln = length * (1 - 0.3 * u * u) * more.uniform(0.82, 1.08)
        lead = 0.16 * length * u * u + more.normal(0, 0.04 * length)
        px = x - u * (n - 1) / 2 * gap * math.sin(a) + (lead - length / 2) * math.cos(a)
        py = y + u * (n - 1) / 2 * gap * math.cos(a) + (lead - length / 2) * math.sin(a)
        w = wmax * more.uniform(0.7, 1.0) * (1 - 0.15 * abs(u))
        ts = np.linspace(0, 1, 44)
        skip = more.uniform(0.3, 0.7) if more.random() < 0.3 else 9.0
        wob = np.convolve(more.normal(0, 1, len(ts) + 6), np.ones(7) / 7, "valid") * 0.5
        mid, half = [], []
        for t, wb in zip(ts, wob):
            ai = a + fan * u * (n - 1) / 2 + turn * (t - 0.5)
            px, py = px + ln / len(ts) * math.cos(ai), py + ln / len(ts) * math.sin(ai)
            h = w / 2 * ((t / 0.22) ** 0.7 if t < 0.22 else ((1 - t) / 0.78) ** 0.9) * (1 + wb)
            if abs(t - skip) < 0.05:                              # the claw skipped
                h = 0.0
            mid.append((px, py))
            half.append(max(h, 0.0))
            if h > 2 and more.random() < 0.035:                  # a splinter or a flake thrown off its edge
                sa_ = ai + more.choice([-1, 1]) * more.uniform(0.2, 0.5)
                needle(M, (px, py), (px + more.uniform(1.0, 2.2) * w * math.cos(sa_), py + more.uniform(1.0, 2.2) * w * math.sin(sa_)), w * 0.35, 0.8)
        run = []
        for (qx, qy), h, t in zip(mid, half, ts):
            ai = a + fan * u * (n - 1) / 2 + turn * (t - 0.5)
            if h > 0:
                run.append((qx, qy, -math.sin(ai) * h, math.cos(ai) * h))
            if h == 0 and len(run) > 2:
                M.poly([(qx + nx, qy + ny) for qx, qy, nx, ny in run] + [(qx - nx, qy - ny) for qx, qy, nx, ny in run[::-1]])
            if h == 0:
                run = []
        if len(run) > 2:
            M.poly([(qx + nx, qy + ny) for qx, qy, nx, ny in run] + [(qx - nx, qy - ny) for qx, qy, nx, ny in run[::-1]])


RAKES = [("wall", lambda x, y: seen(BARE_, x, y, 260, 420) > 0.8)] * 4 \
    + [("wall", lambda x, y: seen(PAPER_, x, y, 150, 190) > 0.7 and seen(WALL_, x, y, 240, 380) > 0.8)] * 4 \
    + [("wood", lambda x, y: seen(WOOD_, x, y, 150, 200) > 0.86)] * 5
for on, fits in RAKES:
    p = spot(fits, 430, lo=620, hi=FLOOR - 50)
    if p is None:
        continue
    n = int(more.choice([3, 4, 4, 5]))
    a = np.pi / 2 + more.normal(0, 0.5) + (np.pi if more.random() < 0.15 else 0)
    if on == "wall":
        rake(CLAW[on], *p, a, more.uniform(330, 700), n, more.uniform(38, 60), more.uniform(15, 22))
    else:
        rake(CLAW[on], *p, a, more.uniform(230, 400), n, more.uniform(28, 42), more.uniform(10, 15))

# cracks the wall did not have, longer and forked: for moss to take, and for a
# creeper to root in
CRK, ROOTS = Mask(), []


def crack(x, y, a, length, w, depth=0):
    pts = jag((x, y), (x + length * math.cos(a), y + length * math.sin(a)), 0.17, more, step=9)
    CRK.line(pts, w)
    ROOTS.extend(pts[::6])
    for _ in range(int(more.integers(0, 3)) if depth < 2 else 0):
        bx_, by_ = pts[int(more.integers(len(pts) // 5, 4 * len(pts) // 5))]
        crack(bx_, by_, a + more.choice([-1, 1]) * more.uniform(0.5, 1.1), length * more.uniform(0.25, 0.5), w * 0.75, depth + 1)


for _ in range(8):
    p = spot(lambda x, y: seen(WALL_, x, y, 240, 400) > 0.7, 380, lo=760, hi=FLOOR - 560)
    if p is not None:
        a = more.uniform(0.9, 2.2)
        crack(*p, a, min(more.uniform(380, 900), (FLOOR - 60 - p[1]) / math.sin(a)), more.uniform(2.6, 3.6))

# muddy paw prints: four beasts went over the wall, each its own foot and its
# own gait. Paws, never hands: a lobed pad and its toes, the claws' nicks ahead
# of them on the ones that do not sheathe them. The mud is thick where a trail
# starts (clods, a dribble or two) and wears off the feet as it goes, till
# only the toes and the pad's edge print; a foot that slipped left its smear
# above it; the smallest beast dragged its tail.
PAWS = {    # the pad's lobes (x, y, rx, ry) and the toes (angle, reach from the pad, rx, ry), in print lengths; the claws' length
    "hound": ([(0, 0.10, 0.19, 0.15), (0, 0.24, 0.27, 0.16), (-0.17, 0.33, 0.12, 0.12), (0.17, 0.33, 0.12, 0.12), (0, 0.36, 0.13, 0.11)],
              [(-0.70, 0.40, 0.085, 0.125), (-0.23, 0.50, 0.095, 0.14), (0.23, 0.50, 0.095, 0.14), (0.70, 0.40, 0.085, 0.125)], 0.13),
    "cat": ([(0, 0.12, 0.20, 0.14), (0, 0.24, 0.29, 0.15), (-0.19, 0.31, 0.11, 0.11), (0.19, 0.31, 0.11, 0.11), (0, 0.33, 0.12, 0.10)],
            [(-0.80, 0.38, 0.095, 0.11), (-0.27, 0.45, 0.10, 0.12), (0.27, 0.45, 0.10, 0.12), (0.80, 0.38, 0.095, 0.11)], 0.0),
    "fox": ([(0, 0.12, 0.14, 0.14), (0, 0.25, 0.20, 0.14), (-0.12, 0.33, 0.10, 0.10), (0.12, 0.33, 0.10, 0.10)],
            [(-0.55, 0.42, 0.07, 0.13), (-0.17, 0.56, 0.075, 0.15), (0.17, 0.56, 0.075, 0.15), (0.55, 0.42, 0.07, 0.13)], 0.10),
    "small": ([(0, 0.20, 0.20, 0.13), (-0.12, 0.28, 0.10, 0.10), (0.12, 0.28, 0.10, 0.10)],
              [(a, 0.43, 0.07, 0.085) for a in (-1.15, -0.58, 0.0, 0.58, 1.15)], 0.08),
}
GAIT = {    # stride and straddle (in print lengths), how the way wanders, how often a foot slips
    "hound": (1.28, 0.42, 0.06, 0.4), "cat": (1.4, 0.26, 0.05, 0.15), "fox": (1.5, 0.3, 0.07, 0.25), "small": (1.25, 0.55, 0.16, 0.0),
}
MUD = {"wall": Mask(), "stack": Mask()}


def pawprint(M, x, y, a, L, kind, v, slip=0.0):
    """One print at (x, y), toes toward a, L long, as heavy as v; slip: how far (in L) the foot slid down the wall to it."""
    pad, toes, claw = PAWS[kind]
    c, s_ = math.cos(a + np.pi / 2), math.sin(a + np.pi / 2)
    shapes = [(cx, cy, rx, ry, 0.0) for cx, cy, rx, ry in pad] + [(math.sin(g) * d, 0.2 - math.cos(g) * d, rx, ry, g * 0.8) for g, d, rx, ry in toes]

    def blob(cx, cy, rx, ry, turn, v_, dy=0.0):
        pts = []
        for t in np.linspace(0, 2 * np.pi, 14, endpoint=False):
            ex, ey = rx * math.cos(t) * more.uniform(0.92, 1.08), ry * math.sin(t) * more.uniform(0.92, 1.08)
            lx, ly = cx + ex * math.cos(turn) - ey * math.sin(turn), cy + ex * math.sin(turn) + ey * math.cos(turn)
            pts.append((x + L * (lx * c - ly * s_), y + dy + L * (lx * s_ + ly * c)))
        M.poly(pts, v_)

    for j in range(1, 1 + int(slip * 7)):                        # the smear above a foot that slid
        for shp in shapes:
            blob(*shp, v * 0.34 * (1 - 0.5 * j / (slip * 7)), dy=-j / 7 * L)
    for k, shp in enumerate(shapes):
        if v > 0.55 or more.random() < 0.85 or k >= len(pad):    # a light print can miss a lobe
            blob(*shp, v * more.uniform(0.85, 1.0))
    if claw:
        for g, d, rx, ry in toes:
            tx, ty = math.sin(g) * (d + ry + 0.03), 0.2 - math.cos(g) * (d + ry + 0.03)
            ex, ey = math.sin(g) * (d + ry + 0.03 + claw), 0.2 - math.cos(g) * (d + ry + 0.03 + claw)
            needle(M, (x + L * (tx * c - ty * s_), y + L * (tx * s_ + ty * c)), (x + L * (ex * c - ey * s_), y + L * (ex * s_ + ey * c)), 0.07 * L, v)
    if v > 0.8:                                                  # heavy with mud: clods thrown round it, and a dribble
        for _ in range(int(more.integers(2, 8))):
            g, d = more.uniform(0, 2 * np.pi), L * more.uniform(0.55, 1.1)
            M.line([(x + d * math.cos(g), y + d * math.sin(g)), (x + d * math.cos(g) + 0.5, y + d * math.sin(g) + more.uniform(0, 0.08) * L)], L * more.uniform(0.03, 0.09), more.uniform(0.6, 1.0))
        if more.random() < 0.55:
            dx_, len_ = more.normal(0, 0.15) * L, L * more.uniform(0.5, 1.6)
            M.line([(x + dx_, y + 0.2 * L), (x + dx_ + more.normal(0, 0.03) * L, y + 0.4 * L + len_)], 0.035 * L, 0.62)
            M.line([(x + dx_, y + 0.4 * L + len_), (x + dx_, y + 0.4 * L + len_ + 1)], 0.075 * L, 0.8)


def footfalls(kind, x, y, a, n, L):
    """Where a trail's prints fall: (x, y, heading, how far along, the way's own x, y). The feet alternate either side of the way, which wanders."""
    stride, straddle, wander, _ = GAIT[kind]
    side, turn, out = more.choice([-1, 1]), more.normal(0, 0.025), []
    for i in range(n):
        a += turn + more.normal(0, wander)
        st = stride * L * more.uniform(0.85, 1.15)
        x, y = x + st * math.cos(a), y + st * math.sin(a)
        out.append((x - side * straddle * L * math.sin(a), y + side * straddle * L * math.cos(a), a + side * more.uniform(0.0, 0.22) + more.normal(0, 0.08), i / n, x, y))
        side = -side
    return out


TRAILS = [   # the beast, its print's length, how many prints, where it set out (down the wall) and which way
    ("hound", (178, 206), (7, 9), (FLOOR - 420, FLOOR - 60), lambda: -np.pi / 2 + more.normal(0, 0.45)),
    ("cat", (104, 124), (12, 16), (700, FLOOR - 200), lambda: more.uniform(0, 2 * np.pi)),
    ("fox", (128, 150), (9, 12), (640, 1400), lambda: np.pi / 2 + more.normal(0, 0.6)),
    ("small", (56, 68), (24, 34), (900, FLOOR - 150), lambda: more.choice([0, np.pi]) + more.normal(0, 0.4)),
]
TROD = []
for kind, size, count, band, heading in TRAILS:
    best = None
    for _ in range(600):                                         # of many ways it might have gone, the one that shows best
        L, n = more.uniform(*size), int(more.integers(*count))
        x, y = more.uniform(0, NW), more.uniform(*band)
        falls = footfalls(kind, x, y, heading(), n, L)
        if not all(580 < f[1] < FLOOR + 30 and apart(f[0], f[1], TROD, 300) for f in falls):
            continue
        score = np.mean([max(seen(WALL_, f[0], f[1], L, L), seen(STACK_, f[0], f[1], L, L)) - 0.6 * (not apart(f[0], f[1], TAKEN, 200)) for f in falls])
        if best is None or score > best[0]:
            best = (score, L, falls)
        if score > 0.93:
            break
    if best is None:
        continue
    _, L, falls = best
    slips = GAIT[kind][3]
    for i, (x, y, a, t, wx, wy) in enumerate(falls):
        on = "stack" if seen(STACK_, x, y, L * 0.5, L * 0.5) > 0.5 else "wall"
        v = (1 - 0.62 * t ** 0.8) * more.uniform(0.85, 1.0)
        pawprint(MUD[on], x, y, a, L * more.uniform(0.93, 1.07), kind, v, slip=more.uniform(0.3, 0.75) if more.random() < slips else 0.0)
        if kind in ("hound", "fox") and more.random() < 0.45:   # the hind foot, set down just behind the fore
            back = more.uniform(0.5, 0.85) * L
            pawprint(MUD[on], x - back * math.cos(a) + more.normal(0, 0.12) * L, y - back * math.sin(a) + more.normal(0, 0.12) * L, a + more.normal(0, 0.12), L * 0.86, kind, v * 0.8)
        if kind == "small" and i and more.random() < 0.8:        # its tail, dragged
            (px, py), (qx, qy) = falls[i - 1][4:], (wx, wy)
            MUD[on].line([(px, py), ((px + qx) / 2 + more.normal(0, 0.12) * L, (py + qy) / 2 + more.normal(0, 0.12) * L), (qx, qy)], 0.11 * L, 0.3 + 0.25 * (1 - t))
    TROD += [f[:2] for f in falls]
TAKEN += TROD[::3]

# now lay them on the wall: the new cracks; moss in every crack and along the
# broken edges of the plaster, in cushions, thicker low down where it is damp
print("  cracks and moss", flush=True)
vis, lit = WALL * (1 - PAPER), LIT["wall"]                      # the wall itself, bare of paper
crk = CRK.render()
daub(hexc("#6a6258"), crk * 0.75, vis, lit)
veins = np.clip(blur(np.maximum(crk, CRACK), 13.0) * 10, 0, 1)
edge = blur(SP, 5.0)
edge = np.clip(4 * edge * (1 - edge), 0, 1) * 0.8
took = 0.2 + 0.8 * smooth(noise(1.6, seed=SEED + 73, feature=300 * S), 0.4, 0.58)       # where moss has taken at all: in patches
damp_ = 0.5 + 0.5 * smooth(yy, 700, 2300)
clump = noise(1.3, seed=SEED + 71, feature=80 * S)
MOSS = smooth(np.maximum(veins, edge) * took * damp_ + 1.0 * (clump - 0.5) + 0.35 * (TEX["speck"] - 0.5), 0.36, 0.41)   # in cushions, ragged
h = blur(MOSS, 2.2)
tone(0.75, np.clip((shift(h, 3.5 * S, 3.5 * S) - MOSS) * 1.5, 0, 1), vis)                 # the cushions' shade on the wall
green = mix(hexc("#566440"), hexc("#8c9858"), smooth(TEX["fine"] * 0.6 + clump * 0.4, 0.38, 0.62)[..., None])
daub(green * np.clip((0.8 + 0.4 * TEX["speck"]) * (1 + 0.8 * relief(h, 2.0)), 0.6, 1.4)[..., None], MOSS * 0.95, vis, lit)
del crk, veins, edge, took, damp_, h, green, CRACK, SP

# the signs
print("  signs", flush=True)
vis = WALL
scr = SCR.render()
flake = smooth(blur(scr, 2.4) + 0.8 * (TEX["speck"] - 0.5), 0.24, 0.3) * PAINTED         # the dado's paint, flaked off round a cut
cut_ = smooth(blur(scr, 0.9) + 0.3 * (TEX["speck"] - 0.5), 0.28, 0.5)                    # the cut itself, its edge ragged
daub(hexc("#e2dccb"), np.clip(blur(scr, 6.0) * 2.5, 0, 0.3) * (1 - PAINTED), vis, lit)                     # the dust of it, rubbed into the wall
daub(PLASTER * 0.99, flake * 0.92, vis, lit)
tone(0.8, np.clip(flake - shift(flake, 2.5 * S, 2.5 * S), 0, 1), vis)                     # the paint's edge, in its own shade
daub(hexc("#ebe6d8"), np.clip(shift(cut_, 2.6 * S, 2.6 * S) - cut_, 0, 1) * 0.85, vis, lit)   # the burr, lit
daub(hexc("#62584f"), cut_ * (0.86 - 0.26 * PAINTED), vis, lit)
del scr, flake, cut_

# the claws on the wall, and through its paper
print("  claws", flush=True)
raw = CLAW["wall"].render()
gouge = smooth(blur(raw, 1.0) + 0.3 * (TEX["speck"] - 0.5), 0.3, 0.55)
chips = 0.2 + 0.8 * smooth(clump, 0.47, 0.56)                    # the plaster broke back from a gouge in places, not all along it
broke = np.maximum(smooth(blur(raw, 4.0) + 0.5 * (TEX["speck"] - 0.5), 0.2, 0.32) * chips * (1 - PAPER),
                   smooth(blur(raw, 2.4) + 0.4 * (TEX["speck"] - 0.5), 0.2, 0.32) * PAPER)               # and paper tears white all along
daub(mix(PLASTER * 1.06, hexc("#ece8dc"), PAPER[..., None]), broke * (0.8 + 0.15 * PAPER), vis, lit)
tone(0.8, np.clip(broke - shift(broke, 3 * S, 3 * S), 0, 1) * (1 - gouge), vis)
h = blur(gouge, 1.6)
daub(mix(hexc("#564c45"), hexc("#6b635a"), PAPER[..., None]) * np.clip(1 - 2.2 * relief(h, 2.0), 0.5, 1.9)[..., None], gouge * 0.92, vis, lit)
# and in the crates
raw = CLAW["wood"].render()
gouge = smooth(blur(raw, 1.0) + 0.3 * (TEX["speck"] - 0.5), 0.3, 0.55)
broke = smooth(blur(raw, 3.0) + 0.9 * (TEX["gh"] - 0.5), 0.22, 0.32)                                     # splintered along the grain
h = blur(gouge, 1.6)
daub(hexc("#dccba6"), broke * 0.9, WOOD, LIT["stack"])
daub(hexc("#5b4d40") * np.clip(1 - 2.2 * relief(h, 2.0), 0.5, 1.9)[..., None], gouge * 0.92, WOOD, LIT["stack"])
del raw, gouge, broke, h

# the mud
print("  mud", flush=True)
blot = noise(1.5, seed=SEED + 72, feature=34 * S)
for on, vis, lit in (("wall", WALL, LIT["wall"]), ("stack", STACK, LIT["stack"])):
    T = smooth(blur(MUD[on].render(), 0.9) * (0.5 + 0.95 * blot), 0.28, 0.55)      # patchy where the foot was light
    h = blur(T, 1.8)
    tone(np.array([0.80, 0.70, 0.56]), smooth(T, 0.0, 0.5), vis)                   # a film of it
    body = mix(hexc("#7a654c"), hexc("#5f4e3b"), smooth(TEX["fine"], 0.3, 0.7)[..., None])
    daub(body * np.clip(1 + 1.2 * relief(h, 1.6), 0.7, 1.3)[..., None], smooth(T, 0.35, 0.9) * 0.9, vis, lit)
    tone(0.78, np.clip((T - h) * 2.2, 0, 1), vis)                                  # it dried darker at its edge
del T, h, body, blot

# creepers: a stem wanders up the wall from a crack or from behind the crates
# (or hangs down it from the gutter), forks, and puts out a leaf at every node:
# big and dark low on the stem, small and pale at the growing tip, a few
# yellowed or dead. Three kinds of leaf. They lie on the wall and its paper,
# under what is hung there; two more wind up poles, in front of everything.
print("  creepers", flush=True)
GREENS = [hexc(c) for c in ("#56633f", "#617046", "#6c7a4c", "#4f5b3b", "#76804f")]
SERE = [hexc(c) for c in ("#9a8c50", "#8b7049", "#a59c64")]
LEAF = {    # half of each outline, from the stalk (0, 0) to the tip (1, 0)
    "ivy": [(0, 0), (-0.07, 0.27), (0.07, 0.45), (0.23, 0.26), (0.48, 0.5), (0.6, 0.2), (1, 0)],
    "heart": [(0, 0), (-0.1, 0.2), (0.0, 0.4), (0.25, 0.46), (0.55, 0.34), (0.82, 0.14), (1, 0)],
    "round": [(0, 0), (0.1, 0.24), (0.35, 0.38), (0.65, 0.35), (0.9, 0.18), (1, 0)],
}
NODE = {"ivy": (40, 60), "heart": (48, 54), "round": (24, 30)}      # units between leaves, and a full-grown leaf's length


def grow(x, y, a, length, w0, kind, home, stems, leaves, depth=0):
    """A stem from (x, y) heading a: it wanders, leans back toward `home` (up,
    for a climber; down, for one that hangs), forks, and leaves at every node."""
    node, big = NODE[kind]
    node *= more.uniform(0.85, 1.2)
    n = int(length / 8)
    pts, side, since, ph = [(x, y)], more.choice([-1, 1]), node * 0.5, more.uniform(0, 2 * np.pi)
    for i in range(n):
        t = i / n
        a += more.normal(0, 0.08) + 0.05 * math.sin(i * 0.13 + ph) - 0.05 * ((a - home + np.pi) % (2 * np.pi) - np.pi)
        x, y = x + 8 * math.cos(a), y + 8 * math.sin(a)
        pts.append((x, y))
        since += 8
        if since >= node:
            since = 0
            for sd in ((side, -side) if kind == "round" else (side,)):
                if more.random() > 0.12:                         # some have fallen
                    la = a + sd * more.uniform(0.75, 1.25)
                    leaves.append((x, y, la + 0.35 * ((np.pi / 2 - la + np.pi) % (2 * np.pi) - np.pi) * (home > 0), big * (1 - 0.55 * t ** 1.5) * more.uniform(0.75, 1.15), t, depth))
            side = -side
            if depth < 2 and t < 0.8 and more.random() < 0.13:
                grow(x, y, a + side * more.uniform(0.5, 1.0), length * (1 - t) * more.uniform(0.45, 0.85), w0 * (1 - 0.55 * t), kind, home, stems, leaves, depth + 1)
    stems.append((pts, w0, 1.6))


def foliage(stems, leaves, kind, pad=90):
    """The sprite of a creeper (its stems and leaves in tile coordinates), and where it goes: (sprite, X, Y)."""
    xs = [p[0] for st in stems for p in st[0]] + [lf[0] for lf in leaves]
    ys = [p[1] for st in stems for p in st[0]] + [lf[1] for lf in leaves]
    X0, Y0 = int(min(xs)) - pad, int(min(ys)) - pad
    s = Spr(max(xs) - X0 + pad, max(ys) - Y0 + pad)
    bark = jit(hexc("#5e5440"), more, 0.04)
    for pts, w0, w1 in stems:
        for i in range(0, len(pts) - 1, 5):
            seg = [(px - X0, py - Y0) for px, py in pts[i:i + 6]]
            w = w0 + (w1 - w0) * i / len(pts)
            s.line(seg, w + 1.4, bark * 0.7)
            s.line(seg, w, mix(bark, GREENS[1], i / len(pts)))
    for x, y, a, size, t, depth in leaves:
        col = jit(GREENS[int(more.integers(len(GREENS)))] * (0.9 + 0.25 * t), more, 0.04)
        if more.random() < 0.17:
            col = jit(SERE[int(more.integers(len(SERE)))], more, 0.04)
        ca, sa = math.cos(a), math.sin(a)
        x, y = x - X0 + 0.22 * size * ca, y - Y0 + 0.22 * size * sa                  # at the end of its stalk
        s.line([(x - 0.22 * size * ca, y - 0.22 * size * sa), (x, y)], 1.6, bark * 0.9)
        wide = more.uniform(0.85, 1.1)
        T = lambda px, py: (x + size * (px * ca - py * wide * sa), y + size * (px * sa + py * wide * ca))
        half = LEAF[kind]
        out = [T(px, py) for px, py in half] + [T(px, -py) for px, py in half[-2:0:-1]]
        s.put(s.mlines([out + out[:1]], 2.6), col * 0.55)
        s.poly(out, col)
        low = 1 if 0.62 * ca - 0.45 * sa > 0 else -1                                 # the half turned from the light
        s.shade(s.mpoly([[T(px, low * py) for px, py in half]]), 0.8)
        s.line([T(0, 0), T(0.9, 0)], 1.3, np.clip(col * 1.3, 0, 1), 0.8)
        if kind == "ivy":
            for sd in (-1, 1):
                s.line([T(0.12, 0), T(0.42, sd * 0.36)], 1.0, np.clip(col * 1.3, 0, 1), 0.6)
    return s, X0, Y0


L_VINE = Layer("creepers on the wall", 3, 4, 2.5, 0.30)
L_TWINE = Layer("creepers up the poles", 4, 6, 3.5, 0.28)
kinds = list(LEAF) * 3
more.shuffle(kinds)
clear = lambda x, y, up: seen(WALL_, x, y - up * 300, 200, 600) > 0.62 and apart(x, y, TAKEN, 240)
roots = [ROOTS[i] for i in more.permutation(len(ROOTS))] if ROOTS else []
roots = [p for p in roots if 1300 < p[1] < FLOOR - 200 and clear(*p, 1)]
for k in range(7):
    hangs = k >= 5
    if hangs:                                                    # down from the gutter
        p = spot(lambda x, y: clear(x, y, -1), 380, lo=560, hi=700)
    elif k < 2 and roots:                                        # out of a crack
        p = roots.pop()
        roots = [q for q in roots if apart(*q, [p], 700)]
        TAKEN.append(p)
    else:                                                        # up from behind the stalls
        p = spot(lambda x, y: clear(x, y, 1), 380, lo=FLOOR - 620, hi=FLOOR - 260)
    if p is None:
        continue
    stems, leaves = [], []
    home = np.pi / 2 if hangs else -np.pi / 2
    grow(*p, home + more.normal(0, 0.4), more.uniform(500, 900) if hangs else min(more.uniform(600, 1400), p[1] - 560), more.uniform(5, 7.5), kinds[k], home, stems, leaves)
    L_VINE.add(*foliage(stems, leaves, kinds[k]))
for j in more.choice(len(POLES), 2, replace=False):              # round a pole: the stem shows where it passes in front
    cx, top, pw = POLES[j]
    kind = ["ivy", "heart"][int(more.integers(2))]
    y1, pitch, ph, R = FLOOR + 30, more.uniform(105, 150), more.uniform(0, 2 * np.pi), pw / 2 + 3
    y0 = max(top + 120, y1 - more.uniform(800, 1700))
    stems, leaves, run, since = [], [], [], 0.0
    for y in np.arange(y1, y0, -4.0):
        t = (y1 - y) / (y1 - y0)
        wide = 6 - 3 * t
        phi = 2 * np.pi * (y1 - y) / pitch + ph
        x = cx + R * math.sin(phi)
        if math.cos(phi) > -0.25:
            run.append((x, y))
        elif run:
            stems.append((run, wide, wide))
            run = []
        since += 4
        if since > NODE[kind][0] * 0.8 and math.cos(phi) > 0.1 and more.random() < 0.8:
            since = 0
            out = 1 if math.sin(phi) > 0 else -1
            leaves.append((x, y, -np.pi / 2 + out * more.uniform(0.5, 1.4), NODE[kind][1] * (1 - 0.5 * t ** 1.5) * more.uniform(0.75, 1.1), t, 0))
    if run:
        stems.append((run, wide, wide))
    if more.random() < 0.7:                                      # and a shoot let go of it, reaching out
        grow(cx, y0 + 60, -np.pi / 2 + more.choice([-1, 1]) * 0.9, more.uniform(200, 420), 3.5, kind, -np.pi / 2, stems, leaves, depth=2)
    L_TWINE.add(*foliage(stems, leaves, kind))
L_VINE.flush(WALL, LIT["wall"])
L_TWINE.flush()
del SHOWS, LIT, WALL, PAPER, STACK, WOOD, PAINTED, vis, lit

# the lit bulbs and lanterns: a warm glow, screened over what is round them
glow = np.zeros((PH, PW), f32)
for (x, y, k) in GLOWS:
    glow[int(y * S) % PH, int(x * S) % PW] += k
glow = blur(glow, 26.0) * (2 * np.pi * (26 * S) ** 2) * 0.10           # a glow of peak 0.1 k, 26 units wide
glow = np.clip(glow, 0, 0.35)
grime = noise(1.9, seed=SEED + 23)
FP = round(FLOOR * S)       # px
HID = PH - FP
t = smooth(np.arange(HID, dtype=f32), HID * 0.25, HID * 0.95)[:, None, None]
accent0[FP:] = np.where(t[..., 0] > 0.5, accent0[HID - 1::-1][:HID], accent0[FP:])


def weathered(img):
    """The wall (with its marks, and without) under the bulbs' glow and the
    street's grime, its hidden foot faded back to its top, a little greyer."""
    img = img + (1 - img) * glow[..., None] * hexc("#f2dca0")
    # grime over everything, a little more toward the street
    img *= (1 - 0.05 * smooth(grime, 0.4, 0.9) - 0.04 * smooth(yy, 2000, FLOOR))[..., None]
    img = np.clip(img, 0, 1)
    # the foot of the tile is under the ground strip or off the page: fade it back to the top, mirrored at the seam
    img[FP:] = img[FP:] * (1 - t) + img[HID - 1::-1][:HID] * t
    lum = img.mean(-1, keepdims=True)
    return img + (lum - img) * 0.18


# drawn back: a little greyer, then toward the mean (the unmarked wall's: the marks do not move the wall); a fine grain so the palette does not band
plain, img = weathered(plain), weathered(img)
mean = plain.reshape(-1, 3).mean(0, dtype=np.float64).astype(f32)   # summed in float64: in float32 it drifts with the px count
grain = (1 + np.random.default_rng(SEED + 900).normal(0, 0.009, (PH, PW)).astype(f32))[..., None]


def eight(img):
    img = mean + (img - mean) * CALM
    img *= grain
    return (np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8)


# an exact palette, no dither: the wall's tones, and the saturated sliver apart;
# then the marks' own colours, cut from the px they changed and used only there
rgb0, rgb = eight(plain), eight(img)
del img, plain
marked = (rgb != rgb0).any(-1)
pal = []
for sel, n in ((~accent0, 160 - ACCENT_COLOURS), (accent0, ACCENT_COLOURS)):
    px = rgb0[sel][None]
    q = Image.fromarray(px, "RGB").quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal += q.getpalette()[:3 * n]
q = Image.fromarray(rgb[marked][None], "RGB").quantize(colors=MARK_COLOURS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
pal_marks = q.getpalette()[:3 * MARK_COLOURS]


def to_palette(rgb, pal):
    palimg = Image.new("P", (1, 1))
    palimg.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
    return np.asarray(Image.fromarray(rgb, "RGB").quantize(palette=palimg, dither=Image.Dither.NONE))


out = Image.fromarray(np.where(marked, to_palette(rgb, pal + pal_marks), to_palette(rgb0, pal)), "P")
out.putpalette(pal + pal_marks)
out.save(ROOT / "images/wall-13.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-13.png  {PW}x{PH}  {PW / DPI:.2f}x{PH / DPI:.2f}in  {int(accent0.mean() * 1000) / 10}% accent  {int(marked.mean() * 1000) / 10}% marked  "
      f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
