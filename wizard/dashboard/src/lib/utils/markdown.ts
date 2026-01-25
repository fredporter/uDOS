import { marked } from 'marked';
import hljs from 'highlight.js';

// Configure marked with highlight.js
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {
        console.error('Highlight.js error:', err);
      }
    }
    // Auto-detect language if not specified
    try {
      return hljs.highlightAuto(code).value;
    } catch (err) {
      console.error('Highlight.js auto-detect error:', err);
    }
    return code;
  },
  breaks: true,
  gfm: true, // GitHub Flavored Markdown
  headerIds: true,
  mangle: false,
  pedantic: false,
});

/**
 * Parse markdown to HTML with syntax highlighting
 */
export function parseMarkdown(markdown: string): string {
  if (!markdown) return '';
  try {
    return marked.parse(markdown) as string;
  } catch (err) {
    console.error('Markdown parsing error:', err);
    return markdown;
  }
}

/**
 * Parse inline markdown (no block elements)
 */
export function parseInlineMarkdown(markdown: string): string {
  if (!markdown) return '';
  try {
    return marked.parseInline(markdown) as string;
  } catch (err) {
    console.error('Inline markdown parsing error:', err);
    return markdown;
  }
}

/**
 * Extract frontmatter from markdown
 */
export function extractFrontmatter(content: string): {
  frontmatter: Record<string, any>;
  body: string;
} {
  const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/;
  const match = content.match(frontmatterRegex);

  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const [, frontmatterStr, body] = match;
  const frontmatter: Record<string, any> = {};

  // Parse simple YAML-like frontmatter
  frontmatterStr.split('\n').forEach((line) => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      const value = line.substring(colonIndex + 1).trim();
      frontmatter[key] = value;
    }
  });

  return { frontmatter, body };
}

/**
 * Supported languages for syntax highlighting
 */
export const SUPPORTED_LANGUAGES = [
  'javascript',
  'typescript',
  'python',
  'rust',
  'go',
  'java',
  'c',
  'cpp',
  'csharp',
  'html',
  'css',
  'scss',
  'json',
  'yaml',
  'toml',
  'markdown',
  'bash',
  'shell',
  'sql',
  'graphql',
  'dockerfile',
  'nginx',
  'xml',
  'svelte',
  'vue',
  'react',
];

/**
 * Get language name for display
 */
export function getLanguageName(lang: string): string {
  const languageNames: Record<string, string> = {
    javascript: 'JavaScript',
    typescript: 'TypeScript',
    python: 'Python',
    rust: 'Rust',
    go: 'Go',
    java: 'Java',
    c: 'C',
    cpp: 'C++',
    csharp: 'C#',
    html: 'HTML',
    css: 'CSS',
    scss: 'SCSS',
    json: 'JSON',
    yaml: 'YAML',
    toml: 'TOML',
    markdown: 'Markdown',
    bash: 'Bash',
    shell: 'Shell',
    sql: 'SQL',
    graphql: 'GraphQL',
    dockerfile: 'Dockerfile',
    nginx: 'Nginx',
    xml: 'XML',
    svelte: 'Svelte',
    vue: 'Vue',
    react: 'React',
  };

  return languageNames[lang.toLowerCase()] || lang;
}
