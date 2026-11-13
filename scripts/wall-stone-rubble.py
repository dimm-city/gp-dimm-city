"""Draw the three rubble walls, 1 (coursed rubble), 3 (random rubble) and 5
(flagstone bedded in courses), as images/wall-1.png, wall-3.png and wall-5.png.

    python3 scripts/wall-stone-rubble.py [1 3 5]   (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css           (then: the CSS for every wall, these included)

They used to be cut from the painted sheet (source-art/wall-sheet.png) by
wall-tiles.py and printed at 240 DPI with about 110 DPI of real detail. Now
they are drawn, at DPI (300, the print bar), in the same look: a line drawing
of the stone, ash (--bg) faces with grey joints, their tones first matched
level by level to the brick tile's (images/brick-wall.png), as the sheet's
tiles were; then weathered (wall_grime.py) into the city's dim, grimy stone.

Each tile is NW x NH px (9in x 12in), and repeats without a seam both ways,
because everything in it is periodic: the noise is filtered in the Fourier
domain (so it wraps), the seeds the stones grow from are laid on the tile's
own torus and every distance to them is taken round it, and the cracks are
drawn with wrap-around.

One renderer draws all three. The stones are the cells of a diagram of seeds
(the nearest seed owns a pixel), each seed's distance measured in its own
stone's half-size, so a long stone reaches further along its course than up:
- coursed rubble: seeds laid in courses of uneven height and a squarish
  metric (Minkowski p > 2), so the beds run level and the joints stand upright;
- random rubble: big seeds scattered at random (never close, in a metric
  squashed flat), each a little bigger or smaller, and a few small spalls in
  the widest gaps, with a round metric, so the stones come out rounded and
  laid flat, of every size, in no courses;
- flagstone: seeds in offset courses with a round metric that reaches further
  up (`tall`), so each slab meets the bed above in a V: long, low hexagons,
  bedded in rough courses, their upright joints wider and often open.
Then the coordinates are warped by periodic noise first, so no edge runs
straight; the corners are rounded (a soft minimum over the second and third
seed), so the joints open into small dark pockets where three stones meet;
and the edge distance (in px, the seeds' difference over its own slope) is
roughened and bitten (chips at the arris).
Then, as marks on the ash, darkest first:
1. The joint: a line along every edge, heavier on a stone's top and left
   (lit from the upper left, the joint lies in the shadow of the stone above
   it), ragged, grey or broken in places; here and there it opens into two
   lines with the mortar showing pale between them.
2. Chipped arrises: speckle along the edges, in patches, and in the pockets;
   and a second, thin line a few px inside the edge, here and there.
3. The face: stipple and a weathering contour where it turns from the
   light, pits and short cracks, and a faint grain.
4. A pale lit band inside the edge on the side away from the shadow, and a
   broad, faint mottle.
The marks are a darkness field; its pixels are ranked and given the brick's
tones by rank (the darkest pixel the brick's darkest tone), so the clean
stone has the brick's tone histogram. Then wall_grime.py weathers it, with
the joints' mask, as it does walls 2, 4 and 6: grime, damp, mould and fungi,
burns, chips, cracks, bullet pocks, claw marks, a scratched mark, dried
blood; dims it to the city's stone (darker than the brick) and writes it as
an exact palette with no dither: lossless, so the joints keep their edges.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wall_grime  # noqa: E402  (the grime and damage, shared with wall-stone-coursed.py)

ROOT = Path(__file__).resolve().parents[1]
DPI = 300                   # px an inch: the print bar
NW, NH = 9 * DPI, 12 * DPI  # px: 9in x 12in, about a page across and taller than one, so a page shows no mark twice
FEATURE = 3 * DPI           # px: the largest mottle or patch, whatever the tile's size
BG = (0xC8, 0xC5, 0xBF)     # --bg (ash concrete), the brick's colour
BRICK = ROOT / "images/brick-wall.png"   # the tones to match: --bg times the brick's line drawing
SUPER = 3                   # the cracks are drawn at SUPER x and boxed down
F32 = np.float32

# Each wall, its lengths in px at DPI (300). The stone sizes are the sheet's:
# measured on the old 240 DPI tiles and carried over in inches.
WALLS = {
    1: dict(   # coursed rubble: rough, squarish stones in rough courses
        kind="coursed", seed=11,
        course=(72, 104),       # a course's height, px (0.24-0.35in)
        length=(1.35, 2.4),     # a stone's length, in course heights
        p=6.0,                  # the metric: squarish cells
        jitter=(0.12, 0.10),    # a seed's play, across and up, in its stone's length and course's height
        warp=(3.5, 1.0),        # px the coordinates wander: broad, fine
        round=2.5,              # px: corner rounding
        line=(1.0, 0.45),       # a joint's half-width and its play, px
        shadow=1.1,             # its extra width on the shadow side, times
        gaps=0.08,              # share of the joints that open into two lines
        chips=0.9,              # how much chipped speckle along the edges
        scuffs=1.0,             # weathering contours on the faces
        arris=1.0,              # a second line inside the edge
        pits=1.0,
        cracks=14,
    ),
    3: dict(   # random rubble: big, rounded stones, no courses
        kind="random", seed=33,
        size=270,               # a stone's width, px (0.9in); seeds no closer than 0.82 of it
        squash=0.52,            # the stones are this tall to their width
        spalls=0.5,             # and small stones in the gaps, this size
        weight=0.35,            # play in a stone's size: some big, some small
        p=2.0,
        warp=(7.0, 1.1),
        round=5.0,
        line=(0.85, 0.4),
        shadow=1.0,
        gaps=0.06,
        chips=1.3,
        scuffs=1.4,
        arris=1.3,
        pits=1.1,
        cracks=18,
    ),
    5: dict(   # flagstone: flat slabs on edge, bedded in rough courses
        kind="flag", seed=55,
        course=(80, 104),       # a bed's height, px
        length=(2.0, 2.7),      # a slab's length, in bed heights
        tall=1.4,               # the metric's reach up, times: the slabs meet the next bed in a V, long low hexagons
        upright=1.2,            # the upright joints this much wider, and often open
        p=2.0,
        jitter=(0.10, 0.06),
        warp=(5.0, 1.0),
        round=3.0,
        line=(1.0, 0.45),
        shadow=0.9,
        gaps=0.16,
        chips=0.8,
        scuffs=1.0,
        strata=0.25,            # the faces' contours run along the bed: a laminated stone
        arris=1.0,
        pits=1.0,
        cracks=12,
    ),
}

FY = np.fft.fftfreq(NH).astype(F32)[:, None]
FX = np.fft.rfftfreq(NW).astype(F32)[None, :]
F2 = FX * FX + FY * FY


def noise(beta, seed, feature=FEATURE, lo=None, stretch=(1.0, 1.0)):
    """Periodic 1/f^beta noise over the tile, as a z-score. No feature is larger
    than `feature` px; `lo` (px) drops features smaller than it; `stretch`
    (sx, sy) < 1 makes it finer across that axis, so it runs along the other."""
    r = np.random.default_rng(seed)
    fx, fy = FX * stretch[0], FY * stretch[1]
    f = np.maximum(np.sqrt(fx * fx + fy * fy), 1 / feature)
    spec = np.fft.rfft2(r.standard_normal((NH, NW), dtype=F32)) / f ** beta
    if lo:
        spec *= np.exp(-(f * lo) ** 2)
    out = np.fft.irfft2(spec, s=(NH, NW)).astype(F32)
    out -= out.mean()
    return out / out.std()


def blur(m, sigma):
    """Gaussian blur on the torus."""
    return np.fft.irfft2(np.fft.rfft2(m) * np.exp(-2 * np.pi ** 2 * sigma * sigma * F2), s=(NH, NW)).astype(F32)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def tor(d, n):
    """A difference on a circle of length n, into [-n/2, n/2)."""
    return (d + n / 2) % n - n / 2


# ── the seeds ─────────────────────────────────────────────────────────────────
def coursed_seeds(c, rng):
    """Seeds in courses: rows of uneven height, each a row of uneven lengths,
    all summing to the tile, so the courses meet themselves at the wrap."""
    heights = []
    while sum(heights) < NH:
        heights.append(rng.uniform(*c["course"]))
    heights = np.array(heights) * NH / sum(heights)
    mids = np.cumsum(heights) - heights / 2
    pts, sizes = [], []
    for k, (ym, hk) in enumerate(zip(mids, heights)):
        widths = []
        while sum(widths) < NW:
            widths.append(rng.uniform(*c["length"]) * hk)
        widths = np.array(widths) * NW / sum(widths)
        xs = np.cumsum(widths) - widths / 2 + rng.uniform(0, NW)
        for xm, wk in zip(xs, widths):
            pts.append(((xm + rng.normal(0, c["jitter"][0]) * wk) % NW, (ym + rng.normal(0, c["jitter"][1]) * hk) % NH))
            sizes.append((wk, hk))
    return np.array(pts, F32), np.array(sizes, F32)


def scattered_seeds(c, rng):
    """Seeds scattered at random but never close (dart throwing on the torus,
    in the squashed metric), so the stones are of a size but not in rows; then
    a few smaller ones (spalls, `spalls` of the size; a third as many) in the
    widest gaps left."""
    pts, sizes = [], []
    for scale, keep, tries_max in ((1.0, 0.82, 6000), (c["spalls"], 0.75, 3000)):
        tries, most = 0, len(pts) // 3 if pts else 10 ** 6
        start = len(pts)
        while tries < tries_max and len(pts) - start < most:
            p = np.array([rng.uniform(0, NW), rng.uniform(0, NH)])
            if pts:
                q, qs = np.array(pts), np.array(sizes)
                dx, dy = tor(q[:, 0] - p[0], NW), tor(q[:, 1] - p[1], NH) / c["squash"]
                reach = (qs + c["size"] * scale) / 2 * keep
                if (np.sqrt(dx * dx + dy * dy) < reach).any():
                    tries += 1
                    continue
            pts.append(p)
            sizes.append(c["size"] * scale)
            tries = 0
    sizes = np.array(sizes, F32)
    return np.array(pts, F32), np.stack([sizes, sizes], 1)


# ── the cells: nearest, second and third seed of every pixel ────────────────────
def cells(pts, half, p, WX, WY):
    """For every pixel (at its warped place WX, WY), the distance to its
    nearest three seeds and which are the nearest two. A seed's distance is
    measured in its own stone's half-size `half` (across, up), with the
    Minkowski exponent p, round the torus, so each stone fills its own box: a
    long stone reaches further along its course than up. Each seed is only
    measured over a box round it no cell reaches past."""
    INF = F32(1e9)
    d1 = np.full((NH, NW), INF, F32)
    d2, d3 = d1.copy(), d1.copy()
    i1 = np.zeros((NH, NW), np.int32)
    i2 = i1.copy()
    for k, ((sx_, sy_), (hx, hy)) in enumerate(zip(pts, half)):
        rx, ry = int(hx * 2.4 + 30), int(hy * 2.4 + 30)
        rows = np.arange(int(sy_) - ry, int(sy_) + ry + 1) % NH
        cols = np.arange(int(sx_) - rx, int(sx_) + rx + 1) % NW
        ix = np.ix_(rows, cols)
        dx = np.abs(tor(WX[ix] - sx_, NW)) / hx
        dy = np.abs(tor(WY[ix] - sy_, NH)) / hy
        d = np.sqrt(dx * dx + dy * dy) if p == 2 else (dx ** p + dy ** p) ** (1 / p)
        a1, a2, a3, b1, b2 = d1[ix], d2[ix], d3[ix], i1[ix], i2[ix]
        n1, n2, n3 = d < a1, d < a2, d < a3
        a3 = np.where(n2, a2, np.where(n3, d, a3))
        a2 = np.where(n1, a1, np.where(n2, d, a2))
        b2 = np.where(n1, b1, np.where(n2, k, b2))
        a1 = np.where(n1, d, a1)
        b1 = np.where(n1, k, b1)
        d1[ix], d2[ix], d3[ix], i1[ix], i2[ix] = a1, a2, a3, b1, b2
    return d1, d2, d3, i1, i2


def px_from(g):
    """A field that is 0 on an edge, as px from that edge: the field over its
    own slope (taken round the torus)."""
    gx = (np.roll(g, -1, 1) - np.roll(g, 1, 1)) / 2
    gy = (np.roll(g, -1, 0) - np.roll(g, 1, 0)) / 2
    return g / np.maximum(np.sqrt(gx * gx + gy * gy), 1e-4)


def draw(n):
    c = WALLS[n]
    seed = c["seed"]
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:NH, 0:NW].astype(F32)

    # the seeds, each with its stone's half-size
    if c["kind"] == "random":
        pts, sizes = scattered_seeds(c, rng)
        sizes = sizes * (1 + c["weight"] * rng.uniform(-1, 1, (len(pts), 1))).astype(F32)
        half = np.stack([sizes[:, 0] / 2, sizes[:, 0] / 2 * c["squash"]], 1)
    else:
        pts, sizes = coursed_seeds(c, rng)
        half = sizes / 2 * np.array([1, c.get("tall", 1.0)], F32)

    # warp the coordinates: the edges wander, broadly and finely
    wb, wf = c["warp"]
    WX = xx + wb * noise(2.6, seed + 1, feature=400, lo=25) + wf * noise(1.6, seed + 2, feature=60, lo=3)
    WY = yy + wb * noise(2.6, seed + 3, feature=400, lo=25) + wf * noise(1.6, seed + 4, feature=60, lo=3)
    d1, d2, d3, i1, i2 = cells(pts, half, c["p"], WX, WY)
    del WX, WY
    print(f"  wall {n}: {len(pts)} stones", flush=True)

    # the edge distance, px: half the way across to the edge with the second
    # seed, its corners rounded with the third (the pockets where three meet)
    k = c["round"]
    e2 = np.minimum(px_from(d2 - d1), 400)
    e3 = np.minimum(px_from(d3 - d1), 400)
    m = np.minimum(e2, e3)
    e = m - k * np.log(np.exp(-(e2 - m) / k) + np.exp(-(e3 - m) / k))
    del d1, d2, d3, e2, e3
    # roughened, and bitten at the arris
    rough = noise(1.0, seed + 5, lo=1.2)
    chip_n = noise(1.5, seed + 6, feature=70, lo=4)
    e = e + 0.35 * rough - 6.0 * smooth(chip_n, 1.8, 2.8) * np.exp(-np.maximum(e, 0) / 6)

    # which way the edge faces: toward the second seed, the joint's other stone
    vx = tor(pts[i2, 0] - pts[i1, 0], NW) / half[i1, 0]
    vy = tor(pts[i2, 1] - pts[i1, 1], NH) / half[i1, 1]
    vl = np.sqrt(vx * vx + vy * vy) + 1e-3
    up, left = -vy / vl, -vx / vl             # 1: the other stone is above / to the left
    shade = np.clip(0.75 * up + 0.45 * left, 0, 1)     # the joint's shadow falls here
    litside = np.clip(-(0.75 * up + 0.45 * left), 0, 1)
    del vx, vy, vl

    # 1. the joint: a line along the edge, heavier in the shadow, fading in
    # places, here and there opened into two with pale mortar between
    lw, lplay = c["line"]
    w = lw + lplay * noise(1.6, seed + 7, feature=160, lo=6)
    w = np.maximum(w, 0.5) * (1 + c["shadow"] * shade * smooth(noise(1.4, seed + 8, feature=200, lo=10), -1.2, 0.6))
    upright = smooth(np.abs(left), 0.6, 0.85) * c.get("upright", 0)
    w = w * (1 + upright)
    gn = noise(1.8, seed + 9, feature=260, lo=15) + 1.5 * upright
    g = np.clip((gn - np.quantile(gn[::8, ::8], 1 - c["gaps"])) * 6, 0, 2.6)   # half the mortar's width, px
    inner = np.where(g > 0.9, smooth(e, g - 0.6, g + 0.6), 1.0)
    J = inner * (1 - smooth(e, g * (g > 0.9) + w - 0.6, g * (g > 0.9) + w + 0.6))
    fade = 1 - smooth(noise(1.5, seed + 10, feature=120, lo=8), -1.1, -0.3)       # the line breaks, or goes grey
    J *= 1 - 0.6 * fade
    J *= 1 - 0.85 * smooth(noise(0.8, seed + 21, feature=30, lo=2.2), 1.0, 1.5)      # ragged: a dry pen
    del inner, gn

    # 2. chipped arrises: speckle along the edges, in patches, and in the pockets
    patch = smooth(noise(1.8, seed + 11, feature=110, lo=10), -0.6, 0.9)
    fine = noise(0.3, seed + 12, lo=1.6)            # grains about 2-3px: chips, not dust
    zone = np.exp(-np.maximum(e - w, 0) / (5 + 14 * patch)) * patch * c["chips"]
    zone = np.minimum(zone * (0.6 + 0.6 * shade), 1)
    speck = smooth(fine, 3.0 - 2.9 * zone, 3.3 - 2.9 * zone)
    # the arris: a second, thin line a few px inside the edge, here and there
    at = 4.5 + 3.5 * smooth(noise(1.6, seed + 18, feature=150, lo=10), -1, 1)
    amask = smooth(noise(1.6, seed + 19, feature=140, lo=8), 0.3, 0.9) * c["arris"]
    arris = amask * (1 - smooth(np.abs(e - w - at), 0.35, 1.1))
    # 3. the face: weathering contours in places, pits, cracks
    h = noise(2.2, seed + 13, feature=150, lo=6, stretch=(1.0, c.get("strata", 1.0)))
    hmask = smooth(noise(1.6, seed + 14, feature=200, lo=20), 0.1, 1.1) * c["scuffs"]
    gy, gx = np.gradient(h)
    gm = np.sqrt(gx * gx + gy * gy) + 1e-4
    contour = (1 - smooth(np.abs(h - 0.4) / gm, 0.4, 1.1)) * hmask * smooth(e, 4, 10)
    # and stippled where the face turns away from the light (down and right)
    away = (gx + gy) / (gm.std() * 1.4)
    stip = np.minimum(smooth(away, 0.3, 1.6) * hmask * 1.3, 1) * smooth(e, 3, 8)
    stipple = smooth(fine, 3.0 - 2.4 * stip, 3.3 - 2.4 * stip)
    contour *= smooth(away, -0.2, 0.4)             # the contour only on the shaded slope
    del h, gx, gy, gm, away
    pit_n = noise(0.6, seed + 15, lo=1.4)
    pits = smooth(pit_n, 3.0 - 0.25 * c["pits"], 3.3 - 0.25 * c["pits"]) * smooth(e, 2, 5)

    crack = Image.new("L", (NW * SUPER, NH * SUPER), 0)
    cd = ImageDraw.Draw(crack)
    for _ in range(c["cracks"]):
        x, y, a = rng.uniform(0, NW), rng.uniform(0, NH), rng.uniform(0, 2 * np.pi)
        pts_ = [(x, y)]
        for _ in range(int(rng.integers(3, 10))):
            a += rng.normal(0, 0.25)
            step = rng.uniform(5, 11)
            x, y = x + step * math.cos(a), y + step * math.sin(a)
            pts_.append((x, y))
        wd = max(1, round(rng.uniform(0.8, 1.6) * SUPER))
        for ox in (-NW, 0, NW):
            for oy in (-NH, 0, NH):
                cd.line([((p + ox) * SUPER, (q + oy) * SUPER) for p, q in pts_], fill=255, width=wd)
    cr = np.asarray(crack.resize((NW, NH), Image.BOX), F32) / 255 * smooth(e, 2, 6)
    del crack

    # 4. the lit band inside the edge, away from the shadow, and a broad mottle
    lit = litside * smooth(e, w + 0.5, w + 2.5) * (1 - smooth(e, w + 5, w + 11))
    mottle = noise(2.0, seed + 16, lo=30)
    tone = noise(1.2, seed + 17, feature=40, lo=2)

    grain = smooth(noise(0.4, seed + 20, lo=0.8), 1.9, 2.3) * (0.5 + 0.5 * smooth(mottle, -1.0, 1.0))

    marks = {"joint": J, "speck": 0.8 * np.maximum(speck, 0.9 * stipple), "arris": 0.6 * arris, "contour": 0.55 * contour,
             "pits": 0.75 * pits, "cracks": 0.65 * cr, "grain": 0.25 * grain}
    print("  " + "  ".join(f"{k} {(v > 0.12).mean() * 100:.1f}%" for k, v in marks.items()), flush=True)
    D = np.maximum.reduce(list(marks.values()))
    D = D + 0.01 * mottle + 0.02 * tone - 0.06 * lit
    wj = w + g * (g > 0.9)                       # the joint: its line, and the mortar where it opens
    joint = 1 - smooth(e, wj - 0.6, wj + 0.6)
    return D, joint


def brick_tones():
    """The brick tile's pixels as multiples of --bg, darkest first."""
    bg = BG[0] * 0.299 + BG[1] * 0.587 + BG[2] * 0.114
    a = np.asarray(Image.open(BRICK).convert("RGB"), np.float64)
    return np.sort((a @ [0.299, 0.587, 0.114]).ravel() / bg)


