/**
 * PanelExecutor - Render ASCII panels
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class PanelExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      // Interpolate variables in the panel content
      const content = this.interpolate(block.content, context.state)

      return {
        success: true,
        output: content,
      }
    } catch (error) {
      return {
        success: false,
        error: `PanelExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private interpolate(text: string, state: any): string {
    return text.replace(/\$([a-zA-Z_][a-zA-Z0-9_.$\[\]]*)/g, (match, varName) => {
      const value = this.getNested(state, varName)
      return value !== undefined ? String(value) : match
    })
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
}
