/**
 * Tile Compositor - Combine objects/sprites into rendered pixel grids
 * 
 * Takes tile content (objects, sprites, markers) and composites them into
 * sextant pixel grids for rendering. Handles z-ordering, layer composition,
 * and character selection.
 * 
 * @module grid-runtime/tile-compositor
 */

import {
  PixelGrid,
  createEmptyGrid,
  createFullGrid,
  mergeGrids,
  pixelGridToSextant,
  RenderQuality,
  renderPixelGrid,
} from './sextant-renderer';
import { TileContent, TileObject, TileSprite } from './location-types';

/**
 * Render options for tile composition
 */
export interface CompositorOptions {
  /** Rendering quality (default: sextant) */
  quality?: RenderQuality;
  
  /** Whether to render background terrain */
  showTerrain?: boolean;
  
  /** Default terrain character if none specified */
  defaultTerrain?: string;
}

/**
 * Rendered tile with character and styling
 */
export interface RenderedTile {
  /** Display character (emoji or Unicode) */
  char: string;
  
  /** Foreground color (hex or named) */
  fg?: string;
  
  /** Background color (hex or named) */
  bg?: string;
  
  /** Z-index of topmost visible element */
  z: number;
}

/**
 * Sort tile elements by z-index (ascending)
 * Lower z-index renders first (background), higher renders last (foreground)
 */
function sortByZIndex<T extends { z?: number }>(elements: T[]): T[] {
  return [...elements].sort((a, b) => (a.z || 0) - (b.z || 0));
}

/**
 * Convert character to pixel grid (simplified - assumes single character)
 * In full implementation, would parse emoji/Unicode to actual pixel patterns
 */
function charToPixelGrid(char: string): PixelGrid {
  // For now, treat any character as "full" (all pixels on)
  // TODO: Implement actual character-to-pixel mapping
  if (!char || char === ' ') {
    return createEmptyGrid();
  }
  
  // Simple heuristic: light chars = partial fill, dense chars = full
  const lightChars = ['.', '·', '°', '˙', '•'];
  const mediumChars = ['░', '▒', ':', '~', '-', '_'];
  
  if (lightChars.includes(char)) {
    return {
      topLeft: true,
      topRight: false,
      middleLeft: false,
      middleRight: true,
      bottomLeft: false,
      bottomRight: true,
    };
  }
  
  if (mediumChars.includes(char)) {
    return {
      topLeft: true,
      topRight: true,
      middleLeft: false,
      middleRight: false,
      bottomLeft: true,
      bottomRight: true,
    };
  }
  
  // Most characters (emoji, letters, symbols) = full grid
  return createFullGrid();
}

/**
 * Composite objects into a single pixel grid
 * @param objects - Array of objects to composite (z-sorted)
 * @returns Merged pixel grid
 */
function compositeObjects(objects: TileObject[]): PixelGrid {
  if (objects.length === 0) {
    return createEmptyGrid();
  }
  
  let grid = createEmptyGrid();
  
  for (const obj of sortByZIndex(objects)) {
    const objGrid = charToPixelGrid(obj.char);
    grid = mergeGrids(grid, objGrid);
  }
  
  return grid;
}

/**
 * Get topmost sprite (highest z-index)
 * Sprites override objects - always visible on top
 */
function getTopmostSprite(sprites: TileSprite[]): TileSprite | null {
  if (sprites.length === 0) return null;
  
  const sorted = sortByZIndex(sprites);
  return sorted[sorted.length - 1]; // Highest z-index
}

/**
 * Get topmost object for styling (highest z-index)
 */
function getTopmostObject(objects: TileObject[]): TileObject | null {
  if (objects.length === 0) return null;
  
  const sorted = sortByZIndex(objects);
  return sorted[sorted.length - 1];
}

/**
 * Composite tile content into a rendered character
 * 
 * Rendering order:
 * 1. Objects (z-sorted, composited into pixel grid)
 * 2. Sprites (topmost sprite always visible)
 * 3. Markers (invisible - metadata only)
 * 
 * @param content - Tile content with objects/sprites/markers
 * @param options - Compositor options
 * @returns Rendered tile with character and styling
 */
export function compositeTile(
  content: TileContent | undefined,
  options: CompositorOptions = {}
): RenderedTile {
  const quality = options.quality || RenderQuality.SEXTANT;
  const showTerrain = options.showTerrain || false;
  const defaultTerrain = options.defaultTerrain || ' ';
  
  // Empty tile
  if (!content || (!content.objects?.length && !content.sprites?.length)) {
    return {
      char: showTerrain ? defaultTerrain : ' ',
      z: 0,
    };
  }
  
  const objects = content.objects || [];
  const sprites = content.sprites || [];
  
  // Check for sprite override
  const topmostSprite = getTopmostSprite(sprites);
  if (topmostSprite) {
    // Sprite always renders as its character (no sextant composition)
    return {
      char: topmostSprite.char,
      fg: topmostSprite.fg,
      bg: topmostSprite.bg,
      z: topmostSprite.z || 1,
    };
  }
  
  // No sprites - composite objects into sextant grid
  const pixelGrid = compositeObjects(objects);
  const char = renderPixelGrid(pixelGrid, quality);
  
  // Use topmost object for styling
  const topmostObj = getTopmostObject(objects);
  
  return {
    char,
    fg: topmostObj?.fg,
    bg: topmostObj?.bg,
    z: topmostObj?.z || 0,
  };
}

