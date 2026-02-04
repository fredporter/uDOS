import { GridCanvasSpec, RenderResult } from "./types.js";

export function packageGrid(spec: GridCanvasSpec, lines: string[]): RenderResult {
  const header = {
    "udos-grid": "v1",
    size: "80x30",
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
