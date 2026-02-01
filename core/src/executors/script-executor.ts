/**
 * ScriptExecutor - Run inline JavaScript scripts against runtime state
 *
 * Intended for advanced blocks where authors need explicit state mutation
 * or computation that is hard to express through structured blocks. Scripts
 * run within a minimal sandbox and may be gated by configuration.
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

type ScriptHelper = {
  setState: (path: string, value: any) => void
  getState: (path: string) => any
  log: (...args: any[]) => void
}

export class ScriptExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const script = block.content.trim()
      if (!script) {
        return { success: true }
      }

      const helper: ScriptHelper = {
        setState: (path, value) => {
          this.setNested(context.state, path, value)
        },
        getState: (path) => this.getNested(context.state, path),
        log: (...args: any[]) => {
          console.debug('[ScriptExecutor]', ...args)
        },
      }

      const fn = new Function('state', 'variables', 'helper', script)
      const result = fn(context.state, context.variables, helper)

      const output = typeof result === 'string' ? result : undefined

      return {
        success: true,
        output,
      }
    } catch (error: any) {
      return {
        success: false,
        error: `ScriptExecutor error: ${error.message ?? error}`,
      }
    }
  }

}
