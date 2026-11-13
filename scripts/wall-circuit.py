"""Draw wall 8, circuit panels falling apart (`@page wall-8`), as images/wall-8.png.

    python3 scripts/wall-circuit.py      (from the package root; needs numpy and Pillow)
    python3 scripts/wall-tiles.py --css  (then: the CSS for every wall, this one included)

Drawn, not sampled: no photograph goes into it. The tile repeats without a
seam both ways, because everything in it is periodic: the noise is filtered
in the Fourier domain (so it wraps), the shadows and drips are circular
convolutions, and each panel is drawn on its own canvas and laid on the
tile's grid with wrap-around.

What it draws, back to front:
1. The wall behind: a grimy grey render, seen in the gaps between panels and
   where a panel has broken away (one bay has lost its panel altogether:
   only its fixings and a cleaner ghost of it are left).
2. Printed circuit board panels on a 1.25in module grid, two to four modules
   a side, each its own solder-mask colour (aged greens, a teal, an olive, a
   tired blue). On each: chip footprints (QFP, SOIC, BGA, passives, headers,
   electrolytic caps, edge fingers), traces routed in buses at 0/45/90
   degrees with mitred bends and staggered vias, a ground pour on some,
   silkscreen outlines and labels. Some chips are still on, most are gone,
   leaving tinned pads and solder lumps.
3. The damage: corners broken off along a jagged fracture (pale glass fibre
   at the break, traces left dangling from it), chipped edges, cracks, the
   odd impact hole, solder mask peeled away (bare fibreglass and tarnished,
   verdigrised copper underneath, a lifted lip at the peel's edge), measling
   and blisters, burn marks with soot climbing above them, leaking caps,
   sagging bodge wires.
4. Fixings: a screw in a plated mounting hole at each corner (one or two
   missing), rust drips under some, and each panel's drop shadow on the wall.
5. Grime over everything.
It is then quantised to an exact palette, as the other walls are (one colour
per tone, lossless and small; an opaque tile PDF/X carries as is).

At DPI (240, wall-tiles.py's) the tile is 10in square, so a page shows no
repeat. Its panel grid is regular, so wall-tiles.py anchors this wall to the
sheet, not the text area, and offsets a right page by the left page's width:
a spread is one continuous wall.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SIZE = 2400                 # px, square; 10in at 240 DPI, so a page shows no repeat
MOD = 300                   # the panel grid's module, px (1.25in); 8 a side
GAP = 22                    # px between panels
M = 96                      # margin round a panel's canvas: dangling traces, wires, shadows
SS = 2                      # each panel is drawn at SS x and boxed down: clean 45-degree edges
SEED = 8
SHADE = 1.05               # the whole tile; its darkest burn stays well under DriveThruRPG's 240% TAC
FONT = ROOT / "fonts/tomorrow/tomorrow-500.ttf"

rng = np.random.default_rng(SEED)
N = SIZE
R2 = math.sqrt(0.5)
DIRS = [np.array(v) for v in ((1, 0), (R2, R2), (0, 1), (-R2, R2), (-1, 0), (-R2, -R2), (0, -1), (R2, -R2))]
CLEAR = 5                   # px kept clear round a trace by the router
POUR_CLEAR = 7              # px between the ground pour and any other copper
VIA_R, VIA_HOLE = 7.5, 3.0

LAYERS = ("scratch", "board", "cu", "keep", "pad", "hole", "silk", "chip", "chiptext", "lead", "solder",
          "crack", "fringe", "burn", "delam", "dangle", "wire", "cap", "capmetal", "crust")


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def noise(beta, stretch=(1.0, 1.0), seed=None):
    """Periodic 1/f^beta noise in [0, 1] over the tile."""
    r = np.random.default_rng(seed)
    white = r.standard_normal((N, N))
    fy = np.fft.fftfreq(N)[:, None] * stretch[1]
    fx = np.fft.fftfreq(N)[None, :] * stretch[0]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    out = np.real(np.fft.ifft2(np.fft.fft2(white) / f ** beta))
    out -= out.min()
    return out / out.max()


def circ_conv(img, kernel):
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(kernel)))


ky, kx = np.mgrid[0:N, 0:N]
ky = np.where(ky > N // 2, ky - N, ky)
kx = np.where(kx > N // 2, kx - N, kx)


def gauss_kernel(sigma, dx=0, dy=0):
    k = np.exp(-(((kx - dx) ** 2 + (ky - dy) ** 2) / (2 * sigma * sigma)))
    return k / k.sum()


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = np.asarray(t)
    if t.ndim == 2:
        t = t[..., None]
    return a + (b - a) * t


def jag(a, b, rough, r):
    """A jagged fracture from a to b: midpoint displacement, kept near the chord."""
    pts = [np.array(a, float), np.array(b, float)]
    while True:
        out, split = [pts[0]], False
        for p, q in zip(pts, pts[1:]):
            d = q - p
            L = np.hypot(*d)
            if L > 5:
                n = np.array([-d[1], d[0]]) / L
                out.append((p + q) / 2 + n * r.normal(0, rough * L) + r.normal(0, 0.6, 2))
                split = True
            out.append(q)
        pts = out
        if not split:
            return pts


# ── the panel grid: rectangles of 1 to 4 modules, packed on the tile's own torus ─
CELLS = N // MOD
taken = np.zeros((CELLS, CELLS), bool)
SIZES = [((2, 2), 3.0), ((3, 2), 2.2), ((2, 3), 2.2), ((3, 3), 1.2), ((4, 2), 1.0), ((2, 4), 0.8),
         ((4, 3), 0.5), ((1, 2), 0.7), ((2, 1), 0.7), ((1, 1), 0.25)]
cells = []
for cy in range(CELLS):
    for cx in range(CELLS):
        if taken[cy, cx]:
            continue
        opts = sorted(SIZES, key=lambda s: -s[1] * rng.random())
        for (cw, ch), _ in opts + [((1, 1), 0)]:
            ys, xs = [(cy + j) % CELLS for j in range(ch)], [(cx + i) % CELLS for i in range(cw)]
            if not taken[np.ix_(ys, xs)].any():
                taken[np.ix_(ys, xs)] = True
                cells.append((cx, cy, cw, ch))
                break

# ── global fields (all periodic) ───────────────────────────────────────────────
mottle = noise(2.0, seed=SEED + 1)
fine = noise(0.9, seed=SEED + 2)
peeln = noise(1.7, seed=SEED + 3)
tarn = noise(1.5, seed=SEED + 4)
verd = noise(1.3, seed=SEED + 5)
grime = noise(1.9, seed=SEED + 6)
speck = noise(0.35, seed=SEED + 7)
flake = noise(0.7, seed=SEED + 9)
stain = noise(1.6, seed=SEED + 10)
streakn = noise(1.0, stretch=(1.0, 0.10), seed=SEED + 8)
yy, xx = np.mgrid[0:N, 0:N]
weave = (np.cos(2 * np.pi * xx / 8) * np.cos(2 * np.pi * yy / 8))       # glass cloth under the resin

# ── 1. the wall behind ────────────────────────────────────────────────────────
wall = hexc("#7a776f") * (0.86 + 0.22 * mottle + 0.10 * (fine - 0.5))[..., None]
wall *= (0.94 + 0.10 * streakn)[..., None]
wall *= (1 - 0.18 * smooth(speck, 0.78, 0.95))[..., None]


class Panel:
    """One board, drawn on its own canvas (board coords 0..w, 0..h; the canvas
    has a margin M round it) at SS x."""

    def __init__(self, w, h, seed):
        self.w, self.h = w, h
        self.W, self.H = w + 2 * M, h + 2 * M
        self.r = np.random.default_rng(seed)
        self.img = {k: Image.new("L", (self.W * SS, self.H * SS), 0) for k in LAYERS}
        self.drw = {k: ImageDraw.Draw(v) for k, v in self.img.items()}
        self.wcol = Image.new("RGB", (self.W * SS, self.H * SS), (0, 0, 0))
        self.wdrw = ImageDraw.Draw(self.wcol)
        self.occ = np.zeros((h, w), bool)
        self.fractures = []         # (polyline, outward direction) where the board broke off
        self.screws = []
        self.cracks = []
        self.fonts = {}
        self.rect("board", 0, 0, w - 1 / SS, h - 1 / SS)

    # drawing primitives, board coords -------------------------------------
    def xy(self, pts):
        return [((x + M) * SS, (y + M) * SS) for x, y in pts]

    def line(self, layer, pts, width, fill=255):
        d = self.drw[layer]
        d.line(self.xy(pts), fill=fill, width=max(1, round(width * SS)), joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.disc(layer, x, y, width / 2, fill)

    def disc(self, layer, x, y, r, fill=255):
        (cx, cy), = self.xy([(x, y)])
        self.drw[layer].ellipse((cx - r * SS, cy - r * SS, cx + r * SS, cy + r * SS), fill=fill)

    def ring(self, layer, x, y, r, width, fill=255):
        (cx, cy), = self.xy([(x, y)])
        self.drw[layer].ellipse((cx - r * SS, cy - r * SS, cx + r * SS, cy + r * SS), outline=fill,
                                width=max(1, round(width * SS)))

    def rect(self, layer, x0, y0, x1, y1, fill=255, outline=None):
        (a, b), (c, d) = self.xy([(x0, y0), (x1, y1)])
        if outline:
            self.drw[layer].rectangle((a, b, c, d), outline=fill, width=max(1, round(outline * SS)))
        else:
            self.drw[layer].rectangle((a, b, c, d), fill=fill)

    def poly(self, layer, pts, fill=255):
        self.drw[layer].polygon(self.xy(pts), fill=fill)

    def text(self, s, x, y, size, vertical=False, layer="silk"):
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(str(FONT), round(size * SS))
        font = self.fonts[size]
        box = font.getbbox(s)
        tw, th = box[2] - box[0], box[3] - box[1]
        bw, bh = (th, tw) if vertical else (tw, th)
        x0, y0 = int(x), int(y)
        if not self.free_box(x0 - 2, y0 - 2, x0 + bw / SS + 2, y0 + bh / SS + 2, 0):
            return False
        t = Image.new("L", (tw + 4, th + 4), 0)
        ImageDraw.Draw(t).text((2 - box[0], 2 - box[1]), s, fill=255, font=font)
        if vertical:
            t = t.rotate(90, expand=True)
        (px, py), = self.xy([(x0, y0)])
        base = self.img[layer]
        region = base.crop((px, py, px + t.width, py + t.height))
        base.paste(Image.fromarray(np.maximum(np.asarray(region), np.asarray(t))), (px, py))
        self.mark_box(x0, y0, x0 + bw / SS, y0 + bh / SS, 2)
        return True

    # occupancy (1x, board coords) -----------------------------------------
    def free_box(self, x0, y0, x1, y1, inset=14):
        x0, y0, x1, y1 = int(math.floor(x0)), int(math.floor(y0)), int(math.ceil(x1)), int(math.ceil(y1))
        if x0 < inset or y0 < inset or x1 > self.w - inset or y1 > self.h - inset:
            return False
        return not self.occ[y0:y1, x0:x1].any()

    def mark_box(self, x0, y0, x1, y1, pad=CLEAR):
        x0, y0 = max(0, int(x0 - pad)), max(0, int(y0 - pad))
        x1, y1 = min(self.w, int(x1 + pad + 1)), min(self.h, int(y1 + pad + 1))
        self.occ[y0:y1, x0:x1] = True

    def stamp(self, pts, r):
        r = int(math.ceil(r))
        for p, q in zip(pts, pts[1:]):
            L = max(1, int(np.hypot(*(np.subtract(q, p)))))
            for t in np.linspace(0, 1, L // 2 + 2):
                x, y = int(p[0] + (q[0] - p[0]) * t), int(p[1] + (q[1] - p[1]) * t)
                self.occ[max(0, y - r):max(0, y + r + 1), max(0, x - r):max(0, x + r + 1)] = True

    # copper ------------------------------------------------------------------
    def trace(self, pts, width):
        self.line("cu", pts, width)
        self.line("keep", pts, width + 2 * POUR_CLEAR)
        self.stamp(pts, width / 2 + CLEAR)

    def pad_rect(self, x0, y0, x1, y1, layer_extra=None):
        self.rect("cu", x0, y0, x1, y1)
        self.rect("pad", x0, y0, x1, y1)
        self.rect("keep", x0 - POUR_CLEAR, y0 - POUR_CLEAR, x1 + POUR_CLEAR, y1 + POUR_CLEAR)

    def pad_disc(self, x, y, r):
        self.disc("cu", x, y, r)
        self.disc("pad", x, y, r)
        self.disc("keep", x, y, r + POUR_CLEAR)

    def via(self, x, y, tented=None):
        if tented is None:
            tented = self.r.random() < 0.7
        self.disc("cu", x, y, VIA_R)
        if not tented:
            self.disc("pad", x, y, VIA_R)
        self.disc("keep", x, y, VIA_R + POUR_CLEAR)
        self.disc("hole", x, y, VIA_HOLE)
        self.mark_box(x - VIA_R, y - VIA_R, x + VIA_R, y + VIA_R, 3)

    def th(self, x, y, r, hole, square=False):
        if square:
            self.pad_rect(x - r, y - r, x + r, y + r)
        else:
            self.pad_disc(x, y, r)
        self.disc("hole", x, y, hole)

    # the router: a bus of k traces, mitred bends, 45-degree turns only ----------
    def free_len(self, p, d, L, hw, skip, allow_out, inset=10):
        n = np.array([-d[1], d[0]])
        ts = np.arange(skip, L + 1, 3.0)
        if len(ts) == 0:
            return 0
        ss = np.linspace(-hw, hw, max(2, int(2 * hw / 3) + 2))
        X = np.rint(p[0] + ts[:, None] * d[0] + ss[None, :] * n[0]).astype(int)
        Y = np.rint(p[1] + ts[:, None] * d[1] + ss[None, :] * n[1]).astype(int)
        within = (X >= 0) & (X < self.w) & (Y >= 0) & (Y < self.h)
        hit = np.zeros(X.shape, bool)
        hit[within] = self.occ[Y[within], X[within]]
        if not allow_out:
            hit |= (X < inset) | (X >= self.w - inset) | (Y < inset) | (Y >= self.h - inset)
        rows = hit.any(1)
        if rows.any():
            return ts[rows.argmax()] - 4
        return L

    def bus(self, start, d, k, pitch, width, first=(16, 40), segs=(2, 7), allow_out=False,
            vias=True, start_vias=False, skip=6, straight=0.45):
        r = self.r
        hw = (k - 1) / 2 * pitch + width / 2 + CLEAR
        room = (2 * VIA_R + 22 if k > 1 else VIA_R + 6) if vias else 0
        pts = [np.array(start, float)]
        cur, turned = d, 0
        lmin = max(14, k * pitch * 0.42)
        for s in range(r.integers(*segs)):
            L = r.uniform(*first) if s == 0 else r.uniform(40, 260)
            if s == 0:
                cand = [0]
            else:
                pref = [t for t in ((0,) if r.random() < straight else ()) + tuple(r.permutation([1, -1]))]
                cand = [t for t in pref + [0] if abs(turned + t) <= 2]
                cand = list(dict.fromkeys(cand))
            done = False
            for t in cand:
                nd = (cur + t) % 8
                got = self.free_len(pts[-1], DIRS[nd], L + room, hw, skip if s == 0 else 0, allow_out)
                got -= room
                if got >= lmin or (s == 0 and got >= 4):
                    pts.append(pts[-1] + DIRS[nd] * min(L, got))
                    cur, turned, done = nd, turned + t, True
                    break
            if not done:
                break
            e = pts[-1]
            if allow_out and not (0 <= e[0] < self.w and 0 <= e[1] < self.h):
                vias = False
                break
        if len(pts) < 2:
            return None
        ends = []
        for j in range(k):
            o = (j - (k - 1) / 2) * pitch
            line = offset(pts, o)
            self.trace(line, width)
            ends.append((line[0], line[-1]))
        if vias:
            dv = DIRS[cur]
            for j, (_, e) in enumerate(ends):
                c = e + dv * (VIA_R - 2 + (j % 2) * (2 * VIA_R + 4) * (k > 1 and pitch < 2 * VIA_R + 6))
                if (j % 2) and k > 1 and pitch < 2 * VIA_R + 6:
                    self.line("cu", [e, c], width)
                    self.line("keep", [e, c], width + 2 * POUR_CLEAR)
                self.via(*c)
        if start_vias:
            for j, (s0, _) in enumerate(ends):
                self.via(*s0)
        return pts


def offset(pts, o):
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0 or i == n - 1:
            a, b = (pts[0], pts[1]) if i == 0 else (pts[-2], pts[-1])
            d = (b - a) / np.hypot(*(b - a))
            out.append(pts[i] + np.array([-d[1], d[0]]) * o)
        else:
            d1 = (pts[i] - pts[i - 1]) / np.hypot(*(pts[i] - pts[i - 1]))
            d2 = (pts[i + 1] - pts[i]) / np.hypot(*(pts[i + 1] - pts[i]))
            n1, n2 = np.array([-d1[1], d1[0]]), np.array([-d2[1], d2[0]])
            m = n1 + n2
            m /= np.hypot(*m)
            out.append(pts[i] + m * (o / (m @ n1)))
    return out


# ── 2. footprints ─────────────────────────────────────────────────────────────
WORDS = ["DCPL RELAY BD", "NODE 4F", "SECTOR 9 LINK", "GRID CTRL", "DO NOT SERVICE", "HV", "MAINS",
         "DIMM CITY", "PWR", "SIG", "GND", "TX/RX", "REV C", "REV 3.1", "LOT 0x1E", "SW-BUS", "AUX",
         "!! 480V !!", "UPLINK", "ROUTER 12", "CTRL-B", "LUMEN 7", "NIGHTLINE", "CELL 22"]


def qfp(p, cx, cy, s, kind):
    r = p.r
    pitch, plen, pw = 14, 20, 7
    n = int((s - 24) // pitch)
    half = s / 2
    on = r.random() < 0.42
    p.mark_box(cx - half - plen - 4, cy - half - plen - 4, cx + half + plen + 4, cy + half + plen + 4)
    sides = []
    for side in range(4):
        d = DIRS[[0, 2, 4, 6][side]]
        t = np.array([-d[1], d[0]])
        pads = []
        for i in range(n):
            o = (i - (n - 1) / 2) * pitch
            c = np.array([cx, cy]) + d * (half + plen / 2 + 1) + t * o
            ext = d * plen / 2 + t * pw / 2
            x0, x1 = sorted((c[0] - ext[0], c[0] + ext[0]))
            y0, y1 = sorted((c[1] - ext[1], c[1] + ext[1]))
            p.pad_rect(x0, y0, x1, y1)
            if not on and r.random() < 0.55:
                p.disc("solder", *(c + d * r.uniform(-4, 4)), r.uniform(2.2, 3.6))
            pads.append(c)
        sides.append(([0, 2, 4, 6][side], pads))
    p.rect("silk", cx - half + 6, cy - half + 6, cx + half - 6, cy + half - 6, outline=2.5)
    p.disc("silk", cx - half - 10, cy - half - 10, 4)
    if on:
        p.rect("chip", cx - half + 2, cy - half + 2, cx + half - 2, cy + half - 2)
        for d_i, pads in sides:
            d = DIRS[d_i]
            for c in pads:
                a = c - d * (plen / 2 + 3)
                b = c + d * (plen / 2 - 5)
                p.line("lead", [a, b], 4)
        p.disc("chiptext", cx - half + 14, cy - half + 14, 4, fill=150)
        word = r.choice(["DC7", "LX", "MQ", "Z80", "R4", "NV"])
        p.text_chip(word + f"{r.integers(10, 99)}", cx - half + 18, cy - 8, max(10, s / 9))
    else:
        ep = s * 0.32                                       # the exposed pad, with its via grid
        p.pad_rect(cx - ep, cy - ep, cx + ep, cy + ep)
        g = max(2, int(ep * 2 // 22))
        for i in range(g):
            for j in range(g):
                p.disc("hole", cx - ep + (i + 0.5) * 2 * ep / g, cy - ep + (j + 0.5) * 2 * ep / g, 2.6)
        if r.random() < 0.5:
            p.disc("crust", cx + r.uniform(-ep, ep) / 2, cy + r.uniform(-ep, ep) / 2, ep * 0.8, fill=120)
    for d_i, pads in sides:
        route_row(p, pads, d_i, pitch, 5.5, plen / 2)
    p.text(f"U{r.integers(1, 60)}", cx - half - plen, cy - half - plen - 22, 13)


def route_row(p, pads, d_i, pitch, width, reach):
    """Escape a row of pads: one or two buses, the rest stubbed out to vias."""
    r = p.r
    d = DIRS[d_i]
    n = len(pads)
    i = 0
    while i < n:
        if r.random() < 0.62 and n - i >= 2:
            k = int(min(n - i, r.integers(2, max(3, n - i + 1))))
            group = pads[i:i + k]
            c = (group[0] + group[-1]) / 2 + d * reach
            p.bus(c, d_i, k, pitch, width, first=(14, 60), segs=(2, 6))
            i += k
        else:
            c = pads[i] + d * reach
            if r.random() < 0.7:
                L = 10 + (i % 2) * 18
                e = c + d * L
                if p.free_len(c, d, L + VIA_R + 4, VIA_R + 3, 4, False) >= L + VIA_R:
                    p.trace([c, e], width)
                    p.via(*(e + d * (VIA_R - 1)))
            i += 1


def Panel_text_chip(self, s, x, y, size):
    if size not in self.fonts:
        self.fonts[size] = ImageFont.truetype(str(FONT), round(size * SS))
    (px, py), = self.xy([(x, y)])
    self.drw["chiptext"].text((px, py), s, fill=150, font=self.fonts[size])


Panel.text_chip = Panel_text_chip


def soic(p, cx, cy, n, vertical):
    r = p.r
    pitch, plen, pw, bw = 18, 22, 9, 64
    on = r.random() < 0.5
    L = n * pitch
    if vertical:
        box = (cx - bw / 2 - plen, cy - L / 2 - 6, cx + bw / 2 + plen, cy + L / 2 + 6)
    else:
        box = (cx - L / 2 - 6, cy - bw / 2 - plen, cx + L / 2 + 6, cy + bw / 2 + plen)
    p.mark_box(*box)
    rows = []
    for side in (0, 1):
        d_i = (0 if side == 0 else 4) if vertical else (2 if side == 0 else 6)
        d = DIRS[d_i]
        t = np.array([-d[1], d[0]])
        pads = []
        for i in range(n):
            c = np.array([cx, cy]) + d * (bw / 2 + plen / 2 - 6) + t * (i - (n - 1) / 2) * pitch
            ext = d * plen / 2 + t * pw / 2
            x0, x1 = sorted((c[0] - ext[0], c[0] + ext[0]))
            y0, y1 = sorted((c[1] - ext[1], c[1] + ext[1]))
            p.pad_rect(x0, y0, x1, y1)
            if not on and r.random() < 0.5:
                p.disc("solder", *(c + d * r.uniform(-5, 5)), r.uniform(2.5, 4))
            pads.append(c)
        rows.append((d_i, pads))
    hx, hy = ((bw / 2 - 10, L / 2 + 2) if vertical else (L / 2 + 2, bw / 2 - 10))
    p.rect("silk", cx - hx, cy - hy, cx + hx, cy + hy, outline=2.5)
    if on:
        p.rect("chip", cx - hx + 3, cy - hy + 3, cx + hx - 3, cy + hy - 3)
        for d_i, pads in rows:
            d = DIRS[d_i]
            for c in pads:
                p.line("lead", [c - d * (plen / 2 - 2), c + d * (plen / 2 - 6)], 5)
        p.disc("chiptext", cx - hx + 12, cy - hy + 12, 3.5, fill=150)
    for d_i, pads in rows:
        route_row(p, pads, d_i, pitch, 6, plen / 2)
    p.text(f"U{r.integers(1, 60)}", box[0], box[1] - 20, 13)


def bga(p, cx, cy, g):
    r = p.r
    pitch = 20
    half = g * pitch / 2 + 8
    on = r.random() < 0.35
    p.mark_box(cx - half - 4, cy - half - 4, cx + half + 4, cy + half + 4)
    p.rect("silk", cx - half, cy - half, cx + half, cy + half, outline=2.5)
    p.poly("silk", [(cx - half - 12, cy - half), (cx - half, cy - half - 12), (cx - half, cy - half)])
    for i in range(g):
        for j in range(g):
            x, y = cx + (i - (g - 1) / 2) * pitch, cy + (j - (g - 1) / 2) * pitch
            p.pad_disc(x, y, 5)
            if 0 < i < g - 1 and 0 < j < g - 1 and i < g - 2 and j < g - 2:
                p.trace([(x, y), (x + pitch / 2, y + pitch / 2)], 3.5)       # dog-bone to a via
                p.disc("cu", x + pitch / 2, y + pitch / 2, 5)
                p.disc("hole", x + pitch / 2, y + pitch / 2, 2)
            if not on and r.random() < 0.45:
                p.disc("solder", x, y, 4.2)
    if on:
        p.rect("chip", cx - half + 2, cy - half + 2, cx + half - 2, cy + half - 2)
        p.text_chip(f"{r.choice(['DCX', 'MEM', 'NPU'])}-{r.integers(100, 999)}", cx - half + 12, cy - 8, max(10, g * 1.8))
    p.text(f"U{r.integers(1, 60)}", cx - half, cy - half - 24, 13)


def passive(p, x, y, vertical):
    r = p.r
    s, gap = 14, 12
    if vertical:
        pads = [(x, y - gap / 2 - s / 2), (x, y + gap / 2 + s / 2)]
        box = (x - s / 2 - 2, y - gap / 2 - s - 2, x + s / 2 + 2, y + gap / 2 + s + 2)
        dirs = [6, 2]
    else:
        pads = [(x - gap / 2 - s / 2, y), (x + gap / 2 + s / 2, y)]
        box = (x - gap / 2 - s - 2, y - s / 2 - 2, x + gap / 2 + s + 2, y + s / 2 + 2)
        dirs = [4, 0]
    if not p.free_box(*box):
        return False
    p.mark_box(*box, 3)
    for (px, py) in pads:
        p.pad_rect(px - s / 2, py - s / 2, px + s / 2, py + s / 2)
    p.rect("silk", box[0] - 3, box[1] - 3, box[2] + 3, box[3] + 3, outline=2)
    if r.random() < 0.55:
        bx, by = ((s / 2 + 1, gap / 2 + s - 2) if vertical else (gap / 2 + s - 2, s / 2 + 1))
        p.rect("chip", x - bx, y - by, x + bx, y + by, fill=int(r.choice([255, 140])))
        if vertical:
            p.rect("lead", x - bx, y - by, x + bx, y - by + 6)
            p.rect("lead", x - bx, y + by - 6, x + bx, y + by)
        else:
            p.rect("lead", x - bx, y - by, x - bx + 6, y + by)
            p.rect("lead", x + bx - 6, y - by, x + bx, y + by)
    for (px, py), d_i in zip(pads, dirs):
        if r.random() < 0.8:
            c = np.array([px, py]) + DIRS[d_i] * s / 2
            p.bus(c, d_i, 1, 0, 5, first=(8, 30), segs=(1, 4), skip=3)
    p.text(f"{r.choice(['R', 'C', 'L', 'D', 'Q'])}{r.integers(1, 120)}", box[2] + 4, box[1] - 2, 11)
    return True


def header(p, x, y, n, rows, vertical):
    r = p.r
    pitch = 24
    span = (n - 1) * pitch
    if vertical:
        box = (x - 14, y - 14, x + (rows - 1) * pitch + 14, y + span + 14)
    else:
        box = (x - 14, y - 14, x + span + 14, y + (rows - 1) * pitch + 14)
    if not p.free_box(*box):
        return False
    p.mark_box(*box, 4)
    on = r.random() < 0.3
    if on:
        p.rect("chip", *box, fill=200)
    p.rect("silk", box[0] - 3, box[1] - 3, box[2] + 3, box[3] + 3, outline=2.5)
    pins = []
    for i in range(n):
        for j in range(rows):
            px, py = (x + j * pitch, y + i * pitch) if vertical else (x + i * pitch, y + j * pitch)
            p.th(px, py, 9, 4.2, square=(i == 0 and j == 0))
            if on:
                p.rect("lead", px - 4, py - 4, px + 4, py + 4)
            pins.append((px, py))
    d_i = (0 if r.random() < 0.5 else 4) if vertical else (2 if r.random() < 0.5 else 6)
    if rows == 1:
        c = np.mean(pins, 0) + DIRS[d_i] * 12
        p.bus(c, d_i, n, pitch, 6, first=(10, 40), segs=(2, 6), skip=0)
    p.text(f"J{r.integers(1, 30)}", box[0], box[1] - 22, 13)
    return True


def cap(p, x, y, R):
    r = p.r
    box = (x - R - 4, y - R - 4, x + R + 4, y + R + 4)
    if not p.free_box(*box):
        return False
    p.mark_box(*box, 4)
    p.ring("silk", x, y, R + 2, 2.5)
    p.text("+", x - R - 14, y - R - 8, 14)
    p.th(x - R * 0.4, y, 7, 3.4, square=True)
    p.th(x + R * 0.4, y, 7, 3.4)
    if r.random() < 0.65:
        p.disc("cap", x, y, R)
        p.disc("capmetal", x, y, R - 5)
        for a in (0, 2.09, 4.19):                               # the scored vent
            p.line("cap", [(x, y), (x + math.cos(a) * (R - 8), y + math.sin(a) * (R - 8))], 2, fill=110)
        if r.random() < 0.55:                                   # it has burst: electrolyte crust round its foot
            for _ in range(5):
                a = r.uniform(0, 2 * math.pi)
                p.disc("crust", x + math.cos(a) * R * 0.9, y + math.sin(a) * R * 0.9 + 8, r.uniform(6, 14), fill=200)
    for (px, d_i) in ((x - R * 0.4, 4), (x + R * 0.4, 0)):
        if r.random() < 0.7:
            p.bus((px + DIRS[d_i][0] * (R * 0.6 + 4), y), d_i, 1, 0, 6, first=(6, 30), segs=(1, 4), skip=0)
    return True


def fingers(p):
    r = p.r
    n = int(r.integers(8, min(22, (p.w - 140) // 22)))
    pitch = 22
    x0 = r.uniform(70, p.w - 70 - n * pitch)
    top = r.random() < 0.3
    for i in range(n):
        x = x0 + i * pitch
        if top:
            p.rect("cu", x - 6, 0, x + 6, 46)
            p.rect("pad", x - 6, 0, x + 6, 46)
            p.rect("keep", x - 13, 0, x + 13, 53)
        else:
            p.rect("cu", x - 6, p.h - 46, x + 6, p.h)
            p.rect("pad", x - 6, p.h - 46, x + 6, p.h)
            p.rect("keep", x - 13, p.h - 53, x + 13, p.h)
    if top:
        p.mark_box(x0 - 10, 0, x0 + (n - 1) * pitch + 10, 50)
        p.bus((x0 + (n - 1) * pitch / 2, 46), 2, n, pitch, 6, first=(30, 90), segs=(2, 5), skip=6)
    else:
        p.mark_box(x0 - 10, p.h - 50, x0 + (n - 1) * pitch + 10, p.h)
        p.bus((x0 + (n - 1) * pitch / 2, p.h - 46), 6, n, pitch, 6, first=(30, 90), segs=(2, 5), skip=6)
    p.finger = True


def populate(p):
    r = p.r
    w, h = p.w, p.h
    # mounting holes: corners, and mid-edge on a long edge
    holes = [(22, 22), (w - 22, 22), (22, h - 22), (w - 22, h - 22)]
    if w > 700:
        holes += [(w / 2, 22), (w / 2, h - 22)]
    if h > 700:
        holes += [(22, h / 2), (w - 22, h / 2)]
    for (x, y) in holes:
        p.disc("cu", x, y, 16)
        p.disc("pad", x, y, 16)
        p.disc("keep", x, y, 22)
        p.disc("hole", x, y, 9)
        p.mark_box(x - 26, y - 26, x + 26, y + 26)
        p.screws.append((x, y))
    if w >= 520 and r.random() < 0.5:
        fingers(p)
    area = w * h
    big = int(area / 150000 + r.uniform(0, 1.5))
    for _ in range(big):
        for _try in range(40):
            kind = r.choice(["qfp", "qfp", "soic", "bga"])
            if kind == "qfp":
                s = float(r.choice([96, 124, 152]))
                ext = s / 2 + 40
            elif kind == "bga":
                g = int(r.integers(5, 9))
                ext = g * 10 + 30
            else:
                n = int(r.integers(4, 9))
                vert = r.random() < 0.5
                ext = max(n * 9 + 20, 70)
            if w - 2 * ext < 70 or h - 2 * ext < 80:
                continue
            cx, cy = r.uniform(ext + 30, w - ext - 30), r.uniform(ext + 40, h - ext - 30)
            if not p.free_box(cx - ext - 30, cy - ext - 40, cx + ext + 30, cy + ext + 30, 10):
                continue
            if kind == "qfp":
                qfp(p, cx, cy, s, kind)
            elif kind == "bga":
                bga(p, cx, cy, g)
            else:
                soic(p, cx, cy, n, vert)
            break
    for _ in range(int(area / 90000 * r.uniform(0.4, 1.2))):
        for _try in range(30):
            if cap(p, r.uniform(60, w - 60), r.uniform(60, h - 60), float(r.uniform(22, 34))):
                break
    for _ in range(int(r.integers(0, 3))):
        for _try in range(30):
            n, rows, vert = int(r.integers(3, 9)), int(r.choice([1, 1, 2])), r.random() < 0.5
            if header(p, r.uniform(40, w - 40), r.uniform(40, h - 40), n, rows, vert):
                break
    for _ in range(int(area / 12000 * r.uniform(0.5, 1.0))):
        for _try in range(12):
            if passive(p, r.uniform(40, w - 40), r.uniform(40, h - 40), r.random() < 0.5):
                break
    # free buses: across open board, some from off the panel's edge
    for _ in range(int(area / 1800)):
        k = int(r.choice([1, 1, 1, 2, 3, 4, 4, 6, 8]))
        pitch = float(r.choice([14, 16, 18]))
        width = float(r.choice([5, 6, 6, 8])) if k > 1 else float(r.choice([5, 6, 8, 12]))
        if r.random() < 0.18:
            side = int(r.integers(4))
            d_i = [2, 4, 6, 0][side]
            t = r.uniform(80, (w if side in (0, 2) else h) - 80)
            start = [(t, -4), (w + 4, t), (t, h + 4), (-4, t)][side]
            p.bus(np.array(start, float), d_i, k, pitch, width, first=(40, 160), segs=(1, 5), skip=16)
        else:
            x, y = r.uniform(20, w - 20), r.uniform(20, h - 20)
            if p.occ[int(y), int(x)]:
                continue
            d_i = int(r.choice([0, 2, 4, 6, 0, 2, 4, 6, 1, 3, 5, 7]))
            p.bus(np.array([x, y]), d_i, k, pitch, width, first=(30, 200), segs=(1, 6), skip=0,
                  start_vias=True)
    # a ground pour over what is left, kept clear of every other copper; some hatched
    if r.random() < 0.55:
        pour = Image.new("L", p.img["cu"].size, 0)
        (a, b), (c, d) = p.xy([(12, 12), (w - 12, h - 12)])
        ImageDraw.Draw(pour).rectangle((a, b, c, d), fill=255)
        pour = ImageChops.subtract(pour, p.img["keep"])
        if r.random() < 0.35:
            Y, X = np.mgrid[0:pour.height, 0:pour.width]
            q = 14 * SS
            grid = ((((X + Y) % q) < 3 * SS) | (((X - Y) % q) < 3 * SS)).astype(np.uint8) * 255
            pour = ImageChops.multiply(pour, Image.fromarray(grid))
        p.img["cu"] = ImageChops.lighter(p.img["cu"], pour)
        p.drw["cu"] = ImageDraw.Draw(p.img["cu"])
    # labels
    for _ in range(int(r.integers(1, 4))):
        for _try in range(20):
            size = float(r.choice([16, 20, 24]))
            if p.text(str(r.choice(WORDS)), r.uniform(30, w - 200), r.uniform(30, h - 40), size,
                      vertical=r.random() < 0.25):
                break


# ── 3. the damage ─────────────────────────────────────────────────────────────
def crack(p, start, heading, length, width=2.0, depth=0):
    r = p.r
    pts = [np.array(start, float)]
    a = heading
    for _ in range(int(length / 9)):
        a += r.normal(0, 0.07) + 0.15 * (heading - a)
        z = a + r.choice([-1, 1]) * r.uniform(0.05, 0.35)            # a fracture zigzags, a little
        pts.append(pts[-1] + 9 * np.array([math.cos(z), math.sin(z)]))
        x, y = pts[-1]
        if not (-5 < x < p.w + 5 and -5 < y < p.h + 5):
            break
        if depth < 2 and r.random() < 0.03:
            crack(p, pts[-1], a + r.choice([-1, 1]) * r.uniform(0.5, 1.0), length * r.uniform(0.2, 0.5),
                  width * 0.7, depth + 1)
    p.line("fringe", pts, width + 6, fill=150)                      # stress-whitened glass along it
    p.line("crack", pts, width)
    p.cracks.append(pts)


def damage(p, age):
    r = p.r
    w, h = p.w, p.h
    corners = [(0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)]
    ncut = r.choice([0, 1, 1, 1, 2], p=None) if age > -0.05 else r.choice([0, 0, 1])
    for ci in r.permutation(4)[:ncut]:
        x0, y0, sx, sy = corners[ci]
        a, b = r.uniform(70, min(260, w * 0.55)), r.uniform(70, min(260, h * 0.55))
        A = (x0 + sx * a, y0)
        B = (x0, y0 + sy * b)
        path = jag(A, B, 0.10, r)
        far = (x0 - sx * M, y0 - sy * M)
        p.poly("board", path + [(B[0] - sx * M, B[1]), far, (A[0], A[1] - sy * M)], fill=0)
        p.line("fringe", path, 7)
        p.fractures.append((path, np.array([-sx, -sy]) / R2 / 2))
        for _ in range(int(r.integers(1, 3))):                         # cracks running on from the break
            q = path[int(r.integers(len(path) // 4, 3 * len(path) // 4))]
            crack(p, q, math.atan2(sy, sx) + r.normal(0, 0.5), r.uniform(80, 300))
    for _ in range(int(r.integers(2, 7))):                             # chips out of the edges
        side = int(r.integers(4))
        t = r.uniform(40, (w if side in (0, 2) else h) - 40)
        e = [(t, 0), (w, t), (t, h), (0, t)][side]
        rad = r.uniform(5, 18)
        ang = np.linspace(0, 2 * math.pi, 14, endpoint=False)
        bite = [(e[0] + math.cos(q) * rad * r.uniform(0.6, 1.3), e[1] + math.sin(q) * rad * r.uniform(0.6, 1.3)) for q in ang]
        p.poly("board", bite, fill=0)
        p.line("fringe", bite + bite[:1], 5)
    for _ in range(int(r.choice([0, 1, 1, 2, 3]))):                    # cracks from an edge
        side = int(r.integers(4))
        t = r.uniform(60, (w if side in (0, 2) else h) - 60)
        e = [(t, 0), (w, t), (t, h), (0, t)][side]
        crack(p, e, [math.pi / 2, math.pi, -math.pi / 2, 0][side] + r.normal(0, 0.4), r.uniform(100, 420))
    if r.random() < 0.3:                                               # an impact hole, cracks radiating
        cx, cy = r.uniform(80, w - 80), r.uniform(80, h - 80)
        R = r.uniform(14, 30)
        ang = np.sort(r.uniform(0, 2 * math.pi, 11))
        hole = [(cx + math.cos(q) * R * r.uniform(0.6, 1.25), cy + math.sin(q) * R * r.uniform(0.6, 1.25)) for q in ang]
        p.poly("board", hole, fill=0)
        p.line("fringe", hole + hole[:1], 9)
        p.fractures.append((hole + hole[:1], None))
        for q in r.uniform(0, 2 * math.pi, int(r.integers(3, 6))):
            crack(p, (cx + math.cos(q) * R, cy + math.sin(q) * R), q, r.uniform(40, 160), 2)
    if r.random() < 0.38:                                              # a burn, soot climbing over it
        cx, cy = r.uniform(70, w - 70), r.uniform(90, h - 60)
        R = r.uniform(40, 95)
        p.burn_at = (cx, cy, R)
    for _ in range(int(r.integers(2, 12))):                             # scratches through the mask
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = r.uniform(0, math.pi)
        Ls = r.uniform(20, 140)
        p.line("scratch", [(x, y), (x + math.cos(a) * Ls, y + math.sin(a) * Ls)], r.uniform(1.2, 3))
    for _ in range(int(r.integers(0, 5))):                              # blisters (delamination)
        cx, cy = r.uniform(30, w - 30), r.uniform(30, h - 30)
        rw, rh = r.uniform(8, 40), r.uniform(6, 28)
        (a0, b0), (a1, b1) = p.xy([(cx - rw, cy - rh), (cx + rw, cy + rh)])
        p.drw["delam"].ellipse((a0, b0, a1, b1), fill=int(r.uniform(140, 255)))
    # bodge wires: muted insulation, sagging between two points; some broken and hanging
    for _ in range(int(r.choice([0, 0, 0, 1, 1, 2]))):
        col = tuple(int(c) for c in r.choice([(143, 82, 72), (160, 148, 92), (96, 118, 134), (112, 120, 96), (150, 140, 130)]))
        a = np.array([r.uniform(40, w - 40), r.uniform(40, h - 40)])
        if r.random() < 0.6:
            b = np.array([r.uniform(40, w - 40), r.uniform(40, h - 40)])
            sag = r.uniform(20, 70)
            pts = [a + (b - a) * t + np.array([0, sag * 4 * t * (1 - t)]) for t in np.linspace(0, 1, 40)]
        else:
            L = r.uniform(80, 200)
            d = r.uniform(-1.2, 1.2)
            pts, q, v = [a], a.copy(), np.array([math.sin(d), -math.cos(d) * 0.3])
            for _ in range(int(L / 4)):
                v = v + np.array([0, 0.09])
                v /= np.hypot(*v)
                q = q + 4 * v
                pts.append(q.copy())
        p.line("wire", pts, 5.5)
        p.wdrw.line(p.xy(pts), fill=col, width=int(5.5 * SS), joint="curve")
        p.disc("solder", *a, 5)
    if not hasattr(p, "burn_at"):
        p.burn_at = None


def shards(p):
    """All of a board broken away but a shard at some of its screws."""
    r = p.r
    w, h = p.w, p.h
    p.img["board"] = Image.new("L", p.img["board"].size, 0)
    p.drw["board"] = ImageDraw.Draw(p.img["board"])
    p.burn_at = None
    for (x0, y0, sx, sy) in ((0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)):
        if r.random() < 0.3:
            continue
        a, b = r.uniform(60, 210), r.uniform(60, 210)
        A, B = (x0 + sx * a, y0), (x0, y0 + sy * b)
        path = jag(A, B, 0.12, r)
        p.poly("board", [(x0, y0)] + path)
        p.line("fringe", path, 7)
        p.fractures.append((path, np.array([sx, sy]) * R2))


def dangles(p, cu):
    """Copper traces that crossed a break, left hanging off it."""
    r = p.r
    for path, out in p.fractures:
        pts = np.array(path)
        seg = np.hypot(*np.diff(pts, axis=0).T)
        samp = []
        for (a, b), L in zip(zip(pts, pts[1:]), seg):
            for t in np.linspace(0, 1, max(2, int(L)), endpoint=False):
                samp.append(a + (b - a) * t)
        samp = np.array(samp)
        xi, yi = np.rint(samp[:, 0] + M).astype(int), np.rint(samp[:, 1] + M).astype(int)
        ok = (xi >= 0) & (xi < p.W) & (yi >= 0) & (yi < p.H)
        on = np.zeros(len(samp), bool)
        on[ok] = cu[yi[ok], xi[ok]] > 0.5
        runs, i = [], 0
        while i < len(on):
            if on[i]:
                j = i
                while j < len(on) and on[j]:
                    j += 1
                runs.append((i, j))
                i = j
            else:
                i += 1
        for (i, j) in runs:
            if r.random() > 0.35 or j - i < 3:
                continue
            q = samp[(i + j) // 2].copy()
            width = min(7, (j - i) * 0.8)
            v = out if out is not None else np.array([0.0, 1.0])
            v = v / np.hypot(*v) + r.normal(0, 0.3, 2)
            v /= np.hypot(*v)
            L = r.uniform(15, 130)
            stiff = r.uniform(0.04, 0.14)
            phase = r.uniform(0, 6)
            prev = q.copy()
            for s in range(int(L / 3)):
                v = v + np.array([0, stiff])
                v /= np.hypot(*v)
                q = q + 3 * v
                wv = width * (0.45 + 0.55 * abs(math.cos(phase + s * 0.08)))   # a twisting strip narrows
                p.line("dangle", [prev, q], wv)
                prev = q.copy()


# ── panel colours ─────────────────────────────────────────────────────────────
MASKS = [("#5f7d66", 3), ("#58786f", 2), ("#6c7d5a", 1.2), ("#5c6e78", 0.9), ("#66806a", 2), ("#55716a", 1.5)]
mask_w = np.array([m[1] for m in MASKS])
SUB = hexc("#b3a682")         # bare FR-4 glass-epoxy
SUB_PALE = hexc("#cdc6ae")    # measled / blistered, fibres showing
COPPER = hexc("#b07e58")
TARNISH = hexc("#7a5238")
DARK_TARN = hexc("#5a4434")
VERDIGRIS = hexc("#79a294")
TIN = hexc("#a6a69e")
GOLD = hexc("#a59670")
SOLDER = hexc("#c4c4bc")
SILK = hexc("#cfcbbb")
CHIP = hexc("#585a56")
CHIP_TEXT = hexc("#8a8c86")
CHAR = hexc("#4a3e33")
CRACK = hexc("#4b4a42")
FIBRE = hexc("#d2ccb6")
CAP_SLEEVE = hexc("#5d6a78")
CAP_TOP = hexc("#a9aaa4")
CRUST = hexc("#9a8460")
HOLE = hexc("#3d3b37")


def compose(p, gx, gy, age):
    """The panel's colour and coverage on its canvas (1x)."""
    r = p.r
    L = {k: np.asarray(v.resize((p.W, p.H), Image.BOX), float) / 255 for k, v in p.img.items()}
    wcol = np.asarray(p.wcol.resize((p.W, p.H), Image.BOX), float) / 255
    rows = (gy - M + np.arange(p.H)) % N
    cols = (gx - M + np.arange(p.W)) % N
    G = lambda f: f[np.ix_(rows, cols)]
    mot, fin, pn, tn, vd, wv, sp = G(mottle), G(fine), G(peeln), G(tarn), G(verd), G(weave), G(speck)
    board = L["board"]
    cu = np.clip(L["cu"], 0, 1)

    # where the board is weakest: near its edges, its cracks and its burn
    edgew = r.uniform(0.2, 0.6)                                  # how far in from its edges the mask lifts
    bimg = Image.fromarray((board * 255).astype(np.uint8))
    edge = 1 - np.asarray(bimg.filter(ImageFilter.GaussianBlur(26)), float) / 255
    crimg = Image.fromarray((np.clip(L["crack"] + L["fringe"] * 0.5, 0, 1) * 255).astype(np.uint8))
    near_crack = np.asarray(crimg.filter(ImageFilter.GaussianBlur(18)), float) / 255
    near_crack = np.clip(near_crack * 3, 0, 1)
    burn = np.zeros((p.H, p.W))
    if p.burn_at:                                                # hottest at its heart, soot climbing above it
        bx, by, R = p.burn_at
        Y, X = np.mgrid[0:p.H, 0:p.W] - M
        dx, dy = X - bx, Y - by
        dy = np.where(dy < 0, dy / 2.4, dy * 1.2)
        d = np.hypot(dx * (1 + 0.5 * np.abs(dy) / (R * 3)), dy) / R * (0.7 + 0.6 * pn)
        burn = np.exp(-1.8 * d * d) * (0.75 + 0.5 * fin)
    burn_core = smooth(burn, 0.62, 0.92)
    if p.burn_at and r.random() < 0.45:                          # burnt right through
        board = board * (1 - smooth(burn, 0.86, 0.9))
    peel_field = 0.60 * pn + 0.22 * fin + edgew * edge + 0.45 * near_crack + 0.15 * burn + age
    peeled = smooth(peel_field, 0.57, 0.60)
    fl = G(flake)
    peeled = np.maximum(peeled, smooth(0.45 * pn + 0.55 * fl + 0.5 * age, 0.66, 0.68))     # flakes round a peel
    peeled = np.maximum(peeled, np.clip(L["scratch"], 0, 1))                               # scratched through
    pad = np.clip(L["pad"], 0, 1)
    maskp = board * (1 - pad) * (1 - peeled)

    # bare glass-epoxy, its cloth showing faintly; measling and blisters paler
    delam = np.clip(L["delam"] * (0.5 + 0.5 * fin) + smooth(sp, 0.82, 0.92) * 0.5, 0, 1)
    sub = SUB * (0.92 + 0.12 * mot + 0.05 * wv)[..., None]
    sub = mix(sub, SUB_PALE, delam * 0.8)
    # bare copper: tarnished brown, darker where thickest, verdigris in patches
    cop = mix(COPPER, TARNISH, smooth(tn, 0.35, 0.6))
    cop = mix(cop, DARK_TARN, smooth(tn, 0.65, 0.85))
    green = smooth(vd, 0.58, 0.68)
    cop = mix(cop, VERDIGRIS, green * 0.9)
    # the mask: its colour over glass and over copper (copper under it reads lighter, yellower)
    mcol = hexc(MASKS[int(r.choice(len(MASKS), p=mask_w / mask_w.sum()))][0])
    mcol = mix(mcol, np.full(3, mcol.mean()), 0.25) * r.uniform(0.95, 1.05)   # aged: the gloss and the colour gone off it
    m_sub = mcol * (0.94 + 0.10 * mot + 0.03 * wv)[..., None]
    m_cu = mix(mcol * 1.16 + np.array([0.03, 0.03, -0.02]), sub, 0.10) * (0.96 + 0.08 * mot)[..., None]
    masked = mix(m_sub, m_cu, cu)
    masked = mix(masked, SUB_PALE * 0.9 + mcol * 0.1, delam * 0.45)
    bare = mix(sub, cop, cu)
    col = mix(bare, masked, np.clip(maskp / np.maximum(board, 1e-6), 0, 1))

    # the peel's edge: the mask lifts (a lit lip) and throws a little shadow on the bare board
    lip = np.clip(np.roll(peeled, (2, 2), (0, 1)) - peeled, 0, 1) * (1 - pad)
    shade = np.clip(peeled - np.roll(peeled, (3, 3), (0, 1)), 0, 1)
    col = mix(col, col * 1.22 + 0.05, lip * 0.8)
    col *= (1 - 0.30 * shade)[..., None]

    # pads: tin or gold, dulled and spotted
    fin_c = GOLD if r.random() < 0.35 else TIN
    padc = fin_c * (0.88 + 0.16 * fin)[..., None]
    padc = mix(padc, TARNISH * 1.1, smooth(tn, 0.55, 0.8) * 0.6)
    padc = mix(padc, VERDIGRIS, green * 0.5)
    col = mix(col, padc, pad * board)
    col = mix(col, SOLDER * (0.9 + 0.2 * fin)[..., None], np.clip(L["solder"], 0, 1) * board)
    crust = np.clip(L["crust"], 0, 1)
    col = mix(col, CRUST * (0.85 + 0.3 * fin)[..., None], crust * smooth(fin + crust, 0.6, 0.9) * board)

    # silkscreen rides on the mask: it goes where the mask went, and it is worn
    wear = smooth(fin * 0.6 + mot * 0.4, 0.28, 0.5)
    col = mix(col, SILK, L["silk"] * np.clip(maskp, 0, 1) * wear * 0.6)

    # parts still on: chips (a lit edge, a pin-1 dimple, faint marking), passives, header plastic, caps
    chip = L["chip"]
    cimg = Image.fromarray((np.clip(chip, 0, 1) * 255).astype(np.uint8))
    clit = np.clip(chip - np.roll(chip, (3, 3), (0, 1)), 0, 1)
    col = mix(col, CHIP * (0.9 + 0.2 * mot)[..., None], np.clip(chip, 0, 1))
    col = mix(col, CHIP * 1.5, clit * 0.6)
    col = mix(col, CHIP_TEXT, L["chiptext"] * chip)
    col = mix(col, padc * 1.05, L["lead"])
    cap_a = L["cap"]
    col = mix(col, CAP_SLEEVE * (0.85 + 0.25 * mot)[..., None], np.clip(cap_a, 0, 1))
    col = mix(col, CAP_TOP * (0.9 + 0.15 * fin)[..., None], L["capmetal"] * np.clip(cap_a * 2 - 1, 0, 1))

    # the burn: scorched brown, a char core, soot
    col = mix(col, col * np.array([0.66, 0.58, 0.50]), smooth(burn, 0.08, 0.55))
    col = mix(col, CHAR * (0.9 + 0.3 * fin)[..., None], burn_core * 0.85)

    # holes, cracks and the glass fibre at a break
    hole = np.clip(L["hole"], 0, 1) * board
    col = mix(col, HOLE, hole)
    col = mix(col, FIBRE * (0.9 + 0.15 * fin)[..., None], np.clip(L["fringe"] - L["crack"], 0, 1) * 0.65)
    col = mix(col, CRACK, np.clip(L["crack"], 0, 1) * 0.9)

    # the board's edge: lit along the top and left, in shade along the bottom and right
    hl = np.clip(board - np.roll(board, (3, 3), (0, 1)), 0, 1)
    dk = np.clip(board - np.roll(board, (-3, -3), (0, 1)), 0, 1)
    col = mix(col, FIBRE, hl * 0.55)
    col *= (1 - 0.35 * dk)[..., None]

    # water stains: a tide mark round each, browner inside
    st = G(stain)
    tide = smooth(st, 0.66, 0.675) - smooth(st, 0.68, 0.70)
    col = mix(col, col * np.array([0.86, 0.80, 0.70]), np.clip(smooth(st, 0.66, 0.70) * 0.35 + tide * 0.6, 0, 1))
    # grime: heavier toward the foot, panel by panel
    fy = np.clip((np.arange(p.H) - M) / p.h, 0, 1)[:, None]
    col *= (1 - 0.10 * smooth(fy, 0.5, 1.0) - 0.10 * smooth(G(grime), 0.5, 0.85) - 0.04 * age)[..., None]

    alpha = np.clip(board, 0, 1)

    # dangling traces and wires, over the board and the wall
    dg = np.clip(L["dangle"], 0, 1)
    dcol = mix(COPPER, DARK_TARN, smooth(tn, 0.3, 0.75)) * (0.85 + 0.35 * fin)[..., None]
    col = mix(col, dcol, dg)
    wire = np.clip(L["wire"], 0, 1)
    wlit = np.clip(wire - np.roll(wire, (2, 0), (0, 1)), 0, 1)
    wc = wcol / np.maximum(wire, 1e-3)[..., None]
    col = mix(col, wc * (1 + 0.25 * wlit)[..., None], wire)
    over = np.maximum(dg, wire)
    alpha = np.maximum(alpha, over)

    # screws: a slotted pan head in each mounting hole, a few missing
    for (x, y) in p.screws:
        if r.random() < 0.1:
            continue
        cx, cy = x + M, y + M
        R = 12
        sy, sx = np.mgrid[int(cy) - R - 6:int(cy) + R + 7, int(cx) - R - 6:int(cx) + R + 7]
        dy, dx = sy - cy, sx - cx
        d = np.hypot(dx, dy)
        head = d <= R
        washer = (d <= R + 4) & ~head
        sh = (np.hypot(dx - 3, dy - 3) <= R + 4) & ~head & ~washer
        light = np.clip(1.12 - ((dx + 4) ** 2 + (dy + 4) ** 2) / (R * R * 2.4), 0.55, 1.12)
        rusty = r.random() < 0.35
        steel = (np.array([0.66, 0.64, 0.6]) if not rusty else np.array([0.58, 0.44, 0.33]))
        ang = r.uniform(0, math.pi)
        slot = (np.abs(dx * math.sin(ang) - dy * math.cos(ang)) < 2.0) | (np.abs(dx * math.cos(ang) + dy * math.sin(ang)) < 2.0)
        slot &= d < R - 2
        col[sy[sh], sx[sh]] *= 0.6
        col[sy[washer], sx[washer]] = np.array([0.6, 0.6, 0.57]) * (0.9 + 0.1 * light[washer])[:, None]
        col[sy[head], sx[head]] = steel * light[head][:, None]
        col[sy[slot], sx[slot]] = steel * 0.45
        a = alpha[sy, sx]
        alpha[sy, sx] = np.maximum(a, (d <= R + 4).astype(float))
    return col, alpha, over


