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

import plugin from "../plugin.js";

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
  // Outcome tiers the roll-table macros emit as modifier classes; the visual
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
  ...Object.fromEntries(["typography", "palette", "layout", "templates", "cli", "reference", "examples", "chapter-6", "chapter-7", "chapter-8", "chapter-9", "chapter-10", "chapter-11"].map((c) => [c, "DG chapter identity label (styled by #id, if at all)"])),
  // Design guide page-template names, shown as `@page .x` in the examples; the template look comes from the page's data-page / other classes.
  "card-grid": "DG page-name label on the specialty catalog example page",
  "specialty-profile": "DG page-name label on the specialty profile example chapter",
  "tech-cybernetics": "DG page-name label on the gear/tech example page",
  "second-page": "DG page-name label on the gear/tech example page",
  // FINDINGS (unstyled in guide.css or the package, 2026-10): allow-listed until styled or dropped.
  "dg-face-sample": "FINDING: used on the typography specimen paragraphs, no rule anywhere",
  "dc-banner-demo": "FINDING: demo-section hook in 02-typography.md / 11-variants.md, no rule anywhere",
  // Field Guide chapters: `@page .x .chapter-NN` / `@chapter .chapter-N`. The
  // book addresses chapters by `#chapter-NN` id in fg-overrides.css, so the
  // class twins are navigation labels only.
  ...Object.fromEntries(["chapter-01", "chapter-02", "chapter-03", "chapter-04", "chapter-1", "chapter-2", "chapter-3", "chapter-4", "chapter-5"].map((c) => [c, "FG chapter identity label (styled by #chapter-NN id instead)"])),
  // Field Guide page names written as `@page .name` for navigation / future per-page art; no rule targets them yet.
  "choose-specialty": "FG page-name label (chapter-01)",
  "vibe": "FG page-name label (chapter-01)",
  "call-home": "FG page-name label (chapter-01)",
  "ideal": "FG page-name label (chapter-01)",
  "flaw": "FG page-name label (chapter-01)",
  "the-players": "FG page-name label (chapter-03)",
  "scenes": "FG page-name label (chapter-03)",
};

/** All classes in a rendered HTML string, with the first file that carried each. */
function classesOfBook(chapterFiles) {
  const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {} }]);
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
  // to page/chapter context classes". The sheets below legitimately style the
  // framework's own `.page` / `.chapter` markup (intro-page chevrons, front-matter
  // page decorations); they are allow-listed per selector, with the reason.
  const PAGE_CHAPTER_ALLOWLIST = [
    // [sheet, selector substring, reason]
    ["styles/components/chrome.css", '.chapter[data-chapter-label] > .page[data-page="intro"]', "chapter-opener h1 chevron: component chrome that keys on the opener page"],
    ["styles/components/chrome.css", '.page[data-page="intro"][data-chapter-label]', "chapter-opener composite, same reason"],
  ];
  const allowedPageChapter = (label, selector) => PAGE_CHAPTER_ALLOWLIST.some(([f, sub]) => f === label && selector.includes(sub));

  test("components/*.css declare no @page and no .chapter/.page selectors (beyond the allow-list)", () => {
    const bad = [];
    for (const s of COMPONENT_SHEETS) {
      s.root.walkAtRules("page", (a) => bad.push(`${s.label}: @page rule`));
      for (const { selector } of selectorsOf(s.root)) {
        const cls = classesIn(selector);
        if ((cls.includes("chapter") || cls.includes("page")) && !allowedPageChapter(s.label, selector)) bad.push(`${s.label}: ${selector}`);
      }
    }
    expect(bad, "page/chapter scaffolding belongs in page-templates.css / page-rules.css / the book's sheet; or allow-list it in PAGE_CHAPTER_ALLOWLIST with a reason").toEqual([]);
  });

  // Columns: page-templates.css owns every THEME `columns:N` (css-architecture.md,
  // "COLUMNS:N Ownership Rule"). Stated exception: none in the doc — see findings.
  const COLUMNS_ALLOWLIST = [
    // [sheet, selector substring, reason] — FINDINGS: both contradict the stated rule; allow-listed until moved.
    ["styles/components/cards.css", ".dc-skill-card.dc-two-col .dc-card-inner", "two-column skill card body (column-count: 2) — no stated exception in css-architecture.md"],
    ["styles/components/cards.css", ".dc-cards-two-col .dc-skill-card", "ancestor-scoped two-column skill cards — component-internal layout of the card body, same class of exception as .dc-two-col above"],
    ["styles/components/section.css", ".dc-card-grid", "card grid uses columns: 2 — no stated exception in css-architecture.md"],
  ];
  test("`columns` / `column-count` are declared only in page-templates.css", () => {
    const bad = [];
    for (const s of PKG) {
      if (s.label === "styles/page-templates.css") continue;
      s.root.walkDecls(/^(columns|column-count)$/, (d) => {
        const sel = where(d.parent);
        if (!COLUMNS_ALLOWLIST.some(([f, sub]) => f === s.label && sel.includes(sub))) bad.push(`${s.label}: ${sel} { ${d.prop}: ${d.value} }`);
      });
    }
    expect(bad, "move it to page-templates.css (css-architecture.md, COLUMNS:N Ownership Rule)").toEqual([]);
  });

  test("page-templates.css never sets columns on core's .gp-columns-* (gap only)", () => {
    const s = PKG.find((x) => x.label === "styles/page-templates.css");
    const bad = [];
    s.root.walkDecls(/^(columns|column-count)$/, (d) => {
      if (d.parent.selectors?.some((sel) => classesIn(sel).some((c) => c.startsWith("gp-columns-")))) bad.push(`${where(d.parent)} { ${d.prop} }`);
    });
    expect(bad).toEqual([]);
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
