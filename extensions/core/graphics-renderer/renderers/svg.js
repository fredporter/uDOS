/**
 * SVG Renderer
 * AI-assisted SVG generation with style templates
 */

const fs = require('fs').promises;
const path = require('path');

class SVGRenderer {
  constructor() {
    this.stylePath = path.join(__dirname, '../../../../core/data/diagrams/svg');
    this.defaultStyle = 'technical';
  }

  async loadStyle(styleName) {
    const filePath = path.join(this.stylePath, `style_${styleName}.json`);
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      throw new Error(`Style not found: ${styleName}`);
    }
  }

  generateSVGHeader(style, width = 800, height = 600) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs>
    ${this.generateGradients(style)}
    ${this.generateMarkers(style)}
  </defs>
  <rect width="100%" height="100%" fill="${style.colors.background}"/>
`;
  }

  generateGradients(style) {
    if (!style.gradients) return '';
    
    return Object.entries(style.gradients).map(([id, gradient]) => `
    <linearGradient id="${id}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:${gradient.start};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${gradient.end};stop-opacity:1" />
    </linearGradient>`).join('');
  }

  generateMarkers(style) {
    const arrow = style.shapes.arrow;
    return `
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="${arrow.marker_fill}" />
    </marker>`;
  }

  generateRectangle(x, y, width, height, text, style) {
    const rect = style.shapes.rectangle;
    return `
  <rect x="${x}" y="${y}" width="${width}" height="${height}" 
        fill="${rect.fill}" stroke="${rect.stroke}" 
        stroke-width="${rect.stroke_width}" rx="${rect.rx}"/>
  <text x="${x + width/2}" y="${y + height/2}" 
        text-anchor="middle" dominant-baseline="middle"
        font-family="${style.settings.font_family}" 
        font-size="${style.settings.font_size}" 
        fill="${style.colors.text}">${text}</text>`;
  }

  generateArrow(x1, y1, x2, y2, style) {
    const arrow = style.shapes.arrow;
    return `
  <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" 
        stroke="${arrow.stroke}" stroke-width="${arrow.stroke_width}" 
        marker-end="url(#arrowhead)"/>`;
  }

  generatePlaceholder(description, style, width = 800, height = 600) {
    // Simple placeholder for AI-assisted generation
    // In production, this would call an AI service
    return this.generateSVGHeader(style, width, height) + `
  <text x="400" y="300" text-anchor="middle" 
        font-family="${style.settings.font_family}" 
        font-size="24" fill="${style.colors.text}">
    ${description}
  </text>
  <text x="400" y="340" text-anchor="middle" 
        font-family="${style.settings.font_family}" 
        font-size="14" fill="${style.colors.secondary}">
    (AI-assisted generation placeholder)
  </text>
</svg>`;
  }

  async render(description, styleName = null, options = {}) {
    // Load style
    const style = await this.loadStyle(styleName || this.defaultStyle);
    
    // Generate SVG (placeholder for now - AI integration in future)
    const width = options.width || 800;
    const height = options.height || 600;
    
    const svg = this.generatePlaceholder(description, style, width, height);
    
    return svg;
  }

  async listStyles() {
    const files = await fs.readdir(this.stylePath);
    return files
      .filter(f => f.startsWith('style_') && f.endsWith('.json'))
      .map(f => f.replace('style_', '').replace('.json', ''));
  }
}

module.exports = new SVGRenderer();
