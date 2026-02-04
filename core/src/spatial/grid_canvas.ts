/**
 * Grid canvas interfaces (stub) for UGRID core.
 * Keep in sync with docs/specs/07-grid-canvas-rendering.md
 */

export type GridCanvasMode = "dashboard" | "calendar" | "schedule" | "table" | "map"

export interface GridCanvasSpec {
  width: 80
  height: 30
  title?: string
  theme?: string
  mode?: GridCanvasMode
}

export interface GridCanvasHeader {
  size: string
  title?: string
  mode?: GridCanvasMode
  theme?: string
  ts?: string
  [key: string]: unknown
}

export interface GridRenderResult {
  header: GridCanvasHeader
  lines: string[]
  rawText: string
}

export interface RendererBackend {
  emit(result: GridRenderResult): string
}

export interface Canvas80x30 {
  clear(fill?: string): void
  box(x: number, y: number, w: number, h: number, style?: string, title?: string): void
  text(x: number, y: number, w: number, h: number, content: string, opts?: Record<string, unknown>): void
  table(x: number, y: number, w: number, h: number, columns: unknown[], rows: unknown[], opts?: Record<string, unknown>): void
  list(x: number, y: number, w: number, h: number, items: string[], bullet?: string): void
  minimap(x: number, y: number, w: number, h: number, cells: unknown, opts?: Record<string, unknown>): void
  toLines(): string[]
}

export interface GridCanvasRenderer {
  render(spec: GridCanvasSpec, data?: Record<string, unknown>): GridRenderResult
}
