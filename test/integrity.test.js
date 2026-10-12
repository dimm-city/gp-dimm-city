// integrity.test.js — drift guards found by the orphan audit, made executable.
//
//   1. No dangling classes: every class a book's rendered HTML carries is
//      styled somewhere, or is a known, explained hook.
//   2. No undeclared custom properties: every `var(--x)` read has a
//      declaration, and every token the docs name exists.
//   3. File contracts from docs/css-architecture.md and the sheets' headers.
//
// The CSS is parsed with postcss (selectors and declarations), never grepped.
// The design guide checks always run; the Field Guide (a sibling repo) is
// checked only when its folder exists.
import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import postcss from "postcss";
import { createMarkdownRenderer } from "gutterpress/render";

import plugin, { markers } from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");
const pkg = JSON.parse(read("package.json"));
const PACKAGE_SHEETS = pkg.gutterpress.styles;

const FG_DIR = path.resolve(ROOT, "../dc-op-manual/field-guide");
const HAS_FG = existsSync(path.join(FG_DIR, "manifest.yaml"));
const GUIDE_DIR = path.join(ROOT, "design-guide");

// ── CSS parsing ──────────────────────────────────────────────────────────────
const parsed = new Map(); // absolute path -> postcss Root
function css(abs) {
  if (!parsed.has(abs)) parsed.set(abs, postcss.parse(readFileSync(abs, "utf8"), { from: abs }));
  return parsed.get(abs);
}
const pkgSheet = (rel) => ({ label: rel, root: css(path.join(ROOT, rel)) });
const PKG = PACKAGE_SHEETS.map(pkgSheet);
const GUIDE_SHEETS = [{ label: "design-guide/styles/guide.css", root: css(path.join(GUIDE_DIR, "styles/guide.css")) }];
const FG_SHEETS = HAS_FG
  ? ["fg-overrides.css", "fg-native.css"].map((f) => ({ label: `field-guide/styles/${f}`, root: css(path.join(FG_DIR, "styles", f)) }))
  : [];

/** Every selector in the sheet, outside keyframes. */
function selectorsOf(root) {
  const out = [];
  root.walkRules((r) => {
    if (r.parent?.type === "atrule" && /keyframes$/i.test(r.parent.name)) return;
    for (const s of r.selectors) out.push({ selector: s.trim(), rule: r });
  });
  return out;
}

