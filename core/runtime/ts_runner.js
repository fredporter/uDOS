/*
 * uDOS TS Runtime Runner
 *
 * Usage:
 *   node ts_runner.js <markdown_file> [section_id]
 *   node ts_runner.js --parse <markdown_file>
 *
 * Outputs JSON to stdout with execution result.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error(
      "Usage: node ts_runner.js <markdown_file> [section_id] | --parse <markdown_file>"
    );
    process.exit(1);
  }

  let parseOnly = false;
  let fileArgIndex = 0;
  let allSections = false;
  if (args[0] === "--parse" || args[0] === "-p") {
    parseOnly = true;
    fileArgIndex = 1;
  } else if (args[0] === "--all") {
    allSections = true;
    fileArgIndex = 1;
  }

  if (!args[fileArgIndex]) {
    console.error(
      "Usage: node ts_runner.js <markdown_file> [section_id] | --parse <markdown_file> | --all <markdown_file>"
    );
    process.exit(1);
  }

  const filePath = path.resolve(args[fileArgIndex]);
  const sectionId = parseOnly || allSections ? null : args[fileArgIndex + 1] || null;

  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  const repoRoot = path.resolve(__dirname, "..", "..");
  const configPath = path.resolve(repoRoot, "core", "config", "runtime.json");
  let runtimeEntry = path.resolve(repoRoot, "core", "grid-runtime", "dist", "index.js");

  try {
    if (fs.existsSync(configPath)) {
      const cfg = JSON.parse(fs.readFileSync(configPath, "utf8"));
      if (cfg.runtime_entry) {
        runtimeEntry = path.resolve(repoRoot, cfg.runtime_entry);
      }
    }
  } catch (err) {
    // Ignore config read errors and fallback to default.
  }

  if (!fs.existsSync(runtimeEntry)) {
    console.error(`Runtime entry not found: ${runtimeEntry}`);
    console.error("Build the TS runtime in core/grid-runtime (npm run build).");
    process.exit(1);
  }

  // Dynamic import for ES module
  (async () => {
    try {
      const runtimeModule = await import(runtimeEntry);
      const Runtime = runtimeModule.Runtime;

      const markdown = fs.readFileSync(filePath, "utf8");
      const runtime = new Runtime({ allowScripts: false });
      runtime.load(markdown);

      const doc = runtime.getDocument();
      const sections = doc ? doc.sections : [];
      if (!sections || sections.length === 0) {
        console.error("No sections found in markdown. Add a '## Section' header.");
        process.exit(1);
      }

      if (parseOnly) {
        const normalized = sections.map((section) => ({
          id: section.id,
          title: section.title || section.heading || section.name || "",
          blocks: Array.isArray(section.blocks) ? section.blocks.length : 0,
        }));
        console.log(JSON.stringify({ sections: normalized }));
        return;
      }

      let target = sectionId;
      if (!target && !allSections) {
        target = sections[0].id;
      }

      const result = await runtime.execute(target);
      console.log(JSON.stringify({ section: target, result }));
    } catch (err) {
      console.error(String(err));
      process.exit(1);
    }
  })();
}

main();
