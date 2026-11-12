# Creaturepunk font source

`creaturepunk-logo.png` is the lettering the font is traced from. C, R, E, A,
T, U, P, N and K are traced from it; every other glyph is assembled in
`defs.py` from pieces of those letters, so the cut edges stay hand-made.

Rebuild the font (writes `fonts/creaturepunk/Creaturepunk.ttf` and `.woff2`)
and the demo page (`docs/creaturepunk-font-demo.html`):

```sh
pip install fonttools brotli numpy pillow scipy potracer
python3 extract.py
python3 build.py
python3 mkdemo.py ../../docs/creaturepunk-font-demo.html
```

`python3 preview.py out.preview.png A,B,C` draws glyphs on the design grid
(units: cap height 44, baseline 0, slant removed) for checking edits.
