import { strictEqual, deepStrictEqual } from "node:assert";
import { mkdtemp, rm } from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import Database from "better-sqlite3";

import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_VAULT = path.join(__dirname, "fixtures", "task-vault");
const INDEXER_PATH = new URL("../dist/tasks/indexer.js", import.meta.url);

async function main() {
  const { indexTasks } = await import(INDEXER_PATH);
  const tmpDir = await mkdtemp(path.join(os.tmpdir(), "udos-task-index-"));
  const dbPath = path.join(tmpDir, "state.db");

  try {
    const total = await indexTasks({ vaultRoot: FIXTURE_VAULT, dbPath });
    strictEqual(total, 3, "should index all tasks from fixture");

    const db = new Database(dbPath);
    db.pragma("foreign_keys = ON");

    const files = db.prepare("SELECT path FROM files ORDER BY path").all();
    strictEqual(files.length, 1, "should record file metadata");
    strictEqual(files[0].path, "notes/tasks.md");

    const tasks = db.prepare("SELECT * FROM tasks ORDER BY line").all();
    strictEqual(tasks.length, 3, "should write three tasks");
    deepStrictEqual(
      tasks.map((row) => row.status),
      ["open", "done", "open"],
      "task statuses should map correctly",
    );

    const due = tasks.find((row) => row.due)?.due;
    strictEqual(due, "2026-02-10", "due date should parse");

    const start = tasks.find((row) => row.start)?.start;
    strictEqual(start, "2026-02-07", "start date should parse");

    const priorities = tasks.map((row) => row.priority);
    deepStrictEqual(priorities, [0, 2, -2], "priority scoring should map");

    const tagRow = tasks.find((row) => row.tags);
    strictEqual(tagRow.tags, JSON.stringify(["alpha"]), "tags should serialize");

    try {
      db.prepare(
        "INSERT INTO tasks (id, file_path, line, text, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
      ).run("bad:1", "missing.md", 1, "bad", "open", Date.now(), Date.now());
      throw new Error("Expected foreign key constraint to fail");
    } catch (error) {
      if (!String(error).includes("FOREIGN KEY")) {
        throw error;
      }
    }
    db.close();
  } finally {
    await rm(tmpDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error("Task indexer regression test failed:", error);
  process.exit(1);
});
