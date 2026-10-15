// page-text.test.js — two guards on the page level (styles/page-templates.css):
//
//   1. "free-standing page text": a bare element at page level gets a paper
//      slip or sheet, but a COMPONENT emitted at page level (`@procedure`'s
//      `ol.dc-steps`, a bare `@lede`, `@toc`) must keep its own look. This
//      sheet's layer (`dc.templates`) outranks `dc.components`, so every rule
//      that styles a bare p/ul/ol/blockquote/heading must exclude an element a
//      component has claimed (`[class*="dc-"]`).
//   2. the 10pt reading floor: no `font-size` in a stylesheet may resolve below
//      `--fs-floor` (10pt).
import { describe, expect, test } from "bun:test";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import postcss from "postcss";
import { createMarkdownRenderer } from "gutterpress/render";

import plugin, { markers } from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");

function render(md) {
  const r = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {}, markers }]);
  return r.render(md, {});
}

/** The `dc-` classes that leave a plain element plain (a look class or a modifier). Must match page-templates.css's guard. */
const LOOK = ["dc-h3", "dc-h4", "dc-h5", "dc-h6", "dc-snug", "dc-avoid-split"];
/** `[class*="dc-"]:not(<LOOK>)`: does the guard exclude an element with this class attribute? */
const guardExcludes = (cls) => cls.includes("dc-") && !cls.split(/\s+/).some((c) => LOOK.includes(c));

/** The last compound of a selector, split at combinators outside brackets and parentheses. */
function subjectOf(selector) {
  let depth = 0;
  let cur = "";
  let last = "";
  for (const ch of selector.trim()) {
    if ("([".includes(ch)) depth++;
    if (")]".includes(ch)) depth--;
    if (!depth && /[\s>+~]/.test(ch)) {
      if (cur) last = cur;
      cur = "";
    } else cur += ch;
  }
  return (cur || last).replace(/::?[a-z-]+(\(.*\))?$/i, (m) => (m.startsWith("::") ? "" : m));
}

describe("free-standing page text", () => {
  test("a component emitted at page level keeps a dc- class, which the page-text guard excludes", () => {
    const cases = {
      "@procedure": "@page\n\n@procedure\n\n1. Do one thing\n2. Do another\n\n@end-procedure\n",
      "@lede": "@page\n\n@lede\n\nA bare lede.\n\n@end-lede\n",
      "@toc": "@page\n\n@toc\n\n1. [One](#one) — blurb\n\n@end-toc\n",
    };
    for (const [name, src] of Object.entries(cases)) {
      const html = render(src);
      // every element that is a direct child of the page wrapper
      const page = html.match(/<div class="page[^"]*"[^>]*>([\s\S]*)<\/div>\s*$/)?.[1] ?? html;
      const tops = [...page.matchAll(/<(ol|ul|p|blockquote|div|h[1-6])\b([^>]*)>/g)];
      expect(tops.length, `${name} rendered nothing`).toBeGreaterThan(0);
      const first = tops[0];
      const cls = first[2].match(/class="([^"]*)"/)?.[1] ?? "";
      expect(cls, `${name} at page level: <${first[1]}> carries no dc- class, so the page-text rules would dress it`).toMatch(/dc-/);
      expect(guardExcludes(cls), `${name}: the guard must exclude <${first[1]} class="${cls}">`).toBe(true);
    }
  });

  test("every page-text rule on a bare element is guarded against a component's element", () => {
    const bare = /^(p|ul|ol|blockquote|h[1-6]|:is\((p|ul|ol|blockquote|h[1-6])(,\s*(p|ul|ol|blockquote|h[1-6]))*\))/;
    const unguarded = [];
    let seen = 0;
    postcss.parse(read("styles/page-templates.css")).walkRules((rule) => {
      for (const selector of rule.selectors) {
        const positive = selector.replace(/:not\((?:[^()]|\([^()]*\))*\)/g, ""); // what the rule selects, without its exclusions
        if (!/\.page|\.chapter/.test(positive) || /dc-page-|dc-chapter-/.test(positive)) continue; // a location rule keys on a page word
        const subject = subjectOf(selector);
        if (!bare.test(subject)) continue;
        seen++;
        if (!subject.includes('[class*="dc-"]') && !selector.includes('[class*="dc-"]')) unguarded.push(selector.trim());
      }
    });
    expect(seen, "found no page-text rules, so the check is not looking at anything").toBeGreaterThan(5);
    expect(unguarded, 'a rule on a bare element at page level needs :not([class*="dc-"]…): this layer outranks dc.components').toEqual([]);
  });
});

