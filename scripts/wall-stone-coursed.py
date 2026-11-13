"""Draw the three coursed stone walls, 2 (ashlar), 4 (running bond) and 6
(square setts), as images/wall-2.png, wall-4.png and wall-6.png.

    python3 scripts/wall-stone-coursed.py [2 4 6]   (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css             (then: the CSS for every wall, these included)

These three were cut from the painted sheet (source-art/wall-sheet.png) by
wall-tiles.py and printed at 240 DPI with about 110 DPI of real detail. They
are drawn here instead, at DPI (300, the print bar), in the same look: a line
drawing of dressed stone, ash (--bg) faces with grey joints, its tones first
matched to the brick tile's own; then weathered by wall_grime.py, as walls
1, 3 and 5 are, into the city's dim, grimy, damaged stone.

    2  ashlar: big dressed blocks in pairs of courses, some blocks the height
       of both (jumpers), the rest in two courses whose joints break.
    4  running bond: small bricks, each course half a brick along.
    6  square setts, each row half a sett along, so it reads as a wall, not
       paving.

Each tile is a whole number of blocks and courses (about 9in x 12in), and
everything in it is periodic, so it repeats without a seam either way: the
noise is filtered in the Fourier domain, blurs are circular convolutions,
and the blocks and every stroke are laid with wrap-around.

One block renderer draws all three. Each block is a rounded box; its signed
distance in from the edge (E) is laid on the tile, wobbled a little and bitten
at the arrises and corners (chips). From E and a few noise fields comes a
darkness field, back to front:
1. The joint: a narrow light gap between two blocks.
2. The arris: a dark line round each block, broken in places, a little
   heavier on the shadow side (light from the upper left).
3. A stippled fringe inside the arris where the dressing is rough.
4. Chips: the broken-away corner or edge, stippled and dark.
5. The face: sparse speckle in clusters, pits, and the tooling (chisel
   strokes, a drafted margin, a few hairline cracks), all faint.
The darkness is then mapped, level by level, onto the clean brick's tones
(wall_grime.clean_brick: --bg times a grey line drawing), as wall-tiles.py's
`tint` mapped the sheet's: the clean stone gets the brick's histogram and
darkest grey. wall_grime.py then weathers it with the joints' mask (grime,
damp, mould and fungi, burns, damage, dried blood), dims it, and saves it
as an exact palette PNG with no dither.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wall_grime  # noqa: E402  (the grime and damage, shared with wall-stone-rubble.py)

ROOT = Path(__file__).resolve().parents[1]
DPI = 300                   # px an inch: the print bar
F32 = np.float32
BG = (0xC8, 0xC5, 0xBF)     # --bg (ash concrete), the brick's colour
SS = 4                      # strokes are drawn at SS x and boxed down
LEVELS = 4096               # darkness levels the tone match works in
TONE_STEP = 0.003           # the tones are rounded to this (a level of luminance): the palette's size

# Each wall: its tile in blocks, its joint and arris, its face. Lengths in px at DPI.
WALLS = {
    2: dict(seed=2, joint=0.6, line=3.0, corner=1.0, wobble=0.7, bite=3.0, fringe=8.0, speck=2.0, chips=0.12,
            flecks=1.6, draft=0.45, tool=0.25, cracks=12, midline=0.0, burst=0.0),
    4: dict(seed=4, joint=0.8, line=2.4, corner=1.0, wobble=0.5, bite=1.4, fringe=6.0, speck=2.15, chips=0.10,
            flecks=1.6, draft=0.0, tool=0.0, cracks=10, midline=0.0, burst=0.2),
    6: dict(seed=6, joint=2.8, line=2.6, corner=0.8, wobble=0.3, bite=0.6, fringe=6.0, speck=2.1, chips=0.15,
            flecks=1.6, draft=0.40, tool=0.15, cracks=8, midline=0.45, burst=0.0),
}
# Each tile is about 9in x 12in, about a page across and taller than one, so a
# page shows no mark of the grime twice; a whole number of blocks and courses.
COURSE_4 = 0.1875 * DPI     # running bond: a course (0.19in, the sheet's), 64 to the tile
BRICK_4 = 0.5 * DPI         # and a brick (0.5in), 18 to the tile: 9in x 12in
SETT_6 = 170                # square setts: a cell (0.567in, the sheet's), 16 x 22 to the tile: 9.07in x 12.47in
PAIRS_2 = 10                # ashlar: pairs of courses (about 1.2in each) in its 9in x 12in tile


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


class Tile:
    """A W x H torus: the blocks' distance field, noise and wrapped strokes on it."""

    def __init__(self, W, H, seed):
        self.W, self.H = W, H
        self.rng = np.random.default_rng(seed)
        self.FY = np.fft.fftfreq(H).astype(F32)[:, None]
        self.FX = np.fft.rfftfreq(W).astype(F32)[None, :]
        self.E = np.full((H, W), -40, F32)          # px in from the nearest block's edge (< 0 in a joint)
        self.ID = np.full((H, W), -1, np.int32)     # which block
        self.blocks = []                            # (x0, y0, x1, y1, angle), px, the box before its joint is taken off

    def noise(self, beta, feature, lo=None, stretch=(1.0, 1.0)):
        """Periodic 1/f^beta noise as a z-score: no feature larger than `feature`
        px, none smaller than `lo` px; `stretch` > 1 elongates it along that axis."""
        spec = np.fft.rfft2(self.rng.standard_normal((self.H, self.W)).astype(F32))
        fy, fx = self.FY * stretch[1], self.FX * stretch[0]
        f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)
        spec = spec / f ** beta
        if lo:
            spec = spec * np.exp(-(f * lo) ** 2)
        out = np.fft.irfft2(spec, s=(self.H, self.W)).astype(F32)
        out -= out.mean()
        return out / out.std()

    def blur(self, m, sigma):
        k = np.exp(-2 * np.pi ** 2 * sigma * sigma * (self.FX ** 2 + self.FY ** 2))
        return np.fft.irfft2(np.fft.rfft2(m) * k, s=(self.H, self.W)).astype(F32)

    def block(self, x0, y0, x1, y1, joint, corner, angle=0.0):
        """Lay a block filling the box (x0, y0)-(x1, y1) less half a joint each side:
        a rounded box, turned by `angle` (radians) about its centre, wrapped."""
        k = len(self.blocks)
        self.blocks.append((x0, y0, x1, y1, angle))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        hx, hy = (x1 - x0) / 2 - joint, (y1 - y0) / 2 - joint
        M = 8
        ix = np.arange(int(math.floor(x0)) - M, int(math.ceil(x1)) + M + 1)
        iy = np.arange(int(math.floor(y0)) - M, int(math.ceil(y1)) + M + 1)
        X = (ix[None, :] + 0.5 - cx).astype(F32)
        Y = (iy[:, None] + 0.5 - cy).astype(F32)
        if angle:
            c, s = math.cos(angle), math.sin(angle)
            X, Y = c * X + s * Y, -s * X + c * Y
        qx = np.abs(X) - (hx - corner)
        qy = np.abs(Y) - (hy - corner)
        e = -(np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - corner)
        at = np.ix_(iy % self.H, ix % self.W)
        old = self.E[at]
        win = e > old
        self.E[at] = np.where(win, e, old)
        self.ID[at] = np.where(win, k, self.ID[at])

    def strokes(self, lines):
        """Polylines [(points, width px, value 0-1)], antialiased (drawn at SS x and
        boxed down) and wrapped; where they cross, the darker wins."""
        W, H = self.W, self.H
        m = Image.new("L", (W * SS, H * SS), 0)
        d = ImageDraw.Draw(m)
        for pts, w, v in sorted(lines, key=lambda l: l[2]):
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            for ox in (-W, 0, W):
                if max(xs) + ox < -w or min(xs) + ox > W + w:
                    continue
                for oy in (-H, 0, H):
                    if max(ys) + oy < -w or min(ys) + oy > H + w:
                        continue
                    d.line([((x + ox) * SS, (y + oy) * SS) for x, y in pts], fill=round(255 * v),
                           width=max(1, round(w * SS)), joint="curve")
        return np.asarray(m.resize((W, H), Image.BOX), F32) / 255


