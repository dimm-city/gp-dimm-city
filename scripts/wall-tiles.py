"""Bake the six stone-wall page tiles (`@page wall-1` ... `wall-6`) and their CSS.

    python3 scripts/wall-tiles.py [source-art/wall-sheet.png]
    python3 scripts/wall-tiles.py --css     # rewrite the CSS only, from images/
    python3 scripts/wall-tiles.py --ground  # redraw the ground only
    python3 scripts/wall-tiles.py --grounds # the three streets (setts, flags, asphalt), grimed, and the CSS

Python 3 with Pillow; the six walls bake in parallel, in a couple of minutes.
Reads the sheet (six square-ish stone panels on a transparent ground, two
columns by three rows), writes images/wall-1.png ... wall-6.png, each an opaque
tile in the brick's colours that repeats without a visible join or a visible
grid, and rewrites the generated `page-walls` blocks in styles/dc-native.css
(each wall's named pages: the background, and the chapter chip's face per hue)
and styles/page-rules.css (the wiring from page word to named page).

For each panel:
1. Crop to the part that is fully opaque (the panels' edges are ragged).
2. Make it wrap left-right, then top-bottom, with a minimum-error seam cut
   (image quilting): choose the overlap whose two ends match best (that also
   locks a regular bond onto its period), then cut through that overlap along
   the path where the two ends differ least, which runs mostly down the mortar.
   The second cut wraps round the first axis, so the corners close too.
3. Grow it. A panel is only 1.3-1.6in of wall, so on its own it repeats six
   or seven times across a page, the same stones in a grid. Walls 1-5 are
   regrown at GROW times the size each way by image quilting on a torus:
   PATCH-px patches of the tile (as is, mirrored, flipped or both) are laid in
   rows, each the one whose overlap with the patches already laid matches best
   (every offset tried at 1/COARSE size, the best few refined at full size),
   then cut in along the path where the two differ least, which runs down the
   mortar. A patch may not repeat one laid nearby, continue one (that would copy
   the panel back in) or mirror its neighbour across their seam. GROW whole
   panels each way, so a course or a bond meets itself at the wrap. Wall 6 is
   a regular grid, which quilting cannot keep straight: its whole setts (a joint
   on every side) are cut out, resized to one SETT-px cell and laid SETTS by
   SETTS in random turns and flips, no sett beside itself, with the panel's
   mean joint drawn along every cell edge so each joint reads the same.
4. Tint it to the brick: the sheet is dark stone with light mortar, the brick
   is light ash (--bg) with grey joints, so the tones are inverted (the stone
   faces go light, the mortar and the pits grey) and matched, level by level,
   to the brick tile's own (images/brick-wall.png: --bg times a grey line
   drawing). Each tile then has the brick's average and its darkest grey, and
   the CSS puts --bg under it, as the brick's rule does.
5. Save as PNG, opaque, with an exact palette (one colour per tone, about a
   hundred): lossless, so the joints keep their edges (a JPEG rings round
   them), a third the size of RGB, and PDF/X carries an opaque tile as is.

The tiles keep the source's pixel scale and print at DPI dots per inch, so
the stones come out the size they are on the sheet, close to the default
wall's bricks, and a tile is about 3.6-4.8in. That is about 240 DPI, under
the 300 DPI print bar, and the sheet is 1024x1536 (about 512px a panel), so
step 3's quilting has already grown each panel about 2x: the real detail is
about 110 DPI. The walls are accepted as texture at that; no upsampling
would add detail, and Gutterpress's resolution checks judge <img> elements,
not CSS backgrounds, so nothing flags them. A sharper wall needs a source
sheet of at least 2048x3072. The ground is drawn, not sampled, so it is
drawn at GROUND_DPI (300): its setts are resampled up from the wall's scale
in the perspective transform, and its joints, foot line and shadow are
drawn at that resolution. It is drawn for the depth Chromium paints it at
(a background is painted in whole CSS px: 0.6in is 58px, 0.604in), so on a
page the PDF keeps as vector the strip's rows measure 300 DPI, not 298.
"""
import math
import random
import sys
from multiprocessing import Pool
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps, ImageStat

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SHEET = ARGS[0] if ARGS else "source-art/wall-sheet.png"
BG = (0xC8, 0xC5, 0xBF)             # --bg (ash concrete), the brick's colour
BRICK = "images/brick-wall.png"     # the tones to match: --bg times the brick's line drawing
OVERLAP = range(28, 110)            # how much of each end the seam may use, px
FEATHER = 2                         # px blended either side of a cut
DPI = 240                           # print resolution, so printed size = px / DPI
GROW = 3                            # a regrown tile is this many panels each way
TALL = 1000                         # px: a tile at least about this tall (4in), however short its panel
PATCH, PATCH_OVERLAP = 200, 56      # quilting patch and its overlap with each neighbour, px
COARSE = 4                          # the patch search's first pass runs at 1/COARSE size
NEAR = 20                           # px: a patch this close to one laid nearby is the same patch
SETT_WALLS = {6}                    # regular grids: laid sett by sett instead of quilted
SETT, SETTS = 136, 8                # the sett cell, px, and cells a side
JOINT = 6                           # half-width of the drawn joint, px
BEDDED = {5: 0.62}                  # walls squashed into beds first: flagstones laid flat read as a wall
GROUND = "images/ground.png"        # the setts: the street under the brick
# Three streets, none a copy of a wall (a street of the wall's own stone read as
# the wall carrying on, not as ground): setts, bonded flagstones cut from the
# same stone, and cracked, patched asphalt. Each wall stands on one that
# contrasts with it. All of them are grimed (`grime`). `--grounds` draws them.
STREETS = {"setts": GROUND, "flags": "images/ground-flags.png", "asphalt": "images/ground-asphalt.png"}
WALL_STREET = {1: "flags", 2: "asphalt", 3: "setts", 4: "flags", 5: "setts", 6: "asphalt"}
GROUND_FROM = 6                     # laid from this wall's panel: its setts make the paving slabs
GROUND_IN = 0.6                     # its depth from the sheet edge, in: just under the footer chips
GROUND_DPI = 300                    # the ground is drawn, so it is drawn at the print bar (the walls print at DPI)
CSS_PX = 96                         # Chromium paints a background in whole CSS px: 0.6in (57.6px) paints 58px deep
GROUND_W = 3000                     # px across (10in at GROUND_DPI): drawn once, in perspective, centred on the sheet
EYE = 5.5                           # in from the wall's foot up to the eye: how fast the rows recede
LEAN = 0.5                          # px the ground's joints run across per px down: all one way, so a spread shows one view
GROUND_DEPTH = 2.4                  # setts of pavement the strip shows, wall to sheet edge
GROUND_SHADE = 0.9                  # the ground's tone against the wall's
# A wall page keeps its chapter's chip colour: one named page per wall and hue.
# The hue faces and the chapter words that wire them are page-rules.css's and
# dc-native.css's (2c); a book wires its own chapters the same way.
HUES = {"blue": "--hud-blue-dark", "rust": "--rust", "violet": "--brand-violet",
        "amethyst": "--crystal-amethyst", "amber": "--amber-dark", "ink": "--ink-dark"}
