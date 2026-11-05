#!/usr/bin/env python3
"""Measure the palette the way the PDF/X build separates it.

What it does: converts every hex token in styles/dc-palette.css and
styles/dc-identity.css (and every color-mix() tint of two palette tokens in
styles/) sRGB -> CMYK the way `gutterpress build --format pdfx` does: a swatch
of each colour goes through Ghostscript's pdfwrite with CGATS21_CRPC1 as the
output profile at Ghostscript's default intent (relative colorimetric with
black-point compensation), and the `c m y k k` operands are read back out of
the PDF. It reports TAC, the colour printed back to sRGB, OKLab distances and
WCAG contrast. docs/print-colour-audit-measurements.md is this script's output.

The CMYK figures are the build's to the digit (the same Ghostscript release
writes the same operands). The "printed" colour is that CMYK converted back
to sRGB with LittleCMS at the same intent (relative colorimetric, BPC), so an
in-gamut colour round-trips to itself and dE measures only what the gamut
moved. Before 1.10.2-alpha.2 the forward conversion was LittleCMS at
perceptual intent, which the build never used; its figures ran 10-30% TAC under
the build's on the purples and 15-20% under on the inks.

Needs: Ghostscript 10.03 or newer on PATH (10.02 and older ignore the output
profile and separate through their default CMYK profile), Python 3 and Pillow
(built with LittleCMS, as the wheels are).
Profile: --icc PATH, else $CRPC1_ICC, else the CGATS21_CRPC1*.icc the
installed gutterpress ships in node_modules/gutterpress/dist/.

Usage: python3 scripts/measure-palette-crpc1.py [--icc PATH] [tokens|mixes|contrast|dupes|converge|all]
"""
import glob, math, os, re, subprocess, sys, tempfile
from PIL import Image, ImageCms

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
icc = os.environ.get('CRPC1_ICC')
if '--icc' in args:
    i = args.index('--icc'); icc = args[i + 1]; del args[i:i + 2]
icc = icc or next(iter(sorted(glob.glob(os.path.join(ROOT, 'node_modules/gutterpress/dist/CGATS21_CRPC1*.icc')))), None)
if not icc or not os.path.exists(icc):
    sys.exit('CGATS21_CRPC1 profile not found: run `bun install`, or pass --icc PATH / set CRPC1_ICC')
try: gs_version = subprocess.run(['gs', '--version'], capture_output=True, text=True, check=True).stdout.strip()
except (OSError, subprocess.CalledProcessError): sys.exit('Ghostscript (gs) not found: the build separates with it, so this script needs it')
if tuple(map(int, gs_version.split('.')[:2])) < (10, 3): sys.exit(f'Ghostscript {gs_version} ignores -sOutputICCProfile; 10.03 or newer is needed')
srgb = ImageCms.createProfile('sRGB'); cmyk = ImageCms.getOpenProfile(icc)
B = ImageCms.buildTransform(cmyk, srgb, 'CMYK', 'RGB', renderingIntent=1, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)

def hex2rgb(h):
    h = h.lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def tohex(rgb): return '#%02x%02x%02x' % tuple(rgb)

