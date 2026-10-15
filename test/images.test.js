// images.test.js — art must be OPAQUE.
//
// A PDF/X-1a or X-3 file has no transparency (both are PDF 1.3). When an image
// carries an alpha channel, Ghostscript flattens EVERY page that shows it into
// one raster: the page's live text, rules and vector chrome become pixels, the
// fonts drop out of the file and the text stops being searchable or sharp. The
// build only warns ("Image contains alpha channel"), so this test is the gate:
// it reads each PNG's header and fails on any alpha channel or colour-key
// transparency, with no image library and no new dependency.
//
// It covers the design guide's art (design-guide/img/, which is the fixture a
// book copies), the art this package ships (images/) and the guide's markdown,
// which may not point at a remote image: a placeholder service fails offline
// and breaks the build (the specialty portraits used to).
import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ART_DIRS = ["design-guide/img", "images"];

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const COLOR_TYPES = { 0: "grayscale", 2: "RGB", 3: "palette", 4: "grayscale + alpha", 6: "RGBA" };

function walk(dir) {
  const abs = path.join(ROOT, dir);
  if (!existsSync(abs)) return [];
  const out = [];
  for (const name of readdirSync(abs).sort()) {
    const rel = path.join(dir, name);
    if (statSync(path.join(ROOT, rel)).isDirectory()) out.push(...walk(rel));
    else out.push(rel);
  }
  return out;
}

/**
 * What a PNG says about transparency, from its chunks: the IHDR colour type
 * (4 and 6 carry an alpha channel) and any tRNS chunk (palette or colour-key
 * transparency on the other types).
 */
export function pngTransparency(buf) {
  if (buf.length < 33 || !buf.subarray(0, 8).equals(PNG_SIGNATURE)) throw new Error("not a PNG");
  const colorType = buf[25]; // 8 signature + 4 length + 4 "IHDR" + 4 width + 4 height + 1 depth, then the type
  let hasTrns = false;
  for (let i = 8; i + 8 <= buf.length; ) {
    const length = buf.readUInt32BE(i);
    const type = buf.toString("latin1", i + 4, i + 8);
    if (type === "tRNS") hasTrns = true;
    if (type === "IDAT" || type === "IEND") break; // tRNS must precede the image data
    i += 12 + length;
  }
  return { colorType, hasAlphaChannel: colorType === 4 || colorType === 6, hasTrns };
}

const files = ART_DIRS.flatMap(walk);

describe("art is opaque", () => {
  test("the art folders hold images to check", () => {
    expect(files.filter((f) => f.startsWith("design-guide/img/")).length).toBeGreaterThan(0);
  });

  test("pngTransparency reads a header (self-check on hand-built PNGs)", () => {
    const png = (colorType, extra = []) => {
      const chunk = (type, data) => {
        const b = Buffer.alloc(12 + data.length);
        b.writeUInt32BE(data.length, 0);
        b.write(type, 4, "latin1");
        Buffer.from(data).copy(b, 8);
        return b;
      };
      const ihdr = Buffer.alloc(13);
      ihdr.writeUInt32BE(1, 0);
      ihdr.writeUInt32BE(1, 4);
      ihdr[8] = 8;
      ihdr[9] = colorType;
      return Buffer.concat([PNG_SIGNATURE, chunk("IHDR", ihdr), ...extra, chunk("IDAT", []), chunk("IEND", [])]);
    };
    expect(pngTransparency(png(2)).hasAlphaChannel).toBe(false);
    expect(pngTransparency(png(6)).hasAlphaChannel).toBe(true);
    expect(pngTransparency(png(4)).hasAlphaChannel).toBe(true);
    const trns = Buffer.alloc(13);
    trns.writeUInt32BE(1, 0);
    trns.write("tRNS", 4, "latin1");
    expect(pngTransparency(png(3, [trns])).hasTrns).toBe(true);
    expect(pngTransparency(png(3)).hasTrns).toBe(false);
  });

  for (const rel of files) {
    const ext = path.extname(rel).toLowerCase();
    test(`${rel} has no alpha channel`, () => {
      if (ext === ".png") {
        const t = pngTransparency(readFileSync(path.join(ROOT, rel)));
        const why = "flatten it onto its solid background before committing (ImageMagick: convert in.png -background '#f0eee9' -alpha remove -alpha off PNG24:out.png)";
        expect(t.hasAlphaChannel, `${rel} is ${COLOR_TYPES[t.colorType]}; ${why}`).toBe(false);
        expect(t.hasTrns, `${rel} has a tRNS (transparency) chunk; ${why}`).toBe(false);
      } else {
        // JPEG has no alpha. Anything else (GIF, WebP, SVG, …) can, and this test cannot read it.
        expect([".jpg", ".jpeg"], `${rel}: use an opaque PNG or JPEG for art`).toContain(ext);
      }
    });
  }
});

describe("the design guide's markdown", () => {
  // Code samples and inline code show image syntax with made-up paths; only real markdown counts.
  const prose = (src) => src.replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm, "").replace(/`[^`\n]*`/g, "");
  const md = readdirSync(path.join(ROOT, "design-guide"))
    .filter((f) => f.endsWith(".md"))
    .sort();

  test("no image points at a remote URL (it fails offline and breaks the build)", () => {
    const remote = [];
    for (const f of md) {
      const src = prose(readFileSync(path.join(ROOT, "design-guide", f), "utf8"));
      for (const m of src.matchAll(/!\[[^\]]*\]\((https?:\/\/[^)\s]+)/g)) remote.push(`${f}: ${m[1]}`);
    }
    expect(remote).toEqual([]);
  });

  test("every local image the markdown references exists", () => {
    const missing = [];
    for (const f of md) {
      const src = prose(readFileSync(path.join(ROOT, "design-guide", f), "utf8"));
      for (const m of src.matchAll(/!\[[^\]]*\]\(([^)\s]+)/g)) {
        if (/^(https?:|data:)/.test(m[1])) continue;
        if (!existsSync(path.join(ROOT, "design-guide", m[1]))) missing.push(`${f}: ${m[1]}`);
      }
    }
    expect(missing).toEqual([]);
  });
});
