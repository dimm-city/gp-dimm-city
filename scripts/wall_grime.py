"""Grime and damage for the stone walls (1-6) and the brick: what makes them Dimm City's.

    import wall_grime
    rgb, special = wall_grime.weather(rgb, joint, seed)
    wall_grime.save(rgb, special, path)

wall-stone-rubble.py (1, 3, 5), wall-stone-coursed.py (2, 4, 6) and
wall-brick.py (the brick) draw a clean wall in the clean brick's tones
(`clean_brick`); each hands its tile here as float RGB (0-1) with its joint
mask (1 in a joint and on the joint's line, 0 on a stone's face), so every
wall is weathered by one hand and all of them read as one city: dim, dirty,
damp and dangerous, but a wall first, behind the white sheets.

The tile is placed from the text area's corner, so on every page the text
area is the same rectangle of it (TEXT_W x TEXT_H) and the side margins are
the columns past it. Big dark marks (soot, wet patches, scorches, grease)
are toned down there (CALM), and some of each kind of damage is put in the
side margins (`place(margin=True)`), so every page shows it.

Back to front, the light from the upper left as on the stone:
1. Dim: the stone is greyed a little, and at the end the lighter half of the
   tile is pulled toward its median (DULL: no face reads as clean stone)
   and the whole tile is scaled to TARGET, lighter than the specialty walls.
2. Grime: dirt in the joints and their pockets, washed down under every bed
   joint, in broad patches, and heavier toward the wall's foot (FOOT, where the
   ground strip meets it on a page); soot and grime run down from the ledges.
3. Damp: dark streaks run down from the joints, dark wet patches with a faint
   tide line, rising damp at the foot under a wavy tide mark (a dark line,
   salt above it, darker and dirtier lower down), and tide-ringed leaks.
4. Mould: black and dark-green speckled blooms spreading from the joints,
   worst where it is wet; a slimy green algal film with a glint in the
   wettest places; small shelf fungi and clusters of caps in the joints.
5. Burns and grease: soot blooms with a scorched core and soot rising above
   them, small burnt patches, often a flame's lick along the wall; grease
   stains soaked in round where they hit, a run or two below.
6. Damage: chipped arrises, cracks, bullet pocks (singles and bursts), four
   sets of 3-4 claw gouges (`gouge`: torn into the stone, its upper-left wall
   in shade and casting a shadow on the floor, its lower-right lip lit, a
   blunt torn bite and a long drag out to torn tines, broken where it crosses
   a joint, flakes and grit spilled along it; fresh, or old and packed with
   dirt; dried blood dragged down one or two), and scratched tallies and
   glyphs. Nothing written.
7. Blood: dried, brown-red, small: spatters by the freshest claw marks and
   elsewhere, specks in little groups, a smear. Grim, not gory: the
   Cybersurgeon's wall (10) is the bloody one.
Then quantised (`save`) to an exact palette with no dither, its last entries
cut from the saturated things alone (blood, mould, algae, fungi), so they keep
their colour instead of going grey.

Everything is periodic, so the tile still repeats without a seam: the noise
is filtered in the Fourier domain, blurs and streaks are circular
convolutions, and every shape is drawn wrapped. The tile is 9in x 12in or so,
taller than a page and about as wide, so a page shows no repeat of a mark.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

F32 = np.float32
DPI = 300
TARGET = np.array([0x9e, 0x9a, 0x92], F32) / 255   # the weathered wall's average: dim, and still lighter than walls 7-13
FOOT = 10.0 * DPI           # px down the tile to the wall's foot: the ground strip's top on a page
# Where the sheets sit. A wall is placed from the text area's corner, so on
# every page the text area (7.5in x 9.675in: dc-palette.css's margins on an
# 8.625in x 11.25in sheet) is the tile's top-left (0, 0)-(TEXT_W, TEXT_H) and
# the margins are the rest: the side margins, both of them, are the columns
# past TEXT_W (the right-hand margin, then, wrapped, the left), the band
# above the ground the rows past TEXT_H. Big dark marks are kept moderate on
# the text area (CALM), where the gaps between sheets are, and some of the
# damage is put in the margins, so every page shows it.
TEXT_W, TEXT_H = 7.5 * DPI, 9.675 * DPI
CALM = 0.35                 # how much big dark marks are toned down on the text area
GREY = 0.30                 # how far the stone is greyed toward its own luminance
DULL = 0.6                  # the lighter half's contrast, kept: the faces dulled, so the wall reads dirty
SS = 2                      # shapes are drawn at SS x and boxed down
LUM = np.array([0.299, 0.587, 0.114], F32)


BG = (0xC8, 0xC5, 0xBF)      # --bg (ash concrete), the brick's colour
BRICK_SRC = Path(__file__).resolve().parents[1] / "source-art/brick-bg-01.png"   # the brick: a grey line drawing, RGBA, 300 DPI


def clean_brick(size=(900, 1165)):
    """The clean brick, the line drawing multiplied into --bg, at `size`: by
    default the old 1.5in tile at 600 DPI, whose pixels are the tones every
    stone wall and street is matched to (byte for byte the old
    images/brick-wall.png, which is now grimed)."""
    src = Image.open(BRICK_SRC)
    solid = Image.new("RGB", src.size, BG)
    flat = Image.composite(ImageChops.multiply(solid, src.convert("RGB")), solid, src.getchannel("A"))
    return flat if size is None else flat.resize(size, Image.LANCZOS)


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], F32) / 255


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t, F32)
    if t.ndim == 2 and np.ndim(a) == 3:
        t = t[..., None]
    return a + (b - a) * t


def mix_into(a, b, t):
    """mix(a, b, t), worked in place in `a` (the tile is big): `b`, a new array
    of `a`'s shape, is used up."""
    t = np.asarray(t, F32)
    if t.ndim == 2:
        t = t[..., None]
    b -= a
    b *= t
    a += b
    return a


# the colours: multipliers (a stain over the stone) and paints (opaque)
DIRT = hexc("#c8bfb2")          # grime: a warm grey-brown, multiplied
WET = hexc("#b0b3ac")           # damp stone: darker and a little cool
SALT = hexc("#e4e2da")          # efflorescence above a tide mark
TIDE = hexc("#8a7d6a")          # the tide line itself, multiplied
MOULD_STAIN = hexc("#c6cfbe")   # the stain round a colony
MOULD_BLACK = hexc("#34352f")
MOULD_GREEN = hexc("#3e4934")
ALGAE = hexc("#cbdcb4")         # the green film, multiplied
SOOT = hexc("#2e2a26")
SCORCH = hexc("#b49a84")        # the brown halo round a burn, multiplied
OIL = hexc("#3e3830")            # grease soaked in, at its darkest
OIL_FILM = hexc("#a39a8c")       # its stain, multiplied
CALCINED = hexc("#a3958d")      # stone burnt pale and pinkish where the fire was hottest
FRESH = hexc("#cfccc5")         # stone broken open: clean, paler than the weathered face
HOLE = hexc("#47423d")
BLOOD_FILM = {"dry": hexc("#b4877a"), "old": hexc("#b49482")}   # thin blood, multiplied
BLOOD_DEEP = {"dry": hexc("#6e3529"), "old": hexc("#6a4a3b")}   # thick blood, dried
SHELVES = [   # zones (dark, mid, light), rim, underside: muted, dirty
    ((hexc("#8a8576"), hexc("#a19c8c"), hexc("#b7b2a2")), hexc("#ccc7b6"), hexc("#625d52")),   # pallid, bone grey
    ((hexc("#6c5a5c"), hexc("#826f72"), hexc("#998889")), hexc("#b2a5a2"), hexc("#4b3e40")),   # bruised
    ((hexc("#86704a"), hexc("#9c855a"), hexc("#b19c6f")), hexc("#c4b58f"), hexc("#5f4e33")),   # dirty ochre
    ((hexc("#7e7f55"), hexc("#939367"), hexc("#a8a87d")), hexc("#bebd98"), hexc("#5b5b3b")),   # sickly sulphur
]
CAPS = [   # cap, its dark
    (hexc("#7d7672"), hexc("#4c4744")),        # ink grey
    (hexc("#9c876a"), hexc("#655542")),        # tan
    (hexc("#8a7c8c"), hexc("#5a4f5d")),        # livid violet
    (hexc("#a3a07a"), hexc("#68664a")),        # pale sulphur
]
# invented glyphs, scratched: strokes in a unit box, y down; no letters
GLYPHS = [
    [[(0.0, 0.5), (0.25, 0.25), (0.5, 0.18), (0.75, 0.25), (1.0, 0.5)],          # an eye: lids, pupil, lashes down
     [(0.0, 0.5), (0.25, 0.75), (0.5, 0.82), (0.75, 0.75), (1.0, 0.5)],
     [(0.5, 0.36), (0.6, 0.5), (0.5, 0.64), (0.4, 0.5), (0.5, 0.36)],
     [(0.3, 0.8), (0.24, 1.0)], [(0.5, 0.84), (0.5, 1.04)], [(0.7, 0.8), (0.76, 1.0)]],
    [[(0.5, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.5), (0.5, 0.0)],                 # a cut diamond, a hook through it
     [(0.5, -0.15), (0.5, 0.75), (0.38, 0.88), (0.25, 0.8)]],
    [[(0.0, 0.0), (0.5, 0.42), (1.0, 0.0)], [(0.5, 0.42), (0.5, 0.62)],           # a crow's foot over a ring
     [(0.3, 0.8), (0.5, 0.62), (0.7, 0.8), (0.5, 0.98), (0.3, 0.8)]],
    [[(0.1, 1.0), (0.5, 0.0), (0.9, 1.0)], [(0.24, 0.66), (0.76, 0.66)],          # a peak, barred twice, a dot under it
     [(0.32, 0.46), (0.68, 0.46)], [(0.5, 1.08), (0.52, 1.12)]],
]


