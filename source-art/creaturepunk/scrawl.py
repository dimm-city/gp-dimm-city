"""Creaturepunk letterforms: a feral brush scrawl.

Every glyph is drawn here as brush strokes. A stroke is a centre line with a pressure that
wanders, a sloppy hand (its points jitter and its blunt ends overshoot the
join) and ends that are blunt, a sharp point, or a talon that hooks as it
tapers. Bars carry fangs; stems end in spikes.

Units: cap height 44, baseline 0, slant removed. A stroke is W wide, so a
centre line at y=B or y=T puts the ink's edge on the baseline or cap line.
Each glyph draws from its own random stream, seeded by its name.
"""
import zlib
from glyphs import *

W_ = 8.6                  # stroke width
B, T, MID = 4.3, 39.7, 22.0


def grng(name, salt):
    return np.random.default_rng(zlib.crc32(f'{name}:{salt}'.encode()))


def _noise(r, n, scale):
    """Smooth random wiggle, n samples, about one bump every `scale` samples."""
    k = max(3, n // max(1, scale) + 3)
    knots = r.normal(0, 1, k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), knots)


def _hook(p, d, turn, length=7.0, steps=8):
    """Points that carry on from p in direction d, curling by `turn` radians."""
    out, a = [], np.arctan2(d[1], d[0])
    for i in range(1, steps + 1):
        a += turn / steps
        p = p + np.array([np.cos(a), np.sin(a)]) * length / steps
        out.append(p)
    return out


class Glyph:
    def __init__(self, name):
        self.name, self.k = name, 0
        self.im = Image.new('L', (W, H), 0)
        self.dr = ImageDraw.Draw(self.im)

    def stroke(self, pts, ends=('blunt', 'blunt'), w=W_, closed=False):
        """ends: 'blunt', 'point', or 'talon<deg>' (a point that hooks by deg)."""
        r = grng(self.name, f'stroke{self.k}')
        self.k += 1
        p = np.array(pts, float) + r.normal(0, 0.55, (len(pts), 2))
        if closed:
            p = np.vstack([p, p[:1] + r.normal(0, 1.2, 2)])   # the scrawl never quite closes
        p = list(p)
        taper = [0.0, 0.0]
        for side in (0, 1):
            e = ends[side]
            i, j = (0, 1) if side == 0 else (-1, -2)
            d = p[i] - p[j]
            d = d / np.hypot(*d)
            if e == 'blunt' and not closed:
                p[i] = p[i] + d * r.uniform(0.3, 2.6)            # overshoot the join
            elif e.startswith('talon'):
                turn = np.radians(float(e[5:] or 40))
                hook = _hook(p[i], d, turn)
                p = (hook[::-1] + p) if side == 0 else (p + hook)
                taper[side] = 11.0
            elif e == 'point':
                p[i] = p[i] + d * 4.0
                taper[side] = 9.0
        p = np.array(p)
        seg = np.hypot(*np.diff(p, axis=0).T)
        s = np.concatenate([[0], np.cumsum(seg)])
        L = s[-1]
        n = max(8, int(L / 0.3))
        t = np.linspace(0, L, n)
        x, y = np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])
        width = w * (1 + 0.13 * _noise(r, n, 40))
        if taper[0]:
            width *= np.clip(t / taper[0], 0.08, 1) ** 0.8
        if taper[1]:
            width *= np.clip((L - t) / taper[1], 0.08, 1) ** 0.8
        for xi, yi, wi in zip(x, y, width):
            cx, cy, rad = (xi - X0) * S, (Y1 - yi) * S, wi / 2 * S
            self.dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=255)
        return self

    def fang(self, x, y, length=8.5, w=4.6, up=False):
        """A tooth hanging off the underside of a bar at y (or up off its top)."""
        r = grng(self.name, f'fang{self.k}')
        self.k += 1
        sgn = 1 if up else -1
        tip = (x + r.normal(0.6, 0.4), y + sgn * length * (0.85 + 0.3 * r.random()))
        pts = [(x - w / 2, y - sgn * 1.5), (x + w / 2, y - sgn * 1.5), tip]
        self.dr.polygon([((px - X0) * S, (Y1 - py) * S) for px, py in pts], fill=255)
        return self

    def mask(self):
        a = nd.gaussian_filter(np.asarray(self.im, np.float32) / 255, 0.15 * S)
        return a > 0.5


def g(name):
    return Glyph(name)


L_ = {}
# ── capitals ────────────────────────────────────────────────────────────────
L_['A'] = g('A').stroke([(4, B), (18, T + 1)], ('talon-40', 'blunt')) \
    .stroke([(15, T + 2.5), (32, B)], ('point', 'talon40')) \
    .stroke([(9, 17), (28, 16.5)]).fang(19, 12.5)
