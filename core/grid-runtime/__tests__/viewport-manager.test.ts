/**
 * Tests for ViewportManager (v1.0.7.0)
 */

import {
  ViewportManager,
  colIndexToCell,
  cellToColIndex,
  parseCellAddress,
  formatCellAddress,
  formatLocationId,
  GRID_COLS,
  GRID_ROWS,
  ROW_OFFSET,
  STANDARD_VIEWPORT,
  MINI_VIEWPORT,
  type GridPosition,
  type Sprite
} from '../src/viewport-manager';

describe('Coordinate Conversion', () => {
  describe('colIndexToCell', () => {
    it('should convert column indices to cell format', () => {
      expect(colIndexToCell(0)).toBe('AA');
      expect(colIndexToCell(1)).toBe('AB');
      expect(colIndexToCell(25)).toBe('AZ');
      expect(colIndexToCell(26)).toBe('BA');
      expect(colIndexToCell(79)).toBe('DC');
    });
    
    it('should throw on invalid indices', () => {
      expect(() => colIndexToCell(-1)).toThrow();
      expect(() => colIndexToCell(80)).toThrow();
    });
  });
  
  describe('cellToColIndex', () => {
    it('should convert cell format to column indices', () => {
      expect(cellToColIndex('AA')).toBe(0);
      expect(cellToColIndex('AB')).toBe(1);
      expect(cellToColIndex('AZ')).toBe(25);
      expect(cellToColIndex('BA')).toBe(26);
      expect(cellToColIndex('DC')).toBe(79);
    });
    
    it('should throw on invalid cells', () => {
      expect(() => cellToColIndex('A')).toThrow();
      expect(() => cellToColIndex('ZZ')).toThrow();
    });
  });
  
  describe('parseCellAddress', () => {
    it('should parse valid cell addresses', () => {
      expect(parseCellAddress('AA10')).toEqual({ col: 0, row: 10 });
      expect(parseCellAddress('AM15')).toEqual({ col: 12, row: 15 });
      expect(parseCellAddress('DC39')).toEqual({ col: 79, row: 39 });
    });
    
    it('should throw on invalid formats', () => {
      expect(() => parseCellAddress('A10')).toThrow();
      expect(() => parseCellAddress('AAA10')).toThrow();
      expect(() => parseCellAddress('AA9')).toThrow();  // Row too low
      expect(() => parseCellAddress('AA40')).toThrow(); // Row too high
    });
  });
  
  describe('formatCellAddress', () => {
    it('should format positions to cell addresses', () => {
      expect(formatCellAddress(0, 10)).toBe('AA10');
      expect(formatCellAddress(12, 15)).toBe('AM15');
      expect(formatCellAddress(79, 39)).toBe('DC39');
    });
  });
  
  describe('formatLocationId', () => {
    it('should format full location IDs', () => {
      expect(formatLocationId(300, 0, 10)).toBe('L300-AA10');
      expect(formatLocationId(301, 12, 15)).toBe('L301-AM15');
      expect(formatLocationId(305, 79, 39)).toBe('L305-DC39');
    });
  });
});

