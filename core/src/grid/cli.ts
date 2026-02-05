import { renderGrid, GridRendererInput, GridCanvasSpec } from "./index.js";
import * as fs from "fs";
import * as path from "path";

export interface CliOptions {
  mode: "calendar" | "table" | "schedule" | "map" | "dashboard";
  input?: string;
  loc?: string;
  layer?: string;
  output?: string;
  title?: string;
  theme?: string;
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
    }
  }

  return { ...opts, inputData };
}

export function executeRender(opts: CliOptions & { inputData: any }): string {
  const spec: GridCanvasSpec = {
    width: 80,
    height: 30,
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

export function main(args: string[]) {
  const opts = parseCli(args);
  const output = executeRender(opts);
  console.log(output);
}

// Export for CLI
if (typeof require !== "undefined" && require.main === module) {
  main(process.argv.slice(2));
}
