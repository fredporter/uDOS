/**
 * LocationManager
 * Phase 4: Location + Sparse World
 *
 * Responsibilities:
 * - Load GridBlock (Phase 3 output) into sparse world coordinates
 * - Validate layer bands (SUR/UDN/SUB) and grid bounds (80×30)
 * - Normalize canonical IDs: L{EffectiveLayer}-{Cell}
 */

import {
  GRID_CELL_COLS,
  GRID_CELL_ROWS,
  LAYER_BANDS,
  FOOTPRINT_STANDARD,
  FOOTPRINT_WIDE,
} from "./geometry.js";
import {
  CanonicalAddress,
  LayerBand,
  Cell,
  parseCell,
  formatCell,
  parseCanonicalAddress,
  formatCanonicalAddress,
  getEffectiveLayer,
  getLayerBand,
  validateLayerInBand,
} from "./address.js";
import { GridBlock } from "./code-block-parser.js";
import { SparseWorld, TilePlacement } from "./sparse-world.js";

/**
 * LocationRecord captures normalized location metadata
 */
export interface LocationRecord {
  id: string; // canonical start address L{layer}-{cell}
  name: string;
  baseLayer: number;
  depth: number;
  effectiveLayer: number;
  startCell: Cell;
  band: LayerBand;
  cells: Array<{
    address: string;
    objects?: Array<{ type: string; props?: Record<string, any> }>;
    sprites?: Array<{ id: string; props?: Record<string, any> }>;
    terrain?: string;
  }>;
}

/**
 * LocationManager orchestrates loading grid blocks into sparse world storage
 */
export class LocationManager {
  private locations: Map<string, LocationRecord> = new Map();
  private world: SparseWorld;

  constructor(world?: SparseWorld) {
    this.world = world || new SparseWorld();
  }

  /**
   * Load a GridBlock (Phase 3 parsed block) and register it
   * @returns LocationRecord
   */
  public loadGridLocation(block: GridBlock): LocationRecord {
    const { location } = block;

    // Validate layer band
    const band = getLayerBand(location.layer);
    if (!validateLayerInBand(location.layer, band)) {
      throw new Error(`Layer ${location.layer} is outside band ${band}`);
    }

    // Normalize start cell
    const startCell = parseCell(location.startCell);
    this.assertInBounds(startCell);

    const record: LocationRecord = {
      id: this.toCanonicalId(location.layer, startCell),
      name: location.name,
      baseLayer: location.layer,
      depth: 0,
      effectiveLayer: location.layer,
      startCell,
      band,
      cells: location.cells || [],
    };

    // Register location
    this.locations.set(record.id, record);

    // Allocate authored cells into sparse world
    for (const cell of record.cells) {
      const parsed = parseCell(cell.address);
      this.assertInBounds(parsed);
      const canonical = this.toCanonicalId(record.effectiveLayer, parsed);

      // Objects
      if (cell.objects) {
        for (const obj of cell.objects) {
          const placement: TilePlacement = {
            id: obj.type,
            type: "object",
            solid: true,
            footprint: FOOTPRINT_STANDARD,
            props: obj.props,
          };
          this.world.place(canonical, placement);
        }
      }

      // Sprites
      if (cell.sprites) {
        for (const sprite of cell.sprites) {
          const placement: TilePlacement = {
            id: sprite.id,
            type: "sprite",
            solid: false,
            footprint: FOOTPRINT_STANDARD,
            props: sprite.props,
          };
          this.world.place(canonical, placement);
        }
      }

      // Terrain as marker (non-solid)
      if (cell.terrain) {
        const placement: TilePlacement = {
          id: cell.terrain,
          type: "marker",
          solid: false,
          footprint: FOOTPRINT_WIDE,
        };
        // Terrain should not block; allow coexistence if empty
        if (!this.world.isOccupied(canonical)) {
          this.world.place(canonical, placement);
        }
      }
    }

    return record;
  }

  /**
   * Retrieve location by canonical id
   */
  public getLocation(id: string): LocationRecord | undefined {
    return this.locations.get(id);
  }

  /**
   * List all registered locations
   */
  public list(): LocationRecord[] {
    return Array.from(this.locations.values());
  }

  /**
   * Serialize all locations and sparse world state
   */
  public serialize(): {
    locations: LocationRecord[];
    world: ReturnType<SparseWorld["toJSON"]>;
  } {
    return {
      locations: this.list(),
      world: this.world.toJSON(),
    };
  }

  /**
   * Replace state with serialized payload
   */
  public loadFromSerialized(payload: {
    locations: LocationRecord[];
    world: ReturnType<SparseWorld["toJSON"]>;
  }): void {
    this.locations.clear();
    for (const loc of payload.locations) {
      this.locations.set(loc.id, loc);
    }
    this.world.fromJSON(payload.world);
  }

  /**
   * Access underlying sparse world
   */
  public getWorld(): SparseWorld {
    return this.world;
  }

  /**
   * Ensure a cell is within 80×30 bounds
   */
  private assertInBounds(cell: Cell): void {
    if (cell.col < 0 || cell.col >= GRID_CELL_COLS) {
      throw new Error(`Column out of bounds: ${cell.col}`);
    }
    if (cell.row < 0 || cell.row >= GRID_CELL_ROWS) {
      throw new Error(`Row out of bounds: ${cell.row}`);
    }
  }

  /**
   * Build canonical ID from layer and cell
   */
  private toCanonicalId(layer: number, cell: Cell): string {
    const base: CanonicalAddress = {
      baseLayer: layer,
      depth: 0,
      cell,
      band: getLayerBand(layer),
    };
    return formatCanonicalAddress(base);
  }
}
