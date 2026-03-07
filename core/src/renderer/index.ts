import { promises as fs } from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";
import { replaceEmojiShortcodes } from "../emoji/replace.js";
import { createDefaultLogger, Logger } from "../runtime/utils/logging.js";
import { nowIso } from "../runtime/utils/time.js";

export interface RenderOptions {
  vaultRoot: string;
  themeName: string;
  themesRoot: string;
  outputRoot: string;
  logger?: Logger;
}

export interface RenderedFile {
  path: string;
  size: number;
  updatedAt: string;
}

export interface RenderSummary {
  theme: string;
  files: RenderedFile[];
  nav: { title: string; href: string }[];
}

type ThemeMeta = {
  contentClass?: string;
};

export class RenderError extends Error {
  constructor(
    message: string,
    public code: string = "RENDER_ERROR",
    public details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "RenderError";
  }
}

type PageInfo = {
  absolute: string;
  rel: string;
  slug: string;
  aliases: string[];
  title: string;
  frontmatter: Record<string, unknown>;
  content: string;
};

const SKIP_DIRS = new Set([
  "_site",
  "_templates",
  ".udos",
  "05_DATA",
  "06_RUNS",
  "07_LOGS",
  "node_modules",
]);

export async function renderVault(
  options: RenderOptions,
): Promise<RenderSummary> {
  const { vaultRoot, themeName, themesRoot, outputRoot } = options;
  const log = options.logger || createDefaultLogger();
  const themeDir = path.join(themesRoot, themeName);
  const shellPath = path.join(themeDir, "shell.html");
  const themeMetaPath = path.join(themeDir, "theme.json");

  try {
    log(
      "INFO",
      `[RENDER] Starting render: theme='${themeName}', vault='${vaultRoot}'`,
    );

    // Validate theme directory exists
    try {
      await fs.stat(themeDir);
    } catch (err) {
      throw new RenderError(
        `Theme directory not found: ${themeDir}`,
        "THEME_NOT_FOUND",
        {
          theme: themeName,
          dir: themeDir,
        },
      );
    }

    // Load shell template
    let shellTemplate: string;
    try {
      shellTemplate = await fs.readFile(shellPath, "utf-8");
    } catch (err) {
      throw new RenderError(
        `Shell template not found: ${shellPath}`,
        "SHELL_NOT_FOUND",
        {
          path: shellPath,
        },
      );
    }

    // Load theme metadata
    let themeMeta: ThemeMeta;
    try {
      const metaText = await fs.readFile(themeMetaPath, "utf-8");
      themeMeta = JSON.parse(metaText) as ThemeMeta;
    } catch (err) {
      throw new RenderError(
        `Theme metadata invalid or not found: ${themeMetaPath}`,
        "THEME_META_INVALID",
        { path: themeMetaPath, error: String(err) },
      );
    }

    log("INFO", `[RENDER] Theme loaded: ${themeName}`);

    const markdownFiles = await collectMarkdownFiles(vaultRoot, log);
    log("INFO", `[RENDER] Found ${markdownFiles.length} markdown files`);

    const pageInfos = (
      await Promise.all(
        markdownFiles.map((file) => readPageInfo(file, vaultRoot, log)),
      )
    ).sort((a, b) => a.slug.localeCompare(b.slug));

    log("INFO", `[RENDER] Parsed ${pageInfos.length} pages`);

    const navEntries = pageInfos.map((info) => ({
      title: info.title,
      href: `./${info.slug}/`,
    }));

    const navHtml = buildNav(navEntries);
    const siteThemeDir = path.join(outputRoot, themeName);
    await fs.mkdir(siteThemeDir, { recursive: true });
    await copyThemeAssets(themeDir, siteThemeDir, log);
    log("INFO", `[RENDER] Theme assets copied to: ${siteThemeDir}`);

    const renderedFiles: RenderedFile[] = [];

    for (const info of pageInfos) {
      const html = marked.parse(info.content);
      const htmlWithEmoji = replaceEmojiShortcodes(
        html,
        (shortcode) =>
          `<span class="emoji" data-emoji="${shortcode}">${shortcode}</span>`,
      );
      const page = fillTemplate(shellTemplate, {
        title: info.title,
        content: wrapContent(htmlWithEmoji, info.title, themeMeta.contentClass),
        nav: navHtml,
        contentClass: themeMeta.contentClass ?? "",
        meta: renderMeta(info.frontmatter),
        footer: `<p class="prose-footer">Rendered ${nowIso()}</p>`,
      });

      const outDir = path.join(siteThemeDir, info.slug);
      await fs.mkdir(outDir, { recursive: true });
      const outPath = path.join(outDir, "index.html");
      await fs.writeFile(outPath, page, "utf-8");

      const stat = await fs.stat(outPath);
      renderedFiles.push({
        path: path.posix.join(info.slug, "index.html"),
        size: stat.size,
        updatedAt: stat.mtime.toISOString(),
      });

      for (const alias of info.aliases) {
        if (!alias || alias === info.slug) {
          continue;
        }
        const aliasOutDir = path.join(siteThemeDir, alias);
        await fs.mkdir(aliasOutDir, { recursive: true });
        const aliasOutPath = path.join(aliasOutDir, "index.html");
        const aliasHref = relativeHref(alias, info.slug);
        await fs.writeFile(aliasOutPath, renderAliasRedirect(aliasHref, info.title), "utf-8");
        const aliasStat = await fs.stat(aliasOutPath);
        renderedFiles.push({
          path: path.posix.join(alias, "index.html"),
          size: aliasStat.size,
          updatedAt: aliasStat.mtime.toISOString(),
        });
      }
    }

    log("INFO", `[RENDER] Successfully rendered ${renderedFiles.length} files`);

    return {
      theme: themeName,
      files: renderedFiles,
      nav: navEntries,
    };
  } catch (error) {
    if (error instanceof RenderError) {
      log("ERROR", `[RENDER] ${error.code}: ${error.message}`);
      throw error;
    }
    log("ERROR", `[RENDER] Unexpected error: ${String(error)}`);
    throw new RenderError(`Render failed: ${String(error)}`, "RENDER_FAILED", {
      theme: themeName,
    });
  }
}

