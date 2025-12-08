/**
 * Teletext Renderer
 * 8-color teletext rendering with palette support
 */

const fs = require('fs').promises;
const path = require('path');

class TeletextRenderer {
  constructor() {
    this.palettePath = path.join(__dirname, '../../../../core/data/diagrams/teletext');
    this.defaultPalette = 'classic';
  }

  async loadPalette(paletteName) {
    const filePath = path.join(this.palettePath, `palette_${paletteName}.json`);
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      throw new Error(`Palette not found: ${paletteName}`);
    }
  }

  colorToANSI(colorName, palette) {
    const ansiCodes = {
      black: '\x1b[30m',
      red: '\x1b[31m',
      green: '\x1b[32m',
      yellow: '\x1b[33m',
      blue: '\x1b[34m',
      magenta: '\x1b[35m',
      cyan: '\x1b[36m',
      white: '\x1b[37m'
    };
    return ansiCodes[colorName] || '';
  }

  applyColors(content, palette) {
    // Simple color tag replacement: {red}text{/red}
    let result = content;
    const colorNames = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'];
    
    colorNames.forEach(color => {
      const ansiCode = this.colorToANSI(color, palette);
      const reset = '\x1b[0m';
      const openTag = new RegExp(`\\{${color}\\}`, 'g');
      const closeTag = new RegExp(`\\{\\/${color}\\}`, 'g');
      
      result = result.replace(openTag, ansiCode);
      result = result.replace(closeTag, reset);
    });
    
    return result;
  }

  applyBackground(content, palette) {
    // Apply palette background color
    const bgColor = palette.background || '#000000';
    // For terminal, we use ANSI background codes
    return `\x1b[40m${content}\x1b[0m`;
  }

  generateTeletextPage(content, palette, options = {}) {
    const width = options.width || 40;
    const height = options.height || 24;
    
    // Teletext page structure (40 cols x 24 rows standard)
    const lines = content.split('\n');
    const page = [];
    
    for (let i = 0; i < height; i++) {
      if (i < lines.length) {
        const line = lines[i].padEnd(width).substring(0, width);
        page.push(line);
      } else {
        page.push(' '.repeat(width));
      }
    }
    
    return page.join('\n');
  }

  async render(content, paletteName = null, options = {}) {
    // Load palette
    const palette = await this.loadPalette(paletteName || this.defaultPalette);
    
    // Generate teletext page
    let result = this.generateTeletextPage(content, palette, options);
    
    // Apply colors
    result = this.applyColors(result, palette);
    
    // Apply background
    if (options.background !== false) {
      result = this.applyBackground(result, palette);
    }
    
    return result;
  }

  async listPalettes() {
    const files = await fs.readdir(this.palettePath);
    return files
      .filter(f => f.startsWith('palette_') && f.endsWith('.json'))
      .map(f => f.replace('palette_', '').replace('.json', ''));
  }
}

module.exports = new TeletextRenderer();
