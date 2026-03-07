import { cpSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, stdio: "inherit" });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

const here = path.dirname(fileURLToPath(import.meta.url));
const coreRoot = path.resolve(here, "..");
const repoRoot = path.resolve(coreRoot, "..");
const demoRoot = path.resolve(repoRoot, ".artifacts", "release-demos", "demo-ts-runtime-v1.5");
const distRoot = path.resolve(coreRoot, "dist");

run("npm", ["run", "build:strict"], coreRoot);
run("npm", ["run", "test:renderer"], coreRoot);
run("npm", ["run", "test:renderer-cli"], coreRoot);

rmSync(demoRoot, { recursive: true, force: true });
mkdirSync(demoRoot, { recursive: true });
cpSync(distRoot, path.join(demoRoot, "dist"), { recursive: true });

const manifest = {
  runtime: "v1.5",
  strict: true,
  generated_at: new Date().toISOString(),
  node: process.version,
  demo_script: "npm run demo:dist:v1.5",
  dist_source: distRoot,
};
writeFileSync(path.join(demoRoot, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf-8");

console.log(`Strict TS distributable demo created at ${demoRoot}`);
