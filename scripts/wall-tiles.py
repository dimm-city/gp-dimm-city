"""Bake the six stone-wall page tiles (`@page wall-1` ... `wall-6`) and their CSS.

    python3 scripts/wall-tiles.py [source-art/wall-sheet.png]

Python 3 with Pillow. Reads the sheet (six square-ish stone panels on a
transparent ground, two columns by three rows), writes images/wall-1.png ...
wall-6.png, each an opaque tile in the brick's colours that repeats without a
visible join, and rewrites the generated `page-walls` blocks in styles/dc-native.css (each wall's
named pages: the background, and the chapter chip's face per hue) and
styles/page-rules.css (the wiring from page word to named page).

For each panel:
1. Crop to the part that is fully opaque (the panels' edges are ragged).
2. Make it wrap left-right, then top-bottom, with a minimum-error seam cut
   (image quilting): choose the overlap whose two ends match best (that also
   locks a regular bond onto its period), then cut through that overlap along
   the path where the two ends differ least, which runs mostly down the mortar.
   The second cut wraps round the first axis, so the corners close too.
3. Tint it to the brick: the sheet is dark stone with light mortar, the brick
   is light ash (--bg) with grey joints, so the tones are inverted (the stone
   faces go light, the mortar and the pits grey) and matched, level by level,
   to the brick tile's own (images/brick-wall.png: --bg times a grey line
   drawing). Each tile then has the brick's average and its darkest grey, and
   the CSS puts --bg under it, as the brick's rule does.
4. Save as PNG, opaque: lossless, so the joints keep their edges (a JPEG rings
   round them), and PDF/X carries an opaque tile as is.

The tiles keep the source's pixels (about 300-390px a side) and print at DPI
dots per inch, which sets their printed size (1.3-1.6in): the bricks come out
close to the default wall's. A sharper source would let them print at 300.
"""
import sys
from PIL import Image

SHEET = sys.argv[1] if len(sys.argv) > 1 else "source-art/wall-sheet.png"
BG = (0xC8, 0xC5, 0xBF)             # --bg (ash concrete), the brick's colour
BRICK = "images/brick-wall.png"     # the tones to match: --bg times the brick's line drawing
OVERLAP = range(28, 110)            # how much of each end the seam may use, px
FEATHER = 2                         # px blended either side of a cut
DPI = 240                           # print resolution, so printed size = px / DPI
# A wall page keeps its chapter's chip colour: one named page per wall and hue.
# The hue faces and the chapter words that wire them are page-rules.css's and
# dc-native.css's (2c); a book wires its own chapters the same way.
HUES = {"blue": "--hud-blue-dark", "rust": "--rust", "violet": "--brand-violet",
        "amethyst": "--crystal-amethyst", "amber": "--amber-dark"}
CHAPTER_HUES = {"specialty": "blue", "rules": "rust", "lore": "violet"}


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


def brick_tones():
    """The brick tile's pixels as multiples of --bg, darkest first."""
    bg = lum(BG)
    return sorted(lum(c) / bg for c in Image.open(BRICK).convert("RGB").get_flattened_data())


def tint(rows, tones):
    """Invert the tile's tones and match them to the brick's, then paint --bg times each."""
    vals = [255 - round(lum(c)) for r in rows for c in r]
    count = [0] * 256
    for v in vals:
        count[v] += 1
    level, seen = [0.0] * 256, 0
    for v in range(256):
        if count[v]:
            # the brick tone at the middle of this level's share of the tile
            level[v] = tones[min(len(tones) - 1, int((seen + count[v] / 2) / len(vals) * len(tones)))]
        seen += count[v]
    return [tuple(min(255, round(BG[i] * level[v])) for i in range(3)) for v in vals]


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


def write_css(walls):
    pages, wiring = [], []
    for n, (w, h) in walls.items():
        size = f"{w / DPI:.2f}in"
        bg = f'var(--bg) url("../images/wall-{n}.png") repeat'
        for name in [f"dc-wall-{n}"] + [f"dc-wall-{n}-{hue}" for hue in HUES]:
            pages.append(f"@page {name} {{ background: {bg}; background-size: {size} auto; }}")
        for hue, token in HUES.items():
            pages.append(f"@page dc-wall-{n}-{hue}:left  {{ @bottom-right {{ background: var({token}); }} }}")
            pages.append(f"@page dc-wall-{n}-{hue}:right {{ @bottom-left  {{ background: var({token}); }} }}")
        # never on a full-bleed plate (its page is `full`, wired below at lower
        # specificity); :where keeps these rules at the templates' specificity
        page = f".page.dc-page-wall-{n}:where(:not(.gp-page-full-bleed, .dc-full-page))"
        wiring.append(f"{page} {{ page: dc-wall-{n}; }}")
        for chapter, hue in CHAPTER_HUES.items():
            wiring.append(f":where(.chapter.dc-chapter-{chapter}) > {page} {{ page: dc-wall-{n}-{hue}; }}")
    replace_block("styles/dc-native.css", "page-walls", "\n".join(pages))
    replace_block("styles/page-rules.css", "page-walls", "\n".join(wiring))


def main():
    sheet = Image.open(SHEET).convert("RGBA")
    tones = brick_tones()
    walls = {}
    for n, box in enumerate(opaque_boxes(sheet), 1):
        rows = rows_of(sheet.crop(box).convert("RGB"))
        rows = wrap_x(rows, cyclic=False)                       # left-right
        rows = transpose(wrap_x(transpose(rows), cyclic=True))  # top-bottom, closing round the first
        h, w = len(rows), len(rows[0])
        tile = Image.new("RGB", (w, h))
        tile.putdata(tint(rows, tones))
        tile.save(f"images/wall-{n}.png", optimize=True)
        walls[n] = (w, h)
        avg = tile.resize((1, 1), Image.BOX).getpixel((0, 0))
        print(f"images/wall-{n}.png  {w}x{h}  {w / DPI:.2f}in wide  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  from {box}")
    write_css(walls)


if __name__ == "__main__":
    main()
