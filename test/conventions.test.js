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


// Keeping a box whole is a token per component, `--dc-<component>-break-inside`
// (defaults at :root in dc-component-defaults.css). `.dc-avoid-split` is a setter
// of those tokens and nothing else, so a book writes the same declarations from
// its own sheet. A rule that gives a box `break-inside: avoid` reads the token.
describe("keep-whole tokens", () => {
  const TOKENS = ["--dc-section-break-inside", "--dc-catalog-break-inside", "--dc-npc-stat-break-inside", "--dc-skill-card-break-inside", "--dc-faction-break-inside"];

  test("each is declared at :root, and a section, a catalog, a skill card and a faction split by default", () => {
    const root = declsOf("styles/dc-component-defaults.css", ":root");
    for (const token of TOKENS) expect(root[token], token).toBeDefined();
    for (const token of TOKENS.filter((t) => t !== "--dc-npc-stat-break-inside")) expect(root[token], token).toBe("auto");
    expect(root["--dc-npc-stat-break-inside"], "a creature stays whole").toBe("avoid");
  });

  test(".dc-avoid-split sets every token to avoid, and the section's edge to 0px, and sets nothing else", () => {
    const setter = declsOf("styles/components/section.css", ".dc-avoid-split");
    expect(Object.keys(setter).sort()).toEqual([...TOKENS, "--dc-section-edge"].sort());
    for (const [prop, value] of Object.entries(setter)) expect(value, prop).toBe(prop === "--dc-section-edge" ? "0px" : "avoid");
  });

  test("no rule says `break-inside: avoid` for a section, a skill card or a faction: they read their token", () => {
    const bad = [];
    for (const rel of pkg.gutterpress.styles) {
      postcss.parse(read(rel)).walkRules((rule) => {
        const avoids = rule.nodes.some((n) => n.type === "decl" && n.prop === "break-inside" && /^avoid/.test(n.value));
        if (!avoids) return;
        for (const selector of rule.selectors) {
          const subject = compoundsOf(selector).at(-1) ?? "";
          if (/\.(dc-skill-card|dc-faction|dc-section-panel|dc-section-flat|dc-npc-stat|dc-catalog)(?![\w-])/.test(subject)) bad.push(`${rel}: ${selector.trim()}`);
        }
      });
    }
    expect(bad, "set the box's --dc-<component>-break-inside token instead").toEqual([]);
  });

  test("a catalog reads its own token: it splits by default, and `.dc-avoid-split` (an author's override) keeps one whole", () => {
    const catalog = declsOf("styles/components/entries.css", ".dc-section-panel.dc-catalog");
    expect(catalog["--dc-section-break-inside"]).toBe("var(--dc-catalog-break-inside)");
    expect(catalog["--dc-section-edge"], "the edge is the setter's, so a catalog marked .dc-avoid-split renders as before").toBeUndefined();
    expect(declsOf("styles/components/section.css", ".dc-avoid-split")["--dc-catalog-break-inside"]).toBe("avoid");
    expect(declsOf("styles/dc-component-defaults.css", ":root")["--dc-catalog-break-inside"]).toBe("auto");
  });

  test("a creature (an @npc-stat with at most one `####`) reads --dc-npc-stat-break-inside", () => {
    const creature = declsOf("styles/components/section.css", ".dc-section-panel.dc-npc-stat:not(:has(h4 ~ h4))");
    expect(creature["break-inside"]).toBe("var(--dc-npc-stat-break-inside)");
  });
});

