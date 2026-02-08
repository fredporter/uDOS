/**
 * Tests for Teletext Renderer (Unicode block graphics)
 */

import {
  TELETEXT_CHARS,
  ASCII_BLOCK_CHARS,
  SHADE_CHARS,
  ASCII_CHARS,
  PixelGrid,
  pixelGridToIndex,
  indexToPixelGrid,
  pixelGridToTeletext,
  pixelGridToAsciiBlock,
  pixelGridToShade,
  pixelGridToASCII,
  RenderQuality,
  renderPixelGrid,
  detectTeletextSupport,
  getRecommendedQuality,
  createEmptyGrid,
  createFullGrid,
  mergeGrids,
  invertGrid,
} from '../src/teletext-renderer';

describe('Teletext Renderer', () => {
  
  describe('Character Lookups', () => {
    it('should have 64 teletext characters', () => {
      expect(TELETEXT_CHARS.length).toBe(64);
    });
    
    it('should have 16 asciiBlock characters', () => {
      expect(ASCII_BLOCK_CHARS.length).toBe(16);
    });
    
    it('should have 5 shade characters', () => {
      expect(SHADE_CHARS.length).toBe(5);
    });
    
    it('should have 5 ASCII characters', () => {
      expect(ASCII_CHARS.length).toBe(5);
    });
    
    it('should start with empty character', () => {
      expect(TELETEXT_CHARS[0]).toBe(' ');
      expect(ASCII_BLOCK_CHARS[0]).toBe(' ');
      expect(SHADE_CHARS[0]).toBe(' ');
      expect(ASCII_CHARS[0]).toBe(' ');
    });
    
    it('should end with full block', () => {
      expect(TELETEXT_CHARS[63]).toBe('█');
      expect(ASCII_BLOCK_CHARS[15]).toBe('█');
      expect(SHADE_CHARS[4]).toBe('█');
    });
  });
  
  describe('Pixel Grid Index Conversion', () => {
    it('should convert empty grid to index 0', () => {
      const grid: PixelGrid = {
        topLeft: false,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      };
      expect(pixelGridToIndex(grid)).toBe(0);
    });
    
    it('should convert full grid to index 63', () => {
      const grid: PixelGrid = {
        topLeft: true,
        topRight: true,
        middleLeft: true,
        middleRight: true,
        bottomLeft: true,
        bottomRight: true,
      };
      expect(pixelGridToIndex(grid)).toBe(63);
    });
    
    it('should convert single pixel patterns', () => {
      // Top-left only: bit 5 (32)
      expect(pixelGridToIndex({
        topLeft: true,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      })).toBe(32);
      
      // Bottom-right only: bit 0 (1)
      expect(pixelGridToIndex({
        topLeft: false,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: true,
      })).toBe(1);
    });
    
    it('should convert index back to grid', () => {
      const grid = indexToPixelGrid(42);
      const index = pixelGridToIndex(grid);
      expect(index).toBe(42);
    });
    
    it('should throw on invalid index', () => {
      expect(() => indexToPixelGrid(-1)).toThrow();
      expect(() => indexToPixelGrid(64)).toThrow();
    });
  });
  
  describe('Teletext Rendering', () => {
    it('should render empty grid as space', () => {
      const grid = createEmptyGrid();
      expect(pixelGridToTeletext(grid)).toBe(' ');
    });
    
    it('should render full grid as full block', () => {
      const grid = createFullGrid();
      expect(pixelGridToTeletext(grid)).toBe('█');
    });
    
    it('should render top half pattern', () => {
      const grid: PixelGrid = {
        topLeft: true,
        topRight: true,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      };
      const char = pixelGridToTeletext(grid);
      expect(char).toBeTruthy();
      expect(char).not.toBe(' ');
      expect(char).not.toBe('█');
    });
  });
  
  describe('AsciiBlock Rendering', () => {
    it('should render empty grid as space', () => {
      const grid = createEmptyGrid();
      expect(pixelGridToAsciiBlock(grid)).toBe(' ');
    });
    
    it('should render top row as half block', () => {
      const grid: PixelGrid = {
        topLeft: true,
        topRight: true,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      };
      expect(pixelGridToAsciiBlock(grid)).toBe('▀');
    });
    
    it('should use only top 2 rows', () => {
      // Bottom row should be ignored
      const grid: PixelGrid = {
        topLeft: true,
        topRight: true,
        middleLeft: false,
        middleRight: false,
        bottomLeft: true, // Ignored
        bottomRight: true, // Ignored
      };
      expect(pixelGridToAsciiBlock(grid)).toBe('▀');
    });
  });
  
  describe('Shade Rendering', () => {
    it('should render by density', () => {
      expect(pixelGridToShade(createEmptyGrid())).toBe(' ');
      
      // 1 pixel = light shade
      expect(pixelGridToShade({
        topLeft: true,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      })).toBe('░');
      
      // 3 pixels = medium shade
      expect(pixelGridToShade({
        topLeft: true,
        topRight: true,
        middleLeft: true,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      })).toBe('▒');
      
      // 5 pixels = dark shade
      expect(pixelGridToShade({
        topLeft: true,
        topRight: true,
        middleLeft: true,
        middleRight: true,
        bottomLeft: true,
        bottomRight: false,
      })).toBe('▓');
      
      expect(pixelGridToShade(createFullGrid())).toBe('█');
    });
  });
  
  describe('ASCII Rendering', () => {
    it('should render by density', () => {
      expect(pixelGridToASCII(createEmptyGrid())).toBe(' ');
      
      // 1 pixel = light
      expect(pixelGridToASCII({
        topLeft: true,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      })).toBe('.');
      
      // 3 pixels = medium
      expect(pixelGridToASCII({
        topLeft: true,
        topRight: true,
        middleLeft: true,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      })).toBe(':');
      
      // 5 pixels = dense
      expect(pixelGridToASCII({
        topLeft: true,
        topRight: true,
        middleLeft: true,
        middleRight: true,
        bottomLeft: true,
        bottomRight: false,
      })).toBe('#');
      
      expect(pixelGridToASCII(createFullGrid())).toBe('@');
    });
  });
  
  describe('Quality Levels', () => {
    it('should render with specified quality', () => {
      const grid = createFullGrid();
      
      expect(renderPixelGrid(grid, RenderQuality.TELETEXT)).toBe('█');
      expect(renderPixelGrid(grid, RenderQuality.ASCII_BLOCK)).toBe('█');
      expect(renderPixelGrid(grid, RenderQuality.SHADE)).toBe('█');
      expect(renderPixelGrid(grid, RenderQuality.ASCII)).toBe('@');
    });
    
    it('should default to teletext quality', () => {
      const grid = createFullGrid();
      expect(renderPixelGrid(grid)).toBe('█');
    });
    
    it('should detect teletext support', () => {
      const supported = detectTeletextSupport();
      expect(typeof supported).toBe('boolean');
    });
    
    it('should recommend quality level', () => {
      const quality = getRecommendedQuality();
      expect([
        RenderQuality.TELETEXT,
        RenderQuality.ASCII_BLOCK,
      ]).toContain(quality);
    });
  });
  
  describe('Grid Utilities', () => {
    it('should create empty grid', () => {
      const grid = createEmptyGrid();
      expect(pixelGridToIndex(grid)).toBe(0);
    });
    
    it('should create full grid', () => {
      const grid = createFullGrid();
      expect(pixelGridToIndex(grid)).toBe(63);
    });
    
    it('should merge grids', () => {
      const a: PixelGrid = {
        topLeft: true,
        topRight: false,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      };
      
      const b: PixelGrid = {
        topLeft: false,
        topRight: true,
        middleLeft: false,
        middleRight: false,
        bottomLeft: false,
        bottomRight: false,
      };
      
      const merged = mergeGrids(a, b);
      expect(merged.topLeft).toBe(true);
      expect(merged.topRight).toBe(true);
    });
    
    it('should invert grid', () => {
      const grid = createEmptyGrid();
      const inverted = invertGrid(grid);
      expect(pixelGridToIndex(inverted)).toBe(63);
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle all 64 teletext patterns', () => {
      for (let i = 0; i < 64; i++) {
        const grid = indexToPixelGrid(i);
        const char = pixelGridToTeletext(grid);
        expect(char).toBeTruthy();
        expect(TELETEXT_CHARS[i]).toBe(char);
      }
    });
    
    it('should be reversible', () => {
      const original: PixelGrid = {
        topLeft: true,
        topRight: false,
        middleLeft: true,
        middleRight: false,
        bottomLeft: true,
        bottomRight: false,
      };
      
      const index = pixelGridToIndex(original);
      const recovered = indexToPixelGrid(index);
      
      expect(recovered).toEqual(original);
    });
  });
  
});
