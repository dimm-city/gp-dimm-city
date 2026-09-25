// dev-registry — serve THIS checkout as an npm registry, so a book can
// `gutterpress ext add gp-dimm-city@<version>` through Gutterpress's real npm
// install path before anything is published.
//
//   bun scripts/dev-registry.mjs            # packs, then serves on 127.0.0.1:4873
//   PORT=5000 bun scripts/dev-registry.mjs
//
// Then, in another shell, for the install AND every build that follows:
//   export GUTTERPRESS_NPM_REGISTRY=http://127.0.0.1:4873
//   gutterpress ext add gp-dimm-city@1.0.0 path/to/book
//   gutterpress build path/to/book --format pdf
//
// Why the env var must stay set for builds: the vendored copy's receipt
// records the tarball's origin, and Gutterpress re-verifies it against the
// configured registry on every load. That is also why a tree vendored from
// this registry must never be committed — its receipt names 127.0.0.1.
//
// Serves exactly what Gutterpress asks for (npm-plugin-installer.ts): the
// abbreviated packument at /<name> with dist.tarball (same origin) and
// dist.integrity, and the tarball itself. Nothing else.
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PORT = Number(process.env.PORT ?? 4873);
const HOST = "127.0.0.1";

const out = mkdtempSync(path.join(tmpdir(), "gp-dimm-city-registry-"));
const [packed] = JSON.parse(execFileSync("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", out], { cwd: ROOT, encoding: "utf8", stdio: ["ignore", "pipe", "inherit"] }));
const pkg = JSON.parse(readFileSync(path.join(ROOT, "package.json"), "utf8"));
const base = `http://${HOST}:${PORT}`;
const tarballPath = `/${pkg.name}/-/${packed.filename}`;
const tarball = readFileSync(path.join(out, packed.filename));

const packument = {
  name: pkg.name,
  "dist-tags": { latest: pkg.version },
  versions: {
    [pkg.version]: {
      ...pkg,
      dist: { tarball: base + tarballPath, integrity: packed.integrity, shasum: packed.shasum },
    },
  },
  modified: new Date().toISOString(),
};

createServer((req, res) => {
  const url = req.url.split("?")[0];
  if (url === `/${pkg.name}` || url === `/${encodeURIComponent(pkg.name)}`) {
    const body = JSON.stringify(packument);
    res.writeHead(200, { "content-type": "application/json", "content-length": Buffer.byteLength(body) });
    res.end(body);
  } else if (url === tarballPath) {
    res.writeHead(200, { "content-type": "application/octet-stream", "content-length": tarball.length });
    res.end(tarball);
  } else {
    res.writeHead(404, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "not found" }));
  }
  console.log(`${res.statusCode} ${req.method} ${url}`);
}).listen(PORT, HOST, () => {
  console.log(`serving ${pkg.name}@${pkg.version} (${packed.filename}, ${(packed.size / 1e6).toFixed(1)} MB, ${packed.integrity.slice(0, 20)}…)`);
  console.log(`export GUTTERPRESS_NPM_REGISTRY=${base}`);
});
