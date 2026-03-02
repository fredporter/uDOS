/**
 * Layer Types and Utilities
 * Extends base types from index.ts with layer-specific helpers
 */

import type { Tile, Layer } from './index';

export type { Tile, Layer };

/**
 * Create an empty tile at given coordinates
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
 * Create a new layer
 */
export function createLayer(name = "Layer"): Layer {
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
 * Map document container
 */
export interface MapDocument {
  id: string;
  name: string;
  layers: Layer[];
  width: number;
  height: number;
  metadata: Record<string, any>;
}

/**
 * Create a new map document
 */
export function createMapDocument(name = "Untitled Map"): MapDocument {
  return {
    id: `map-${Math.random().toString(36).substr(2, 9)}`,
    name,
    layers: [createLayer("Background")],
    width: 80,
    height: 24,
    metadata: {},
  };
}
