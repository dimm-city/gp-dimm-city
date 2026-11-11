"""Soft proof a rendered page through the press profile, with simulated press faults.

    python3 proofs/neon/softproof.py PAGE.png ICC OUT.png   (needs Pillow)

Render a page region at 300dpi first, e.g.
    pdftoppm -r 300 -f 1 -l 1 -png -singlefile .build/neon-proof.pdf page

Panels: screen | press colour (sRGB -> CGATS21_CRPC1 -> sRGB, relative
colorimetric + BPC, as the build converts) | press colour plus ink spread (each
separation grown ~0.04mm) and misregistration (cyan and magenta plates shifted
~0.08mm opposite ways, a bad-but-in-spec day on a digital press)."""
import sys

from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFilter

src, icc, out = sys.argv[1:4]
im = Image.open(src).convert("RGB")
srgb = ImageCms.createProfile("sRGB")
press = ImageCms.getOpenProfile(icc)
flags = ImageCms.Flags.BLACKPOINTCOMPENSATION
to_cmyk = ImageCms.buildTransform(srgb, press, "RGB", "CMYK", renderingIntent=1, flags=flags)
to_rgb = ImageCms.buildTransform(press, srgb, "CMYK", "RGB", renderingIntent=1, flags=flags)

cmyk = ImageCms.applyTransform(im, to_cmyk)
proof = ImageCms.applyTransform(cmyk, to_rgb)

# at 300dpi 1px = 0.085mm: grow each separation by a soft pixel (ink spread),
# then shift cyan and magenta one pixel (misregistration)
c, m, y, k = cmyk.split()
c, m, y, k = (ImageChops.lighter(ch, ch.filter(ImageFilter.GaussianBlur(0.6))) for ch in (c, m, y, k))
c = ImageChops.offset(c, 1, 1)
m = ImageChops.offset(m, -1, 0)
faults = ImageCms.applyTransform(Image.merge("CMYK", (c, m, y, k)), to_rgb)

W, H = im.size
sheet = Image.new("RGB", (W * 3 + 16, H + 26), "#111")
for i, (pane, label) in enumerate([(im, "Screen"), (proof, "Press colour (CRPC1)"), (faults, "Press colour + ink spread + misregistration")]):
    sheet.paste(pane, (i * (W + 8), 26))
    ImageDraw.Draw(sheet).text((i * (W + 8) + 6, 7), label, fill="white")
sheet.save(out)
print(out, sheet.size)
