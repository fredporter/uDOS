/**
 * Base Executor Interface
 * All block executors implement this interface
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'

/**
 * Base interface for all block executors
 */
export interface IExecutor {
  execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult>
}

/**
 * Abstract base class for executors
 */
export abstract class BaseExecutor implements IExecutor {
  abstract execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult>

  /**
   * Helper: Parse simple key=value lines from block content
   */
  protected parseKeyValues(content: string): Record<string, string> {
    const result: Record<string, string> = {}
    const lines = content.split('\n').filter(l => l.trim())

    for (const line of lines) {
      const match = line.match(/^(\w+)\s*=\s*(.+)$/)
      if (match) {
        const [, key, value] = match
        result[key] = value.trim()
      }
    }

    return result
  }

  /**
   * Helper: Parse YAML-like nested structure
   */
  protected parseNested(content: string): Record<string, any> {
    const result: Record<string, any> = {}
    const lines = content.split('\n')
    let current: any = result
    let currentKey: string | null = null
    let indent = 0

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue

      const spaces = line.match(/^(\s*)/)?.[1].length || 0

      if (line.includes(':')) {
        const [key, ...valueParts] = trimmed.split(':')
        const value = valueParts.join(':').trim()

        if (spaces === 0) {
          // Top-level
          currentKey = key.trim()
          result[currentKey] = value || {}
          current = result[currentKey]
          indent = 0
        } else {
          // Nested
          if (typeof current === 'object' && current !== null) {
            current[key.trim()] = value
          }
        }
      }
    }

    return result
  }

  /**
   * Helper: Evaluate a condition
   */
  protected evaluateCondition(condition: string, state: any): boolean {
    let expr = condition.trim()

    // Replace variables with their values
    expr = expr.replace(/\$([a-zA-Z_][a-zA-Z0-9_.$\[\]]*)/g, (match, varName) => {
      const getValue = (obj: any, path: string): any => {
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

      const value = getValue(state, varName)
      if (value === undefined) return 'undefined'
      if (typeof value === 'string') return `"${value}"`
      return JSON.stringify(value)
    })

    try {
      // eslint-disable-next-line no-eval
      return Boolean(eval(expr))
    } catch {
      return false
    }
  }
}
