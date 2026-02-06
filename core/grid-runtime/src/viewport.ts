/**
 * Viewport System
 * 
 * Manages viewport composition, layering, and rendering bounds
 */

import { Viewport, RenderOptions } from "./index.js";
import { Cell, CanonicalAddress, getEffectiveLayer, formatCell } from "./address.js";
import {
  VIEWPORT_STANDARD,
  VIEWPORT_MINI,
  GRID_CELL_COLS,
  GRID_CELL_ROWS,
  LAYER_BANDS,
  TILE_WIDTH,
  TILE_HEIGHT,
  GraphicsMode,
  SEXTANT_CHARS,
  QUADRANT_CHARS,
  SHADE_CHARS,
  ASCII_CHARS
} from "./geometry.js";

/**
 * Render state: what layers are visible at this viewport
 * 
 * SUR (L300–L305)  — surface layer (buildings, terrain, sprites)
 * UDN (L299–L294)  — underground (caves, roots)
 * SUB (L293+)       — substrate (deep earth, sky reflection)
 */
export interface ViewportState {
  center: Cell;                    // center cell of viewport
  viewport: Viewport;              // dimensions (80×30 or 40×15)
  visibleLayers: CanonicalAddress[]; // which depth layers render
  renderMode: GraphicsMode;        // sextant, quadrant, shade, or ASCII
}

/**
 * Render layer: single pass of tile data
 */
export interface RenderLayer {
  baseLayer: number;               // L300, L299, etc.
  tiles: Map<string, string>;      // cell_id → character
  colors: Map<string, number>;     // cell_id → palette color
  priorities: Map<string, number>; // cell_id → z-order (0=back, 1000=front)
}

/**
 * Viewport Manager
 * 
 * Handles viewport composition, visible tile determination, fallback rendering
 */
export class ViewportManager {
  private state: ViewportState;
  private renderLayers: RenderLayer[] = [];

  constructor(center: Cell, viewport: Viewport = VIEWPORT_STANDARD) {
    this.state = {
      center,
      viewport,
      visibleLayers: [], // will be populated by setViewLayers()
      renderMode: GraphicsMode.Sextant
    };
  }

  /**
   * Set which layers are visible in this viewport
   * 
   * Typical: SUR (primary) + UDN (caves) + maybe SUB
   */
  setViewLayers(...layers: number[]): void {
    this.state.visibleLayers = layers.map((layer) => ({
      baseLayer: layer,
      depth: 0,
      cell: this.state.center,
      band: layer >= 300 && layer <= 305 ? "SUR" : layer >= 294 && layer <= 299 ? "UDN" : "SUB"
    }));

    // Rebuild render stack
    this.rebuildRenderStack();
  }

  /**
   * Get bounds (cell coords that are visible in viewport)
   */
  getViewBounds(): { minCol: number; maxCol: number; minRow: number; maxRow: number } {
    const halfCols = Math.floor(this.state.viewport.cols / 2);
    const halfRows = Math.floor(this.state.viewport.rows / 2);

    return {
      minCol: Math.max(0, this.state.center.col - halfCols),
      maxCol: Math.min(GRID_CELL_COLS, this.state.center.col + halfCols),
      minRow: Math.max(0, this.state.center.row - halfRows),
      maxRow: Math.min(GRID_CELL_ROWS, this.state.center.row + halfRows)
    };
  }

  /**
   * Determine which tiles are visible (within viewport bounds)
   */
  getVisibleTiles(): Map<string, CanonicalAddress> {
    const visible = new Map<string, CanonicalAddress>();
    const bounds = this.getViewBounds();

    for (const addr of this.state.visibleLayers) {
      for (let col = bounds.minCol; col <= bounds.maxCol; col++) {
        for (let row = bounds.minRow; row <= bounds.maxRow; row++) {
          const cellId = formatCell({ col, row });
          visible.set(`L${addr.baseLayer}-${cellId}`, addr);
        }
      }
    }

    return visible;
  }

  /**
   * Switch render mode (sextant → quadrant → shade → ASCII)
   */
  setRenderMode(mode: GraphicsMode): void {
    this.state.renderMode = mode;
  }