# ── lay the panels ────────────────────────────────────────────────────────────
P_rgb = np.zeros((N, N, 3))         # premultiplied
P_a = np.zeros((N, N))
D_a = np.zeros((N, N))              # dangles and wires: they shade what is under them
gone = int(rng.integers(len(cells)))
drips = np.zeros((N, N))
for i, (cx, cy, cw, ch) in enumerate(cells):
    jx, jy = rng.integers(-4, 5, 2)
    w, h = cw * MOD - GAP, ch * MOD - GAP
    gx, gy = cx * MOD + GAP // 2 + int(jx), cy * MOD + GAP // 2 + int(jy)
    age = float(rng.uniform(-0.14, 0.10))
    p = Panel(w, h, SEED * 100 + i)
    populate(p)
    if i == gone:
        # the bay whose panel has gone: a cleaner ghost of it on the wall, and
        # shards of the board still held by their screws
        rows, cols = (gy + np.arange(h)) % N, (gx + np.arange(w)) % N
        wall[np.ix_(rows, cols)] *= 1.07
        for b in range(10):
            f = 0.93 + 0.007 * b
            wall[np.ix_(rows[[b, -1 - b]], cols)] *= f
            wall[np.ix_(rows, cols[[b, -1 - b]])] *= f
        shards(p)
    else:
        damage(p, age)
    cu_pre = np.asarray(p.img["cu"].resize((p.W, p.H), Image.BOX), float) / 255
    dangles(p, cu_pre)
    col, alpha, over = compose(p, gx, gy, age)
    for (x, y) in p.screws:
        if rng.random() < 0.3:
            drips[int(gy + y + 13) % N, int(gx + x) % N] += rng.uniform(0.4, 1.0)
    rows = (gy - M + np.arange(p.H)) % N
    cols = (gx - M + np.arange(p.W)) % N
    ix = np.ix_(rows, cols)
    P_rgb[ix] = col * alpha[..., None] + P_rgb[ix] * (1 - alpha[..., None])
    P_a[ix] = alpha + P_a[ix] * (1 - alpha)
    D_a[ix] = np.maximum(D_a[ix], over)
    print(f"  panel {i + 1}/{len(cells)}  {cw}x{ch}", flush=True)

