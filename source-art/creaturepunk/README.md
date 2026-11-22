# Creaturepunk source

`fonts/creaturepunk/Creaturepunk.ttf` is the working source: edit it in
`docs/creaturepunk-font-demo.html`. The Python generator here is the
deterministic reset: it rebuilds the same `.ttf` every time.

## Edit the font

1. Serve the repo root with any static server (for example `bunx serve .`)
   and open `/docs/creaturepunk-font-demo.html`. The page loads the font from
   `fonts/creaturepunk/`. Opened straight from disk, it asks you to open the
   `.ttf` instead.
2. Under *Edit glyphs*, pick a glyph, drag its points and set its side
   bearings. The whole page redraws in the edited font.
3. Click *Download Creaturepunk.ttf* and replace
   `fonts/creaturepunk/Creaturepunk.ttf` with the download.

The editor changes outlines and spacing only; names, licence and line
metrics are copied unchanged.

## Reset the font from the generator

**Running it overwrites every hand edit made in the page.**

```sh
pip install fonttools numpy pillow scipy potracer
python3 build.py            # writes ../../fonts/creaturepunk/Creaturepunk.ttf
python3 build.py out.ttf    # or somewhere else, to compare first
cd ../.. && python3 scripts/heading-metrics.py   # then refresh the heading widths in plugin.js
```

How the glyphs are made:

- `scrawl.py` draws every default glyph as brush strokes: a centre line with
  wandering pressure, a sloppy hand (jittered points, ends that overshoot
  their joins) and ends that are blunt, pointed, or a talon that hooks as it
  tapers. Bars carry fangs; stems end in spikes.
- `feral.py` then damages them: claw rakes, bite marks with fang punctures,
  drips, chewed edges, and a tilt and baseline wobble per glyph. The `FERAL`
  table says which glyph gets what.

Every glyph draws from its own random stream, seeded by its name, so changing
one glyph leaves the others as they are. `python3 preview.py out.preview.png
A,B,C` draws glyphs on the design grid (units: cap height 44, baseline 0,
slant removed).