CMYK = {}  # sRGB -> (c, m, y, k) in 0..1, as Ghostscript wrote them
def separate(rgbs):
    """Run the given sRGB colours through pdfwrite exactly as the build does (one
    swatch each, in order) and cache the CMYK operands it writes. pdfwrite skips
    a colour operator when the colour has not changed, so the swatches are
    deduplicated; it writes no-ink white as DeviceGray `1 g`."""
    rgbs = [c for c in dict.fromkeys(rgbs) if c not in CMYK]
    if not rgbs: return
    with tempfile.TemporaryDirectory() as d:
        ps, pdf = os.path.join(d, 'swatches.ps'), os.path.join(d, 'swatches.pdf')
        with open(ps, 'w') as f:
            f.write('%%!\n<< /PageSize [%d 10] >> setpagedevice\n' % len(rgbs))
            for i, (r, g, b) in enumerate(rgbs): f.write('%.6f %.6f %.6f setrgbcolor %d 0 1 10 rectfill\n' % (r / 255, g / 255, b / 255, i))
            f.write('showpage\n')
        subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-dSAFER', f'--permit-file-read={icc}', '-sDEVICE=pdfwrite', '-dPDFX',
                        '-dCompressPages=false', '-sProcessColorModel=DeviceCMYK', '-sColorConversionStrategy=CMYK',
                        '-dOverrideICC=true', f'-sOutputICCProfile={icc}', f'-sOutputFile={pdf}', ps], check=True)
        ops = []
        for line in open(pdf, 'rb').read().decode('latin1').splitlines():
            if m := re.fullmatch(r'([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) k', line.strip()): ops.append(tuple(float(x) for x in m.groups()))
            elif m := re.fullmatch(r'([\d.]+) g', line.strip()): ops.append((0.0, 0.0, 0.0, 1 - float(m.group(1))))
    if len(ops) != len(rgbs): sys.exit(f'Ghostscript wrote {len(ops)} colours for {len(rgbs)} swatches')
    CMYK.update(zip(rgbs, ops))
def to_cmyk(rgb):
    if rgb not in CMYK: separate([rgb])
    return CMYK[rgb]
def printed(rgb): return ImageCms.applyTransform(Image.new('CMYK', (1, 1), tuple(round(x * 255) for x in to_cmyk(rgb))), B).getpixel((0, 0))
def pct(rgb): return [round(x * 100) for x in to_cmyk(rgb)]
def cmyk_str(p): return 'C%d M%d Y%d K%d' % tuple(p)

# sRGB <-> OKLab / OKLCh
def lin(c): c /= 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def gam(c): c = min(max(c, 0), 1); return round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))
def oklab(rgb):
    r, g, b = map(lin, rgb)
    l, m, s = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b) ** (1/3), (0.2119034982*r + 0.6806995451*g + 0.1073969566*b) ** (1/3), (0.0883024619*r + 0.2817188376*g + 0.6299787005*b) ** (1/3)
    return (0.2104542553*l + 0.7936177850*m - 0.0040720468*s, 1.9779984951*l - 2.4285922050*m + 0.4505937099*s, 0.0259040371*l + 0.7827717662*m - 0.8086757660*s)
def from_oklab(L, a, b):
    l, m, s = (L + 0.3963377774*a + 0.2158037573*b) ** 3, (L - 0.1055613458*a - 0.0638541728*b) ** 3, (L - 0.0894841775*a - 1.2914855480*b) ** 3
    return tuple(map(gam, (4.0767416621*l - 3.3077115913*m + 0.2309699292*s, -1.2684380046*l + 2.6097574011*m - 0.3413193965*s, -0.0041960863*l - 0.7034186147*m + 1.7076147010*s)))
def oklch(rgb):
    L, a, b = oklab(rgb); return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360
def dE(r1, r2): return 100 * math.dist(oklab(r1), oklab(r2))  # OKLab distance x100
def Y(rgb): r, g, b = map(lin, rgb); return .2126*r + .7152*g + .0722*b
def contrast(a, b): ya, yb = sorted((Y(a), Y(b))); return (yb + .05) / (ya + .05)

def mix(space, c1, p1, c2):
    """color-mix(in <space>, c1 p1%, c2) as Chromium paints it (sRGB clipped). An
    achromatic colour's hue is missing in oklch, so the other colour's is used."""
    w = p1 / 100
    if space == 'srgb': return tuple(round(a * w + b * (1 - w)) for a, b in zip(c1, c2))
    (L1, C1, h1), (L2, C2, h2) = oklch(c1), oklch(c2)
    if C1 < 2e-4: h1 = h2
    if C2 < 2e-4: h2 = h1
    dh = (h2 - h1 + 180) % 360 - 180; h = math.radians(h1 + dh * (1 - w)); C = C1 * w + C2 * (1 - w)
    return from_oklab(L1 * w + L2 * (1 - w), C * math.cos(h), C * math.sin(h))