/**
 * Composite multiple tiles into a 2D grid
 * @param tiles - Map of cell addresses to tile content
 * @param width - Grid width (default: 80)
 * @param height - Grid height (default: 30)
 * @param options - Compositor options
 * @returns 2D array of rendered tiles
 */
export function compositeGrid(
  tiles: Record<string, TileContent>,
  width: number = 80,
  height: number = 30,
  options: CompositorOptions = {}
): RenderedTile[][] {
  const grid: RenderedTile[][] = [];
  const emptyChar = options.showTerrain ? options.defaultTerrain || ' ' : ' ';
  
  // Initialize empty grid
  for (let row = 0; row < height; row++) {
    const rowTiles: RenderedTile[] = [];
    for (let col = 0; col < width; col++) {
      rowTiles.push({ char: emptyChar, z: 0 });
    }
    grid.push(rowTiles);
  }
  
  // Composite each tile
  for (const [cellAddr, content] of Object.entries(tiles)) {
    // Parse cell address (e.g., "AA10" → col=0, row=10)
    const colStr = cellAddr.slice(0, 2);
    const rowStr = cellAddr.slice(2);
    
    const col = (colStr.charCodeAt(0) - 65) * 26 + (colStr.charCodeAt(1) - 65);
    const row = parseInt(rowStr, 10);
    
    // Validate row before clamping (must be within grid height)
    if (isNaN(row) || row < 0 || row >= height) {
      continue;
    }

    const safeCol = Math.min(Math.max(col, 0), width - 1);
    const safeRow = Math.min(Math.max(row, 0), height - 1);
    grid[safeRow][safeCol] = compositeTile(content, options);
  }
  
  return grid;
}

/**
 * Render grid to string (for display)
 * @param grid - 2D array of rendered tiles
 * @returns Multi-line string representation
 */
export function renderGridToString(grid: RenderedTile[][]): string {
  return grid.map(row => row.map(tile => tile.char).join('')).join('\n');
}

/**
 * Render grid with ANSI colors (for terminal display)
 * @param grid - 2D array of rendered tiles
 * @returns Multi-line string with ANSI color codes
 */
export function renderGridWithColors(grid: RenderedTile[][]): string {
  const lines: string[] = [];
  
  for (const row of grid) {
    let line = '';
    for (const tile of row) {
      let char = tile.char;
      
      // Apply ANSI color codes if specified
      if (tile.fg || tile.bg) {
        const fg = tile.fg ? colorToANSI(tile.fg) : '';
        const bg = tile.bg ? colorToANSI(tile.bg, true) : '';
        char = `${fg}${bg}${char}\x1b[0m`; // Reset after each character
      }
      
      line += char;
    }
    lines.push(line);
  }
  
  return lines.join('\n');
}

/**
 * Convert color name/hex to ANSI code
 * @param color - Color name or hex (#RRGGBB)
 * @param background - Whether to apply to background (default: foreground)
 * @returns ANSI escape sequence
 */
function colorToANSI(color: string, background: boolean = false): string {
  const prefix = background ? '\x1b[4' : '\x1b[3';
  
  // Named colors
  const namedColors: Record<string, string> = {
    black: '0',
    red: '1',
    green: '2',
    yellow: '3',
    blue: '4',
    magenta: '5',
    cyan: '6',
    white: '7',
  };
  
  if (namedColors[color.toLowerCase()]) {
    return `${prefix}${namedColors[color.toLowerCase()]}m`;
  }
  
  // Hex colors (simplified - no true color support)
  if (color.startsWith('#')) {
    // For now, map to nearest named color
    return `${prefix}7m`; // Default to white
  }
  
  return ''; // Unknown color
}

/**
 * Tile compositor class for managing rendering state
 */
export class TileCompositor {
  private options: CompositorOptions;
  
  constructor(options: CompositorOptions = {}) {
    this.options = {
      quality: RenderQuality.SEXTANT,
      showTerrain: false,
      defaultTerrain: ' ',
      ...options,
    };
  }
  
  /**
   * Set rendering quality
   */
  setQuality(quality: RenderQuality): void {
    this.options.quality = quality;
  }
  
  /**
   * Composite single tile
   */
  compositeTile(content: TileContent | undefined): RenderedTile {
    return compositeTile(content, this.options);
  }
  
  /**
   * Composite full grid
   */
  compositeGrid(
    tiles: Record<string, TileContent>,
    width?: number,
    height?: number
  ): RenderedTile[][] {
    return compositeGrid(tiles, width, height, this.options);
  }
  
  /**
   * Render grid to string
   */
  render(
    tiles: Record<string, TileContent>,
    width?: number,
    height?: number,
    withColors: boolean = false
  ): string {
    const grid = this.compositeGrid(tiles, width, height);
    return withColors ? renderGridWithColors(grid) : renderGridToString(grid);
  }
}
