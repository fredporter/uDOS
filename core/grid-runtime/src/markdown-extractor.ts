/**
 * MarkdownCodeBlockExtractor - Extract code blocks from markdown files
 * Phase 3: Code Block Parser component
 *
 * Extracts blocks in format:
 * ```teletext
 * ...
 * ```
 *
 * ```grid
 * ...
 * ```
 *
 * ```tiles
 * ...
 * ```
 */

import { CodeBlock } from "./code-block-parser.js";

/**
 * Extracted code block with metadata
 */
export interface ExtractedCodeBlock extends CodeBlock {
  lineNumber: number;
}

/**
 * MarkdownCodeBlockExtractor: Find and extract code blocks from markdown
 */
export class MarkdownCodeBlockExtractor {
  /**
   * Extract all code blocks from markdown content
   * @param markdown - Markdown file content
   * @returns Array of extracted code blocks
   */
  public extractBlocks(markdown: string): ExtractedCodeBlock[] {
    const blocks: ExtractedCodeBlock[] = [];
    const lines = markdown.split("\n");

    let i = 0;
    while (i < lines.length) {
      const line = lines[i];

      // Look for opening fence with type
      const match = line.match(/^```(\w+)\s*(.*)?$/);
      if (match) {
        const blockType = match[1];
        const metadata = match[2] ? this.parseMetadata(match[2]) : undefined;
        const lineNumber = i + 1;

        // Valid block types
        if (["teletext", "grid", "tiles"].includes(blockType)) {
          // Collect content until closing fence
          i++;
          const contentLines: string[] = [];

          while (i < lines.length) {
            if (lines[i].match(/^```\s*$/)) {
              // Found closing fence
              break;
            }
            contentLines.push(lines[i]);
            i++;
          }

          blocks.push({
            type: blockType as "teletext" | "grid" | "tiles",
            content: contentLines.join("\n"),
            metadata,
            lineNumber,
          });
        }
      }

      i++;
    }

    return blocks;
  }

  /**
   * Extract blocks of a specific type
   * @param markdown - Markdown content
   * @param type - Block type to extract
   * @returns Array of matching blocks
   */
  public extractBlocksByType(
    markdown: string,
    type: "teletext" | "grid" | "tiles"
  ): ExtractedCodeBlock[] {
    return this.extractBlocks(markdown).filter((block) => block.type === type);
  }

  /**
   * Extract first block of a type (useful for single-block files)
   * @param markdown - Markdown content
   * @param type - Block type to find
   * @returns First matching block or undefined
   */
  public extractFirstBlock(
    markdown: string,
    type: "teletext" | "grid" | "tiles"
  ): ExtractedCodeBlock | undefined {
    return this.extractBlocksByType(markdown, type)[0];
  }

  /**
   * Extract grid blocks (locations)
   * @param markdown - Markdown content
   * @returns Array of grid blocks
   */
  public extractGridBlocks(markdown: string): ExtractedCodeBlock[] {
    return this.extractBlocksByType(markdown, "grid");
  }

  /**
   * Extract tiles blocks (tile definitions)
   * @param markdown - Markdown content
   * @returns Array of tiles blocks
   */
  public extractTilesBlocks(markdown: string): ExtractedCodeBlock[] {
    return this.extractBlocksByType(markdown, "tiles");
  }

  /**
   * Extract teletext blocks (ASCII art)
   * @param markdown - Markdown content
   * @returns Array of teletext blocks
   */
  public extractTeletextBlocks(markdown: string): ExtractedCodeBlock[] {
    return this.extractBlocksByType(markdown, "teletext");
  }

  /**
   * Parse inline metadata from fence
   * Examples: ```grid location-name, ```tiles v1.0
   * @param metadata - Metadata string
   * @returns Metadata object
   */
  private parseMetadata(metadata: string): Record<string, string> {
    const result: Record<string, string> = {};

    // Split by comma
    const parts = metadata.split(",").map((p) => p.trim());

    for (const part of parts) {
      if (part.includes("=")) {
        const [key, value] = part.split("=").map((p) => p.trim());
        result[key] = value;
      } else if (part) {
        // Positional metadata
        result[`_${Object.keys(result).length}`] = part;
      }
    }

    return result;
  }

  /**
   * Find block by name/identifier in metadata
   * @param markdown - Markdown content
   * @param name - Block name
   * @returns Matching block or undefined
   */
  public findBlockByName(markdown: string, name: string): ExtractedCodeBlock | undefined {
    const blocks = this.extractBlocks(markdown);

    for (const block of blocks) {
      if (block.metadata) {
        // Check _0 (first positional) or "name" key
        if (block.metadata._0 === name || block.metadata.name === name) {
          return block;
        }
      }
    }

    return undefined;
  }

  /**
   * Count blocks by type
   * @param markdown - Markdown content
   * @returns Object with counts
   */
  public countBlocks(
    markdown: string
  ): { teletext: number; grid: number; tiles: number; total: number } {
    const blocks = this.extractBlocks(markdown);
    const counts = {
      teletext: 0,
      grid: 0,
      tiles: 0,
      total: blocks.length,
    };

    for (const block of blocks) {
      counts[block.type]++;
    }

    return counts;
  }

  /**
   * Validate markdown has all required block types
   * @param markdown - Markdown content
   * @param requiredTypes - Types that must be present
   * @returns True if all required types present
   */
  public hasAllBlockTypes(
    markdown: string,
    requiredTypes: Array<"teletext" | "grid" | "tiles">
  ): boolean {
    const blocks = this.extractBlocks(markdown);
    const present = new Set(blocks.map((b) => b.type));

    for (const required of requiredTypes) {
      if (!present.has(required)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get block statistics
   * @param markdown - Markdown content
   * @returns Statistics object
   */
  public getStatistics(markdown: string): {
    totalBlocks: number;
    types: Record<string, number>;
    averageSize: number;
    maxSize: number;
    minSize: number;
  } {
    const blocks = this.extractBlocks(markdown);

    const stats = {
      totalBlocks: blocks.length,
      types: { teletext: 0, grid: 0, tiles: 0 },
      averageSize: 0,
      maxSize: 0,
      minSize: Infinity,
    };

    let totalSize = 0;

    for (const block of blocks) {
      stats.types[block.type]++;

      const size = block.content.length;
      totalSize += size;
      stats.maxSize = Math.max(stats.maxSize, size);
      stats.minSize = Math.min(stats.minSize, size);
    }

    if (blocks.length > 0) {
      stats.averageSize = Math.round(totalSize / blocks.length);
    }

    return stats;
  }
}
