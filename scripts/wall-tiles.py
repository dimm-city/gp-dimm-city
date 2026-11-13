"""The CSS for every page wall, and the streets under them.

    python3 scripts/wall-tiles.py           # the CSS, from the tiles in images/
    python3 scripts/wall-tiles.py --ground  # redraw the ground (the setts) only
    python3 scripts/wall-tiles.py --grounds # the three streets (setts, flags, asphalt), grimed, and the CSS

Python 3 with Pillow. Every wall tile is drawn by its own script in scripts/
at DPI (300), the print bar: 1-6 the stone walls (wall-stone-rubble.py: 1, 3,
5; wall-stone-coursed.py: 2, 4, 6), 7-13 the specialty walls (wall-metal.py,
wall-circuit.py, wall-moss.py, wall-surgery.py, wall-aether.py,
wall-techlab.py, wall-bazaar.py). This script rewrites the generated
`page-walls` blocks in styles/dc-native.css (each wall's named pages: the
background, and the chapter chip's face per hue) and styles/page-rules.css (the
wiring from page word to named page), sizing each tile at DPI.

The streets are drawn here. The setts and the flags are laid from the painted
sheet's square-sett panel (source-art/wall-sheet.png, panel GROUND_FROM):
its whole setts (a joint on every side) are cut out, resized to one SETT-px
cell and laid in random turns and flips, no sett beside itself, with the
panel's mean joint drawn along every cell edge; the asphalt is drawn. Each is
tinted to the brick (images/brick-wall.png: --bg times a grey line drawing),
seen in perspective from EYE above it and grimed. The sheet's setts are at
SHEET_DPI (240); the ground resamples them to GROUND_DPI (300) in its
perspective transform and draws its joints, foot line and shadow at that
resolution, for the depth Chromium paints it at (a background is painted in
whole CSS px: 0.6in is 58px, 0.604in), so its rows measure 300 DPI.
"""
import math
import random
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SHEET = ARGS[0] if ARGS else "source-art/wall-sheet.png"
BG = (0xC8, 0xC5, 0xBF)             # --bg (ash concrete), the brick's colour
BRICK = "images/brick-wall.png"     # the tones to match: --bg times the brick's line drawing
DPI = 300                           # every wall tile is drawn at the print bar, so printed size = px / DPI
SHEET_DPI = 240                     # the painted sheet's scale: the ground's setts are laid at it
SETT, SETTS = 136, 8                # the sett cell, px, and cells a side
JOINT = 6                           # half-width of the drawn joint, px
GROUND = "images/ground.png"        # the setts: the street under the brick
# Three streets, none a copy of a wall (a street of the wall's own stone read as
# the wall carrying on, not as ground): setts, bonded flagstones cut from the
# same stone, and cracked, patched asphalt. Each wall stands on one that
# contrasts with it. All of them are grimed (`grime`). `--grounds` draws them.
STREETS = {"setts": GROUND, "flags": "images/ground-flags.png", "asphalt": "images/ground-asphalt.png"}
WALL_STREET = {1: "flags", 2: "asphalt", 3: "setts", 4: "flags", 5: "setts", 6: "asphalt", 7: "asphalt", 8: "setts",
               9: "asphalt", 10: "asphalt", 11: "flags", 12: "setts", 13: "flags"}
# Walls with a regular grid (7's steel plates, 9's courses, 10's tiles, 11's courses and plates, 12's conduit, 13's stalls): an @page background is placed
# from the text area's corner, which sits at a different place on a left page,
# a right page and a margin-free page, so a grid restarts on each and breaks at
# the spine. These are anchored to the sheet instead, and a right page carries
# on from the left page's width: a spread is one wall. (A stone wall has no grid
# to break, so it keeps the text area's corner. Walls 8 and 11 also carry a
# board or a rift the spine cuts on across the spread.)
ALIGNED = {7, 8, 9, 10, 11, 12, 13}
SHEET_W = "var(--gp-page-width, 8.625in)"
ANCHOR = {   # tile offset from the text area's corner, per side; a full page has no margins
    "left": ("calc(-1 * var(--outer-margin))", "calc(-1 * var(--page-margin))"),
    "right": (f"calc(-1 * ({SHEET_W} + var(--binding-margin)))", "calc(-1 * var(--page-margin))"),
    "full-left": ("0", "0"),
    "full-right": (f"calc(-1 * {SHEET_W})", "0"),
}
WALLS = range(1, 14)
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
        "amethyst": "--crystal-amethyst", "amber": "--amber-dark", "indigo": "--signal-indigo",
        "ink": "--ink-dark"}
CHAPTER_HUES = {"specialty": "blue", "rules": "rust", "lore": "violet", "dm": "ink", "gear": "indigo"}
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


def transpose(rows):
    return [list(col) for col in zip(*rows)]


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
    S = GROUND_DPI / SHEET_DPI                              # output px per source px: the setts are at the sheet's scale
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
        def stone_at(x="0", y="0"):
            return f'url("../images/wall-{n}.png") {x} {y} / {w / DPI:.2f}in auto repeat var(--bg)'
        stone = stone_at()
        bg = f"{ground_layer(n=n)}, {stone}"

        for name in [f"dc-wall-{n}"] + [f"dc-wall-{n}-{hue}" for hue in HUES]:
            pages.append(f"@page {name} {{ background: {bg}; }}")
            if n in ALIGNED:
                for side in ("left", "right"):
                    pages.append(f"@page {name}:{side} {{ background: {ground_layer(n=n)}, {stone_at(*ANCHOR[side])}; }}")
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
        if n in ALIGNED:
            for side in ("left", "right"):
                wiring.append(f"@page dc-wall-{n}-full:{side} {{ background: {ground_layer(sheet=True, n=n)}, "
                              f"{stone_at(*ANCHOR['full-' + side])}; }}")
        wiring.append(f".dc-page-wall-{n}:not(.page, {KEEPS}) > .dc-specialty-art {{ page: dc-wall-{n}-full; }}")
    replace_block("styles/dc-native.css", "page-walls", "\n".join(pages))
    replace_block("styles/page-rules.css", "page-walls", "\n".join(wiring))


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
        write_css({n: Image.open(f"images/wall-{n}.png").size for n in WALLS})
        return
    write_css({n: Image.open(f"images/wall-{n}.png").size for n in WALLS})


if __name__ == "__main__":
    main()
