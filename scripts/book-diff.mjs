#!/usr/bin/env bun
// book-diff.mjs — prove a plugin.js change leaves real books' rendered HTML alone.
//
// Renders every chapter of one or more books (and optionally this repo's own
// design guide) through Gutterpress's renderer twice — once with a BASE
// plugin, once with a HEAD plugin — normalises the expected noise, and diffs.
//
//   bun scripts/book-diff.mjs --base main --book ../dc-op-manual/field-guide \
//        --book ../dc-op-manual/SysOps --design-guide --out /tmp/book-diff-report
//
//   --base <ref|path>   REQUIRED. A git ref (`main`, `v1.1.5`, a SHA), read with
//                       `git show <ref>:plugin.js`; or a path to a plugin.js
//                       (or a directory containing one).
//   --head <path>       The plugin under test (default ./plugin.js).
//   --book <dir>        A book directory containing manifest.yaml. Repeatable.
//   --design-guide      Also render this repo's design-guide/.
//   --out <dir>         Report directory (default: a fresh temp dir). Must be
//                       OUTSIDE this repository: books are private.
//   --context <n>       Lines of diff context (default 3).
//
// Exit code: 0 everything identical, 1 diffs (or a render error that differs),
// 2 usage / setup error.
//
// Private book content must never reach this public repo: the reports contain
// book text, so this script refuses an --out inside the repository.
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { createMarkdownRenderer } from "gutterpress/render";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

const USAGE = `Usage: bun scripts/book-diff.mjs --base <git-ref-or-plugin-path> [--head <plugin-path>] \\
         --book <book-dir> [--book <book-dir> …] [--design-guide] [--out <report-dir>] [--context <n>]`;

function fail(message, code = 2) {
  console.error(`book-diff: ${message}`);
  process.exit(code);
}

function parseArgs(argv) {
  const opts = { books: [], designGuide: false, head: "./plugin.js", context: 3 };
  const need = (i, flag) => {
    if (i + 1 >= argv.length) fail(`${flag} needs a value\n${USAGE}`);
    return argv[i + 1];
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const [flag, inline] = a.startsWith("--") && a.includes("=") ? [a.slice(0, a.indexOf("=")), a.slice(a.indexOf("=") + 1)] : [a, undefined];
    const value = () => {
      if (inline !== undefined) return inline;
      const v = need(i, flag);
      i++;
      return v;
    };
    if (flag === "--base") opts.base = value();
    else if (flag === "--head") opts.head = value();
    else if (flag === "--book") opts.books.push(value());
    else if (flag === "--out") opts.out = value();
    else if (flag === "--context") opts.context = Number(value());
    else if (flag === "--design-guide") opts.designGuide = true;
    else if (flag === "-h" || flag === "--help") {
      console.log(USAGE);
      process.exit(0);
    } else fail(`unknown argument ${a}\n${USAGE}`);
  }
  if (!opts.base) fail(`--base is required\n${USAGE}`);
  if (!opts.books.length && !opts.designGuide) fail(`nothing to render: pass --book <dir> and/or --design-guide\n${USAGE}`);
  if (!Number.isInteger(opts.context) || opts.context < 0) fail("--context must be a non-negative integer");
  return opts;
}

const isInside = (child, parent) => {
  const rel = path.relative(parent, child);
  return rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel));
};

// ---------------------------------------------------------------------------
// Loading the two plugins
// ---------------------------------------------------------------------------

/**
 * Resolve a `--base` / `--head` spec to a loaded plugin module.
 * An existing path is imported in place; anything else is a git ref whose
 * plugin.js is staged into a temp dir next to a `type: module` package.json
 * (plugin.js imports nothing — docs/developing.md — so the file is enough).
 */
