/**
 * ASCII Renderer
 * Direct template loading and substitution
 */

const fs = require('fs').promises;
const path = require('path');

class ASCIIRenderer {
  constructor() {
    this.templatePath = path.join(__dirname, '../../../../core/data/diagrams/ascii');
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

  substituteVariables(template, data) {
    if (!data) return template;
    
    let result = template;
    for (const [key, value] of Object.entries(data)) {
      const regex = new RegExp(`\\{${key}\\}`, 'g');
      result = result.replace(regex, value);
    }
    return result;
  }

  applyOptions(content, options = {}) {
    let result = content;
    
    // Width adjustment (word wrap)
    if (options.width) {
      const lines = result.split('\n');
      result = lines.map(line => {
        if (line.length > options.width) {
          return line.substring(0, options.width);
        }
        return line;
      }).join('\n');
    }
    
    // Add border
    if (options.border) {
      const lines = result.split('\n');
      const maxLen = Math.max(...lines.map(l => l.length));
      const top = '┌' + '─'.repeat(maxLen + 2) + '┐';
      const bottom = '└' + '─'.repeat(maxLen + 2) + '┘';
      const bordered = lines.map(line => `│ ${line.padEnd(maxLen)} │`);
      result = [top, ...bordered, bottom].join('\n');
    }
    
    return result;
  }

  async render(template, data = {}, options = {}) {
    // Load template
    const templateContent = await this.loadTemplate(template);
    
    // Substitute variables
    let result = this.substituteVariables(templateContent, data);
    
    // Apply options
    result = this.applyOptions(result, options);
    
    return result;
  }

  async listTemplates() {
    const files = await fs.readdir(this.templatePath);
    return files
      .filter(f => f.endsWith('.txt'))
      .map(f => f.replace('.txt', ''));
  }
}

module.exports = new ASCIIRenderer();
