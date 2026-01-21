/**
 * Location Parser & Data Model
 * 
 * Rebuilds location system with new grid geometry
 * Handles: cell addresses, layer bands, sparse world allocation, pathfinding
 */

import { Cell, parseCell, formatCell, CanonicalAddress, parseCanonicalAddress } from "../grid-runtime/src/address";

/**
 * Location: sparse, on-demand world model
 * 
 * Only explicit authored or discovered locations exist.
 * No pre-generation of tiles ever occurs.
 */
export interface Location {
  id: string;              // canonical ID (e.g., L300-AA10)
  address: CanonicalAddress;
  name?: string;
  kind?: string;           // "landmark", "town", "poi", etc.
  terrain?: string;        // terrain type
  objects?: string[];      // object tile IDs at this location
  sprites?: string[];      // sprite IDs
  markers?: string[];      // marker IDs
  connections?: {
    [direction: string]: string;  // "N", "E", "S", "W", etc. → adjacent location ID
  };
  metadata?: Record<string, any>;
}

/**
 * World State: collection of authored locations
 * 
 * Sparse allocation: only locations with explicit data are stored
 */
export class World {
  locations: Map<string, Location> = new Map();
  adjacencyGraph: Map<string, Map<string, string>> = new Map(); // optimize pathfinding

  /**
   * Register a location
   */
  addLocation(loc: Location): void {
    this.locations.set(loc.id, loc);

    // Build adjacency graph
    if (!this.adjacencyGraph.has(loc.id)) {
      this.adjacencyGraph.set(loc.id, new Map());
    }

    if (loc.connections) {
      for (const [dir, neighborId] of Object.entries(loc.connections)) {
        this.adjacencyGraph.get(loc.id)!.set(dir, neighborId);
      }
    }
  }

  /**
   * Get location by canonical ID
   */
  getLocation(id: string): Location | undefined {
    return this.locations.get(id);
  }

  /**
   * Find adjacent location in direction (N/E/S/W/NE/etc.)
   */
  getNeighbor(locationId: string, direction: string): string | undefined {
    return this.adjacencyGraph.get(locationId)?.get(direction);
  }

  /**
   * Validate address against authored world
   */
  isValidLocation(address: CanonicalAddress): boolean {
    const id = `L${address.baseLayer}-${formatCell(address.cell)}`;
    return this.locations.has(id);
  }

  /**
   * Sparse tile allocation: allocate if not exists
   */
  allocateTile(address: CanonicalAddress, kind: "object" | "sprite" | "marker"): void {
    const id = `L${address.baseLayer}-${formatCell(address.cell)}`;
    if (!this.locations.has(id)) {
      this.locations.set(id, {
        id,
        address,
        kind,
        metadata: { allocated_at: new Date().toISOString() }
      });
    }
  }
}

/**
 * Pathfinding: sparse world navigation
 * 
 * Uses explicit connections (tile_edges) rather than coordinate math
 */
export class PathFinder {
  constructor(private world: World) {}

  /**
   * Find path between two locations (BFS)
   */
  findPath(from: string, to: string): string[] | null {
    if (from === to) return [from];

    const queue: Array<{ id: string; path: string[] }> = [{ id: from, path: [from] }];
    const visited = new Set<string>([from]);

    while (queue.length > 0) {
      const { id, path } = queue.shift()!;

      // Check all directions
      const locNode = this.world.adjacencyGraph.get(id);
      if (!locNode) continue;

      for (const [_direction, neighborId] of locNode.entries()) {
        if (neighborId === to) {
          return [...path, neighborId];
        }

        if (!visited.has(neighborId)) {
          visited.add(neighborId);
          queue.push({ id: neighborId, path: [...path, neighborId] });
        }
      }
    }

    return null; // no path found
  }

  /**
   * Get adjacent walkable locations
   */
  getWalkable(locationId: string): string[] {
    return Array.from(this.world.adjacencyGraph.get(locationId)?.values() || []);
  }
}

/**
 * Location JSON Parser
 * 
 * Converts location.json → World instance
 */
export interface LocationJSON {
  version: string;
  locations: Array<{
    id: string;
    name?: string;
    kind?: string;
    terrain?: string;
    objects?: string[];
    sprites?: string[];
    markers?: string[];
    connections?: Record<string, string>;
    metadata?: Record<string, any>;
  }>;
}

export function parseLocationJSON(data: LocationJSON): World {
  const world = new World();

  for (const locData of data.locations) {
    // Validate and parse address
    let address: CanonicalAddress;
    try {
      address = parseCanonicalAddress(locData.id);
    } catch (e) {
      console.warn(`Skipping invalid location: ${locData.id}`, e);
      continue;
    }

    const loc: Location = {
      id: locData.id,
      address,
      name: locData.name,
      kind: locData.kind,
      terrain: locData.terrain,
      objects: locData.objects,
      sprites: locData.sprites,
      markers: locData.markers,
      connections: locData.connections,
      metadata: locData.metadata
    };

    world.addLocation(loc);
  }

  return world;
}

/**
 * Location JSON Serializer
 * 
 * Converts World → location.json
 */
export function serializeWorldToJSON(world: World): LocationJSON {
  const locations = Array.from(world.locations.values()).map((loc) => ({
    id: loc.id,
    name: loc.name,
    kind: loc.kind,
    terrain: loc.terrain,
    objects: loc.objects,
    sprites: loc.sprites,
    markers: loc.markers,
    connections: loc.connections,
    metadata: loc.metadata
  }));

  return {
    version: "1.0.0",
    locations
  };
}
