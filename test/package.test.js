// package.test.js — what npm would publish, and whether Gutterpress can load it.
//
// Ported from dc-op-manual's tools/extension-package.test.mjs and extended
// with the checks that would have caught the two bugs found when this package
// was first test-installed through Gutterpress's npm path:
//   - the entry is ESM but package.json had no "type": "module", so the npm
//     loader parsed it as CommonJS and refused it;
//   - dc-native.css referenced an image that `files` never shipped, so every
//     book failed at build time with "Missing asset".
// The old test only checked paths DECLARED in package.json. This one also
// follows every url() inside every declared stylesheet.
//
// `npm pack --dry-run --json` is the same packer `npm publish` uses; it needs
// `npm` on PATH (CI runners and any Node install have it).
import { describe, expect, test } from "bun:test";
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pkg = JSON.parse(readFileSync(path.join(ROOT, "package.json"), "utf8"));
const gp = pkg.gutterpress ?? {};
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");

/** The containment rule Gutterpress enforces (extension-manifest.ts pathEscapesFolder). */
const escapesFolder = (rel) => path.isAbsolute(rel) || rel.split(/[\\/]/).includes("..");

/** Licence file names Gutterpress's asset.font.license check accepts (checks/asset/font-license.ts). */
const LICENSE_NAMES = ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENCE.txt", "OFL.txt", "OFL-1.1.txt", "COPYING"];
const FONT_EXTS = [".woff", ".woff2", ".otf", ".ttf", ".eot"];

const EXPECTED_LAYER_STATEMENT = "@layer dc.tokens, dc.base, dc.components, dc.templates, dc.pages;";

function declaredPaths() {
  const out = [pkg.main, ...(gp.styles ?? []), gp.tokensFile, gp.components, gp.snippets].filter(Boolean);
  return [...new Set(out)];
}

