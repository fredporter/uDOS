/**
 * Markdown Parser for uDOS Scripts
 * Extracts frontmatter, sections, and runtime blocks
 */

import { Document, Frontmatter, Section, RuntimeBlock } from '../types'

export class MarkdownParser {
  static parse(markdown: string): Document {
    const lines = markdown.split('\n')
    let idx = 0

    // Parse frontmatter (YAML between ---)
    const frontmatter = this.parseFrontmatter(lines, idx)
    idx = this.skipPastFrontmatter(lines, idx)

    // Parse sections and blocks
    const sections: Section[] = []
    let currentSection: Partial<Section> | null = null

    while (idx < lines.length) {
      const line = lines[idx]
      const trimmed = line.trim()

      // Section header (## Title)
      if (trimmed.startsWith('## ')) {
        if (currentSection) {
          sections.push(currentSection as Section)
        }
        const title = trimmed.substring(3).trim()
        const id = this.titleToId(title)
        currentSection = {
          id,
          title,
          content: '',
          blocks: [],
        }
        idx++
        continue
      }

      // Runtime block (```block-type)
      if (trimmed.startsWith('```')) {
        const blockType = trimmed.substring(3).trim()
        if (this.isRuntimeBlock(blockType)) {
          idx++
          const { content, endIdx } = this.extractBlockContent(lines, idx)
          idx = endIdx

          if (currentSection) {
            currentSection.blocks!.push({
              type: blockType as any,
              content: content.trim(),
            })
          }
          continue
        }
      }

      // Regular content
      if (currentSection) {
        currentSection.content += line + '\n'
      }

      idx++
    }

    // Push final section
    if (currentSection) {
      sections.push(currentSection as Section)
    }

    return {
      frontmatter,
      sections,
      raw: markdown,
    }
  }

  private static parseFrontmatter(
    lines: string[],
    startIdx: number
  ): Frontmatter {
    const result: Partial<Frontmatter> = {
      title: 'uDOS Script',
      id: 'script',
      version: '1.0',
      runtime: 'udos-md-runtime',
      mode: 'teletext',
    }

    let idx = startIdx
    if (idx < lines.length && lines[idx].trim() === '---') {
      idx++
      while (idx < lines.length) {
        const trimmed = lines[idx].trim()
        if (trimmed === '---') break

        const match = trimmed.match(/^(\w+):\s*(.+)$/)
        if (match) {
          const [, key, value] = match
          const cleanValue = value.replace(/^["']|["']$/g, '').trim()
          result[key as keyof Frontmatter] = cleanValue as any
        }
        idx++
      }
    }

    return result as Frontmatter
  }

  private static skipPastFrontmatter(lines: string[], startIdx: number): number {
    let idx = startIdx
    let dashes = 0

    while (idx < lines.length) {
      const trimmed = lines[idx].trim()
      if (trimmed.startsWith('---')) {
        dashes++
        if (dashes === 2) {
          return idx + 1
        }
      }
      idx++
    }
    return idx
  }

  private static isRuntimeBlock(type: string): boolean {
    return [
      'state',
      'set',
      'form',
      'if',
      'else',
      'nav',
      'panel',
      'map',
      'script',
    ].includes(type)
  }

  private static extractBlockContent(
    lines: string[],
    startIdx: number
  ): { content: string; endIdx: number } {
    const content: string[] = []
    let idx = startIdx

    while (idx < lines.length) {
      const trimmed = lines[idx].trim()
      if (trimmed.startsWith('```')) {
        return { content: content.join('\n'), endIdx: idx + 1 }
      }
      content.push(lines[idx])
      idx++
    }

    return { content: content.join('\n'), endIdx: idx }
  }

  private static titleToId(title: string): string {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }
}
