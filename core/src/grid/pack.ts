import { GridCanvasSpec, RenderResult } from "./types.js";

export function packageGrid(spec: GridCanvasSpec, lines: string[]): RenderResult {
  const width = Number.isFinite(spec.width) && spec.width > 0 ? Math.floor(spec.width) : 80;
  const height = Number.isFinite(spec.height) && spec.height > 0 ? Math.floor(spec.height) : 30;
  const header = {
    "udos-grid": "v1",
    size: `${width}x${height}`,
    title: spec.title ?? "",
    mode: spec.mode ?? "",
    theme: spec.theme ?? "mono",
    ts: spec.ts ?? ""
  };

  const meta = Object.entries(header)
    .filter(([, v]) => v)
    .map(([k, v]) => `${k}: ${v}`);

  const rawText = [
    "--- udos-grid:v1",
    ...meta,
    "---",
    "",
    ...lines,
    "--- end ---",
    ""
  ].join("\n");

  return { header, lines, rawText };
}