async function loadPlugin(spec, label, stageRoot) {
  let file;
  let describe;
  const asPath = path.resolve(spec);
  if (existsSync(asPath)) {
    file = statSync(asPath).isDirectory() ? path.join(asPath, "plugin.js") : asPath;
    if (!existsSync(file)) fail(`${label}: no plugin.js in ${asPath}`);
    describe = `path ${file}`;
  } else {
    let source;
    let sha;
    try {
      source = execFileSync("git", ["-C", ROOT, "show", `${spec}:plugin.js`], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024, stdio: ["ignore", "pipe", "pipe"] });
      sha = execFileSync("git", ["-C", ROOT, "rev-parse", "--short", `${spec}^{commit}`], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
    } catch (e) {
      fail(`${label}: "${spec}" is neither an existing path nor a git ref with a plugin.js (${String(e.stderr ?? e.message).trim().split("\n")[0]})`);
    }
    if (/^\s*import\s[^(]|\brequire\(/m.test(source)) {
      fail(`${label}: plugin.js at ${spec} has imports; book-diff stages only plugin.js. Pass a checked-out path instead.`);
    }
    const dir = path.join(stageRoot, label);
    mkdirSync(dir, { recursive: true });
    writeFileSync(path.join(dir, "package.json"), '{ "type": "module" }\n');
    file = path.join(dir, "plugin.js");
    writeFileSync(file, source);
    describe = `git ${spec} (${sha}) plugin.js`;
  }
  const mod = await import(pathToFileURL(file).href);
  if (typeof mod.default !== "function") fail(`${label}: ${file} has no default-exported plugin function`);
  return { label, describe, mod, markers: mod.markers };
}

/** Mirror what Gutterpress's loader hands the renderer for an extension: plugin, options AND the `markers` export. */
const asLoaded = (p) => ({ name: "gp-dimm-city", plugin: p.mod.default, options: {}, markers: p.mod.markers });

// ---------------------------------------------------------------------------
// Book manifests
// ---------------------------------------------------------------------------

async function readYaml(file) {
  const text = readFileSync(file, "utf8");
  try {
    // `yaml` is gutterpress's own dependency (hoisted next to it); not a dependency of this package.
    const { parse } = await import("yaml");
    return parse(text);
  } catch (e) {
    if (e?.code !== "ERR_MODULE_NOT_FOUND" && !/Cannot find (module|package)/.test(String(e?.message))) throw e;
    return parseManifestMinimal(text);
  }
}

/** Fallback reader: only `extensions:` and `source.files` lists, which is all this script needs. */
function parseManifestMinimal(text) {
  const lines = text.replace(/^[ \t]*#.*$/gm, "").split("\n");
  const unquote = (s) => s.trim().replace(/^(["'])(.*)\1$/, "$2");
  const list = (startIdx, baseIndent) => {
    const items = [];
    for (let i = startIdx; i < lines.length; i++) {
      const m = lines[i].match(/^(\s*)-\s+(.*\S)\s*$/);
      if (m && m[1].length >= baseIndent) items.push(unquote(m[2]));
      else if (lines[i].trim() && !/^\s*-/.test(lines[i])) break;
    }
    return items;
  };
  const out = {};
  lines.forEach((line, i) => {
    if (/^extensions:\s*$/.test(line)) out.extensions = list(i + 1, 0);
    if (/^source:\s*$/.test(line)) {
      for (let j = i + 1; j < lines.length && (/^\s/.test(lines[j]) || !lines[j].trim()); j++) {
        if (/^\s+files:\s*$/.test(lines[j])) out.source = { files: list(j + 1, 0) };
      }
    }
  });
  return out;
}

/** The chapters Gutterpress would render: `source.files` in order, else every `.md` sorted (minus `.online.md` siblings). */
function chapterList(dir, manifest) {
  const configured = manifest?.source?.files;
  if (Array.isArray(configured) && configured.length) return configured.map(String);
  return readdirSync(dir)
    .filter((f) => f.endsWith(".md") && !f.endsWith(".online.md"))
    .sort();
}

/** Names of the manifest's extensions, whichever shape they are written in. */
function extensionNames(manifest) {
  return (manifest?.extensions ?? []).map((e) => {
    if (typeof e === "string") return e;
    if (e && typeof e === "object") return e.use ?? e.name ?? e.path ?? JSON.stringify(e);
    return String(e);
  });
}

/** Does this extension entry refer to the Dimm City package (a pin, or the working copy `../`)? */
const isDimmCity = (name) => /(^|\/)gp-dimm-city(@|$|\/)/.test(name) || /^(\.\.\/?|\.\.\/\.\.\/?)$/.test(name.trim());

// ---------------------------------------------------------------------------
// Normalisation
// ---------------------------------------------------------------------------

/**
 * Attribute names dropped from BOTH sides before diffing. Explicit, and printed
 * in the report. Core adds these to blocks it handles itself; they differ
 * between a hand-written plugin and a declared marker and say nothing about
 * what the author sees.
 */
function droppedAttributes(markerNames) {
  const literal = ["data-source-range", "data-source-line", "data-label"];
  const names = [...markerNames].sort();
  const set = new Set([...literal, ...names.map((n) => `data-${n}`)]);
  const patterns = [
    'data-source-range="…"'.padEnd(30) + "(core: source mapping)",
    'data-source-line="…"'.padEnd(30) + "(markdown-it-source-map)",
    'data-label="…"'.padEnd(30) + "(declared markers: the marker's label attribute)",
    ...names.map((n) => `data-${n}="…"`.padEnd(30) + "(declared marker @" + n + ": its own name/variant)"),
  ];
  return { set, patterns };
}

const TAG_RE = /<!--[\s\S]*?-->|<(\/?)([a-zA-Z][\w:-]*)((?:\s+[^\s"'>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'>]+))?)*)\s*(\/?)>/g;
const ATTR_RE = /([^\s"'>\/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+)))?/g;

/**
 * html → one tag or text run per line, with:
 *  - dropped attributes removed (counted into `dropped`),
 *  - attributes sorted by name,
 *  - class tokens sorted (the class SET is still compared exactly),
 *  - whitespace between tags removed; text whitespace collapsed (verbatim inside <pre>).
 */
function normalise(html, drop, dropped) {
  const lines = [];
  let pre = 0;
  let last = 0;
  const pushText = (text) => {
    if (pre > 0) {
      if (text) lines.push(...text.split("\n"));
      return;
    }
    const t = text.replace(/\s+/g, " ").trim();
    if (t) lines.push(t);
  };
  for (const m of html.matchAll(TAG_RE)) {
    pushText(html.slice(last, m.index));
    last = m.index + m[0].length;
    if (m[0].startsWith("<!--")) {
      lines.push(m[0].replace(/\s+/g, " "));
      continue;
    }
    const [, closing, tagName, attrText, selfClose] = m;
    const tag = tagName.toLowerCase();
    if (tag === "pre") pre += closing ? -1 : 1;
    if (pre < 0) pre = 0;
    if (closing) {
      lines.push(`</${tag}>`);
      continue;
    }
    const attrs = [];
    for (const a of attrText.matchAll(ATTR_RE)) {
      const name = a[1].toLowerCase();
      const value = a[2] ?? a[3] ?? a[4];
      if (drop.has(name)) {
        dropped.set(name, (dropped.get(name) ?? 0) + 1);
        continue;
      }
      attrs.push([name, name === "class" && value !== undefined ? value.trim().split(/\s+/).filter(Boolean).sort().join(" ") : value]);
    }
    attrs.sort((x, y) => (x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0));
    const rendered = attrs.map(([n, v]) => (v === undefined ? n : v.includes('"') ? `${n}='${v}'` : `${n}="${v}"`));
    lines.push(`<${[tag, ...rendered].join(" ")}${selfClose ? " /" : ""}>`);
  }
  pushText(html.slice(last));
  return lines;
}

// ---------------------------------------------------------------------------
// Unified diff (Myers, with a size cap)
// ---------------------------------------------------------------------------

const MAX_D = 3000;

/** Edit script between a and b as [op, line] pairs; op is " ", "-" or "+". */
function editScript(a, b) {
  let pre = 0;
  while (pre < a.length && pre < b.length && a[pre] === b[pre]) pre++;
  let suf = 0;
  while (suf < a.length - pre && suf < b.length - pre && a[a.length - 1 - suf] === b[b.length - 1 - suf]) suf++;
  const A = a.slice(pre, a.length - suf);
  const B = b.slice(pre, b.length - suf);
  const ops = [];
  for (let i = 0; i < pre; i++) ops.push([" ", a[i]]);
  const mid = myers(A, B);
  if (mid) ops.push(...mid);
  else {
    // Pathologically different: show the middle as one replacement rather than burn memory.
    for (const l of A) ops.push(["-", l]);
    for (const l of B) ops.push(["+", l]);
  }
  for (let i = a.length - suf; i < a.length; i++) ops.push([" ", a[i]]);
  return { ops, capped: mid === null };
}

function myers(A, B) {
  const N = A.length;
  const M = B.length;
  if (N === 0) return B.map((l) => ["+", l]);
  if (M === 0) return A.map((l) => ["-", l]);
  const max = Math.min(N + M, MAX_D);
  const offset = max + 1;
  let v = new Int32Array(2 * max + 3);
  const trace = [];
  let found = -1;
  for (let d = 0; d <= max && found < 0; d++) {
    trace.push(v.slice());
    for (let k = -d; k <= d; k += 2) {
      let x = k === -d || (k !== d && v[offset + k - 1] < v[offset + k + 1]) ? v[offset + k + 1] : v[offset + k - 1] + 1;
      let y = x - k;
      while (x < N && y < M && A[x] === B[y]) {
        x++;
        y++;
      }
      v[offset + k] = x;
      if (x >= N && y >= M) {
        found = d;
        break;
      }
    }
  }
  if (found < 0) return null;
  const ops = [];
  let x = N;
  let y = M;
  for (let d = found; d > 0; d--) {
    const pv = trace[d];
    const k = x - y;
    const prevK = k === -d || (k !== d && pv[offset + k - 1] < pv[offset + k + 1]) ? k + 1 : k - 1;
    const prevX = pv[offset + prevK];
    const prevY = prevX - prevK;
    while (x > prevX && y > prevY) {
      ops.push([" ", A[x - 1]]);
      x--;
      y--;
    }
    if (x === prevX) ops.push(["+", B[y - 1]]);
    else ops.push(["-", A[x - 1]]);
    x = prevX;
    y = prevY;
  }
  while (x > 0 && y > 0) {
    ops.push([" ", A[x - 1]]);
    x--;
    y--;
  }
  return ops.reverse();
}

function unifiedDiff(a, b, labelA, labelB, context) {
  const { ops, capped } = editScript(a, b);
  if (!ops.some(([op]) => op !== " ")) return { text: "", changed: 0, capped };
  const out = [`--- ${labelA}`, `+++ ${labelB}`];
  if (capped) out.push(`# diff too large for line alignment; the differing region is shown as a full replacement`);
  // Group into hunks with `context` lines around each change.
  const changeIdx = ops.map(([op], i) => (op !== " " ? i : -1)).filter((i) => i >= 0);
  let changed = changeIdx.length;
  let h = 0;
  while (h < changeIdx.length) {
    let start = Math.max(0, changeIdx[h] - context);
    let end = Math.min(ops.length, changeIdx[h] + context + 1);
    while (h + 1 < changeIdx.length && changeIdx[h + 1] - context <= end) {
      h++;
      end = Math.min(ops.length, changeIdx[h] + context + 1);
    }
    h++;
    let aLine = 1;
    let bLine = 1;
    for (let i = 0; i < start; i++) {
      if (ops[i][0] !== "+") aLine++;
      if (ops[i][0] !== "-") bLine++;
    }
    const slice = ops.slice(start, end);
    const aCount = slice.filter(([op]) => op !== "+").length;
    const bCount = slice.filter(([op]) => op !== "-").length;
    out.push(`@@ -${aLine},${aCount} +${bLine},${bCount} @@`);
    for (const [op, line] of slice) out.push(op + line);
  }
  return { text: out.join("\n") + "\n", changed, capped };
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function renderChapter(loaded, file) {
  try {
    const md = createMarkdownRenderer([loaded]);
    const env = {};
    const html = md.render(readFileSync(file, "utf8"), env);
    return { html, warnings: env.layoutWarnings ?? [] };
  } catch (e) {
    return { html: "", warnings: [], error: String(e?.stack ?? e).split("\n").slice(0, 4).join("\n") };
  }
}

const warningKey = (w) => JSON.stringify({ line: w.line, type: w.type, marker: w.marker, message: w.message });
const countBy = (arr) => arr.reduce((m, x) => m.set(x, (m.get(x) ?? 0) + 1), new Map());

/** Warnings present on one side only (multiset difference), as readable strings. */
function warningDelta(baseW, headW) {
  const b = countBy(baseW.map(warningKey));
  const h = countBy(headW.map(warningKey));
  const only = (from, other) => {
    const res = [];
    for (const [k, n] of from) for (let i = 0; i < n - (other.get(k) ?? 0); i++) res.push(JSON.parse(k));
    return res;
  };
  return { removed: only(b, h), added: only(h, b) };
}

const fmtWarning = (w) => `line ${w.line ?? "?"} [${w.type ?? "?"}${w.marker ? ` @${w.marker}` : ""}] ${w.message}`;
const safeName = (s) => s.replace(/\.md$/i, "").replace(/[^\w.-]+/g, "_");

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv.slice(2));

  const outDir = path.resolve(opts.out ?? mkdtempSync(path.join(os.tmpdir(), "book-diff-")));
  if (isInside(outDir, ROOT)) {
    fail(`--out ${outDir} is inside this repository. Book content is private and reports quote it: pick a directory outside ${ROOT}.`);
  }
  mkdirSync(outDir, { recursive: true });

  const stage = mkdtempSync(path.join(os.tmpdir(), "book-diff-plugins-"));
  try {
    const base = await loadPlugin(opts.base, "base", stage);
    const head = await loadPlugin(opts.head, "head", stage);

    const markerNames = new Set([...Object.keys(base.markers ?? {}), ...Object.keys(head.markers ?? {})]);
    const { set: dropSet, patterns } = droppedAttributes(markerNames);

    // The targets: each book dir, then the design guide.
    const targets = opts.books.map((b) => ({ kind: "book", dir: path.resolve(b) }));
    if (opts.designGuide) targets.push({ kind: "design-guide", dir: path.join(ROOT, "design-guide") });

    const report = [];
    const log = (line = "") => report.push(line);

    log("book-diff");
    log(`  base : ${base.describe}${base.markers ? `  (markers export: ${Object.keys(base.markers).length})` : "  (no markers export)"}`);
    log(`  head : ${head.describe}${head.markers ? `  (markers export: ${Object.keys(head.markers).length})` : "  (no markers export)"}`);
    log(`  renderer: gutterpress ${gutterpressVersion()}`);
    log(`  report dir: ${outDir}`);
    log();
    log("Normalisation applied to both sides before diffing:");
    log("  - attributes DROPPED (patterns):");
    for (const p of patterns) log(`      ${p}`);
    log("  - attributes within each tag are SORTED by name");
    log("  - class tokens within class=\"…\" are SORTED (class ORDER is normalised; the class SET is compared exactly)");
    log("  - whitespace between tags is removed; text whitespace is collapsed (kept verbatim inside <pre>)");
    log("  - compared separately, not normalised: env.layoutWarnings (line, type, marker, message)");
    log();

    const summary = { books: [], totals: { chapters: 0, identical: 0, differing: 0, warningDeltas: 0, errors: 0 } };
    const usedNames = new Set();

    for (const target of targets) {
      const manifestFile = path.join(target.dir, "manifest.yaml");
      if (!existsSync(manifestFile)) fail(`${target.dir} has no manifest.yaml`);
      const manifest = await readYaml(manifestFile);
      const chapters = chapterList(target.dir, manifest);
      const extensions = extensionNames(manifest);
      const skipped = extensions.filter((e) => !isDimmCity(e));
      const missing = chapters.filter((c) => !existsSync(path.join(target.dir, c)));
      if (missing.length) fail(`${manifestFile} lists chapters that do not exist: ${missing.join(", ")}`);

      let name = target.kind === "design-guide" ? "design-guide" : path.basename(target.dir);
      for (let n = 2; usedNames.has(name); n++) name = `${path.basename(target.dir)}-${n}`;
      usedNames.add(name);
      const bookOut = path.join(outDir, name);
      rmSync(bookOut, { recursive: true, force: true });
      mkdirSync(bookOut, { recursive: true });

      const droppedBase = new Map();
      const droppedHead = new Map();
      const entry = { name, dir: target.dir, chapters: chapters.length, identical: 0, differing: [], warningDeltas: [], errors: [] };

      for (const chapter of chapters) {
        const file = path.join(target.dir, chapter);
        const b = renderChapter(asLoaded(base), file);
        const h = renderChapter(asLoaded(head), file);
        const bLines = b.error ? [`RENDER ERROR: ${b.error}`] : normalise(b.html, dropSet, droppedBase);
        const hLines = h.error ? [`RENDER ERROR: ${h.error}`] : normalise(h.html, dropSet, droppedHead);
        if (b.error || h.error) entry.errors.push({ chapter, base: b.error, head: h.error });

        const diff = unifiedDiff(bLines, hLines, `base/${chapter}`, `head/${chapter}`, opts.context);
        const wd = warningDelta(b.warnings, h.warnings);
        const warningsDiffer = wd.removed.length > 0 || wd.added.length > 0;

        let diffFile = null;
        if (diff.changed) {
          diffFile = path.join(bookOut, `${safeName(chapter)}.diff`);
          writeFileSync(diffFile, diff.text);
        }
        if (warningsDiffer) {
          const lines = [`Layout warnings: base ${b.warnings.length}, head ${h.warnings.length}`, ""];
          for (const w of wd.removed) lines.push(`- ${fmtWarning(w)}`);
          for (const w of wd.added) lines.push(`+ ${fmtWarning(w)}`);
          writeFileSync(path.join(bookOut, `${safeName(chapter)}.warnings.txt`), lines.join("\n") + "\n");
        }
        if (!diff.changed && !warningsDiffer) entry.identical++;
        else {
          if (diff.changed) entry.differing.push({ chapter, changedLines: diff.changed, diffFile });
          if (warningsDiffer) entry.warningDeltas.push({ chapter, base: b.warnings.length, head: h.warnings.length, removed: wd.removed.map(fmtWarning), added: wd.added.map(fmtWarning) });
        }
        entry.baseWarnings = (entry.baseWarnings ?? 0) + b.warnings.length;
        entry.headWarnings = (entry.headWarnings ?? 0) + h.warnings.length;
      }

      const diffChapters = new Set([...entry.differing.map((d) => d.chapter), ...entry.warningDeltas.map((d) => d.chapter)]);
      log(`== ${target.kind === "design-guide" ? "design guide" : "book"}: ${name}  (${target.dir})`);
      log(`   extensions: ${extensions.join(", ") || "(none)"}`);
      if (skipped.length) log(`   NOT exercised (only the Dimm City plugin is swapped; others are not loadable through gutterpress's public API): ${skipped.join(", ")}`);
      log(`   chapters compared: ${entry.chapters}   identical: ${entry.chapters - diffChapters.size}   differing: ${diffChapters.size}`);
      log(`   layout warnings: base ${entry.baseWarnings}, head ${entry.headWarnings}   chapters with a warning delta: ${entry.warningDeltas.length}`);
      log(`   attributes dropped by normalisation (base / head): ${formatDropped(droppedBase, droppedHead)}`);
      for (const d of entry.differing) log(`   DIFF  ${d.chapter}  (${d.changedLines} changed lines)  -> ${path.relative(outDir, d.diffFile)}`);
      for (const d of entry.warningDeltas) {
        log(`   WARN  ${d.chapter}  (base ${d.base}, head ${d.head})  -> ${name}/${safeName(d.chapter)}.warnings.txt`);
        for (const w of d.removed) log(`           - ${w}`);
        for (const w of d.added) log(`           + ${w}`);
      }
      for (const e of entry.errors) log(`   ERROR ${e.chapter}: base ${e.base ? "threw" : "ok"}, head ${e.head ? "threw" : "ok"}`);
      log();

      entry.identical = entry.chapters - diffChapters.size;
      summary.books.push(entry);
      summary.totals.chapters += entry.chapters;
      summary.totals.identical += entry.identical;
      summary.totals.differing += diffChapters.size;
      summary.totals.warningDeltas += entry.warningDeltas.length;
      summary.totals.errors += entry.errors.length;
    }

    const t = summary.totals;
    log(`TOTAL: ${t.chapters} chapters compared, ${t.identical} identical, ${t.differing} differing, ${t.warningDeltas} with warning deltas, ${t.errors} render errors`);
    log(t.differing === 0 ? "RESULT: identical" : "RESULT: DIFFERENCES FOUND");

    const text = report.join("\n") + "\n";
    writeFileSync(path.join(outDir, "report.txt"), text);
    writeFileSync(path.join(outDir, "summary.json"), JSON.stringify({ base: base.describe, head: head.describe, droppedAttributePatterns: patterns, ...summary }, null, 2) + "\n");
    process.stdout.write(text);
    process.exitCode = t.differing === 0 ? 0 : 1;
  } finally {
    rmSync(stage, { recursive: true, force: true });
  }
}

function formatDropped(b, h) {
  const names = [...new Set([...b.keys(), ...h.keys()])].sort();
  if (!names.length) return "none";
  return names.map((n) => `${n} ${b.get(n) ?? 0}/${h.get(n) ?? 0}`).join(", ");
}

function gutterpressVersion() {
  try {
    const pkg = path.join(ROOT, "node_modules", "gutterpress", "package.json");
    return JSON.parse(readFileSync(pkg, "utf8")).version;
  } catch {
    return "(unknown)";
  }
}

main().catch((e) => fail(String(e?.stack ?? e)));
