import { existsSync, lstatSync, mkdirSync, readlinkSync, rmSync, symlinkSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

const needsInstall =
  !existsSync("node_modules/typescript/package.json") ||
  !existsSync("node_modules/@types/node/package.json");

if (needsInstall) {
  run("npm", ["install", "--no-audit", "--no-fund"]);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const coreRoot = path.resolve(here, "..");
const artifactNodeModules = path.resolve(coreRoot, "..", "dev", "build-artifacts", "core", "node_modules");
const coreNodeModules = path.resolve(coreRoot, "node_modules");
mkdirSync(path.dirname(artifactNodeModules), { recursive: true });

if (existsSync(artifactNodeModules)) {
  const stats = lstatSync(artifactNodeModules);
  if (!stats.isSymbolicLink()) {
    rmSync(artifactNodeModules, { recursive: true, force: true });
  } else {
    const linkedTarget = readlinkSync(artifactNodeModules);
    if (path.resolve(path.dirname(artifactNodeModules), linkedTarget) !== coreNodeModules) {
      rmSync(artifactNodeModules, { recursive: true, force: true });
    }
  }
}
if (!existsSync(artifactNodeModules)) {
  try {
    symlinkSync(coreNodeModules, artifactNodeModules, "dir");
  } catch (error) {
    if (error && error.code !== "EEXIST") {
      throw error;
    }
  }
}

run("npm", ["exec", "--yes", "--", "tsc", "-p", "tsconfig.json"]);