/** Every local url() target in a stylesheet, resolved relative to that sheet. */
function cssAssetRefs(rel) {
  const css = read(rel);
  const dir = path.posix.dirname(rel);
  const refs = [];
  for (const m of css.matchAll(/url\(\s*["']?([^"')]+?)["']?\s*\)/g)) {
    const target = m[1].trim();
    // Skip data URIs, remote URLs, and fragment references — including the
    // `url(%23g)` an inline SVG data URI carries for its own gradient id.
    if (/^(data:|https?:|#|%23)/.test(target)) continue;
    refs.push({ sheet: rel, target, resolved: path.posix.normalize(path.posix.join(dir, target.split(/[?#]/)[0])) });
  }
  return refs;
}

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = path.join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

let packedFiles;
function packed() {
  if (!packedFiles) {
    const raw = execFileSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
    const [entry] = JSON.parse(raw);
    packedFiles = { paths: new Set(entry.files.map((f) => f.path)), size: entry.size, unpackedSize: entry.unpackedSize };
  }
  return packedFiles;
}

describe("package.json identity", () => {
  test("is the shape Gutterpress's npm loader needs", () => {
    expect(pkg.name).toBe("gp-dimm-city");
    expect(pkg.type).toBe("module"); // an ESM .js entry is parsed as CommonJS without this
    expect(pkg.main).toBe("plugin.js");
    expect(pkg.keywords).toContain("gutterpress"); // the keyword `ext search` and the desktop filter on
    expect(pkg.dependencies).toBeUndefined(); // the plugin imports nothing
    expect(gp.engineStyles).toBeUndefined(); // rejected by Gutterpress
    expect(gp.markdown).toBeUndefined(); // for npm the entry IS the markdown-it plugin
    expect(pkg.module).toBeUndefined(); // would take priority over main
    expect(pkg.exports).toBeUndefined();
  });

  test("declares a valid licence and the repository provenance needs", () => {
    expect(pkg.license).toMatch(/^[A-Za-z0-9.+-]+( (AND|OR) [A-Za-z0-9.+-]+)*$/);
    expect(pkg.license).not.toBe("CC-BY"); // the old, invalid identifier
    expect(pkg.repository?.url).toMatch(/github\.com\/dimm-city\/gp-dimm-city/);
  });

  test("declares no glob styles", () => {
    for (const s of gp.styles ?? []) expect(s).not.toMatch(/[*?]/);
  });
});

describe("declared paths", () => {
  test("every declared path exists and stays inside the package", () => {
    const declared = declaredPaths();
    expect(declared.length).toBeGreaterThan(0);
    for (const rel of declared) {
      expect(escapesFolder(rel)).toBe(false);
      expect(existsSync(path.join(ROOT, rel))).toBe(true);
    }
  });

  test("snippets is a flat folder of .md files, each with a placeholder", () => {
    const dir = path.join(ROOT, gp.snippets);
    const entries = readdirSync(dir);
    expect(entries.length).toBeGreaterThan(0);
    for (const entry of entries) {
      expect(entry.endsWith(".md")).toBe(true);
      expect(statSync(path.join(dir, entry)).isFile()).toBe(true);
      expect(read(path.posix.join(gp.snippets, entry))).toMatch(/\{\{\s*[a-zA-Z0-9_.-]+\s*\}\}/);
    }
  });
});

describe("the tarball npm would publish", () => {
  test("ships every declared path", () => {
    for (const rel of declaredPaths()) {
      if (rel === gp.snippets) continue; // a folder; its files are checked below
      expect(packed().paths.has(rel)).toBe(true);
    }
    for (const entry of readdirSync(path.join(ROOT, gp.snippets))) {
      expect(packed().paths.has(path.posix.join(gp.snippets, entry))).toBe(true);
    }
  });

  test("ships every asset the stylesheets reference (fonts, images)", () => {
    const refs = (gp.styles ?? []).flatMap(cssAssetRefs);
    expect(refs.length).toBeGreaterThan(0);
    for (const { sheet, target, resolved } of refs) {
      expect(escapesFolder(resolved)).toBe(false);
      expect(existsSync(path.join(ROOT, resolved))).toBe(true);
      // The check that would have caught images/brick-bg-01.png going missing.
      if (!packed().paths.has(resolved)) throw new Error(`${sheet} references ${target} but npm pack would not ship ${resolved}`);
    }
  });

  test("ships nothing it should not, and stays within Gutterpress's limits", () => {
    for (const p of packed().paths) {
      expect(p.startsWith("test/")).toBe(false);
      expect(p.startsWith("docs/")).toBe(false);
      expect(p.startsWith("scripts/")).toBe(false);
      expect(p.split("/")).not.toContain("node_modules");
      // Windows-safe: Gutterpress refuses paths it cannot vendor on every OS.
      expect(p).not.toMatch(/[<>:"|?*]/);
      for (const seg of p.split("/")) {
        expect(seg).not.toMatch(/[. ]$/);
        expect(seg.toLowerCase()).not.toMatch(/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$/);
      }
    }
    expect(packed().unpackedSize).toBeLessThan(50 * 1024 * 1024);
  });
});

describe("fonts", () => {
  const fontFiles = walk(path.join(ROOT, "fonts")).filter((p) => FONT_EXTS.includes(path.extname(p).toLowerCase()));

  test("every font file is referenced by exactly one @font-face", () => {
    const refs = (gp.styles ?? []).flatMap(cssAssetRefs).filter((r) => FONT_EXTS.includes(path.extname(r.resolved).toLowerCase()));
    const counts = new Map();
    for (const r of refs) counts.set(r.resolved, (counts.get(r.resolved) ?? 0) + 1);
    expect(fontFiles.length).toBeGreaterThan(0);
    for (const abs of fontFiles) {
      const rel = path.relative(ROOT, abs).split(path.sep).join("/");
      expect(counts.get(rel) ?? 0).toBe(1);
    }
  });

  test("every directory that holds font files ships a licence beside them", () => {
    const dirs = new Set(fontFiles.map((p) => path.dirname(p)));
    for (const dir of dirs) {
      const present = readdirSync(dir).filter((f) => LICENSE_NAMES.includes(f));
      if (present.length === 0) throw new Error(`${path.relative(ROOT, dir)} has font files but no licence file (one of: ${LICENSE_NAMES.join(", ")})`);
      for (const f of present) {
        const rel = path.relative(ROOT, path.join(dir, f)).split(path.sep).join("/");
        expect(packed().paths.has(rel)).toBe(true);
      }
    }
  });
});

describe("cascade contract", () => {
  const styles = gp.styles ?? [];

  test("dc-fonts.css is first and carries the layer order statement", () => {
    expect(styles[0]).toBe("styles/dc-fonts.css");
    expect(read(styles[0])).toContain(EXPECTED_LAYER_STATEMENT);
    expect(read(styles[0])).not.toMatch(/dc\.guide/); // dropped in 1.0.0
  });

  test("dc-native.css is last and unlayered", () => {
    expect(styles.at(-1)).toBe("styles/dc-native.css");
    expect(read(styles.at(-1))).not.toMatch(/@layer/);
  });

  test("every other sheet keeps all of its rules inside its own dc.* layer", () => {
    for (const rel of styles.slice(1, -1)) {
      const css = read(rel).replace(/\/\*[\s\S]*?\*\//g, "");
      const open = css.match(/@layer\s+(dc\.[a-z]+)\s*\{/);
      expect(open, `${rel} has no @layer dc.<name> { block`).toBeTruthy();
      const before = css.slice(0, open.index).trim();
      expect(before, `${rel} has rules before its @layer block: ${before.slice(0, 80)}`).toBe("");
      // The block must run to the end of the file: strip it and expect nothing left.
      const afterOpen = css.slice(open.index + open[0].length);
      let depth = 1;
      let i = 0;
      for (; i < afterOpen.length && depth > 0; i++) {
        if (afterOpen[i] === "{") depth++;
        else if (afterOpen[i] === "}") depth--;
      }
      expect(depth, `${rel}: unbalanced braces`).toBe(0);
      expect(afterOpen.slice(i).trim(), `${rel} has rules after its @layer block`).toBe("");
    }
  });
});

describe("component catalog", () => {
  test("every css path it cites exists in the package", () => {
    const yaml = read(gp.components);
    const cited = new Set([...yaml.matchAll(/(?:^|[\s\[,])((?:styles\/)[A-Za-z0-9_./-]+\.css)/gm)].map((m) => m[1]));
    expect(cited.size).toBeGreaterThan(0);
    for (const rel of cited) expect(existsSync(path.join(ROOT, rel)), `components.yaml cites ${rel}`).toBe(true);
    expect(yaml).not.toMatch(/css\/[a-z-]+\.css/); // old css/ paths from the book repo
    expect(yaml).not.toMatch(/dg-overrides|fg-overrides/);
  });
});