# Tokens: hex declarations, plus var() aliases resolved through them.
tokens, aliases = {}, {}
for f in ('styles/dc-palette.css', 'styles/dc-identity.css'):
    for name, val in re.findall(r'^\s*(--[a-z0-9-]+):\s*([^;]+);', open(os.path.join(ROOT, f)).read(), re.M):
        if re.fullmatch(r'#[0-9a-fA-F]{3,6}', val.strip()): tokens[name] = hex2rgb(val.strip())
        elif m := re.fullmatch(r'var\((--[a-z0-9-]+)\)', val.strip()): aliases[name] = m.group(1)
def tok(name):
    while name in aliases: name = aliases[name]
    return tokens.get(name)
W = (255, 255, 255)
separate(tokens.values())  # one Ghostscript run for the whole palette

def report_tokens():
    print(f"{'token':24} {'hex':8} {'CMYK (build)':20} {'TAC':>4} {'printed':8} {'dE':>5}  {'okL':>5} {'okC':>5} {'okH':>4}")
    for n, rgb in tokens.items():
        p = pct(rgb); L, C, h = oklch(rgb)
        print(f"{n:24} {tohex(rgb):8} {cmyk_str(p):20} {sum(p):4d} {tohex(printed(rgb)):8} {dE(rgb, printed(rgb)):5.1f}  {L:5.2f} {C:5.3f} {h:4.0f}")
    print('aliases: ' + ', '.join(f'{a} -> {b}' for a, b in aliases.items() if tok(a)))

def report_mixes():
    """Every color-mix() of two palette tokens in styles/ (mixes with transparent,
    or with a --dc-* variable, are not tints of paper and are skipped)."""
    pat = re.compile(r'color-mix\(in (srgb|oklch), var\((--[a-z0-9-]+)\) (\d+)%, var\((--[a-z0-9-]+)\)(?: \d+%)?\)')
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, 'styles/**/*.css'), recursive=True)):
        for ln, line in enumerate(open(f), 1):
            for space, a, p, b in pat.findall(line):
                if (space, a, p, b) in seen or not tok(a) or not tok(b): continue
                seen.add((space, a, p, b)); rows.append((os.path.relpath(f, ROOT)[7:] + ':' + str(ln), space + ' ' + a + ' ' + p + '% ' + b, mix(space, tok(a), int(p), tok(b))))
    separate(rgb for _, _, rgb in rows)
    print(f"{'where':38} {'mix':48} {'hex':8} {'CMYK':18} {'TAC':>4} {'max':>4} {'min':>4}")
    for where, what, rgb in rows:
        c = pct(rgb); nz = [x for x in c if x]
        print(f"{where:38} {what:48} {tohex(rgb):8} {cmyk_str(c):18} {sum(c):4d} {max(c):4d} {min(nz) if nz else 0:4d}")