// ── the 10pt floor ───────────────────────────────────────────────────────────
const sheets = [
  ...["styles", "styles/components"].flatMap((d) => readdirSync(path.join(ROOT, d)).filter((f) => f.endsWith(".css")).map((f) => `${d}/${f}`)),
  "design-guide/styles/guide.css",
];
const FLOOR_PT = 10;

/** Every custom property any sheet declares, for resolving `var(--x)`. A token declared twice resolves to its smallest value. */
function tokens() {
  const map = new Map();
  for (const rel of sheets) {
    postcss.parse(read(rel)).walkDecls(/^--/, (d) => {
      (map.get(d.prop) ?? map.set(d.prop, []).get(d.prop)).push(d.value.trim());
    });
  }
  return map;
}

/**
 * The smallest size, in pt, a font-size value can take, or `{ rel }` for a size relative to its parent (em, rem,
 * %) and `null` when it cannot be resolved without layout (calc(), inherit…). `max()` takes its largest argument,
 * `min()` its smallest, `clamp()` its first.
 */
function resolve(value, map, depth = 0) {
  const v = value.trim();
  if (depth > 8) return null;
  let m;
  if ((m = v.match(/^var\(\s*(--[\w-]+)\s*(?:,\s*(.+))?\)$/))) {
    const decls = map.get(m[1]);
    if (!decls) return m[2] ? resolve(m[2], map, depth + 1) : null;
    const all = decls.map((d) => resolve(d, map, depth + 1));
    const pts = all.filter((r) => typeof r === "number");
    if (pts.length) return Math.min(...pts);
    return all.find((r) => r && r.rel !== undefined) ?? null;
  }
  if ((m = v.match(/^(-?[\d.]+)(pt|px|in|rem|em|%)$/))) {
    const n = parseFloat(m[1]);
    if (m[2] === "pt") return n;
    if (m[2] === "px") return n * 0.75;
    if (m[2] === "in") return n * 72;
    if (m[2] === "%") return { rel: n / 100 };
    return { rel: n };
  }
  const fn = v.match(/^(max|min|clamp)\((.*)\)$/s);
  if (fn) {
    const args = [];
    let depthP = 0;
    let cur = "";
    for (const ch of fn[2]) {
      if (ch === "(") depthP++;
      if (ch === ")") depthP--;
      if (ch === "," && !depthP) (args.push(cur), (cur = ""));
      else cur += ch;
    }
    args.push(cur);
    const rs = args.map((a) => resolve(a, map, depth + 1));
    if (fn[1] === "clamp") return rs[0];
    const pts = rs.filter((r) => typeof r === "number");
    if (fn[1] === "max") {
      if (pts.length) return Math.max(...pts);
      return rs.find((r) => r) ?? null;
    }
    return pts.length ? Math.min(...pts) : (rs.find((r) => r) ?? null);
  }
  return null;
}

describe("the 10pt reading floor", () => {
  test("--fs-floor is 10pt", () => {
    expect(read("styles/dc-palette.css")).toMatch(/--fs-floor:\s*10pt/);
  });

  test("no font-size in any stylesheet resolves below the floor", () => {
    const map = tokens();
    const bad = [];
    let checked = 0;
    for (const rel of sheets) {
      postcss.parse(read(rel)).walkDecls("font-size", (d) => {
        const r = resolve(d.value, map);
        if (r === null) return; // cannot be resolved without layout (calc, inherit, keywords)
        checked++;
        const where = `${rel}:${d.source?.start?.line}: ${d.parent?.selector ?? "?"} { font-size: ${d.value} }`;
        // a relative size is judged against the parent, which is itself >= the floor: 1em and up keeps it
        if (typeof r === "number" ? r < FLOOR_PT - 0.01 : r.rel < 1 && !/max\(/.test(d.value)) bad.push(where);
      });
    }
    expect(checked, "resolved no font-size declarations, so the scan is not looking at anything").toBeGreaterThan(40);
    expect(bad, "a font-size below 10pt: raise it to var(--fs-floor), or wrap a relative size in max(…, var(--fs-floor))").toEqual([]);
  });
});