class Torus:
    """An H x W tile on the torus: periodic noise, blurs, shifts and wrapped shapes."""

    def __init__(self, H, W, seed):
        self.H, self.W = H, W
        self.rng = np.random.default_rng(seed)
        self.FY = np.fft.fftfreq(H).astype(F32)[:, None]
        self.FX = np.fft.rfftfreq(W).astype(F32)[None, :]
        self.ky = np.where(np.arange(H) > H // 2, np.arange(H) - H, np.arange(H)).astype(F32)[:, None]
        self.kx = np.where(np.arange(W) > W // 2, np.arange(W) - W, np.arange(W)).astype(F32)[None, :]

    def noise(self, beta, feature, lo=None, stretch=(1.0, 1.0)):
        """Periodic 1/f^beta noise as a z-score: nothing larger than `feature` px,
        nothing smaller than `lo` px; `stretch` (sx, sy) < 1 makes it finer across
        that axis, so it runs along the other."""
        spec = np.fft.rfft2(self.rng.standard_normal((self.H, self.W), dtype=F32))
        fx, fy = self.FX * stretch[0], self.FY * stretch[1]
        f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)
        spec /= f ** beta
        if lo:
            spec *= np.exp(-(f * lo) ** 2)
        out = np.fft.irfft2(spec, s=(self.H, self.W)).astype(F32, copy=False)
        out -= out.mean()
        return out / out.std()

    def spec(self, m):
        """`m`'s spectrum, for a blur or conv of it to take instead of `m` when it
        is blurred or convolved more than once."""
        return m if np.iscomplexobj(m) else np.fft.rfft2(m)

    def blur(self, m, sigma):
        k = np.exp(-2 * np.pi ** 2 * sigma * sigma * (self.FX ** 2 + self.FY ** 2))
        return np.fft.irfft2(self.spec(m) * k, s=(self.H, self.W)).astype(F32, copy=False)

    def conv(self, m, kernel):
        k = np.fft.rfft2(kernel)            # named, so numpy never multiplies into it (k * m rounds differently from m * k)
        return np.fft.irfft2(self.spec(m) * k, s=(self.H, self.W)).astype(F32, copy=False)

    def drip(self, length, width, up=False):
        """A streak's kernel: running down (or up) from its source, fading over `length` px."""
        ky = -self.ky if up else self.ky
        return (np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(self.kx / width) ** 2)).astype(F32)

    def box(self, x, y, left, right, up, down):
        """A patch round (x, y), wrapped: its index and each pixel's offset from (x, y)."""
        iy = np.arange(int(y) - up, int(y) + down + 1)
        ix = np.arange(int(x) - left, int(x) + right + 1)
        return np.ix_(iy % self.H, ix % self.W), (ix[None, :] + 0.5 - x).astype(F32), (iy[:, None] + 0.5 - y).astype(F32)

    def patch(self, x, y, rx, ry=None):
        ry = rx if ry is None else ry
        return self.box(x, y, rx, rx, ry, ry)


class Layer:
    """Shapes drawn on the torus at SS x and boxed down: an antialiased mask, 0-1;
    where shapes overlap, the higher value wins."""

    def __init__(self, t):
        self.t, self.shapes = t, []

    def poly(self, pts, v=1.0):
        self.shapes.append(("poly", pts, 0, v))

    def line(self, pts, w, v=1.0):
        self.shapes.append(("line", pts, w, v))

    def ellipse(self, x, y, rx, ry, v=1.0):
        self.shapes.append(("ellipse", [(x - rx, y - ry), (x + rx, y + ry)], 0, v))

    def render(self):
        W, H = self.t.W, self.t.H
        m = Image.new("L", (W * SS, H * SS), 0)
        d = ImageDraw.Draw(m)
        for kind, pts, w, v in sorted(self.shapes, key=lambda s: s[3]):
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            for ox in (-W, 0, W):
                if max(xs) + ox < -w - 2 or min(xs) + ox > W + w + 2:
                    continue
                for oy in (-H, 0, H):
                    if max(ys) + oy < -w - 2 or min(ys) + oy > H + w + 2:
                        continue
                    q = [((x + ox) * SS, (y + oy) * SS) for x, y in pts]
                    fill = round(255 * v)
                    if kind == "poly":
                        d.polygon(q, fill=fill)
                    elif kind == "line":
                        d.line(q, fill=fill, width=max(1, round(w * SS)), joint="curve")
                    else:
                        d.ellipse(q, fill=fill)
        return np.asarray(m.resize((W, H), Image.BOX), F32) / 255


def lblur(a, r):
    """A blur on a small patch (not wrapped: the patch has room round its shape)."""
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), F32) / 255


def lshift(a, dx, dy):
    return np.roll(a, (dy, dx), (0, 1))


def shift(m, dy, dx):
    """np.roll by (dy, dx) px, fractions too: linear between the whole-pixel rolls."""
    out = 0
    fy, fx = math.floor(dy), math.floor(dx)
    for oy, wy in ((fy, 1 - (dy - fy)), (fy + 1, dy - fy)):
        for ox, wx in ((fx, 1 - (dx - fx)), (fx + 1, dx - fx)):
            if wy * wx:
                out = out + wy * wx * np.roll(m, (oy, ox), (0, 1))
    return out


def wobble(pts, r, amp):
    return [(x + r.normal(0, amp), y + r.normal(0, amp)) for x, y in pts]


