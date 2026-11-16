"""Creature damage: the pass that makes Creaturepunk look gnawed on.

Runs on the letterforms from scrawl.py (which stay as they are) and adds
sloppy hand-lettering, claw slashes, bite marks and drips. Every glyph draws
from its own random stream, seeded by its name, so the result is the same on
every run and changing one glyph's damage leaves the others alone.

Units are the design grid's: cap height 44, baseline 0, slant removed (the
slant goes back on at build, so the marks lean with the letters).
"""
import zlib
from scrawl import *


def grng(name, salt):
    return np.random.default_rng(zlib.crc32(f'{name}:{salt}'.encode()))


def ink_points(m):
    ys, xs = np.nonzero(m)
    return X0 + (xs + 0.5) / S, Y1 - (ys + 0.5) / S


def disc(cx, cy, r):
    return (XX - cx) ** 2 + (YY - cy) ** 2 <= r * r


def slit(p0, p1, w, r, bend):
    """A tapered tear from p0 to p1: widest in the middle, sharp at both ends."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    n = np.array([-d[1], d[0]]) / np.hypot(*d)
    left, right, steps = [], [], 28
    for i in range(steps + 1):
        s = i / steps
        c = p0 + d * s + n * bend * 4 * s * (1 - s)
        half = w / 2 * np.sin(np.pi * s) ** 0.6 * (1 + r.normal(0, 0.15))
        left.append(tuple(c + n * half))
        right.append(tuple(c - n * half))
    return P(left + right[::-1], rough=0, soft=0.12)


def claw(m, name, cx, cy, angle=-38, length=30, n=3, gap=5.6, w=3.4):
    """n parallel slashes, the middle claw longest, raked through the glyph."""
    r = grng(name, 'claw')
    a = np.radians(angle + r.normal(0, 4))
    t = np.array([np.cos(a), np.sin(a)])
    nrm = np.array([-t[1], t[0]])
    bend = r.normal(0, 1.2)
    for k in range(n):
        off = (k - (n - 1) / 2) * gap * (1 + r.normal(0, 0.08))
        mid = 1 - abs(k - (n - 1) / 2) / n * 0.6
        L = length * mid * (1 + r.normal(0, 0.07))
        c = np.array([cx, cy]) + nrm * off + t * r.normal(0, 1.5)
        m = m & ~slit(c - t * L / 2, c + t * L / 2, w * (0.85 + 0.3 * r.random()), r, bend)
    return m


def bite(m, name, toward=(1, 1), R=8.0, depth=0.45):
    """A jaw-shaped chunk out of the edge the glyph shows toward `toward`:
    a scalloped arc of teeth, plus two fang punctures past the bite."""
    r = grng(name, 'bite')
    xs, ys = ink_points(m)
    d = np.array(toward, float) / np.hypot(*toward)
    i = np.argmax(xs * d[0] + ys * d[1])
    cx, cy = xs[i] + d[0] * R * depth, ys[i] + d[1] * R * depth
    pts, teeth = [], 11
    for k in range(teeth * 4):
        th = 2 * np.pi * k / (teeth * 4)
        rad = R * (1 + r.normal(0, 0.04))
        if k % 4 == 2:
            rad += 2.2 + r.random() * 1.0     # a tooth punching past the bite's rim
        pts.append((cx + rad * np.cos(th), cy + rad * np.sin(th)))
    m = m & ~P(pts, rough=0, soft=0.1)
    inward = np.arctan2(-d[1], -d[0])
    for side in (-1, 1):
        th = inward + side * np.radians(32 + r.normal(0, 5))
        fx, fy = cx + (R + 4.2) * np.cos(th), cy + (R + 4.2) * np.sin(th)
        m = m & ~disc(fx, fy, 1.5 + r.random() * 0.4)
    return m


def drip(m, name, x=None, length=7.0):
    """A drip running off the lowest edge near x (or a random spot)."""
    r = grng(name, 'drip')
    xs, ys = ink_points(m)
    low = ys < ys.min() + 3
    if x is None:
        x = np.quantile(xs[low], 0.25 + 0.5 * r.random())
    col = np.abs(xs - x) < 0.6
    y = ys[col].min() + 0.6 if col.any() else ys.min() + 0.6
    w = 3.4 + r.random() * 0.8
    L = length * (0.9 + 0.5 * r.random())
    body = P([(x - w / 2, y + 1.5), (x + w / 2, y + 1.5), (x + 0.5, y - L), (x - 0.4, y - L)], rough=0.2, soft=0.3)
    return m | body | disc(x + 0.05, y - L, w * 0.42)


def gnaw(m, name, density=1.0):
    """Chewed edges: small nicks taken out all along the outline."""
    r = grng(name, 'gnaw')
    edge = m & ~nd.binary_erosion(m, iterations=3)
    ys, xs = np.nonzero(edge)
    if not len(xs):
        return m
    k = int(len(xs) / S / 34 * density)
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    for j in r.choice(len(xs), size=k, replace=False):
        rad = (0.7 + r.random() ** 2 * 1.4) * S
        dr.ellipse([xs[j] - rad, ys[j] - rad, xs[j] + rad, ys[j] + rad], fill=255)
    return m & ~(np.asarray(im) > 0)


def wobble(m, name, tilt=2.2, lift=1.1):
    """Sloppy hand: each glyph sits a little off-square and off the baseline."""
    r = grng(name, 'wobble')
    a = np.radians(r.uniform(-tilt, tilt))
    dy = r.uniform(-lift, lift)
    xs, _ = ink_points(m)
    cx, cy = (xs.min() + xs.max()) / 2, CAP / 2
    # output (row, col) -> input (row, col): rotate about (cx, cy) in y-up units, then lift
    pc, pr = (cx - X0) * S, (Y1 - cy) * S
    ca, sa = np.cos(a), np.sin(a)
    mat = np.array([[ca, sa], [-sa, ca]])
    off = np.array([pr, pc]) - mat @ np.array([pr + dy * S, pc])
    return nd.affine_transform(m.astype(np.float32), mat, offset=off, order=1) > 0.5


def cx_of(m):
    xs, _ = ink_points(m)
    return (xs.min() + xs.max()) / 2


# What each glyph gets, beyond the sloppy hand and chewed edges every glyph has.
# claw: (dx from centre, y, angle, length[, n]); bite: direction it bites from.
FERAL = {
    'A': dict(claw=(1, 9, -34, 40)),
    'B': dict(bite=(1, 0.6)),
    'C': dict(bite=(1, 1)),
    'E': dict(drip=True),
    'F': dict(drip=True),
    'G': dict(bite=(1, -0.6)),
    'D': dict(claw=(-4, 16, -34, 32)),
    'H': dict(drip=True),
    'K': dict(claw=(-8, 12, -34, 30)),
    'L': dict(drip=True),
    'M': dict(bite=(1, 1)),
    'R': dict(claw=(-3, 9, -34, 34)),
    'S': dict(bite=(-1, -0.4)),
    'T': dict(drip=True),
    'U': dict(bite=(-1, 1.2)),
    'W': dict(drip=True),
    'Y': dict(drip=True),
    'Z': dict(bite=(1, 1)),
    'three': dict(bite=(-1, 0)),
    'four': dict(drip=True),
    'five': dict(claw=(0, 11, -34, 34)),
    'six': dict(bite=(1, 1)),
    'eight': dict(claw=(0, 22, -34, 30)),
    'nine': dict(bite=(-1, -1)),
}
SMALL = {'period', 'comma', 'colon', 'semicolon', 'quotesingle', 'quotedbl', 'hyphen', 'ellipsis', 'asterisk'}

for name in list(G):
    m = G[name]
    if not m.any():
        continue
    spec = FERAL.get(name, {})
    if 'claw' in spec:
        dx, y, ang, L, *n = spec['claw']
        m = claw(m, name, cx_of(m) + dx, y, ang, L, n[0] if n else 3)
    if 'bite' in spec:
        m = bite(m, name, spec['bite'])
    if spec.get('drip'):
        m = drip(m, name)
    m = gnaw(m, name, 0.5 if name in SMALL else 1.0)
    if name not in SMALL:
        m = wobble(m, name)
    # drop specks a bite or a claw left floating (the dots of : ; … are bigger)
    lab, k = nd.label(m)
    if k > 1:
        sizes = nd.sum(m, lab, range(1, k + 1))
        m = np.isin(lab, 1 + np.nonzero(sizes >= 12 * S * S)[0])
    G[name] = m