# ── the bonds ─────────────────────────────────────────────────────────────────
def running_bond(t, p):
    """Wall 4: bricks in courses, each course half a brick along the last; a
    head joint wanders a px or two, a bed joint a px."""
    r = t.rng
    rows = round(t.H / COURSE_4)
    cols = round(t.W / BRICK_4)
    beds = np.arange(rows + 1) * COURSE_4 + np.r_[r.normal(0, 0.8, rows), 0]
    beds[-1] = beds[0] + t.H
    for j in range(rows):
        heads = np.arange(cols + 1) * BRICK_4 + (j % 2) * BRICK_4 / 2 + np.r_[r.normal(0, 3.5, cols), 0]
        heads[-1] = heads[0] + t.W
        for i in range(cols):
            t.block(heads[i], beds[j], heads[i + 1], beds[j + 1], p["joint"], p["corner"], r.normal(0, 0.003))


def setts(t, p):
    """Wall 6: square setts, every other row half a sett along; each sett sits a
    little off true, so the joints vary as they do between hand-laid stones."""
    r = t.rng
    cols, rows = t.W // SETT_6, t.H // SETT_6
    for j in range(rows):
        for i in range(cols):
            x0 = i * SETT_6 + (j % 2) * SETT_6 / 2 + r.normal(0, 0.8)
            y0 = j * SETT_6 + r.normal(0, 0.8)
            s = SETT_6 + r.normal(0, 1.5)
            t.block(x0, y0, x0 + s, y0 + s, p["joint"] + abs(r.normal(0, 0.6)), p["corner"], r.normal(0, 0.006))


