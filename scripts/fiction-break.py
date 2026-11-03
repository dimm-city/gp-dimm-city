"""Draw the fiction excerpt's hole smashed in the wall, as two clip-path polygons.

    python3 scripts/fiction-break.py [seed]    # default seed 4

Rewrites the generated block in styles/dc-component-defaults.css (between the
`fiction-break:begin` and `fiction-break:end` comments). Python 3, standard
library only. The seed picks the shape; 4 is the one that ships.

Both polygons sit on the excerpt's ::before / ::after, a box 16px larger than
the excerpt all round. Depths are px in from that outer edge, so the excerpt's
own edge is depth 16, and the wall never reaches past it:

  --dc-fiction-hole   the hole: the wall's broken edge, stepping between depth 4
                      and 16 along the brick courses, with a few hairline cracks
                      into the bricks. Filled with --dc-fiction-cavity (::before).
  --dc-fiction-shape  the page: the hole shrunk by T px, so the band between the
                      two is the broken wall's thickness, one face all round with
                      every step's sides joined. Filled with --dc-fiction-bg.

Bricks keep their size at any box size: each edge holds a whole number of P-px
runs (CSS round()), centred between its corners. K runs are drawn per edge; one
the edge has no room for collapses onto the end of the last that fits (zero-area
spikes, which paint nothing). Every run and corner is flat at depth D0 for more
than T px where it meets the next, so the shrink never crosses a join. Vector
all the way: no image, so nothing tiles, seams at any zoom or prints as a bitmap.
"""
import random
import re
import sys

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
SHEET = "styles/dc-component-defaults.css"

C = 46            # corner zone, from the outer corner along each edge
P = 172           # a run: four bricks of the wall tile (43px)
K = 6             # runs drawn per edge: 92 + 6 * 172 = 1124px, more than a page
BRICK = 43
D0 = 8            # the depth at every join
LEVELS = [4, 8, 12, 16]
T = 5             # the broken wall's thickness: the face band
FLAT = T + 2      # flat at D0 at both ends of a run


