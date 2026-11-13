"""Draw the brick wall, the page wall behind every page that names no other,
as images/brick-wall.png.

    python3 -I scripts/wall-brick.py   (from the package root; needs numpy and Pillow)

The brick is a grey line drawing (source-art/brick-bg-01.png, RGBA, a
seamless tile) multiplied into --bg (#c8c5bf), as it always was
(wall_grime.clean_brick), printed at REPEAT (1.5in) across. Here it is
resampled to DPI (300) at that same size, laid COPIES x COPIES into a tile
about 9in x 12in, and weathered by wall_grime.py like the stone walls 1-6:
grime, damp, mould, burns, damage and dried blood, dimmed to the same
average, so the book is one dim city. The joints wall_grime needs are the
drawing's long straight lines (a brick's outline) and the mortar between two
of them; the speckle and cracks on a brick's face are left out.

Everything stays periodic: the drawing is resampled from a wrapped copy, so
each repeat meets the next without a seam, and wall_grime's marks wrap.
The tile is COPIES x REPEAT wide; its height is COPIES repeats of the
drawing's own height at that width, rounded to whole px (0.06% shorter than
exact), so the bricks print at the size they always have.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wall_grime  # noqa: E402  (the clean brick, and the grime shared with walls 1-6)

ROOT = Path(__file__).resolve().parents[1]
DPI = wall_grime.DPI
REPEAT = 1.5                # in: the drawing's printed width, as it always was
COPIES = 6                  # repeats a side: 9in x 11.6in
SEED = 4207
PAD = 64                    # px of the source wrapped round it, so the resample has no edge


def resample(im, size):
    """Resize a seamless tile to `size` (Lanczos) from a copy wrapped PAD px on
    every side, so its edges are filtered with the far side's pixels."""
    W, H = im.size
    big = Image.new(im.mode, (W + 2 * PAD, H + 2 * PAD))
    for ox in (-W, 0, W):
        for oy in (-H, 0, H):
            big.paste(im, (PAD + ox, PAD + oy))
    return big.resize(size, Image.LANCZOS, box=(PAD, PAD, PAD + W, PAD + H))


def joints(dark):
    """The joints: the drawing's lines that run on along a course or up a
    head (a box mean along the line keeps them, drops the face's speckle and
    short cracks), widened to take in the mortar between a brick's outline and
    its neighbour's. Periodic, as the tile is."""
    def run(a, n, axis):
        out = np.zeros_like(a)
        for k in range(-n, n + 1):
            out += np.roll(a, k, axis)
        return out / (2 * n + 1)

    line = (dark > 0.12).astype(np.float32)
    beds = run(line, 12, 1) > 0.5                 # along a course: 25px of line
    heads = run(line, 7, 0) > 0.5                 # up a head: 15px
    j = beds | heads
    grown = j.copy()
    for dy in range(-2, 3):                       # widened 2px: over the mortar between a brick's outline and the next
        for dx in range(-2, 3):
            grown |= np.roll(j, (dy, dx), (0, 1))
    return grown.astype(np.float32)


def main():
    w = round(REPEAT * DPI)
    src = wall_grime.clean_brick(None)                      # --bg times the drawing, full size
    h = round(w * src.height / src.width)
    one = np.asarray(resample(src, (w, h)), np.float32) / 255
    alpha = Image.open(wall_grime.BRICK_SRC).getchannel("A")
    ink = Image.open(wall_grime.BRICK_SRC).convert("L")
    dark = Image.fromarray((np.asarray(alpha, np.float32) * (1 - np.asarray(ink, np.float32) / 255)).astype(np.uint8))
    dark = np.asarray(resample(dark, (w, h)), np.float32) / 255
    rgb = np.tile(one, (COPIES, COPIES, 1))
    joint = joints(np.tile(dark, (COPIES, COPIES)))
    del one, dark
    out, special = wall_grime.weather(rgb, joint, seed=SEED)
    del rgb, joint
    path = ROOT / "images/brick-wall.png"
    pal = wall_grime.save(out, special, path)
    avg = pal.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
    print(f"images/brick-wall.png  {pal.width}x{pal.height}  {pal.width / DPI:.2f}x{pal.height / DPI:.2f}in  {len(pal.getcolors())} colours  "
          f"average #{avg[0]:02x}{avg[1]:02x}{avg[2]:02x}  {path.stat().st_size / 1e6:.2f}MB", flush=True)


if __name__ == "__main__":
    main()
