/**
 * Viewport Manager for v1.0.7.0 Grid Runtime
 * 
 * Manages viewport state and tile visibility calculations for the 80×30 grid.
 * Handles centering, visible range, and sprite z-ordering.
 * 
 * Coordinate System:
 * - Columns: AA-DC (0-79)
 * - Rows: 10-39 (with offset)
 * - Layers: L300-L305 (SUR surface band)
 * 
 * Standard viewports:
 * - 80×30 (full terminal)
 * - 40×15 (mini map)
 * 
 * @author uDOS Development Team
 * @version 1.0.7.0
 */

// =============================================================================
// Types
// =============================================================================

export interface GridPosition {
  layer: number;    // L300-L305
  col: number;      // 0-79 (AA-DC)
  row: number;      // 10-39
}

export interface CellAddress {
  layer: number;
  cell: string;     // e.g., "AA10", "BK25"
}

export interface ViewportSize {
  width: number;    // Columns (default: 80)
  height: number;   // Rows (default: 30)
}

export interface ViewportState {
  center: GridPosition;
  size: ViewportSize;
  visibleTiles: CellAddress[];
  bounds: {
    minCol: number;
    maxCol: number;
    minRow: number;
    maxRow: number;
  };
}

export interface Sprite {
  id: string;
  position: GridPosition;
  character: string;
  color?: string;
  zIndex: number;   // Higher = rendered on top
  kind: 'player' | 'npc' | 'object' | 'marker';
}

export interface Tile {
  address: CellAddress;
  terrain: string;
  objects: any[];
  sprites: Sprite[];
}

// =============================================================================
// Constants
// =============================================================================

export const GRID_COLS = 80;      // AA-DC
export const GRID_ROWS = 30;      // 10-39 (offset)
export const ROW_OFFSET = 10;     // First row is 10

export const STANDARD_VIEWPORT: ViewportSize = { width: 80, height: 30 };
export const MINI_VIEWPORT: ViewportSize = { width: 40, height: 15 };

export const LAYER_MIN = 300;     // L300 (base surface)
export const LAYER_MAX = 305;     // L305 (highest precision)

// =============================================================================
// Coordinate Conversion
// =============================================================================

/**
 * Convert column index (0-79) to cell format (AA-DC)
 */
export function colIndexToCell(col: number): string {
  if (col < 0 || col >= GRID_COLS) {
    throw new Error(`Column index out of range: ${col} (must be 0-79)`);
  }
  
  // AA=0, AB=1, ... AZ=25, BA=26, ... DC=79
  // Formula: first = floor(col / 26), second = col % 26
  // But DC is special: col 79 → first=3, second=1 would give "DB"
  // DC is actually at first=2, second=28, but that's invalid
  // Correct: We need first letter A-D (0-3 * 26 = 0, 26, 52, 78)
  //          DC = D(3)*26 + C(2) = 78+2 = 80, but we're 0-indexed!
  // Actually: AA-AZ = 0-25, BA-BZ = 26-51, CA-CZ = 52-77, DA-DC = 78-79
  
  const first = Math.floor(col / 26);
  const second = col % 26;
  
  // Handle edge case: col 79 (DC) = D(3) + C(2)
  // But 79 / 26 = 3.03, floor = 3, 79 % 26 = 1 → gives "DB"
  // We need special handling for last column
  if (col === 79) {
    return 'DC';  // Special case
  }
  
  return String.fromCharCode(65 + first) + String.fromCharCode(65 + second);
}

/**
 * Convert cell format (AA-DC) to column index (0-79)
 */
export function cellToColIndex(cell: string): number {
  if (cell.length < 2) {
    throw new Error(`Invalid cell format: ${cell}`);
  }
  
  // Handle special case DC = 79
  if (cell === 'DC') {
    return 79;
  }
  
  const first = cell.charCodeAt(0) - 65;
  const second = cell.charCodeAt(1) - 65;
  
  const col = first * 26 + second;
  
  if (col < 0 || col > 79) {  // Changed >= to > to allow 79
    throw new Error(`Cell converts to invalid column: ${cell} → ${col}`);
  }
  
  return col;
}

/**
 * Parse cell address (e.g., "AA10") to position
 */
export function parseCellAddress(cell: string): { col: number; row: number } {
  const match = cell.match(/^([A-Z]{2})(\d{2})$/);
  if (!match) {
    throw new Error(`Invalid cell address format: ${cell}`);
  }
  
  const col = cellToColIndex(match[1]);
  const row = parseInt(match[2], 10);
  
  if (row < ROW_OFFSET || row >= ROW_OFFSET + GRID_ROWS) {
    throw new Error(`Row out of range: ${row} (must be ${ROW_OFFSET}-${ROW_OFFSET + GRID_ROWS - 1})`);
  }
  
  return { col, row };
}

/**
 * Format position to cell address (e.g., {col: 0, row: 10} → "AA10")
 */
export function formatCellAddress(col: number, row: number): string {
  const colStr = colIndexToCell(col);
  return `${colStr}${row.toString().padStart(2, '0')}`;
}

/**
 * Format full location ID (e.g., L300-AA10)
 */
export function formatLocationId(layer: number, col: number, row: number): string {
  const cell = formatCellAddress(col, row);
  return `L${layer}-${cell}`;
}

// =============================================================================
// Viewport Manager
// =============================================================================

