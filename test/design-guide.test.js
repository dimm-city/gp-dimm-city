// design-guide.test.js — the design guide (design-guide/) is this package's
// fixture: it is the book that documents the package AND the markdown every
// test here renders through core's pipeline with the working-copy plugin.
//
//   - the manifest loads the package from this repository (`../`), never a
//     published pin — otherwise the guide would be testing npm, not the diff;
//   - every chapter renders without a layout warning or an unrendered marker;
//   - every macro and alert type the plugin handles is demonstrated somewhere
//     in the guide, so a new macro cannot ship undocumented;
//   - each chapter's rendered HTML is snapshotted. A change to the plugin's
//     output fails here until the snapshot is updated ON PURPOSE
//     (`bun run test:update-snapshot`) and the diff reviewed with the code.
import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createMarkdownRenderer } from "gutterpress/render";

import plugin from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const GUIDE = path.join(ROOT, "design-guide");
const read = (rel) => readFileSync(path.join(GUIDE, rel), "utf8");

/** The manifest with its comment lines dropped — a comment may quote a pin as an example. */
const manifest = read("manifest.yaml").replace(/^[ \t]*#.*\n/gm, "");
/** The chapters, in manifest order — the only `.md` entries in the manifest. */
const chapters = [...manifest.matchAll(/^\s*-\s*(\S+\.md)\s*$/gm)].map((m) => m[1]);

/** Markers the plugin recognises but deliberately renders as nothing. */
const DEPRECATED_MARKERS = new Set(["@roll-table", "@options-table"]);

function render(rel) {
  const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {} }]);
  const env = {};
  const html = md.render(read(rel), env);
  return { html, warnings: env.layoutWarnings ?? [] };
}

/** Core stamps every block with its source line; strip that so a prose edit above a specimen does not churn the snapshot. */
const stripSourceLines = (html) => html.replace(/ data-source-range="[^"]*" data-source-line="[^"]*"/g, "");

describe("the manifest", () => {
  test("loads the package from this repository, not a published version", () => {
    const extensions = manifest.match(/^extensions:\n((?:[ \t]+-.*\n)+)/m)?.[1] ?? "";
    expect(extensions.trim()).toBe("- ../");
    expect(manifest).not.toMatch(/gp-dimm-city@/);
  });

  test("lists every chapter on disk, and every chapter it lists exists", () => {
    const onDisk = readdirSync(GUIDE).filter((f) => f.endsWith(".md")).sort();
    expect(chapters.length).toBeGreaterThan(0);
    expect([...chapters].sort()).toEqual(onDisk);
  });
});

describe("every chapter", () => {
  for (const rel of chapters) {
    test(`${rel} renders without layout warnings or unrendered markers`, () => {
      const { html, warnings } = render(rel);
      expect(warnings).toEqual([]);
      // A marker the plugin did not consume is left as a paragraph of text.
      expect(html.match(/<p[^>]*>@[a-z-]+/g) ?? []).toEqual([]);
    });

    test(`${rel} references only local images that exist`, () => {
      const prose = read(rel).replace(/^```[\s\S]*?^```/gm, ""); // a code block may show an example path
      const refs = [...prose.matchAll(/!\[[^\]]*\]\(([^)\s]+)/g)].map((m) => m[1]).filter((r) => !/^https?:/.test(r));
      for (const ref of refs) expect(existsSync(path.join(GUIDE, ref)), `${rel} → ${ref}`).toBe(true);
    });
  }
});

describe("coverage", () => {
  const source = chapters.map(read).join("\n");
  const code = readFileSync(path.join(ROOT, "plugin.js"), "utf8");

  test("the guide demonstrates every macro the plugin handles", () => {
    // Every marker literal the plugin matches on, e.g. parseMarker(tok, tokens, i, '@skill').
    const macros = [...new Set([...code.matchAll(/'(@[a-z-]+)'/g)].map((m) => m[1]))]
      .filter((m) => !m.startsWith("@end-") && !DEPRECATED_MARKERS.has(m));
    expect(macros.length).toBeGreaterThan(20);
    const missing = macros.filter((m) => !new RegExp(`^${m}(\\s|$)`, "m").test(source));
    expect(missing).toEqual([]);
  });

  test("the guide demonstrates every alert type the plugin handles", () => {
    const table = code.match(/DC_ALERT_TYPES = \{([\s\S]*?)\n\};/)?.[1] ?? "";
    const types = [...table.matchAll(/^\s*([A-Z_]+):/gm)].map((m) => m[1]);
    expect(types.length).toBeGreaterThan(5);
    const missing = types.filter((t) => !source.includes(`[!${t}]`));
    expect(missing).toEqual([]);
  });
});

describe("rendered output", () => {
  for (const rel of chapters) {
    test(`${rel} matches its snapshot`, () => {
      expect(stripSourceLines(render(rel).html)).toMatchSnapshot();
    });
  }
});
