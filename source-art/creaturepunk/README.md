# Creaturepunk source lettering

`creaturepunk-logo.png` is the lettering the Creaturepunk font was traced
from. The font file, `fonts/creaturepunk/Creaturepunk.ttf`, is the source
now: edit it in `docs/creaturepunk-font-demo.html`.

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
