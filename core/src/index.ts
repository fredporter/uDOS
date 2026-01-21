/**
 * uDOS Lean TypeScript Runtime
 * Parse and execute markdown scripts
 */

import { MarkdownParser } from './parser/markdown'
import { StateManager } from './state/manager'
import { ExecutorFactory } from './executors'
import {
  Document,
  RuntimeBlock,
  ExecutionContext,
  ExecutorResult,
  RuntimeConfig,
  Section,
} from './types'

export class Runtime {
  private doc: Document | null = null
  private state: StateManager
  private config: RuntimeConfig
  private currentSection: Section | null = null

  constructor(config: RuntimeConfig = {}) {
    this.state = new StateManager()
    this.config = {
      allowScripts: false,
      maxDepth: 100,
      timeout: 5000,
      ...config,
    }
  }

  /**
   * Load and parse a markdown script
   */
  load(markdown: string): void {
    this.doc = MarkdownParser.parse(markdown)
  }

  /**
   * Execute a section by ID
   */
  async execute(sectionId: string): Promise<ExecutorResult> {
    if (!this.doc) {
      return { success: false, error: 'No document loaded' }
    }

    const section = this.doc.sections.find(s => s.id === sectionId)
    if (!section) {
      return { success: false, error: `Section not found: ${sectionId}` }
    }

    this.currentSection = section

    const context: ExecutionContext = {
      state: this.state.getAll(),
      section,
      history: [],
      variables: new Map(),
    }

    // Execute blocks in sequence
    let output = ''
    let lastResult: ExecutorResult = { success: true }
    let inSkippedBranch = false
    
    for (let i = 0; i < section.blocks.length; i++) {
      const block = section.blocks[i]

      // Reset skip state at new if block
      if (block.type === 'if') {
        inSkippedBranch = false
      }

      // Don't execute if we're in a skipped branch
      if (inSkippedBranch && block.type !== 'if' && block.type !== 'else') {
        continue
      }

      const result = await this.executeBlock(block, context)
      
      if (!result.success) {
        return result
      }

      // Handle conditional skip logic
      if (block.type === 'if' && result.skip) {
        // If condition false, skip until else
        inSkippedBranch = true
      } else if (block.type === 'else') {
        if (result.skip) {
          // Else condition false (if was true), skip rest
          inSkippedBranch = true
        } else {
          // Else condition true (if was false), stop skipping
          inSkippedBranch = false
        }
      }

      if (result.output) {
        output += result.output + '\n'
      }
      if (result.nextSection) {
        return { ...result, nextSection: result.nextSection }
      }
      // Preserve form fields, choices, map config for final result
      lastResult = result
    }

    // Sync context.state back to this.state manager
    this.state.setAll(context.state)

    // Return last executor result with accumulated output
    return {
      success: true,
      output: output || this.renderSection(section),
      formFields: lastResult.formFields,
      choices: lastResult.choices,
      mapConfig: lastResult.mapConfig,
      isNavigation: lastResult.isNavigation,
    }
  }

  /**
   * Execute a single block
   */
  private async executeBlock(
    block: RuntimeBlock,
    context: ExecutionContext
  ): Promise<ExecutorResult> {
    return ExecutorFactory.execute(block, context)
  }

  /**
   * Render a section as output
   */
  private renderSection(section: Section): string {
    let output = `# ${section.title}\n\n`
    output += this.state.interpolate(section.content)
    return output
  }

  /**
   * Get current state
   */
  getState(): any {
    return this.state.getAll()
  }

  /**
   * Set state directly
   */
  setState(state: any): void {
    this.state.setAll(state)
  }

  /**
   * Get the loaded document
   */
  getDocument(): Document | null {
    return this.doc
  }
}

export { MarkdownParser, StateManager }
export * from './types'