describe('ViewportManager', () => {
  describe('Constructor', () => {
    it('should initialize with default center and size', () => {
      const vm = new ViewportManager();
      const state = vm.getState();
      
      expect(state.center.layer).toBe(300);
      expect(state.center.col).toBe(40);
      expect(state.center.row).toBe(20);
      expect(state.size.width).toBe(80);
      expect(state.size.height).toBe(30);
    });
    
    it('should initialize with custom center and size', () => {
      const center: GridPosition = { layer: 301, col: 10, row: 15 };
      const vm = new ViewportManager(center, MINI_VIEWPORT);
      const state = vm.getState();
      
      expect(state.center).toEqual(center);
      expect(state.size).toEqual(MINI_VIEWPORT);
    });
  });
  
  describe('Viewport Manipulation', () => {
    it('should set center position', () => {
      const vm = new ViewportManager();
      const newCenter: GridPosition = { layer: 300, col: 20, row: 25 };
      
      vm.setCenter(newCenter);
      expect(vm.getCenter()).toEqual(newCenter);
    });
    
    it('should move by delta', () => {
      const vm = new ViewportManager({ layer: 300, col: 40, row: 20 }, STANDARD_VIEWPORT);
      
      vm.moveBy(5, -3);
      const center = vm.getCenter();
      
      expect(center.col).toBe(45);
      expect(center.row).toBe(17);
    });
    
    it('should clamp movement to grid bounds', () => {
      const vm = new ViewportManager({ layer: 300, col: 2, row: 12 }, STANDARD_VIEWPORT);
      
      // Try to move left beyond boundary
      vm.moveBy(-10, 0);
      expect(vm.getCenter().col).toBe(0);
      
      // Try to move up beyond boundary
      vm.moveBy(0, -10);
      expect(vm.getCenter().row).toBe(10);
    });
    
    it('should change viewport size', () => {
      const vm = new ViewportManager();
      
      vm.setSize(MINI_VIEWPORT);
      expect(vm.getSize()).toEqual(MINI_VIEWPORT);
    });
    
    it('should change layer', () => {
      const vm = new ViewportManager();
      
      vm.setLayer(301);
      expect(vm.getCenter().layer).toBe(301);
    });
    
    it('should throw on invalid layer', () => {
      const vm = new ViewportManager();
      
      expect(() => vm.setLayer(299)).toThrow();
      expect(() => vm.setLayer(306)).toThrow();
    });
  });
  
  describe('Visibility Calculation', () => {
    it('should calculate visible tiles', () => {
      const center: GridPosition = { layer: 300, col: 40, row: 20 };
      const size = { width: 5, height: 3 };
      const vm = new ViewportManager(center, size);
      
      const tiles = vm.getVisibleTiles();
      
      // 5×3 = 15 tiles
      expect(tiles.length).toBe(15);
      
      // Check center tile is included
      const centerTile = tiles.find(t => t.cell === 'BO20');
      expect(centerTile).toBeDefined();
    });
    
    it('should check if position is visible', () => {
      const vm = new ViewportManager(
        { layer: 300, col: 40, row: 20 },
        { width: 10, height: 10 }
      );
      
      // Center should be visible
      expect(vm.isVisible({ layer: 300, col: 40, row: 20 })).toBe(true);
      
      // Adjacent should be visible
      expect(vm.isVisible({ layer: 300, col: 41, row: 20 })).toBe(true);
      expect(vm.isVisible({ layer: 300, col: 40, row: 21 })).toBe(true);
      
      // Far away should not be visible
      expect(vm.isVisible({ layer: 300, col: 0, row: 10 })).toBe(false);
      expect(vm.isVisible({ layer: 300, col: 79, row: 39 })).toBe(false);
      
      // Different layer should not be visible
      expect(vm.isVisible({ layer: 301, col: 40, row: 20 })).toBe(false);
    });
    
    it('should get screen coordinates for visible positions', () => {
      const vm = new ViewportManager(
        { layer: 300, col: 40, row: 20 },
        { width: 10, height: 10 }
      );
      
      // Center should be at screen center
      const centerCoords = vm.getScreenCoordinates({ layer: 300, col: 40, row: 20 });
      expect(centerCoords).toEqual({ x: 5, y: 5 });
      
      // Adjacent positions
      const rightCoords = vm.getScreenCoordinates({ layer: 300, col: 41, row: 20 });
      expect(rightCoords).toEqual({ x: 6, y: 5 });
      
      const downCoords = vm.getScreenCoordinates({ layer: 300, col: 40, row: 21 });
      expect(downCoords).toEqual({ x: 5, y: 6 });
      
      // Not visible should return null
      const farCoords = vm.getScreenCoordinates({ layer: 300, col: 0, row: 10 });
      expect(farCoords).toBeNull();
    });
  });
  
  describe('Sprite Management', () => {
    const sprites: Sprite[] = [
      {
        id: 'player',
        position: { layer: 300, col: 40, row: 20 },
        character: '@',
        zIndex: 100,
        kind: 'player'
      },
      {
        id: 'npc1',
        position: { layer: 300, col: 41, row: 20 },
        character: 'N',
        zIndex: 50,
        kind: 'npc'
      },
      {
        id: 'tree',
        position: { layer: 300, col: 0, row: 10 },
        character: 'T',
        zIndex: 10,
        kind: 'object'
      }
    ];
    
    it('should sort sprites by z-index', () => {
      const vm = new ViewportManager();
      const sorted = vm.sortSprites(sprites);
      
      expect(sorted[0].id).toBe('tree');   // zIndex 10
      expect(sorted[1].id).toBe('npc1');   // zIndex 50
      expect(sorted[2].id).toBe('player'); // zIndex 100
    });
    
    it('should filter visible sprites', () => {
      const vm = new ViewportManager(
        { layer: 300, col: 40, row: 20 },
        { width: 10, height: 10 }
      );
      
      const visible = vm.getVisibleSprites(sprites);
      
      expect(visible.length).toBe(2);
      expect(visible.find(s => s.id === 'player')).toBeDefined();
      expect(visible.find(s => s.id === 'npc1')).toBeDefined();
      expect(visible.find(s => s.id === 'tree')).toBeUndefined(); // Too far
    });
    
    it('should get sprites at specific position', () => {
      const vm = new ViewportManager();
      const atPos = vm.getSpritesAtPosition(sprites, { layer: 300, col: 40, row: 20 });
      
      expect(atPos.length).toBe(1);
      expect(atPos[0].id).toBe('player');
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle viewport at grid boundaries', () => {
      const vm = new ViewportManager(
        { layer: 300, col: 0, row: 10 },
        { width: 10, height: 10 }
      );
      
      expect(vm.isVisible({ layer: 300, col: 0, row: 10 })).toBe(true);
    });
    
    it('should handle mini viewport', () => {
      const vm = new ViewportManager(
        { layer: 300, col: 40, row: 20 },
        MINI_VIEWPORT
      );
      
      const tiles = vm.getVisibleTiles();
      // 40×15 viewport centered at (40,20) will show tiles within half-width/height
      // Actual calculation: (20 + 20 + 1) × (7 + 7 + 1) = 41 × 15 = 615
      expect(tiles.length).toBe(615);
    });
  });
});
