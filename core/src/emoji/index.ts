import { readFileSync } from "node:fs";
import path from "node:path";
import type { EmojiReference, EmojiShortcode } from "./types";

let cachedReference: EmojiReference | null = null;
let cachedSet: ReadonlySet<EmojiShortcode> | null = null;

function findRepoRoot(startDir: string): string | null {
  let current = path.resolve(startDir);
  for (let i = 0; i < 6; i++) {
    const candidate = path.join(
      current,
      "vendor",
      "emoji",
      "github-emoji-shortcodes.json",
    );
    try {
      readFileSync(candidate, "utf-8");
      return current;
    } catch {
      // keep searching upward
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
}

function loadEmojiReference(): EmojiReference {
  if (cachedReference) {
    return cachedReference;
  }
  const repoRoot = findRepoRoot(process.cwd()) ?? process.cwd();
  const jsonPath = path.join(
    repoRoot,
    "vendor",
    "emoji",
    "github-emoji-shortcodes.json",
  );
  const raw = readFileSync(jsonPath, "utf-8");
  const parsed = JSON.parse(raw) as EmojiReference;
  cachedReference = parsed;
  cachedSet = new Set(parsed.shortcodes);
  return parsed;
}

function getEmojiSet(): ReadonlySet<EmojiShortcode> {
  if (!cachedSet) {
    loadEmojiReference();
  }
  return cachedSet ?? new Set();
}

export function isEmojiShortcode(token: string): token is EmojiShortcode {
  return getEmojiSet().has(token as EmojiShortcode);
}

export function getAllEmojiShortcodes(): EmojiShortcode[] {
  return loadEmojiReference().shortcodes;
}

export function getEmojiMeta() {
  return loadEmojiReference().source;
}
