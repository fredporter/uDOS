/**
 * Markdown renderer utilities for story components.
 * 
 * Keeps the story presentation helpers focused on rendering, while parsing is
 * delegated to the backend story service.
 */

import { marked } from 'marked';

const STORY_BLOCK_REGEX = /```story[\s\S]*?```/g;

export function renderMarkdown(content: string): string {
  if (!content) return '';
  const cleanContent = content.replace(STORY_BLOCK_REGEX, '');
  return marked.parse(cleanContent);
}

export function getProgress(currentIndex: number, totalSections: number): number {
  if (!totalSections) return 0;
  const cappedIndex = Math.min(Math.max(currentIndex, 0), totalSections - 1);
  return Math.round(((cappedIndex + 1) / totalSections) * 100);
}
