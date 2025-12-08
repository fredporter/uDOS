/**
 * Flowchart Renderer
 * Uses flowchart.js library
 */

const flowchart = require('flowchart.js');
const fs = require('fs').promises;
const path = require('path');

class FlowRenderer {
  constructor() {
    this.templatePath = path.join(__dirname, '../../../../core/data/diagrams/flow');
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

  parseFlowchart(source) {
    try {
      const diagram = flowchart.parse(source);
      return diagram;
    } catch (error) {
      throw new Error(`Flowchart syntax error: ${error.message}`);
    }
  }

  renderToSVG(diagram, options = {}) {
    // Flowchart rendering options
    const renderOptions = {
      'line-width': options.lineWidth || 2,
      'line-length': options.lineLength || 50,
      'text-margin': options.textMargin || 10,
      'font-size': options.fontSize || 14,
      'font-family': options.fontFamily || 'Arial',
      'font-weight': options.fontWeight || 'normal',
      'font-color': options.fontColor || 'black',
      'line-color': options.lineColor || 'black',
      'element-color': options.elementColor || 'black',
      'fill': options.fill || 'white',
      'yes-text': options.yesText || 'yes',
      'no-text': options.noText || 'no',
      'arrow-end': options.arrowEnd || 'block',
      'scale': options.scale || 1,
      'symbols': {
        'start': options.startSymbol || { 'font-color': 'white', 'fill': '#2F3542' },
        'end': options.endSymbol || { 'font-color': 'white', 'fill': '#2F3542' }
      }
    };
    
    // Create SVG container
    const svg = diagram.drawSVG(renderOptions);
    
    return svg;
  }

  async render(source, options = {}) {
    let flowSource = source;
    
    // If source is a template name, load it
    if (!source.includes('=>') && !source.includes('->')) {
      flowSource = await this.loadTemplate(source);
    }
    
    // Parse flowchart
    const diagram = this.parseFlowchart(flowSource);
    
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

module.exports = new FlowRenderer();
