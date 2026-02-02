/**
 * SparseWorld
 * Phase 4: Sparse tile allocation on 80×30 grids
 *
 * Responsibilities:
 * - Store tile placements keyed by canonical address
 * - Enforce footprints (1×1, 2×1) and occupancy rules
 * - Provide serialization/deserialization for persistence
 */

import { FOOTPRINT_STANDARD, GRID_CELL_COLS, GRID_CELL_ROWS } from "./geometry.js";
import { parseCanonicalAddress, formatCanonicalAddress } from "./address.js";

export type TileType = "object" | "sprite" | "marker";

export interface Footprint {
  width: number;
  height: number;
}

export interface TilePlacement {
  id: string;
  type: TileType;
  solid?: boolean;
  footprint?: Footprint;
  props?: Record<string, any>;
}

interface CellPlacement {
  canonical: string;
  tiles: TilePlacement[];
}

export class SparseWorld {
  private cells: Map<string, CellPlacement> = new Map();

  /**
   * Place a tile at a canonical location.
   * Enforces footprint collision and grid bounds.
   */
  public place(canonical: string, placement: TilePlacement): void {
    const addr = parseCanonicalAddress(canonical);
    this.assertInBounds(addr.cell.col, addr.cell.row);

    const footprint = placement.footprint || FOOTPRINT_STANDARD;
    const coveredCells = this.computeFootprintCells(canonical, footprint);

    // Collision check
    for (const cellId of coveredCells) {
      const existing = this.cells.get(cellId);
      if (existing && existing.tiles.some((t) => t.solid || placement.solid)) {
        throw new Error(`Collision detected at ${cellId}`);
      }
    }

    // Apply placement to all covered cells (store reference)
    for (const cellId of coveredCells) {
      const entry = this.cells.get(cellId) || { canonical: cellId, tiles: [] };
      entry.tiles.push(placement);
      this.cells.set(cellId, entry);
    }
  }

  /**
   * Check if a canonical cell is occupied
   */
  public isOccupied(canonical: string): boolean {
    return this.cells.has(canonical);
  }

  /**
   * Get tiles at canonical cell
   */
  public getTiles(canonical: string): TilePlacement[] {
    const entry = this.cells.get(canonical);
    return entry ? [...entry.tiles] : [];
  }

  /**
   * Remove all tiles at canonical cell
   */
  public clear(canonical: string): void {
    this.cells.delete(canonical);
  }

  /**
   * Check if a move is within bounds
   */
  public isInBounds(col: number, row: number): boolean {
    return col >= 0 && col < GRID_CELL_COLS && row >= 0 && row < GRID_CELL_ROWS;
  }

  /**
   * Serialize to plain object
   */
  public toJSON(): { cells: Array<{ canonical: string; tiles: TilePlacement[] }> } {
    return {
      cells: Array.from(this.cells.values()).map((c) => ({
        canonical: c.canonical,
        tiles: c.tiles,
      })),
    };
  }

  /**
   * Load from serialized payload
   */
  public fromJSON(payload: { cells: Array<{ canonical: string; tiles: TilePlacement[] }> }): void {
    this.cells.clear();
    for (const cell of payload.cells) {
      this.cells.set(cell.canonical, { canonical: cell.canonical, tiles: [...cell.tiles] });
    }
  }

  /**
   * Compute canonical IDs covered by a footprint anchored at canonical
   */
  private computeFootprintCells(anchorCanonical: string, footprint: Footprint): string[] {
    const addr = parseCanonicalAddress(anchorCanonical);
    const anchors: string[] = [];

    for (let dx = 0; dx < footprint.width; dx++) {
      for (let dy = 0; dy < footprint.height; dy++) {
        const col = addr.cell.col + dx;
        const row = addr.cell.row + dy;
        this.assertInBounds(col, row);
        const cellId = `${formatCanonicalAddress({
          baseLayer: addr.baseLayer,
          depth: addr.depth,
          cell: { col, row },
          band: addr.band,
        })}`;
        anchors.push(cellId);
      }
    }

    return anchors;
  }

  private assertInBounds(col: number, row: number): void {
    if (!this.isInBounds(col, row)) {
      throw new Error(`Out of bounds: col=${col}, row=${row}`);
    }
  }
}
