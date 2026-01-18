/**
 * Tests for Tile Compositor
 */

import {
  compositeTile,
  compositeGrid,
  renderGridToString,
  renderGridWithColors,
  TileCompositor,
  CompositorOptions,
} from '../src/tile-compositor';
import { TileContent, TileObject, TileSprite } from '../src/location-types';
import { RenderQuality } from '../src/sextant-renderer';

describe('Tile Compositor', () => {
  describe('compositeTile', () => {
    it('should render empty tile', () => {
      const result = compositeTile(undefined);
      expect(result.char).toBe(' ');
      expect(result.z).toBe(0);
    });

    it('should render tile with terrain', () => {
      const result = compositeTile(undefined, {
        showTerrain: true,
        defaultTerrain: '.',
      });
      expect(result.char).toBe('.');
      expect(result.z).toBe(0);
    });

    it('should render single object', () => {
      const content: TileContent = {
        objects: [
          { id: 'tree', char: '🌲', z: 1 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Should render as sextant character (full grid)
      expect(result.char).not.toBe(' ');
      expect(result.z).toBe(1);
    });

    it('should render sprite override', () => {
      const content: TileContent = {
        objects: [
          { id: 'grass', char: '🌿', z: 0 },
        ],
        sprites: [
          { id: 'player', char: '🚶', z: 5, state: 'idle' },
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
          { id: 'npc', char: '👤', z: 2, state: 'idle' },
          { id: 'player', char: '🚶', z: 5, state: 'idle' },
          { id: 'item', char: '💎', z: 3, state: 'visible' },
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
          { id: 'ground', char: '░', z: 0 },
          { id: 'wall', char: '▓', z: 1 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Should merge into sextant character
      expect(result.char).not.toBe(' ');
      expect(result.z).toBe(1); // Topmost object z-index
    });

    it('should preserve styling from topmost object', () => {
      const content: TileContent = {
        objects: [
          { id: 'ground', char: '░', z: 0, fg: 'green' },
          { id: 'wall', char: '▓', z: 1, fg: 'gray', bg: 'black' },
        ],
      };
      
      const result = compositeTile(content);
      
      expect(result.fg).toBe('gray');
      expect(result.bg).toBe('black');
    });

    it('should preserve styling from sprite', () => {
      const content: TileContent = {
        objects: [
          { id: 'ground', char: '░', z: 0, fg: 'green' },
        ],
        sprites: [
          { id: 'player', char: '🚶', z: 5, state: 'idle', fg: 'yellow' },
        ],
      };
      
      const result = compositeTile(content);
      
      expect(result.fg).toBe('yellow');
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
        'AA00': { objects: [{ id: 'tree', char: '🌲', z: 1 }] },
        'AB01': { sprites: [{ id: 'player', char: '🚶', z: 5, state: 'idle' }] },
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
        'DC00': { sprites: [{ id: 'edge', char: '|', z: 1, state: 'visible' }] },
      };
      
      const grid = compositeGrid(tiles, 80, 30);
      
      // DC = column 79 (last column)
      expect(grid[0][79].char).toBe('|');
    });

    it('should ignore out-of-bounds tiles', () => {
      const tiles: Record<string, TileContent> = {
        'ZZ99': { objects: [{ id: 'invalid', char: '?', z: 1 }] },
      };
      
      const grid = compositeGrid(tiles, 80, 30);
      
      // Should not crash, grid should be empty
      expect(grid[0][0].char).toBe(' ');
    });
  });

  describe('renderGridToString', () => {
    it('should render grid to string', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: 'a', char: 'A', z: 1, state: 'visible' }] },
        'AB00': { sprites: [{ id: 'b', char: 'B', z: 1, state: 'visible' }] },
        'AC00': { sprites: [{ id: 'c', char: 'C', z: 1, state: 'visible' }] },
      };
      
      const grid = compositeGrid(tiles, 5, 1);
      const output = renderGridToString(grid);
      
      expect(output).toBe('ABC  ');
    });

    it('should render multi-line grid', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: '1', char: '1', z: 1, state: 'visible' }] },
        'AA01': { sprites: [{ id: '2', char: '2', z: 1, state: 'visible' }] },
        'AA02': { sprites: [{ id: '3', char: '3', z: 1, state: 'visible' }] },
      };
      
      const grid = compositeGrid(tiles, 3, 3);
      const output = renderGridToString(grid);
      
      expect(output).toContain('1  \n2  \n3  ');
    });
  });

  describe('renderGridWithColors', () => {
    it('should render with ANSI colors', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': {
          sprites: [{
            id: 'red-dot', label: 'red-dot',
            char: '•',
            z: 1,
            state: 'visible',
            fg: 'red',
          }],
        },
      };
      
      const grid = compositeGrid(tiles, 3, 1);
      const output = renderGridWithColors(grid);
      
      // Should contain ANSI color code
      expect(output).toContain('\x1b[3'); // Foreground color code
      expect(output).toContain('•');
    });

    it('should render with background color', () => {
      const tiles: Record<string, TileContent> = {
        'AA00': {
          sprites: [{
            id: 'highlight', label: 'highlight',
            char: 'X',
            z: 1,
            state: 'visible',
            bg: 'yellow',
          }],
        },
      };
      
      const grid = compositeGrid(tiles, 3, 1);
      const output = renderGridWithColors(grid);
      
      // Should contain background color code
      expect(output).toContain('\x1b[4'); // Background color code
      expect(output).toContain('X');
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
        objects: [{ id: 'wall', char: '█', z: 1 }],
      };
      
      const result = compositor.compositeTile(content);
      
      // ASCII quality should use simple characters
      expect(result.char).toMatch(/[#X ]/);
    });

    it('should composite grid with options', () => {
      const compositor = new TileCompositor({
        showTerrain: true,
        defaultTerrain: '·',
      });
      
      const tiles: Record<string, TileContent> = {
        'AA00': { sprites: [{ id: 'player', char: '🚶', z: 5, state: 'idle' }] },
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
        'AA00': { sprites: [{ id: 'a', char: 'A', z: 1, state: 'visible' }] },
        'AB00': { sprites: [{ id: 'b', char: 'B', z: 1, state: 'visible' }] },
      };
      
      const output = compositor.render(tiles, 5, 1);
      
      expect(output).toBe('AB   ');
    });

    it('should render with colors', () => {
      const compositor = new TileCompositor();
      
      const tiles: Record<string, TileContent> = {
        'AA00': {
          sprites: [{
            id: 'red-dot', label: 'red-dot',
            char: '•',
            z: 1,
            state: 'visible',
            fg: 'red',
          }],
        },
      };
      
      const output = compositor.render(tiles, 3, 1, true);
      
      expect(output).toContain('\x1b['); // ANSI escape code
      expect(output).toContain('•');
    });
  });

  describe('Z-index sorting', () => {
    it('should respect z-index for objects', () => {
      const content: TileContent = {
        objects: [
          { id: 'top', char: 'T', z: 10 },
          { id: 'bottom', char: 'B', z: 1 },
          { id: 'middle', char: 'M', z: 5 },
        ],
      };
      
      const result = compositeTile(content);
      
      // Styling should come from highest z (top)
      expect(result.z).toBe(10);
    });

    it('should respect z-index for sprites', () => {
      const content: TileContent = {
        sprites: [
          { id: 'a', char: 'A', z: 1, state: 'visible' },
          { id: 'b', char: 'B', z: 10, state: 'visible' },
          { id: 'c', char: 'C', z: 5, state: 'visible' },
        ],
      };
      
      const result = compositeTile(content);
      
      // Highest z-index sprite (B) should win
      expect(result.char).toBe('B');
      expect(result.z).toBe(10);
    });

    it('should handle missing z-index (default to 0)', () => {
      const content: TileContent = {
        objects: [
          { id: 'no-z', char: '?'  }, // No z specified
        ],
      };
      
      const result = compositeTile(content);
      
      expect(result.z).toBe(0);
    });
  });

  describe('Quality levels', () => {
    const content: TileContent = {
      objects: [{ id: 'test', char: '█', z: 1 }],
    };

    it('should render with sextant quality', () => {
      const result = compositeTile(content, { quality: RenderQuality.SEXTANT });
      
