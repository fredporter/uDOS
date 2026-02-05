import { promises as fs } from "node:fs";
import * as crypto from "node:crypto";
import path from "node:path";
import matter from "gray-matter";
import Database from "better-sqlite3";

type LogLevel = "INFO" | "WARN" | "ERROR" | "DEBUG";
type Logger = (level: LogLevel, msg: string) => void;

const defaultLogger: Logger = (level, msg) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${level}] ${msg}`);
};

export interface TaskRow {
  id: string;
  file_path: string;
  line: number;
  text: string;
  status: "open" | "done";
  due?: string;
  start?: string;
  priority?: number;
  tags?: string;
  created_at: number;
  updated_at: number;
}

export interface TaskCatalog {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  by_tag: Record<string, number>;
  upcoming_due: TaskRow[];
  high_priority: TaskRow[];
  indexed_at: string;
}

export interface ExecutionStats {
  total_indexed: number;
  files_processed: number;
  indexing_duration_ms: number;
  errors: Array<{ file: string; error: string }>;
}

export interface IndexOptions {
  vaultRoot: string;
  dbPath: string;
  logger?: Logger;
}

const CHECKBOX_REGEX = /^(\s*)-\s+\[([ xX])\]\s+(.+)$/;
const DUE_REGEX = /📅\s*(\d{4}-\d{2}-\d{2})/;
const START_REGEX = /🛫\s*(\d{4}-\d{2}-\d{2})/;
const PRIORITY_HIGH = /⏫/;
const PRIORITY_LOW = /⏬/;
const TAG_REGEX = /#(\w+)/g;

export async function indexTasks(options: IndexOptions): Promise<number> {
  const stats = await indexTasksWithStats(options);
  return stats.total_indexed;
}

export async function indexTasksWithStats(
  options: IndexOptions,
): Promise<ExecutionStats> {
  const { vaultRoot, dbPath } = options;
  const log = options.logger || defaultLogger;
  const startTime = Date.now();

  try {
    log("INFO", `[INDEXER] Starting task indexing: vault='${vaultRoot}'`);

    await fs.mkdir(path.dirname(dbPath), { recursive: true });

    const db = new Database(dbPath);
    db.pragma("foreign_keys = ON");

    ensureSchema(db);

    const mdFiles = await collectMarkdownFiles(vaultRoot, log);
    log("INFO", `[INDEXER] Found ${mdFiles.length} markdown files`);
    let totalTasks = 0;
    const errors: Array<{ file: string; error: string }> = [];

    for (const filePath of mdFiles) {
      const rel = path.relative(vaultRoot, filePath);

      try {
        await updateFileRecord(db, rel, filePath);

        const tasks = await parseTasksFromFile(filePath, rel);

        db.prepare("DELETE FROM tasks WHERE file_path = ?").run(rel);

        for (const task of tasks) {
          upsertTask(db, task);
          totalTasks++;
        }
      } catch (err) {
        errors.push({ file: rel, error: String(err) });
        log("WARN", `[INDEXER] Failed to index ${rel}: ${String(err)}`);
      }
    }

    db.close();
    const duration = Date.now() - startTime;
    log(
      "INFO",
      `[INDEXER] Completed: ${totalTasks} tasks in ${duration}ms (${errors.length} errors)`,
    );

    return {
      total_indexed: totalTasks,
      files_processed: mdFiles.length,
      indexing_duration_ms: duration,
      errors,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    log("ERROR", `[INDEXER] Failed after ${duration}ms: ${String(error)}`);
    throw error;
  }
}

function ensureSchema(db: Database.Database): void {
  const sql = `
    CREATE TABLE IF NOT EXISTS files (
      path TEXT PRIMARY KEY,
      mtime INTEGER NOT NULL,
      hash TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tasks (
      id TEXT PRIMARY KEY,
      file_path TEXT NOT NULL,
      line INTEGER NOT NULL,
      text TEXT NOT NULL,
      status TEXT NOT NULL,
      due TEXT,
      start TEXT,
      priority INTEGER,
      tags TEXT,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL,
      FOREIGN KEY(file_path) REFERENCES files(path)
    );

    CREATE INDEX IF NOT EXISTS idx_tasks_status_due ON tasks(status, due);
    CREATE INDEX IF NOT EXISTS idx_tasks_file ON tasks(file_path);
  `;
  db.exec(sql);
}

async function collectMarkdownFiles(
  root: string,
  log?: Logger,
): Promise<string[]> {
  const SKIP = new Set([
    "_site",
    "_templates",
    ".udos",
    "05_DATA",
    "06_RUNS",
    "07_LOGS",
    "node_modules",
  ]);
  const results: string[] = [];

  async function walk(dir: string) {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory()) {
          if (!SKIP.has(entry.name) && !entry.name.startsWith(".")) {
            await walk(path.join(dir, entry.name));
          }
        } else if (entry.isFile() && entry.name.endsWith(".md")) {
          results.push(path.join(dir, entry.name));
        }
      }
    } catch (err) {
      if (log) {
        log("WARN", `[INDEXER] Failed to walk ${dir}: ${String(err)}`);
      }
    }
  }

  await walk(root);
  return results;
}

async function parseTasksFromFile(
  filePath: string,
  relPath: string,
): Promise<TaskRow[]> {
  const content = await fs.readFile(filePath, "utf-8");
  const { content: body } = matter(content);

  const lines = body.split("\n");
  const tasks: TaskRow[] = [];
  const now = Date.now();

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const match = CHECKBOX_REGEX.exec(line);

    if (!match) continue;

    const status = match[2].toLowerCase() === "x" ? "done" : "open";
    const text = match[3];

    const due = DUE_REGEX.exec(text)?.[1];
    const start = START_REGEX.exec(text)?.[1];

    let priority = 0;
    if (PRIORITY_HIGH.test(text)) priority = 2;
    else if (PRIORITY_LOW.test(text)) priority = -2;

    const tags: string[] = [];
    let tagMatch;
    const tagRegexCopy = new RegExp(TAG_REGEX);
    while ((tagMatch = tagRegexCopy.exec(text)) !== null) {
      tags.push(tagMatch[1]);
    }

    const taskId = `${relPath}:${i + 1}`;

    tasks.push({
      id: taskId,
      file_path: relPath,
      line: i + 1,
      text: text.replace(/📅.*|🛫.*|⏫|⏬/g, "").trim(),
      status,
      due,
      start,
      priority,
      tags: tags.length ? JSON.stringify(tags) : undefined,
      created_at: now,
      updated_at: now,
    });
  }

  return tasks;
}

function upsertTask(db: Database.Database, task: TaskRow): void {
  const insertSql = `
    INSERT INTO tasks (id, file_path, line, text, status, due, start, priority, tags, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      text = excluded.text,
      status = excluded.status,
      due = excluded.due,
      start = excluded.start,
      priority = excluded.priority,
      tags = excluded.tags,
      updated_at = excluded.updated_at
  `;

  const stmt = db.prepare(insertSql);

  stmt.run(
    task.id,
    task.file_path,
    task.line,
    task.text,
    task.status,
    task.due ?? null,
    task.start ?? null,
    task.priority ?? null,
    task.tags ?? null,
    task.created_at,
    task.updated_at,
  );
}

async function updateFileRecord(
  db: Database.Database,
  relPath: string,
  absPath: string,
): Promise<void> {
  const stats = await fs.stat(absPath);
  const content = await fs.readFile(absPath);
  const hash = crypto.createHash("sha256").update(content).digest("hex");

  const insertSql = `
    INSERT INTO files (path, mtime, hash)
    VALUES (?, ?, ?)
    ON CONFLICT(path) DO UPDATE SET
      mtime = excluded.mtime,
      hash = excluded.hash
  `;

  const stmt = db.prepare(insertSql);
  stmt.run(relPath, Math.floor(stats.mtime / 1000), hash);
}

export function queryTaskCatalog(dbPath: string): TaskCatalog {
  const db = new Database(dbPath, { readonly: true });
  db.pragma("foreign_keys = ON");

  const totalResult = db
    .prepare("SELECT COUNT(*) as count FROM tasks")
    .get() as {
    count: number;
  };

  const byStatusResult = db
    .prepare("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    .all() as Array<{ status: string; count: number }>;

  const byPriorityResult = db
    .prepare(
      "SELECT priority, COUNT(*) as count FROM tasks WHERE priority IS NOT NULL GROUP BY priority",
    )
    .all() as Array<{ priority: number; count: number }>;

  const tagRows = db
    .prepare("SELECT tags FROM tasks WHERE tags IS NOT NULL")
    .all() as Array<{ tags: string }>;

  const upcomingResult = db
    .prepare(
      "SELECT * FROM tasks WHERE status = 'open' AND due IS NOT NULL ORDER BY due ASC LIMIT 10",
    )
    .all() as TaskRow[];

  const highPriorityResult = db
    .prepare(
      "SELECT * FROM tasks WHERE status = 'open' AND priority >= 2 ORDER BY priority DESC LIMIT 10",
    )
    .all() as TaskRow[];

  const by_status: Record<string, number> = {};
  for (const row of byStatusResult) {
    by_status[row.status] = row.count;
  }

  const by_priority: Record<string, number> = {};
  for (const row of byPriorityResult) {
    by_priority[String(row.priority)] = row.count;
  }

  const by_tag: Record<string, number> = {};
  for (const row of tagRows) {
    try {
      const tags = JSON.parse(row.tags) as string[];
      for (const tag of tags) {
        by_tag[tag] = (by_tag[tag] || 0) + 1;
      }
    } catch {
      // skip malformed tag data
    }
  }

  db.close();

  return {
    total: totalResult.count,
    by_status,
    by_priority,
    by_tag,
    upcoming_due: upcomingResult,
    high_priority: highPriorityResult,
    indexed_at: new Date().toISOString(),
  };
}

export function searchTasks(
  dbPath: string,
  filters?: { status?: string; due?: string; tag?: string; priority?: number },
): TaskRow[] {
  const db = new Database(dbPath, { readonly: true });
  db.pragma("foreign_keys = ON");

  let sql = "SELECT * FROM tasks WHERE 1 = 1";
  const params: Array<string | number> = [];

  if (filters?.status) {
    sql += " AND status = ?";
    params.push(filters.status);
  }

  if (filters?.due) {
    sql += " AND due = ?";
    params.push(filters.due);
  }

  if (filters?.priority !== undefined) {
    sql += " AND priority = ?";
    params.push(filters.priority);
  }

  if (filters?.tag) {
    sql += " AND tags LIKE ?";
    params.push(`%${filters.tag}%`);
  }

  sql += " ORDER BY due ASC, priority DESC";

  const stmt = db.prepare(sql);
  const results = stmt.all(...params) as TaskRow[];
  db.close();

  return results;
}
