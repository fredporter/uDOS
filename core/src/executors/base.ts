/**
 * Base Executor Interface
 * All block executors implement this interface
 */

import {
  RuntimeBlock,
  ExecutionContext,
  ExecutorResult,
  RuntimeValue,
} from '../types'

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
   * Helper: Evaluate a condition
   */
  protected evaluateCondition(condition: string, state: any): boolean {
    let expr = condition.trim()

    // Replace variables with their values
    expr = expr.replace(/\$([a-zA-Z_][a-zA-Z0-9_.$\[\]]*)/g, (match, varName) => {
      const value = this.getNested(state, varName)
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

  /**
   * Helper: Parse simple literals + auto-detect types
   */
  protected parseLiteral(value: string | undefined): RuntimeValue {
    if (value === undefined) {
      return ''
    }

    const trimmed = value.trim()
    if (!trimmed) {
      return ''
    }

    if (trimmed === 'true') {
      return true
    }
    if (trimmed === 'false') {
      return false
    }
    if (trimmed === 'null') {
      return null
    }
    if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
      return Number(trimmed)
    }

    if (
      (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      (trimmed.startsWith("[") && trimmed.endsWith("]")) ||
      (trimmed.startsWith("{") && trimmed.endsWith("}"))
    ) {
      try {
        return JSON.parse(trimmed)
      } catch {
        const normalize = (input: string) =>
          input.replace(/([a-zA-Z0-9_$]+)\s*:/g, '"$1":')

        try {
          const normalized = normalize(trimmed)
          return JSON.parse(normalized)
        } catch {
          // fall through to string fallback
        }
      }
    }

    return trimmed.replace(/^["']|["']$/g, '')
  }

  /**
   * Interpolate `$` templates against state
   */
  protected interpolate(text: string, state: any): string {
    if (!text) {
      return ''
    }

    return text.replace(/\$([a-zA-Z_][a-zA-Z0-9_.$\[\]]*)/g, (match, varName) => {
      const value = this.getNested(state, varName)
      return value !== undefined && value !== null ? String(value) : match
    })
  }

  /**
   * Resolve literal value after interpolation
   */
  protected resolveLiteral(value: string | undefined, state: any): RuntimeValue {
    const interpolated = this.interpolate(value ?? '', state)
    return this.parseLiteral(interpolated)
  }

  /**
   * Parse comma/JSON list of params for SQL or other operations
   */
  protected parseParams(params: string | undefined, state: any): RuntimeValue[] {
    if (!params) {
      return []
    }

    const interpolated = this.interpolate(params, state).trim()
    if (!interpolated) {
      return []
    }

    try {
      const parsed = JSON.parse(interpolated)
      if (Array.isArray(parsed)) {
        return parsed
      }
    } catch {
      // ignore JSON parse errors
    }

    return interpolated
      .split(',')
      .map(segment => segment.trim())
      .filter(Boolean)
      .map(segment => this.parseLiteral(segment))
  }

  /**
   * Parse number strings safely
   */
  protected parseNumber(value: string | undefined, state: any, fallback = 0): number {
    if (!value) {
      return fallback
    }
    const interpolated = this.interpolate(value, state)
    const parsed = Number(interpolated)
    return Number.isNaN(parsed) ? fallback : parsed
  }

  protected getNested(obj: any, path: string): any {
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

  protected setNested(obj: any, path: string, value: any): void {
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
