import { Runtime } from './runtime'
import { RuntimeConfig, ExecutorResult, Document } from '../types'

export interface RunnerResult extends ExecutorResult {
  executedSections: string[]
  aggregatedOutput: string
  history: ExecutorResult[]
  finalState: Record<string, any>
}

export class DocumentRunner {
  private runtime: Runtime

  constructor(config: RuntimeConfig = {}) {
    this.runtime = new Runtime(config)
  }

  async run(markdown: string, sectionId?: string): Promise<RunnerResult> {
    this.runtime.load(markdown)
    const doc = this.runtime.getDocument()

    if (!doc || doc.sections.length === 0) {
      return {
        success: false,
        error: 'Document contains no sections',
        executedSections: [],
        aggregatedOutput: '',
        history: [],
        finalState: this.runtime.getState(),
      }
    }

    const startSection = sectionId || doc.sections[0].id
    if (!startSection) {
      return {
        success: false,
        error: 'No section ID provided and document has no identifiable sections',
        executedSections: [],
        aggregatedOutput: '',
        history: [],
        finalState: this.runtime.getState(),
      }
    }

    const executedSections: string[] = []
    const history: ExecutorResult[] = []
    let aggregatedOutput = ''
    let currentSection: string | null = startSection
    const visited = new Set<string>()

    while (currentSection) {
      if (visited.has(currentSection) || visited.size > 50) {
        return {
          success: false,
          error: 'DocumentRunner detected a loop or too many sections',
          executedSections,
          aggregatedOutput: aggregatedOutput.trim(),
          history,
          finalState: this.runtime.getState(),
        }
      }

      visited.add(currentSection)
      const result = await this.runtime.execute(currentSection)
      history.push(result)
      executedSections.push(currentSection)
      if (!result.success) {
        return {
          ...result,
          success: false,
          executedSections,
          aggregatedOutput: aggregatedOutput.trim(),
          history,
          finalState: this.runtime.getState(),
        }
      }

      if (result.output) {
        aggregatedOutput += result.output + '\n'
      }

      currentSection = result.nextSection ?? null
    }

    const trimmedOutput = aggregatedOutput.trim()
    return {
      success: true,
      output: trimmedOutput || undefined,
      aggregatedOutput: trimmedOutput,
      executedSections,
      history,
      finalState: this.runtime.getState(),
    }
  }

  getState(): Record<string, any> {
    return this.runtime.getState()
  }

  setState(state: Record<string, any>): void {
    this.runtime.setState(state)
  }

  getDocument(): Document | null {
    return this.runtime.getDocument()
  }
}
