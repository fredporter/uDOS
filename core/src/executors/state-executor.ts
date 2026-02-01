/**
 * StateExecutor - Initialize state from block
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class StateExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const content = block.content
      const assignments = this.extractAssignments(content)

      for (const { varName, rawValue } of assignments) {
        if (!rawValue) {
          continue
        }

        if (this.getNested(context.state, varName) !== undefined) {
          continue
        }

        const parsed = this.resolveLiteral(rawValue, context.state)
        this.setNested(context.state, varName, parsed)
      }

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: `StateExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private extractAssignments(content: string): Array<{ varName: string; rawValue: string }> {
    const assignments: Array<{ varName: string; rawValue: string }> = []
    let currentVar: string | null = null
    let buffer = ''

    const flush = () => {
      if (currentVar) {
        assignments.push({ varName: currentVar, rawValue: buffer.trim() })
        currentVar = null
        buffer = ''
      }
    }

    for (const rawLine of content.split('\n')) {
      const trimmed = rawLine.trim()
      if (!trimmed) {
        if (currentVar) {
          buffer += rawLine + '\n'
        }
        continue
      }

      if (trimmed.startsWith('//') || trimmed.startsWith('/*')) {
        if (currentVar) {
          buffer += rawLine + '\n'
        }
        continue
      }

      const match = trimmed.match(/^\$([a-zA-Z_][\w.]*)\s*=\s*(.*)$/)
      if (match) {
        flush()
        currentVar = match[1]
        buffer = match[2]
        continue
      }

      if (currentVar) {
        buffer += rawLine + '\n'
      }
    }

    flush()
    return assignments
  }
}
