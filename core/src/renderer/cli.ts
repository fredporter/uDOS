import { promises as fs } from "node:fs";
import path from "node:path";
import { renderVault, RenderOptions, RenderSummary } from "./index.js";

type CliOptions = {
  theme: string;
  vaultRoot: string;
  themesRoot: string;
  outputRoot: string;
  missionId?: string;
  runsRoot?: string;
};

type RenderCliOptions = RenderOptions & {
  missionId?: string;
  runsRoot?: string;
};

function resolveDefaults(): CliOptions {
  const cwd = process.cwd();
  const vaultRoot =
    process.env.VAULT_ROOT ?? path.resolve(cwd, "..", "memory", "vault");
  const themesRoot =
    process.env.THEMES_ROOT ?? path.resolve(cwd, "..", "themes");
  const outputRoot =
    process.env.OUTPUT_ROOT ??
    path.resolve(cwd, "..", "memory", "vault", "_site");
  return {
    theme: process.env.THEME ?? "prose",
    vaultRoot,
    themesRoot,
    outputRoot,
    missionId: process.env.MISSION_ID,
    runsRoot: process.env.RUNS_ROOT ?? path.join(vaultRoot, "06_RUNS"),
  };
}

function parseArgs(args: string[]): Partial<CliOptions> {
  const parsed: Partial<CliOptions> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--theme" && args[i + 1]) {
      parsed.theme = args[++i];
    } else if (arg === "--vault" && args[i + 1]) {
      parsed.vaultRoot = args[++i];
    } else if (arg === "--themes" && args[i + 1]) {
      parsed.themesRoot = args[++i];
    } else if (arg === "--output" && args[i + 1]) {
      parsed.outputRoot = args[++i];
    } else if (arg === "--mission" && args[i + 1]) {
      parsed.missionId = args[++i];
    } else if (arg === "--runs" && args[i + 1]) {
      parsed.runsRoot = args[++i];
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`Render vault notes to a theme pack.

Usage:
  node renderer/cli.js [--theme THEME] [--vault PATH] [--themes PATH] [--output PATH] [--mission ID] [--runs PATH]

Environment overrides:
  VAULT_ROOT      Repo vault folder (default ../memory/vault)
  THEMES_ROOT     Themes folder (default ../themes)
  OUTPUT_ROOT     _site output folder (default ../memory/vault/_site)
  THEME           Theme id (default prose)
  MISSION_ID      Mission id used for run reports (default renderer-<theme>)
  RUNS_ROOT       Run report root (default <vault>/06_RUNS)
`);
}

function buildOptions(): RenderCliOptions {
  const defaults = resolveDefaults();
  const overrides = parseArgs(process.argv.slice(2));
  const vaultRoot = overrides.vaultRoot ?? defaults.vaultRoot;
  return {
    themeName: overrides.theme ?? defaults.theme,
    vaultRoot,
    themesRoot: overrides.themesRoot ?? defaults.themesRoot,
    outputRoot: overrides.outputRoot ?? defaults.outputRoot,
    missionId: overrides.missionId ?? defaults.missionId,
    runsRoot: overrides.runsRoot ?? path.join(vaultRoot, "06_RUNS"),
  };
}

function formatReportPath(vaultRoot: string, reportPath: string): string {
  const rel = path.relative(vaultRoot, reportPath).replace(/\\/g, "/");
  if (rel.startsWith("..")) {
    return reportPath;
  }
  return rel;
}

async function writeRunReport(
  options: RenderCliOptions,
  jobId: string,
  status: "completed" | "failed",
  startedAt: string,
  completedAt: string,
  result?: RenderSummary,
  error?: unknown,
): Promise<{ reportPath: string; missionId: string }> {
  const missionId = options.missionId ?? `renderer-${options.themeName}`;
  const runsRoot = options.runsRoot ?? path.join(options.vaultRoot, "06_RUNS");
  const runDir = path.join(runsRoot, missionId);
  await fs.mkdir(runDir, { recursive: true });
  const reportPath = path.join(runDir, `${jobId}.json`);
  const report: Record<string, unknown> = {
    mission_id: missionId,
    job_id: jobId,
    runner: "renderer-cli",
    status,
    theme: options.themeName,
    started_at: startedAt,
    completed_at: completedAt,
    output_root: options.outputRoot,
    artifacts: {
      site_root: path.join(options.outputRoot, options.themeName),
    },
  };
  if (result) {
    report.rendered_files = result.files;
    report.nav = result.nav;
  }
  if (error) {
    report.error = String(error);
  }
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2), "utf-8");
  return { reportPath, missionId };
}

async function main() {
  const options = buildOptions();
  const startedAt = new Date().toISOString();
  const jobId = `job-${Date.now()}`;
  try {
    const result = await renderVault(options);
    const completedAt = new Date().toISOString();
    const { reportPath, missionId } = await writeRunReport(
      options,
      jobId,
      "completed",
      startedAt,
      completedAt,
      result,
    );
    const payload = {
      ...result,
      job_id: jobId,
      mission_id: missionId,
      theme: options.themeName,
      status: "completed",
      report_path: formatReportPath(options.vaultRoot, reportPath),
    };
    console.log(JSON.stringify(payload));
  } catch (error) {
    const completedAt = new Date().toISOString();
    try {
      const { reportPath } = await writeRunReport(
        options,
        jobId,
        "failed",
        startedAt,
        completedAt,
        undefined,
        error,
      );
      console.error("Renderer failed:", error);
      console.error(
        `Report written to ${formatReportPath(options.vaultRoot, reportPath)}`,
      );
    } catch (reportError) {
      console.error("Renderer failed:", error);
      console.error("Failed to write mission report:", reportError);
    }
    process.exit(1);
  }
}

main();