def run_profile():
    """One run's risers: [(t, depth_after)], t in (FLAT, P - FLAT); D0 before the first."""
    risers, t, d = [], FLAT, D0
    while True:
        t += random.choice([BRICK // 2, BRICK, BRICK, BRICK + BRICK // 2])
        if t > P - FLAT - 12:
            break
        nd = random.choice([x for x in LEVELS if x != d])
        if abs(nd - d) >= 8 and random.random() < 0.35:
            # a fractured brick end: a short jog halfway down the riser
            j = random.choice([-3, 3])
            risers += [(min(t, t + j), (d + nd) // 2), (max(t, t + j), nd)]
        else:
            risers.append((t, nd))
        d = nd
    if d != D0:
        risers.append((P - FLAT, D0))
    return risers


def depth_at(risers, x):
    d = D0
    for t, after in risers:
        if x >= t:
            d = after
    return d


def shrink(risers):
    """The run's edge moved T px into the hole: depth'(x) = (deepest within T of x) + T."""
    h, out, prev = 0.5, [], D0 + T
    for i in range(int(P / h)):
        x = i * h + h / 2
        d = max([depth_at(risers, x - T)] + [a for t, a in risers if x - T < t <= x + T]) + T
        if d != prev:
            out.append((i * h, d))
            prev = d
    return out


def cracks(risers):
    """One or two hairline cracks per run, from a flat stretch into the bricks."""
    out = []
    for _ in range(random.choice([1, 1, 2])):
        x = random.randint(FLAT + 8, P - FLAT - 8)
        if any(abs(x - t) < 8 for t, _ in risers):
            continue
        d = depth_at(risers, x)
        if d >= 8:
            out.append((x, d, min(d - 2, random.randint(5, 10)), random.choice([-1, 1])))
    return out


def px(v):
    return f"{v:g}px"


def along(s, rev):
    """A point s px into an edge's runs, from its start corner (or its end, rev)."""
    a = f"var(--dc-fiction-run-at) {'-' if rev else '+'} min({px(s)}, var(--dc-fiction-run))"
    return f"calc(100% - {a})" if rev else f"calc({a})"


def far(v):
    return f"calc(100% - {px(v)})"


def place(side, s, d):
    """(s along the side in polygon order, depth d) -> polygon coordinate."""
    return {
        "top": lambda: f"{along(s, False)} {px(d)}",
        "right": lambda: f"{far(d)} {along(s, False)}",
        "bottom": lambda: f"{along(s, True)} {far(d)}",
        "left": lambda: f"{px(d)} {along(s, True)}",
    }[side]()


def side_points(side, inset):
    e = D0 + inset
    pts = [(0, e)]
    for k, r in enumerate(RUNS[side]):
        d, base = e, k * P
        events = [(t, "r", a) for t, a in (shrink(r) if inset else r)]
        if not inset:
            events += [(x, "c", (dd, L, w)) for x, dd, L, w in CRACKS[side][k]]
        for t, kind, v in sorted(events, key=lambda ev: ev[0]):
            if kind == "r":
                pts += [(base + t, d), (base + t, v)]
                d = v
            else:
                dd, L, w = v
                pts += [(base + t - 0.8, dd), (base + t + 0.4 * w, dd - L), (base + t + 0.8, dd)]
    pts.append((K * P, e))
    return [place(side, s, d) for s, d in pts]


def corner(name, inset):
    """A corner zone, walked clockwise: a chunk of brick A deep and B across, or none."""
    a, b = CHUNKS[name]
    e, A, B, c = D0 + inset, a + inset, b + inset, C
    f = far
    if a == D0:
        return {"tl": [f"{px(e)} {px(c)}", f"{px(e)} {px(e)}", f"{px(c)} {px(e)}"],
                "tr": [f"{f(c)} {px(e)}", f"{f(e)} {px(e)}", f"{f(e)} {px(c)}"],
                "br": [f"{f(e)} {f(c)}", f"{f(e)} {f(e)}", f"{f(c)} {f(e)}"],
                "bl": [f"{px(c)} {f(e)}", f"{px(e)} {f(e)}", f"{px(e)} {f(c)}"]}[name]
    return {"tl": [f"{px(e)} {px(c)}", f"{px(e)} {px(A)}", f"{px(B)} {px(A)}", f"{px(B)} {px(e)}", f"{px(c)} {px(e)}"],
            "tr": [f"{f(c)} {px(e)}", f"{f(B)} {px(e)}", f"{f(B)} {px(A)}", f"{f(e)} {px(A)}", f"{f(e)} {px(c)}"],
            "br": [f"{f(e)} {f(c)}", f"{f(e)} {f(A)}", f"{f(B)} {f(A)}", f"{f(B)} {f(e)}", f"{f(c)} {f(e)}"],
            "bl": [f"{px(c)} {f(e)}", f"{px(B)} {f(e)}", f"{px(B)} {f(A)}", f"{px(e)} {f(A)}", f"{px(e)} {f(c)}"]}[name]


def polygon(inset):
    pts = []
    for cname, side in [("tl", "top"), ("tr", "right"), ("br", "bottom"), ("bl", "left")]:
        pts += corner(cname, inset) + side_points(side, inset)
    return "polygon(" + ", ".join(pts) + ")"


SIDES = ["top", "right", "bottom", "left"]
RUNS = {s: [run_profile() for _ in range(K)] for s in SIDES}
CRACKS = {s: [cracks(r) for r in RUNS[s]] for s in SIDES}
CHUNKS = {c: random.choice([(D0, D0), (12, 12), (12, 16), (16, 12), (16, 16)]) for c in ["tl", "tr", "br", "bl"]}

block = f"""/* fiction-break:begin — generated by scripts/fiction-break.py; edit that, not this */
  --dc-fiction-run:          clamp(0px, round(down, calc(100% - {2 * C}px), {P}px), {K * P}px);  /* the runs an edge has room for: whole runs, centred */
  --dc-fiction-run-at:       calc({C}px + (100% - {2 * C}px - var(--dc-fiction-run)) / 2);
  --dc-fiction-hole:         {polygon(0)};
  --dc-fiction-shape:        {polygon(T)};
  /* fiction-break:end */"""

with open(SHEET) as fh:
    css = fh.read()
new, n = re.subn(r"/\* fiction-break:begin.*?fiction-break:end \*/", lambda m: block, css, flags=re.S)
if n != 1:
    raise SystemExit(f"{SHEET}: expected one fiction-break:begin ... fiction-break:end block, found {n}")
with open(SHEET, "w") as fh:
    fh.write(new)
print(f"wrote {SHEET}: hole {len(polygon(0))} chars, shape {len(polygon(T))} chars")