def weather(rgb, joint, seed):
    """Weather a clean stone tile: `rgb` (H x W x 3, 0-1), `joint` (H x W, 1 in a
    joint). Returns the weathered tile, scaled to TARGET, and a mask of the
    pixels whose colours `save` keeps apart."""
    H, W = joint.shape
    t = Torus(H, W, seed)
    r = t.rng
    img = rgb.astype(F32)
    lum = img @ LUM
    img = mix(img, lum[..., None], GREY)
    clean = img.copy()                                  # what a fresh break shows, before the dirt
    joint = np.clip(joint.astype(F32), 0, 1)
    stone = 1 - joint
    special = np.zeros((H, W), F32)
    fine = t.noise(0.6, feature=60, lo=1.3)             # px grain: the dirt's tooth
    yv = np.arange(H, dtype=F32)[:, None]
    hidden = 1 - smooth(yv, FOOT + 0.4 * DPI, FOOT + 1.3 * DPI)   # under the ground strip and off the sheet: back to clean by the top
    foot = smooth(yv, 0.35 * FOOT, FOOT) * hidden
    xv = np.arange(W, dtype=F32)[None, :]
    inner = (smooth(xv, 0.1 * DPI, 0.6 * DPI) * smooth(TEXT_W - xv, 0.1 * DPI, 0.6 * DPI)
             * smooth(yv, 0.1 * DPI, 0.6 * DPI) * smooth(TEXT_H - yv, 0.1 * DPI, 0.6 * DPI))
    calm = 1 - CALM * inner                             # big dark marks toned down where the sheets are

    def visible_y(lo=0.3, hi=0.3):
        return r.uniform(lo * DPI, FOOT - hi * DPI)

    def margin_x():
        """A column in a side margin that both pages show: just past the text
        area (a right page's outer margin, a left page's binding margin), or
        just before the tile's edge (the left-hand margins, wrapped)."""
        return r.uniform(TEXT_W + 0.08 * DPI, TEXT_W + 0.45 * DPI) if r.random() < 0.5 else r.uniform(W - 0.45 * DPI, W - 0.08 * DPI)

    placed = []

    def place(lo=0.5, hi=0.5, apart=2.2, margin=False):
        """Somewhere on the visible wall (in a side margin if `margin`), `apart`
        in (or as far as it can) from every other mark placed, round the torus:
        the damage spread out, not heaped."""
        best, bd = None, -1.0
        for _ in range(60):
            x, y = (margin_x() if margin else r.uniform(0, W)), visible_y(lo, hi)
            d = min((math.hypot(min(abs(x - px_), W - abs(x - px_)), min(abs(y - py_), H - abs(y - py_))) for px_, py_ in placed),
                    default=1e9)
            if d > bd:
                best, bd = (x, y), d
            if d >= apart * DPI:
                break
        placed.append(best)
        return best

    # ── 2. grime ────────────────────────────────────────────────────────────────
    jf = t.spec(joint)
    near = np.clip(t.blur(jf, 5) * 2.5, 0, 1)           # in a joint and just beside it
    pocket = smooth(t.blur(jf, 3), 0.42, 0.8)           # where joints open or meet: pockets
    del jf
    ledge = joint * np.roll(stone, -3, 0)               # a joint's lower edge: the stone below it takes what runs off
    wash = t.conv(ledge, t.drip(22, 1.2))
    wash = np.clip(wash / np.quantile(wash[::4, ::4][wash[::4, ::4] > 1e-3], 0.9), 0, 1) * stone
    broad = t.noise(2.0, feature=4 * DPI, lo=40)
    patchy = smooth(t.noise(1.6, feature=300, lo=6), -0.4, 1.6)
    rain = t.noise(1.2, feature=600, lo=7, stretch=(0.10, 1.0))           # dirt washed down the faces in long streaks
    blotch = t.noise(1.8, feature=1.2 * DPI, lo=12)                        # dirty patches a stone or two across
    g = (0.42 * foot + 0.36 * smooth(broad, -0.8, 1.8) + 0.38 * smooth(blotch, -0.2, 2.0) + 0.32 * smooth(rain, 0.0, 2.0)
         + 0.40 * near * (0.5 + 0.5 * patchy) + 0.65 * pocket
         + 0.50 * wash * smooth(t.noise(1.4, feature=200, lo=4), -0.8, 0.8))
    img = mix_into(img, img * DIRT, np.clip(g, 0, 1.4))
    img = mix_into(img, img * hexc("#5e5850"), pocket * 0.55)       # soot and dirt packed into the recesses
    del patchy, g, rain, blotch

    # soot and grime run down from the ledges: grey-black stains under a joint,
    # long and streaked, the city's smoke washed off the stone above
    cand = np.flatnonzero(ledge[::2, ::2].ravel() > 0.5)
    src = np.zeros((H, W), F32)
    for c in r.choice(cand, min(len(cand), 110), replace=False):
        yy, xx = divmod(int(c), (W + 1) // 2)
        src[(yy * 2) % H, (xx * 2) % W] += r.uniform(0.3, 1.0)
    sf = t.spec(src)
    runs = t.conv(sf, t.drip(380, 2.5)) + 0.7 * t.conv(sf, t.drip(140, 9.0))
    runs = np.clip(runs / np.percentile(runs[runs > 1e-4], 99), 0, 1)
    runs *= smooth(t.noise(1.0, feature=700, lo=2, stretch=(0.10, 1.0)), -0.6, 1.0)
    img = mix_into(img, img * hexc("#8a857c"), runs * 0.55 * calm)
    img = mix_into(img, img * hexc("#9a948a"), wash * 0.35)          # and the stone just under every ledge
    del src, sf, runs, wash

    # ── 3. damp ──────────────────────────────────────────────────────────────────
    # streaks from the joints: water off a ledge, down the face below
    src = np.zeros((H, W), F32)
    for c in r.choice(cand, min(len(cand), 260), replace=False):
        yy, xx = divmod(int(c), (W + 1) // 2)
        src[(yy * 2) % H, (xx * 2) % W] += r.uniform(0.3, 1.0) * (1 + 1.5 * foot[(yy * 2) % H, 0])
    sf = t.spec(src)
    streaks = t.conv(sf, t.drip(260, 3.0)) + 0.5 * t.conv(sf, t.drip(80, 8.0))
    streaks = np.clip(streaks / np.percentile(streaks[streaks > 1e-4], 99), 0, 1)
    streaks *= smooth(t.noise(1.0, feature=900, lo=2, stretch=(0.10, 1.0)), -0.7, 0.9)
    img = mix_into(img, img * WET, streaks * 0.75)
    edge_s = np.clip(streaks - t.blur(streaks, 2.0), 0, 1)    # a streak dries to a darker edge
    img *= (1 - 0.7 * edge_s)[..., None]
    del src, sf, edge_s

    # wet patches: soft and dark where the stone holds water, a faint tide line
    # where one has dried back
    patch_ = t.noise(1.8, feature=1.6 * DPI, lo=30) + 0.2 * t.noise(1.4, feature=200, lo=5)
    wetp = smooth(patch_, 0.5, 1.8) * (1 - 0.4 * inner)
    img = mix_into(img, img * hexc("#a5a8a1"), wetp * 0.6)
    img = mix_into(img, img * TIDE, np.exp(-((patch_ - 0.45) / 0.035) ** 2) * 0.22 * (1 - 0.4 * inner))
    del patch_

    # rising damp at the foot: darker and wet below a wavy tide line, salt just above it
    tx = np.arange(W) / W
    tide_h = np.zeros(W, F32)
    for k in range(1, 10):
        tide_h += r.normal() / k ** 1.4 * np.sin(2 * np.pi * (k * tx + r.uniform()))
    tide_y = FOOT - (1.25 + 0.3 * tide_h / tide_h.std()) * DPI         # px, per column
    rel = yv - tide_y[None, :] + 4 * t.noise(1.4, feature=60, lo=3)    # px below the tide line
    below = smooth(rel, -6, 40) * hidden
    tidem = np.exp(-(rel / 1.8) ** 2) + 0.45 * np.exp(-((rel - 26) / 1.6) ** 2)   # a second, fainter line where it stood once
    salt = smooth(-rel, 2, 6) * (1 - smooth(-rel, 10, 26))
    brk = smooth(t.noise(1.5, feature=200, lo=4), -1.0, 0.2)
    img = mix_into(img, img * WET, below * 0.50 * (0.7 + 0.3 * smooth(fine, -1, 1)))
    img = mix_into(img, img * hexc("#bdb5a8"), below * smooth(rel, 20, 120) * 0.45)   # and darker, dirtier, lower down
    img = mix_into(img, img * TIDE, np.clip(tidem, 0, 1) * 0.40 * brk)
    img = mix_into(img, SALT * (0.94 + 0.04 * fine)[..., None], salt * 0.30 * brk * smooth(fine, -0.6, 0.6))

    # leaks: a stain run down from a joint, its edge dried to a tide mark, the
    # lower edge scalloped where it ran
    leaks = np.zeros((H, W), F32)
    streaky = t.noise(1.0, feature=300, lo=2, stretch=(0.12, 1.0))
    for _ in range(int(r.integers(3, 5))):
        for _ in range(50):
            yy, xx = divmod(int(r.choice(cand)), (W + 1) // 2)
            x0, y0 = xx * 2.0, yy * 2.0
            if 0.5 * DPI < y0 < FOOT - 3 * DPI:
                break
        R, Lh = r.uniform(35, 70), r.uniform(1.2, 2.4) * DPI
        ix, dx, dy = t.box(x0, y0, int(R * 3), int(R * 3), 8, int(Lh * 1.2))
        u = np.clip(dy / Lh, 0, None)
        wd = R * (0.5 + 1.6 * np.sqrt(np.clip(u, 0, 1)) * (1 - 0.6 * u))   # widening as it runs, then narrowing
        lobes = 0.06 * np.sin(dx / R * 2.3 + r.uniform(0, 6)) + 0.04 * np.sin(dx / R * 5.1 + r.uniform(0, 6))
        d = np.maximum(np.abs(dx) / np.maximum(wd, 1), (u + lobes) / 1.0) + 0.03 * fine[ix]
        inside = smooth(1 - d, 0.0, 0.2) * smooth(dy, -2, 4) * (0.6 + 0.4 * smooth(streaky[ix], -1, 1))
        rings = np.exp(-((d - 1) / 0.012) ** 2) + 0.5 * np.exp(-((d - 0.86) / 0.01) ** 2)
        rings *= smooth(dy, 0, 10)
        sub = img[ix]
        sub = mix(sub, sub * WET, inside * 0.40)
        sub = mix(sub, sub * TIDE, np.clip(rings, 0, 1) * 0.45)
        img[ix] = sub
        leaks[ix] = np.maximum(leaks[ix], inside)
    wet = np.clip(0.6 * below + 1.0 * streaks + 0.5 * leaks + 0.6 * wetp + 0.15 * foot, 0, 1)
    del leaks, streaky, rel, tidem, salt, brk, below, wetp

    # ── 4. mould, algae and fungi ────────────────────────────────────────────────
    colonies = t.noise(1.5, feature=500, lo=8)
    field = colonies + 1.6 * near + 1.1 * wet
    T = np.quantile(field[::4, ::4], 0.95)
    colony = smooth(field, T - 0.5, T + 0.6)
    speck = t.noise(0.2, feature=40, lo=1.1)
    dots = smooth(speck, 2.2 - 1.9 * colony, 2.45 - 1.9 * colony) * smooth(colony, 0.05, 0.3)
    halo = np.clip(t.blur(colony, 10) * 1.3, 0, 1)
    img = mix_into(img, img * MOULD_STAIN, halo * 0.55)
    green = smooth(t.noise(1.8, feature=400, lo=10) + 0.8 * wet, 0.0, 0.8)     # green where it is wet, black where it is not
    mc = mix(MOULD_BLACK, MOULD_GREEN, green[..., None]) * (0.9 + 0.12 * smooth(fine, -1.5, 1.5))[..., None]
    img = mix_into(img, mc, dots * 0.9)
    special = np.maximum(special, (dots > 0.25) * green)
    del colonies, field, speck, halo, mc

    film = smooth(wet, 0.55, 1.0) * smooth(t.noise(1.6, feature=300, lo=6), 0.2, 1.2)
    img = mix_into(img, img * ALGAE, film * 0.45)
    glint = film * smooth(t.noise(0.9, feature=200, lo=1.5, stretch=(0.15, 1.0)), 2.0, 2.6)   # the slime's sheen, running down
    img = mix_into(img, np.minimum(img * 1.25 + 0.04, 1), glint * 0.6)
    special = np.maximum(special, smooth(film, 0.3, 0.45))
    special = np.maximum(special, smooth(film, 0.25, 0.4))
    del film, glint, green

    # fungi: a few small shelves and clusters of caps on the bed joints, where it is wet
    beds = np.flatnonzero((ledge[::3, ::3] > 0.5).ravel() & (wet[::3, ::3].ravel() > 0.15)
                          & (np.repeat(np.arange(0, H, 3), (W + 2) // 3) < FOOT - 0.3 * DPI))
    if len(beds) < 20:
        beds = np.flatnonzero((ledge[::3, ::3] > 0.5).ravel())

    def bed_point():
        yy, xx = divmod(int(r.choice(beds)), (W + 2) // 3)
        return float(xx * 3), float(yy * 3)

    fung = np.zeros((H, W), F32)

    def shelf(cx, cy, w, dep, pal, ang):
        """One small shelf seen from a little above: a fan below its line of
        attachment, zoned in arcs parallel to its margin, a pale rim, a dark lip."""
        zones, rim, under = pal
        rx, ry = int(w / 2) + 10, int(dep) + 12
        ix, dx, dy = t.patch(cx, cy + dep / 2, rx, ry)
        dy = dy + dep / 2
        ca, sa = math.cos(ang), math.sin(ang)
        X, Y = dx * ca + dy * sa, -dx * sa + dy * ca
        th = np.arctan2(Y, X / (w / (2 * dep)))
        lob = 1 + 0.06 * np.sin(int(r.integers(3, 7)) * th + r.uniform(0, 6)) + 0.03 * np.sin(11 * th + r.uniform(0, 6))
        rho = np.hypot(X / (w / 2), Y / dep) / lob
        top = smooth((1 - rho) * dep, -0.8, 0.8) * smooth(Y, -1.0, 1.0)
        lip_rho = np.hypot(X / (w / 2), (Y - 3) / dep) / lob
        lip = smooth((1 - lip_rho) * dep, -0.8, 0.8) * smooth(Y - 3, -1.0, 1.0)
        sil = np.maximum(top, lip)
        sub = img[ix]
        sub *= (1 - 0.45 * lblur(lshift(sil, 4, 6), 3.0))[..., None]       # its shadow, down and right
        sub = mix(sub, under * (0.9 + 0.15 * smooth(-X / (w / 2), -1, 1))[..., None], lip)
        z = rho * int(r.integers(3, 6)) + 0.12 * fine[ix] + 0.15 * np.sin(th * 3)
        band = 0.5 + 0.5 * np.sin(2 * np.pi * z)
        zc = mix(zones[0], zones[1], smooth(band, 0.0, 0.5)[..., None])
        zc = mix(zc, zones[2], (smooth(band, 0.6, 1.0) * smooth(rho, 0.2, 0.9))[..., None])
        zc = mix(zc, rim, smooth(rho, 0.84, 0.95)[..., None])
        zc *= (1 + 0.10 * (1 - rho) - 0.08 * (X / (w / 2)))[..., None]          # lit from the left
        zc *= (1 - 0.3 * smooth(0.2 - rho, 0, 0.2))[..., None]
        sub = mix(sub, zc, top)
        edge = top * (1 - smooth((1 - rho) * dep, 0.6, 1.8))
        sub *= (1 - 0.3 * edge * smooth(Y, 0, 3))[..., None]
        img[ix] = sub
        fung[ix] = np.maximum(fung[ix], sil)

    def caps(cx, cy, n, size, pal):
        """A clump of small domed caps pushing out of a joint, lit from the upper left."""
        cap, dark = pal
        items = sorted([(cy + r.uniform(-2, 4), cx + r.normal(0, size * 0.9), size * r.uniform(0.5, 1.2)) for _ in range(n)])
        for by, bx, cw in items:
            a, b = cw / 2, cw * r.uniform(0.3, 0.45)
            R = int(cw) + 8
            ix, dx, dy = t.patch(bx, by, R)
            nx, ny = dx / a, (dy + b * 0.2) / b
            rr = nx * nx + ny * ny
            dome = smooth((1 - np.sqrt(rr)) * min(a, b), -0.6, 0.6) * smooth(-(dy - b * 0.35), -0.6, 0.6)
            nz = np.sqrt(np.clip(1 - rr, 0, 1))
            lit = np.clip(-0.55 * nx - 0.55 * ny + 0.63 * nz, 0, 1)
            cc = mix(dark, cap, smooth(lit, 0.1, 0.7)[..., None]) * (0.85 + 0.25 * lit)[..., None]
            cc = mix(cc, np.minimum(cap * 1.25, 1), (smooth(lit, 0.88, 1.0) * 0.7)[..., None])     # wet: a glint
            sub = img[ix]
            sub *= (1 - 0.40 * lblur(lshift(dome, 3, 3), 2.0) * (1 - dome))[..., None]
            sub = mix(sub, cc, dome)
            outline = dome * (1 - smooth((1 - np.sqrt(rr)) * min(a, b), 0.4, 1.4))
            sub *= (1 - 0.25 * outline)[..., None]
            img[ix] = sub
            fung[ix] = np.maximum(fung[ix], dome)

    for _ in range(int(r.integers(3, 5))):
        x0, y0 = bed_point()
        pal = SHELVES[int(r.integers(len(SHELVES)))]
        W0 = r.uniform(45, 85)
        specs = []
        for k in range(int(r.integers(1, 4))):
            w = W0 * r.uniform(0.6, 1.0) * (1 - 0.15 * k)
            specs.append((x0 + r.normal(0, W0 * 0.3), y0 + k * W0 * r.uniform(0.25, 0.4), w, w * r.uniform(0.32, 0.45), r.normal(0, 0.1)))
        for cx, cy, w, dep, ang in sorted(specs, key=lambda s: -s[1]):
            shelf(cx, cy, w, dep, pal, ang)
    for _ in range(int(r.integers(3, 6))):
        x0, y0 = bed_point()
        caps(x0, y0, int(r.integers(3, 9)), r.uniform(9, 16), CAPS[int(r.integers(len(CAPS)))])
    special = np.maximum(special, fung)

    # ── 5. burns ─────────────────────────────────────────────────────────────────

    def scorch(x0, y0, R, plume=True):
        """A burn: soot thrown out round it in rays, its hottest middle burnt
        pale and crazed, a brown scorch round the soot, soot rising above it."""
        up = int(R * (8 if plume else 2.5))
        ix, dx, dy = t.box(x0, y0, int(R * 3.5), int(R * 3.5), up, int(R * 2.5))
        n1, n2 = fine[ix], t_mid[ix]
        th = np.arctan2(dy, dx)
        rays = sum(np.sin(k * th + r.uniform(0, 6)) * r.uniform(0.4, 1.0) / k ** 0.2 for k in (5, 9, 14, 23, 37))
        d = np.hypot(dx, dy) / R * (1 + 0.18 * n2) / (1 + 0.11 * rays)
        blast = np.exp(-1.3 * d * d)
        calc = np.exp(-(d / 0.32) ** 2)                            # burnt pale where it was hottest
        soot = np.clip(1.25 * blast, 0, 1) * (1 - 0.5 * calc)
        if plume:
            h = np.clip(-dy, 0, None) / R                          # R's above the burn
            sway = R * 0.25 * np.sin(h * 0.9 + r.uniform(0, 6)) * h ** 0.5
            wd = R * (0.6 + 0.35 * h)
            pl = np.exp(-((dx - sway) / wd) ** 2) * np.exp(-h / 3.5) * smooth(-dy, -R * 0.6, R * 0.6)
            pl *= 0.45 + 0.55 * smooth(t_up[ix], -1.2, 1.0)        # the soot laid in tongues
            soot = soot + 1.0 * pl
        soot = np.clip(soot * (0.8 + 0.25 * smooth(n1, -1.5, 1.5)), 0, 1)
        halo = np.exp(-(d / 1.9) ** 2)
        sub = img[ix]
        k = calm[ix]
        sub = mix(sub, sub * SCORCH, halo * 0.60 * k)
        sub = mix(sub, SOOT * (0.92 + 0.16 * smooth(n1, -1.5, 1.5))[..., None], soot * 0.70 * k)
        sub = mix(sub, CALCINED * (0.95 + 0.08 * smooth(n1, -1, 1))[..., None], calc * 0.45)
        craze = calc * (1 - smooth(np.abs(t_craze[ix]), 0.03, 0.10))    # heat crazing: a net of fine cracks
        sub *= (1 - 0.40 * craze)[..., None]
        img[ix] = sub

    t_mid = t.noise(1.8, feature=120, lo=6)
    t_up = t.noise(1.2, feature=300, lo=3, stretch=(0.18, 1.0))
    t_craze = t.noise(1.6, feature=40, lo=2.5)
    scorch(*place(2.2, 0.6, margin=True), r.uniform(40, 60))
    for _ in range(int(r.integers(1, 3))):
        scorch(*place(2.2, 0.6), r.uniform(40, 70))
    for _ in range(int(r.integers(2, 4))):
        scorch(*place(0.5, 0.5, 1.5), r.uniform(12, 22), plume=False)
    if r.random() < 0.85:                                  # a flame's lick along the wall
        L = Layer(t)
        (x, y), a = place(2.0, 1.0), r.uniform(-0.25, 0.25) + (math.pi if r.random() < 0.5 else 0)
        pts = [(x, y)]
        for _ in range(int(r.integers(14, 26))):
            a += r.normal(0, 0.08)
            x, y = x + 18 * math.cos(a), y + 18 * math.sin(a) + r.normal(0, 1.5)
            pts.append((x, y))
        L.line(pts, 16)
        lick = t.spec(L.render())
        band = np.clip(t.blur(lick, 14) * 1.6, 0, 1)
        rise = t.conv(lick, t.drip(90, 18, up=True))
        rise = np.clip(rise / rise.max() * 1.3, 0, 1) * smooth(t_up, -1.0, 1.2)
        soot = np.clip(0.75 * band + 0.55 * rise, 0, 1) * (0.75 + 0.25 * smooth(fine, -1, 1))
        img = mix_into(img, img * SCORCH, np.clip(t.blur(lick, 30) * 2.5, 0, 1) * 0.45 * calm)
        img = mix_into(img, SOOT * (0.9 + 0.2 * smooth(fine, -1.5, 1.5))[..., None], soot * 0.75 * calm)
        del L, lick, band, rise, soot

    def oil(x0, y0, R):
        """A grease stain: oil splashed or leaked from a fixing, soaked dark into
        the stone round where it hit, its edge soft and its middle darkest, a
        run or two down from it, a dull sheen where it is still tacky."""
        ix, dx, dy = t.box(x0, y0, int(R * 3), int(R * 3), int(R * 2.5), int(R * 9))
        d = np.hypot(dx, dy * 1.15) / R * (1 + 0.22 * t_mid[ix]) + 0.04 * fine[ix]
        soak = np.exp(-1.4 * d * d)
        core = smooth(0.6 - d, 0.0, 0.3)
        run = 0
        for _ in range(int(r.integers(1, 4))):
            o, wr, ln = r.normal(0, R * 0.35), r.uniform(2.5, 6.0), R * r.uniform(2.0, 7.0)
            wob = o + 2.5 * np.sin(dy / r.uniform(25, 60) + r.uniform(0, 6))
            run = run + np.exp(-((dx - wob) / wr) ** 2) * smooth(dy, 0, R * 0.5) * np.exp(-np.clip(dy, 0, None) / ln) * r.uniform(0.6, 1.0)
        stain = np.clip(0.9 * soak + 0.9 * run, 0, 1) * calm[ix]
        sub = img[ix]
        sub = mix(sub, sub * OIL_FILM, stain * 0.85)
        sub = mix(sub, OIL * (0.92 + 0.16 * smooth(fine[ix], -1.5, 1.5))[..., None], core * 0.55 * calm[ix])
        sheen = core * smooth(t_mid[ix] + 0.6 * fine[ix], 1.2, 2.0)
        img[ix] = mix(sub, np.minimum(sub * 1.5 + 0.03, 1), sheen * 0.35)

    oil(*place(1.5, 1.2, margin=True), r.uniform(25, 40))
    for _ in range(int(r.integers(1, 3))):
        oil(*place(1.2, 1.2), r.uniform(18, 45))
    del t_mid, t_up, t_craze

    # ── 6. damage: recesses cut into the stone, lit from the upper left ─────────
    def carve(m, sigma, k, floor=1.0, alpha=0.9):
        """Cut a recess (mask m, 0-1) and light it: fresh stone at its floor
        (`floor` x as bright), its walls a slope `sigma` px wide, lit from the
        upper left: the upper-left wall in shade, the lower-right wall lit."""
        nonlocal img
        h = -t.blur(m, sigma) + 0.04 * fine * m                    # depth, roughened
        gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) / 2
        gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) / 2
        light = np.clip(1 + k * (gx + gy), 0.35, 1.4)
        fresh = mix(clean * FRESH / hexc("#c8c5bf"), img * 1.04, 0.45) * floor   # broken open, but dirty
        fresh = mix(fresh, img * 0.85, joint * 0.7)            # the mortar, where it crosses a joint
        img = mix_into(img, fresh, m * alpha)
        img *= light[..., None]

    dmg = Layer(t)       # recesses
    crk = Layer(t)       # cracks: dark lines
    rad = []             # bullet pocks: (x, y, r)

    # chipped arrises: a flake broken from a stone's edge
    edges = np.flatnonzero(((near[::3, ::3] > 0.25) & (near[::3, ::3] < 0.6) & (joint[::3, ::3] < 0.1)).ravel())
    for _ in range(50):
        yy, xx = divmod(int(r.choice(edges)), (W + 2) // 3)
        cx, cy, R = xx * 3.0, yy * 3.0, r.uniform(4, 12)
        k = int(r.integers(5, 8))
        ang = np.sort(r.uniform(0, 2 * np.pi, k))
        dmg.poly([(cx + R * r.uniform(0.5, 1.2) * math.cos(q), cy + R * r.uniform(0.4, 1.0) * math.sin(q)) for q in ang], r.uniform(0.6, 0.9))

    # cracks: wandering across stones and joints, branching
    def crack(x, y, a, length, w, depth=0):
        pts = [(x, y)]
        s = 0
        while s < length:
            a += r.normal(0, 0.35)
            st = r.uniform(5, 12)
            x, y, s = x + st * math.cos(a), y + st * math.sin(a), s + st
            pts.append((x, y))
            if depth < 2 and r.random() < 0.05:
                crack(x, y, a + r.choice([-1, 1]) * r.uniform(0.5, 1.0), (length - s) * r.uniform(0.3, 0.6), max(1.0, w * 0.7), depth + 1)
        crk.line(pts, w, r.uniform(0.7, 1.0))

    for _ in range(int(r.integers(4, 7))):
        crack(r.uniform(0, W), r.uniform(0, H), r.uniform(0, 2 * np.pi), r.uniform(120, 420), r.uniform(1.3, 2.0))

    # claw marks: sets of 3-4 gouges torn into the stone, each set raked at its
    # own spacing and its strokes of different lengths; some fresh, some old and
    # grimed over. Laid out here (the flakes, the torn tines and the grit along
    # them go in with the other damage); cut after it (`gouge`).
    strokes = []
    grit = (Layer(t), Layer(t))          # dark grit, pale grit, spilled along the lips
    sets = [(True, True), (True, False), (False, False), (False, r.random() < 0.5)]   # (big, in a side margin)
    ages = r.permutation([0.05, 0.35, 0.7, 0.9])
    claw_at = []
    for (big, edge), age in zip(sets, ages):
        L = r.uniform(600, 950) if big else r.uniform(350, 550)
        x, y = place(L / 2 / DPI + 0.3, L / 2 / DPI + 0.4, 2.6, margin=edge)
        claw_at.append((x, y, age))
        a = (r.uniform(1.3, 1.5) if edge else r.uniform(0.85, 1.4)) * r.choice([1, -1])   # raked down, aslant
        a += math.pi if (r.random() < 0.15 and not edge) else 0
        n = int(r.integers(3, 5))
        gap = r.uniform(36, 55) if big else r.uniform(26, 38)
        offs = np.cumsum([0] + [gap * r.uniform(0.7, 1.4) for _ in range(n - 1)])
        offs -= offs.mean()
        bend = r.normal(0, 0.2)
        for k, o in enumerate(offs):
            mid_ = 1 - 0.25 * abs(k - (n - 1) / 2) / max(1, (n - 1) / 2)
            lk = L * mid_ * r.uniform(0.7, 1.05)
            ak = a + r.normal(0, 0.04)
            along = -lk / 2 + r.normal(0, 0.07 * L)
            sx_ = x - o * math.sin(a) + along * math.cos(ak)
            sy_ = y + o * math.cos(a) + along * math.sin(ak)
            w = r.uniform(24, 34) if big else r.uniform(17, 23)
            g = dict(x=sx_, y=sy_, a=ak, L=lk, w=w, bend=bend + r.normal(0, 0.05), age=float(np.clip(age + r.normal(0, 0.08), 0, 1)),
                     e_in=r.uniform(0.03, 0.08), e_out=r.uniform(0.25, 0.45), bleed=False,
                     jag=[np.interp(np.linspace(0, 1, 160), np.linspace(0, 1, 40), np.convolve(r.normal(0, 1, 40), np.ones(3) / 1.7, "same"))
                          for _ in range(2)],
                     torn=r.uniform(0, 6, 4))
            strokes.append(g)

            def at(u, off=0.0, g=g):
                c = g["bend"] * g["L"] * 0.25 * (u * u - u) + off
                return (g["x"] + u * g["L"] * math.cos(g["a"]) - c * math.sin(g["a"]),
                        g["y"] + u * g["L"] * math.sin(g["a"]) + c * math.cos(g["a"]))
            fresh_ = 1 - g["age"]
            for _ in range(int(r.poisson(lk / 70 * (0.3 + fresh_)))):     # flakes torn from the lips, most near the bite
                u = min(r.beta(1.3, 2.6), 0.85)
                side = r.choice([-1, 1])
                R = w * r.uniform(0.3, 0.75)
                px_, py_ = at(u, side * (w / 2 * (1 - u) ** 0.4 + R * 0.25))
                dmg.poly([(px_ + R * math.cos(q) * r.uniform(0.5, 1.1), py_ + R * math.sin(q) * r.uniform(0.5, 1.1))
                          for q in np.sort(r.uniform(0, 2 * np.pi, 6))], r.uniform(0.55, 0.8))
            prev = None                                                    # and the stone's edge where it crossed a joint
            for u in np.linspace(0.02, 0.8, 120):
                px_, py_ = at(u)
                j = joint[int(py_) % H, int(px_) % W] > 0.5
                if prev is not None and j != prev and r.random() < 0.3:
                    R = w * r.uniform(0.3, 0.6)
                    dmg.poly([(px_ + R * math.cos(q) * r.uniform(0.5, 1.1), py_ + R * math.sin(q) * r.uniform(0.5, 1.1))
                              for q in np.sort(r.uniform(0, 2 * np.pi, 6))], 0.7)
                prev = j
            for _ in range(int(r.integers(1, 4))):                         # the claw lifting out: torn tines past the taper
                o2 = r.normal(0, w * 0.2)
                u0 = r.uniform(0.86, 0.93)
                crk.line(wobble([at(u, o2 * (1 + 6 * (u - u0))) for u in np.linspace(u0, u0 + r.uniform(40, 90) / lk, 4)], r, 0.5),
                         r.uniform(0.9, 1.4), 0.5 + 0.3 * fresh_)
            for _ in range(int(r.integers(1, 4))):                         # and where it bit in: torn, not cut
                u = r.uniform(-0.01, 0.05)
                R = w * r.uniform(0.35, 0.8)
                px_, py_ = at(u, r.normal(0, w * 0.3))
                dmg.poly([(px_ + R * math.cos(q) * r.uniform(0.5, 1.1), py_ + R * math.sin(q) * r.uniform(0.5, 1.1))
                          for q in np.sort(r.uniform(0, 2 * np.pi, 7))], r.uniform(0.6, 0.85))
            for _ in range(int(r.poisson(lk / 4 * (0.15 + fresh_)))):      # grit, spilled along the lips and fallen below them
                u = r.uniform(0.03, 0.85)
                side = r.choice([-1, 1])
                px_, py_ = at(u, side * (w / 2 * (1 - u) ** 0.5 + abs(r.normal(0, 5))))
                py_ += r.exponential(5)
                rr_ = r.uniform(0.6, 1.8)
                grit[int(r.random() < 0.35)].ellipse(px_, py_, rr_ * r.uniform(0.7, 1.3), rr_, r.uniform(0.6, 1.0))
    young = [g for g in strokes if g["age"] < 0.3] or strokes
    young[int(r.integers(len(young)))]["bleed"] = True                 # blood dragged down one groove, or two
    if r.random() < 0.6:
        strokes[int(r.integers(len(strokes)))]["bleed"] = True
    claw_blood = np.zeros((H, W), F32)
    grain = t.noise(1.4, feature=40, lo=3)              # the lips' roughness: broken, not fuzzy

    def gouge(g):
        """Cut one stroke: a groove torn into the stone, its ends ragged (a
        blunt bite where the claw went in, a long drag to a point where it
        lifted out), skating over the joints; its upper-left wall in shadow
        and a shadow cast across the floor, the lower-right lip lit; the floor
        a little lighter than the face when fresh, dark and packed with dirt
        when old; dried blood dragged along it in `bleed`."""
        x0, y0, a, L, w, age = g["x"], g["y"], g["a"], g["L"], g["w"], g["age"]
        ca, sa = math.cos(a), math.sin(a)
        cx, cy = x0 + L * ca / 2, y0 + L * sa / 2
        rx, ry = int(abs(L * ca) / 2 + 2 * w + 30 + abs(g["bend"]) * L * 0.07), int(abs(L * sa) / 2 + 2 * w + 30 + abs(g["bend"]) * L * 0.07)
        ix, dx, dy = t.box(cx, cy, rx, rx, ry, ry)
        px_, py_ = dx + cx - x0, dy + cy - y0
        u = (px_ * ca + py_ * sa) / L
        uc = np.clip(u, 0, 1)
        v = -px_ * sa + py_ * ca - g["bend"] * L * 0.25 * (uc * uc - uc)
        z = v / (w / 2)
        tA, tB, tC, tD = g["torn"]
        torn_in = 0.5 * np.sin(3.1 * z + tA) + 0.4 * np.sin(7.7 * z + tB)
        torn_out = 0.5 * np.sin(2.3 * z + tC) + 0.5 * np.sin(6.1 * z + tD)
        taper = smooth(u + g["e_in"] * 0.5 * torn_in, 0, g["e_in"]) * smooth(1 - u + 0.04 * torn_out, 0, g["e_out"]) ** 0.8
        jag = np.where(v < 0, np.interp(uc, np.linspace(0, 1, 160), g["jag"][0]), np.interp(uc, np.linspace(0, 1, 160), g["jag"][1]))
        hw = w / 2 * taper * (1 + 0.22 * jag) + 1.4 * grain[ix] * smooth(taper, 0.05, 0.3)
        over = np.clip(lblur(joint[ix], 1.5) * 1.8, 0, 1)                  # the joint is recessed: the claw skates over it
        m = smooth(hw - np.abs(v), -0.6, 0.6) * smooth(hw, 0.3, 1.2) * (1 - over)
        if age > 0.6:
            m = lblur(m, 0.5 + 0.8 * age)                                  # old: worn soft
        q = np.clip(np.abs(v) / np.maximum(hw, 0.5), 0, 1)
        prof = 1 - smooth(q, 0.35, 1.0)                                    # a floor, and steep walls
        h = -(0.3 + 0.7 * taper) * w * (0.38 - 0.12 * age) * prof * m      # px deep
        gy, gx = np.gradient(h)
        shade = np.clip((1 + gx + gy) / np.sqrt(1 + gx * gx + gy * gy), 0.0, 1.6)
        shade = 0.38 + 0.62 * shade                                        # Lambert, the light from the upper left, and a little ambient
        cast = 0
        for k in range(1, 9):                                              # the shadow the upper-left lip casts on the floor
            cast = np.maximum(cast, lshift(h, k, k) - h - 1.6 * k)
        cast = smooth(cast, 0.0, 1.5) * m
        lip = (1 - m) * np.maximum.reduce([lshift(m, k, k) for k in (1, 2, 3)]) * smooth(taper, 0.1, 0.5)
        dull = smooth(fine[ix], -1.5, 1.5)
        sub = img[ix]
        floor = sub * (1.02 - 0.28 * age) * (0.93 + 0.08 * dull)[..., None]
        floor = mix(floor, floor * DIRT * hexc("#cfc6b8"), (0.3 + 0.7 * age) * (0.6 + 0.4 * dull))   # dirty; old, dirt packed in
        sub = mix(sub, floor, m)
        sub *= mix(np.ones_like(shade), shade, (1 - 0.35 * age))[..., None]
        sub *= (1 - (0.55 - 0.2 * age) * cast)[..., None]
        sub *= (1 + (0.42 - 0.25 * age) * lip)[..., None]
        sub *= (1 - 0.18 * (1 - m) * np.maximum.reduce([lshift(m, -k, -k) for k in (1, 2)]) * (1 - 0.5 * age))[..., None]   # the shaded arris
        img[ix] = sub
        if g["bleed"]:
            u0 = r.uniform(0.0, 0.2)
            u1 = u0 + r.uniform(0.25, 0.5)
            lanes = sum(np.exp(-((z - c) / r.uniform(0.15, 0.3)) ** 2) * r.uniform(0.6, 1.0) for c in r.uniform(-0.6, 0.6, 3))
            bb = m * smooth(u, u0, u0 + 0.04) * (1 - smooth(u, u1 - 0.2, u1 + 0.1 * torn_out)) * np.clip(0.35 + lanes, 0, 1)
            bb *= smooth(fine[ix] + 1.5 * (1 - (u - u0) / (u1 - u0 + 1e-3)), -0.2, 1.0)    # thinner as it drags, flaking
            claw_blood[ix] = np.maximum(claw_blood[ix], np.clip(bb, 0, 1))

    # bullet pocks: singles, and a burst or two
    for i in range(int(r.integers(6, 10))):
        rad.append((*place(0.4, 0.4, 1.2, margin=i < 2), r.uniform(5, 8)))
    for i in range(2):
        cx, cy = place(0.8, 1.0, margin=i == 0)
        a0 = r.uniform(0, np.pi) if i else r.uniform(1.2, 1.9)        # in a margin, a burst up the wall
        for _ in range(int(r.integers(3, 7))):
            s = r.normal(0, 70)
            rad.append((cx + s * math.cos(a0) + r.normal(0, 15), cy + s * math.sin(a0) + r.normal(0, 15), r.uniform(5, 7)))
    for x, y, rr in rad:
        k = int(r.integers(6, 10))
        ang = np.linspace(0, 2 * np.pi, 2 * k, endpoint=False)
        dmg.poly([(x + rr * (2.1 if i % 2 else 1.6) * r.uniform(0.75, 1.15) * math.cos(q),
                   y + rr * (2.1 if i % 2 else 1.6) * r.uniform(0.75, 1.15) * math.sin(q)) for i, q in enumerate(ang)], 0.85)
        for _ in range(int(r.integers(2, 5))):
            q = r.uniform(0, 2 * np.pi)
            l0, l1 = rr * 1.8, rr * r.uniform(3.0, 5.5)
            crk.line([(x + l0 * math.cos(q), y + l0 * math.sin(q)),
                      (x + (l0 + l1) / 2 * math.cos(q + r.normal(0, 0.1)), y + (l0 + l1) / 2 * math.sin(q + r.normal(0, 0.1))),
                      (x + l1 * math.cos(q), y + l1 * math.sin(q))], 1.3, 0.8)

    # something scratched into it: a tally or two, and a glyph or two
    scr = Layer(t)

    def tally(x, y):                                    # fours struck through, the last group not done
        h, sp = r.uniform(70, 95), r.uniform(11, 15)
        left, gx = int(r.integers(7, 19)), x
        while left > 0:
            k = min(5, left)
            for i in range(min(k, 4)):
                bx = gx + i * sp + r.normal(0, 2)
                scr.line(wobble([(bx, y + r.normal(0, 3)), (bx + r.normal(0, 2), y + h / 2), (bx + r.normal(0, 3), y + h + r.normal(0, 3))], r, 0.6), 2.2)
            if k == 5:
                scr.line(wobble([(gx - 8, y + h * 0.72), (gx + 3 * sp + 8, y + h * 0.25)], r, 1.0), 2.2)
            left -= k
            gx += 4 * sp + r.uniform(18, 26)

    def glyph(x, y):
        size = r.uniform(150, 210)
        for stroke in GLYPHS[int(r.integers(len(GLYPHS)))]:
            pts = [(x + u * size * 0.8, y + v * size) for u, v in stroke]
            for k in range(2):                                   # a blade scratches twice, near the same line
                o = k * r.uniform(1.5, 2.5)
                scr.line(wobble([(px_ + o, py_ + o * 0.5) for px_, py_ in pts], r, 1.2), 1.8 - 0.4 * k, 1.0 - 0.3 * k)

    tally(*place(0.8, 1.5, margin=True))
    glyph(*place(0.8, 1.5))
    if r.random() < 0.5:
        tally(*place(0.8, 1.5))
    else:
        glyph(*place(0.8, 1.5, margin=True))

    D = np.clip(dmg.render(), 0, 1)
    D = smooth(t.blur(D, 0.8) + 0.12 * fine * (D > 0.05), 0.3, 0.7) * np.maximum(D, 0.6)   # ragged edges
    carve(D, 1.6, 2.6)
    S_ = scr.render()
    carve(S_ * 0.7, 0.9, 1.8, floor=0.97, alpha=0.6)
    C = crk.render()
    img *= (1 - 0.55 * C)[..., None]
    img *= (1 + 0.10 * np.clip(shift(C, 1.2, 1.2) - C, 0, 1))[..., None]     # the crack's lower lip, lit
    for g in strokes:
        gouge(g)
    Gd, Gl = grit[0].render(), grit[1].render()
    img *= (1 - 0.45 * Gd)[..., None]
    img = mix_into(img, np.minimum(img * 1.16, 1), Gl)
    del Gd, Gl, grit
    for x, y, rr in rad:                     # the hole, and the powder round it
        ix, dx, dy = t.patch(x, y, int(rr * 5))
        d = np.hypot(dx, dy)
        hole = smooth(rr * 0.7 - d, -0.6, 0.6)
        bowl = smooth(rr * 1.7 - d, -1, 1) * np.clip((dx + dy) / (d + 1e-3) / 1.41, -1, 1)   # the crater: shaded up-left, lit down-right
        sub = img[ix]
        sub *= (1 - 0.10 * np.exp(-(d / (rr * 3.5)) ** 2))[..., None]
        sub *= (1 + 0.12 * bowl)[..., None]
        sub = mix(sub, HOLE * (0.9 + 0.2 * smooth(dx + dy, 0, rr))[..., None], hole)
        img[ix] = sub
    del D, S_, C, dmg, crk, scr, grain

    # ── 7. blood: dried, small ───────────────────────────────────────────────────
    blood = {"dry": Layer(t), "old": Layer(t)}

    def drop(lay, x, y, a, length, width, v, tail=0.0):
        n = 24
        u = np.linspace(0, 2 * np.pi, n, endpoint=False)
        ex = length / 2 * np.cos(u) + tail * np.clip(np.cos(u), 0, 1) ** 10
        ey = width / 2 * np.sin(u) * (1 - 0.5 * np.clip(np.cos(u), 0, 1) ** 10 * (tail > 0))
        ca, sa = math.cos(a), math.sin(a)
        lay.poly([(x + px_ * ca - py_ * sa, y + px_ * sa + py_ * ca) for px_, py_ in zip(ex, ey)], v)

    def spatter(lay, cx, cy, R, count, spread, aim, cone):
        """An impact: a small stain, a spray of drops flung from it (round near it,
        long and tailed further out), a run or two down from it."""
        drop(lay, cx, cy, r.uniform(0, np.pi), R * 2.0, R * 1.5, 0.95)
        for _ in range(int(r.integers(2, 4))):
            q = r.uniform(0, 2 * np.pi)
            drop(lay, cx + R * 0.7 * math.cos(q), cy + R * 0.7 * math.sin(q), q, R * 1.1, R * 0.7, 0.9)
        for _ in range(count):
            q = aim + r.normal(0, cone)
            d = R + r.exponential(spread)
            size = max(1.2, r.lognormal(math.log(2.4), 0.45) * (1.3 - 0.6 * min(1.0, d / (3 * spread))))
            el = min(1 + d / spread, 4.0) * r.uniform(0.9, 1.1)
            drop(lay, cx + d * math.cos(q), cy + d * math.sin(q), q, size * el, size, r.uniform(0.6, 0.95),
                 tail=size * el * r.uniform(0.3, 0.7) if el > 1.6 else 0.0)
        for _ in range(int(r.integers(0, 2))):          # a run, thin, ending in a bead
            x, y = cx + r.normal(0, R * 0.5), cy + R * 0.5
            w, left, right = r.uniform(1.8, 2.8), [], []
            for _ in range(int(r.uniform(6, 22))):
                x += r.normal(0, 0.25)
                left.append((x - w / 2, y))
                right.append((x + w / 2, y))
                y += 2
            lay.poly(left + right[::-1], 0.85)
            lay.ellipse(x, y, w * 0.7, w * 0.9, 0.95)

    claw_at.sort(key=lambda c: c[2])                     # by the freshest claw marks: whatever made them was hurt, or did the hurting
    for (cx, cy, _), a in zip(claw_at[:2], ("dry", "old")):
        spatter(blood[a], cx + r.normal(0, 80), cy + r.normal(0, 80), r.uniform(4, 8), int(r.integers(12, 26)), r.uniform(22, 45),
                r.uniform(0, 2 * np.pi), 0.6)
    for i in range(2):
        spatter(blood["old" if i else "dry"], *place(1.0, 1.0, margin=i == 0), r.uniform(3, 6), int(r.integers(8, 16)), r.uniform(18, 32),
                r.uniform(0, 2 * np.pi), 0.7)
    for i in range(int(r.integers(7, 11))):             # specks, in little groups
        gx, gy = place(0.4, 0.4, 1.2, margin=i < 3)
        aim = r.uniform(0, 2 * np.pi)
        for _ in range(int(r.integers(2, 7))):
            q, d = aim + r.normal(0, 0.5), r.uniform(0, 40)
            s = r.uniform(1.2, 2.6)
            drop(blood["old" if r.random() < 0.6 else "dry"], gx + d * math.cos(q), gy + d * math.sin(q), q, s * r.uniform(1, 2.5), s, r.uniform(0.6, 0.9))
    smear = np.zeros((H, W), F32)                       # a smear: something dragged along the wall, low down
    x0, y0 = r.uniform(0, W), r.uniform(FOOT - 3.0 * DPI, FOOT - 0.8 * DPI)
    length, width, ang = r.uniform(140, 240), r.uniform(16, 24), r.uniform(-0.3, 0.3) + (math.pi if r.random() < 0.5 else 0)
    ix, dx, dy = t.patch(x0, y0, int(length * 0.6) + 10)
    u = (dx * math.cos(ang) + dy * math.sin(ang)) / length + 0.5
    v = (-dx * math.sin(ang) + dy * math.cos(ang)) / width
    lanes = r.uniform(-0.75, 0.75, int(r.integers(3, 5)))              # claws or fingers dragged through it
    stripes = sum(np.exp(-((v - c + 0.08 * fine[ix]) / r.uniform(0.07, 0.12)) ** 2) * r.uniform(0.6, 1.0) for c in lanes)
    contact = np.exp(-((u - 0.06) / 0.06) ** 2 - (v / 0.8) ** 4 - 0.6 * fine[ix] ** 2 / 4)   # where it was pressed to the wall
    smear[ix] = np.clip(0.95 * contact + 0.85 * np.clip(stripes, 0, 1) * np.clip(1 - u, 0, 1) ** 0.8 * smooth(u, 0.0, 0.08), 0, 1) * smooth(1 - u, 0.0, 0.1)

    B = {a: lay.render() for a, lay in blood.items()}
    B["old"] = np.maximum(B["old"], smear)
    B["dry"] = np.maximum(B["dry"], claw_blood)
    for a, b in B.items():
        b = b * (0.7 + 0.3 * smooth(fine, -1.5, 1.0)) * (fine < 2.2)          # dried, flaking
        rim = np.clip(b - t.blur(b, 1.2), 0, 1)                             # the darker rim a drop dries to
        thick = np.clip(smooth(b, 0.5, 1.0) + 0.6 * rim, 0, 1)
        img *= mix(np.ones(3, F32), BLOOD_FILM[a], smooth(b, 0.0, 0.5)[..., None])
        img = mix_into(img, BLOOD_DEEP[a] * (0.95 + 0.1 * smooth(fine, -1, 1))[..., None], thick * 0.85)
        special = np.maximum(special, smooth(b, 0.05, 0.2))
    del B, smear, claw_blood

    # ── 1. dim: the faces dulled (the lighter half of the tile pulled toward its
    # median, so nothing reads as clean stone), then the whole tile to TARGET
    lum = img @ LUM
    med = np.median(lum[::4, ::4])
    img *= np.where(lum > med, (med + (lum - med) * DULL) / np.maximum(lum, 1e-3), 1)[..., None]
    img *= TARGET / img.reshape(-1, 3).mean(0, dtype=np.float64).astype(F32)
    return np.clip(img, 0, 1), special > 0.5


def save(img, special, path, colours=200, reserved=48):
    """Quantise to an exact palette with no dither and write a palette PNG: the
    wall's pixels get colours - reserved entries cut from them, the saturated
    things (`special`) the rest, cut from their own pixels, so a speck of blood
    or a fungus keeps its colour instead of the nearest grey (a third of them
    for the warm ones, the blood, a sliver of the tile beside the greens)."""
    rgb8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

    def cut(px, n):
        px = px[:: max(1, len(px) // 2_000_000)]
        return Image.fromarray(px.reshape(1, -1, 3)).quantize(colors=n, method=Image.Quantize.MEDIANCUT,
                                                              dither=Image.Dither.NONE).getpalette()[:3 * n]

    warm = special & (rgb8[..., 0].astype(np.int16) - rgb8[..., 2] > 20)    # blood: a sliver beside the greens, so it gets its own
    cool = special & ~warm
    pal = cut(rgb8[~special], colours - reserved)
    for part, n in ((warm, reserved // 3), (cool, reserved - reserved // 3)):
        if part.any():
            pal += cut(rgb8[part], n)
    ref = Image.new("P", (1, 1))
    ref.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
    out = Image.fromarray(rgb8, "RGB").quantize(palette=ref, dither=Image.Dither.NONE)
    out.putpalette(pal)
    out.save(path, optimize=True)
    return out
