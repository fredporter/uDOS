/**
 * Location Data Types for v1.0.7.0 Grid Runtime
 * 
 * Defines the structure for location data parsed from locations-examples-v1.0.7.0.json
 * Implements the schema specified in location.schema.json
 * 
 * @module grid-runtime/location-types
 */

/**
 * Connection between locations (bidirectional or directional)
 */
export interface LocationConnection {
  /** Target location ID (e.g., "L300-BD14") */
  target: string;
  
  /** Connection type (default: "walk") */
  type?: 'walk' | 'climb' | 'jump' | 'teleport' | 'door' | 'ladder' | 'stairs';
  
  /** Human-readable label for the connection */
  label?: string;
  
  /** Whether connection requires a condition/key */
  requires?: string;
  
  /** Whether connection is bidirectional (default: true) */
  bidirectional?: boolean;
}

/**
 * Static object (fixed position, non-interactive)
 */
export interface TileObject {
  /** Display character or emoji */
  char: string;
  
  /** Descriptive label */
  label: string;
  
  /** Z-index layer (0-2) */
  z?: number;
  
  /** Background color (hex or named) */
  bg?: string;
  
  /** Foreground color (hex or named) */
  fg?: string;
  
  /** Whether object blocks movement */
  blocks?: boolean;
}

/**
 * Sprite (dynamic, can move/animate)
 */
export interface TileSprite {
  /** Unique sprite ID (e.g., "player", "npc-merchant") */
  id: string;
  
  /** Display character or emoji */
  char: string;
  
  /** Descriptive label */
  label: string;
  
  /** Z-index layer (0-2, sprites usually z=1) */
  z?: number;
  
  /** Background color (hex or named) */
  bg?: string;
  
  /** Foreground color (hex or named) */
  fg?: string;
  
  /** Whether sprite blocks movement */
  blocks?: boolean;
  
  /** Animation frames (alternating characters) */
  animation?: string[];
  
  /** Animation interval in ms */
  animationSpeed?: number;
}

/**
 * Location marker (waypoint, spawn point, etc.)
 */
export interface TileMarker {
  /** Marker type (spawn, waypoint, exit, etc.) */
  type: string;
  
  /** Optional label */
  label?: string;
  
  /** Optional metadata */
  metadata?: Record<string, any>;
}

/**
 * Tile content at a specific grid position
 */
export interface TileContent {
  /** Static objects at this position */
  objects?: TileObject[];
  
  /** Sprites at this position */
  sprites?: TileSprite[];
  
  /** Markers at this position */
  markers?: TileMarker[];
}

/**
 * Sparse tile map (only stores non-empty tiles)
 * Key format: "AA10" (cell address)
 */
export type TileMap = Record<string, TileContent>;

/**
 * Location metadata
 */
export interface LocationMetadata {
  /** Display name */
  name: string;
  
  /** Location description */
  description: string;
  
  /** Location type (e.g., "city", "dungeon", "wilderness") */
  type?: string;
  
  /** Tags for categorization */
  tags?: string[];
  
  /** Creation/update timestamps */
  created?: string;
  updated?: string;
  
  /** Author/creator */
  author?: string;
}

/**
 * Complete location definition
 */
export interface Location {
  /** Unique location ID (e.g., "L300-AA10") */
  id: string;
  
  /** Location metadata */
  metadata: LocationMetadata;
  
  /** Connections to other locations */
  connections: LocationConnection[];
  
  /** Sparse tile map (only non-empty tiles) */
  tiles: TileMap;
  
  /** Layer number (300-305) */
  layer: number;
  
  /** Center cell address (e.g., "AA10") */
  center: string;
}

/**
 * Collection of all locations
 */
export interface LocationDatabase {
  /** Schema version (e.g., "1.0.7.0") */
  version: string;
  
  /** All locations indexed by ID */
  locations: Record<string, Location>;
}

/**
 * Parse location ID into components
 * @param locationId - Full location ID (e.g., "L300-AA10")
 * @returns Parsed components or null if invalid
 */
export function parseLocationId(locationId: string): {
  layer: number;
  cell: string;
} | null {
  const match = locationId.match(/^L(\d+)-([A-Z]{2}\d+)$/);
  if (!match) return null;
  
  const layer = parseInt(match[1], 10);
  const cell = match[2];
  
  // Validate layer range (300+ for terrestrial through cosmic)
  if (layer < 300) return null;
  
  return { layer, cell };
}

/**
 * Format location ID from components
 * @param layer - Layer number (300+)
 * @param cell - Cell address (e.g., "AA10")
 * @returns Formatted location ID (e.g., "L300-AA10")
 */
export function formatLocationId(layer: number, cell: string): string {
  if (layer < 300) {
    throw new Error(`Invalid layer: ${layer} (must be 300+)`);
  }
  
  if (!/^[A-Z]{2}\d+$/.test(cell)) {
    throw new Error(`Invalid cell format: ${cell}`);
  }
  
  return `L${layer}-${cell}`;
}

/**
 * Validate location structure
 * @param location - Location object to validate
 * @returns True if valid, throws error if invalid
 */
export function validateLocation(location: Location): boolean {
  // Validate ID format
  const parsed = parseLocationId(location.id);
  if (!parsed) {
    throw new Error(`Invalid location ID: ${location.id}`);
  }
  
  // Validate layer matches ID
  if (parsed.layer !== location.layer) {
    throw new Error(`Layer mismatch: ${parsed.layer} vs ${location.layer}`);
  }
  
  // Validate center matches ID
  if (parsed.cell !== location.center) {
    throw new Error(`Center mismatch: ${parsed.cell} vs ${location.center}`);
  }
  
  // Validate metadata
  if (!location.metadata || !location.metadata.name) {
    throw new Error(`Missing location metadata name`);
  }
  
  // Validate connections
  for (const conn of location.connections) {
    if (!conn.target) {
      throw new Error(`Connection missing target`);
    }
    if (!parseLocationId(conn.target)) {
      throw new Error(`Invalid connection target: ${conn.target}`);
    }
  }
  
  return true;
}
