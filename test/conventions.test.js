// conventions.test.js — the rules Gutterpress's extension template calls
// load-bearing, made executable for this package:
//   - one prefix (`dc-`), and never `gp-`, which belongs to Gutterpress core;
//   - never import from `gutterpress` (or anything else) at runtime — the
//     plugin is a self-contained markdown-it plugin;
//   - the CSS may READ core's hooks (`.gp-columns-2`, `--gp-content-h`, …)
//     but may not invent `gp-` names of its own.
import { describe, expect, test } from "bun:test";
import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createMarkdownRenderer } from "gutterpress/render";

import plugin from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");
const pkg = JSON.parse(read("package.json"));

/** Core hooks the stylesheets legitimately reference. Add to this list on purpose, never by accident. */
const CORE_HOOKS_READ_BY_CSS = [
  ".gp-columns-2",
  ".gp-columns-3",
  ".gp-columns-", // attribute/prefix selectors such as [class*="gp-columns-"]
  ".gp-grid-2",
  ".gp-grid-",
  ".gp-pin",
  ".gp-bottom",
  ".gp-left",
  ".gp-bleed",
  ".gp-behind",
  ".gp-page-break",
  "--gp-column-gap", // the one core property this package is allowed to SET (page-templates.css)
  "--gp-content-h", // read only
];

function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(^|[^:])\/\/[^\n]*/g, "$1");
}

describe("plugin.js", () => {
  const src = read("plugin.js");
  const code = stripComments(src);

  test("imports nothing at runtime", () => {
    expect(code).not.toMatch(/^\s*import\s/m);
    expect(code).not.toMatch(/^\s*export\s+.*\bfrom\s/m);
    expect(code).not.toMatch(/\brequire\s*\(/);
    expect(code).not.toMatch(/\bimport\s*\(/);
  });

  test("never mentions gutterpress core's gp- prefix in code", () => {
    // The one legitimate reference is core's `gp-continued` class, which the
    // @continue handler must recognise — it is core's vocabulary, read not written.
    const hits = [...code.matchAll(/["'`][^"'`]*\bgp-[a-z0-9-]+[^"'`]*["'`]/g)].map((m) => m[0]);
    for (const h of hits) expect(h).toMatch(/gp-continued/);
  });
});

describe("what the plugin emits", () => {
  const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {} }]);
  const html = md.render(read("test/fixtures/all-macros.md"), {});
  const classes = [...new Set([...html.matchAll(/class="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/)))];

  test("every class the plugin adds carries the dc- prefix (core and author classes aside)", () => {
    // Core's own vocabulary and the author-supplied classes in the fixture.
    const notOurs = new Set([
      "page", "section", "chapter", "gp-continued",
      "page-toc", "page-credits", "page-chapter-start", "credits-colophon", "chapter-7", "augmerc", "inset", "warning",
    ]);
    const unexpected = classes.filter((c) => !c.startsWith("dc-") && !notOurs.has(c) && !/^(tier-)?(crit|hit|mixed|miss|fail|free|variable)$/.test(c));
    expect(unexpected).toEqual([]);
  });

  test("emits no gp- class of its own", () => {
    expect(classes.filter((c) => c.startsWith("gp-") && c !== "gp-continued")).toEqual([]);
  });
});

describe("stylesheets", () => {
  const sheets = pkg.gutterpress.styles;

  test("reference only the allow-listed core hooks", () => {
    for (const rel of sheets) {
      const css = stripComments(read(rel));
      const hooks = new Set([...css.matchAll(/(\.gp-[a-z0-9-]+|--gp-[a-z0-9-]+)/g)].map((m) => m[1]));
      for (const h of hooks) {
        const allowed = CORE_HOOKS_READ_BY_CSS.some((a) => h === a || (a.endsWith("-") && h.startsWith(a)));
        if (!allowed) throw new Error(`${rel} references ${h}, which is not an allow-listed core hook`);
      }
    }
  });

  test("declare custom properties only under the package's own names", () => {
    // Properties this package DECLARES (`--x:`) must not squat on core's namespace.
    for (const rel of sheets) {
      const css = stripComments(read(rel));
      const declared = [...css.matchAll(/(--gp-[a-z0-9-]+)\s*:/g)].map((m) => m[1]);
      expect(declared.filter((p) => p !== "--gp-column-gap"), `${rel} declares a core property`).toEqual([]);
    }
  });

  test("no stylesheet points outside the package", () => {
    for (const rel of sheets) {
      const css = stripComments(read(rel));
      for (const m of css.matchAll(/url\(\s*["']?([^"')]+?)["']?\s*\)/g)) {
        const target = m[1].trim();
        if (/^(data:|https?:|#)/.test(target)) continue;
        const resolved = path.posix.normalize(path.posix.join(path.posix.dirname(rel), target));
        expect(resolved.startsWith("../"), `${rel} → ${target} escapes the package`).toBe(false);
      }
      expect(css).not.toMatch(/@import\s/); // every sheet is listed in package.json instead
      expect(css).not.toMatch(/url\(\s*["']?https?:/); // a remote url() is a Gutterpress build error
    }
  });
});

describe("snippets", () => {
  test("every snippet renders through the plugin without a layout warning", () => {
    const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {} }]);
    const dir = path.join(ROOT, pkg.gutterpress.snippets);
    for (const f of readdirSync(dir)) {
      if (!statSync(path.join(dir, f)).isFile()) continue;
      const src = read(path.posix.join(pkg.gutterpress.snippets, f)).replace(/\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}/g, "$1");
      const env = {};
      const html = md.render(src, env);
      expect(env.layoutWarnings ?? [], `${f} produced layout warnings`).toEqual([]);
      expect(html.match(/^@[a-z]/gm) ?? [], `${f} left a marker unrendered`).toEqual([]);
    }
  });
});
