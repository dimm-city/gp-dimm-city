"""Write the neon print-proof page: proofs/neon/neon-proof.md.

    python3 proofs/neon/make-proof.py     (from the package root; needs Pillow)

A one-off proof page for neon tube colours, read on screen as a soft proof
(proofs/neon/softproof.py) and, whenever one is ordered, as a physical print.
Every swatch is flat, opaque vector (SVG strokes on an ink plate): no blur, no
gradient, no transparency. Each is labelled with its tube's CMYK and total ink
through the press profile (CGATS21_CRPC1, relative colorimetric with black-point
compensation, as the build converts), the colour it prints as and how far that
is from the screen colour (dE76), and its contrast on the printed plate."""
from pathlib import Path

from PIL import Image, ImageCms

ROOT = Path(__file__).resolve().parents[2]
ICC = next((ROOT / "node_modules/gutterpress/dist").glob("CGATS21_CRPC1*.icc"))
PLATE = "#1e1d1c"  # --ink: darker and nearer neutral than --ink-dark
WHITE = "#ffffff"

_srgb = ImageCms.createProfile("sRGB")
_cmyk = ImageCms.getOpenProfile(str(ICC))
_fwd = ImageCms.buildTransform(_srgb, _cmyk, "RGB", "CMYK", renderingIntent=1, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
_back = ImageCms.buildTransform(_cmyk, _srgb, "CMYK", "RGB", renderingIntent=1, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
_lab = ImageCms.buildTransform(_srgb, ImageCms.createProfile("LAB"), "RGB", "LAB")


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def cmyk(h):
    c = ImageCms.applyTransform(Image.new("RGB", (1, 1), rgb(h)), _fwd).getpixel((0, 0))
    pct = [round(v / 2.55) for v in c]
    return "C%d M%d Y%d K%d" % tuple(pct), sum(pct)


def printed(h):
    """The colour the press makes of h (sRGB -> CRPC1 -> sRGB), and dE76 between them."""
    c = ImageCms.applyTransform(Image.new("RGB", (1, 1), rgb(h)), _fwd)
    out = "#%02x%02x%02x" % ImageCms.applyTransform(c, _back).getpixel((0, 0))
    a, b = (ImageCms.applyTransform(Image.new("RGB", (1, 1), rgb(x)), _lab).getpixel((0, 0)) for x in (h, out))
    return out, ((a[0] - b[0]) ** 2 / 2.55 ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    """t of a, the rest b, in sRGB: a pale tint of the tube for its core."""
    return "#%02x%02x%02x" % tuple(round(x * t + y * (1 - t)) for x, y in zip(rgb(a), rgb(b)))


# name, tube, ring 1 (mid), ring 2 (dark), where it would be used
LADDERS = [
    ("Cyan", "#00bcd4", "#006878", "#003a40", "Dream Master chapter; Augmerc"),
    ("Yellow", "#ffd700", "#8a6a00", "#46360c", "Gear chapter; Etherlock"),
    ("Orange (control)", "#d4500a", "#7a3008", "#4c290f", "Rules chapter; Technosorcerer"),
    ("Orange, brighter (candidate)", "#f06a1e", "#7a3008", "#4c290f", "Rules chapter candidate"),
    ("Hot pink (proposed)", "#f0288c", "#9c0f63", "#690045", "Citizen File, lore; Proxy"),
    ("Brand magenta (control)", "#cf217e", "#9c0f63", "#690045", "today's magenta, for comparison"),
    ("Fungi green", "#c8e040", "#4d6020", "#30461e", "Gutterdruid"),
    ("Civic green", "#4db840", "#347828", "#30461e", "Streetwarden"),
    ("Chrome", "#a8b4b8", "#52626f", "#303840", "Cybersurgeon"),
    ("Indigo (control)", "#396cb7", "#093c81", "#181b45", "Wirephreak today: expected dull"),
    ("Indigo, brighter (rejected)", "#4f8cf0", "#093c81", "#181b45", "out of gamut: prints dusty"),
    ("Azure (candidate)", "#0090d8", "#004f7a", "#0d2a45", "Wirephreak candidate"),
]

PT = 1.333  # CSS px per pt


def tube_svg(tube, r1, r2, core, w_core=1.2, w_tube=3, w_r1=6, w_r2=9, dead=False):
    """A tube on an ink plate: a straight run, a loop and a zigzag, drawn back to front
    as four opaque round-capped strokes (ring 2, ring 1, tube, core)."""
    d = "M18 62 L70 62 M88 62 C88 30 132 30 132 52 C132 74 96 74 96 52 M150 70 L162 34 L174 70 L186 34 L198 70"
    layers = [(r2, w_r2), (r1, w_r1), (tube, w_tube), (core, w_core)]
    if dead:
        layers = [("#665b4e", w_tube), ("#8a8078", w_core)]
    paths = "".join(
        f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w * PT:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
        for c, w in layers)
    return (f'<svg class="np-tube" viewBox="0 0 216 96" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<rect width="216" height="96" fill="{PLATE}"/>{paths}</svg>')


def swatch(name, tube, r1, r2, use):
    core = mix(tube, WHITE, 0.25)
    ink, tac = cmyk(tube)
    out, de = printed(tube)
    return (f'<figure class="np-swatch">{tube_svg(tube, r1, r2, core)}'
            f'<figcaption><b>{name}</b> {tube}<br>{ink} = {tac}%<br>'
            f'prints {out} (dE {de:.0f}) · {contrast(out, printed(PLATE)[0]):.1f}:1 on the plate<br>{use}</figcaption></figure>')


def strip(label, items):
    return f'<div class="np-row"><h3>{label}</h3><div class="np-grid">{"".join(items)}</div></div>'


def main():
    out = ["# Neon print proof {.np-title}", "",
           '<p class="np-lede">Read this page as a soft proof (proofs/neon/softproof.py) and, when one is ordered, as a print proof. '
           "Every swatch is flat, opaque vector on an ink plate (--ink): a 1.2pt core (25% of the tube into white), "
           "a 3pt tube, a 6pt and a 9pt ring. Check: does it read as lit? Does the core fringe? Do the rings stay "
           "apart? CMYK is the tube's, through CGATS21_CRPC1.</p>", ""]
    out.append(strip("1. Tube ladders", [swatch(*l) for l in LADDERS]))
    pink, cyan = LADDERS[4], LADDERS[0]
    cores = []
    for nm, t, a, b, _ in (pink, cyan):
        for w in (1.0, 1.5, 2.0):
            cores.append(f'<figure class="np-swatch">{tube_svg(t, a, b, mix(t, WHITE, 0.25), w_core=w)}'
                         f'<figcaption><b>{nm.split(" ")[0]} core {w:g}pt</b><br>fringe test: look for colour around the core</figcaption></figure>')
    out.append(strip("2. Core width (registration)", cores))
    rings = []
    for nm, t, a, b, _ in (pink, cyan):
        for step in (1.0, 1.5, 2.0):
            rings.append(f'<figure class="np-swatch">{tube_svg(t, a, b, mix(t, WHITE, 0.25), w_r1=3 + 2 * step, w_r2=3 + 4 * step)}'
                         f'<figcaption><b>{nm.split(" ")[0]} ring step {step:g}pt</b><br>dot-gain test: the rings must not merge</figcaption></figure>')
    out.append(strip("3. Ring step (dot gain)", rings))
    out.append(strip("4. Lit and dead tubes", [
        f'<figure class="np-swatch">{tube_svg(*pink[1:4], mix(pink[1], WHITE, 0.25))}<figcaption><b>Lit</b></figcaption></figure>',
        f'<figure class="np-swatch">{tube_svg(*pink[1:4], mix(pink[1], WHITE, 0.25), dead=True)}<figcaption><b>Dead tube</b> (grey, no halo)</figcaption></figure>',
        f'<figure class="np-swatch np-day">{tube_svg(*cyan[1:4], mix(cyan[1], WHITE, 0.25)).replace(f"fill=\"{PLATE}\"", "fill=\"#ffffff\"")}'
        '<figcaption><b>Daylight</b> (no plate, on white): expected to read as an outline, not light</figcaption></figure>',
    ]))
    out.append(SIGN)
    Path(__file__).with_name("neon-proof.md").write_text("\n".join(out) + "\n")


def word(text, layers, size, x, y, dead=None):
    """A word drawn as stacked text runs, back to front (outer ring first, the
    core fill last), each one whole word so every letter keeps its place. A
    `dead` letter index is drawn grey with no halo in every run."""
    runs = []
    for stroke, width in layers:
        spans = "".join(
            (f'<tspan stroke="none" fill="none">{ch}</tspan>' if i == dead and stroke != "fill" else
             f'<tspan fill="#3a3530" stroke="#665b4e" stroke-width="2">{ch}</tspan>' if i == dead else ch)
            for i, ch in enumerate(text))
        paint = f'fill="{width}"' if stroke == "fill" else f'fill="none" stroke="{stroke}" stroke-width="{width}"'
        runs.append(f'<text x="{x}" y="{y}" text-anchor="middle" {paint}>{spans}</text>')
    return (f'<g font-family="lixdu, Tomorrow, sans-serif" font-size="{size}" stroke-linejoin="round" '
            f'stroke-linecap="round">{"".join(runs)}</g>')


PINK = [("#690045", 11), ("#9c0f63", 7.5), ("#f0288c", 4), ("fill", "#fcc9e2")]
ORANGE = [("#4c290f", 11), ("#7a3008", 7.5), ("#d4500a", 4), ("fill", "#f6d3c2")]

SIGN = f'''<div class="np-row"><h3>5. Lettering and a sign</h3>
<p class="np-note">Left: the word as SVG text, drawn as four stacked runs (outer ring, inner ring, tube, pale core fill). Right: the same word as live HTML text in the core colour, with the tube drawn as zero-blur rings on the plate's edge. Both build as live text (Lixdu is embedded and the word copies out of the PDF). Under them, the whole object: a bolted plate on standoffs, one dead letter, the cable and the transformer box.</p>
<div class="np-grid">
<figure class="np-swatch np-wide"><svg viewBox="0 0 300 96" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="300" height="96" fill="#1e1d1c"/>{word("RULES", PINK, 40, 150, 63)}</svg><figcaption><b>SVG lettering</b></figcaption></figure>
<figure class="np-swatch np-wide"><div class="np-html-sign">RULES</div><figcaption><b>Live-text lettering</b>, ringed plate</figcaption></figure>
</div>
<div class="np-sign">
<span class="np-bolt np-bolt-l"></span><span class="np-bolt np-bolt-r"></span>
<svg viewBox="0 0 420 110" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="420" height="110" fill="#1e1d1c"/>{word("RULES", ORANGE, 54, 210, 74, dead=3)}</svg>
<span class="np-cable"></span><span class="np-transformer"></span>
</div>
</div>'''


if __name__ == "__main__":
    main()
