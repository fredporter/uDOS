import { promises as fs } from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";

export interface RenderOptions {
  vaultRoot: string;
  themeName: string;
  themesRoot: string;
  outputRoot: string;
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

type PageInfo = {
  absolute: string;
  rel: string;
  slug: string;
  title: string;
  frontmatter: Record<string, unknown>;
  content: string;
};

const SKIP_DIRS = new Set(["_site", "_templates", ".udos", "05_DATA", "06_RUNS", "07_LOGS", "node_modules"]);

export async function renderVault(options: RenderOptions): Promise<RenderSummary> {
  const { vaultRoot, themeName, themesRoot, outputRoot } = options;
  const themeDir = path.join(themesRoot, themeName);
  const shellPath = path.join(themeDir, "shell.html");
  const themeMetaPath = path.join(themeDir, "theme.json");

  const shellTemplate = await fs.readFile(shellPath, "utf-8");
  const themeMeta = JSON.parse(await fs.readFile(themeMetaPath, "utf-8"));

  const markdownFiles = await collectMarkdownFiles(vaultRoot);
  const pageInfos = (
    await Promise.all(markdownFiles.map((file) => readPageInfo(file, vaultRoot)))
  ).sort((a, b) => a.slug.localeCompare(b.slug));
  const navEntries = pageInfos.map((info) => ({
    title: info.title,
    href: `./${info.slug}/`,
  }));

  const navHtml = buildNav(navEntries);
  const siteThemeDir = path.join(outputRoot, themeName);
  await fs.mkdir(siteThemeDir, { recursive: true });
  await copyThemeAssets(themeDir, siteThemeDir);

  const renderedFiles: RenderedFile[] = [];

  for (const info of pageInfos) {
    const html = marked.parse(info.content);
    const page = fillTemplate(shellTemplate, {
      title: info.title,
      content: wrapContent(html, info.title, themeMeta.contentClass),
      nav: navHtml,
      contentClass: themeMeta.contentClass ?? "",
      meta: renderMeta(info.frontmatter),
      footer: `<p class="prose-footer">Rendered ${new Date().toISOString()}</p>`,
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
  }

  return {
    theme: themeName,
    files: renderedFiles,
    nav: navEntries,
  };
}

async function collectMarkdownFiles(root: string): Promise<string[]> {
  const entries = await fs.readdir(root, { withFileTypes: true });
  const result: string[] = [];
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (shouldSkipDir(entry.name)) {
        continue;
      }
      result.push(...(await collectMarkdownFiles(path.join(root, entry.name))));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      result.push(path.join(root, entry.name));
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

async function readPageInfo(filePath: string, vaultRoot: string): Promise<PageInfo> {
  const raw = await fs.readFile(filePath, "utf-8");
  const { data, content } = matter(raw);
  const rel = path.relative(vaultRoot, filePath);
  const slug = normalizeRel(rel);
  const title =
    typeof data.title === "string" && data.title.trim().length > 0
      ? data.title
      : path.basename(slug) || "Untitled";

  return {
    absolute: filePath,
    rel,
    slug,
    title,
    frontmatter: data,
    content,
  };
}

function normalizeRel(rel: string): string {
  const trimmed = rel.replace(/\\/g, "/").replace(/\.md$/i, "");
  return trimmed;
}

function wrapContent(html: string, title: string, contentClass?: string): string {
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
        `<li><a href="${escapeHtml(entry.href)}">${escapeHtml(entry.title)}</a></li>`
    )
    .join("");
  return `<nav class="prose-nav"><ul>${list}</ul></nav>`;
}

function renderMeta(frontmatter: Record<string, unknown>): string {
  const entries = Object.entries(frontmatter).filter(([key]) => key !== "title");
  if (!entries.length) {
    return "";
  }
  const rows = entries
    .map(([key, value]) => {
      const text = typeof value === "string" ? value : JSON.stringify(value);
      return `<div class="meta-row"><span>${escapeHtml(key)}</span>: ${escapeHtml(
        text
      )}</div>`;
    })
    .join("");
  return `<div class="prose-meta">${rows}</div>`;
}

async function copyThemeAssets(themeDir: string, destDir: string): Promise<void> {
  const themeCss = path.join(themeDir, "theme.css");
  try {
    await fs.copyFile(themeCss, path.join(destDir, "theme.css"));
  } catch {
    /* ignore missing css */
  }
  await copyDirIfExists(path.join(themeDir, "assets"), path.join(destDir, "assets"));
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
