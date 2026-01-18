/**
 * Phase 4: Location + Sparse World tests
 */

import { LocationManager } from "../src/location-manager";
import { SparseWorld, TilePlacement } from "../src/sparse-world";
import { Pathfinder } from "../src/pathfinding";
import { GridBlock } from "../src/code-block-parser";
import { FOOTPRINT_WIDE } from "../src/geometry";

const simpleGrid: GridBlock = {
  type: "grid",
  location: {
    name: "Test Location",
    layer: 300,
    startCell: "AA10",
    cells: [
      { address: "AA10", terrain: "grass" },
      { address: "AB10", terrain: "tree" },
    ],
  },
};

describe("LocationManager", () => {
  test("loads grid block and registers location", () => {
    const manager = new LocationManager();
    const record = manager.loadGridLocation(simpleGrid);

    expect(record.name).toBe("Test Location");
    expect(record.band).toBe("SUR");
    expect(record.startCell.col).toBe(0);
    expect(manager.getLocation(record.id)).toBeDefined();
  });

  test("throws on invalid layer outside SUR/UDN/SUB", () => {
    const manager = new LocationManager();
    const badGrid: GridBlock = {
      type: "grid",
      location: {
        name: "Bad",
        layer: 999,
        startCell: "AA10",
        cells: [],
      },
    };
    expect(() => manager.loadGridLocation(badGrid)).toThrow("Layer 999");
  });

  test("throws on out-of-bounds cell", () => {
    const manager = new LocationManager();
    const badCell: GridBlock = {
      type: "grid",
      location: {
        name: "Bad Cell",
        layer: 300,
        startCell: "ZZ99",
        cells: [],
      },
    } as any;

    expect(() => manager.loadGridLocation(badCell)).toThrow();
  });
});

describe("SparseWorld", () => {
  test("prevents collision with solid footprint", () => {
    const world = new SparseWorld();
    world.place("L300-AA10", { id: "tree", type: "object", solid: true, footprint: FOOTPRINT_WIDE });
    expect(() =>
      world.place("L300-AA10", { id: "rock", type: "object", solid: true })
    ).toThrow("Collision");
  });

  test("allows non-solid terrain coexistence", () => {
    const world = new SparseWorld();
    world.place("L300-AA10", { id: "grass", type: "marker", solid: false });
    expect(world.isOccupied("L300-AA10")).toBe(true);
    const tiles = world.getTiles("L300-AA10");
    expect(tiles.length).toBe(1);
  });

  test("serializes and restores state", () => {
    const world = new SparseWorld();
    world.place("L300-AA10", { id: "grass", type: "marker" });
    const snapshot = world.toJSON();

    const restored = new SparseWorld();
    restored.fromJSON(snapshot);
    expect(restored.isOccupied("L300-AA10")).toBe(true);
    expect(restored.getTiles("L300-AA10")[0].id).toBe("grass");
  });
});

describe("Pathfinder", () => {
  test("finds path when unblocked", () => {
    const world = new SparseWorld();
    const finder = new Pathfinder(world);
    const result = finder.findPath("L300-AA10", "L300-AB10");
    expect(result.found).toBe(true);
    expect(result.path[0]).toBe("L300-AA10");
    expect(result.path[result.path.length - 1]).toBe("L300-AB10");
  });

  test("returns no path when blocked by solid", () => {
    const world = new SparseWorld();
    world.place("L300-AB10", { id: "wall", type: "object", solid: true });
    const finder = new Pathfinder(world);
    const result = finder.findPath("L300-AA10", "L300-AB10");
    expect(result.found).toBe(false);
  });

  test("rejects path across different effective layers", () => {
    const world = new SparseWorld();
    const finder = new Pathfinder(world);
    const result = finder.findPath("L300-AA10", "L301-AA10");
    expect(result.found).toBe(false);
    expect(result.path.length).toBe(0);
  });
});
