# Creaturepunk source

`creaturepunk-logo.png` is the lettering the Creaturepunk font was traced
from. `fonts/creaturepunk/Creaturepunk.ttf` is the working source: edit it in
`docs/creaturepunk-font-demo.html`. The Python generator here is the
deterministic reset.

## Edit the font

1. Serve the repo root with any static server (for example `bunx serve .`)
   and open `/docs/creaturepunk-font-demo.html`. The page loads the font from
   `fonts/creaturepunk/`. Opened straight from disk, it asks you to open the
   `.ttf` instead.
2. Under *Edit glyphs*, pick a glyph, drag its points and set its side
   bearings. The whole page redraws in the edited font.
3. Click *Download Creaturepunk.ttf* and replace
   `fonts/creaturepunk/Creaturepunk.ttf` with the download.

The editor changes outlines and spacing only; names, licence, swash features
and line metrics are copied unchanged.

## Reset the font from the generator

The generator rebuilds `Creaturepunk.ttf` from the traced lettering, the same
way every time (its edge noise is seeded). **Running it overwrites every hand
edit made in the page.**

```sh
pip install fonttools numpy pillow scipy potracer
python3 extract.py
python3 build.py            # writes ../../fonts/creaturepunk/Creaturepunk.ttf
python3 build.py out.ttf    # or somewhere else, to compare first
```

R, E, A, T, P, N and K (and the logo C, U and K alternates) are traced from
the lettering; `defs.py` builds every other glyph from pieces of those.
`python3 preview.py out.preview.png A,B,C` draws glyphs on the design grid
(units: cap height 44, baseline 0, slant removed). In `defs.py`, change a glyph
by redefining it at the end of the file: the edge noise comes from one seeded
stream, so editing a definition in place shifts every glyph defined after it.