def tint(D, tones, levels=1024):
    """Rank the darkness field's pixels and give them the brick's tones by rank,
    the darkest pixel the brick's darkest tone: a palette image of --bg times
    each tone (levels that land on one colour share its index)."""
    flat = D.ravel()
    order = np.argsort(-flat, kind="stable")             # darkest first
    rank = np.empty(flat.size, np.int64)
    rank[order] = np.arange(flat.size)
    level = (rank * levels // flat.size).astype(np.int64)   # equal-count levels
    mids = ((np.arange(levels) + 0.5) / levels * len(tones)).astype(int)
    colours, index = [], []
    for t in tones[mids]:
        col = tuple(min(255, round(BG[i] * t)) for i in range(3))
        if col not in colours:
            colours.append(col)
        index.append(colours.index(col))
    idx = np.array(index, np.uint8)[level].reshape(D.shape)
    out = Image.fromarray(idx, "P")
    out.putpalette([v for col in colours for v in col])
    return out


def main():
    which = [int(a) for a in sys.argv[1:]] or sorted(WALLS)
    tones = brick_tones()
    for n in which:
        D, joint = draw(n)
        stone = np.asarray(tint(D, tones).convert("RGB"), F32) / 255
        del D
        rgb, special = wall_grime.weather(stone, joint, seed=WALLS[n]["seed"] * 100 + 7)
        path = ROOT / f"images/wall-{n}.png"
        out = wall_grime.save(rgb, special, path)
        avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
        print(f"images/wall-{n}.png  {NW}x{NH}  {NW / DPI:.2f}x{NH / DPI:.2f}in  {len(out.getcolors())} colours  "
              f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  {path.stat().st_size / 1e6:.2f}MB", flush=True)


if __name__ == "__main__":
    main()
