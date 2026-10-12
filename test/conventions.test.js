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

import postcss from "postcss";
import { createMarkdownRenderer } from "gutterpress/render";

import plugin, { markers } from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");
const pkg = JSON.parse(read("package.json"));

/** Core hooks the stylesheets legitimately reference. Add to this list on purpose, never by accident. */
const CORE_HOOKS_READ_BY_CSS = [
  ".gp-columns", // what `@columns N` emits (the run itself)
  ".gp-columns-", // count classes, and attribute/prefix selectors such as [class*="gp-columns-"]
  ".gp-pin",
  ".gp-bottom",
  ".gp-left",
  ".gp-bleed",
  ".gp-behind",
  ".gp-page-break",
  ".gp-page-full-bleed", // core's `@page full-bleed`, which shares the plate geometry and named page of `.dc-full-page`
  "--gp-column-gap", // the two core hooks this package is allowed to SET, once, at :root (dc-component-defaults.css)
  "--gp-column-rule", //   and to reset on a component that wants none
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
  // The design guide rendered twice: with the plugin, and through core alone.
  // A class present only in the first render was added by the plugin — unless
  // the author wrote it on a marker line (`@specialty .augmerc`), in which
  // case it appears as `.name` somewhere in the markdown source.
  const GUIDE = path.join(ROOT, "design-guide");
  const chapters = [...read("design-guide/manifest.yaml").matchAll(/^\s*-\s*(\S+\.md)\s*$/gm)].map((m) => m[1]);
  const source = chapters.map((f) => readFileSync(path.join(GUIDE, f), "utf8")).join("\n");
  const classesOf = (md) => new Set(chapters.flatMap((f) => [...md.render(readFileSync(path.join(GUIDE, f), "utf8"), {}).matchAll(/class="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/))));
  const withPlugin = classesOf(createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {}, markers }]));
  const coreOnly = classesOf(createMarkdownRenderer([]));
  const authored = new Set([...source.matchAll(/\.([a-zA-Z][\w-]*)/g)].map((m) => m[1]));
  const added = [...withPlugin].filter((c) => !coreOnly.has(c) && !authored.has(c));

  // `warning` is the one unprefixed modifier the plugin emits (.dc-note.warning).
  test("every class the plugin adds carries the dc- prefix", () => {
    expect(added.length).toBeGreaterThan(10);
    const unexpected = added.filter((c) => !c.startsWith("dc-") && !/^(tier-)?(crit|hit|mixed|miss|fail|free|variable|warning)$/.test(c));
    expect(unexpected).toEqual([]);
  });

  test("emits no gp- class of its own", () => {
    expect(added.filter((c) => c.startsWith("gp-"))).toEqual([]);
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
      expect(declared.filter((p) => !["--gp-column-gap", "--gp-column-rule"].includes(p)), `${rel} declares a core property`).toEqual([]);
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

  // PDF/X-1a (DriveThruRPG) carries no transparency: Ghostscript flattens any
  // page that uses it to a raster image — no live text, and black text stays
  // four-colour. Every colour is opaque; see docs/print-transparency-inventory.md.
  test("paint nothing transparent (PDF/X-1a)", () => {
    const ALPHA = [
      [/rgba\(|hsla\(/, "an rgba()/hsla() colour"],
      [/(^|[^-\w])opacity\s*:\s*0?\.\d/, "opacity below 1"],
      [/#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{4}\b(?![-\w])/, "a hex colour with alpha"],
      [/mix-blend-mode\s*:\s*(?!normal)|background-blend-mode\s*:\s*(?!normal)/, "a blend mode"],
      [/gradient\([^;]*\btransparent\b/, "a transparent gradient stop"],
      [/(box|text)-shadow\s*:[^;]*?-?\d[\d.]*(px|pt)\s+-?\d[\d.]*(px|pt)\s+[1-9][\d.]*(px|pt)\s/, "a blurred shadow"],
    ];
    const found = [];
    for (const rel of sheets) {
      const css = stripComments(read(rel));
      for (const [re, what] of ALPHA) if (re.test(css)) found.push(`${rel}: ${what}`);
    }
    expect(found).toEqual([]);
  });
});

/** The simple selectors a compound selector puts on ONE element: `:is()`/`:where()` arguments are merged in (one alternative at a time), other functional pseudos are dropped. */
function elementClassSets(compound) {
  const m = compound.match(/:(?:is|where)\(/);
  if (!m) return [[...compound.replace(/:[\w-]+\((?:[^()]|\([^()]*\))*\)/g, "").matchAll(/\.(-?[_a-zA-Z][\w-]*)/g)].map((x) => x[1])];
  let depth = 1;
  let i = m.index + m[0].length;
  for (; i < compound.length && depth; i++) depth += compound[i] === "(" ? 1 : compound[i] === ")" ? -1 : 0;
  const args = compound.slice(m.index + m[0].length, i - 1);
  const alts = [];
  let cur = "";
  depth = 0;
  for (const ch of args) {
    if (ch === "(") depth++;
    if (ch === ")") depth--;
    if (ch === "," && !depth) (alts.push(cur), (cur = ""));
    else cur += ch;
  }
  alts.push(cur);
  const rest = compound.slice(0, m.index) + compound.slice(i);
  return alts.flatMap((alt) => elementClassSets(rest + alt));
}
/** Split a selector into compounds at the combinators that sit outside parentheses and brackets. */
function compoundsOf(selector) {
  const out = [];
  let cur = "";
  let depth = 0;
  for (const ch of selector) {
    if ("([".includes(ch)) depth++;
    if (")]".includes(ch)) depth--;
    if (!depth && /[\s>+~]/.test(ch)) (cur && out.push(cur), (cur = ""));
    else cur += ch;
  }
  return cur ? [...out, cur] : out;
}


// A bare `@section` is core's plain box. No rule here may reach it: every
// selector that names `.section` must name a `dc-` class on the same element.
describe("a bare @section is unstyled", () => {
  test("no selector in styles/** matches `.section` without a dc- class on the same element", () => {
    const bad = [];
    const dirs = ["styles", "styles/components"];
    for (const rel of dirs.flatMap((d) => readdirSync(path.join(ROOT, d)).filter((f) => f.endsWith(".css")).map((f) => `${d}/${f}`))) {
      postcss.parse(read(rel)).walkRules((rule) => {
        for (const selector of rule.selectors) {
          for (const compound of compoundsOf(selector)) {
            if (elementClassSets(compound).some((cls) => cls.includes("section") && !cls.some((c) => c.startsWith("dc-")))) bad.push(`${rel}: ${selector.trim()}`);
          }
        }
      });
    }
    expect(bad, "a bare .section is core's plain box: key the rule on a variant class (.dc-section-panel, …)").toEqual([]);
  });
});


// A skill card is a third to half a page: kept atomic, it left most specialty
// pages holding one card and a third of the sheet empty. Cards split by
// default; `.dc-avoid-split` is the only thing that keeps one whole.
describe("skill cards split by default", () => {
  test("no rule gives a skill card break-inside: avoid unless it names .dc-avoid-split", () => {
    const bad = [];
    for (const rel of pkg.gutterpress.styles) {
      postcss.parse(read(rel)).walkRules((rule) => {
        const avoids = rule.nodes.some((n) => n.type === "decl" && n.prop === "break-inside" && /^avoid/.test(n.value));
        if (!avoids) return;
        for (const selector of rule.selectors) {
          const subject = compoundsOf(selector).at(-1) ?? "";
          if (/\.dc-skill-card(?![\w-])/.test(subject) && !/dc-avoid-split/.test(selector)) bad.push(`${rel}: ${selector.trim()}`);
        }
      });
    }
    expect(bad, "a skill card splits by default: key the avoid on .dc-avoid-split").toEqual([]);
  });

  test("an ability row is never cut, and a split card never opens with only its tab", () => {
    const css = read("styles/components/cards.css");
    expect(css).toMatch(/\.dc-skill-card \.dc-ability \{\s*break-inside: avoid;/);
    expect(css).toMatch(/\.dc-skill-card:not\(\.dc-avoid-split\) \.dc-card-inner > :nth-child\(-n\+2\) \{\s*break-after: avoid;/);
  });
});

// A location (a page template such as `@page chapter-start`, a chapter such as
// `@chapter rules`) only ADJUSTS a component: it may set `--dc-*` tokens on the
// component, and it may style its OWN element and plain elements (the page's
// h1, its paragraphs, its margins). It never supplies the component's chrome.
// The check is on the element a rule styles (the subject, the last compound):
// when that is a component (`.dc-section-flat`, `.dc-toc`, `.dc-intro`, …) the
// rule may declare custom properties only.
describe("a location adjusts components by tokens only", () => {
  const LOCATION = /^(dc-page-|dc-chapter-|page-[a-z]|chapter$|chapter-\d)|^(dc-credits|dc-citizen-file-page|dc-full-page)$/;
  const MODIFIER = /^(dc-snug|dc-avoid-split)$/;
  const isComponent = (c) => c.startsWith("dc-") && !LOCATION.test(c) && !MODIFIER.test(c);
  /** The compound a rule styles, without its pseudo-element (`::before` belongs to the element before it). */
  const subjectOf = (selector) => (compoundsOf(selector).at(-1) ?? "").replace(/::?(before|after|first-line|first-letter|marker)$/, "");

  test("a rule keyed on a page or chapter class declares only custom properties on a component", () => {
    const bad = [];
    let seen = 0;
    for (const rel of ["styles/page-templates.css", "styles/page-rules.css", "styles/dc-native.css"]) {
      postcss.parse(read(rel)).walkRules((rule) => {
        const chrome = rule.nodes.filter((n) => n.type === "decl" && !n.prop.startsWith("--")).map((n) => n.prop);
        for (const selector of rule.selectors) {
          const compounds = compoundsOf(selector);
          if (!compounds.some((c) => elementClassSets(c).some((cls) => cls.some((x) => LOCATION.test(x))))) continue;
          seen++;
          if (elementClassSets(subjectOf(selector)).some((cls) => cls.some(isComponent)) && chrome.length) bad.push(`${rel}: ${selector.trim()} { ${[...new Set(chrome)].join(", ")} }`);
        }
      });
    }
    expect(seen, "found no location rules, so the check is not looking at anything").toBeGreaterThan(10);
    expect(bad, "a location sets --dc-* tokens on a component; the component's own rule reads them").toEqual([]);
  });
});

describe("snippets", () => {
  test("every snippet renders through the plugin without a layout warning", () => {
    const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {}, markers }]);
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