/** Class names a selector mentions. Attribute values and strings are dropped first. */
function classesIn(selector) {
  const bare = selector.replace(/\[[^\]]*\]/g, "").replace(/(["'])(?:\\.|(?!\1).)*\1/g, "");
  return [...bare.matchAll(/\.(-?[_a-zA-Z][\w-]*)/g)].map((m) => m[1]);
}

const definedClasses = (sheets) => new Set(sheets.flatMap((s) => selectorsOf(s.root).flatMap((x) => classesIn(x.selector))));

/** Every custom-property declaration: { prop, value, rule, label }. */
function declarations(sheets) {
  const out = [];
  for (const s of sheets)
    s.root.walkDecls((d) => {
      if (d.prop.startsWith("--")) out.push({ prop: d.prop, value: d.value, rule: d.parent, label: s.label });
    });
  return out;
}

/** Every `var(--x[, fallback])` read: { name, hasFallback, prop, rule, label }. */
function reads(sheets) {
  const out = [];
  for (const s of sheets)
    s.root.walkDecls((d) => {
      for (const m of d.value.matchAll(/var\(\s*(--[\w-]+)\s*(,)?/g)) out.push({ name: m[1], hasFallback: !!m[2], prop: d.prop, rule: d.parent, label: s.label });
    });
  return out;
}

const where = (rule) => (rule?.selector ? rule.selector.replace(/\s+/g, " ").slice(0, 80) : `@${rule?.name ?? "?"}`);

// ── 1. Dangling classes ──────────────────────────────────────────────────────

/** Classes the plugin emits on purpose with no CSS — read from components.yaml `unstyled:` fields. */
const UNSTYLED_ACKNOWLEDGED = [...read("components.yaml").matchAll(/^\s*unstyled:\s*\[([^\]]*)\]/gm)].flatMap((m) => m[1].split(",").map((s) => s.trim()).filter(Boolean));

/**
 * Hooks with no stylesheet rule that are not covered by components.yaml.
 * Keep this SMALL; every entry needs a reason.
 */
const HOOK_ALLOWLIST = {
  // Outcome tiers @outcome emits as modifier classes; the visual
  // difference is carried by a `data-` attribute / table-cell styling instead.
  "tier-crit": "outcome tier hook emitted by the plugin",
  "tier-hit": "outcome tier hook emitted by the plugin",
  "tier-mixed": "outcome tier hook emitted by the plugin",
  "tier-miss": "outcome tier hook emitted by the plugin",
  "tier-fail": "outcome tier hook emitted by the plugin",
};

const isCoreOrFence = (c) => c.startsWith("gp-") || c.startsWith("language-");

/** Chapter/page identity hooks authors put on markers purely for navigation or per-book targeting. */
const IDENTITY_HOOKS = {
  // Design guide: chapter/part names written as `@chapter .typography` / `@page .x` / `@chapter .chapter-N`
  // purely so the markup is navigable; nothing styles them (guide.css keys on #ch-* ids).
  ...Object.fromEntries(["typography", "palette", "layout", "templates", "cli", "reference", "examples", "chapter-03", "chapter-6", "chapter-7", "chapter-8", "chapter-9", "chapter-10", "chapter-11"].map((c) => [c, "DG chapter identity label (styled by #id, if at all)"])),
  // Design guide page-template names, shown as `@page .x` in the examples; the template look comes from the page's data-page / other classes.
  "card-grid": "DG page-name label on the specialty catalog example page",
  "specialty-profile": "DG page-name label on the specialty profile example chapter",
  "tech-cybernetics": "DG page-name label on the gear/tech example page",
  "second-page": "DG page-name label on the gear/tech example page",
  // Both guides: gutterpress core emits `chapter-N` on `@chapter … ch="N"` (not author-written); nothing styles the number-only twin.
  ...Object.fromEntries(["chapter-1", "chapter-2", "chapter-3", "chapter-4", "chapter-5"].map((c) => [c, "core-emitted chapter-N class from `@chapter ch=\"N\"`"])),
};

/** All classes in a rendered HTML string, with the first file that carried each. */
function classesOfBook(chapterFiles) {
  const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {}, markers }]);
  const seen = new Map();
  for (const file of chapterFiles) {
    const html = md.render(readFileSync(file, "utf8"), {});
    for (const m of html.matchAll(/class="([^"]+)"/g)) for (const c of m[1].split(/\s+/)) if (c && !seen.has(c)) seen.set(c, path.basename(file));
  }
  return seen;
}

function danglingIn(book, files, sheets) {
  const defined = definedClasses([...PKG, ...sheets]);
  const dangling = [];
  for (const [c, file] of classesOfBook(files)) {
    if (defined.has(c) || isCoreOrFence(c) || UNSTYLED_ACKNOWLEDGED.includes(c) || c in HOOK_ALLOWLIST || c in IDENTITY_HOOKS) continue;
    dangling.push(`.${c} (first used in ${book}/${file})`);
  }
  return dangling;
}

