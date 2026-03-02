/**
 * Layer and Tile types for pixel/tile editor
 */

export interface Tile {
  id: string;
  x: number;
  y: number;
  char: string;
  fg: string; // foreground color
  bg: string; // background color
  bold: boolean;
  underline: boolean;
}

export interface Layer {
  id: string;
  name: string;
  tiles: Tile[];
  visible: boolean;
  opacity: number;
  zIndex: number;
}

/**
 * Create an empty tile
 */
export function createEmptyTile(x = 0, y = 0): Tile {
  return {
    id: `tile-${Math.random().toString(36).substr(2, 9)}`,
    x,
    y,
    char: " ",
    fg: "#ffffff",
    bg: "#000000",
    bold: false,
    underline: false,
  };
}

/**
 * Create an empty layer
 */
export function createEmptyLayer(name = "Layer"): Layer {
  return {
    id: `layer-${Math.random().toString(36).substr(2, 9)}`,
    name,
    tiles: [],
    visible: true,
    opacity: 1,
    zIndex: 0,
  };
}

/**
 * Mission types
 */
export interface MissionData {
  id: string;
  title: string;
  description: string;
  status: "pending" | "in-progress" | "completed" | "failed";
  priority: "low" | "normal" | "high" | "critical";
  dueDate?: string;
  tags: string[];
}

/**
 * Contribution types
 */
export interface ContributionRow {
  id: string;
  title: string;
  author: string;
  status: string;
  createdAt: string;
}

/**
 * Spatial types
 */
export interface AnchorRow {
  id: string;
  name: string;
  location: string;
  type: string;
}

export interface PlaceRow {
  id: string;
  name: string;
  description: string;
  tags: string[];
}

export interface FileTagRow {
  id: string;
  file: string;
  tags: string[];
}
