/**
 * Layer Editor Type Definitions
 *
 * Core types for the tile-based layer mapping system
 */

/**
 * A single tile in the layer grid
 */
export interface Tile {
  /** Character code (ASCII or Unicode) */
  char: string;
  /** Character code point */
  code: number;
  /** Foreground color (hex) */
  fg?: string;
  /** Background color (hex) */
  bg?: string;
  /** Link to document/location/marker */
  link?: TileLink;
  /** Additional metadata */
  metadata?: TileMetadata;
}

/**
 * Link from tile to uDOS resource
 */
export interface TileLink {
  /** Type of linked resource */
  type: "doc" | "location" | "marker" | "waypoint" | "object" | "script";
  /** Path to resource (relative to memory/) */
  path: string;
  /** Display label */
  label?: string;
  /** Additional properties specific to link type */
  properties?: Record<string, any>;
}

/**
 * Extended tile metadata
 */
export interface TileMetadata {
  /** Tile name/label */
  name?: string;
  /** Description */
  description?: string;
  /** Tags for categorization */
  tags?: string[];
  /** Custom properties */
  custom?: Record<string, any>;
}

/**
 * A map layer containing a 60x20 grid of tiles
 */
export interface Layer {
  /** Unique layer ID */
  id: string;
  /** Layer name */
  name: string;
  /** Layer description */
  description?: string;
  /** Grid dimensions */
  width: number;
  height: number;
  /** 2D array of tiles [row][col] */
  tiles: Tile[][];
  /** Layer visibility */
  visible: boolean;
  /** Layer opacity (0-1) */
  opacity: number;
  /** Layer locked (prevent editing) */
  locked: boolean;
  /** Z-index for stacking */
  zIndex: number;
  /** Blend mode for compositing */
  blendMode: "normal" | "multiply" | "screen" | "overlay";
  /** Layer metadata */
  metadata?: LayerMetadata;
}

/**
 * Layer-level metadata
 */
export interface LayerMetadata {
  /** Author */
  author?: string;
  /** Creation timestamp */
  created?: string;
  /** Last modified timestamp */
  modified?: string;
  /** Layer category/type */
  category?: string;
  /** Tags */
  tags?: string[];
  /** Custom properties */
  custom?: Record<string, any>;
}

/**
 * A map document containing multiple layers
 */
export interface MapDocument {
  /** Unique map ID */
  id: string;
  /** Map name */
  name: string;
  /** Map description */
  description?: string;
  /** Map version */
  version: string;
  /** All layers in the map */
  layers: Layer[];
  /** Active layer ID */
  activeLayerId: string | null;
  /** Default grid dimensions */
  defaultWidth: number;
  defaultHeight: number;
  /** Map-level metadata */
  metadata?: MapMetadata;
}

/**
 * Map-level metadata
 */
export interface MapMetadata {
  /** Author */
  author?: string;
  /** Creation timestamp */
  created?: string;
  /** Last modified timestamp */
  modified?: string;
  /** Map category/type */
  category?: string;
  /** Related maps */
  relatedMaps?: string[];
  /** Tags */
  tags?: string[];
  /** Custom properties */
  custom?: Record<string, any>;
}

/**
 * Layer editor state
 */
export interface LayerEditorState {
  /** Current map document */
  document: MapDocument | null;
  /** Selected tool */
  tool: "draw" | "erase" | "fill" | "select" | "link";
  /** Currently selected character */
  selectedChar: string;
  /** Currently selected character code */
  selectedCode: number;
  /** Current foreground color */
  fgColor: string;
  /** Current background color */
  bgColor: string;
  /** Show grid lines */
  showGrid: boolean;
  /** Show tile links */
  showLinks: boolean;
  /** Zoom level */
  zoom: number;
  /** Sidebar visibility */
  sidebarOpen: boolean;
  /** Active sidebar tab */
  sidebarTab: "layers" | "palette" | "links" | "browser";
  /** Dark mode */
  darkMode: boolean;
}

/**
 * Layer history entry for undo/redo
 */
export interface LayerHistoryEntry {
  /** Timestamp */
  timestamp: number;
  /** Action description */
  action: string;
  /** Layer ID */
  layerId: string;
  /** Previous state (for undo) */
  before: any;
  /** New state (for redo) */
  after: any;
}

/**
 * Default empty tile
 */
export function createEmptyTile(): Tile {
  return {
    char: " ",
    code: 0x0020,
  };
}

/**
 * Create a new layer with empty tiles
 */
export function createLayer(
  id: string,
  name: string,
  width: number = 60,
  height: number = 20
): Layer {
  const tiles: Tile[][] = Array(height)
    .fill(null)
    .map(() =>
      Array(width)
        .fill(null)
        .map(() => createEmptyTile())
    );

  return {
    id,
    name,
    width,
    height,
    tiles,
    visible: true,
    opacity: 1.0,
    locked: false,
    zIndex: 0,
    blendMode: "normal",
    metadata: {
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
    },
  };
}

/**
 * Create a new map document
 */
export function createMapDocument(
  name: string,
  width: number = 60,
  height: number = 20
): MapDocument {
  const baseLayer = createLayer("layer-1", "Base Layer", width, height);

  return {
    id: `map-${Date.now()}`,
    name,
    version: "1.0.0",
    layers: [baseLayer],
    activeLayerId: baseLayer.id,
    defaultWidth: width,
    defaultHeight: height,
    metadata: {
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
    },
  };
}