# Text-on-fill pairs: (what, text, ground). A colour is a token, a '#hex', or
# ('oklch'|'srgb', token, percent, token) for a color-mix().
PAIRS = [
    ('body text on paper', '--ink', W), ('--ink-dark on paper', '--ink-dark', W),
    ('--ink on --paper-aged (field chip, code)', '--ink', '--paper-aged'), ('--ink on the wall', '--ink', '--bg'),
    ('--ink on --concrete-pale (pullquote, dm)', '--ink', '--concrete-pale'), ('--ink on --hud-blue-dim (alert, reference bar)', '--ink', '--hud-blue-dim'),
    ('--ink on --brand-yellow', '--ink', '--brand-yellow'), ('--ink on --fungi-glow (hit row)', '--ink', '--fungi-glow'),
    ('--ink on --dc-tape-bg', '--ink', ('srgb', '--brand-yellow', 30, '--paper-aged')),
    ('white on magenta bar (90% over ink)', W, ('srgb', '--brand-magenta', 90, '--ink')), ('white on --brand-magenta', W, '--brand-magenta'),
    ('--brand-magenta on white (h1, large)', '--brand-magenta', W),
    ('white on --brand-magenta-deep (chevron, crit, VAR chip, proxy band)', W, '--brand-magenta-deep'),
    ('--brand-magenta-deep on white (default accent ink)', '--brand-magenta-deep', W),
    ('--brand-magenta-deep on --concrete-pale (pullquote ink)', '--brand-magenta-deep', '--concrete-pale'),
    ('white on proxy band facet (30% ink)', W, ('srgb', '--ink', 30, '--brand-magenta-deep')),
    ('magenta 38% term on --wirephreak-dark', ('srgb', '--brand-magenta', 38, W), '--wirephreak-dark'),
    ('--proxy-dark on white (proxy chip)', '--proxy-dark', W), ('white on --proxy-dark (sticker)', W, '--proxy-dark'),
    ('white on --proxy-mid (tab)', W, '--proxy-mid'),
    ('white on --brand-violet (chip, badge)', W, '--brand-violet'), ('--brand-violet on white (treasure ink)', '--brand-violet', W),
    ('--brand-violet on vibe sheet (accent ink)', '--brand-violet', ('oklch', '--brand-violet', 22, '--paper-cream')),
    ('--ink on the darkest tint (treasure ornament)', '--ink', ('oklch', '--crystal-amethyst', 40, '--paper-cream')),
    ('--blood on the flaws/cult tint', '--blood', ('oklch', '--blood', 18, '--paper-cream')),
    ('--hud-blue-dark on the ideals/reference tint', '--hud-blue-dark', ('oklch', '--hud-blue-dim', 30, '--paper-cream')),
    ('white on lore bar (violet 72% over ink)', W, ('srgb', '--brand-violet', 72, '--ink')),
    ('white on --crystal-amethyst (chip)', W, '--crystal-amethyst'),
    ('white on --signal-indigo (wirephreak band, chip)', W, '--signal-indigo'), ('--signal-indigo on white (classtag)', '--signal-indigo', W),
    ('--wirephreak-mid on white (spec ink)', '--wirephreak-mid', W), ('white on --wirephreak-mid (tab)', W, '--wirephreak-mid'),
    ('white on --wirephreak-dark', W, '--wirephreak-dark'),
    ('white on --hud-blue-dark (AP chip, block title)', W, '--hud-blue-dark'), ('--hud-blue-dark on white', '--hud-blue-dark', W),
    ('white on --rust (chapter chip)', W, '--rust'), ('white on --crimson (card band default)', W, '--crimson'),
    ('--orange dot on white (classtag; non-text, needs 3:1)', '--orange', W), ('--orange-deep on white (lede ink)', '--orange-deep', W),
    ('white on --orange-deep (mixed row)', W, '--orange-deep'), ('white on --blood (miss row)', W, '--blood'),
    ('white on --fungi-rot (fail row)', W, '--fungi-rot'), ('white on --amber-dark', W, '--amber-dark'),
    ('--fungi-glow on visit bg (accent ink)', '--fungi-glow', ('srgb', '--fungi-rot', 85, '--fungi-glow')),
    ('white on visit bg (body)', W, ('srgb', '--fungi-rot', 85, '--fungi-glow')),
    ('--brand-cyan on --ink-dark (dm accent)', '--brand-cyan', '--ink-dark'),
    ('--ink-dust on the wall', '--ink-dust', '--bg'),
]
# Specialties (specialty-identity.css): band / on-band, tier chip bg / fg, text ink.
# Cream type also sits on every --*-mid (card tab) and --*-dark (path chip).
SPECIALTIES = {
    'augmerc': ('--augmerc-accent', '--ink', '--augmerc-accent', '--ink', '--augmerc-mid'),
    'technosorcerer': (('srgb', '--orange', 87, '--paper-cream'), '--ink', W, '--technosorcerer-dark', '--technosorcerer-mid'),
    'streetwarden': ('--streetwarden-accent', '--ink', '--streetwarden-accent', '--ink', '--streetwarden-dark'),
    'gutterdruid': ('--gutterdruid-accent', '--ink', '--gutterdruid-accent', '--ink', '--gutterdruid-dark'),
    'cybersurgeon': ('--cybersurgeon-accent', '--ink', '--cybersurgeon-accent', '--ink', '--cybersurgeon-dark'),
    'wirephreak': ('--wirephreak-accent', W, '--wirephreak-accent', W, '--wirephreak-mid'),
    'proxy': ('--brand-magenta-deep', W, W, '--proxy-dark', '--brand-magenta-deep'),
    'etherlock': ('--etherlock-accent', '--ink', '--etherlock-accent', '--ink', '--etherlock-dark'),
    'dualist': ('--dualist-accent', '--ink', '--dualist-accent', '--ink', '--dualist-mid'),
    'generalist': ('--generalist-accent', W, '--generalist-accent', W, '--generalist-mid'),
}
for n, (band, on, chip, chip_fg, ink) in SPECIALTIES.items():
    PAIRS += [(f'{n}: on-band type on band', on, band), (f'{n}: tier chip', chip_fg, chip),
              (f'{n}: text ink on paper', ink, W), (f'{n}: cream on --{n}-mid (tab)', W, f'--{n}-mid'), (f'{n}: cream on --{n}-dark (chip)', W, f'--{n}-dark')]
    if n in ('technosorcerer', 'gutterdruid', 'etherlock'):  # their cards sit on --paper-aged
        PAIRS.append((f'{n}: text ink on --paper-aged', ink, '--paper-aged'))
