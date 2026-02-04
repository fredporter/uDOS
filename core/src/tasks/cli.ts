#!/usr/bin/env node
import path from "node:path";
import { indexTasks } from "./indexer.js";

function resolveDefaults() {
  const cwd = process.cwd();
  return {
    vaultRoot: process.env.VAULT_ROOT ?? path.resolve(cwd, "..", "..", "vault"),
    dbPath: process.env.DB_PATH ?? path.resolve(cwd, "..", "..", "vault", ".udos", "state.db"),
  };
}

function parseArgs(args: string[]) {
  const parsed: any = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--vault" && args[i + 1]) {
      parsed.vaultRoot = args[++i];
    } else if (arg === "--db" && args[i + 1]) {
      parsed.dbPath = args[++i];
    } else if (arg === "--help" || arg === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return parsed;
}

function printHelp() {
  console.log(`Index tasks from vault Markdown files into SQLite.

Usage:
  node tasks/cli.js [--vault PATH] [--db PATH]

Environment:
  VAULT_ROOT      Vault folder (default ../../vault)
  DB_PATH         SQLite database (default ../../vault/.udos/state.db)
`);
}

async function main() {
  const defaults = resolveDefaults();
  const parsed = parseArgs(process.argv.slice(2));
  const options = { ...defaults, ...parsed };

  console.log(`Indexing tasks from: ${options.vaultRoot}`);
  console.log(`Writing to: ${options.dbPath}`);

  try {
    const taskCount = await indexTasks(options);
    console.log(`✅ Indexed ${taskCount} tasks`);
  } catch (error) {
    console.error("Task indexing failed:", error);
    process.exit(1);
  }
}

main();
