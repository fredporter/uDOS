import { deepStrictEqual, strictEqual } from "node:assert";
import { mkdtemp, rm, access, cp, readdir } from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_VAULT = path.join(__dirname, "fixtures", "vault");
const THEMES_ROOT = path.join(__dirname, "..", "..", "..", "themes");
const CLI_PATH = fileURLToPath(new URL("../dist/renderer/cli.js", import.meta.url));

async function copyVaultFixture() {
  const tmpVault = await mkdtemp(path.join(os.tmpdir(), "udos-renderer-vault-"));
  await cp(FIXTURE_VAULT, tmpVault, { recursive: true });
  return tmpVault;
}

async function runCli(vaultRoot, outputRoot, missionId) {
  return new Promise((resolve, reject) => {
    const args = [
      CLI_PATH,
      "--theme",
      "prose",
      "--vault",
      vaultRoot,
      "--themes",
      THEMES_ROOT,
      "--output",
      outputRoot,
      "--mission",
      missionId,
    ];
    const child = spawn(process.execPath, args, { env: process.env });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        return reject(new Error(`CLI exit ${code}: ${stderr || stdout}`));
      }
      try {
        const payload = JSON.parse(stdout.trim().split("\n").pop());
        resolve(payload);
      } catch (error) {
        reject(new Error(`Invalid JSON output: ${error} | stdout=${stdout} | stderr=${stderr}`));
      }
    });
  });
}

async function assertReportWritten(vaultRoot, missionId) {
  const runsDir = path.join(vaultRoot, "06_RUNS", missionId);
  const entries = await readdir(runsDir);
  const hasReport = entries.some((name) => name.endsWith(".json"));
  strictEqual(hasReport, true, "should write run report");
}

async function main() {
  const tmpVaultA = await copyVaultFixture();
  const tmpVaultB = await copyVaultFixture();
  const tmpOutA = await mkdtemp(path.join(os.tmpdir(), "udos-renderer-out-"));
  const tmpOutB = await mkdtemp(path.join(os.tmpdir(), "udos-renderer-out-"));
  try {
    const resultA = await runCli(tmpVaultA, tmpOutA, "renderer-cli-test-a");
    const resultB = await runCli(tmpVaultB, tmpOutB, "renderer-cli-test-b");

    strictEqual(resultA.theme, "prose");
    strictEqual(resultB.theme, "prose");

    const pathsA = resultA.files.map((f) => f.path);
    const pathsB = resultB.files.map((f) => f.path);
    deepStrictEqual(pathsA, pathsB, "file list should be deterministic");

    const navTitles = resultA.nav.map((entry) => entry.title);
    const sorted = [...navTitles].sort();
    deepStrictEqual(navTitles, sorted, "navigation should be deterministically sorted");

    await access(path.join(tmpOutA, "prose", "theme.css"));
    await access(path.join(tmpOutA, "prose", "assets", "tokens.css"));

    await assertReportWritten(tmpVaultA, "renderer-cli-test-a");
  } finally {
    await rm(tmpVaultA, { recursive: true, force: true });
    await rm(tmpVaultB, { recursive: true, force: true });
    await rm(tmpOutA, { recursive: true, force: true });
    await rm(tmpOutB, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error("Renderer CLI regression test failed:", error);
  process.exit(1);
});
