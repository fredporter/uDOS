/**
 * SetExecutor - Execute set operations (set, inc, dec, toggle)
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class SetExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const lines = block.content.split('\n').filter(l => l.trim())

      for (const line of lines) {
        const trimmed = line.trim()

        const setMatch = trimmed.match(/^set\s+\$([a-zA-Z_][\w.]*)\s*(?:=\s*)?(.+)$/)
        if (setMatch) {
          const [, varPath, rawValue] = setMatch
          const parsedValue = this.resolveLiteral(rawValue, context.state)
          this.setNested(context.state, varPath, parsedValue)
          continue
        }

        const incMatch = trimmed.match(/^inc\s+\$([a-zA-Z_][\w.]*)(?:\s+(.+))?$/)
        if (incMatch) {
          const [, varPath, deltaRaw] = incMatch
          const amount = this.parseNumber(deltaRaw, context.state, 1)
          const current = Number(this.getNested(context.state, varPath) ?? 0)
          this.setNested(context.state, varPath, current + amount)
          continue
        }

        const decMatch = trimmed.match(/^dec\s+\$([a-zA-Z_][\w.]*)(?:\s+(.+))?$/)
        if (decMatch) {
          const [, varPath, deltaRaw] = decMatch
          const amount = this.parseNumber(deltaRaw, context.state, 1)
          const current = Number(this.getNested(context.state, varPath) ?? 0)
          this.setNested(context.state, varPath, current - amount)
          continue
        }

        const toggleMatch = trimmed.match(/^toggle\s+\$([a-zA-Z_][\w.]*)$/)
        if (toggleMatch) {
          const [, varPath] = toggleMatch
          const current = this.getNested(context.state, varPath)
          const normalized = typeof current === 'boolean' ? current : Boolean(current)
          this.setNested(context.state, varPath, !normalized)
        }
      }

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: `SetExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

}
