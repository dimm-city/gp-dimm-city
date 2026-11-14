"""Draw wall 14, the Proxy's wall (`@page wall-14`), as images/wall-14.png:
wall 6's square setts, with what a priest's rites leave on a wall.

    python3 scripts/wall-proxy.py        (from the package root; needs numpy, Pillow and images/wall-6.png)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

The stone is wall 6's (scripts/wall-stone-coursed.py, weathered by
wall_grime.py), and it is loaded from images/wall-6.png, not drawn again: the
tile is two of wall 6's side by side (18.13in x 12.47in, wider than a spread
and taller than a page), so away from a mark every pixel is wall 6's own. It
is not drawn at double width because wall_grime lays its marks out for one
text-anchored page (its calm text area, its margin columns, a fixed count of
claw sets and burns): at twice the width that gives a sparser wall that is no
longer wall 6. So draw wall 6 first (draw-walls.py does).

Wall 6 is placed from a page's text corner; this wall is anchored to the
sheet (wall-tiles.py's ALIGNED), so a spread is one wall, its two pages show
the tile's two halves and a mark carries on across the spine. The stone is
rolled by a left page's outer and top margins (ROLL), so it lies under a left
page exactly as wall 6 does, its foot on the ground strip; a right page's
text area is one sett (0.57in) along from wall 6's.

The marks, at the page's scale (0.9in to 3in across), each kind made its own
way and no two of a kind alike, placed at random and spaced apart (`place`:
each kind dealt to both pages, the first of a kind on each page near the
page's edge, where no sheet covers it; all of them on the spread, so what
wraps round the tile lands in the part of it no page shows), back to front:
1. Soot rings: something burned in a circle against the wall. A blackened
   ring with a hard, ragged edge, crisp inside (what stood there kept the
   soot off) and licked outward in tongues, long above it and short below,
   uneven and broken round its length, soot spat round it and risen above
   it, a brown scorch round it. Inside, the stone it shielded is a little
   cleaner, or is scorched, sooty, burnt pale and crazed, or holds a second ring.
2. Candle scorches: a row of three to seven soot tongues, each a flame's
   shape risen from a small burnt spot where a flame stood by the wall, of
   different heights, swaying.
3. Cracks from a point: a crushed pit, flakes spalled off round it, and five
   to nine cracks out from it, wide at the pit and tapering to hairlines,
   wandering, branching, stepping along a joint where they meet one; some
   linked by ring cracks, some old and packed with dirt.
4. Ritual knife cuts: tapered cuts in the stone, dark, the lower lip lit,
   skating over the joints, rubbed with ash; arranged as a rite would, not
   counted: ribs either side of an empty spine, a spiral of cuts, a column
   of chevrons, a lattice, a triangle with a cut in from each side.
5. Burned sigils: invented symbols (`sigil`: a frame and a core, no letters
   and no real religious signs) branded into the stone with something hot:
   charred strokes with ragged edges, knobs where the iron dwelt, flecks of
   pale ash left in them, the joints showing through, the stone burnt brown
   beside each and a lick of soot above it.
Everything is drawn wrapped, so the tile repeats without a seam. A pixel no
mark touches keeps wall 6's palette index; the marks get the palette's
remaining entries, cut from their own pixels (an exact palette PNG, no dither).
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wall_grime import DPI, F32, Layer, Torus, hexc, mix, smooth  # noqa: E402  (the torus, wrapped shapes, the burns' colours' kin)

ROOT = Path(__file__).resolve().parents[1]
SEED = 14
SETT = 170                              # wall 6's sett cell, px (wall-stone-coursed.py's SETT_6)
SHEET_W, SHEET_H = 8.625 * DPI, 11.25 * DPI
GROUND = 0.6 * DPI                      # the ground strip at the sheet's foot
ROLL = (round(0.625 * DPI), round(0.625 * DPI))   # a left page's top and outer margins (dc-palette.css), px: down, along
IN = DPI

SOOT = hexc("#3a3632")                  # soot at its thickest: a warm dark grey, not black (ink)
CHAR = hexc("#36312d")                  # charred stone
SCORCH = hexc("#b3936f")                # the brown round a burn, multiplied
BURN = hexc("#a47c56")                  # and hard by a brand, where the stone is burnt brown
ASH = hexc("#b5aca3")                   # stone burnt pale, ash left on it
RUB = hexc("#a59e95")                   # ash rubbed into the cuts, multiplied

# ── the stone: wall 6, twice across ──────────────────────────────────────────
src = Image.open(ROOT / "images/wall-6.png")
assert src.mode == "P", "images/wall-6.png is a palette image"
idx = np.asarray(src)
N6 = int(idx.max()) + 1
pal6 = np.array(src.getpalette()[:3 * N6], np.uint8).reshape(-1, 3)
idx = np.roll(np.tile(idx, (1, 2)), ROLL, (0, 1))
H, W = idx.shape
stone8 = pal6[idx]
img = stone8.astype(F32) / 255
rng = np.random.default_rng(SEED)
t = Torus(H, W, SEED + 1)
u = rng.uniform


def joint_at(x, y):
    """Is (x, y) in a joint of wall 6's bond, and which: 'bed' (level) or 'head' (upright)."""
    yy, xx = (y - ROLL[0]) % H, (x - ROLL[1]) % (W // 2)
    bed = min(yy % SETT, SETT - yy % SETT)
    xs = (xx - (int(yy // SETT) % 2) * SETT / 2) % SETT
    head = min(xs, SETT - xs)
    return None if min(bed, head) > 4 else ("bed" if bed <= head else "head")


yy = (np.arange(H) - ROLL[0]) % H
xx = (np.arange(W) - ROLL[1]) % (W // 2)
bed = np.minimum(yy % SETT, SETT - yy % SETT).astype(F32)[:, None]
xs = (xx[None, :] - ((yy // SETT) % 2)[:, None] * (SETT / 2)) % SETT
joint = 1 - smooth(np.minimum(bed, np.minimum(xs, SETT - xs)).astype(F32), 3, 7)    # 1 in a joint
del yy, xx, bed, xs

fine = t.noise(0.6, feature=60, lo=1.3)                         # px grain
mid = t.noise(1.8, feature=120, lo=6)                           # patches a few tenths of an inch across
ragged = t.noise(1.4, feature=40, lo=3)                         # a burnt edge's raggedness
tongue = t.noise(1.2, feature=300, lo=3, stretch=(0.18, 1.0))   # soot laid in tongues, up the wall
crazing = t.noise(1.6, feature=40, lo=2.5)

# ── where the marks go ───────────────────────────────────────────────────────
placed = []     # (x, y, room, kind)


def place(kind, room, page, edge, head=0.0):
    """A place for a mark `room` px in radius on the left (0) or right (1) page
    of the spread, near the page's edge if `edge` (its side margins, its head,
    the band over the ground: what no sheet covers), as far as it can be from
    every other mark and further from its own kind. The tile is wider than the
    spread and taller than the sheet: a mark is kept where what wraps round
    the tile lands in the part no page shows (`head`: the least it may be from
    the top, for what rises above it)."""
    best, score = None, -1e9
    for _ in range(400):
        x, y = u(0.2 * IN, SHEET_W - 0.2 * IN), u(0.35 * IN, SHEET_H - GROUND - 0.35 * IN)
        if edge:
            band = int(rng.integers(4))
            if band < 2:
                x = u(0.1 * IN, 0.8 * IN) if band else SHEET_W - u(0.1 * IN, 0.8 * IN)
            else:
                y = u(0.2 * IN, 0.7 * IN) if band == 2 else u(9.6 * IN, 10.3 * IN)
        x = min(max(x + page * SHEET_W, room - (W - 2 * SHEET_W) + 10, 0.55 * room), W - room - 10, 2 * SHEET_W - 0.55 * room)
        y = max(y, head, 0.55 * room)                   # and most of it on the sheet
        s = min((((min(abs(x - px), W - abs(x - px)) ** 2 + min(abs(y - py), H - abs(y - py)) ** 2) ** 0.5 - 0.7 * (room + pr))
                 / ((4.5 if pk == kind else 0.9) * IN) for px, py, pr, pk in placed), default=9.0)
        if s > score:
            best, score = (x, y), s
        if s >= 1:
            break
    placed.append((*best, room, kind))
    return best


def spots(kind, rooms, heads=None):
    """A place for each mark of a kind: dealt to the two pages in turn, the first on each page at its edge."""
    first = int(rng.integers(2))
    return [place(kind, room, (i + first) % 2, i < 2, heads[i] if heads is not None else 0.0) for i, room in enumerate(rooms)]


def harmonics(th, ks, fall=0.5):
    """A wavy function of the angle, about -1 to 1."""
    h = sum(rng.normal() / k ** fall * np.sin(k * th + u(0, 6.3)) for k in ks)
    return h / (np.abs(h).max() + 1e-6)


# ── 1. soot rings ────────────────────────────────────────────────────────────
print("soot rings, candle scorches", flush=True)
SOOT_M = np.zeros((H, W), F32)      # soot
HALO_M = np.zeros((H, W), F32)      # the brown scorch
ASH_M = np.zeros((H, W), F32)       # stone burnt pale
CRAZE_M = np.zeros((H, W), F32)     # and crazed
CLEAN_M = np.zeros((H, W), F32)     # stone something kept the soot and grime off


def stamp(field, ix, m):
    field[ix] = np.maximum(field[ix], np.where(m < 0.03, 0, np.clip(m, 0, 1)))


RISE = 4.0      # R's above a ring's middle that its soot rises


def ring(x, y, R, inside):
    pad = int(R * 2.3)
    ix, dx, dy = t.box(x, y, pad, pad, int(R * RISE), pad)
    th, d = np.arctan2(dy, dx), np.hypot(dx, dy)
    e = d - R * (1 + 0.035 * harmonics(th, (2, 3, 4, 5, 6)))               # px outside the ring's line: not a true circle
    up = np.clip(-dy / np.maximum(d, 1), 0, 1)                             # 1 at the ring's top
    w = R * u(0.07, 0.12) * (1 + 0.45 * harmonics(th, (1, 2, 3, 5, 7)))    # the ring's own width
    strength = 0.3 + 0.7 * smooth(harmonics(th, (1, 2, 3, 4)), -0.75, -0.1)               # broken round its length
    spikes = np.clip(harmonics(th, range(9, 46), fall=0.3), 0, 1) ** 1.3   # flames licked out from it, and up: long tongues above, short below
    reach = w * (0.7 + (1.2 + 5.5 * up ** 1.5) * spikes + 1.0 * up)
    band = np.clip(np.where(e < 0, 1 + e / (0.9 * w), np.exp(-np.clip(e, 0, None) / reach)), 0, 1)
    grit = 0.5 + 0.5 * smooth(fine[ix] + 0.7 * ragged[ix], -1.0, 0.8)
    black = smooth(band * (0.3 + 0.7 * strength) + 0.16 * ragged[ix] + 0.10 * fine[ix], 0.42, 0.56)   # blackened: a hard, ragged edge
    specks = smooth(fine[ix], 1.9, 2.2) * np.exp(-np.abs(e) / (4 * w))                             # and soot spat round it
    hh = np.clip(-dy / R, 0, None)                                         # R's above its middle
    rise = (smooth(e, 0, w) * smooth(hh, 0.2, 1.0) * np.exp(-(dx / (R * u(0.85, 1.05))) ** 2)
            * np.exp(-np.clip(hh - 1, 0, None) / u(0.6, 1.2)) * (1 - smooth(hh, RISE - 0.8, RISE - 0.1))
            * (0.2 + 0.8 * smooth(tongue[ix], -0.8, 1.0)))
    soot = black * (0.75 + 0.25 * grit) + 0.3 * band * strength * grit + 0.7 * specks + u(0.2, 0.32) * rise
    halo = np.where(e < 0, 0.8 * np.exp(e / (2.5 * w)), 0.8 * np.exp(-e / (0.5 * reach + 1.5 * w)))
    within = smooth(-e, 0.3 * w, 1.2 * w)
    if inside == "shielded":                    # what stood there kept the wall behind it clean
        stamp(CLEAN_M, ix, 0.25 * within * (0.6 + 0.4 * smooth(mid[ix], -1, 1)))
    elif inside == "burnt":                     # a fire in a ring: scorched within, sooty in patches, burnt pale at its heart
        heart = np.exp(-(d / (0.6 * R)) ** 2) * smooth(mid[ix] + 0.4 * fine[ix], -1.2, 0.6)
        halo = np.maximum(halo, 0.8 * within)
        soot = soot + 0.55 * within * smooth(mid[ix] + 0.5 * ragged[ix], 0.0, 1.2) * grit
        stamp(ASH_M, ix, 0.8 * heart)
        stamp(CRAZE_M, ix, within * np.exp(-(d / (0.75 * R)) ** 2))
    else:                                       # a second ring within the first
        e2 = d - R * u(0.5, 0.62) * (1 + 0.05 * harmonics(th, (2, 3, 5)))
        w2 = w * u(0.6, 0.9)
        soot = soot + smooth(np.exp(-(e2 / w2) ** 2) * (0.3 + 0.7 * smooth(harmonics(th, (1, 2, 3)), -0.6, 0.1)) + 0.16 * ragged[ix], 0.4, 0.55)
        halo = np.maximum(halo, 0.5 * within)
    stamp(SOOT_M, ix, soot)
    stamp(HALO_M, ix, halo)


radii = rng.permutation(np.linspace(0.5, 1.3, 5)) * u(0.9, 1.1, 5) * IN
hidden = H - (SHEET_H - GROUND)     # px of the tile under the ground strip and off the sheet's foot: where what rises past the top lands
for (x, y), R, inside in zip(spots("ring", 1.3 * radii, RISE * radii - hidden + 20), radii, rng.permutation(["shielded", "burnt", "double", "shielded", "burnt"])):
    ring(x, y, R, inside)


# ── 2. candle scorches ───────────────────────────────────────────────────────
def candles(x, y, n):
    gap = u(75, 130)
    for i in range(n):
        cx, cy = x + (i - (n - 1) / 2) * gap + rng.normal(0, 9), y + rng.normal(0, 12)
        h, w = u(170, 430), u(16, 28)
        ix, dx, dy = t.box(cx, cy, int(w * 7) + 40, int(w * 7) + 40, int(h * 1.1), int(w * 4))
        v_ = -dy / h                                                       # 0 at the flame, 1 at the tongue's tip
        vc = np.clip(v_, 0, 1)
        sway = w * u(0.6, 1.8) * np.sin(vc * u(2.5, 6) + u(0, 6.3)) * vc
        hw = w * (0.4 * (1 - vc) + 2.4 * vc ** 0.4 * (1 - vc) ** 1.2) + 1.5        # a flame's shape: widest low, to a point
        along = smooth(v_, -0.04, 0.02) * (1 - 0.6 * vc) * (1 - smooth(v_, 0.8, 1.0))
        lick = np.exp(-np.abs((dx - sway) / hw) ** 3) * along
        black = smooth(lick + 0.14 * ragged[ix] + 0.08 * fine[ix], 0.34, 0.5)             # the tongue itself: a hard, ragged edge
        spot = np.hypot(dx, dy * 1.2)
        stamp(SOOT_M, ix, black * (0.7 + 0.3 * smooth(tongue[ix] + fine[ix], -1.2, 0.8)) + 0.45 * lick + 0.9 * np.exp(-(spot / (1.5 * w)) ** 2))
        stamp(HALO_M, ix, 0.6 * np.exp(-((dx - sway) / (2.6 * hw)) ** 2) * along + 0.7 * np.exp(-(spot / (3 * w)) ** 2))
        stamp(ASH_M, ix, 0.9 * np.exp(-(spot / (0.55 * w)) ** 2))


counts = [int(n) for n in rng.permutation([3, 5, 7])]
for (x, y), n in zip(spots("candles", [n * 55 + 60 for n in counts], [1.6 * IN] * 3), counts):
    candles(x, min(y + 0.4 * IN, SHEET_H - GROUND - 0.15 * IN), n)

# ── 3. cracks from a point ───────────────────────────────────────────────────
print("cracks, knife cuts, sigils", flush=True)
CRK, SPALL = Layer(t), Layer(t)      # cracks, flakes spalled off round their pits
CRK_OLD = np.zeros((H, W), F32)      # the old cracks, kept apart: worn and dirty


def walk(lay, x, y, a, length, w0, depth=0):
    """One crack: a wandering walk out from (x, y), tapering, branching, running
    along a joint for a way where it meets one. Returns its points."""
    pts, s, follow, snap = [(x, y)], 0.0, 0, a
    while s < length:
        if follow:
            follow -= 1
            step = snap + rng.normal(0, 0.04)
        else:
            a += rng.normal(0, 0.07) + (rng.random() < 0.07) * rng.choice([-1, 1]) * u(0.3, 0.7)      # near straight, kinked now and then
            step = a
            j = joint_at(x, y)
            if j and rng.random() < 0.3:
                axes = (0.0, math.pi) if j == "bed" else (math.pi / 2, -math.pi / 2)
                snap = min(axes, key=lambda q: abs(math.remainder(q - a, 2 * math.pi)))
                if abs(math.remainder(snap - a, 2 * math.pi)) < 1.1:
                    follow = int(rng.integers(3, 9))
        st = u(7, 13)
        x, y, s = x + st * math.cos(step), y + st * math.sin(step), s + st
        pts.append((x, y))
        if depth < 2 and rng.random() < 0.03:
            walk(lay, x, y, a + rng.choice([-1, 1]) * u(0.4, 0.9), (length - s) * u(0.3, 0.7), max(1.2, w0 * (1 - s / length) * 0.8), depth + 1)
    for k in range(0, len(pts) - 1, 3):
        lay.line(pts[k:k + 4], max(1.1, w0 * (1 - k / len(pts)) ** 0.8), u(0.75, 1.0))
    return pts


def flake(lay, cx, cy, R, v, sides=7):
    lay.poly([(cx + R * u(0.55, 1.15) * math.cos(q), cy + R * u(0.55, 1.15) * math.sin(q)) for q in np.sort(u(0, 2 * np.pi, sides))], v)


def star(x, y, R, old):
    n = int(rng.integers(5, 10))
    while True:                                                           # the cracks' bearings: uneven, none on top of another
        angs = np.sort(u(0, 2 * np.pi, n))
        if np.diff(np.r_[angs, angs[0] + 2 * np.pi]).min() > 0.3:
            break
    lay = Layer(t) if old else CRK
    arms = [walk(lay, x, y, a, R * u(0.4, 1.0), u(6.0, 9.5)) for a in angs]
    if rng.random() < 0.6:                                                # ring cracks from one to the next, as round an impact
        for rr in (R * u(0.14, 0.24), R * u(0.36, 0.52)):
            for p, q in zip(arms, arms[1:] + arms[:1]):
                i, j = int(rr * u(0.8, 1.2) / 10), int(rr * u(0.8, 1.2) / 10)
                if i < len(p) and j < len(q) and rng.random() < 0.75:
                    (ax, ay), (bx, by) = p[i], q[j]
                    bow = u(0.02, 0.12)
                    lay.line([(ax, ay), ((ax + bx) / 2 + bow * (ax + bx - 2 * x) / 2, (ay + by) / 2 + bow * (ay + by - 2 * y) / 2), (bx, by)], u(2.0, 3.4), 0.85)
    flake(lay, x, y, u(10, 18), 1.0, 8)                                   # the pit
    for _ in range(int(rng.integers(4, 9))):                              # flakes spalled off between the cracks, by the pit
        q, dd = u(0, 2 * np.pi), u(18, 60)
        flake(SPALL, x + dd * math.cos(q), y + dd * math.sin(q), u(12, 32), u(0.6, 0.95))
    if old:
        np.maximum(CRK_OLD, lay.render(), out=CRK_OLD)


radii = rng.permutation(np.linspace(0.7, 2.0, 6)) * u(0.9, 1.1, 6) * IN
for (x, y), R, old in zip(spots("cracks", 0.7 * radii), radii, rng.permutation([True, False, False, True, False, False])):
    star(x, y, R, old)


# ── 4. ritual knife cuts ─────────────────────────────────────────────────────
CUT = Layer(t)


def cut(x, y, a, length, w, v):
    """One cut, from (x, y) along `a`: the blade bites, is drawn, and lifts out to
    a point; now and then it slips on past its end."""
    ts = np.linspace(0, 1, 22)
    bend = rng.normal(0, 0.012) * length
    ca, sa = math.cos(a), math.sin(a)
    centre = [(x + length * s * ca - bend * 4 * s * (1 - s) * sa, y + length * s * sa + bend * 4 * s * (1 - s) * ca) for s in ts]
    half = [w / 2 * math.sin(np.pi * s ** 0.75) ** 0.5 for s in ts]
    CUT.poly([(px - sa * h, py + ca * h) for (px, py), h in zip(centre, half)]
             + [(px + sa * h, py - ca * h) for (px, py), h in zip(centre[::-1], half[::-1])], v)
    if rng.random() < 0.25:
        ex, ey = centre[-1]
        slip, turn = u(12, 45), rng.normal(0, 0.15)
        CUT.line([(ex - 6 * ca, ey - 6 * sa), (ex + slip * math.cos(a + turn), ey + slip * math.sin(a + turn))], 1.3, 0.6 * v)


def ribs(S):
    """Pairs of cuts down and out from an empty spine, longest in the middle."""
    n, slant, gap = int(rng.integers(5, 9)), u(0.45, 0.95), S * u(0.07, 0.14)
    for i in range(n):
        yy = -S + (i + 0.5) * 2 * S / n
        L = S * (0.3 + 0.6 * math.sin(np.pi * (i + 0.5) / n))
        for side in (-1, 1):
            yield side * gap, yy, (slant if side > 0 else math.pi - slant), L


def spiral(S):
    """Cuts laid end to end round a spiral, longer as it opens."""
    turns, way, th, r0 = u(2.0, 2.7), rng.choice([-1, 1]), u(0, 6.3), 0.14 * S
    a = 0.0
    while a < 2 * np.pi * turns:
        r = r0 + (S - r0) * a / (2 * np.pi * turns)
        L = S * (0.11 + 0.24 * r / S)
        q = th + way * a
        tang = q + way * (math.pi / 2 - 0.12)
        yield r * math.cos(q) - L / 2 * math.cos(tang), r * math.sin(q) - L / 2 * math.sin(tang), tang, L
        a += 1.28 * L / r


def chevrons(S):
    """A column of chevrons, point down, each two cuts that do not quite meet, smaller down the column."""
    n, spread = int(rng.integers(4, 7)), u(0.75, 1.1)
    for i in range(n):
        yy = -S + (i + 0.8) * 2 * S / (n + 0.3)
        L = S * (0.95 - 0.55 * i / (n - 1))
        for side in (-1, 1):
            a = -math.pi / 2 + side * spread
            yield side * u(4, 9) + L * math.cos(a), yy + L * math.sin(a), a + math.pi, L


def lattice(S):
    """Two sets of parallel cuts crossed: a net, its outline a lozenge."""
    a0, cross = u(-0.5, 0.5), u(0.95, 1.35)
    for a, n in ((a0, int(rng.integers(4, 7))), (a0 + cross, int(rng.integers(4, 7)))):
        for i in range(n):
            o = (i - (n - 1) / 2) * 1.5 * S / n
            L = 1.9 * S * (1 - 0.75 * abs(o) / (0.75 * S)) ** 0.7 + 0.25 * S
            yield -o * math.sin(a) - L / 2 * math.cos(a), o * math.cos(a) - L / 2 * math.sin(a), a, L


def triangle(S):
    """Three long cuts round a triangle, open at its corners, and a short cut in from each side."""
    turn = u(0, 2.1)
    for k in range(3):
        q = turn + k * 2 * np.pi / 3                                       # this side's outward normal
        mx, my, tang = 0.5 * S * math.cos(q), 0.5 * S * math.sin(q), q + math.pi / 2
        L = 1.45 * S
        yield mx - L / 2 * math.cos(tang), my - L / 2 * math.sin(tang), tang, L
        yield 0.38 * S * math.cos(q), 0.38 * S * math.sin(q), q + math.pi, 0.26 * S


RITES = [ribs, spiral, chevrons, lattice, triangle]
rites = [RITES[i] for i in rng.permutation(len(RITES))] + [RITES[int(rng.integers(len(RITES)))]]
sizes = rng.permutation(np.linspace(0.5, 1.05, len(rites))) * IN
for (x, y), S, rite in zip(spots("cuts", sizes), sizes, rites):
    tilt, w, v = rng.normal(0, 0.25), u(8.0, 12.0), u(0.7, 1.0)
    ct, st_ = math.cos(tilt), math.sin(tilt)
    for cx, cy, a, L in list(rite(S)):
        cx, cy = cx + rng.normal(0, 3), cy + rng.normal(0, 3)
        cut(x + cx * ct - cy * st_, y + cx * st_ + cy * ct, a + tilt + rng.normal(0, 0.04), L * u(0.85, 1.1), w * u(0.8, 1.15), v)


# ── 5. burned sigils ─────────────────────────────────────────────────────────
BRAND = Layer(t)


def arc(cx, cy, rad, a0, a1):
    n = max(6, int(abs(a1 - a0) * 9))
    wob = 1 + 0.04 * np.sin(np.linspace(0, 1, n) * u(3, 8) + u(0, 6.3))
    return [(cx + rad * k * math.cos(a), cy + rad * k * math.sin(a)) for a, k in zip(np.linspace(a0, a1, n), wob)]


def curve(a, b, bow):
    """From a to b, bowed aside by `bow` of its length."""
    (ax, ay), (bx, by) = a, b
    return [(ax + (bx - ax) * s - (by - ay) * bow * 4 * s * (1 - s), ay + (by - ay) * s + (bx - ax) * bow * 4 * s * (1 - s)) for s in np.linspace(0, 1, 9)]


def sigil(frame, core):
    """An invented sign in a box about -1 to 1, y down: (strokes, dots). A frame
    (a broken ring, an open lozenge, an open triangle, an open crate, a ring
    in two halves, or none) round a core (a twig, a comb, a pendant, a kite, a
    flame, a ladder, a key): things, not letters. No stroke crosses another, nothing
    closes into a star, and none is a sign anyone prays to."""
    S, dots = [], []
    if frame == "ring":
        gap = u(0, 6.3)
        S.append(arc(0, 0, 0.95, gap + u(0.35, 0.7), gap + 2 * np.pi))
    elif frame == "lozenge":
        k = u(0.6, 0.8)
        S.append([(0.18, -0.82), (k, 0), (0, 1), (-k, 0), (-0.08, -0.9)])
    elif frame == "delta":
        S.append([(-0.75, -0.72), (0.88, -0.8), (0.02, 0.98), (-0.62, -0.42)])
    elif frame == "crate":
        S.append([(-0.3, -0.8), (-0.82, -0.76), (-0.86, 0.8), (0.8, 0.86), (0.84, -0.3)])
    elif frame == "halves":
        S += [arc(0, 0.08, 0.95, math.pi + u(0.25, 0.45), 2 * math.pi - u(0.25, 0.45)), arc(0, -0.08, 0.95, u(0.25, 0.45), math.pi - u(0.25, 0.45))]
    C, cd = [], []
    if core == "twig":                           # a bent stem, a branch off it on alternate sides, a dot at the end of each
        stem = curve((u(-0.1, 0.1), 0.85), (u(-0.1, 0.1), -0.85), u(-0.12, 0.12))
        C.append(stem)
        for i, k in enumerate((2, 4, 6)):
            side = 1 if i % 2 else -1
            bx, by = stem[k]
            ex, ey = bx + side * u(0.36, 0.55), by - u(0.2, 0.4)
            C.append([(bx, by), (ex, ey)])
            cd.append((ex + side * 0.13, ey - 0.09))
    elif core == "comb":                         # a bowed bar, four teeth of uneven length hung from it, a dot over each end
        bar = curve((-0.8, -0.3), (0.8, -0.36), -0.07)             # (nothing stands on the bar: a ring over its middle made a looped cross of it)
        C.append(bar)
        for k in (1, 3, 5, 7):
            bx, by = bar[k]
            C.append([(bx, by + 0.04), (bx + rng.normal(0, 0.05), by + u(0.4, 1.1))])
        cd += [(-0.8, -0.66), (0.8, -0.72)]
    elif core == "pendant":                      # three rings, smaller down a line, a stroke from each to the next, a bar under
        C += [arc(0.0, -0.62, 0.26, 0, 2 * np.pi), arc(0.04, 0.02, 0.19, 0, 2 * np.pi), arc(0.0, 0.5, 0.13, 0, 2 * np.pi)]
        C += [[(0.0, -0.36), (0.03, -0.17)], [(0.04, 0.21), (0.01, 0.37)], [(-0.4, 0.86), (0.4, 0.78)]]
    elif core == "kite":                         # a kite, open at its head, a bent tail with two barbs off one side (nothing in it: no eye)
        C.append([(0.1, -0.84), (0.5, -0.3), (0.0, 0.1), (-0.5, -0.3), (-0.12, -0.8)])
        tail = curve((0.0, 0.1), (0.2, 0.9), u(0.08, 0.16))
        C.append(tail)
        for k in (3, 6):
            bx, by = tail[k]
            C.append([(bx, by), (bx - u(0.25, 0.4), by + u(0.02, 0.14))])
    elif core == "flame":                        # a flame, open at its tip, a tongue within it, a bar and two dots under
        C.append([(0.12, -0.9), (0.2, -0.45), (0.5, -0.05), (0.46, 0.3), (0.2, 0.5), (-0.2, 0.5), (-0.46, 0.3), (-0.5, -0.05), (-0.3, -0.4), (-0.22, -0.72)])
        C.append(curve((0.0, 0.3), (0.06, -0.2), 0.2))
        C.append([(-0.5, 0.78), (0.5, 0.74)])
        cd += [(-0.75, 0.78), (0.75, 0.72)]
    elif core == "ladder":                       # two rails side by side, one longer, four rungs between them, a ring by its head
        rails = [curve((-0.28, 0.9), (-0.22, -0.55), 0.04), curve((0.24, 0.62), (0.3, -0.9), 0.04)]
        C += rails
        for h in (0.45, 0.15, -0.15, -0.42):
            C.append([(-0.19, h + rng.normal(0, 0.03)), (0.2, h - 0.06 + rng.normal(0, 0.03))])
        C.append(arc(-0.3, -0.76, 0.14, 0, 2 * np.pi))
    else:                                        # a key: a slanted shank, a ring at its head, three wards off its foot
        (ax, ay), (bx, by) = (-0.45, 0.8), (0.3, -0.42)
        C.append([(ax, ay), (bx, by)])
        C.append(arc(bx + 0.16, by - 0.2, 0.25, 0, 2 * np.pi))
        nx, ny = (by - ay) / 1.43, -(bx - ax) / 1.43
        for s_, L in ((0.06, 0.34), (0.22, 0.22), (0.38, 0.32)):
            px, py = ax + (bx - ax) * s_, ay + (by - ay) * s_
            C.append([(px, py), (px - nx * L, py - ny * L)])
    k = 1.0 if frame == "none" else 0.6          # a core in a frame is smaller
    S += [[(px * k, py * k) for px, py in c] for c in C]
    dots += [(px * k, py * k) for px, py in cd]
    if frame == "ring" and rng.random() < 0.7:   # dots set round the ring's outside
        a0 = u(0, 6.3)
        dots += [(1.22 * math.cos(a0 + q), 1.22 * math.sin(a0 + q)) for q in (0, 0.42, 0.84)[:int(rng.integers(2, 4))]]
    return S, dots


FRAMES, CORES = ["ring", "lozenge", "delta", "crate", "halves", "none"], ["twig", "comb", "pendant", "kite", "flame", "ladder", "key"]
frames = [FRAMES[i] for i in rng.permutation(len(FRAMES))] + ["ring"]
cores = [CORES[i] for i in rng.permutation(len(CORES))]
sizes = rng.permutation(np.linspace(0.62, 1.15, 7)) * IN
for (x, y), S, frame, core in zip(spots("sigil", sizes), sizes, frames, cores):
    strokes, dots = sigil(frame, core)
    tilt, tall, w, v = rng.normal(0, 0.18), u(0.92, 1.12), min(max(S * u(0.05, 0.07), 11), 20), u(0.72, 1.0)
    ct, st_ = math.cos(tilt), math.sin(tilt)
    to = lambda p: (x + S * (p[0] * ct - p[1] * tall * st_) + rng.normal(0, 1.5), y + S * (p[0] * st_ + p[1] * tall * ct) + rng.normal(0, 1.5))
    for s in strokes:
        pts = [to(p) for p in s]
        BRAND.line(pts, w * u(0.85, 1.1), v)
        for px, py in (pts[0], pts[-1]):                                  # where the iron was set down and lifted: it dwelt
            BRAND.ellipse(px, py, w * u(0.55, 0.75), w * u(0.55, 0.75), v)
    for d in dots:
        px, py = to(d)
        BRAND.ellipse(px, py, w * u(0.6, 0.85), w * u(0.6, 0.85), v)

# ── lay them on the stone, back to front ─────────────────────────────────────
print("laying them on", flush=True)
grain = (0.9 + 0.2 * smooth(fine, -1.5, 1.5))[..., None]


def relief(m, sigma, k):
    """How a recess (mask m) is lit from the upper left: its upper-left wall in shade, its lower-right one lit."""
    h = -t.blur(m, sigma)
    return np.clip(1 + k * (np.roll(h, -1, 1) - np.roll(h, 1, 1) + np.roll(h, -1, 0) - np.roll(h, 1, 0)) / 2, 0.4, 1.4)[..., None]


# the burns
img = mix(img, np.minimum(img * 1.12 + 0.02, 1), CLEAN_M * 0.75)
img = mix(img, img * SCORCH, HALO_M * 0.6)
img = mix(img, SOOT * grain, np.clip(SOOT_M * (1 + 0.3 * joint), 0, 1) * 0.84)
img = mix(img, ASH * grain, ASH_M * 0.6)
img *= (1 - 0.4 * np.clip(CRAZE_M, 0, 1) * (1 - smooth(np.abs(crazing), 0.03, 0.10)))[..., None]     # heat crazing: a net of fine cracks
del CLEAN_M, CRAZE_M

# cracks: the gap dark, its lower lip lit; the old ones worn wider and softer, dirt spread from them
C = CRK.render()
old = np.clip(t.blur(CRK_OLD, 0.9) * 1.25, 0, 1)
img = mix(img, img * hexc("#aaa398"), np.clip(t.blur(CRK_OLD, 7) * 2.2, 0, 1) * 0.7)
C = np.maximum(C, 0.8 * old)
sp = SPALL.render()
sp = smooth(t.blur(sp, 0.8) + 0.12 * fine * (sp > 0.05), 0.3, 0.7) * np.maximum(sp, 0.6)                 # ragged edges
img = mix(img, np.minimum(img * 1.16 + 0.03, 1), sp * 0.8)                                          # stone broken open: paler
img *= relief(sp, 1.6, 2.4)
img *= (1 - 0.72 * C)[..., None]
img *= (1 + 0.14 * np.clip(np.roll(C, (1, 1), (0, 1)) - C, 0, 1))[..., None]
del C, old, sp, CRK_OLD

# knife cuts: skating over the joints, ash rubbed in round them
K = CUT.render() * (1 - 0.65 * joint)
img = mix(img, img * RUB, np.clip(t.blur(K, 10) * 1.5, 0, 1) * 0.6)
img *= relief(K, 1.0, 2.6)
img = mix(img, img * 0.4, K * 0.92)
del K

# the brands: a brown scorch and a bloom of soot round each stroke, a lick of soot above it; the stroke charred, its
# edge ragged, worn through in patches and at the joints, flecks of pale ash left in it
B = BRAND.render()
Bf = t.spec(B)
near = t.blur(Bf, 2.0)
char = smooth(near + 0.2 * ragged * smooth(near, 0.05, 0.3), 0.36, 0.6) * np.clip(t.blur(Bf, 6) * 4, 0, 1)
char *= (0.8 + 0.2 * smooth(mid + 0.5 * fine, -1.3, 0.3)) * (1 - 0.35 * joint)
lick = t.conv(Bf, t.drip(75, 6, up=True))
lick = np.clip(lick / np.quantile(lick[lick > 0.05], 0.9), 0, 1) * (0.3 + 0.7 * smooth(tongue, -1.0, 1.0))
img = mix(img, img * SCORCH, np.clip(t.blur(Bf, 13) * 2.0, 0, 1) * 0.8)
img = mix(img, img * BURN, np.clip(t.blur(Bf, 6) * 1.7, 0, 1) * 0.85)                               # browner hard by the stroke
img = mix(img, SOOT * grain, np.clip(0.4 * np.clip(t.blur(Bf, 5) * 1.2, 0, 1) + 0.8 * lick, 0, 1) * 0.6)
img = mix(img, CHAR * grain, np.clip(char, 0, 1) * 0.93)
img = mix(img, ASH * grain, smooth(t.blur(Bf, 3.2), 0.75, 0.92) * smooth(ragged + 0.6 * fine, 1.5, 2.1) * (1 - joint) * 0.7)    # flecks of ash
del B, Bf, near, char, lick

# ── the palette: wall 6's own, and the marks' ────────────────────────────────
rgb8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
marked = (rgb8 != stone8).any(2)
px = rgb8[marked]
new = Image.fromarray(px[:: max(1, len(px) // 2_000_000)].reshape(1, -1, 3)).quantize(
    colors=256 - N6, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).getpalette()[:3 * (256 - N6)]
pal = pal6.ravel().tolist() + new
ref = Image.new("P", (1, 1))
ref.putpalette(pal + pal[:3] * (256 - len(pal) // 3))
both = np.asarray(Image.fromarray(rgb8, "RGB").quantize(palette=ref, dither=Image.Dither.NONE))
both = np.where(both < len(pal) // 3, both, 0)        # the padding repeats entry 0
out = Image.fromarray(np.where(marked, both, idx).astype(np.uint8), "P")
out.putpalette(pal)
path = ROOT / "images/wall-14.png"
out.save(path, optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-14.png  {W}x{H}  {W / DPI:.2f}x{H / DPI:.2f}in  {len(out.getcolors())} colours  {marked.mean():.1%} marked  "
      f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  {path.stat().st_size / 1e6:.2f}MB", flush=True)
