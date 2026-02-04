import { promises as fs } from "node:fs";
import * as crypto from "node:crypto";
import path from "node:path";
import matter from "gray-matter";
import Database from "better-sqlite3";

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

export interface IndexOptions {
  vaultRoot: string;
  dbPath: string;
}

const CHECKBOX_REGEX = /^(\s*)-\s+\[([ xX])\]\s+(.+)$/;
const DUE_REGEX = /📅\s*(\d{4}-\d{2}-\d{2})/;
const START_REGEX = /🛫\s*(\d{4}-\d{2}-\d{2})/;
const PRIORITY_HIGH = /⏫/;
const PRIORITY_LOW = /⏬/;
const TAG_REGEX = /#(\w+)/g;

export async function indexTasks(options: IndexOptions): Promise<number> {
  const { vaultRoot, dbPath } = options;

  // Ensure parent directory exists
  await fs.mkdir(path.dirname(dbPath), { recursive: true });

  const db = new Database(dbPath);
  db.pragma("foreign_keys = ON");

  ensureSchema(db);

  const mdFiles = await collectMarkdownFiles(vaultRoot);
  let totalTasks = 0;

  for (const filePath of mdFiles) {
    const rel = path.relative(vaultRoot, filePath);

    // Update file record first (foreign key requirement)
    await updateFileRecord(db, rel, filePath);

    const tasks = await parseTasksFromFile(filePath, rel);

    // Clear stale tasks for this file before inserting fresh entries
    db.prepare("DELETE FROM tasks WHERE file_path = ?").run(rel);

    for (const task of tasks) {
      upsertTask(db, task);
      totalTasks++;
    }
  }

  db.close();
  return totalTasks;
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

async function collectMarkdownFiles(root: string): Promise<string[]> {
  const SKIP = new Set(["_site", "_templates", ".udos", "05_DATA", "06_RUNS", "07_LOGS", "node_modules"]);
  const results: string[] = [];

  async function walk(dir: string) {
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
  }

  await walk(root);
  return results;
}

async function parseTasksFromFile(filePath: string, relPath: string): Promise<TaskRow[]> {
  const content = await fs.readFile(filePath, "utf-8");
  const { data, content: body } = matter(content);

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
    task.updated_at
  );
}

async function updateFileRecord(db: Database.Database, relPath: string, absPath: string): Promise<void> {
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
  stmt.run(relPath, Math.floor(stats.mtimeMs), hash);
}
