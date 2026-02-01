import { RuntimeState, RuntimeValue, RuntimeSnapshot, StatePersistence } from '../types'

export class StateStore implements RuntimeState {
  private vars: Map<string, RuntimeValue>
  private persistence?: StatePersistence

  constructor(initial?: RuntimeSnapshot, persistence?: StatePersistence) {
    this.vars = new Map()
    if (initial) {
      for (const [key, value] of Object.entries(initial)) {
        this.vars.set(key, value)
      }
    }
    this.persistence = persistence
  }

  get(name: string): RuntimeValue {
    return this.vars.get(name) ?? null
  }

  set(name: string, value: RuntimeValue): void {
    this.vars.set(name, value)
  }

  has(name: string): boolean {
    return this.vars.has(name)
  }

  delete(name: string): void {
    this.vars.delete(name)
  }

  snapshot(): RuntimeSnapshot {
    const snapshot: RuntimeSnapshot = {}
    for (const [key, value] of this.vars.entries()) {
      snapshot[key] = value
    }
    return snapshot
  }

  restore(snapshot: RuntimeSnapshot): void {
    this.vars.clear()
    for (const [key, value] of Object.entries(snapshot)) {
      this.vars.set(key, value)
    }
  }

  clear(): void {
    this.vars.clear()
  }

  async persist(): Promise<void> {
    if (!this.persistence) {
      return
    }
    const snapshot = this.snapshot()
    await this.persistence.save(snapshot)
  }

  async load(): Promise<void> {
    if (!this.persistence) {
      return
    }
    const data = await this.persistence.load()
    if (data) {
      this.restore(data)
    }
  }
}
