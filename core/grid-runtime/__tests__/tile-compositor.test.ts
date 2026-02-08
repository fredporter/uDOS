/**
 * Tests for Tile Compositor
 */

import {
  compositeTile,
  compositeGrid,
  renderGridToString,
  TileCompositor,
} from '../src/tile-compositor';
import { TileContent } from '../src/location-types';
import { RenderQuality } from '../src/teletext-renderer';

describe('Tile Compositor', () => {
  describe('compositeTile', () => {
    it('should render empty tile', () => {
      const result = compositeTile(undefined);
      expect(result.char).toBe(' ');
      expect(result.z).toBe(0);
    });

    it('should render single object', () => {
      const content: TileContent = {
        objects: [
          { char: '🌲', label: 'tree', z: 1 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Should render as teletext character (full grid)
      expect(result.char).not.toBe(' ');
      expect(result.z).toBe(1);
    });

    it('should render sprite override', () => {
      const content: TileContent = {
        objects: [
          { char: '🌿', label: 'grass', z: 0 },
        ],
        sprites: [
          { id: 'player', char: '🚶', label: 'player', z: 5 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Sprite always overrides objects
      expect(result.char).toBe('🚶');
      expect(result.z).toBe(5);
    });

    it('should use topmost sprite', () => {
      const content: TileContent = {
        sprites: [
          { id: 'npc', char: '👤', label: 'npc', z: 2 },
          { id: 'player', char: '🚶', label: 'player', z: 5 },
          { id: 'item', char: '💎', label: 'item', z: 3 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Highest z-index wins
      expect(result.char).toBe('🚶');
      expect(result.z).toBe(5);
    });

    it('should composite multiple objects', () => {
      const content: TileContent = {
        objects: [
          { char: '░', label: 'ground', z: 0 },
          { char: '▓', label: 'wall', z: 1 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Should merge into teletext character
      expect(result.char).not.toBe(' ');
      expect(result.z).toBe(1); // Topmost object z-index
    });

    it('should preserve styling from topmost object', () => {
      const content: TileContent = {
        objects: [
          { char: '░', label: 'ground', z: 0, fg: 'green' },
          { char: '▓', label: 'wall', z: 1, fg: 'gray', bg: 'black' },
        ],
      };
      
      const result = compositeTile(content);
      
      expect(result.fg).toBe('gray');
      expect(result.bg).toBe('black');
    });
  });

  describe('compositeGrid', () => {
    it('should render empty grid', () => {
      const grid = compositeGrid({}, 10, 5);
      
      expect(grid.length).toBe(5);
      expect(grid[0].length).toBe(10);
      expect(grid[0][0].char).toBe(' ');
    });

    it('should render grid with tiles', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': { objects: [{ char: '🌲', label: 'tree', z: 1 }] },
        'AB01': { sprites: [{ id: 'player', char: '🚶', label: 'player', z: 5 }] },
      };
      
      const grid = compositeGrid(tiles, 80, 30);
      
      // AA00 = col 0, row 0
      expect(grid[0][0].char).not.toBe(' ');
      
      // AB01 = col 1, row 1
      expect(grid[1][1].char).toBe('🚶');
      
      // Empty tile
      expect(grid[0][1].char).toBe(' ');
    });

    it('should handle DC column (79)', () => {
      const tiles: Record<string, TileContent> = {
        'DC00': { sprites: [{ id: 'edge', char: '|', label: 'edge', z: 1 }] },
      };
      
      const grid = compositeGrid(tiles, 80, 30);
      
      // DC = column 79 (last column)
      expect(grid[0][79].char).toBe('|');
    });
  });

  describe('renderGridToString', () => {
    it('should render grid to string', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: 'a', char: 'A', label: 'a', z: 1 }] },
        'AB00': { sprites: [{ id: 'b', char: 'B', label: 'b', z: 1 }] },
        'AC00': { sprites: [{ id: 'c', char: 'C', label: 'c', z: 1 }] },
      };
      
      const grid = compositeGrid(tiles, 5, 1);
      const output = renderGridToString(grid);
      
      expect(output).toBe('ABC  ');
    });
  });

  describe('TileCompositor class', () => {
    it('should initialize with default options', () => {
      const compositor = new TileCompositor();
      
      const result = compositor.compositeTile(undefined);
      expect(result.char).toBe(' ');
    });

    it('should allow setting quality', () => {
      const compositor = new TileCompositor();
      
      compositor.setQuality(RenderQuality.ASCII);
      
      const content: TileContent = {
        objects: [{ char: '█', label: 'wall', z: 1 }],
      };
      
      const result = compositor.compositeTile(content);
      
      // ASCII quality should use simple characters
      expect(result.char).toMatch(/[ .:#X@]/);
    });

    it('should composite grid with terrain option', () => {
      const compositor = new TileCompositor({
        showTerrain: true,
        defaultTerrain: '·',
      });
      
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: 'player', char: '🚶', label: 'player', z: 5 }] },
      };
      
      const grid = compositor.compositeGrid(tiles, 3, 1);
      
      // Player tile
      expect(grid[0][0].char).toBe('🚶');
      
      // Terrain should show on empty tiles
      expect(grid[0][1].char).toBe('·');
    });

    it('should render to string', () => {
      const compositor = new TileCompositor();
      
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: 'a', char: 'A', label: 'a', z: 1 }] },
        'AB00': { sprites: [{ id: 'b', char: 'B', label: 'b', z: 1 }] },
      };
      
      const output = compositor.render(tiles, 5, 1);
      
      expect(output).toBe('AB   ');
    });
  });

  describe('Z-index sorting', () => {
    it('should respect z-index for objects', () => {
      const content: TileContent = {
        objects: [
          { char: 'T', label: 'top', z: 10 },
          { char: 'B', label: 'bottom', z: 1 },
          { char: 'M', label: 'middle', z: 5 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Styling should come from highest z (top)
      expect(result.z).toBe(10);
    });

    it('should respect z-index for sprites', () => {
      const content: TileContent = {
        sprites: [
          { id: 'a', char: 'A', label: 'a', z: 1 },
          { id: 'b', char: 'B', label: 'b', z: 10 },
          { id: 'c', char: 'C', label: 'c', z: 5 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Highest z-index sprite (B) should win
      expect(result.char).toBe('B');
      expect(result.z).toBe(10);
    });
  });

  describe('Quality levels', () => {
    const content: TileContent = {
      objects: [{ char: '█', label: 'test', z: 1 }],
    };

    it('should render with teletext quality', () => {
      const result = compositeTile(content, { quality: RenderQuality.TELETEXT });
      
      // Should be teletext character (full grid = █)
      expect(result.char).toBe('█');
    });

    it('should render with ASCII quality', () => {
      const result = compositeTile(content, { quality: RenderQuality.ASCII });
      
      // Should be ASCII character
      expect(result.char).toMatch(/[ .:#X@]/);
    });
  });
});