def ashlar(t, p):
    """Wall 2: pairs of courses. Along each pair, jumpers (blocks the height of
    both) between runs of blocks a course high, the upper and lower course's
    joints breaking; no head joint sits over one in the pair below."""
    r = t.rng
    hp = r.uniform(0.85, 1.15, PAIRS_2)
    hp = hp * t.H / hp.sum()
    tops = np.r_[0, np.cumsum(hp)]
    gap = 0.14 * DPI                                # the least a joint is from one above or below it
    prev_low, first_up = None, None

    def split(g):
        n = max(1, round(g / (r.uniform(0.66, 0.86) * DPI)))
        w = r.uniform(0.8, 1.2, n)
        return np.r_[0, np.cumsum(w / w.sum() * g)]

    def dist(a, b):
        d = np.abs(np.asarray(a)[:, None] - np.asarray(b)[None, :]) % t.W
        return np.minimum(d, t.W - d).min() if len(a) and len(b) else t.W

    for k in range(PAIRS_2):
        for _ in range(400):
            items, total = [], 0.0
            while total < t.W:
                if items and items[-1][0] == "S" and r.random() < 0.5:
                    items.append(("D", r.uniform(0.8, 1.1) * DPI))
                else:
                    items.append(("S", int(r.integers(1, 4)) * r.uniform(0.66, 0.86) * DPI))
                total += items[-1][1]
            if items[-1][0] == "S" and len(items) > 1:      # two runs meet round the wrap: one run
                items[0] = ("S", items[0][1] + items.pop()[1])
                total = sum(w for _, w in items)
            scale, off = t.W / total, r.uniform(0, t.W)
            up, low, x = [], [], off                        # (x0, x1) of each block, and which course
            jumpers = []
            ok = True
            for kind, w in items:
                w *= scale
                if kind == "D":
                    jumpers.append((x, x + w))
                else:
                    for _ in range(40):
                        a, b = split(w), split(w)
                        if len(a) == 2 and len(b) == 2 or dist(a[1:-1], b[1:-1]) > gap:
                            break
                    else:
                        ok = False
                    up += [(x + a[i], x + a[i + 1]) for i in range(len(a) - 1)]
                    low += [(x + b[i], x + b[i + 1]) for i in range(len(b) - 1)]
                x += w
            heads_up = [b[0] for b in up + jumpers]
            heads_low = [b[0] for b in low + jumpers]
            if prev_low is not None and dist(heads_up, prev_low) < gap:
                ok = False
            if k == PAIRS_2 - 1 and dist(heads_low, first_up) < gap:
                ok = False
            if ok:
                break
        prev_low = heads_low
        if k == 0:
            first_up = heads_up
        y0, y1 = tops[k], tops[k + 1]
        ym = y0 + (y1 - y0) * r.uniform(0.44, 0.56)
        for a, b in jumpers:
            t.block(a, y0, b, y1, p["joint"], p["corner"], r.normal(0, 0.002))
        for a, b in up:
            t.block(a, y0, b, ym, p["joint"], p["corner"], r.normal(0, 0.002))
        for a, b in low:
            t.block(a, ym, b, y1, p["joint"], p["corner"], r.normal(0, 0.002))


