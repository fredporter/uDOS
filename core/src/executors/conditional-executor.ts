/**
 * ConditionalExecutor - Execute if/else blocks
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class ConditionalExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const condition = block.content.trim()
      const isTrue = this.evaluateCondition(condition, context.state)

      // Store result for if/else chaining
      context.variables.set('__last_condition__', isTrue)

      if (!isTrue) {
        // Condition false - skip this block
        return { success: true, skip: true }
      }

      // Condition true - execute
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: `ConditionalExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }
}

export class ElseExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const lastCondition = context.variables.get('__last_condition__') ?? false

      if (lastCondition) {
        // Previous if was true - skip else
        return { success: true, skip: true }
      }

      // Previous if was false - execute else
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: `ElseExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }
}