CHAPTER_HUES = {"specialty": "blue", "rules": "rust", "lore": "violet", "dm": "ink", "gear": "amber"}
# pages that keep their own named page (and so the brick) whatever wall they name
KEEPS = ".gp-page-full-bleed, .dc-full-page, .dc-page-contents, .dc-page-credits, .dc-page-intro, .dc-page-citizen-file"
# and inside a block that names a wall, the children that keep their own page
PLATES = KEEPS + ", .dc-specialty-art"


def lum(c):
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000


def opaque_boxes(im):
    """The six panels' fully opaque boxes, row by row, left to right."""
    a = im.getchannel("A").load()
    W, H = im.size

    def spans(counts, need, minlen=100):
        out, start = [], None
        for i, v in enumerate(counts + [0]):
            if v > need and start is None:
                start = i
            elif v <= need and start is not None:
                if i - start > minlen:
                    out.append((start, i))
                start = None
        return out

    cols = spans([sum(1 for y in range(H) if a[x, y] > 200) for x in range(W)], 200)
    rows = spans([sum(1 for x in range(W) if a[x, y] > 200) for y in range(H)], 200)
    boxes = []
    for r0, r1 in rows:
        for c0, c1 in cols:
            x0, y0, x1, y1 = c0, r0, c1, r1
            for _ in range(80):
                moved = False
                if sum(a[x0, y] > 250 for y in range(y0, y1)) < 0.995 * (y1 - y0): x0 += 1; moved = True
                if sum(a[x1 - 1, y] > 250 for y in range(y0, y1)) < 0.995 * (y1 - y0): x1 -= 1; moved = True
                if sum(a[x, y0] > 250 for x in range(x0, x1)) < 0.995 * (x1 - x0): y0 += 1; moved = True
                if sum(a[x, y1 - 1] > 250 for x in range(x0, x1)) < 0.995 * (x1 - x0): y1 -= 1; moved = True
                if not moved:
                    break
            boxes.append((x0 + 2, y0 + 2, x1 - 2, y1 - 2))
    return boxes