# ── the face ──────────────────────────────────────────────────────────────────
def chisel(t, b, frac, lines):
    """Tooling on a block's face: long, faint scratches from the claw chisel,
    near parallel on one block, wandering a little."""
    r = t.rng
    x0, y0, x1, y1, _ = b
    w, h = x1 - x0, y1 - y0
    a0 = r.choice([-1, 1]) * r.uniform(0.25, 0.7)
    for _ in range(r.poisson(frac * max(1.0, w * h / (0.25 * DPI * DPI)))):
        a = a0 + r.normal(0, 0.12)
        x, y = r.uniform(x0 + 12, x1 - 12), r.uniform(y0 + 12, y1 - 12)
        L = r.uniform(0.25, 0.7) * w
        pts = [(x, y)]
        for _ in range(int(L / 8)):
            a += r.normal(0, 0.06)
            x, y = x + 8 * math.cos(a), y + 8 * math.sin(a)
            if not (x0 + 8 < x < x1 - 8 and y0 + 8 < y < y1 - 8):
                break
            pts.append((x, y))
        if len(pts) > 2:
            lines.append((pts, r.uniform(1.0, 1.4), r.uniform(0.45, 0.75)))


def burst(t, b, lines):
    """A spalled spot on a brick: a few short cracks out from a point near its foot."""
    r = t.rng
    x0, y0, x1, y1, _ = b
    cx, cy = r.uniform(x0 + 20, x1 - 20), r.uniform(y0 + 0.55 * (y1 - y0), y1 - 8)
    for _ in range(int(r.integers(3, 6))):
        a = r.uniform(-math.pi, 0) if r.random() < 0.8 else r.uniform(0, math.pi)
        l = r.uniform(5, 12)
        lines.append(([(cx, cy), (cx + l * math.cos(a), cy + l * math.sin(a))], r.uniform(1.0, 1.5), r.uniform(0.5, 0.8)))


def flecks(t, b, rate, lines):
    """Short flecks and hooks on a block's face, a few px long, and ticks struck
    in from its arris."""
    r = t.rng
    x0, y0, x1, y1, _ = b
    for _ in range(r.poisson(rate * (x1 - x0) * (y1 - y0) / (0.1 * DPI * DPI))):
        x, y, a = r.uniform(x0 + 8, x1 - 8), r.uniform(y0 + 8, y1 - 8), r.uniform(0, 2 * math.pi)
        pts = [(x, y)]
        for _ in range(int(r.integers(1, 4))):
            a += r.normal(0, 0.9)
            s = r.uniform(2.0, 5.0)
            x, y = x + s * math.cos(a), y + s * math.sin(a)
            pts.append((x, y))
        lines.append((pts, r.uniform(1.3, 2.2), r.uniform(0.75, 1.0)))
    for _ in range(r.poisson(rate * 2 * ((x1 - x0) + (y1 - y0)) / (0.6 * DPI))):
        k = int(r.integers(4))
        u = r.uniform(0.1, 0.9)
        x, y, a = ((x0 + u * (x1 - x0), y0 + 4, math.pi / 2), (x0 + u * (x1 - x0), y1 - 4, -math.pi / 2),
                   (x0 + 4, y0 + u * (y1 - y0), 0.0), (x1 - 4, y0 + u * (y1 - y0), math.pi))[k]
        a += r.normal(0, 0.3)
        l = r.uniform(4, 11)
        lines.append(([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], r.uniform(1.3, 2.0), r.uniform(0.75, 1.0)))


def crack(t, lines):
    r = t.rng
    x, y, a = r.uniform(0, t.W), r.uniform(0, t.H), r.uniform(0, 2 * math.pi)
    pts = [(x, y)]
    for _ in range(int(r.integers(4, 12))):
        a += r.normal(0, 0.5)
        s = r.uniform(5, 12)
        x, y = x + s * math.cos(a), y + s * math.sin(a)
        pts.append((x, y))
    lines.append((pts, r.uniform(1.0, 1.4), r.uniform(0.45, 0.7)))