L_['B'] = g('B').stroke([(5, B - 1), (5, T)]) \
    .stroke([(4, T), (24, T + 0.5), (29, 33), (25, 24.5), (6, 23)]) \
    .stroke([(8, 23), (28, 21.5), (32, 13), (27, B), (4, B)])
L_['C'] = g('C').stroke([(31, 35), (24, T + 0.5), (11, T), (5, 30), (5, 13), (11, B), (25, B - 0.5), (32, 10)], ('point', 'talon45'))
L_['D'] = g('D').stroke([(5, B - 1), (5, T + 1)]) \
    .stroke([(4, T), (20, T + 0.5), (30, 31), (31, 14), (22, B), (4, B)])
L_['E'] = g('E').stroke([(5, B), (5, T)]) \
    .stroke([(4, T), (30, T + 1)], ('blunt', 'point')).fang(14, T - 4.2).fang(23, T - 4.0) \
    .stroke([(6, MID), (24, MID + 0.5)], ('blunt', 'point')) \
    .stroke([(4, B), (31, B - 0.5)], ('blunt', 'point'))
L_['F'] = g('F').stroke([(5, B - 3), (5, T)], ('talon-35', 'blunt')) \
    .stroke([(4, T), (30, T + 1)], ('blunt', 'point')).fang(15, T - 4.2).fang(24, T - 4.0) \
    .stroke([(6, MID), (24, MID + 0.5)], ('blunt', 'point'))
L_['G'] = g('G').stroke([(31, 35), (24, T + 0.5), (11, T), (5, 30), (5, 13), (11, B), (25, B - 0.5), (31, 11), (31, 21)], ('point', 'blunt')) \
    .stroke([(32, 20), (19, 20.5)], ('blunt', 'point'))
L_['H'] = g('H').stroke([(5, B), (5, T + 2)], ('blunt', 'point')) \
    .stroke([(31, B - 1), (31.5, T + 3)], ('blunt', 'point')) \
    .stroke([(5, MID), (31, MID - 0.5)]).fang(13, MID - 4.2).fang(23, MID - 4.4)
L_['I'] = g('I').stroke([(7, B - 1), (7, T + 1)]) \
    .stroke([(0, T + 0.5), (14, T)], ('point', 'point')) \
    .stroke([(0, B), (15, B - 0.5)], ('point', 'point'))
L_['J'] = g('J').stroke([(26, T + 2), (26, 13), (20, B), (9, B - 0.5), (3, 12)], ('point', 'talon50')) \
    .stroke([(15, T), (33, T + 0.5)], ('point', 'point'))
L_['K'] = g('K').stroke([(5, B), (5, T + 2)], ('blunt', 'point')) \
    .stroke([(31, T + 4), (7, 19)], ('point', 'blunt')) \
    .stroke([(12, 24), (32, B - 1)], ('blunt', 'talon40'))
L_['L'] = g('L').stroke([(5, T + 3), (5, B)], ('point', 'blunt')) \
    .stroke([(4, B), (29, B - 0.5)], ('blunt', 'talon50'))
L_['M'] = g('M').stroke([(4, B), (5, T + 3)], ('blunt', 'point')) \
    .stroke([(5, T), (20, 13)]).stroke([(20, 13), (35, T)]) \
    .stroke([(35, T + 3), (37, B)], ('point', 'blunt'))
L_['N'] = g('N').stroke([(5, B), (5, T + 3)], ('blunt', 'point')) \
    .stroke([(5, T), (31, B)]) \
    .stroke([(31, B - 1), (31.5, T + 3)], ('blunt', 'point'))
L_['O'] = g('O').stroke([(18, T + 0.5), (29, 34), (32, 21), (28, 8), (17, B - 0.5), (7, 8), (4, 22), (7, 35)], closed=True)
L_['P'] = g('P').stroke([(5, B - 2), (5, T)], ('talon-35', 'blunt')) \
    .stroke([(4, T), (24, T + 0.5), (30, 31), (25, 21.5), (6, 20.5)])
L_['Q'] = g('Q').stroke([(18, T + 0.5), (29, 34), (32, 21), (28, 8), (17, B - 0.5), (7, 8), (4, 22), (7, 35)], closed=True) \
    .stroke([(19, 12), (38, -4)], ('blunt', 'talon35'))
L_['R'] = g('R').stroke([(5, B - 1), (5, T)]) \
    .stroke([(4, T), (24, T + 0.5), (30, 31), (25, 22), (6, 21)]) \
    .stroke([(15, 21), (33, B - 1)], ('blunt', 'talon40'))