def colour(c):
    if isinstance(c, tuple) and isinstance(c[0], str): return mix(c[0], colour(c[1]), c[2], colour(c[3]))
    if isinstance(c, str): return hex2rgb(c) if c.startswith('#') else tok(c)
    return c
def report_contrast():
    for what, fg, bg in PAIRS:
        r = contrast(colour(fg), colour(bg))
        print(f"{r:5.2f}:1  {'AAA' if r >= 7 else 'AA' if r >= 4.5 else 'AA-large' if r >= 3 else 'FAIL':8} {what}")

def report_dupes(limit=6):
    names = list(tokens)
    out = sorted((dE(tokens[a], tokens[b]), a, b) for i, a in enumerate(names) for b in names[i + 1:])
    for d, a, b in out:
        if d < limit: print(f"dE {d:4.1f}  {a:24} {tohex(tokens[a])}  ~  {b:24} {tohex(tokens[b])}")

FAMILIES = {
    'purples': ['--brand-magenta', '--proxy-mid', '--brand-magenta-deep', '--crystal-amethyst', '--brand-violet', '--signal-indigo', '--wirephreak-mid', '--wirephreak-dark', '--tint-magenta-rose'],
    'warm reds': ['--crimson', '--orange', '--rust', '--orange-deep', '--blood', '--deep-rust', '--technosorcerer-mid'],
    'teals': ['--brand-cyan', '--hud-blue', '--hud-blue-dark', '--crystal-aqua', '--augmerc-mid', '--hud-blue-dim'],
    'greens': ['--fungi-glow', '--streetwarden-accent', '--streetwarden-mid', '--gutterdruid-mid', '--brand-yellow', '--etherlock-mid'],
}
def report_converge():
    for fam, names in FAMILIES.items():
        print(f"\n== {fam}: OKLab distance on screen -> printed (CRPC1 round trip); pairs printing < 10 apart ==")
        names = [n for n in names if n in tokens]
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                d0, d1 = dE(tok(a), tok(b)), dE(printed(tok(a)), printed(tok(b)))
                if d1 < 10: print(f"  {a:22} {b:22} {d0:5.1f} -> {d1:5.1f}  (printed {tohex(printed(tok(a)))} vs {tohex(printed(tok(b)))})")

MODES = {'tokens': report_tokens, 'mixes': report_mixes, 'contrast': report_contrast, 'dupes': report_dupes, 'converge': report_converge}
print('profile:', ImageCms.getProfileDescription(cmyk).strip(), '· Ghostscript', gs_version)
for m in (MODES if args[:1] == ['all'] else args[:1] or ['tokens']):
    if len(MODES) > 1 and args[:1] == ['all']: print(f'\n## {m}')
    MODES[m]()
