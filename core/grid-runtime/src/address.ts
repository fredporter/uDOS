/**
 * Grid Address Model
 * 
 * Handles cell addressing (AA10), layer bands, and canonical address normalization
 */

import { GRID_CELL_COLS, GRID_CELL_ROWS, GRID_CELL_ROW_OFFSET, LAYER_BANDS } from "./geometry.js";

/**
 * Cell Format: AA10 (2 letters + 2 digits)
 * - Columns: AA (0)–DC (79), strictly paired uppercase
 * - Rows: 10–39 (internally 0–29, offset by 10)
 */
export interface Cell {
  col: number; // 0–79
  row: number; // 0–29 (stored), displayed as 10–39
}

/**
 * Layer Band: SUR, UDN, or SUB
 */
export type LayerBand = "SUR" | "UDN" | "SUB";

/**
 * Canonical Address: L{EffectiveLayer}-{Cell}
 * where EffectiveLayer = BaseLayer + Depth
 */
export interface CanonicalAddress {
  baseLayer: number;
  depth: number;  // number of -Cell segments
  cell: Cell;
  band: LayerBand;
}

/**
 * Parse cell string "AA10" → { col: 0, row: 0 }
 */
export function parseCell(cellStr: string): Cell {
  if (cellStr.length !== 4) {
    throw new Error(`Invalid cell format: "${cellStr}" (expected AA10)`);
  }

  const colLetters = cellStr.slice(0, 2);
  const rowDigits = cellStr.slice(2, 4);

  // Parse column (AA=0, AB=1, ..., DC=79)
  const col1 = colLetters.charCodeAt(0) - "A".charCodeAt(0); // 0–25
  const col2 = colLetters.charCodeAt(1) - "A".charCodeAt(0); // 0–25
  const col = col1 * 26 + col2;

  if (col < 0 || col >= GRID_CELL_COLS) {
    throw new Error(`Column out of range: "${colLetters}" (0–79)`);
  }

  // Parse row (10–39)
  const row = parseInt(rowDigits, 10) - GRID_CELL_ROW_OFFSET;
  if (row < 0 || row >= GRID_CELL_ROWS) {
    throw new Error(`Row out of range: ${rowDigits} (10–39)`);
  }

  return { col, row };
}

/**
 * Format cell { col: 0, row: 0 } → "AA10"
 */
export function formatCell(cell: Cell): string {
  const col1 = Math.floor(cell.col / 26);
  const col2 = cell.col % 26;
  const colLetters = String.fromCharCode("A".charCodeAt(0) + col1) +
                     String.fromCharCode("A".charCodeAt(0) + col2);

  const rowStr = String(cell.row + GRID_CELL_ROW_OFFSET).padStart(2, "0");
  return colLetters + rowStr;
}

/**
 * Determine layer band from layer number
 */
export function getLayerBand(layer: number): LayerBand {
  if (layer >= LAYER_BANDS.SUR.min && layer <= LAYER_BANDS.SUR.max) {
    return "SUR";
  }
  if (layer >= LAYER_BANDS.UDN.min && layer <= LAYER_BANDS.UDN.max) {
    return "UDN";
  }
  if (layer <= LAYER_BANDS.SUB.max) {
    return "SUB";
  }
  throw new Error(`Layer ${layer} out of valid ranges`);
}

/**
 * Validate layer for band
 */
export function validateLayerInBand(layer: number, band: LayerBand): boolean {
  const bandRange = LAYER_BANDS[band];
  if (band === "UDN") {
    // UDN is reversed: L299–L294 (decreasing)
    return layer >= bandRange.min && layer <= bandRange.max;
  }
  return layer >= bandRange.min && layer <= bandRange.max;
}

/**
 * Parse canonical address "L300-AA10" or fractal "L300-AA10-BA20-CC15"
 */
export function parseCanonicalAddress(addressStr: string): CanonicalAddress {
  const parts = addressStr.split("-");
  if (parts.length < 2) {
    throw new Error(`Invalid address format: "${addressStr}" (expected L###-AA##...)`);
  }

  // Parse base layer
  const baseLayerStr = parts[0];
  if (!baseLayerStr.startsWith("L")) {
    throw new Error(`Invalid layer format: "${baseLayerStr}" (expected L###)`);
  }

  const baseLayer = parseInt(baseLayerStr.slice(1), 10);
  const depth = parts.length - 2; // number of cells beyond first

  // Final cell is the last segment
  const finalCell = parseCell(parts[parts.length - 1]);
  const band = getLayerBand(baseLayer);

  return { baseLayer, depth, cell: finalCell, band };
}

/**
 * Format canonical address from parts
 */
export function formatCanonicalAddress(addr: CanonicalAddress): string {
  const layer = `L${addr.baseLayer}`;
  const cell = formatCell(addr.cell);
  return `${layer}-${cell}`;
}

/**
 * Compute effective layer: baseLayer + depth
 */
export function getEffectiveLayer(addr: CanonicalAddress): number {
  return addr.baseLayer + addr.depth;
}