def draw(n):
    p = WALLS[n]
    if n == 4:
        t = Tile(round(18 * BRICK_4), round(64 * COURSE_4), p["seed"])
        running_bond(t, p)
    elif n == 6:
        t = Tile(16 * SETT_6, 22 * SETT_6, p["seed"])     # an even count of rows, so the half-lap wraps
        setts(t, p)
    else:
        t = Tile(9 * DPI, 12 * DPI, p["seed"])
        ashlar(t, p)
    r = t.rng
    W, H = t.W, t.H
    print(f"  wall {n}: {len(t.blocks)} blocks", flush=True)

    # the edge: a little wobble, the dressing's roughness, then chips bitten from the arris
    E0 = t.E + p["wobble"] * t.noise(1.8, 90, lo=6) + 0.3 * t.noise(1.0, 20, lo=1.5)
    chip_n = t.noise(1.4, 60, lo=3)
    bite = p["bite"] * smooth(chip_n, 1.7, 2.7) * np.exp(-np.maximum(E0, 0) / 4.0)
    blobs = np.zeros((H, W), F32)                   # the corners knocked off
    for x0, y0, x1, y1, _ in t.blocks:
        size = min(x1 - x0, y1 - y0)
        for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            if r.random() < p["chips"]:
                R = size * r.uniform(0.03, 0.07)
                ix = np.arange(int(cx - 3 * R), int(cx + 3 * R) + 1)
                iy = np.arange(int(cy - 3 * R), int(cy + 3 * R) + 1)
                g = np.exp(-(((ix[None, :] + 0.5 - cx) ** 2 + (iy[:, None] + 0.5 - cy) ** 2) / (2 * R * R)))
                at = np.ix_(iy % H, ix % W)
                blobs[at] = np.maximum(blobs[at], (g * R * r.uniform(1.8, 2.6)).astype(F32))
    rough = t.noise(1.2, 30, lo=1.5)
    E1 = E0 - (bite + blobs * (1 + 0.3 * rough)) * smooth(E0, -3, 3)
    face = smooth(E1, -0.6, 0.6)                    # the stone, antialiased
    body = smooth(E0, -0.6, 0.6)                    # the stone as dressed, before the chips
    chipped = np.clip(body - face, 0, 1)

    # the arris: a dark line round each block, heavier on its shadow side (lower
    # right) than its lit one, broken here and there. It is the darkest thing on
    # the wall: everything else stays under LINE, so the tone match gives the
    # lines the brick's darkest greys.
    gy, gx = np.gradient(E0)
    side = np.clip((gx + gy) / 1.41, -1, 1)         # +1 on a top-left edge (lit), -1 on a bottom-right one
    lw = p["line"] * (1 + 0.25 * t.noise(1.5, 50, lo=4)) * (1 - 0.3 * side)
    lw = np.maximum(lw, 1.2)
    line = face * (1 - smooth(E1, lw - 0.6, lw + 0.6))
    brk = t.noise(1.6, 80, lo=6)
    grain = t.noise(0.0, 10, lo=1.0)                # px-scale grain: the stone's tooth
    blot = t.noise(0.0, 10, lo=2.8) + 0.45 * grain  # ragged 2-5px blots: stipple, speckle
    blot /= blot.std()
    strength = np.clip(1 - 0.85 * smooth(brk + 0.25 * grain, 1.4, 2.1) - 0.25 * np.clip(side, 0, 1), 0, 1)
    dark = line * (0.55 + 0.45 * strength) * smooth(strength, 0.0, 0.25)

    # the fringe: stipple just inside the arris, where the cluster field says
    inner = np.maximum(E1 - lw, 0)
    cluster = t.noise(2.0, 140, lo=10)
    fr = np.exp(-inner / p["fringe"]) * smooth(cluster, -1.2, 1.0)
    stip = smooth(blot + 3.4 * fr - 2.9, 0.0, 0.4) * face * (E1 > lw)
    dark = np.maximum(dark, 0.8 * stip)

    # chips: the broken face falls back to joint, a dot or two left in it
    dark = np.maximum(dark, chipped * 0.6 * smooth(blot, 2.2, 2.5))

    # the face: speckle in clusters, the odd pit, short flecks and hooks
    thr = p["speck"] - 0.6 * smooth(cluster, 0.0, 2.0)
    dark = np.maximum(dark, face * 0.85 * smooth(blot, thr, thr + 0.4))
    patch = smooth(t.noise(1.8, 160, lo=12), 0.6, 2.2)      # dry-brush patches: the dressing's roughness
    dark = np.maximum(dark, face * 0.8 * smooth(blot + 1.6 * patch, 2.5, 2.9))
    pit = t.noise(0.0, 10, lo=2.8)
    dark = np.maximum(dark, face * 0.7 * smooth(pit, 3.6, 3.8))

    # tooling: chisel strokes, flecks, a drafted margin, a few hairline cracks
    lines = []
    for b in t.blocks:
        if r.random() < p["burst"]:
            burst(t, b, lines)
        chisel(t, b, p["tool"], lines)
        flecks(t, b, p["flecks"], lines)
    for _ in range(p["cracks"]):
        crack(t, lines)
    marks = t.strokes(lines) * smooth(grain, -1.3, -0.5)    # dry: broken by the stone's tooth
    dark = np.maximum(dark, 0.85 * marks * smooth(inner, 1.5, 4))
    if p["draft"]:
        drafted = np.asarray(r.random(len(t.blocks)) < p["draft"])[np.maximum(t.ID, 0)]
        dd = r.uniform(9, 14, len(t.blocks))[np.maximum(t.ID, 0)]
        dl = (1 - np.abs(E1 - dd) / 0.8).clip(0, 1)
        part = smooth(t.noise(1.8, 120, lo=8), -0.2, 0.4)    # it runs along part of the edge, not all of it
        dark = np.maximum(dark, drafted * dl * part * 0.55 * smooth(grain, -1.2, -0.6))

    # the joint: lighter than the face
    joint = (1 - face) * (1 - chipped)
    D = dark - joint * (0.25 + 0.05 * grain)
    if p["midline"]:                                # a hairline down the middle of a wide joint: its pointing
        mid = smooth(-E0, p["joint"] - 1.3, p["joint"] - 0.5) * smooth(strength, 0.0, 0.3)
        D = np.maximum(D, joint * mid * p["midline"])
    return t, D, 1 - smooth(E1, lw - 0.6, lw + 0.6)     # and the joint: the gap and the arris line round it