export class ViewportManager {
  private state: ViewportState;
  
  constructor(
    center: GridPosition = { layer: 300, col: 40, row: 20 },
    size: ViewportSize = STANDARD_VIEWPORT
  ) {
    this.state = {
      center,
      size,
      visibleTiles: [],
      bounds: { minCol: 0, maxCol: 0, minRow: 0, maxRow: 0 }
    };
    
    this.updateVisibleTiles();
  }
  
  // ---------------------------------------------------------------------------
  // State Accessors
  // ---------------------------------------------------------------------------
  
  getState(): ViewportState {
    return { ...this.state };
  }
  
  getCenter(): GridPosition {
    return { ...this.state.center };
  }
  
  getSize(): ViewportSize {
    return { ...this.state.size };
  }
  
  getVisibleTiles(): CellAddress[] {
    return [...this.state.visibleTiles];
  }
  
  // ---------------------------------------------------------------------------
  // Viewport Manipulation
  // ---------------------------------------------------------------------------
  
  /**
   * Set viewport center position
   */
  setCenter(position: GridPosition): void {
    this.state.center = { ...position };
    this.updateVisibleTiles();
  }
  
  /**
   * Move viewport by delta
   */
  moveBy(deltaCol: number, deltaRow: number): void {
    const newCol = Math.max(0, Math.min(GRID_COLS - 1, this.state.center.col + deltaCol));
    const newRow = Math.max(ROW_OFFSET, Math.min(ROW_OFFSET + GRID_ROWS - 1, this.state.center.row + deltaRow));
    
    this.state.center.col = newCol;
    this.state.center.row = newRow;
    
    this.updateVisibleTiles();
  }
  
  /**
   * Set viewport size
   */
  setSize(size: ViewportSize): void {
    this.state.size = { ...size };
    this.updateVisibleTiles();
  }
  
  /**
   * Change layer
   */
  setLayer(layer: number): void {
    if (layer < LAYER_MIN || layer > LAYER_MAX) {
      throw new Error(`Layer out of range: ${layer} (must be ${LAYER_MIN}-${LAYER_MAX})`);
    }
    
    this.state.center.layer = layer;
    this.updateVisibleTiles();
  }
  
  // ---------------------------------------------------------------------------
  // Visibility Calculation
  // ---------------------------------------------------------------------------
  
  /**
   * Calculate visible tiles based on current viewport state
   */
  private updateVisibleTiles(): void {
    const halfWidth = Math.floor(this.state.size.width / 2);
    const halfHeight = Math.floor(this.state.size.height / 2);
    
    const minCol = Math.max(0, this.state.center.col - halfWidth);
    const maxCol = Math.min(GRID_COLS - 1, this.state.center.col + halfWidth);
    const minRow = Math.max(ROW_OFFSET, this.state.center.row - halfHeight);
    const maxRow = Math.min(ROW_OFFSET + GRID_ROWS - 1, this.state.center.row + halfHeight);
    
    this.state.bounds = { minCol, maxCol, minRow, maxRow };
    
    // Generate list of visible cells
    const tiles: CellAddress[] = [];
    
    for (let row = minRow; row <= maxRow; row++) {
      for (let col = minCol; col <= maxCol; col++) {
        const cell = formatCellAddress(col, row);
        tiles.push({
          layer: this.state.center.layer,
          cell
        });
      }
    }
    
    this.state.visibleTiles = tiles;
  }
  
  /**
   * Check if a position is currently visible
   */
  isVisible(position: GridPosition): boolean {
    if (position.layer !== this.state.center.layer) {
      return false;
    }
    
    const { minCol, maxCol, minRow, maxRow } = this.state.bounds;
    
    return (
      position.col >= minCol &&
      position.col <= maxCol &&
      position.row >= minRow &&
      position.row <= maxRow
    );
  }
  
  /**
   * Get relative screen coordinates for a position
   * Returns null if not visible
   */
  getScreenCoordinates(position: GridPosition): { x: number; y: number } | null {
    if (!this.isVisible(position)) {
      return null;
    }
    
    const halfWidth = Math.floor(this.state.size.width / 2);
    const halfHeight = Math.floor(this.state.size.height / 2);
    
    const x = position.col - this.state.center.col + halfWidth;
    const y = position.row - this.state.center.row + halfHeight;
    
    return { x, y };
  }
  
  // ---------------------------------------------------------------------------
  // Sprite Management
  // ---------------------------------------------------------------------------
  
  /**
   * Sort sprites by z-index (ascending)
   * Use for rendering: lower z-index renders first
   */
  sortSprites(sprites: Sprite[]): Sprite[] {
    return [...sprites].sort((a, b) => a.zIndex - b.zIndex);
  }
  
  /**
   * Filter sprites to only visible ones
   */
  getVisibleSprites(sprites: Sprite[]): Sprite[] {
    return sprites.filter(sprite => this.isVisible(sprite.position));
  }
  
  /**
   * Get sprites at specific position (for collision detection)
   */
  getSpritesAtPosition(sprites: Sprite[], position: GridPosition): Sprite[] {
    return sprites.filter(sprite =>
      sprite.position.layer === position.layer &&
      sprite.position.col === position.col &&
      sprite.position.row === position.row
    );
  }
}

// =============================================================================
// Exports
// =============================================================================

export default ViewportManager;
