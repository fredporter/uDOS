/**
 * Executor Factory
 * Creates executor instances based on block type
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { StateExecutor } from './state-executor'
import { SetExecutor } from './set-executor'
import { FormExecutor } from './form-executor'
import { ConditionalExecutor, ElseExecutor } from './conditional-executor'
import { NavigationExecutor } from './nav-executor'
import { PanelExecutor } from './panel-executor'
import { MapExecutor } from './map-executor'
import { BaseExecutor } from './base'

/**
 * ExecutorFactory - Creates appropriate executor for block type
 */
export class ExecutorFactory {
  static create(blockType: string): BaseExecutor | null {
    switch (blockType) {
      case 'state':
        return new StateExecutor()
      case 'set':
        return new SetExecutor()
      case 'form':
        return new FormExecutor()
      case 'if':
        return new ConditionalExecutor()
      case 'else':
        return new ElseExecutor()
      case 'nav':
        return new NavigationExecutor()
      case 'panel':
        return new PanelExecutor()
      case 'map':
        return new MapExecutor()
      default:
        return null
    }
  }

  static async execute(
    block: RuntimeBlock,
    context: ExecutionContext
  ): Promise<ExecutorResult> {
    const executor = ExecutorFactory.create(block.type)
    if (!executor) {
      return {
        success: false,
        error: `Unknown block type: ${block.type}`,
      }
    }
    return executor.execute(block, context)
  }
}
