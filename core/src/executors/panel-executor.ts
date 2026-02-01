/**
 * PanelExecutor - Render ASCII panels
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class PanelExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
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
}
