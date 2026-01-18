/**
 * Core Types for uDOS Markdown Runtime
 */

export interface Frontmatter {
  title: string
  id: string
  version: string
  runtime: string
  mode: 'teletext' | 'browser' | 'cli'
  stateDefaults?: 'preserve' | 'reset'
  data?: {
    db?: {
      provider?: string
      path?: string
      namespace?: string
      bind?: string[]
    }
  }
}

export interface RuntimeBlock {
  type: 'state' | 'set' | 'form' | 'if' | 'else' | 'nav' | 'panel' | 'map' | 'script'
  content: string
  metadata?: Record<string, any>
}

export interface Section {
  id: string
  title: string
  content: string
  blocks: RuntimeBlock[]
}

export interface Document {
  frontmatter: Frontmatter
  sections: Section[]
  raw: string
}

export interface StateValue {
  [key: string]: any
}

export interface FormField {
  var: string
  type: 'text' | 'number' | 'toggle' | 'choice' | 'email' | 'date'
  label?: string
  placeholder?: string
  min?: number
  max?: number
  options?: string[]
  required?: boolean
  default?: any
}

export interface NavChoice {
  label: string
  to: string
  when?: string // Conditional: "$player.has_key == true"
}

export interface Panel {
  title?: string
  content: string
  style?: 'box' | 'line' | 'block'
}

export interface MapConfig {
  center: string // Tile ID: "AA340-100"
  layer: number
  viewport: string // "15x9"
  style: 'teletext' | 'svg'
  show?: {
    terrain?: boolean
    sprites?: boolean
    poi?: boolean
    edges?: boolean
  }
  sprites?: Array<{
    id: string
    ch: string
    z: number
    pos: { tile: string; layer: number }
  }>
}

export interface ExecutionContext {
  state: StateValue
  section: Section
  currentBlock?: RuntimeBlock
  history: string[]
  variables: Map<string, any>
}

export interface ExecutorResult {
  success: boolean
  nextSection?: string
  stateChanges?: Partial<StateValue>
  output?: string
  error?: string
  skip?: boolean
  formFields?: FormField[]
  choices?: Array<{ text: string; target?: string; available: boolean }>
  isNavigation?: boolean
  mapConfig?: any
  [key: string]: any // Allow additional executor-specific properties
}

export interface RuntimeConfig {
  allowScripts?: boolean
  dbPath?: string
  maxDepth?: number
  timeout?: number
}
