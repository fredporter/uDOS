/**
 * Location Loader - Parse and manage location database
 * 
 * Supports terrestrial (L300-L305) through cosmic scales (L306+)
 * Distance scaling: meters → km → AU → light years → mega light years
 * 
 * @module grid-runtime/location-loader
 */

import {
  Location,
  LocationDatabase,
  LocationConnection,
  TileContent,
  parseLocationId,
  formatLocationId,
  validateLocation,
} from './location-types';

/**
 * Distance scale for layer ranges
 * Higher layers = exponentially larger distances
 */
export enum DistanceScale {
  TERRESTRIAL = 'terrestrial',  // L300-L305: meters/kilometers (Earth surface/underground)
  ORBITAL = 'orbital',           // L306-L310: thousands of km (satellites, space stations)
  PLANETARY = 'planetary',       // L311-L320: AU (solar system: planets, moons, asteroids)
  STELLAR = 'stellar',           // L321-L350: light years (nearby stars, exoplanets)
  GALACTIC = 'galactic',         // L351-L400: kilo light years (galaxy regions)
  COSMIC = 'cosmic',             // L401+: mega light years (galaxies, clusters)
}

/**
 * Get distance scale for a given layer
 * @param layer - Layer number
 * @returns Distance scale category
 */
export function getDistanceScale(layer: number): DistanceScale {
  if (layer >= 300 && layer <= 305) return DistanceScale.TERRESTRIAL;
  if (layer >= 306 && layer <= 310) return DistanceScale.ORBITAL;
  if (layer >= 311 && layer <= 320) return DistanceScale.PLANETARY;
  if (layer >= 321 && layer <= 350) return DistanceScale.STELLAR;
  if (layer >= 351 && layer <= 400) return DistanceScale.GALACTIC;
  return DistanceScale.COSMIC;
}

/**
 * Get distance unit for a scale
 * @param scale - Distance scale
 * @returns Human-readable unit (e.g., "km", "AU", "ly")
 */
export function getDistanceUnit(scale: DistanceScale): string {
  switch (scale) {
    case DistanceScale.TERRESTRIAL: return 'm';
    case DistanceScale.ORBITAL: return 'km';
    case DistanceScale.PLANETARY: return 'AU';
    case DistanceScale.STELLAR: return 'ly';
    case DistanceScale.GALACTIC: return 'kly';
    case DistanceScale.COSMIC: return 'Mly';
  }
}

/**
 * Calculate base distance per cell for a given scale
 * @param scale - Distance scale
 * @returns Distance in scale units (e.g., 1 cell = 16m terrestrial, 1 cell = 0.1 AU planetary)
 */
export function getCellDistance(scale: DistanceScale): number {
  switch (scale) {
    case DistanceScale.TERRESTRIAL: return 16;      // 16 meters (tile size)
    case DistanceScale.ORBITAL: return 1000;        // 1000 km
    case DistanceScale.PLANETARY: return 0.1;       // 0.1 AU
    case DistanceScale.STELLAR: return 1;           // 1 light year
    case DistanceScale.GALACTIC: return 100;        // 100 kly
    case DistanceScale.COSMIC: return 1000;         // 1000 Mly
  }
}

/**
 * Parse a cell address (e.g., "AA10") into grid coordinates.
 * Columns are base-26 (A=0), rows are numeric.
 */
function parseCellAddress(cell: string): { col: number; row: number } | null {
  const match = cell.match(/^([A-Z]{2})(\d+)$/);
  if (!match) return null;

  const letters = match[1];
  const row = parseInt(match[2], 10);
  if (Number.isNaN(row)) return null;

  const col =
    (letters.charCodeAt(0) - 65) * 26 +
    (letters.charCodeAt(1) - 65);

  if (col < 0) return null;

  return { col, row };
}

/**
 * World model - manages all locations and spatial relationships
 */
export class World {
  private locations: Map<string, Location>;
  private version: string;
  private connectionGraph: Map<string, Set<string>>;
  
  constructor() {
    this.locations = new Map();
    this.version = '1.0.7.0';
    this.connectionGraph = new Map();
  }
  
  /**
   * Load locations from JSON database
   * @param data - LocationDatabase object
   */
  loadDatabase(data: LocationDatabase): void {
    this.version = data.version;
    
    // Validate and load all locations
    for (const [id, location] of Object.entries(data.locations)) {
      try {
        validateLocation(location);
        this.locations.set(id, location);
      } catch (error) {
        console.warn(`Skipping invalid location ${id}:`, error);
      }
    }
    
    // Build connection graph
    this.buildConnectionGraph();
  }
  
  /**
   * Build bidirectional connection graph for pathfinding
   */
  private buildConnectionGraph(): void {
    this.connectionGraph.clear();
    
    for (const location of this.locations.values()) {
      const sourceId = location.id;
      
      if (!this.connectionGraph.has(sourceId)) {
        this.connectionGraph.set(sourceId, new Set());
      }
      
      for (const conn of location.connections) {
        const targetId = conn.target;
        
        // Add forward connection
        this.connectionGraph.get(sourceId)!.add(targetId);
        
        // Add reverse connection if bidirectional
        if (conn.bidirectional !== false) {
          if (!this.connectionGraph.has(targetId)) {
            this.connectionGraph.set(targetId, new Set());
          }
          this.connectionGraph.get(targetId)!.add(sourceId);
        }
      }
    }
  }
  
  /**
   * Get location by ID
   * @param id - Location ID (e.g., "L300-AA10")
   * @returns Location or undefined if not found
   */
  getLocation(id: string): Location | undefined {
    return this.locations.get(id);
  }
  
  /**
   * Get all locations
   * @returns Array of all locations
   */
  getAllLocations(): Location[] {
    return Array.from(this.locations.values());
  }
  