# ── 4. shadows and drips ──────────────────────────────────────────────────────
shadow = np.clip(circ_conv(P_a, gauss_kernel(5.0, 6, 8)), 0, 1)
wall *= (1 - 0.55 * shadow)[..., None]
img = P_rgb + wall * (1 - P_a)[..., None]
dsh = np.clip(circ_conv(D_a, gauss_kernel(2.5, 4, 5)), 0, 1)
img *= (1 - 0.45 * dsh * (1 - D_a))[..., None]


def drip(length, width):
    return np.where(ky >= 0, np.exp(-ky / length), 0) * np.exp(-(kx / width) ** 2)


streaks = circ_conv(drips, drip(90.0, 2.5))
streaks = np.clip(streaks / np.percentile(streaks[streaks > 1e-4], 99), 0, 1)
streaks *= smooth(streakn, 0.2, 0.7)
img = mix(img, img * np.array([0.78, 0.62, 0.48]), streaks * 0.7)

# ── 5. grime over everything ──────────────────────────────────────────────────
img *= (1 - 0.08 * smooth(grime, 0.45, 0.9) - 0.06 * (fine - 0.5))[..., None]

out = Image.fromarray((np.clip(img * SHADE, 0, 1) * 255).astype(np.uint8), "RGB")
out = out.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
out.save(ROOT / "images/wall-8.png", optimize=True)
avg = out.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
print(f"images/wall-8.png  {SIZE}x{SIZE}  {SIZE / 240:.2f}in  {len(cells)} panels  average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}")