def brick_tones():
    """The clean brick's pixels (wall_grime.clean_brick) as multiples of --bg, darkest first."""
    a = np.asarray(wall_grime.clean_brick(), F32)
    lum = a @ np.array([0.299, 0.587, 0.114], F32)
    return np.sort(lum.ravel() / (np.array(BG, F32) @ np.array([0.299, 0.587, 0.114], F32)))


def tint(D, tones):
    """Map darkness onto the brick's tones, level by level: each level takes the
    tone at the middle of its share of the tile (darkest first), as --bg times it.
    A palette image: levels that land on one colour share its index."""
    lo, hi = float(D.min()), float(D.max())
    q = (LEVELS - 1) - np.clip(np.round((D - lo) / (hi - lo) * (LEVELS - 1)), 0, LEVELS - 1).astype(np.int32)
    count = np.bincount(q.ravel(), minlength=LEVELS)
    mid = (np.cumsum(count) - count / 2) / q.size
    tone = tones[np.minimum((mid * len(tones)).astype(int), len(tones) - 1)]
    tone = np.round(tone / TONE_STEP) * TONE_STEP          # about a hundred tones: one colour each
    cols = np.minimum(255, np.round(np.array(BG)[None, :] * tone[:, None])).astype(np.uint8)
    palette, index = np.unique(cols, axis=0, return_inverse=True)
    out = Image.fromarray(index.reshape(-1)[q].astype(np.uint8), "P")
    out.putpalette(palette.ravel().tolist())
    return out


def main():
    walls = [int(a) for a in sys.argv[1:]] or sorted(WALLS)
    tones = brick_tones()
    for n in walls:
        t, D, joint = draw(n)
        stone = np.asarray(tint(D, tones).convert("RGB"), F32) / 255
        del D
        rgb, special = wall_grime.weather(stone, joint, seed=WALLS[n]["seed"] * 100 + 7)
        path = ROOT / f"images/wall-{n}.png"
        out = wall_grime.save(rgb, special, path)
        avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
        print(f"images/wall-{n}.png  {t.W}x{t.H}  {t.W / DPI:.2f}x{t.H / DPI:.2f}in  {len(out.getcolors())} colours  "
              f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  {path.stat().st_size / 1e6:.2f}MB", flush=True)


if __name__ == "__main__":
    main()
