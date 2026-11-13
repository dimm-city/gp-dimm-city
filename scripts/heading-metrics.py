"""Write FIT_FONTS into plugin.js: the advance widths (and Lixdu's kerning) of the
two heading faces, so the plugin can measure a heading's words at build time.

    python3 scripts/heading-metrics.py      (from the package root; needs fontTools)

A heading that would wrap may shrink a little to keep one line (plugin.js,
dcHeadingFit; dc-core.css, `.dc-fit`). CSS cannot measure text, so the plugin
writes each heading's width in em onto it, read from the fonts the stylesheet
sets: Creaturepunk for h1 and h2 (`--font-title`, at its @font-face's size-adjust), Lixdu for the rest
(`--font-display`, whose curly quotes, dashes and ellipsis come from Tomorrow
Bold). A character a face lacks falls through to the next face of its stack, as
in the browser. Headings are set in capitals, so only the characters a capital
heading can hold are listed, with every pair of them Lixdu kerns. Widths are
font units per em (1000). The block sits between its BEGIN and END lines in
plugin.js (which imports nothing at runtime)."""
import json
import re
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
# What a capital heading can hold: printable ASCII less the lower case, and the
# typeset punctuation the book's smart quotes produce.
CHARS = [chr(c) for c in range(0x20, 0x7F) if not "a" <= chr(c) <= "z"] + list("‘’“”–—…")
LIXDU_TOMORROW = set("‘’“”–—…")   # dc-fonts.css: lixdu's second @font-face (Tomorrow Bold)


def advances(font, scale=1.0):
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return {ch: round(hmtx[cmap[ord(ch)]][0] * 1000 * scale / upm) for ch in CHARS if ord(ch) in cmap}


def overhangs(font, scale=1.0):
    """How far each glyph's ink runs past its advance (Creaturepunk's slanted
    caps do, by up to 0.4em), so the last letter of a line can be fitted by
    its ink, not its advance."""
    cmap, glyf, hmtx, upm = font.getBestCmap(), font["glyf"], font["hmtx"], font["head"].unitsPerEm
    out = {}
    for ch in CHARS:
        name = cmap.get(ord(ch))
        over = getattr(glyf[name], "xMax", 0) - hmtx[name][0] if name else 0
        if over * 1000 / upm > 10:
            out[ch] = round(over * 1000 * scale / upm)
    return out


def size_adjust(family):
    """The `size-adjust` of a family's @font-face in dc-fonts.css (1 when it has none)."""
    css = (ROOT / "styles/dc-fonts.css").read_text()
    face = re.search(rf"@font-face\s*{{[^}}]*font-family:\s*'{family}'[^}}]*}}", css).group(0)
    m = re.search(r"size-adjust:\s*([\d.]+)%", face)
    return float(m.group(1)) / 100 if m else 1.0


def kerning(font):
    """Pair adjustments from GPOS PairPos (format 1 and 2), keyed by character pair."""
    cmap = font.getBestCmap()
    glyph = {ch: cmap[ord(ch)] for ch in CHARS if ord(ch) in cmap}
    pairs = {}
    for lookup in font["GPOS"].table.LookupList.Lookup:
        if lookup.LookupType != 2:
            continue
        for st in lookup.SubTable:
            cover = set(st.Coverage.glyphs)
            for a, ga in glyph.items():
                if ga not in cover:
                    continue
                for b, gb in glyph.items():
                    if a + b in pairs:
                        continue
                    v = 0
                    if st.Format == 1:
                        ps = st.PairSet[st.Coverage.glyphs.index(ga)]
                        rec = next((r for r in ps.PairValueRecord if r.SecondGlyph == gb), None)
                        v = getattr(rec.Value1, "XAdvance", 0) if rec and rec.Value1 else 0
                    else:
                        c1 = st.ClassDef1.classDefs.get(ga, 0)
                        c2 = st.ClassDef2.classDefs.get(gb, 0)
                        rec = st.Class1Record[c1].Class2Record[c2]
                        v = getattr(rec.Value1, "XAdvance", 0) if rec.Value1 else 0
                    if v:
                        pairs[a + b] = v
    return pairs


creaturepunk = TTFont(FONTS / "creaturepunk/Creaturepunk.ttf")
lixdu = TTFont(FONTS / "lixdu/lixdu.woff")
tomorrow_bold = advances(TTFont(FONTS / "tomorrow/tomorrow-700.ttf"))
tomorrow = advances(TTFont(FONTS / "tomorrow/tomorrow-400.ttf"))

display = {ch: w for ch, w in advances(lixdu).items() if ch not in LIXDU_TOMORROW}
display.update({ch: tomorrow_bold[ch] for ch in LIXDU_TOMORROW})
display.update({ch: w for ch, w in tomorrow.items() if ch not in display})
title = advances(creaturepunk, size_adjust("Creaturepunk"))   # drawn larger than its em
title_over = overhangs(creaturepunk, size_adjust("Creaturepunk"))
title.update({ch: w for ch, w in display.items() if ch not in title})
kern = {p: v for p, v in kerning(lixdu).items() if not set(p) & LIXDU_TOMORROW}
assert "kern" not in creaturepunk and "GPOS" not in creaturepunk, "Creaturepunk now kerns: list its pairs too"


def row(widths):
    return "".join(ch for ch in CHARS if ch in widths), " ".join(str(widths[ch]) for ch in CHARS if ch in widths)


def js(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


lines = []
for name, widths in (("title", title), ("display", display)):
    chars, w = row(widths)
    lines.append(f"  {name}: {{\n    chars: {js(chars)},\n    widths: '{w}',")
    pairs = kern if name == "display" else {}
    over = title_over if name == "title" else {}   # Lixdu's ink stays inside its advances
    lines.append(f"    overhang: {json.dumps(over, ensure_ascii=False)},")
    lines.append(f"    kern: {json.dumps(dict(sorted(pairs.items())), ensure_ascii=False)},\n  }},")

BEGIN = "// BEGIN FIT_FONTS (generated by scripts/heading-metrics.py; do not edit)"
END = "// END FIT_FONTS"
block = f"""{BEGIN}
// Advance widths per 1000 units of em, one per character of `chars`; `kern` maps
// a pair of characters to its adjustment, `overhang` a character to how far its
// ink runs past its advance (a line ends at its last letter's ink). Creaturepunk and Lixdu
// (fonts/*/LICENSE.txt), with the fallbacks of their stacks.
const FIT_FONTS = {{
{chr(10).join(lines)}
}};
{END}"""
plugin = ROOT / "plugin.js"
src = plugin.read_text()
i, j = src.index(BEGIN), src.index(END) + len(END)
plugin.write_text(src[:i] + block + src[j:])
print("wrote FIT_FONTS into plugin.js:", len(title), "title,", len(display), "display,", len(kern), "kerning pairs")
