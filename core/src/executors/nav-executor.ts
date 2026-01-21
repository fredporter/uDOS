/**
 * NavigationExecutor - Handle navigation choices
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class NavigationExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const choices = this.parseChoices(block.content, context.state)

      // Render navigation UI
      const output = this.renderChoices(choices)

      return {
        success: true,
        output,
        choices,
        isNavigation: true,
      } as any
    } catch (error) {
      return {
        success: false,
        error: `NavigationExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private parseChoices(content: string, state: any): Array<{ text: string; target?: string; available: boolean }> {
    const choices: Array<{ text: string; target?: string; available: boolean }> = []
    const lines = content.split('\n')
    let currentChoice: any = null

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue

      const isIndented = line.startsWith('  ')

      if (!isIndented && trimmed.startsWith('choice:')) {
        // New choice
        if (currentChoice) {
          choices.push(currentChoice)
        }

        const text = trimmed.substring('choice:'.length).trim().replace(/^["']|["']$/g, '')
        currentChoice = { text, available: true }
      } else if (isIndented && currentChoice) {
        // Choice property
        if (trimmed.startsWith('when:')) {
          const condition = trimmed.substring('when:'.length).trim()
          currentChoice.available = this.evaluateCondition(condition, state)
        } else if (trimmed.startsWith('target:')) {
          currentChoice.target = trimmed.substring('target:'.length).trim().replace(/^["']|["']$/g, '')
        }
      }
    }

    if (currentChoice) {
      choices.push(currentChoice)
    }

    return choices
  }

  private renderChoices(choices: Array<{ text: string; target?: string; available: boolean }>): string {
    let output = '┌' + '─'.repeat(40) + '┐\n'
    output += '│ What do you want to do?              │\n'
    output += '├' + '─'.repeat(40) + '┤\n'

    let index = 1
    for (const choice of choices) {
      const status = choice.available ? `[${index}]` : '[ ]'
      const text = choice.available ? choice.text : `${choice.text} (unavailable)`
      output += `│ ${status} ${text.padEnd(35)}│\n`
      if (choice.available) index++
    }

    output += '└' + '─'.repeat(40) + '┘\n'

    return output
  }
}