L_['S'] = g('S').stroke([(30, 35), (22, T + 0.5), (9, T), (5, 31), (12, 24), (25, 20), (31, 12), (25, B), (11, B - 0.5), (3, 10)], ('point', 'talon-45'))
L_['T'] = g('T').stroke([(0, T), (35, T + 1)], ('point', 'point')).fang(8, T - 4.2).fang(28, T - 4.0) \
    .stroke([(18, T), (17, B - 2)], ('blunt', 'talon35'))
L_['U'] = g('U').stroke([(4, T + 3), (4, 12), (10, B), (24, B - 0.5), (30, 12), (30.5, T + 3)], ('point', 'point'))
L_['V'] = g('V').stroke([(2, T + 3), (17, B), (33, T + 3)], ('point', 'point'))
L_['W'] = g('W').stroke([(2, T + 3), (11, B), (21, 31), (31, B), (41, T + 3)], ('point', 'point'))
L_['X'] = g('X').stroke([(3, T + 2), (32, B - 1)], ('point', 'talon40')) \
    .stroke([(31, T + 2), (2, B - 1)], ('point', 'talon-40'))
L_['Y'] = g('Y').stroke([(2, T + 3), (17, 21)], ('point', 'blunt')) \
    .stroke([(33, T + 3), (17, 21), (16.5, B - 2)], ('point', 'talon35'))
L_['Z'] = g('Z').stroke([(1, T), (31, T + 1)], ('point', 'blunt')).fang(10, T - 4.2) \
    .stroke([(31, T), (4, B)]) \
    .stroke([(3, B), (33, B - 0.5)], ('blunt', 'point'))
# ── digits ──────────────────────────────────────────────────────────────────
L_['zero'] = g('zero').stroke([(14, T + 0.5), (24, 34), (26, 21), (23, 8), (13, B - 0.5), (5, 8), (3, 22), (5, 35)], closed=True) \
    .stroke([(9, 12), (20, 30)], ('point', 'point'), w=4.5)
L_['one'] = g('one').stroke([(15, B), (15, T + 1)]) \
    .stroke([(15, T + 1), (4, 31)], ('blunt', 'talon-30')) \
    .stroke([(6, B - 0.5), (25, B)], ('point', 'point'))
L_['two'] = g('two').stroke([(4, 32), (11, T + 0.5), (24, T), (29, 31), (26, 22), (4, B), (31, B - 0.5)], ('point', 'point'))
L_['three'] = g('three').stroke([(4, 36), (13, T + 0.5), (25, T), (29, 31), (23, 23.5), (12, 22.5)], ('point', 'blunt')) \
    .stroke([(20, 23), (30, 15), (27, B + 1), (14, B - 0.5), (3, 9)], ('blunt', 'talon-45'))
L_['four'] = g('four').stroke([(23, B - 2), (23, T + 2)], ('talon35', 'point')) \
    .stroke([(22, T), (3, 15), (33, 15.5)], ('blunt', 'point'))
L_['five'] = g('five').stroke([(30, T + 0.5), (7, T)], ('point', 'blunt')) \
    .stroke([(6, T), (5, 24), (21, 26), (30, 17), (26, B), (12, B - 0.5), (3, 10)], ('blunt', 'talon-45'))
L_['six'] = g('six').stroke([(28, 37), (18, T + 0.5), (8, 33), (4, 18), (7, B + 1), (19, B - 0.5), (29, 8), (29, 18), (19, 24.5), (5, 19)], ('point', 'blunt'))
L_['seven'] = g('seven').stroke([(2, 33), (5, T + 0.5), (31, T + 1)], ('talon-30', 'blunt')) \
    .stroke([(31, T), (19, 20), (13, B - 2)], ('blunt', 'talon35'))
L_['eight'] = g('eight').stroke([(16, 22), (6, 29), (8, T - 0.5), (17, T + 0.5), (26, T - 1), (27, 29), (16, 22), (5, 14), (7, B), (17, B - 0.5), (28, B + 1), (30, 14)], ('blunt', 'blunt'), closed=True)
L_['nine'] = g('nine').stroke([(4, 7), (14, B - 0.5), (24, 11), (28, 26), (25, T - 0.5), (13, T + 0.5), (3, 36), (3, 26), (13, 19.5), (27, 25)], ('talon40', 'blunt'))
# ── punctuation ─────────────────────────────────────────────────────────────
def dot(gl, x=5, y=B):
    return gl.stroke([(x - 1.5, y - 0.5), (x + 2, y + 1)], ('blunt', 'blunt'))
