/**
 * State Manager for uDOS Runtime
 * Handles variable storage, interpolation, nested access
 */

import { StateValue } from '../types'

export class StateManager {
  private state: StateValue = {}
  private watchers: Map<string, Function[]> = new Map()

  constructor(initialState?: StateValue) {
    if (initialState) {
      this.state = JSON.parse(JSON.stringify(initialState))
    }
  }

  /**
   * Get a value from state using dot notation
   * Examples: $player.name, $inventory[0].label, $world.layers[300].name
   */
  get(path: string): any {
    const parts = this.parsePath(path)
    let current = this.state

    for (const part of parts) {
      if (current == null) return undefined
      current = current[part]
    }

    return current
  }

  /**
   * Set a value in state using dot notation
   */
  set(path: string, value: any): void {
    const parts = this.parsePath(path)
    if (parts.length === 0) return

    let current = this.state
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i]
      if (!(part in current)) {
        current[part] = {}
      }
      current = current[part]
    }

    current[parts[parts.length - 1]] = value
    this.notifyWatchers(path)
  }

  /**
   * Increment a numeric value
   */
  increment(path: string, amount: number = 1): void {
    const current = this.get(path) ?? 0
    this.set(path, current + amount)
  }

  /**
   * Decrement a numeric value
   */
  decrement(path: string, amount: number = 1): void {
    const current = this.get(path) ?? 0
    this.set(path, current - amount)
  }

  /**
   * Toggle a boolean value
   */
  toggle(path: string): void {
    const current = this.get(path) ?? false
    this.set(path, !current)
  }

  /**
   * Interpolate variables in a string
   * Example: "Hello $player.name" -> "Hello Traveller"
   */
  interpolate(text: string): string {
    return text.replace(/\$([a-zA-Z_][a-zA-Z0-9_.$\[\]]*)/g, (match, varName) => {
      const value = this.get(varName)
      return value != null ? String(value) : match
    })
  }

  /**
   * Get all state
   */
  getAll(): StateValue {
    return JSON.parse(JSON.stringify(this.state))
  }

  /**
   * Set all state
   */
  setAll(state: StateValue): void {
    this.state = JSON.parse(JSON.stringify(state))
  }

  /**
   * Merge state
   */
  merge(partial: Partial<StateValue>): void {
    this.state = { ...this.state, ...partial }
  }

  /**
   * Watch for changes to a path
   */
  watch(path: string, callback: Function): void {
    if (!this.watchers.has(path)) {
      this.watchers.set(path, [])
    }
    this.watchers.get(path)!.push(callback)
  }

  /**
   * Parse dot notation path into parts
   * "player.pos.tile" -> ["player", "pos", "tile"]
   * "inventory[0].label" -> ["inventory", "0", "label"]
   */
  private parsePath(path: string): string[] {
    const parts: string[] = []
    let current = ''
    let inBrackets = false

    for (let i = 0; i < path.length; i++) {
      const char = path[i]

      if (char === '[') {
        if (current) parts.push(current)
        current = ''
        inBrackets = true
      } else if (char === ']') {
        if (current) parts.push(current)
        current = ''
        inBrackets = false
      } else if (char === '.' && !inBrackets) {
        if (current) parts.push(current)
        current = ''
      } else {
        current += char
      }
    }

    if (current) parts.push(current)
    return parts.filter(p => p.length > 0)
  }

  private notifyWatchers(path: string): void {
    const callbacks = this.watchers.get(path) || []
    callbacks.forEach(cb => cb(this.get(path)))
  }
}
