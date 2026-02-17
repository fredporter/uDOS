export type GridMode =
  | "dashboard"
  | "calendar"
  | "schedule"
  | "table"
  | "map"
  | "workflow";

export interface GridCanvasSpec {
  width: 80;
  height: 30;
  title?: string;
  theme?: string;
  mode?: GridMode;
  ts?: string;
}

export interface RenderResult {
  header: Record<string, unknown>;
  lines: string[];
  rawText: string;
}

export interface GridLocationRef {
  locId?: string;
  placeRef?: string;
  location?: string;
  layer?: string;
  z?: number;
}

export interface TaskItem extends GridLocationRef {
  id?: string;
  status: string;
  text: string;
  due?: string;
  owner?: string;
}

export interface ScheduleItem extends GridLocationRef {
  id?: string;
  start?: string;
  end?: string;
  time?: string;
  item?: string;
  title?: string;
  channel?: string;
}

export interface WorkflowStep extends GridLocationRef {
  id: string;
  title: string;
  state: "todo" | "in_progress" | "blocked" | "done";
  owner?: string;
  dependsOn?: string[];
}

export interface LocIdOverlay {
  locId: string;
  icon: string; // T|N|E|!|*
  label?: string;
  z?: number;
}

// Map layer stack types
export type MapLayerKind = "terrain" | "objects" | "overlays" | "workflow";

export interface TerrainCell {
  locId: string;
  glyph: string; // single char: . = ~ ^ # etc.
  label?: string;
  z?: number;
}

export interface MapObject {
  locId: string;
  sprite: string; // 1-2 char symbol: @ P E $ etc.
  label?: string;
  z?: number;
}

export interface WorkflowMarker {
  locId: string;
  stepId: string;
  state: "todo" | "in_progress" | "blocked" | "done";
  title?: string;
  z?: number;
}

export interface MapLayerSpec {
  kind: MapLayerKind;
  label?: string;
  visible?: boolean; // default true
}

export interface MapInput {
  focusLocId?: string;
  overlays?: LocIdOverlay[];
  terrain?: TerrainCell[];
  objects?: MapObject[];
  workflowMarkers?: WorkflowMarker[];
  layers?: MapLayerSpec[]; // ordered layer stack (bottom → top)
  viewport?: MapViewportOptions;
}

export interface MapViewportOptions {
  zRange?: number; // Nearby z layers included around focus plane (default: 1)
}

export interface MinimapCell {
  type: "empty" | "occupied" | "selected" | "tagged";
  content?: string;
  overlay?: LocIdOverlay;
}

export interface MinimapOptions {
  showLabels?: boolean;
  focusCell?: { x: number; y: number };
}

export type BorderStyle = "single" | "none";

export interface TextOptions {
  wrap?: boolean;
}

export interface TableColumn {
  key: string;
  title: string;
  width?: number;
}

export interface TableOptions {
  header?: boolean;
  rowSep?: boolean;
}

export interface CalendarInput {
  events?: ScheduleItem[];
  tasks?: TaskItem[];
}

export interface ScheduleInput {
  events?: ScheduleItem[];
  scheduleItems?: ScheduleItem[];
  filters?: Record<string, string>;
}

export interface DashboardInput {
  missions?: Array<{ status?: string; title?: string }>;
  stats?: Record<string, string | number | boolean>;
  apiQuota?: { used?: number; limit?: number };
  nodeState?: { status?: string; uptime?: string };
  logs?: Array<{ time?: string; level?: string; message?: string }>;
  tasks?: TaskItem[];
  scheduleItems?: ScheduleItem[];
  workflowSteps?: WorkflowStep[];
}

export interface WorkflowInput {
  tasks?: TaskItem[];
  scheduleItems?: ScheduleItem[];
  workflowSteps?: WorkflowStep[];
}
