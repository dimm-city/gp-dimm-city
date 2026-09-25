// Regenerate test/fixtures/all-macros.expected.html from the current plugin.
//
// Run this ONLY when the plugin's output is meant to change; review the
// resulting diff of the snapshot as carefully as the code change itself.
//   bun run test:update-snapshot
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createMarkdownRenderer } from "gutterpress/render";

import plugin from "../plugin.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixture = path.join(ROOT, "test/fixtures/all-macros.md");
const snapshot = path.join(ROOT, "test/fixtures/all-macros.expected.html");

const md = createMarkdownRenderer([{ name: "gp-dimm-city", plugin, options: {} }]);
const env = {};
const html = md.render(readFileSync(fixture, "utf8"), env);
if ((env.layoutWarnings ?? []).length) {
  console.error("Refusing to snapshot output that carries layout warnings:", env.layoutWarnings);
  process.exit(1);
}
writeFileSync(snapshot, html);
console.log(`wrote ${path.relative(ROOT, snapshot)} (${html.length} bytes) — now review \`git diff\` on it`);
