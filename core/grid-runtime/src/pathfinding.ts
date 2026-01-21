/**
 * Pathfinding (BFS) on 80×30 grids
 *
 * - Validates movement on same effective layer
 * - Respects occupancy (solid tiles block paths)
 * - Returns list of canonical addresses including start and goal
 */

import { GRID_CELL_COLS, GRID_CELL_ROWS } from "./geometry";
import { parseCanonicalAddress, formatCanonicalAddress } from "./address";
import { SparseWorld } from "./sparse-world";

export interface PathResult {
  path: string[];
  found: boolean;
}

export class Pathfinder {
  private world: SparseWorld;

  constructor(world: SparseWorld) {
    this.world = world;
  }

  /**
   * Find shortest path using BFS; returns empty path if unreachable
   */
  public findPath(startCanonical: string, goalCanonical: string): PathResult {
    const start = parseCanonicalAddress(startCanonical);
    const goal = parseCanonicalAddress(goalCanonical);

    // Must be on same effective layer
    if (start.baseLayer + start.depth !== goal.baseLayer + goal.depth) {
      return { path: [], found: false };
    }

    const visited = new Set<string>();
    const queue: Array<{ canonical: string; prev?: string }> = [];

    const startId = formatCanonicalAddress(start);
    const goalId = formatCanonicalAddress(goal);
    queue.push({ canonical: startId });
    visited.add(startId);

    const parents: Record<string, string | undefined> = {};

    while (queue.length) {
      const current = queue.shift()!;
      if (current.canonical === goalId) {
        const path = this.reconstructPath(parents, goalId, startId);
        return { path, found: true };
      }

      const neighbors = this.getNeighbors(current.canonical);
      for (const n of neighbors) {
        if (visited.has(n)) continue;
        // Blocked check
        if (this.world.isOccupied(n)) {
          const tiles = this.world.getTiles(n);
          if (tiles.some((t) => t.solid)) {
            continue;
          }
        }
        visited.add(n);
        parents[n] = current.canonical;
        queue.push({ canonical: n, prev: current.canonical });
      }
    }

    return { path: [], found: false };
  }

  /**
   * Get 4-directional neighbors within bounds for the same layer
   */
  private getNeighbors(canonical: string): string[] {
    const addr = parseCanonicalAddress(canonical);
    const { col, row } = addr.cell;
    const neighbors: string[] = [];

    const deltas = [
      { dc: 1, dr: 0 },
      { dc: -1, dr: 0 },
      { dc: 0, dr: 1 },
      { dc: 0, dr: -1 },
    ];

    for (const delta of deltas) {
      const nc = col + delta.dc;
      const nr = row + delta.dr;
      if (nc < 0 || nc >= GRID_CELL_COLS || nr < 0 || nr >= GRID_CELL_ROWS) {
        continue;
      }
      const neighbor = formatCanonicalAddress({
        baseLayer: addr.baseLayer,
        depth: addr.depth,
        cell: { col: nc, row: nr },
        band: addr.band,
      });
      neighbors.push(neighbor);
    }

    return neighbors;
  }

  /**
   * Reconstruct path from parent map
   */
  private reconstructPath(parents: Record<string, string | undefined>, goal: string, start: string): string[] {
    const path: string[] = [];
    let current: string | undefined = goal;
    while (current) {
      path.push(current);
      if (current === start) break;
      current = parents[current];
    }
    return path.reverse();
  }
}