  /**
   * Get locations by layer
   * @param layer - Layer number (e.g., 300)
   * @returns Array of locations on that layer
   */
  getLocationsByLayer(layer: number): Location[] {
    return this.getAllLocations().filter(loc => loc.layer === layer);
  }
  
  /**
   * Get locations by distance scale
   * @param scale - Distance scale category
   * @returns Array of locations in that scale range
   */
  getLocationsByScale(scale: DistanceScale): Location[] {
    return this.getAllLocations().filter(loc => 
      getDistanceScale(loc.layer) === scale
    );
  }
  
  /**
   * Get tile content at a specific position in a location
   * @param locationId - Location ID
   * @param cell - Cell address (e.g., "AA10")
   * @returns Tile content or undefined if empty
   */
  getTileContent(locationId: string, cell: string): TileContent | undefined {
    const location = this.getLocation(locationId);
    if (!location) return undefined;
    
    return location.tiles[cell];
  }
  
  /**
   * Get connected locations
   * @param locationId - Source location ID
   * @returns Array of connected location IDs
   */
  getConnectedLocations(locationId: string): string[] {
    const connections = this.connectionGraph.get(locationId);
    return connections ? Array.from(connections) : [];
  }
  
  /**
   * Find shortest path between two locations (BFS)
   * @param startId - Starting location ID
   * @param targetId - Target location ID
   * @returns Array of location IDs (path) or null if no path exists
   */
  findPath(startId: string, targetId: string): string[] | null {
    if (startId === targetId) return [startId];
    
    const queue: Array<{ id: string; path: string[] }> = [
      { id: startId, path: [startId] }
    ];
    const visited = new Set<string>([startId]);
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      
      const neighbors = this.getConnectedLocations(current.id);
      for (const neighborId of neighbors) {
        if (neighborId === targetId) {
          return [...current.path, neighborId];
        }
        
        if (!visited.has(neighborId)) {
          visited.add(neighborId);
          queue.push({
            id: neighborId,
            path: [...current.path, neighborId]
          });
        }
      }
    }
    
    return null; // No path found
  }
  
  /**
   * Calculate distance between two locations (same layer only)
   * @param locationId1 - First location ID
   * @param locationId2 - Second location ID
   * @returns Distance in appropriate units or null if different layers
   */
  calculateDistance(locationId1: string, locationId2: string): number | null {
    const loc1 = this.getLocation(locationId1);
    const loc2 = this.getLocation(locationId2);
    
    if (!loc1 || !loc2 || loc1.layer !== loc2.layer) {
      return null;
    }
    
    const parsed1 = parseLocationId(locationId1);
    const parsed2 = parseLocationId(locationId2);
    
    if (!parsed1 || !parsed2) return null;

    const cell1 = parseCellAddress(parsed1.cell);
    const cell2 = parseCellAddress(parsed2.cell);
    if (!cell1 || !cell2) return null;

    const dx = cell2.col - cell1.col;
    const dy = cell2.row - cell1.row;
    const distanceCells = Math.sqrt(dx * dx + dy * dy);

    const scale = getDistanceScale(loc1.layer);
    return distanceCells * getCellDistance(scale);
  }
  
  /**
   * Get location metadata for display
   * @param locationId - Location ID
   * @returns Formatted location info or null
   */
  getLocationInfo(locationId: string): {
    id: string;
    name: string;
    description: string;
    layer: number;
    scale: DistanceScale;
    unit: string;
    connectionCount: number;
  } | null {
    const location = this.getLocation(locationId);
    if (!location) return null;
    
    const scale = getDistanceScale(location.layer);
    const unit = getDistanceUnit(scale);
    const connectionCount = location.connections.length;
    
    return {
      id: location.id,
      name: location.metadata.name,
      description: location.metadata.description,
      layer: location.layer,
      scale,
      unit,
      connectionCount,
    };
  }
  
  /**
   * Search locations by name or description
   * @param query - Search query
   * @returns Array of matching locations
   */
  searchLocations(query: string): Location[] {
    const lowerQuery = query.toLowerCase();
    
    return this.getAllLocations().filter(location => {
      const name = location.metadata.name.toLowerCase();
      const desc = location.metadata.description.toLowerCase();
      const tags = location.metadata.tags?.join(' ').toLowerCase() || '';
      
      return name.includes(lowerQuery) || 
             desc.includes(lowerQuery) || 
             tags.includes(lowerQuery);
    });
  }
  
  /**
   * Get statistics about the world
   */
  getStatistics(): {
    totalLocations: number;
    locationsByScale: Record<DistanceScale, number>;
    totalConnections: number;
  } {
    const totalLocations = this.locations.size;
    
    const locationsByScale: Record<DistanceScale, number> = {
      [DistanceScale.TERRESTRIAL]: 0,
      [DistanceScale.ORBITAL]: 0,
      [DistanceScale.PLANETARY]: 0,
      [DistanceScale.STELLAR]: 0,
      [DistanceScale.GALACTIC]: 0,
      [DistanceScale.COSMIC]: 0,
    };
    
    let totalConnections = 0;
    
    for (const location of this.locations.values()) {
      const scale = getDistanceScale(location.layer);
      locationsByScale[scale]++;
      totalConnections += location.connections.length;
    }
    
    return {
      totalLocations,
      locationsByScale,
      totalConnections,
    };
  }
}

/**
 * Load location database from JSON file
 * @param jsonData - Raw JSON string or parsed object
 * @returns Initialized World instance
 */
export function loadLocationDatabase(jsonData: string | LocationDatabase): World {
  const data = typeof jsonData === 'string' 
    ? JSON.parse(jsonData) as LocationDatabase
    : jsonData;
  
  const world = new World();
  world.loadDatabase(data);
  
  return world;
}
