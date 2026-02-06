/**
 * Anchor types (stub) for universe + gameplay integration.
 * Keep in sync with docs/uDOS-Gameplay-Anchors-v1.3-Spec.md
 */

export type AnchorId =
  | "EARTH"
  | "SKY"
  | `GAME:${string}`
  | `BODY:${string}`
  | `CATALOG:${string}`

export type SpaceId = "SUR" | "SUB" | "UDN"
export type EffectiveLayer = `L${number}`
export type CellId = string
export type AnchorLocId = `${AnchorId}:${SpaceId}:${EffectiveLayer}-${CellId}`

export interface AnchorCoord {
  kind: string
  data: Record<string, unknown>
}

export interface AnchorCapabilities {
  terminal?: boolean
  framebuffer?: boolean
  tiles?: boolean
  saveState?: boolean
  deterministicSeed?: boolean
  questEvents?: boolean
  locidReverseLookup?: boolean
  networkAllowed?: boolean
}

export interface AnchorMeta {
  id: AnchorId
  title: string
  version?: string
  description?: string
  capabilities?: AnchorCapabilities
}

export interface QuantiseOptions {
  cellSize?: number
  layerBandBase?: number
  clampToBounds?: boolean
}

export interface AnchorTransform {
  toLocId(coord: AnchorCoord, opts?: QuantiseOptions): AnchorLocId
  toCoord(locId: AnchorLocId): AnchorCoord | null
}

export interface AnchorInstance {
  instanceId: string
  anchorId: AnchorId
  createdAt: string
  updatedAt: string
  meta?: Record<string, unknown>
}

export interface AnchorRegistry {
  listAnchors(): AnchorMeta[]
  getAnchor(id: AnchorId): AnchorMeta | null
  registerAnchor(meta: AnchorMeta): void
}

export interface InputEvent {
  ts: number
  type: "key" | "mouse" | "gamepad" | "touch"
  data: Record<string, unknown>
}

export interface RenderFrame {
  ts: number
  terminal?: {
    width: number
    height: number
    lines?: string[]
    grid?: string[]
  }
  framebuffer?: {
    width: number
    height: number
    ref: string
    format: "RGBA8888" | "RGB565" | "INDEXED"
  }
  overlays?: Array<{
    locId?: AnchorLocId
    label?: string
    icon?: string
    data?: Record<string, unknown>
  }>
}

export interface SaveStateRef {
  ref: string
  sizeBytes?: number
  hash?: string
  createdAt: string
}

export interface AnchorEvent {
  ts: number
  anchorId: AnchorId
  instanceId: string
  type:
    | "MOVE"
    | "ENTER_CELL"
    | "EXIT_CELL"
    | "PICKUP"
    | "DROP"
    | "DIALOGUE"
    | "QUEST_TRIGGER"
    | "CUSTOM"
  locId?: AnchorLocId
  coord?: AnchorCoord
  data?: Record<string, unknown>
}

export interface AnchorRuntime {
  meta(): Promise<AnchorMeta>
  transform(): Promise<AnchorTransform>

  createInstance(params?: {
    seed?: string
    profileId?: string
    space?: SpaceId
    initialLocId?: AnchorLocId
  }): Promise<AnchorInstance>

  destroyInstance(instanceId: string): Promise<void>

  input(instanceId: string, event: InputEvent): Promise<void>
  tick(instanceId: string, dtMs: number): Promise<void>

  render(instanceId: string): Promise<RenderFrame>

  saveState?(instanceId: string): Promise<SaveStateRef>
  loadState?(instanceId: string, state: SaveStateRef): Promise<void>
  pollEvents?(instanceId: string, sinceTs: number): Promise<AnchorEvent[]>
}
