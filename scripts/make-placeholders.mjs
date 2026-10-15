#!/usr/bin/env node
// Regenerates the guide's placeholder art in design-guide/img/ with ImageMagick.
//
//   node scripts/make-placeholders.mjs        (needs `convert`, ImageMagick 6 or 7's `magick`)
//
// One card (300x340) and one portrait (600x800) per specialty, a 640x360
// banner for Augmerc, and three generic stand-ins (Lil Thump, Portrait,
// Street Sign). Every file is OPAQUE: a flat dark ground in the specialty's own
// `--<name>-dark`, its `--<name>-mid` silhouette and texture, an accent rule,
// and the name in the bold display face. They exist so the guide builds offline
// and so that its PDF/X output keeps live text: an image with an alpha channel
// makes Ghostscript flatten the whole page into one bitmap (see README, "Art
// must be opaque"). Colours are read from the stylesheets, so a retuned token
// shows up the next time this runs. Flat shapes keep each file under ~30 KB.

import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const outDir = join(root, 'design-guide', 'img');
const FONT = join(root, 'fonts', 'tomorrow', 'tomorrow-700.ttf');

// Token table: every `--name: #hex | var(--other)` in the two token sheets.
const tokens = new Map();
for (const f of ['styles/dc-palette.css', 'styles/dc-identity.css']) {
  for (const m of readFileSync(join(root, f), 'utf8').matchAll(/(--[a-z0-9-]+):\s*([^;]+);/g)) {
    if (!tokens.has(m[1])) tokens.set(m[1], m[2].trim());
  }
}
function token(name) {
  let v = tokens.get(name);
  if (!v) throw new Error(`no token ${name}`);
  const alias = v.match(/^var\((--[a-z0-9-]+)\)/);
  if (alias) return token(alias[1]);
  return v.match(/^#[0-9a-f]{6}/i)[0].toLowerCase();
}
const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const hex = (c) => '#' + c.map((x) => Math.round(x).toString(16).padStart(2, '0')).join('');
const mix = (a, b, pct) => hex(rgb(a).map((x, i) => (x * (100 - pct) + rgb(b)[i] * pct) / 100));

const CREAM = token('--paper-cream');

const SPECIALTIES = {
  augmerc: 'slash',
  proxy: 'arcs',
  streetwarden: 'hazard',
  gutterdruid: 'spores',
  cybersurgeon: 'crosses',
  wirephreak: 'scan',
  technosorcerer: 'rings',
  etherlock: 'rays',
  dualist: 'split',
  generalist: 'chevrons',
};

// One image. `pattern` names the ground texture; the silhouette is a
// head and shoulders in the mid tone with an accent rim.
function draw({ file, w, h, name, dark, mid, accent, pattern }) {
  const u = w / 300; // everything scales from the 300px card
  const tex = mix(dark, mid, 38);
  const plateH = Math.round(h * 0.17);
  const cx = w / 2;
  const headR = Math.round(h * 0.13);
  const headY = Math.round(h * 0.34);
  const shoulderY = Math.round(h * 0.78);
  const cmds = [];
  const stroke = (c, wd) => cmds.push('-stroke', c, '-strokewidth', String(wd), '-fill', 'none');
  const fill = (c) => cmds.push('-stroke', 'none', '-fill', c);
  const line = (x1, y1, x2, y2) => cmds.push('-draw', `line ${x1},${y1} ${x2},${y2}`);

  // 1. texture, no antialiasing (crisp ink, small file)
  cmds.push('+antialias');
  const step = Math.round(26 * u);
  stroke(tex, Math.max(2, Math.round(3 * u)));
  if (pattern === 'slash') for (let x = -h; x < w; x += step) line(x, h, x + h, 0);
  else if (pattern === 'scan') for (let y = step / 2; y < h; y += step / 2) line(0, y, w, y);
  else if (pattern === 'hazard') for (let x = -h; x < w; x += step * 1.4) line(x, 0, x + h, h);
  else if (pattern === 'chevrons')
    for (let y = 0; y < h; y += step) for (let x = 0; x < w; x += 2 * step) {
      line(x, y + step / 2, x + step, y);
      line(x + step, y, x + 2 * step, y + step / 2);
    }
  else if (pattern === 'crosses')
    for (let y = step / 2; y < h; y += step) for (let x = step / 2; x < w; x += step) {
      line(x - 4 * u, y, x + 4 * u, y);
      line(x, y - 4 * u, x, y + 4 * u);
    }
  else if (pattern === 'spores') {
    fill(tex);
    let row = 0;
    for (let y = step / 2; y < h; y += step * 0.8, row++)
      for (let x = (row % 2) * step * 0.6; x < w; x += step * 1.2) cmds.push('-draw', `circle ${x},${y} ${x + 4 * u},${y}`);
  } else if (pattern === 'arcs')
    for (let r = step * 1.5; r < w + h; r += step * 1.5) cmds.push('-draw', `circle ${w},${h} ${w + r},${h}`);
  else if (pattern === 'rings')
    for (let r = step * 1.6; r < w + h; r += step * 1.6) cmds.push('-draw', `circle ${cx},${headY} ${cx + r},${headY}`);
  else if (pattern === 'rays')
    for (let a = 0; a < 360; a += 12) {
      const rad = (a * Math.PI) / 180;
      line(cx, headY, cx + Math.cos(rad) * (w + h), headY + Math.sin(rad) * (w + h));
    }
  else if (pattern === 'split') {
    fill(mix(dark, mid, 22));
    cmds.push('-draw', `polygon ${w * 0.5},0 ${w},0 ${w},${h} ${w * 0.1},${h}`);
  }

  // 2. silhouette: shoulders, neck and head. Drawn twice, first in the accent
  // with a heavy stroke, then in the mid tone on top: the accent shows only as
  // one clean rim around the whole shape, with no inner outlines.
  cmds.push('-antialias');
  const rim = Math.max(3, Math.round(4 * u));
  const shape = [
    `ellipse ${cx},${shoulderY + h * 0.02} ${w * 0.36},${h * 0.2} 180,360`,
    `rectangle ${cx - headR * 0.45},${headY + headR * 0.7} ${cx + headR * 0.45},${shoulderY - h * 0.15}`,
    `circle ${cx},${headY} ${cx + headR},${headY}`,
  ];
  cmds.push('-fill', accent, '-stroke', accent, '-strokewidth', String(rim * 2));
  for (const d of shape) cmds.push('-draw', d);
  cmds.push('-fill', mid, '-stroke', 'none');
  for (const d of shape) cmds.push('-draw', d);

  // 3. name plate: the dark ground again, an accent rule, the name in bold caps
  fill(dark);
  cmds.push('-stroke', 'none', '-draw', `rectangle 0,${h - plateH} ${w},${h}`);
  fill(accent);
  cmds.push('-draw', `rectangle 0,${h - plateH} ${w},${h - plateH + Math.max(4, Math.round(5 * u))}`);

  const label = [
    '(', '-background', 'none', '-fill', CREAM, '-font', FONT, '-size', `${Math.round(w * 0.88)}x${Math.round(plateH * 0.52)}`,
    `label:${name.toUpperCase()}`, ')',
    '-gravity', 'south', '-geometry', `+0+${Math.round(plateH * 0.2)}`, '-composite',
  ];

  const bin = process.env.IM_BIN || 'convert';
  execFileSync(bin, [
    '-size', `${w}x${h}`, `xc:${dark}`, ...cmds, ...label,
    '-alpha', 'off', '-strip', '-define', 'png:color-type=2', '-define', 'png:compression-level=9',
    `PNG24:${join(outDir, file)}`,
  ]);
  console.log(`${file}  ${w}x${h}`);
}

for (const [spec, pattern] of Object.entries(SPECIALTIES)) {
  const name = spec[0].toUpperCase() + spec.slice(1);
  const c = { dark: token(`--${spec}-dark`), mid: token(`--${spec}-mid`), accent: token(`--${spec}-accent`), pattern };
  draw({ file: `specialty-${spec}-card.png`, w: 300, h: 340, name, ...c });
  draw({ file: `specialty-${spec}-art.png`, w: 600, h: 800, name, ...c });
  if (spec === 'augmerc') draw({ file: `specialty-${spec}-wide.png`, w: 640, h: 360, name, ...c });
}

// Generic stand-ins for a character portrait, a vignette and a sign.
const generic = { dark: token('--ink-smoke'), mid: token('--ink-dark'), accent: token('--brand-magenta-deep'), pattern: 'slash' };
draw({ file: 'placeholder-lil-thump.png', w: 600, h: 400, name: 'Lil Thump', ...generic });
draw({ file: 'placeholder-portrait.png', w: 600, h: 400, name: 'Portrait', ...generic });
draw({ file: 'placeholder-street-sign.png', w: 600, h: 800, name: 'Street Sign', ...generic, pattern: 'hazard' });
