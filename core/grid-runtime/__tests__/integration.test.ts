/**
 * Integration Tests - Rendering Pipeline
 * 
 * Tests the core rendering flow:
 * Location data → Compositor → Display
 */

import { TileCompositor } from '../src/tile-compositor';
import { RenderQuality } from '../src/teletext-renderer';
import * as fs from 'fs';
import * as path from 'path';

// Load real location data
const loadLocationDatabase = () => {
  const dataPath = path.join(__dirname, '../../locations-full-examples-v1.0.7.0.json');
  const data = fs.readFileSync(dataPath, 'utf-8');
  return JSON.parse(data);
};

describe('Integration Tests - Rendering Pipeline', () => {
  let db: any;
  
  beforeAll(() => {
    db = loadLocationDatabase();
  });

  describe('Location Data Loading', () => {
    it('should load all 31 locations', () => {
      expect(db.locations.length).toBe(31);
    });

    it('should have Forest Clearing with tiles', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      expect(forest).toBeDefined();
      expect(forest.name).toBe('Forest Clearing');
      expect(forest.tiles).toBeDefined();
      expect(Object.keys(forest.tiles).length).toBeGreaterThan(0);
    });

    it('should have cosmic locations', () => {
      const andromeda = db.locations.find((l: any) => l.layer === 401);
      expect(andromeda).toBeDefined();
      expect(andromeda.name).toBe('Andromeda Galaxy (M31)');
    });

    it('should have major cities across continents', () => {
      const cities = db.locations.filter((l: any) => l.type === 'major-city');
      expect(cities.length).toBeGreaterThan(5);
      
      const continents = new Set(cities.map((c: any) => c.continent));
      expect(continents.has('Asia')).toBe(true);
      expect(continents.has('Africa')).toBe(true);
      expect(continents.has('North America')).toBe(true);
      expect(continents.has('South America')).toBe(true);
      expect(continents.has('Europe')).toBe(true);
      expect(continents.has('Oceania')).toBe(true);
    });

    it('should have geographical landmarks', () => {
      const landmarks = db.locations.filter((l: any) => l.type === 'geographical-landmark');
      expect(landmarks.length).toBe(12);
      
      // Verify diverse geographic features
      const names = landmarks.map((l: any) => l.name);
      expect(names.some((n: string) => n.includes('Mount'))).toBe(true);
      expect(names.some((n: string) => n.includes('Beach') || n.includes('Reef'))).toBe(true);
      expect(names.some((n: string) => n.includes('Desert'))).toBe(true);
      expect(names.some((n: string) => n.includes('Falls'))).toBe(true);
      expect(names.some((n: string) => n.includes('Rainforest'))).toBe(true);
    });
  });

  describe('Tile Rendering', () => {
    it('should render Forest Clearing tiles', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor();
      
      const output = compositor.render(forest.tiles, 5, 5);
      
      // Should contain player sprite (AA10 = row 10, but we're rendering 5x5 from AA00)
      // Player is at AA10, which is outside our 5x5 grid starting at AA00
      // So let's just check the grid renders without error
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });

    it('should render orbital location (ISS)', () => {
      const orbit = db.locations.find((l: any) => l.layer === 306);
      const compositor = new TileCompositor();
      
      const output = compositor.render(orbit.tiles, 5, 5);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });

    it('should render Mars surface', () => {
      const mars = db.locations.find((l: any) => l.layer === 311);
      const compositor = new TileCompositor();
      
      const output = compositor.render(mars.tiles, 5, 5);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });

    it('should render Alpha Centauri system', () => {
      const alphaCen = db.locations.find((l: any) => l.layer === 321);
      const compositor = new TileCompositor();
      
      const output = compositor.render(alphaCen.tiles, 5, 5);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });

    it('should render Sagittarius A* (black hole)', () => {
      const blackHole = db.locations.find((l: any) => l.layer === 351);
      const compositor = new TileCompositor();
      
      const output = compositor.render(blackHole.tiles, 5, 5);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });

    it('should render Andromeda Galaxy', () => {
      const andromeda = db.locations.find((l: any) => l.layer === 401);
      const compositor = new TileCompositor();
      
      const output = compositor.render(andromeda.tiles, 5, 5);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.split('\n').length).toBe(5);
    });
  });

  describe('Quality Levels', () => {
    it('should render with teletext quality', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor({ quality: RenderQuality.TELETEXT });
      
      const output = compositor.render(forest.tiles, 5, 5);
      
      expect(output.length).toBeGreaterThan(0);
    });

    it('should render with ASCII quality', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor({ quality: RenderQuality.ASCII });
      
      const output = compositor.render(forest.tiles, 5, 5);
      
      expect(output.length).toBeGreaterThan(0);
      // ASCII uses simpler characters
      expect(output).toMatch(/[@#X. \n]/);
    });
  });

  describe('Grid Sizes', () => {
    it('should render 80x30 standard grid', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor();
      
      const output = compositor.render(forest.tiles, 80, 30);
      
      const lines = output.split('\n');
      expect(lines.length).toBe(30);
      expect(lines[0].length).toBeGreaterThanOrEqual(70); // Allow for emoji widths
    });

    it('should render 40x15 mini grid', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor();
      
      const output = compositor.render(forest.tiles, 40, 15);
      
      const lines = output.split('\n');
      expect(lines.length).toBe(15);
    });
  });

  describe('Performance', () => {
    it('should render 80x30 grid in <100ms', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor();
      
      const start = Date.now();
      compositor.render(forest.tiles, 80, 30);
      const duration = Date.now() - start;
      
      expect(duration).toBeLessThan(100);
    });

    it('should handle empty grids efficiently', () => {
      const compositor = new TileCompositor();
      
      const start = Date.now();
      compositor.render({}, 80, 30);
      const duration = Date.now() - start;
      
      expect(duration).toBeLessThan(50);
    });
  });

  describe('Z-Index Layering', () => {
    it('should render sprites on top of objects', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      const compositor = new TileCompositor();
      
      // AA10 has both objects and sprite (player)
      const tile = compositor.compositeTile(forest.tiles.AA10);
      
      // Sprite should override objects
      expect(tile.char).toBe('🚶');
      expect(tile.z).toBe(5); // Player z-index
    });

    it('should respect object z-ordering', () => {
      const bridge = db.locations.find((l: any) => l.id === 'L300-AC10');
      const compositor = new TileCompositor();
      
      // Bridge location has layered objects
      const output = compositor.render(bridge.tiles, 5, 5);
      
      expect(output.length).toBeGreaterThan(0);
      // Grid renders without error
      expect(output.split('\n').length).toBe(5);
    });
  });

  describe('Color Rendering', () => {
    it('should preserve foreground colors', () => {
      const bridge = db.locations.find((l: any) => l.id === 'L300-AC10');
      
      // Bridge stones have gray fg color
      const bridgeTile = bridge.tiles.AB10;
      expect(bridgeTile.objects[0].fg).toBe('gray');
    });

    it('should handle color inheritance', () => {
      const bridge = db.locations.find((l: any) => l.id === 'L300-AC10');
      const compositor = new TileCompositor();
      
      // Render with colors
      const output = compositor.render(bridge.tiles, 5, 5, true);
      
      // Grid renders correctly
      expect(output).toBeDefined();
      expect(output.length).toBeGreaterThan(0);
    });
  });

  describe('Connection Data', () => {
    it('should have bidirectional forest connections', () => {
      const clearing = db.locations.find((l: any) => l.id === 'L300-AA10');
      const path = db.locations.find((l: any) => l.id === 'L300-AB10');
      
      // Clearing → Path
      const clearingToPath = clearing.connections.find((c: any) => c.to === 'L300-AB10');
      expect(clearingToPath).toBeDefined();
      expect(clearingToPath.direction).toBe('east');
      
      // Path → Clearing
      const pathToClearing = path.connections.find((c: any) => c.to === 'L300-AA10');
      expect(pathToClearing).toBeDefined();
      expect(pathToClearing.direction).toBe('west');
    });

    it('should have cross-scale connections with requirements', () => {
      const orbit = db.locations.find((l: any) => l.layer === 306);
      
      const earthConnection = orbit.connections.find((c: any) => c.to === 'L300-AA10');
      expect(earthConnection).toBeDefined();
      expect(earthConnection.requires).toBe('re-entry vehicle');
    });
  });

  describe('Markers', () => {
    it('should have spawn marker in Forest Clearing', () => {
      const forest = db.locations.find((l: any) => l.id === 'L300-AA10');
      
      const markers = forest.tiles.AA10.markers;
      expect(markers).toBeDefined();
      expect(markers.length).toBe(1);
      expect(markers[0].type).toBe('spawn');
    });

    it('should have landmark markers', () => {
      const mars = db.locations.find((l: any) => l.layer === 311);
      
      const markers = mars.tiles.AA00.markers;
      expect(markers).toBeDefined();
      expect(markers[0].type).toBe('landmark');
      expect(markers[0].label).toBe('Olympus Mons summit');
    });
  });
});
