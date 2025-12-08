/**
 * Sequence Diagram Renderer
 * Uses js-sequence-diagrams library
 */

const { Diagram } = require('js-sequence-diagrams');
const fs = require('fs').promises;
const path = require('path');

class SequenceRenderer {
  constructor() {
    this.templatePath = path.join(__dirname, '../../../../core/data/diagrams/sequence');
  }

  async loadTemplate(templateName) {
    const filePath = path.join(this.templatePath, `${templateName}.txt`);
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return content;
    } catch (error) {
      throw new Error(`Template not found: ${templateName}`);
    }
  }

  parseSequence(source) {
    // js-sequence-diagrams parser
    try {
      const diagram = Diagram.parse(source);
      return diagram;
    } catch (error) {
      throw new Error(`Sequence syntax error: ${error.message}`);
    }
  }

  renderToSVG(diagram, options = {}) {
    const theme = options.theme || 'simple';
    
    // Render diagram to SVG
    const svg = diagram.drawSVG(theme);
    
    return svg;
  }

  async render(source, options = {}) {
    let diagramSource = source;
    
    // If source is a template name, load it
    if (!source.includes('->') && !source.includes('Title:')) {
      diagramSource = await this.loadTemplate(source);
    }
    
    // Parse sequence diagram
    const diagram = this.parseSequence(diagramSource);
    
    // Render to SVG
    const svg = this.renderToSVG(diagram, options);
    
    return svg;
  }

  async listTemplates() {
    const files = await fs.readdir(this.templatePath);
    return files
      .filter(f => f.endsWith('.txt'))
      .map(f => f.replace('.txt', ''));
  }
}

module.exports = new SequenceRenderer();
