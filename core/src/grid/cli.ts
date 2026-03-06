import { renderGrid, GridRendererInput, GridCanvasSpec } from "./index.js";
import * as fs from "fs";
import * as path from "path";

export interface CliOptions {
  mode: "calendar" | "table" | "schedule" | "map" | "dashboard" | "workflow";
  input?: string;
  loc?: string;
  layer?: string;
  output?: string;
  title?: string;
  theme?: string;
  width?: number;
  height?: number;
  viewport?: string;
}

export function parseCli(args: string[]): CliOptions & { inputData: any } {
  const opts: CliOptions = { mode: "calendar" };
  const inputData: any = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === "--mode") {
      opts.mode = args[++i] as any;
    } else if (arg === "--input") {
      const inputPath = args[++i];
      try {
        const content = fs.readFileSync(inputPath, "utf-8");
        Object.assign(inputData, JSON.parse(content));
      } catch (e) {
        console.error(`Failed to read input file: ${inputPath}`);
      }
    } else if (arg === "--loc") {
      opts.loc = args[++i];
      inputData.focusLocId = opts.loc;
    } else if (arg === "--layer") {
      opts.layer = args[++i];
    } else if (arg === "--output") {
      opts.output = args[++i];
    } else if (arg === "--title") {
      opts.title = args[++i];
    } else if (arg === "--theme") {
      opts.theme = args[++i];
    } else if (arg === "--width") {
      const value = Number(args[++i]);
      if (Number.isFinite(value) && value > 0) {
        opts.width = Math.floor(value);
      }
    } else if (arg === "--height") {
      const value = Number(args[++i]);
      if (Number.isFinite(value) && value > 0) {
        opts.height = Math.floor(value);
      }
    } else if (arg === "--viewport") {
      opts.viewport = args[++i];
    }
  }

  return { ...opts, inputData };
}

export function executeRender(opts: CliOptions & { inputData: any }): string {
  const preset = parseViewportPreset(opts.viewport);
  const sizeFromEnv = parseViewportSize(process.env.UDOS_VIEWPORT_SIZE_CH);
  const width = opts.width ?? preset?.width ?? sizeFromEnv?.width ?? 80;
  const height = opts.height ?? preset?.height ?? sizeFromEnv?.height ?? 30;
  const spec: GridCanvasSpec = {
    width,
    height,
    title: opts.title || opts.mode.charAt(0).toUpperCase() + opts.mode.slice(1),
    theme: opts.theme || "mono",
    ts: new Date().toISOString(),
  };

  const input: GridRendererInput = {
    mode: opts.mode,
    spec,
    data: opts.inputData,
  };

  const result = renderGrid(input);

  // Write output if specified
  if (opts.output) {
    fs.writeFileSync(opts.output, result.rawText, "utf-8");
    console.error(`Output written to: ${opts.output}`);
  }

  return result.rawText;
}

function parseViewportSize(raw?: string): { width: number; height: number } | null {
  if (!raw) return null;
  const match = raw.match(/^\s*(\d+)\s*x\s*(\d+)\s*$/i);
  if (!match) return null;
  const width = Number(match[1]);
  const height = Number(match[2]);
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    return null;
  }
  return { width: Math.floor(width), height: Math.floor(height) };
}

function parseViewportPreset(raw?: string): { width: number; height: number } | null {
  if (!raw) return null;
  const value = raw.trim().toLowerCase();
  const presets: Record<string, { width: number; height: number }> = {
    // v1.5 display matrix (character dimensions)
    v0: { width: 25, height: 25 }, // watch minimum
    v1: { width: 40, height: 25 }, // compact handheld
    v2: { width: 64, height: 32 }, // tablet portrait
    v3: { width: 80, height: 40 }, // tablet landscape
    v4: { width: 100, height: 40 }, // laptop baseline
    v5: { width: 120, height: 50 }, // desktop baseline
    v6: { width: 80, height: 45 }, // widescreen 1280x720 class
    v7: { width: 120, height: 67 }, // widescreen 1920x1080 class
    watch: { width: 25, height: 25 },
    handheld: { width: 40, height: 25 },
    tablet: { width: 80, height: 40 },
    laptop: { width: 100, height: 40 },
    desktop: { width: 120, height: 50 },
    widescreen: { width: 120, height: 67 },
  };
  return presets[value] || null;
}

export function main(args: string[]) {
  const opts = parseCli(args);
  const output = executeRender(opts);
  console.log(output);
}

// Export for CLI
if (typeof require !== "undefined" && require.main === module) {
  main(process.argv.slice(2));
}
