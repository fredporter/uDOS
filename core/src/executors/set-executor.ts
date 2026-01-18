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

        // set $var value
        if (trimmed.startsWith('set ')) {
          const [, rest] = trimmed.split('set ', 2)
          const parts = rest.trim().split(/\s+/, 2)
          if (parts.length >= 2) {
            const varPath = parts[0].replace('$', '')
            const value = parts[1]
            this.setNested(context.state, varPath, isNaN(Number(value)) ? value : Number(value))
          }
        }

        // inc $var [amount]
        if (trimmed.startsWith('inc ')) {
          const [, rest] = trimmed.split('inc ', 2)
          const parts = rest.trim().split(/\s+/)
          const varPath = parts[0].replace('$', '')
          const amount = parseInt(parts[1] || '1')
          const current = this.getNested(context.state, varPath) || 0
          this.setNested(context.state, varPath, current + amount)
        }

        // dec $var [amount]
        if (trimmed.startsWith('dec ')) {
          const [, rest] = trimmed.split('dec ', 2)
          const parts = rest.trim().split(/\s+/)
          const varPath = parts[0].replace('$', '')
          const amount = parseInt(parts[1] || '1')
          const current = this.getNested(context.state, varPath) || 0
          this.setNested(context.state, varPath, current - amount)
        }

        // toggle $var
        if (trimmed.startsWith('toggle ')) {
          const [, varPath] = trimmed.split('toggle ', 2)
          const path = varPath.trim().replace('$', '')
          const current = this.getNested(context.state, path)
          this.setNested(context.state, path, !current)
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

  private getNested(obj: any, path: string): any {
    const parts = path.split('.')
    let current = obj
    for (const part of parts) {
      if (current?.[part] !== undefined) {
        current = current[part]
      } else {
        return undefined
      }
    }
    return current
  }

  private setNested(obj: any, path: string, value: any): void {
    const parts = path.split('.')
    let current = obj
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i]
      if (current[part] === undefined) {
        current[part] = {}
      }
      current = current[part]
    }
    current[parts[parts.length - 1]] = value
  }
}