def rows_of(im):
    w, h = im.size
    px = im.load()
    return [[px[x, y] for x in range(w)] for y in range(h)]


def best_overlap(rows):
    """The overlap o whose first o columns best match the last o columns."""
    w = len(rows[0])
    best = None
    for o in OVERLAP:
        err = 0.0
        for r in rows[::2]:
            for j in range(0, o, 2):
                err += (lum(r[j]) - lum(r[w - o + j])) ** 2
        err /= len(rows[::2]) * len(range(0, o, 2))
        if best is None or err < best[0]:
            best = (err, o)
    return best[1]


def min_cut(cost, cyclic):
    """Columns c[y] of a min-cost top-to-bottom path through cost[y][j], moving
    at most one column a row. cyclic: the path also closes, |c[last] - c[0]| <= 1."""
    h, o = len(cost), len(cost[0])
    starts = range(o) if cyclic else [None]
    best = None
    for s in starts:
        INF = float("inf")
        acc = [(cost[0][j] if s is None or j == s else INF) for j in range(o)]
        back = []
        for y in range(1, h):
            row, br = [], []
            for j in range(o):
                k = min((acc[k], k) for k in (j - 1, j, j + 1) if 0 <= k < o)
                row.append(k[0] + cost[y][j])
                br.append(k[1])
            acc = row
            back.append(br)
        ends = [j for j in range(o) if s is None or abs(j - s) <= 1]
        j = min(ends, key=lambda e: acc[e])
        if best is None or acc[j] < best[0]:
            path = [j]
            for br in reversed(back):
                j = br[j]
                path.append(j)
            best = (acc[path[0]], path[::-1])
    return best[1]


def wrap_x(rows, cyclic):
    """Make rows wrap left-right: the tile loses o columns."""
    w = len(rows[0])
    o = best_overlap(rows)
    cost = [[(lum(r[j]) - lum(r[w - o + j])) ** 2 for j in range(o)] for r in rows]
    cut = min_cut(cost, cyclic)
    out = []
    for r, c in zip(rows, cut):
        left = []
        for j in range(o):
            a, b = r[w - o + j], r[j]                  # the right end runs on into the left
            t = min(1.0, max(0.0, (j - c + FEATHER) / (2 * FEATHER)))
            left.append(tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3)))
        out.append(left + r[o:w - o])
    return out


def transpose(rows):
    return [list(col) for col in zip(*rows)]


def tor(d, n):
    """d as the shortest signed step round a loop of n."""
    d %= n
    return d - n if d > n / 2 else d


def wrap_crop(im, x, y, w, h):
    out = Image.new("L", (w, h))
    for ox in (0, im.width):
        for oy in (0, im.height):
            out.paste(im, (ox - x, oy - y))
    return out


def wrap_paste(im, patch, mask, x, y):
    for ox in (0, -im.width):
        for oy in (0, -im.height):
            im.paste(patch, (x + ox, y + oy), mask)


