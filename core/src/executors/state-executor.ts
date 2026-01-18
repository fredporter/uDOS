/**
 * StateExecutor - Initialize state from block
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class StateExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const content = block.content.trim()

      // Handle multi-line assignments (arrays, objects spanning multiple lines)
      let processedContent = ''
      let inMultiline = false
      let currentLine = ''

      for (const line of content.split('\n')) {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith('/*')) continue

        currentLine += line + '\n'

        // Check if we're in a multi-line structure
        const openBrackets = (currentLine.match(/[\[\{]/g) || []).length
        const closeBrackets = (currentLine.match(/[\]\}]/g) || []).length

        if (openBrackets > closeBrackets) {
          inMultiline = true
        } else if (inMultiline && openBrackets === closeBrackets && currentLine.includes('=')) {
          inMultiline = false
          processedContent += currentLine
          currentLine = ''
        } else if (!inMultiline && currentLine.includes('=')) {
          processedContent += currentLine
          currentLine = ''
        }
      }

      if (currentLine.trim()) {
        processedContent += currentLine
      }

      // Parse assignments
      const assignmentRegex = /\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([\s\S]+?)(?=\n\$|$)/g
      let match

      while ((match = assignmentRegex.exec(processedContent)) !== null) {
        const varName = match[1]
        const valueStr = match[2].trim()

        try {
          // Try JSON parse first
          const value = JSON.parse(valueStr)
          context.state[varName] = value
        } catch {
          // Try evaluating as JavaScript (for unquoted keys)
          try {
            // eslint-disable-next-line no-eval
            const value = eval(`(${valueStr})`)
            context.state[varName] = value
          } catch {
            // Fallback: treat as string
            context.state[varName] = valueStr.trim()
          }
        }
      }

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: `StateExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }
}