async function collectMarkdownFiles(
  root: string,
  log?: Logger,
): Promise<string[]> {
  const result: string[] = [];
  try {
    const entries = await fs.readdir(root, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (shouldSkipDir(entry.name)) {
          continue;
        }
        result.push(
          ...(await collectMarkdownFiles(path.join(root, entry.name), log)),
        );
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        result.push(path.join(root, entry.name));
      }
    }
  } catch (err) {
    if (log) {
      log("WARN", `[RENDER] Failed to read directory ${root}: ${String(err)}`);
    }
  }
  return result;
}

function shouldSkipDir(name: string): boolean {
  if (SKIP_DIRS.has(name)) {
    return true;
  }
  if (name.startsWith(".")) {
    return true;
  }
  return false;
}

async function readPageInfo(
  filePath: string,
  vaultRoot: string,
  log?: Logger,
): Promise<PageInfo> {
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    const { data, content } = matter(raw);
    const rel = path.relative(vaultRoot, filePath);
    const fallbackSlug = normalizeRel(rel);
    const frontmatter = (data ?? {}) as Record<string, unknown>;
    const frontmatterSlug = normalizeFrontmatterSlug(frontmatter.slug);
    const slug = frontmatterSlug || fallbackSlug;
    const aliases = collectAliasSlugs(frontmatter, fallbackSlug, slug);
    const title =
      typeof frontmatter.title === "string" && frontmatter.title.trim().length > 0
        ? frontmatter.title
        : path.basename(slug) || "Untitled";

    return {
      absolute: filePath,
      rel,
      slug,
      aliases,
      title,
      frontmatter,
      content,
    };
  } catch (err) {
    if (log) {
      log("WARN", `[RENDER] Failed to parse ${filePath}: ${String(err)}`);
    }
    throw err;
  }
}

function normalizeRel(rel: string): string {
  const trimmed = rel.replace(/\\/g, "/").replace(/\.md$/i, "");
  const segments = trimmed
    .split("/")
    .map((segment) => normalizeSlugSegment(segment))
    .filter((segment) => segment.length > 0);
  return segments.join("/");
}

function normalizeSlugSegment(segment: string): string {
  const keepAtPrefix = segment.startsWith("@");
  let base = keepAtPrefix ? segment.slice(1) : segment;
  base = base.trim().toLowerCase();
  base = base.replace(/--+/g, "-");
  base = base.replace(/[_\s]+/g, "-");
  base = base.replace(/[^a-z0-9-]/g, "-");
  base = base.replace(/-+/g, "-").replace(/^-+|-+$/g, "");
  if (!base) {
    return keepAtPrefix ? "@note" : "note";
  }
  return keepAtPrefix ? `@${base}` : base;
}

