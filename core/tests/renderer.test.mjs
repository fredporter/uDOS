import { deepStrictEqual, strictEqual } from "node:assert";
import { mkdtemp, rm, access } from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_VAULT = path.join(__dirname, "fixtures", "vault");
const THEMES_ROOT = path.join(__dirname, "..", "..", "themes");

function buildOptions(outputRoot) {
  return {
    vaultRoot: FIXTURE_VAULT,
    themeName: "prose",
    themesRoot: THEMES_ROOT,
    outputRoot,
  };
}

async function main() {
  const { renderVault } = await import("../dist/renderer/index.js");

  const tmpA = await mkdtemp(path.join(os.tmpdir(), "udos-renderer-test-"));
  const tmpB = await mkdtemp(path.join(os.tmpdir(), "udos-renderer-test-"));
  try {
    const renderA = await renderVault(buildOptions(tmpA));
    const renderB = await renderVault(buildOptions(tmpB));

    strictEqual(renderA.files.length, 2, "should render two markdown fixtures");
    strictEqual(renderB.files.length, 2, "second run should match fixture count");

    const pathsA = renderA.files.map((f) => f.path);
    const pathsB = renderB.files.map((f) => f.path);
    deepStrictEqual(pathsA, pathsB, "file list should be deterministic");

    const navTitles = renderA.nav.map((entry) => entry.title);
    const sorted = [...navTitles].sort();
    deepStrictEqual(navTitles, sorted, "navigation should be deterministically sorted");

    await access(path.join(tmpA, "prose", "theme.css"));
    await access(path.join(tmpA, "prose", "assets", "tokens.css"));
  } finally {
    await rm(tmpA, { recursive: true, force: true });
    await rm(tmpB, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error("Renderer regression test failed:", error);
  process.exit(1);
});