L_['period'] = dot(g('period'))
L_['comma'] = dot(g('comma')).stroke([(7, B), (2, -7)], ('blunt', 'talon-30'), w=6)
L_['colon'] = dot(dot(g('colon')), 6, 24)
L_['semicolon'] = dot(g('semicolon'), 6, 24).stroke([(5, B + 1), (5, B), (1, -7)], ('blunt', 'talon-30'), w=8)
L_['exclam'] = dot(g('exclam')).stroke([(6, T + 2), (5.5, 14)], ('blunt', 'point'))
L_['question'] = dot(g('question'), 15).stroke([(4, 34), (11, T + 0.5), (24, T), (29, 31), (17, 23), (16, 14)], ('point', 'point'))
L_['ellipsis'] = dot(dot(dot(g('ellipsis')), 18), 31)
L_['hyphen'] = g('hyphen').stroke([(1, 19), (21, 20)], ('point', 'point'))
L_['underscore'] = g('underscore').stroke([(0, -7), (36, -6.5)], ('point', 'point'))
L_['quotesingle'] = g('quotesingle').stroke([(6, T + 2), (5, 30)], ('blunt', 'point'), w=8)
L_['quotedbl'] = g('quotedbl').stroke([(6, T + 2), (5, 30)], ('blunt', 'point'), w=8).stroke([(17, T + 2), (16, 30)], ('blunt', 'point'), w=8)
L_['slash'] = g('slash').stroke([(2, B - 2), (33, T + 2)], ('point', 'point'))
L_['backslash'] = g('backslash').stroke([(2, T + 2), (33, B - 2)], ('point', 'point'))
L_['parenleft'] = g('parenleft').stroke([(16, T + 6), (6, 30), (6, 12), (16, -2)], ('point', 'point'), w=8)
L_['parenright'] = g('parenright').stroke([(4, T + 6), (14, 30), (14, 12), (4, -2)], ('point', 'point'), w=8)
L_['bracketleft'] = g('bracketleft').stroke([(17, T + 5), (5, T + 5), (5, -1), (17, -1)], ('point', 'point'), w=8)
L_['bracketright'] = g('bracketright').stroke([(3, T + 5), (15, T + 5), (15, -1), (3, -1)], ('point', 'point'), w=8)
L_['less'] = g('less').stroke([(28, 36), (4, 22), (28, 8)], ('point', 'point'))
L_['greater'] = g('greater').stroke([(4, 36), (28, 22), (4, 8)], ('point', 'point'))
L_['plus'] = g('plus').stroke([(15, 7), (15, 35)], ('point', 'point')).stroke([(2, 21), (29, 21.5)], ('point', 'point'))
L_['equal'] = g('equal').stroke([(2, 28), (26, 28.5)], ('point', 'point')).stroke([(2, 15), (27, 15.5)], ('point', 'point'))
L_['asterisk'] = g('asterisk').stroke([(12, 26), (12, 46)], ('point', 'point'), w=7) \
    .stroke([(3, 31), (21, 41)], ('point', 'point'), w=7).stroke([(3, 41), (21, 31)], ('point', 'point'), w=7)
L_['numbersign'] = g('numbersign').stroke([(10, -1), (15, T + 4)], ('point', 'point'), w=8).stroke([(24, -1), (29, T + 4)], ('point', 'point'), w=8) \
    .stroke([(1, 13), (36, 13.5)], ('point', 'point'), w=8).stroke([(3, 29), (38, 29.5)], ('point', 'point'), w=8)
L_['percent'] = g('percent').stroke([(2, B - 2), (33, T + 2)], ('point', 'point'), w=7) \
    .stroke([(3, 36), (9, 36.5)], w=9).stroke([(26, 8), (32, 8.5)], w=9)
L_['bar'] = g('bar').stroke([(6, -5), (6, T + 6)], ('point', 'point'), w=8)
L_['dollar'] = g('dollar').stroke([(30, 35), (22, T + 0.5), (9, T), (5, 31), (12, 24), (25, 20), (31, 12), (25, B), (11, B - 0.5), (3, 10)], ('point', 'talon-45')) \
    .stroke([(17, -6), (18, T + 7)], ('point', 'point'), w=5)
L_['ampersand'] = g('ampersand').stroke([(33, B - 1), (9, 28), (10, T - 0.5), (18, T + 0.5), (25, 36), (23, 29), (7, 17), (5, 8), (13, B - 0.5), (24, 7), (33, 20)], ('talon35', 'point'))

for _n, _gl in L_.items():
    G[_n] = _gl.mask()
