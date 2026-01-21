/**
 * MAP/PANEL Block Parser - Extract and parse grid runtime blocks from markdown
 * 
 * Parses ```map and ```panel code blocks with location/viewport syntax
 * Integrates with ViewportManager, World, and Sextant Renderer
 * 
 * @module grid-runtime/block-parser
 */

import { ViewportManager, ViewportSize } from './viewport-manager';
import { World } from './location-loader';
import { RenderQuality } from './sextant-renderer';

/**
 * MAP block configuration
 */
export interface MapBlock {
  type: 'map';
  /** Target location ID (e.g., "L300-AA10") */
  location?: string;
  /** Viewport size (80×30 or 40×15) */
  size?: ViewportSize;
  /** Center cell override */
  center?: string;
  /** Render quality level */
  quality?: RenderQuality;
  /** Show coordinate labels */
  showCoords?: boolean;
  /** Show layer indicator */
  showLayer?: boolean;
}

/**
 * PANEL block configuration  
 */
export interface PanelBlock {
  type: 'panel';
  /** Target location ID */
  location?: string;
  /** Panel region (e.g., "AA10:BD14") */
  region?: string;
  /** Render quality level */
  quality?: RenderQuality;
  /** Show grid lines */
  showGrid?: boolean;
}

/**
 * Generic grid block (MAP or PANEL)
 */
export type GridBlock = MapBlock | PanelBlock;

/**
 * Parse MAP block header
 * Format: ```map [location] [size] [options]
 * 
 * Examples:
 *   ```map L300-AA10
 *   ```map L300-AA10 40x15
 *   ```map L300-AA10 center=BD14
 *   ```map L300-AA10 quality=sextant coords
 */
export function parseMapBlock(headerLine: string): MapBlock {
  const block: MapBlock = { type: 'map' };
  
  // Remove ```map prefix
  const args = headerLine.replace(/^```map\s*/, '').trim();
  if (!args) return block;
  
  const tokens = args.split(/\s+/);
  
  for (const token of tokens) {
    // Location ID (L###-CELL format)
    if (/^L\d+-[A-Z]{2}\d+$/.test(token)) {
      block.location = token;
      continue;
    }
    
    // Viewport size (80x30 or 40x15)
    if (/^\d+x\d+$/.test(token)) {
      const [width, height] = token.split('x').map(Number);
      block.size = { width, height };
      continue;
    }
    
    // Key=value options
    if (token.includes('=')) {
      const [key, value] = token.split('=');
      
      switch (key.toLowerCase()) {
        case 'center':
          block.center = value;
          break;
        case 'quality':
          block.quality = value as RenderQuality;
          break;
        case 'coords':
          block.showCoords = value === 'true';
          break;
        case 'layer':
          block.showLayer = value === 'true';
          break;
      }
      continue;
    }
    
    // Boolean flags
    switch (token.toLowerCase()) {
      case 'coords':
        block.showCoords = true;
        break;
      case 'layer':
        block.showLayer = true;
        break;
    }
  }
  
  return block;
}

/**
 * Parse PANEL block header
 * Format: ```panel [location] [region] [options]
 * 
 * Examples:
 *   ```panel L300-AA10
 *   ```panel L300-AA10 AA10:BD14
 *   ```panel L300-AA10 quality=quadrant grid
 */
export function parsePanelBlock(headerLine: string): PanelBlock {
  const block: PanelBlock = { type: 'panel' };
  
  // Remove ```panel prefix
  const args = headerLine.replace(/^```panel\s*/, '').trim();
  if (!args) return block;
  
  const tokens = args.split(/\s+/);
  
  for (const token of tokens) {
    // Location ID
    if (/^L\d+-[A-Z]{2}\d+$/.test(token)) {
      block.location = token;
      continue;
    }
    
    // Region (AA10:BD14 format)
    if (/^[A-Z]{2}\d+:[A-Z]{2}\d+$/.test(token)) {
      block.region = token;
      continue;
    }
    
    // Key=value options
    if (token.includes('=')) {
      const [key, value] = token.split('=');
      
      switch (key.toLowerCase()) {
        case 'quality':
          block.quality = value as RenderQuality;
          break;
        case 'grid':
          block.showGrid = value === 'true';
          break;
      }
      continue;
    }
    
    // Boolean flags
    if (token.toLowerCase() === 'grid') {
      block.showGrid = true;
    }
  }
  
  return block;
}

/**
 * Extract all grid blocks from markdown content
 * @param markdown - Full markdown document
 * @returns Array of parsed grid blocks
 */
export function extractGridBlocks(markdown: string): GridBlock[] {
  const blocks: GridBlock[] = [];
  const lines = markdown.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Detect MAP block
    if (line.startsWith('```map')) {
      blocks.push(parseMapBlock(line));
      continue;
    }
    
    // Detect PANEL block
    if (line.startsWith('```panel')) {
      blocks.push(parsePanelBlock(line));
      continue;
    }
  }
  
  return blocks;
}

/**
 * Grid block executor - renders blocks using viewport + world
 */
