"""The logo's own C, U and K, traced from creaturepunk-logo.png.

They are the swash alternates (`swsh`/`ss01`), so the logo can still be set.
Every default glyph is drawn in scrawl.py.
"""
from glyphs import *

G['C.swsh'] = canon('C', k=1.1, base=77)
G['U.swsh'] = src('U')
G['K.swsh'] = src('K')
