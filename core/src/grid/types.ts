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

export type BorderStyle = "single" | "none";

export interface TextOptions {
  align?: "left" | "centre" | "right";
  wrap?: boolean;
  ellipsis?: boolean;
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