const guideChapters = [...read("design-guide/manifest.yaml").replace(/^[ \t]*#.*\n/gm, "").matchAll(/^\s*-\s*(\S+\.md)\s*$/gm)].map((m) => path.join(GUIDE_DIR, m[1]));
const fgChapters = HAS_FG
  ? readdirSync(FG_DIR)
      .filter((f) => f.endsWith(".md"))
      .sort()
      .map((f) => path.join(FG_DIR, f))
  : [];

describe("no dangling classes", () => {
  const hint = "Style it, remove it from the markup, or (if it is a deliberate hook) add it to HOOK_ALLOWLIST / IDENTITY_HOOKS in test/integrity.test.js with a reason, or to `unstyled:` in components.yaml.";

  test("design guide: every rendered class is styled or a known hook", () => {
    expect(guideChapters.length).toBeGreaterThan(15);
    expect(danglingIn("design-guide", guideChapters, GUIDE_SHEETS), hint).toEqual([]);
  });

  test.skipIf(!HAS_FG)("field guide: every rendered class is styled or a known hook", () => {
    expect(fgChapters.length).toBeGreaterThan(5);
    expect(danglingIn("field-guide", fgChapters, FG_SHEETS), hint).toEqual([]);
  });
});

// ── 2. Custom properties ─────────────────────────────────────────────────────

/**
 * Names read with a fallback and never declared by any sheet. A fallback makes
 * the read safe, so these are not failures — but the list is pinned so a NEW
 * undeclared name cannot slip in under the cover of a fallback.
 */
const FALLBACK_ONLY_ALLOWLIST = {};

function undeclaredReads(sheets) {
  const declared = new Set(declarations(sheets).map((d) => d.prop));
  const bad = [];
  for (const r of reads(sheets)) {
    if (r.name.startsWith("--gp-") || declared.has(r.name)) continue;
    if (r.hasFallback && r.name in FALLBACK_ONLY_ALLOWLIST) continue;
    bad.push(`${r.label}: ${where(r.rule)} { ${r.prop}: var(${r.name}${r.hasFallback ? ", …" : ""}) } — ${r.name} is never declared`);
  }
  return [...new Set(bad)];
}

describe("custom properties", () => {
  test("package sheets read only declared tokens (core's --gp-* excepted)", () => {
    expect(undeclaredReads(PKG), "Declare the token (dc-palette / dc-identity / dc-component-defaults) or stop reading it.").toEqual([]);
  });

  test("design guide sheet reads only tokens declared in the package or guide.css", () => {
    expect(undeclaredReads([...PKG, ...GUIDE_SHEETS]).filter((m) => m.startsWith("design-guide/"))).toEqual([]);
  });

  test.skipIf(!HAS_FG)("field guide sheets read only tokens declared in the package or FG sheets", () => {
    expect(undeclaredReads([...PKG, ...FG_SHEETS]).filter((m) => m.startsWith("field-guide/"))).toEqual([]);
  });

  test("every --token named in backticks in docs/components-and-palette-reference.md is declared in the package", () => {
    const declared = new Set(declarations(PKG).map((d) => d.prop));
    const named = new Set([...read("docs/components-and-palette-reference.md").matchAll(/`(--[a-z][\w-]*)`/g)].map((m) => m[1]));
    expect(named.size).toBeGreaterThan(50);
    const phantom = [...named].filter((t) => !declared.has(t) && !t.startsWith("--gp-"));
    expect(phantom, "docs/components-and-palette-reference.md names tokens no package sheet declares").toEqual([]);
  });
});

// ── 3. File contracts ────────────────────────────────────────────────────────
const COMPONENT_SHEETS = PKG.filter((s) => s.label.startsWith("styles/components/"));
const TOKEN_SHEETS = ["styles/dc-palette.css", "styles/dc-identity.css", "styles/dc-component-defaults.css"];

describe("file contracts", () => {
  // css-architecture.md, dc.components: "MUST NOT contain … `@page` declarations,
  // `div.chapter` scaffolding". callouts.css's header adds "element selectors scoped
  // to page/chapter context classes". No exceptions: page/chapter styling lives in
  // page-templates.css, page-rules.css or the book's sheet.
  test("components/*.css declare no @page and no .chapter/.page selectors", () => {
    const bad = [];
    for (const s of COMPONENT_SHEETS) {
      s.root.walkAtRules("page", (a) => bad.push(`${s.label}: @page rule`));
      for (const { selector } of selectorsOf(s.root)) {
        const cls = classesIn(selector);
        if ((cls.includes("chapter") || cls.includes("page"))) bad.push(`${s.label}: ${selector}`);
      }
    }
    expect(bad, "page/chapter scaffolding belongs in page-templates.css / page-rules.css / the book's sheet").toEqual([]);
  });

  // Columns (css-architecture.md, "Column ownership"): this package owns NO column
  // layout. `@columns N` is core's, and so are the count, the gap, the rule and the
  // fill. The package sets the two author hooks (`--gp-column-gap`, `--gp-column-rule`)
  // once at :root, and `column-span` stays with the column panel's header bar. The
  // grids inside one component (`.dc-stat-grid`, `.dc-steps`, `.dc-outcome-row`) are
  // `grid-template-columns`, which is not column layout.
  test("no stylesheet sets `columns`, `column-count`, `column-width`, `column-gap`, `column-fill` or `column-rule`", () => {
    const bad = [];
    for (const s of PKG) {
      s.root.walkDecls(/^(columns|column-count|column-width|column-gap|column-fill|column-rule)$/, (d) => {
        bad.push(`${s.label}: ${where(d.parent)} { ${d.prop}: ${d.value} }`);
      });
    }
    expect(bad, "columns are core's `@columns N`; set `--gp-column-gap` / `--gp-column-rule` at :root instead").toEqual([]);
  });

  test("the only component-internal grids are the three approved ones", () => {
    const APPROVED = new Set([".dc-stat-grid", ".dc-steps>li", ".dc-outcome-row"]);
    const found = new Set();
    for (const s of PKG) {
      s.root.walkDecls("grid-template-columns", (d) => {
        for (const sel of d.parent.selectors ?? []) found.add(sel.replace(/\s+/g, "").replace(/^[a-z0-9]+(?=\.)/, ""));
      });
    }
    expect([...found].filter((x) => !APPROVED.has(x)), "a grid is not a way to lay out columns of content; use `@columns N`").toEqual([]);
  });

  test("`--gp-column-gap` and `--gp-column-rule` are set once, at :root, in dc-component-defaults.css", () => {
    const sets = [];
    for (const s of PKG) {
      s.root.walkDecls(/^--gp-column-(gap|rule)$/, (d) => {
        const sels = (d.parent.selectors ?? []).map((x) => x.trim());
        sets.push({ label: s.label, prop: d.prop, sels, value: d.value });
      });
    }
    for (const prop of ["--gp-column-gap", "--gp-column-rule"]) {
      const atRoot = sets.filter((x) => x.prop === prop && x.sels.includes(":root"));
      expect(atRoot.map((x) => x.label), `${prop} at :root`).toEqual(["styles/dc-component-defaults.css"]);
    }
    // Anywhere else it may only be reset to `none` (a component that wants no hairline).
    const elsewhere = sets.filter((x) => !x.sels.includes(":root") && x.value !== "none");
    expect(elsewhere, "only `--gp-column-rule: none` may be set on a component").toEqual([]);
  });

  // dc#34 (callouts.css TOKEN CONVENTION) + css-architecture.md "Tokens flow downward only":
  //   - `:root` custom properties are declared ONLY by the three dc.tokens sheets;
  //   - a component's BASE rule (a lone `.dc-x`) never declares a public `--dc-*` token;
  //     variants (`.dc-x.free`, `.dc-specialty.augmerc .dc-x`) and ancestors may;
  //   - no inline `var(--dc-x, fallback)` on components.
  test(":root declares custom properties only in the dc.tokens sheets", () => {
    const bad = [];
    for (const s of PKG) {
      if (TOKEN_SHEETS.includes(s.label)) continue;
      s.root.walkDecls(/^--/, (d) => {
        if (d.parent.selectors?.some((x) => x.trim() === ":root" || x.trim() === "html")) bad.push(`${s.label}: ${d.parent.selector} { ${d.prop} }`);
      });
    }
    expect(bad, "declare it in dc-palette / dc-identity / dc-component-defaults (css-architecture.md, 'Tokens flow downward only')").toEqual([]);
  });

  test("a component's base rule never declares its own public --dc-* token (dc#34)", () => {
    const bad = [];
    for (const s of COMPONENT_SHEETS) {
      s.root.walkDecls(/^--dc-/, (d) => {
        const sels = d.parent.selectors ?? [];
        // base rule = a lone `.dc-name` declaring `--dc-name-*`, its OWN component's token.
        // (`.dc-note { --dc-alert-* }` is a variant of .dc-alert, which the convention allows.)
        const own = (x) => { const m = /^(?:[a-z0-9]+)?\.(dc-[\w-]+)$/.exec(x.trim()); return m && d.prop.startsWith(`--${m[1]}-`); };
        if (sels.some(own)) bad.push(`${s.label}: ${d.parent.selector} { ${d.prop}: ${d.value} }`);
      });
    }
    expect(bad, "move the default to :root in dc-component-defaults.css and set variants on a variant class or ancestor").toEqual([]);
  });

  test("components read public tokens as a bare var(--dc-x) — no inline fallback (dc#34)", () => {
    const bad = reads(COMPONENT_SHEETS).filter((r) => r.hasFallback && r.name.startsWith("--dc-")).map((r) => `${r.label}: ${where(r.rule)} { ${r.prop}: var(${r.name}, …) }`);
    expect([...new Set(bad)]).toEqual([]);
  });
});

// ── 4. The component catalog ─────────────────────────────────────────────────
// components.yaml is the record of what an author can write. It has to name
// every marker plugin.js declares, every variant word on `section`, `page` and
// `chapter`, and the two modifiers, and each needs a snippet for the desktop's
// picker. Retired items stay in it as tombstones that name their replacement.
describe("component catalog", () => {
  const catalog = Bun.YAML.parse(read("components.yaml")).components;
  const snippetFiles = readdirSync(path.join(ROOT, "snippets")).filter((f) => f.endsWith(".md")).map((f) => f.replace(/\.md$/, ""));
  const asList = (v) => (v == null ? [] : Array.isArray(v) ? v : [v]);
  const entryFor = (spelling) => catalog.find((e) => e.status !== "retired" && asList(e.markers).includes(spelling));
  const WORD_MARKERS = ["section", "page", "chapter"]; // declared as variant words only
  const REQUIRED_MODIFIERS = ["dc-avoid-split", "dc-snug"];
  const REQUIRED_RETIRED = ["tabbed", "plain", "section-allow-split", "column-panel", "chapter-opener", "sidebar-inset"];
  /** Classes a retired entry mentions that stay styled because a live component uses them. */
  const SHARED_CLASSES = {
    "dc-sub-header": "the skill card's sub-header",
    "dc-sidebar": "@sidebar, the floated box, stays",
  };
  const styled = definedClasses(PKG);
  const classesOf = (entry) => [...new Set(asList(entry.emits).flatMap((e) => [...String(e).matchAll(/\.(-?[_a-zA-Z][\w-]*)/g)].map((m) => m[1])))];

  /** Every spelling plugin.js declares: "@name" for a marker, "@section word" for a variant word. */
  const declared = [
    ...Object.keys(markers).filter((k) => !WORD_MARKERS.includes(k)).map((k) => `@${k}`),
    ...WORD_MARKERS.flatMap((k) => Object.keys(markers[k]?.variants ?? {}).map((w) => `@${k} ${w}`)),
  ];

  test("plugin.js declares markers and variant words to check", () => {
    expect(declared.length).toBeGreaterThan(40);
    for (const k of WORD_MARKERS) expect(Object.keys(markers[k].variants).length, `${k} variants`).toBeGreaterThan(0);
  });

  test("every declared marker and variant word has a live catalog entry", () => {
    const missing = declared.filter((s) => !entryFor(s));
    expect(missing, "add an entry to components.yaml whose `markers:` lists each of these spellings").toEqual([]);
  });

  test("every declared marker and variant word has a snippet that exists", () => {
    const bad = [];
    for (const s of declared) {
      const entry = entryFor(s);
      if (!entry) continue; // reported by the test above
      const names = asList(entry.snippet);
      if (!names.length) bad.push(`${s}: entry "${entry.name}" names no snippet`);
      for (const n of names) if (!snippetFiles.includes(n)) bad.push(`${s}: snippets/${n}.md does not exist`);
    }
    expect(bad, "add snippets/<name>.md (first line the marker, at least one {{placeholder}}) and name it in the entry's `snippet:`").toEqual([]);
  });

  test("every snippet a catalog entry names exists, and every snippet file belongs to an entry", () => {
    const named = new Set(catalog.flatMap((e) => asList(e.snippet)));
    expect([...named].filter((n) => !snippetFiles.includes(n)), "named but missing").toEqual([]);
    expect(snippetFiles.filter((n) => !named.has(n)), "a snippet no components.yaml entry names").toEqual([]);
  });

  test("each modifier has a live entry, a snippet, and a rule that styles its class", () => {
    for (const cls of REQUIRED_MODIFIERS) {
      const entry = catalog.find((e) => e.status === "live" && e.modifier === cls);
      expect(entry, `no live entry with modifier: ${cls}`).toBeTruthy();
      expect(styled.has(cls), `no stylesheet styles .${cls}`).toBe(true);
      expect(asList(entry.snippet).length, `${cls} has no snippet`).toBeGreaterThan(0);
    }
  });

  test("every live entry maps to something declared, and to a class a stylesheet styles", () => {
    const bad = [];
    for (const e of catalog.filter((x) => x.status === "live" || x.status === "unused")) {
      for (const s of asList(e.markers)) if (!declared.includes(s)) bad.push(`${e.name}: markers lists ${s}, which plugin.js does not declare`);
      if (e.origin === "core") continue; // core's own box; this package styles nothing on it
      const cls = classesOf(e);
      if (!cls.some((c) => styled.has(c))) bad.push(`${e.name}: none of its classes (${cls.join(", ") || "none listed"}) is styled by any sheet`);
      if (!asList(e.css).length) bad.push(`${e.name}: names no css file`);
    }
    expect(bad).toEqual([]);
  });

  test("retired entries: spellings are gone from plugin.js, classes from the sheets, and the replacement is named", () => {
    const bad = [];
    for (const e of catalog.filter((x) => x.status === "retired")) {
      for (const s of asList(e.markers)) if (declared.includes(s)) bad.push(`${e.name}: ${s} is retired but plugin.js still declares it`);
      const alive = classesOf(e).filter((c) => c.startsWith("dc-") && styled.has(c) && !(c in SHARED_CLASSES));
      if (alive.length) bad.push(`${e.name}: retired but ${alive.map((c) => "." + c).join(", ")} is still styled`);
    }
    for (const name of REQUIRED_RETIRED) {
      const e = catalog.find((x) => x.name === name);
      if (!e) bad.push(`${name}: missing from components.yaml`);
      else if (e.status !== "retired") bad.push(`${name}: should be status: retired`);
      else if (!e.replaced_by) bad.push(`${name}: retired without \`replaced_by\``);
    }
    for (const e of catalog.filter((x) => asList(x.markers).length && x.status === "retired" && !x.replaced_by)) bad.push(`${e.name}: retired marker without \`replaced_by\``);
    expect(bad).toEqual([]);
  });
});
