/**
 * Main Grid Runtime Module
 * 
 * Exports all grid runtime types, utilities, and rendering pipeline
 */

export * from "./geometry";
export * from "./address";
export * from "./renderer";
export * from "./viewport";

// Phase 3: Code Block Parser exports
export * from "./expression-evaluator";
export * from "./code-block-parser";
export * from "./markdown-extractor";

// Phase 4: Location + Sparse World
export * from "./location-manager";
export * from "./sparse-world";
export * from "./pathfinding";

// Type definitions for tiles and entities
export interface Tile {
  id: string;
  type: "object" | "sprite" | "marker";
  static: boolean;
  palette?: number[]; // 5-bit indices
}

export interface ObjectTile extends Tile {
  type: "object";
  solid?: boolean;
  state?: string;
  udn?: {
    depthMm: number; // 0..3000 for buried objects
  };
}

export interface SpriteTile extends Tile {
  type: "sprite";
  frames: number;
  currentFrame?: number;
  animationSpeed?: number;
  facing?: "N" | "E" | "S" | "W" | "NE" | "NW" | "SE" | "SW";
}

export interface MarkerTile extends Tile {
  type: "marker";
  visible?: boolean;
  name: string;
  tags?: string[];
}

// Viewport and rendering types
export interface Viewport {
  cols: number;
  rows: number;
  name: "standard" | "mini";
}

export interface RenderOptions {
  mode: "sextant" | "quadrant" | "shade" | "ascii";
  showTerrain: boolean;
  showSprites: boolean;
  showMarkers: boolean;
}

// Code block types for markdown integration
export interface TeletextBlock {
  type: "teletext";
  content: string; // raw sextant/ASCII grid
  variables?: Record<string, any>;
}

export interface GridBlock {
  type: "grid";
  definition: any; // YAML/JSON grid spec
  variables?: Record<string, any>;
}

export interface TilesBlock {
  type: "tiles";
  tiles: Tile[];
  manifest?: Record<string, any>;
}