function normalizeFrontmatterSlug(value: unknown): string {
  if (typeof value !== "string") {
    return "";
  }
  const raw = value.trim().replace(/\\/g, "/");
  if (!raw) {
    return "";
  }
  return raw
    .split("/")
    .map((segment) => normalizeSlugSegment(segment))
    .filter((segment) => segment.length > 0)
    .join("/");
}

function collectAliasSlugs(
  frontmatter: Record<string, unknown>,
  fallbackSlug: string,
  canonicalSlug: string,
): string[] {
  const aliases: string[] = [];
  if (fallbackSlug && fallbackSlug !== canonicalSlug) {
    aliases.push(fallbackSlug);
  }

  const aliasCandidates: string[] = [];
  const maybeAliases = frontmatter.aliases;
  if (Array.isArray(maybeAliases)) {
    for (const alias of maybeAliases) {
      if (typeof alias === "string") {
        aliasCandidates.push(alias);
      }
    }
  } else if (typeof maybeAliases === "string") {
    aliasCandidates.push(maybeAliases);
  }

  const maybeSlugHistory = frontmatter.slug_history;
  if (Array.isArray(maybeSlugHistory)) {
    for (const alias of maybeSlugHistory) {
      if (typeof alias === "string") {
        aliasCandidates.push(alias);
      }
    }
  }

  for (const alias of aliasCandidates) {
    const normalized = normalizeFrontmatterSlug(alias);
    if (normalized) {
      aliases.push(normalized);
    }
  }

  return dedupeStrings(aliases).filter((slug) => slug !== canonicalSlug);
}

function dedupeStrings(values: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const value of values) {
    if (!value || seen.has(value)) {
      continue;
    }
    seen.add(value);
    out.push(value);
  }
  return out;
}

function relativeHref(fromSlug: string, toSlug: string): string {
  const fromDir = `/${fromSlug}/`;
  const toDir = `/${toSlug}/`;
  const rel = path.posix.relative(fromDir, toDir);
  return rel || "./";
}

function renderAliasRedirect(href: string, title: string): string {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0; url=${escapeHtml(href)}" />
    <title>${escapeHtml(title)}</title>
  </head>
  <body>
    <p>Moved: <a href="${escapeHtml(href)}">${escapeHtml(title)}</a></p>
  </body>
</html>`;
}

function wrapContent(
  html: string,
  title: string,
  contentClass?: string,
): string {
  return `
    <section class="shell-card">
      <div class="prose-header">
        <p>${escapeHtml(title)}</p>
      </div>
      <div class="prose-main ${contentClass ?? ""}">
        ${html}
      </div>
    </section>
  `;
}

function buildNav(entries: { title: string; href: string }[]): string {
  if (!entries.length) {
    return "";
  }
  const list = entries
    .sort((a, b) => a.title.localeCompare(b.title))
    .map(
      (entry) =>
        `<li><a href="${escapeHtml(entry.href)}">${escapeHtml(entry.title)}</a></li>`,
    )
    .join("");
  return `<nav class="prose-nav"><ul>${list}</ul></nav>`;
}

function renderMeta(frontmatter: Record<string, unknown>): string {
  const entries = Object.entries(frontmatter).filter(
    ([key]) => key !== "title",
  );
  if (!entries.length) {
    return "";
  }
  const rows = entries
    .map(([key, value]) => {
      const text = typeof value === "string" ? value : JSON.stringify(value);
      return `<div class="meta-row"><span>${escapeHtml(key)}</span>: ${escapeHtml(
        text,
      )}</div>`;
    })
    .join("");
  return `<div class="prose-meta">${rows}</div>`;
}

async function copyThemeAssets(
  themeDir: string,
  destDir: string,
  log?: Logger,
): Promise<void> {
  const themeCss = path.join(themeDir, "theme.css");
  try {
    await fs.copyFile(themeCss, path.join(destDir, "theme.css"));
  } catch (err) {
    if (log) {
      log(
        "DEBUG",
        `[RENDER] theme.css not found or copy failed (optional): ${String(err)}`,
      );
    }
  }
  await copyDirIfExists(
    path.join(themeDir, "assets"),
    path.join(destDir, "assets"),
  );
}

async function copyDirIfExists(src: string, dest: string): Promise<void> {
  try {
    await fs.access(src);
    await fs.cp(src, dest, { recursive: true });
  } catch {
    // skip if assets absent
  }
}

function fillTemplate(template: string, slots: Record<string, string>): string {
  return template.replace(/{{\s*(\w+)\s*}}/g, (_, name) => slots[name] ?? "");
}

const ESCAPE_MAP: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => ESCAPE_MAP[char] ?? char);
}