def quilt(src, seed):
    """src (a tile that wraps) regrown at GROW times the size, with no repeat inside
    (a short panel, such as a bedded one, as many times down as reach TALL px)."""
    rnd = random.Random(seed)
    w, h = src.size
    W, H, B, F = GROW * w, max(GROW, round(TALL / h)) * h, PATCH, COARSE
    step = PATCH - PATCH_OVERLAP
    nx, ny = round(W / step), round(H / step)
    xs = [round(i * W / nx) for i in range(nx)]
    ys = [round(j * H / ny) for j in range(ny)]
    # the four faces of the tile, each tiled out by a patch so any offset crops
    # whole: v ^ 1 is v mirrored, v ^ 2 is v flipped
    faces = []
    for face in (src, ImageOps.mirror(src), ImageOps.flip(src), ImageOps.flip(ImageOps.mirror(src))):
        big = Image.new("L", (w + B, h + B))
        for ox in (0, w):
            for oy in (0, h):
                big.paste(face, (ox, oy))
        faces.append(big)
    small = [f.reduce(F) for f in faces]
    out = Image.new("L", (W, H))
    laid = {}
    for j in range(ny):
        for i in range(nx):
            x0, y0 = xs[i], ys[j]
            ov = {}                                   # overlap with each side already laid, px
            if i > 0: ov["l"] = xs[i - 1] + B - x0
            if j > 0: ov["t"] = ys[j - 1] + B - y0
            if i == nx - 1: ov["r"] = x0 + B - W
            if j == ny - 1: ov["b"] = y0 + B - H
            target = wrap_crop(out, x0, y0, B, B)
            seen = Image.new("L", (B, B), 0)
            for side, o in ov.items():
                seen.paste(255, {"l": (0, 0, o, B), "t": (0, 0, B, o), "r": (B - o, 0, B, B), "b": (0, B - o, B, B)}[side])
            bans = []
            for (ii, jj), (lv, lx, ly) in laid.items():
                ox, oy = tor(x0 - xs[ii], W), tor(y0 - ys[jj], H)
                if abs(ox) <= 2.5 * step and abs(oy) <= 2.5 * step:
                    bans += [(lv, lx, ly), (lv, (lx + ox) % w, (ly + oy) % h)]
            mirrors = {laid[k][0] ^ flip for k, flip in [((i - 1, j), 1), ((0, j) if i == nx - 1 else None, 1),
                                                         ((i, j - 1), 2), ((i, 0) if j == ny - 1 else None, 2)] if k in laid}
            banned_coarse = set()
            for bv, bx, by in bans:
                cx = [x for x in ((bx + d) % w for d in range(-NEAR + 1, NEAR)) if x % F == 0]
                cy = [y for y in ((by + d) % h for d in range(-NEAR + 1, NEAR)) if y % F == 0]
                banned_coarse.update((bv, x, y) for x in cx for y in cy)

            def banned(v, x, y):
                return v in mirrors or any(bv == v and abs(tor(bx - x, w)) < NEAR and abs(tor(by - y, h)) < NEAR for bv, bx, by in bans)

            if not ov:
                while True:
                    pick = (rnd.randrange(4), rnd.randrange(w), rnd.randrange(h))
                    if not banned(*pick):
                        break
            else:
                ts, ms, bs = target.reduce(F), seen.reduce(F), B // F
                coarse = {}
                for v in range(4):
                    if v in mirrors:
                        continue
                    for y in range(0, h, F):
                        for x in range(0, w, F):
                            if (v, x, y) not in banned_coarse:
                                crop = small[v].crop((x // F, y // F, x // F + bs, y // F + bs))
                                coarse[(v, x, y)] = ImageStat.Stat(ImageChops.difference(crop, ts), ms).sum2[0]
                fine = {}
                for v, x, y in sorted(coarse, key=coarse.get)[:10]:
                    for dx in range(-F, F + 1):
                        for dy in range(-F, F + 1):
                            c = (v, (x + dx) % w, (y + dy) % h)
                            if c not in fine and not banned(*c):
                                crop = faces[c[0]].crop((c[1], c[2], c[1] + B, c[2] + B))
                                fine[c] = ImageStat.Stat(ImageChops.difference(crop, target), seen).sum2[0]
                best = min(fine.values())
                pick = rnd.choice([c for c, e in fine.items() if e <= best * 1.08 + 1])
            v, x, y = pick
            patch = faces[v].crop((x, y, x + B, y + B))
            keep = [[255] * B for _ in range(B)]       # 0 where the pixels laid already stay
            pp, tp = patch.tobytes(), target.tobytes()

            def cost(px, py):
                return (pp[py * B + px] - tp[py * B + px]) ** 2

            if "l" in ov:
                o = ov["l"]
                for py, c in enumerate(min_cut([[cost(q, py) for q in range(o)] for py in range(B)], False)):
                    for px in range(c): keep[py][px] = 0
            if "r" in ov:
                o = ov["r"]
                for py, c in enumerate(min_cut([[cost(B - o + q, py) for q in range(o)] for py in range(B)], False)):
                    for px in range(B - o + c + 1, B): keep[py][px] = 0
            if "t" in ov:
                o = ov["t"]
                for px, c in enumerate(min_cut([[cost(px, q) for q in range(o)] for px in range(B)], False)):
                    for py in range(c): keep[py][px] = 0
            if "b" in ov:
                o = ov["b"]
                for px, c in enumerate(min_cut([[cost(px, B - o + q) for q in range(o)] for px in range(B)], False)):
                    for py in range(B - o + c + 1, B): keep[py][px] = 0
            mask = Image.frombytes("L", (B, B), bytes(v for r in keep for v in r))
            wrap_paste(out, patch, mask.filter(ImageFilter.BoxBlur(1)) if ov else mask, x0, y0)
            laid[(i, j)] = pick
    return out


def joints(profile):
    """Centres of the joints a light-mortar profile crosses whole (not cut by its ends)."""
    m = sorted(profile)[len(profile) // 2]
    out = []
    for i, v in enumerate(profile):
        if v > m + 20 and v == max(profile[max(0, i - 10):i + 11]):
            lo = hi = i
            while lo > 0 and profile[lo - 1] > m + 10: lo -= 1
            while hi < len(profile) - 1 and profile[hi + 1] > m + 10: hi += 1
            if 0 < lo and hi < len(profile) - 1:
                out.append(sum(k * (profile[k] - m) for k in range(lo, hi + 1)) / sum(profile[k] - m for k in range(lo, hi + 1)))
    return out


def lay_setts(panel, seed, bond=False):
    """The panel's whole setts relaid, each in one of its eight turns and flips: in a
    grid, or with every other row half a sett along (bond), which reads as a wall."""
    rnd = random.Random(seed)
    w, h = panel.size
    px = panel.load()
    cols = [sum(px[x, y] for y in range(h)) / h for x in range(w)]
    rows = [sum(px[x, y] for x in range(w)) / w for y in range(h)]
    xs, ys = joints(cols), joints(rows)
    setts = []
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            s = panel.resize((SETT, SETT), Image.LANCZOS, box=(x0, y0, x1, y1))
            for k in range(8):
                t = s.transpose(Image.Transpose.ROTATE_90) if k & 4 else s
                t = t.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if k & 1 else t
                setts.append(((x0, y0), t.transpose(Image.Transpose.FLIP_TOP_BOTTOM) if k & 2 else t))
    S = SETT * SETTS
    out = Image.new("L", (S, S))
    grid = {}
    for j in range(SETTS):
        for i in range(SETTS):
            near = [grid.get(((i + di) % SETTS, (j + dj) % SETTS)) for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            while True:
                q = rnd.randrange(len(setts))
                if all(n is None or setts[n][0] != setts[q][0] for n in near) or rnd.random() < 0.05:
                    break
            grid[(i, j)] = q
            lap = SETT // 2 if bond and j % 2 else 0
            for x in (i * SETT + lap, i * SETT + lap - S):
                out.paste(setts[q][1], (x, j * SETT))
    # the joint: the panel's mean cross-section of one, drawn along every cell
    # edge where it is lighter, so a sett's own rim still shows
    cut = [cols[round(c) + d] for c in xs for d in range(-JOINT, JOINT + 1)] + \
          [rows[round(c) + d] for c in ys for d in range(-JOINT, JOINT + 1)]
    n = len(xs) + len(ys)
    joint = [round(sum(cut[k * (2 * JOINT + 1) + d] for k in range(n)) / n) for d in range(2 * JOINT + 1)]
    o = out.load()
    for k in range(SETTS):
        for t in range(S):
            lap = SETT // 2 if bond and (t // SETT) % 2 else 0
            for d in range(-JOINT, JOINT + 1):
                e = (k * SETT + d) % S                      # bed joint, row k's top
                o[t, e] = max(o[t, e], joint[d + JOINT])
                e = (k * SETT + lap + d) % S                # head joint, in row t // SETT
                o[e, t] = max(o[e, t], joint[d + JOINT])
    return out


def ground(panel, tones, grid=None):
    """The pavement at the wall's foot: the panel's setts in a grid (or `grid`, a
    seamless stone tile, dark stone on light joints), its rows receding as seen
    from EYE above it and its joints all leaning LEAN the same way (a vanishing
    point at each sheet's middle mirrored the two pages of a spread), GROUND_SHADE
    darker than the wall, with the wall's shadow along its top edge."""
    grid = grid if grid is not None else lay_setts(panel, seed=60)
    src = Image.new("L", (grid.width * 3, grid.height))
    for k in range(3):
        src.paste(grid, (k * grid.width, 0))
    U = 2                                                   # drawn at U times, then reduced
    S = GROUND_DPI / DPI                                    # output px per source px: the setts are at the wall's scale
    painted = math.ceil(GROUND_IN * CSS_PX) / CSS_PX        # in: the depth Chromium paints the strip at (whole CSS px), so
    W, G, Hh = GROUND_W * U, math.ceil(painted * GROUND_DPI) * U, EYE * GROUND_DPI * U  # its rows still land at 300 DPI
    depth = GROUND_DEPTH * SETT                             # source px from the wall's foot to the sheet edge
    K = depth / (1 / Hh - 1 / (Hh + G))
    x0, z0, s0 = src.width / 2, SETT * 0.3, 1 / (S * U)
    # output (x, y) -> source (s0 (x - W/2 - LEAN y) + x0, z0 + (K / Hh) y / (Hh + y)):
    # no one projective map does that, so it is laid in bands two px deep
    X = lambda x, y: s0 * (x - W / 2 - LEAN * y) + x0
    Z = lambda y: z0 + (K / Hh) * y / (Hh + y)
    mesh = [((0, y, W, min(G, y + 2)), (X(0, y), Z(y), X(0, min(G, y + 2)), Z(min(G, y + 2)),
                                        X(W, min(G, y + 2)), Z(min(G, y + 2)), X(W, y), Z(y)))
            for y in range(0, G, 2)]
    strip = src.transform((W, G), Image.MESH, mesh, Image.BICUBIC).reduce(U)
    rgb = tint(strip, tones).convert("RGB")
    px = rgb.load()
    line = tuple(round(c * 0.55) for c in BG)               # the wall's foot
    for y in range(rgb.height):
        k = GROUND_SHADE * (0.8 + 0.2 * min(1, y / (14 * S)))  # its shadow, fading over 14 wall px
        for x in range(rgb.width):
            px[x, y] = line if y < 3 * S else tuple(round(v * k) for v in px[x, y])
    return rgb                                              # RGB: the shadow makes too many tones for a palette


def brick_tones():
    """The brick tile's pixels as multiples of --bg, darkest first."""
    bg = lum(BG)
    return sorted(lum(c) / bg for c in Image.open(BRICK).convert("RGB").get_flattened_data())


def tint(tile, tones):
    """Invert the tile's tones and match them to the brick's, as a palette image of
    --bg times each brick tone (levels that land on one colour share its index)."""
    inv = ImageOps.invert(tile)
    count = inv.histogram()
    colours, index, seen = [], [], 0
    for v in range(256):
        # the brick tone at the middle of this level's share of the tile
        level = tones[min(len(tones) - 1, int((seen + count[v] / 2) / sum(count) * len(tones)))]
        c = tuple(min(255, round(BG[i] * level)) for i in range(3))
        if c not in colours:
            colours.append(c)
        index.append(colours.index(c))
        seen += count[v]
    out = Image.frombytes("P", inv.size, inv.point(index).tobytes())
    out.putpalette([v for c in colours for v in c])
    return out


def replace_block(path, name, body):
    import re
    with open(path) as fh:
        css = fh.read()
    begin = f"/* {name}:begin — generated by scripts/wall-tiles.py; edit that, not this */"
    new, count = re.subn(rf"/\* {name}:begin.*?{name}:end \*/", lambda m: f"{begin}\n{body}\n/* {name}:end */", css, flags=re.S)
    if count != 1:
        raise SystemExit(f"{path}: expected one {name}:begin ... {name}:end block, found {count}")
    with open(path, "w") as fh:
        fh.write(new)


def ground_of(n):
    """The street a wall's pages stand on."""
    return STREETS[WALL_STREET[n]]


def asphalt(seed, size=SETT * SETTS):
    """Cracked asphalt, flat, as the ground's source: high values come out dark. A
    fine grain and cracks that wander and branch. (Cut-in patches were tried: in
    the strip's shallow perspective their seams stretched into long lines.)"""
    rnd = random.Random(seed)
    grain = Image.effect_noise((size, size), 46).filter(ImageFilter.GaussianBlur(0.8))
    out = ImageChops.multiply(grain, Image.new("L", grain.size, 190))
    draw = ImageDraw.Draw(out)
    for _ in range(14):                                  # cracks: random walks that branch
        # mostly across the street: a crack running toward the viewer is stretched
        # into a long straight line by the strip's shallow perspective
        x, y, a = rnd.randrange(size), rnd.randrange(size), rnd.choice((0, math.pi)) + rnd.uniform(-0.5, 0.5)
        stack = [(x, y, a, rnd.randint(50, 120))]
        while stack:
            x, y, a, n = stack.pop()
            for _ in range(n):
                a += rnd.uniform(-0.45, 0.45)
                a += (round(a / math.pi) * math.pi - a) * 0.15   # drawn back toward across
                nx, ny = x + 4 * math.cos(a), y + 4 * math.sin(a)
                a0, a1 = (x % size, y % size), (nx % size, ny % size)
                if abs(a0[0] - a1[0]) < 8 and abs(a0[1] - a1[1]) < 8:   # not across the wrap: that line spans the tile
                    draw.line((*a0, *a1), fill=255, width=rnd.choice((2, 2, 3)))
                x, y = nx, ny
                if rnd.random() < 0.025:
                    stack.append((x, y, a + rnd.choice((-1, 1)) * rnd.uniform(0.4, 0.8), rnd.randint(12, 35)))
    return out


def grime(rgb, seed, base=1.0, grain=0):
    """Street dirt over a drawn ground, in the book's flat, drawn look: hard-edged
    tone steps, never a soft blur, and darkening only, so it stays in the brick's
    greys. Ragged stains in two flat tones, soot pooled along the wall's foot,
    grit specks and chips, and a ragged gutter edge at the sheet's foot.
    `base` darkens the whole surface (asphalt), `grain` adds its speckle."""
    import numpy as np
    rng = np.random.default_rng(seed)
    a = np.asarray(rgb).astype(float) * base
    H, W = a.shape[:2]

    def noise(sx, sy):                                   # smooth noise, cells sx by sy px
        cells = rng.random((H // sy + 3, W // sx + 3))
        im = Image.fromarray((cells * 255).astype("uint8")).resize((W + 3 * sx, H + 3 * sy), Image.BICUBIC)
        return np.asarray(im.crop((sx, sy, sx + W, sy + H))).astype(float) / 255

    rough = noise(3, 3) * 0.10                           # ragged edges: a fine jitter on every threshold
    blot = noise(80, 24) + rough
    stains = 0.13 * (blot > 0.70) + 0.11 * (blot > 0.84)  # two flat tones, hard edges
    spots = noise(22, 9) + rough
    stains += 0.12 * (spots > 0.86)
    y = np.arange(H)[:, None] / H
    # soot pooled along the wall's foot: a ragged band, deepest where the noise says
    reach = 0.10 + 0.22 * noise(26, H)[:1, :] ** 2 + 0.05 * noise(5, H)[:1, :]   # ragged in 5px steps, not per pixel
    foot = 0.16 * (y < reach) + 0.08 * (y < reach * 0.45)
    gutter = 0.12 * (y > 0.84 + (noise(18, H)[:1, :] - 0.5) * 0.10 + (noise(5, H)[:1, :] - 0.5) * 0.04)
    specks = rng.random((H, W))
    grit = 0.40 * (specks < 0.004) + 0.22 * ((specks >= 0.004) & (specks < 0.010))
    chips = Image.fromarray(((rng.random((H, W)) < 0.0008) * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3))
    grit = np.maximum(grit, 0.30 * (np.asarray(chips) > 0))
    if grain:
        grit = np.maximum(grit, grain * (rng.random((H, W)) < 0.12))
    k = (1 - np.minimum(stains, 0.36)) * (1 - foot) * (1 - gutter) * (1 - grit)
    return Image.fromarray(np.clip(a * k[..., None], 0, 255).astype("uint8"))


def street(kind, tones):
    """One of the three streets, drawn and grimed."""
    panel = Image.open(SHEET).convert("RGBA").crop(opaque_boxes(Image.open(SHEET).convert("RGBA"))[GROUND_FROM - 1]).convert("L")
    if kind == "setts":
        grid = lay_setts(panel, seed=60)
    elif kind == "flags":                               # bigger slabs, every other row half along
        grid = lay_setts(panel, seed=61, bond=True)
        grid = grid.resize((round(grid.width * 1.7), round(grid.height * 1.7)), Image.LANCZOS)
    else:
        grid = asphalt(seed=62)
    asph = kind == "asphalt"
    return grime(ground(None, tones, grid=grid), seed=sum(map(ord, kind)), base=0.80 if asph else 1.0, grain=0.14 if asph else 0)


def ground_layer(deeper="", sheet=False, n=None):
    """The ground's background layer, as dc-native.css §1 writes it for the brick.
    Print measures an @page background from the top of the text area, and
    gutterpress publishes that area's height (--gp-content-h) to print only, so
    the strip sits at content height + bottom margin - its own depth there. The
    app's viewer paints it on the sheet instead, where --gp-content-h is not set:
    the fallback makes the sum 100%, the sheet's foot. `deeper` is a page's top
    margin past the default, which print alone must take back. `sheet` is a
    page with no margins (a full-bleed plate's): its text area is the sheet in
    print too, so the strip sits its depth above the sheet's foot in both."""
    take = f" + {deeper}" if deeper else ""
    back = f" - {deeper}" if deeper else ""
    y = (f"calc(var(--gp-content-h, 100% - var(--bottom-margin) + {GROUND_IN}in{take}) "
         f"+ var(--bottom-margin) - {GROUND_IN}in{back})")
    if sheet:
        y = f"calc(var(--gp-page-height, 11.25in) - {GROUND_IN}in)"
    return f'url("../{ground_of(n) if n else GROUND}") 50% {y} / {GROUND_W / GROUND_DPI:g}in {GROUND_IN}in no-repeat'


def write_css(walls):
    pages, wiring = [], []
    for n, (w, h) in walls.items():
        # the ground over the foot of the sheet, then the wall: both opaque
        stone = f'url("../images/wall-{n}.png") 0 0 / {w / DPI:.2f}in auto repeat var(--bg)'
        bg = f"{ground_layer(n=n)}, {stone}"

        for name in [f"dc-wall-{n}"] + [f"dc-wall-{n}-{hue}" for hue in HUES]:
            pages.append(f"@page {name} {{ background: {bg}; }}")
        for hue, token in HUES.items():
            pages.append(f"@page dc-wall-{n}-{hue}:left  {{ @bottom-right {{ background: var({token}); }} }}")
            pages.append(f"@page dc-wall-{n}-{hue}:right {{ @bottom-left  {{ background: var({token}); }} }}")
        # each chapter's twin, then the plain wall, then a block that is not a
        # .page: the app's viewer takes the first rule that matches, print the
        # cascade (the twin outranks the plain rule), and both get the same page
        page = f".page.dc-page-wall-{n}:where(:not({KEEPS}))"
        for chapter, hue in CHAPTER_HUES.items():
            wiring.append(f".chapter.dc-chapter-{chapter} > {page} {{ page: dc-wall-{n}-{hue}; }}")
        wiring.append(f"{page} {{ page: dc-wall-{n}; }}")
        # a block that stands for its pages with no .page of its own (a
        # specialty: `@specialty .augmerc .dc-page-wall-3`) names them through
        # its children, never itself: the app's viewer lays a block that has a
        # page name as one run on that page and never looks inside it, so the
        # art plate in it (page: full) was set inside the wall's margins.
        # Every child but a plate names the wall. In a chapter with a colour it
        # names that wall's twin, so the chip keeps the chapter's colour (a
        # specialty's pages had shown the default magenta chip): the twins
        # come first and outrank the plain rule, as for a .page
        block = f":where(.dc-page-wall-{n}:not(.page, {KEEPS})) > :not({PLATES})"
        for chapter, hue in CHAPTER_HUES.items():
            wiring.append(f".chapter.dc-chapter-{chapter} {block} {{ page: dc-wall-{n}-{hue}; }}")
        wiring.append(f"{block} {{ page: dc-wall-{n}; }}")
        # and its art plate takes this wall too, on a page like `@page full`
        # (no margins, no chips): the specialty art is transparent, so the
        # wall and its ground show through it. The selector outranks
        # `.dc-specialty-art { page: full }` in print and comes before it for
        # the viewer
        wiring.append(f"@page dc-wall-{n}-full {{ margin: 0; background: {ground_layer(sheet=True, n=n)}, {stone}; "
                      "@bottom-left { content: none; } @bottom-right { content: none; } }")
        wiring.append(f".dc-page-wall-{n}:not(.page, {KEEPS}) > .dc-specialty-art {{ page: dc-wall-{n}-full; }}")
    replace_block("styles/dc-native.css", "page-walls", "\n".join(pages))
    replace_block("styles/page-rules.css", "page-walls", "\n".join(wiring))


def bake(job):
    n, box = job
    panel = Image.open(SHEET).convert("RGBA").crop(box).convert("RGB")
    if n in BEDDED:
        panel = panel.resize((panel.width, round(panel.height * BEDDED[n])), Image.LANCZOS)
    if n in SETT_WALLS:
        tile = lay_setts(panel.convert("L"), seed=n, bond=True)
    else:
        rows = wrap_x(rows_of(panel), cyclic=False)             # left-right
        rows = transpose(wrap_x(transpose(rows), cyclic=True))  # top-bottom, closing round the first
        seamless = Image.new("RGB", (len(rows[0]), len(rows)))
        seamless.putdata([c for r in rows for c in r])
        tile = quilt(seamless.convert("L"), seed=n)
    if n == GROUND_FROM:
        ground(panel.convert("L"), brick_tones()).save(GROUND, optimize=True)
    out = tint(tile, brick_tones())
    out.save(f"images/wall-{n}.png", optimize=True)
    avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
    print(f"images/wall-{n}.png  {out.width}x{out.height}  {out.width / DPI:.2f}in wide  "
          f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  from {box}", flush=True)
    return n, out.size


def main():
    if "--ground" in sys.argv:              # the ground alone, from its wall's panel
        box = opaque_boxes(Image.open(SHEET).convert("RGBA"))[GROUND_FROM - 1]
        panel = Image.open(SHEET).convert("RGBA").crop(box).convert("L")
        ground(panel, brick_tones()).save(GROUND, optimize=True)
        return
    if "--grounds" in sys.argv:             # the three streets, grimed, and the CSS
        tones = brick_tones()
        for kind, path in STREETS.items():
            street(kind, tones).save(path, optimize=True)
            print(path, flush=True)
        write_css({n: Image.open(f"images/wall-{n}.png").size for n in range(1, 7)})
        return
    if "--css" in sys.argv:                 # the CSS alone, from the tiles already baked
        write_css({n: Image.open(f"images/wall-{n}.png").size for n in range(1, 7)})
        return
    boxes = opaque_boxes(Image.open(SHEET).convert("RGBA"))
    with Pool(len(boxes)) as pool:
        walls = dict(pool.map(bake, enumerate(boxes, 1)))
    write_css(walls)


if __name__ == "__main__":
    main()
