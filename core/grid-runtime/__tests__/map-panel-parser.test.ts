/**
 * Tests for MAP/PANEL Block Parser
 */

import {
  parseMapBlock,
  parsePanelBlock,
  extractGridBlocks,
  GridBlockExecutor,
  MapBlock,
  PanelBlock,
} from '../src/map-panel-parser';
import { World, loadLocationDatabase } from '../src/location-loader';
import { LocationDatabase } from '../src/location-types';
import { RenderQuality } from '../src/sextant-renderer';

// Mock location data for testing
const mockLocationData: LocationDatabase = {
  version: '1.0.7.0',
  locations: {
    'L300-AA10': {
      id: 'L300-AA10',
      layer: 300,
      center: 'AA10',
      metadata: {
        name: 'Test Location',
        description: 'Test description',
        type: 'test',
      },
      connections: [],
      tiles: {
        'AA10': {
          objects: [{ char: '🏛️', label: 'Building', z: 0 }],
        },
        'BD14': {
          sprites: [{ id: 'player', char: '@', label: 'Player', z: 1 }],
        },
      },
    },
  },
};

describe('Block Parser', () => {
  
  describe('parseMapBlock', () => {
    it('should parse minimal MAP block', () => {
      const block = parseMapBlock('```map');
      expect(block.type).toBe('map');
      expect(block.location).toBeUndefined();
    });
    
    it('should parse MAP with location', () => {
      const block = parseMapBlock('```map L300-AA10');
      expect(block.type).toBe('map');
      expect(block.location).toBe('L300-AA10');
    });
    
    it('should parse MAP with size', () => {
      const block = parseMapBlock('```map L300-AA10 40x15');
      expect(block.size).toEqual({ width: 40, height: 15 });
    });
    
    it('should parse MAP with center override', () => {
      const block = parseMapBlock('```map L300-AA10 center=BD14');
      expect(block.center).toBe('BD14');
    });
    
    it('should parse MAP with quality', () => {
      const block = parseMapBlock('```map L300-AA10 quality=sextant');
      expect(block.quality).toBe(RenderQuality.SEXTANT);
    });
    
    it('should parse MAP with boolean flags', () => {
      const block = parseMapBlock('```map L300-AA10 coords layer');
      expect(block.showCoords).toBe(true);
      expect(block.showLayer).toBe(true);
    });
    
    it('should parse MAP with all options', () => {
      const block = parseMapBlock('```map L300-AA10 80x30 center=BD14 quality=quadrant coords layer');
      expect(block.location).toBe('L300-AA10');
      expect(block.size).toEqual({ width: 80, height: 30 });
      expect(block.center).toBe('BD14');
      expect(block.quality).toBe(RenderQuality.QUADRANT);
      expect(block.showCoords).toBe(true);
      expect(block.showLayer).toBe(true);
    });
  });
  
  describe('parsePanelBlock', () => {
    it('should parse minimal PANEL block', () => {
      const block = parsePanelBlock('```panel');
      expect(block.type).toBe('panel');
      expect(block.location).toBeUndefined();
    });
    
    it('should parse PANEL with location', () => {
      const block = parsePanelBlock('```panel L300-AA10');
      expect(block.type).toBe('panel');
      expect(block.location).toBe('L300-AA10');
    });
    
    it('should parse PANEL with region', () => {
      const block = parsePanelBlock('```panel L300-AA10 AA10:BD14');
      expect(block.region).toBe('AA10:BD14');
    });
    
    it('should parse PANEL with quality', () => {
      const block = parsePanelBlock('```panel L300-AA10 quality=shade');
      expect(block.quality).toBe(RenderQuality.SHADE);
    });
    
    it('should parse PANEL with grid flag', () => {
      const block = parsePanelBlock('```panel L300-AA10 grid');
      expect(block.showGrid).toBe(true);
    });
    
    it('should parse PANEL with all options', () => {
      const block = parsePanelBlock('```panel L300-AA10 AA10:BD14 quality=ascii grid');
      expect(block.location).toBe('L300-AA10');
      expect(block.region).toBe('AA10:BD14');
      expect(block.quality).toBe(RenderQuality.ASCII);
      expect(block.showGrid).toBe(true);
    });
  });
  
  describe('extractGridBlocks', () => {
    it('should extract MAP blocks from markdown', () => {
      const markdown = `
# Test Document

Some text here.

\`\`\`map L300-AA10
\`\`\`

More text.

\`\`\`map L300-BD14 40x15 coords
\`\`\`
`;
      
      const blocks = extractGridBlocks(markdown);
      expect(blocks.length).toBe(2);
      expect(blocks[0].type).toBe('map');
      expect((blocks[0] as MapBlock).location).toBe('L300-AA10');
      expect(blocks[1].type).toBe('map');
      expect((blocks[1] as MapBlock).location).toBe('L300-BD14');
    });
    
    it('should extract PANEL blocks from markdown', () => {
      const markdown = `
\`\`\`panel L300-AA10 AA10:BD14
\`\`\`

\`\`\`panel L300-BD14 grid
\`\`\`
`;
      
      const blocks = extractGridBlocks(markdown);
      expect(blocks.length).toBe(2);
      expect(blocks[0].type).toBe('panel');
      expect((blocks[0] as PanelBlock).region).toBe('AA10:BD14');
      expect(blocks[1].type).toBe('panel');
      expect((blocks[1] as PanelBlock).showGrid).toBe(true);
    });
    
    it('should extract mixed MAP and PANEL blocks', () => {
      const markdown = `
\`\`\`map L300-AA10
\`\`\`

\`\`\`panel L300-BD14
\`\`\`

\`\`\`map L300-CC20 40x15
\`\`\`
`;
      
      const blocks = extractGridBlocks(markdown);
      expect(blocks.length).toBe(3);
      expect(blocks[0].type).toBe('map');
      expect(blocks[1].type).toBe('panel');
      expect(blocks[2].type).toBe('map');
    });
    
    it('should ignore non-grid code blocks', () => {
      const markdown = `
\`\`\`javascript
const x = 1;
\`\`\`

\`\`\`map L300-AA10
\`\`\`

\`\`\`python
print("hello")
\`\`\`
`;
      
      const blocks = extractGridBlocks(markdown);
      expect(blocks.length).toBe(1);
      expect(blocks[0].type).toBe('map');
    });
    
    it('should handle empty markdown', () => {
      const blocks = extractGridBlocks('');
      expect(blocks.length).toBe(0);
    });
  });
  
  describe('GridBlockExecutor', () => {
    let world: World;
    let executor: GridBlockExecutor;
    
    beforeEach(() => {
      world = loadLocationDatabase(mockLocationData);
      executor = new GridBlockExecutor(world);
    });
    
    it('should execute MAP block with location', () => {
      const block: MapBlock = {
        type: 'map',
        location: 'L300-AA10',
        showLayer: true, // Enable header to see location name
      };
      
      const output = executor.executeMapBlock(block);
      expect(output).toContain('Test Location');
    });
    
    it('should show error for MAP without location', () => {
      const block: MapBlock = {
        type: 'map',
      };
      
      const output = executor.executeMapBlock(block);
      expect(output).toContain('⚠️');
      expect(output).toContain('requires location');
    });
    
    it('should show error for invalid location', () => {
      const block: MapBlock = {
        type: 'map',
        location: 'L999-XX99',
      };
      
      const output = executor.executeMapBlock(block);
      expect(output).toContain('⚠️');
      expect(output).toContain('not found');
    });
    
    it('should respect size parameter', () => {
      const block: MapBlock = {
        type: 'map',
        location: 'L300-AA10',
        size: { width: 40, height: 15 },
        showCoords: true,
      };
      
      const output = executor.executeMapBlock(block);
      expect(output).toContain('40×15');
    });
    
    it('should show layer indicator when requested', () => {
      const block: MapBlock = {
        type: 'map',
        location: 'L300-AA10',
        showLayer: true,
      };
      
      const output = executor.executeMapBlock(block);
      expect(output).toContain('Terrestrial');
    });
    
    it('should execute PANEL block with location', () => {
      const block: PanelBlock = {
        type: 'panel',
        location: 'L300-AA10',
        region: 'AA10:BD14',
      };
      
      const output = executor.executePanelBlock(block);
      expect(output).toContain('Test Location');
      expect(output).toContain('[AA10:BD14]');
    });
    
    it('should show error for PANEL without location', () => {
      const block: PanelBlock = {
        type: 'panel',
      };
      
      const output = executor.executePanelBlock(block);
      expect(output).toContain('⚠️');
      expect(output).toContain('requires location');
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle malformed MAP syntax', () => {
      const block = parseMapBlock('```map invalid-id');
      expect(block.location).toBeUndefined();
    });
    
    it('should handle malformed PANEL syntax', () => {
      const block = parsePanelBlock('```panel invalid:region');
      expect(block.region).toBeUndefined();
    });
    
    it('should handle extra whitespace', () => {
      const block = parseMapBlock('```map   L300-AA10   80x30   coords  ');
      expect(block.location).toBe('L300-AA10');
      expect(block.size).toEqual({ width: 80, height: 30 });
      expect(block.showCoords).toBe(true);
    });
  });
  
});