// A skill card is a third to half a page: kept atomic, it left most specialty
// pages holding one card and a third of the sheet empty. Cards split by
// default; `.dc-avoid-split` is the only thing that keeps one whole.
describe("skill cards split by default", () => {
  test("a skill card's break-inside is its token", () => {
    expect(declsOf("styles/components/cards.css", ".dc-skill-card")["break-inside"]).toBe("var(--dc-skill-card-break-inside)");
  });

  test("an ability row is never cut, and a split card never opens with only its tab", () => {
    const css = read("styles/components/cards.css");
    expect(css).toMatch(/\.dc-skill-card \.dc-ability \{\s*break-inside: avoid;/);
    expect(css).toMatch(/\.dc-skill-card \.dc-card-inner > :nth-child\(-n\+2\) \{\s*break-after: avoid;/);
  });
});

// A faction profile runs to half a page or more; kept whole it left half-empty
// pages through a chapter of factions. It splits like an entry.
describe("faction cards split by default", () => {
  test("a faction card overrides .dc-card's avoid with its token, which defaults to auto", () => {
    const css = read("styles/components/section.css");
    expect(css).toMatch(/\.dc-card\.dc-faction \{[^}]*break-inside: var\(--dc-faction-break-inside\);/);
    expect(css).toMatch(/\.dc-card\.dc-faction > :is\(h3, h4\):first-of-type \{[^}]*break-after: avoid;/);
  });
});

// Art gets a default by where it sits: an entry's picture floats right, the
// credits plate is a band at the foot of the sheet. Both read only an image with
// no class, so a `.gp-*` class an author writes (the desktop writes them from
// its Image Properties) is never overridden by the plugin, which outranks core's.
describe("art defaults leave a classed image alone", () => {
  test("an entry's picture reads --dc-entry-art-width", () => {
    const art = declsOf("styles/components/entries.css", ".dc-entry img:not([class])");
    expect(art.float).toBe("right");
    expect(art.width).toBe("var(--dc-entry-art-width)");
    expect(declsOf("styles/dc-component-defaults.css", ":root")["--dc-entry-art-width"]).toBe("50%");
  });

  test("the credits plate reads --dc-credits-art-height", () => {
    const plate = declsOf("styles/page-templates.css", ".page.dc-page-credits > p > img:not([class])");
    expect(plate.height).toBe("var(--dc-credits-art-height)");
    expect(declsOf("styles/dc-component-defaults.css", ":root")["--dc-credits-art-height"]).toBe("2.75in");
  });
});

// The space under a paragraph or list item is `--dc-flow-gap`, which nothing
// sets by default (each component keeps its own), `.dc-snug` sets, and a book
// may set on any box. `revert-layer` hands the margin back while it is unset.
describe("the flow gap", () => {
  test("the rule reads the token with a `revert-layer` fallback, and `.dc-snug` sets it to 0.04in", () => {
    expect(declsOf("styles/page-templates.css", ":is(p, li)")["margin-bottom"]).toBe("var(--dc-flow-gap, revert-layer)");
    expect(declsOf("styles/page-templates.css", ".dc-snug")["--dc-flow-gap"]).toBe("0.04in");
  });

  test("nothing declares it at :root: unset is what keeps a component's own spacing", () => {
    for (const rel of pkg.gutterpress.styles) postcss.parse(read(rel)).walkRules(":root", (rule) => rule.walkDecls("--dc-flow-gap", () => { throw new Error(`${rel} declares --dc-flow-gap at :root`); }));
  });
});

/** The declarations of the rule whose selector is exactly `selector`, as {prop: value}. */
function declsOf(rel, selector) {
  const found = {};
  postcss.parse(read(rel)).walkRules((rule) => {
    if (rule.selectors.map((s) => s.trim().replace(/\s+/g, " ")).includes(selector)) {
      for (const n of rule.nodes) if (n.type === "decl") found[n.prop] = n.value;
    }
  });
  return found;
}

// The SPECS box used to be a callout, which split between lines. A field that
// avoids a split is pushed whole to the next page, and thirty of them in a
// chapter cost a book four pages. The chip is inline on the first line, so two
// lines at either edge keep it with its text.
describe("a field splits between lines", () => {
  test("`.dc-field` does not avoid a split, and never leaves one line at an edge", () => {
    const field = declsOf("styles/components/entries.css", ".dc-field");
    expect(field["break-inside"], "a field splits like the callout it replaced").toBeUndefined();
    expect(field.orphans).toBe("2");
    expect(field.widows).toBe("2");
  });
});

// Chromium keeps the orphans and drops the widows when a paragraph is too short
// to satisfy both, so the body's 2 + 2 let a three-line paragraph split 2 + 1.
// Orphans of 3 move it whole.
describe("skill card text never leaves one line at a page edge", () => {
  test("the text in a card asks for 3 orphans and 2 widows", () => {
    const text = declsOf("styles/components/cards.css", ".dc-skill-card :is(.dc-ability-text, p, li)");
    expect(text.orphans).toBe("3");
    expect(text.widows).toBe("2");
  });
});

// A panel's edge and shadow hang below its box. A layer that really extends
// below the box (a negative `bottom`) is fragmented onto a page of its own when
// its panel ends in the last pixels of a page, a page holding only the bottom
// rule. The layers are exactly the box and the hang is box-shadow paint.
describe("a panel's overhang opens no page", () => {
  const layers = [".dc-section-panel::before", ".dc-section-panel::after"];

  test("the layers are exactly the box: nothing extends below it", () => {
    for (const layer of layers) {
      const d = declsOf("styles/components/section.css", layer);
      expect(d.bottom ?? d.inset, layer).toBe("0");
    }
  });

  test("the edge hangs as a box-shadow pushed down by the edge, and the clip-path reaches it", () => {
    for (const layer of layers) {
      const d = declsOf("styles/components/section.css", layer);
      expect(d["box-shadow"], layer).toMatch(/0 (calc\(3px \+ )?var\(--dc-section-edge\)/);
      expect(d["clip-path"], layer).toMatch(/calc\(100% \+ (3px \+ )?var\(--dc-section-edge\)\)/);
    }
  });

  test("nothing clips the panel's block overflow to hide the hang", () => {
    const panel = declsOf("styles/components/section.css", ".dc-section-panel:last-child");
    expect(panel["overflow-y"]).toBeUndefined();
    expect(panel["overflow-clip-margin"]).toBeUndefined();
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

// `hyphens: auto` hyphenates only where the browser ships a dictionary, and
// Chromium builds differ, so the same book paginated differently in the desktop
// app and the CLI. The package hyphenates manually (soft hyphens only).
describe("hyphenation does not depend on the browser", () => {
  test("no package rule sets hyphens: auto", () => {
    const bad = [];
    for (const rel of pkg.gutterpress.styles) {
      postcss.parse(read(rel)).walkDecls("hyphens", (d) => {
        if (d.value.trim() === "auto") bad.push(`${rel}: ${d.parent.selector}`);
      });
    }
    expect(bad).toEqual([]);
  });
});