  /**
   * Render a character with automatic fallback
   * 
   * Input: preferred sextant character (16 chars)
   * Output: character in current render mode, or fallback
   */
  renderCharacter(sextantIndex: number): string {
    const index = sextantIndex % 16; // 0–15

    switch (this.state.renderMode) {
      case GraphicsMode.Sextant:
        const sextantChar = SEXTANT_CHARS[index];
        if (sextantChar.length === 1) {
          return sextantChar;
        }
        return ASCII_CHARS[Math.floor(index / 4) % ASCII_CHARS.length];
      case GraphicsMode.Quadrant:
        // Map sextant → quadrant (every other sextant segment)
        return QUADRANT_CHARS[Math.floor(index / 2) % 16];
      case GraphicsMode.Shade:
        // Map to shade levels (0–3)
        return SHADE_CHARS[Math.floor(index / 4) % 4];
      case GraphicsMode.ASCII:
        // Map to ASCII block chars
        return ASCII_CHARS[Math.floor(index / 8) % 4];
      default:
        return "?";
    }
  }

  /**
   * Compose viewport image from render stack
   * 
   * Returns: 2D array of characters (viewport.rows × viewport.cols)
   */
  compose(): string[][] {
    const { cols, rows } = this.state.viewport;
    const image: string[][] = Array(rows)
      .fill(null)
      .map(() => Array(cols).fill(" "));

    const bounds = this.getViewBounds();
    const viewCenterScreenCol = Math.floor(cols / 2);
    const viewCenterScreenRow = Math.floor(rows / 2);

    // Render each visible layer (back to front)
    for (const layer of this.renderLayers) {
      for (const [cellId, char] of layer.tiles.entries()) {
        const [, colStr, rowStr] = cellId.match(/^(\w+)(\d+)$/) || [];
        if (!colStr || !rowStr) continue;

        const col = parseInt(colStr, 36);
        const row = parseInt(rowStr, 36);

        // Project cell to screen coords
        const screenCol = viewCenterScreenCol + (col - this.state.center.col);
        const screenRow = viewCenterScreenRow + (row - this.state.center.row);

        // Clamp to viewport
        if (screenCol >= 0 && screenCol < cols && screenRow >= 0 && screenRow < rows) {
          image[screenRow][screenCol] = this.renderCharacter(char.charCodeAt(0));
        }
      }
    }

    return image;
  }

  /**
   * Render viewport as string (for display/logging)
   */
  toString(): string {
    const image = this.compose();
    return image.map((row) => row.join("")).join("\n");
  }

  private rebuildRenderStack(): void {
    this.renderLayers = this.state.visibleLayers.map((addr) => ({
      baseLayer: addr.baseLayer,
      tiles: new Map(),
      colors: new Map(),
      priorities: new Map()
    }));
  }
}

/**
 * Sky View: compute sky from location + time
 * 
 * Placeholder for future implementation
 */
export interface SkyTile {
  character: string;
  color: number;
}

export function computeSkyView(
  latitude: number,
  longitude: number,
  time: Date
): SkyTile[][] {
  const rows = 16;
  const cols = 24;
  const tiles: SkyTile[][] = [];

  const hour = time.getHours();
  const isDay = hour >= 6 && hour < 18;
  const isTwilight = (hour >= 5 && hour < 6) || (hour >= 18 && hour < 19);

  // Deterministic seed based on time + location
  const seed =
    Math.floor(time.getTime() / (1000 * 60 * 60)) +
    Math.round(latitude * 10) * 31 +
    Math.round(longitude * 10) * 37;

  const dayChar = '·';
  const nightChar = '.';
  const starChar = '*';

  const starThreshold = isTwilight ? 0.96 : 0.93;

  for (let r = 0; r < rows; r++) {
    const row: SkyTile[] = [];
    for (let c = 0; c < cols; c++) {
      let character = isDay ? dayChar : nightChar;
      let color = 0;

      if (!isDay) {
        const hash = Math.sin((r * 73856093 + c * 19349663 + seed * 83492791) * 0.000001);
        const value = hash - Math.floor(hash);
        if (value > starThreshold) {
          character = starChar;
        }
      }

      row.push({ character, color });
    }
    tiles.push(row);
  }

  return tiles;
}
