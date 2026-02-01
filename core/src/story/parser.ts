/**
 * Story Parser Utilities
 *
 * Parses -story.md files into structured StoryState objects:
 * 1. Extract YAML frontmatter
 * 2. Split markdown into sections (separated by ---)
 * 3. Extract ```story code blocks as form questions
 * 4. Build section index and field references
 */

import YAML from "js-yaml";
import type {
  StoryFrontmatter,
  StorySection,
  FormField,
  StoryState,
} from "./types";

/**
 * Parse -story.md file content into StoryState
 */
export function parseStoryFile(content: string): StoryState {
  // Step 1: Extract frontmatter
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) {
    throw new Error("Story file must start with YAML frontmatter");
  }

  const frontmatter = YAML.load(frontmatterMatch[1]) as StoryFrontmatter;
  const bodyContent = content.slice(frontmatterMatch[0].length).trim();

  // Step 2: Extract variables section (at end of file, starts with ONLY ---)
  // Variables section must start with --- on its own line, then YAML
  // Section separators are --- followed by optional whitespace then a heading (# Title)
  const variablesMatch = bodyContent.match(/\n---\n(?!\s*#)([\s\S]*)$/);
  let variablesContent = "";
  let mainContent = bodyContent;

  if (variablesMatch) {
    variablesContent = variablesMatch[1];
    mainContent = bodyContent.slice(0, bodyContent.indexOf(variablesMatch[0]));
  }

  // Parse variables section (YAML format)
  const variables = variablesContent
    ? (YAML.load(variablesContent) as Record<string, any>)
    : frontmatter.variables || {};

  // Step 3: Split main content into sections (separated by ---)
  const sectionTexts = mainContent.split(/\n---\n/);

  // Step 4: Build sections with questions
  const sections: StorySection[] = sectionTexts.map((text, index) => {
    const section = parseSection(text, index, variables);
    return section;
  });

  // Initialize answer object with default values
  const answers: Record<string, any> = { ...variables };
  sections.forEach((section) => {
    section.questions.forEach((question) => {
      if (!(question.name in answers)) {
        answers[question.name] = question.value || "";
      }
    });
  });

  return {
    frontmatter,
    sections,
    currentSectionIndex: 0,
    answers,
    isComplete: false,
  };
}

/**
 * Parse a single section into title, content, and questions
 */
export function parseSection(
  text: string,
  index: number,
  variables: Record<string, any>,
): StorySection {
  const lines = text.trim().split("\n");

  // First line should be # Title
  let titleLine = 0;
  let title = `Section ${index + 1}`;

  if (lines[0].startsWith("# ")) {
    title = lines[0].slice(2).trim();
    titleLine = 1;
  }

  // Extract ```story blocks as questions
  const questions = extractStoryBlocks(text);

  // Rest is content (markdown)
  const contentLines = lines.slice(titleLine);
  const content = contentLines.join("\n").trim();

  return {
    id: `section-${index}`,
    title,
    content,
    questions,
    order: index,
  };
}

/**
 * Extract ```story blocks from section text
 *
 * ```story block format:
 * ```story
 * name: field_name
 * label: "What is your name?"
 * type: text
 * required: true
 * ```
 */
export function extractStoryBlocks(text: string): FormField[] {
  const questions: FormField[] = [];

  // Match all ```story ... ``` blocks
  const blockRegex = /```story\n([\s\S]*?)\n```/g;
  let match;

  while ((match = blockRegex.exec(text)) !== null) {
    const blockContent = match[1];
    const field = parseStoryBlock(blockContent);
    if (field) {
      questions.push(field);
    }
  }

  return questions;
}

/**
 * Parse a single ```story block into FormField
 */
export function parseStoryBlock(content: string): FormField | null {
  try {
    // Parse as YAML
    const data = YAML.load(content) as Record<string, any>;

    if (!data.name || !data.label) {
      console.warn("Story block missing required fields: name, label");
      return null;
    }

    return {
      name: data.name,
      label: data.label,
      type: data.type || "text",
      required: data.required || false,
      placeholder: data.placeholder,
      options: data.options || (data.type === "select" ? [] : undefined),
      value: data.value || "",
      validation: data.validation,
    };
  } catch (error) {
    console.error("Failed to parse story block:", error);
    return null;
  }
}

/**
 * Render markdown content to HTML
 */
type MarkedFn = (content: string) => string | Promise<string>;
let cachedMarked: MarkedFn | null = null;

async function loadMarked(): Promise<MarkedFn> {
  if (cachedMarked) {
    return cachedMarked;
  }

  const module = await import("marked");
  cachedMarked = module.marked;
  return cachedMarked;
}

export async function renderMarkdown(content: string): Promise<string> {
  // Remove ```story blocks before rendering
  const cleanContent = content.replace(/```story\n[\s\S]*?\n```\n?/g, "");
  const markedFn = await loadMarked();
  return await markedFn(cleanContent);
}

/**
 * Get progress percentage
 */
export function getProgress(
  currentIndex: number,
  totalSections: number,
): number {
  if (totalSections === 0) return 0;
  return Math.round(((currentIndex + 1) / totalSections) * 100);
}

export type {
  StoryState,
  StorySection,
  FormField,
  StoryFrontmatter,
} from "./types";
