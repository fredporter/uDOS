/*
 * uDOS Pattern Runner
 * Node-backed pattern rendering for DRAW PAT subcommands.
 *
 * Usage:
 *   node pattern_runner.js list
 *   node pattern_runner.js render <pattern>
 *   node pattern_runner.js cycle [seconds]
 *   node pattern_runner.js text <message...>
 */

const PATTERNS = ["c64", "chevrons", "scanlines", "raster", "progress", "mosaic"];

function renderLine(pattern, i, width = 64) {
  if (pattern === "c64") return "█".repeat((i % width) + 1).padEnd(width, " ");
  if (pattern === "chevrons") return Array.from({ length: width }, (_, x) => ((x + i) % 4 < 2 ? "/" : "\\")).join("");
  if (pattern === "scanlines") return i % 2 === 0 ? "─".repeat(width) : " ".repeat(width);
  if (pattern === "raster") return Array.from({ length: width }, (_, x) => ((x + i) % 6 < 3 ? "▓" : "░")).join("");
  if (pattern === "progress") return `${"■".repeat((i % 20) + 1).padEnd(20, "·")} ${(i * 5) % 100}%`;
  return Array.from({ length: width }, (_, x) => ((x + i) % 5 === 0 ? "█" : "·")).join("");
}

function renderPattern(name) {
  const pattern = PATTERNS.includes(name) ? name : "mosaic";
  const lines = [];
  for (let i = 0; i < 20; i += 1) lines.push(renderLine(pattern, i));
  return {
    status: "success",
    pattern,
    output: lines.join("\n"),
  };
}

function renderCycle(seconds) {
  const parts = [];
  for (const p of PATTERNS) {
    parts.push(`=== ${p.toUpperCase()} (${seconds}s) ===`);
    parts.push(renderPattern(p).output);
    parts.push("");
  }
  return { status: "success", output: parts.join("\n"), patterns: PATTERNS };
}

function renderText(message) {
  const text = (message || "").trim();
  if (!text) return { status: "error", message: "Missing text" };
  return {
    status: "success",
    output: text.toUpperCase(),
  };
}

function main() {
  const args = process.argv.slice(2);
  const action = (args[0] || "list").toLowerCase();
  let result = { status: "error", message: "Unknown action" };

  if (action === "list") result = { status: "success", patterns: PATTERNS };
  else if (action === "render") result = renderPattern((args[1] || "").toLowerCase());
  else if (action === "cycle") result = renderCycle(Number(args[1] || 5));
  else if (action === "text") result = renderText(args.slice(1).join(" "));

  process.stdout.write(JSON.stringify(result));
}

main();