export class GridBlockExecutor {
  private world: World;
  private viewportManager: ViewportManager;
  
  constructor(world: World) {
    this.world = world;
    this.viewportManager = new ViewportManager();
  }
  
  /**
   * Execute MAP block - render viewport at location
   * @param block - Parsed MAP block
   * @returns Rendered output (ASCII/Unicode grid)
   */
  executeMapBlock(block: MapBlock): string {
    if (!block.location) {
      return '⚠️  MAP block requires location parameter';
    }
    
    // Get location from world
    const location = this.world.getLocation(block.location);
    if (!location) {
      return `⚠️  Location not found: ${block.location}`;
    }
    
    // Parse location ID to get layer and center
    const parsed = this.parseLocationId(block.location);
    if (!parsed) {
      return `⚠️  Invalid location ID: ${block.location}`;
    }
    
    // Configure viewport
    const size = block.size || { width: 80, height: 30 };
    const center = this.parseCellAddress(block.center || location.center);
    
    this.viewportManager.setSize(size);
    this.viewportManager.setLayer(parsed.layer);
    this.viewportManager.setCenter(center);
    
    // Render grid
    const output: string[] = [];
    
    // Header (optional)
    if (block.showLayer) {
      const scale = this.getDistanceScale(parsed.layer);
      output.push(`📍 ${location.metadata.name} (${scale})`);
      output.push('');
    }
    
    // Get visible tiles
    const tiles = this.viewportManager.getVisibleTiles();
    
    // Render tiles to grid (simplified - would use sextant renderer)
    const grid = this.renderTilesToGrid(tiles, location.tiles);
    output.push(grid);
    
    // Footer (optional)
    if (block.showCoords) {
      output.push('');
      output.push(`Center: ${block.center || location.center} | Size: ${size.width}×${size.height}`);
    }
    
    return output.join('\n');
  }
  
  /**
   * Execute PANEL block - render specific region
   * @param block - Parsed PANEL block
   * @returns Rendered output
   */
  executePanelBlock(block: PanelBlock): string {
    if (!block.location) {
      return '⚠️  PANEL block requires location parameter';
    }
    
    const location = this.world.getLocation(block.location);
    if (!location) {
      return `⚠️  Location not found: ${block.location}`;
    }
    
    // Parse region bounds
    let region = block.region || `${location.center}:${location.center}`;
    const [startCell, endCell] = region.split(':');
    
    const output: string[] = [];
    output.push(`📋 ${location.metadata.name} [${startCell}:${endCell}]`);
    output.push('');
    
    // Render region (simplified)
    output.push('[Panel rendering not yet implemented]');
    
    return output.join('\n');
  }
  
  /**
   * Execute any grid block
   */
  executeBlock(block: GridBlock): string {
    switch (block.type) {
      case 'map':
        return this.executeMapBlock(block);
      case 'panel':
        return this.executePanelBlock(block);
    }
  }
  
  // Helper methods (simplified - would import from location-types)
  
  private parseLocationId(id: string): { layer: number; cell: string } | null {
    const match = id.match(/^L(\d+)-([A-Z]{2}\d+)$/);
    if (!match) return null;
    return { layer: parseInt(match[1], 10), cell: match[2] };
  }
  
  private parseCellAddress(cell: string): { layer: number; col: number; row: number } {
    // Simplified - assumes layer 300, parses AA10 format
    const colStr = cell.slice(0, 2);
    const rowStr = cell.slice(2);
    
    // Convert AA-DC to 0-79
    const col = (colStr.charCodeAt(0) - 65) * 26 + (colStr.charCodeAt(1) - 65);
    const row = parseInt(rowStr, 10);
    
    return { layer: 300, col, row };
  }
  
  private getDistanceScale(layer: number): string {
    if (layer >= 300 && layer <= 305) return 'Terrestrial';
    if (layer >= 306 && layer <= 310) return 'Orbital';
    if (layer >= 311 && layer <= 320) return 'Planetary';
    if (layer >= 321 && layer <= 350) return 'Stellar';
    if (layer >= 351 && layer <= 400) return 'Galactic';
    return 'Cosmic';
  }
  
  private renderTilesToGrid(tiles: any[], tileMap: any): string {
    // Simplified rendering - would use sextant renderer
    const grid: string[] = [];
    
    grid.push('┌' + '─'.repeat(78) + '┐');
    
    for (let i = 0; i < 28; i++) {
      grid.push('│' + ' '.repeat(78) + '│');
    }
    
    grid.push('└' + '─'.repeat(78) + '┘');
    
    return grid.join('\n');
  }
}

/**
 * Parse and execute all grid blocks in markdown
 * @param markdown - Full markdown document
 * @param world - World instance with loaded locations
 * @returns Array of rendered outputs
 */
export function executeGridBlocks(markdown: string, world: World): string[] {
  const blocks = extractGridBlocks(markdown);
  const executor = new GridBlockExecutor(world);
  
  return blocks.map(block => executor.executeBlock(block));
}
