/*
 * uDOS Data Runner
 * Implements RUN DATA subcommands via Node runtime.
 *
 * Usage:
 *   node data_runner.js list
 *   node data_runner.js validate <id>
 *   node data_runner.js build <id> [output_id]
 *   node data_runner.js regen <id> [output_id]
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..", "..");

function loadJson(filePath, fallback = null) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return fallback;
  }
}

function resolvePath(p) {
  if (path.isAbsolute(p)) return p;
  return path.resolve(repoRoot, p);
}

function parseCell(cellId) {
  const clean = String(cellId || "").trim().toUpperCase();
  const match = /^([A-Z]+)(\d+)$/.exec(clean);
  if (!match) return null;
  const colStr = match[1];
  const row = Number(match[2]);
  let col = 0;
  for (const ch of colStr) {
    col = col * 26 + (ch.charCodeAt(0) - 64);
  }
  return { col: col - 1, row };
}

function gridBounds() {
  const cfg = loadJson(path.resolve(repoRoot, "core", "config", "grid.json"), {});
  const standard = cfg?.viewports?.standard || {};
  return {
    cols: Number(standard.cols || 80),
    rows: Number(standard.rows || 30),
  };
}

function loadDatasets() {
  const cfg = loadJson(path.resolve(repoRoot, "core", "config", "datasets.json"), {});
  const datasets = Array.isArray(cfg.datasets) ? cfg.datasets : [];
  const outputs = typeof cfg.outputs === "object" && cfg.outputs ? cfg.outputs : {};
  return { datasets, outputs };
}

function listDatasets() {
  const { datasets } = loadDatasets();
  return {
    status: "success",
    datasets: datasets.map((d) => ({ id: d.id || "", type: d.type || "", path: d.path || "" })),
  };
}

function validateDataset(datasetId) {
  const { datasets } = loadDatasets();
  const ds = datasets.find((d) => d.id === datasetId);
  if (!ds) return { status: "error", message: `Unknown dataset: ${datasetId}` };

  const datasetPath = resolvePath(ds.path || "");
  if (!fs.existsSync(datasetPath)) {
    return { status: "error", message: `Dataset file not found: ${datasetPath}` };
  }

  if (ds.type !== "locations") {
    return { status: "success", message: "Dataset exists", valid: true };
  }

  const payload = loadJson(datasetPath, {});
  const locations = Array.isArray(payload.locations) ? payload.locations : [];
  const { cols, rows } = gridBounds();

  const bad = [];
  for (const loc of locations) {
    const locId = loc?.id || "unknown";
    const tiles = loc?.tiles || {};
    for (const cellId of Object.keys(tiles)) {
      const parsed = parseCell(cellId);
      if (!parsed) {
        bad.push({ location: locId, cell: cellId, reason: "parse" });
        continue;
      }
      if (parsed.col >= cols || parsed.row >= rows) {
        bad.push({ location: locId, cell: cellId, reason: "bounds" });
      }
    }
  }

  if (bad.length) {
    return {
      status: "warning",
      message: "Dataset validation warnings",
      invalid: bad.length,
      sample: bad.slice(0, 20),
    };
  }

  return { status: "success", message: "Dataset valid", valid: true };
}

function buildDataset(datasetId, outputId, mode) {
  if (datasetId !== "locations") {
    return { status: "error", message: "Only locations build is supported" };
  }
  const { datasets, outputs } = loadDatasets();
  const key = outputId || `${datasetId}_unified`;
  const outRel = outputs[key];
  if (!outRel) return { status: "error", message: `No output configured for key: ${key}` };

  const { cols, rows } = gridBounds();
  const merged = {
    description: "Unified locations dataset",
    grid: { cols, rows },
    locations: [],
  };

  const seen = new Set();
  let dropped = 0;
  const normalize = mode === "regen";

  for (const ds of datasets) {
    if (ds.type !== "locations") continue;
    const sourcePath = resolvePath(ds.path || "");
    const payload = loadJson(sourcePath, null);
    if (!payload || !Array.isArray(payload.locations)) continue;

    for (const loc of payload.locations) {
      const locId = loc?.id;
      if (!locId || seen.has(locId)) continue;

      const tiles = typeof loc.tiles === "object" && loc.tiles ? loc.tiles : {};
      const cleaned = {};
      for (const [cellId, tile] of Object.entries(tiles)) {
        const normalized = normalize ? String(cellId).trim().toUpperCase().replace(/\s+/g, "") : cellId;
        const parsed = parseCell(normalized);
        if (!parsed) {
          dropped += 1;
          continue;
        }
        if (parsed.col >= cols || parsed.row >= rows) {
          dropped += 1;
          continue;
        }
        cleaned[normalized] = tile;
      }
      merged.locations.push({ ...loc, tiles: cleaned });
      seen.add(locId);
    }
  }

  const outPath = resolvePath(outRel);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(merged, null, 2));

  return {
    status: "success",
    message: `Built ${datasetId} dataset`,
    output: outPath,
    locations: merged.locations.length,
    dropped_cells: dropped,
    mode,
  };
}

function main() {
  const args = process.argv.slice(2);
  const action = (args[0] || "").toLowerCase();
  let result = { status: "error", message: "Usage: list|validate|build|regen ..." };

  if (action === "list") {
    result = listDatasets();
  } else if (action === "validate") {
    result = validateDataset(args[1]);
  } else if (action === "build") {
    result = buildDataset(args[1], args[2], "build");
  } else if (action === "regen") {
    result = buildDataset(args[1], args[2], "regen");
  }

  process.stdout.write(JSON.stringify(result));
}

main();
