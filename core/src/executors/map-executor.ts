/**
 * MapExecutor - Render viewport with sprites
 */

import { RuntimeBlock, ExecutionContext, ExecutorResult } from '../types'
import { BaseExecutor } from './base'

export class MapExecutor extends BaseExecutor {
  async execute(block: RuntimeBlock, context: ExecutionContext): Promise<ExecutorResult> {
    try {
      const mapConfig = this.parseMapConfig(block.content, context.state)
      const output = this.renderMap(mapConfig)

      return {
        success: true,
        output,
        mapConfig,
      } as any
    } catch (error) {
      return {
        success: false,
        error: `MapExecutor error: ${error instanceof Error ? error.message : String(error)}`,
      }
    }
  }

  private parseMapConfig(content: string, state: any): any {
    const config: any = {
      width: 20,
      height: 10,
      viewport: false,
      sprites: [],
      terrain: [],
    }

    const lines = content.split('\n')
    let currentSprite: any = null
    let parsingSprite = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmed = line.trim()

      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('/*')) {
        continue
      }

      // Lines should have colon separator for key:value pairs
      if (!trimmed.includes(':')) {
        continue
      }

      const colonIndex = trimmed.indexOf(':')
      const key = trimmed.substring(0, colonIndex).trim()
      const value = trimmed.substring(colonIndex + 1).trim()

      // Handle top-level map properties
      if (key === 'width') {
        config.width = parseInt(value)
        parsingSprite = false
      } else if (key === 'height') {
        config.height = parseInt(value)
        parsingSprite = false
      } else if (key === 'viewport') {
        config.viewport = value === 'true'
        parsingSprite = false
      } else if (key === 'sprite') {
        // Save previous sprite if it exists
        if (currentSprite && currentSprite.ch && currentSprite.x !== undefined && currentSprite.y !== undefined) {
          config.sprites.push(currentSprite)
        }
        // Start new sprite
        currentSprite = { name: value, ch: '@', x: 0, y: 0 }
        parsingSprite = true
      } else if (parsingSprite && currentSprite) {
        // Parse sprite properties
        if (key === 'ch') {
          currentSprite.ch = value.replace(/^["']|["']$/g, '')
        } else if (key === 'x') {
          const evaluated = this.evaluateExpression(value, state)
          currentSprite.x = evaluated
        } else if (key === 'y') {
          const evaluated = this.evaluateExpression(value, state)
          currentSprite.y = evaluated
        }
      }
    }

    // Add last sprite if exists
    if (currentSprite && currentSprite.ch && currentSprite.x !== undefined && currentSprite.y !== undefined) {
      config.sprites.push(currentSprite)
    }

    return config
  }

  private evaluateExpression(expr: string, state: any): number {
    let result = expr.trim()

    // Replace $var and $var.prop with their values
    result = result.replace(/\$([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)/g, (match, varPath) => {
      // varPath is like "player.x", and state is { player: {...}, ... }
      const value = this.getNested(state, varPath)
      if (value !== undefined && value !== null) {
        return String(value)
      }
      return '0'
    })

    try {
      // eslint-disable-next-line no-eval
      return Number(eval(result))
    } catch {
      return 0
    }
  }

  private renderMap(config: any): string {
    const { width, height, sprites } = config
    const grid: string[][] = Array(height)
      .fill(null)
      .map(() => Array(width).fill('.'))

    // Place sprites
    for (const sprite of sprites) {
      const x = Math.min(Math.max(sprite.x, 0), width - 1)
      const y = Math.min(Math.max(sprite.y, 0), height - 1)
      if (grid[y] && x < width) {
        grid[y][x] = sprite.char
      }
    }

    // Render with borders
    let output = '┌' + '─'.repeat(width) + '┐\n'
    for (const row of grid) {
      output += '│' + row.join('') + '│\n'
    }
    output += '└' + '─'.repeat(width) + '┘\n'

    return output
  }
}
