export type GridMode = "dashboard" | "calendar" | "schedule" | "table" | "map";

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

export interface LocIdOverlay {
  locId: string;
  icon: string; // T|N|E|!|*
  label?: string;
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
