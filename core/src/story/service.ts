/**
 * Story Service
 *
 * Manages loading, parsing, and persisting story state.
 */

import { parseStoryFile, type StoryState } from "./parser";

/**
 * Load story from file or URL
 */
export async function loadStory(source: string | File): Promise<StoryState> {
  let content: string;

  if (typeof source === "string") {
    // Load from URL
    const response = await fetch(source);
    if (!response.ok) {
      throw new Error(`Failed to load story: ${response.statusText}`);
    }
    content = await response.text();
  } else {
    // Load from File object
    content = await source.text();
  }

  return parseStoryFile(content);
}

/**
 * Save story state to localStorage (browser only)
 */
export function saveStoryState(storyId: string, state: StoryState): void {
  if (typeof localStorage === "undefined") {
    throw new Error("localStorage not available (browser-only feature)");
  }
  const key = `story:${storyId}`;
  localStorage.setItem(key, JSON.stringify(state));
}

/**
 * Load story state from localStorage (browser only)
 */
export function loadStoryState(storyId: string): StoryState | null {
  if (typeof localStorage === "undefined") {
    return null;
  }
  const key = `story:${storyId}`;
  const stored = localStorage.getItem(key);
  return stored ? JSON.parse(stored) : null;
}

/**
 * Clear story state from localStorage (browser only)
 */
export function clearStoryState(storyId: string): void {
  if (typeof localStorage === "undefined") {
    throw new Error("localStorage not available (browser-only feature)");
  }
  const key = `story:${storyId}`;
  localStorage.removeItem(key);
}

/**
 * Export story answers as JSON
 */
export function exportStoryAnswers(
  story: StoryState,
  format: "json" | "csv" = "json",
): string {
  if (format === "json") {
    return JSON.stringify(
      {
        story: story.frontmatter.title,
        version: story.frontmatter.version,
        timestamp: new Date().toISOString(),
        answers: story.answers,
      },
      null,
      2,
    );
  } else {
    // CSV format
    const headers = Object.keys(story.answers);
    const values = headers.map((h) => String(story.answers[h] || ""));
    return [headers.join(","), values.join(",")].join("\n");
  }
}

/**
 * Download story answers as file (browser only)
 */
export function downloadStoryAnswers(
  story: StoryState,
  format: "json" | "csv" = "json",
): void {
  if (typeof document === "undefined") {
    throw new Error(
      "downloadStoryAnswers not available (browser-only feature)",
    );
  }
  const content = exportStoryAnswers(story, format);
  const filename = `${story.frontmatter.title.toLowerCase().replace(/\s+/g, "-")}-answers.${format}`;
  const blob = new Blob([content], {
    type: format === "json" ? "application/json" : "text/csv",
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
