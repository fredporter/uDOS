/**
 * uDOS Panel System v1.2
 * JavaScript component for rendering uCODE panel embeds in markdown
 */

class UDOSPanelSystem {
  constructor(options = {}) {
    this.options = {
      defaultWidth: 80,
      defaultHeight: 24,
      defaultBg: '#000000',
      defaultFg: '#00E676',
      syntaxHighlight: true,
      ...options
    };

    this.panels = new Map();
    this.currentTheme = 'DUNGEON';
  }

  /**
   * Parse uCODE panel parameters from code block info string
   * Example: ```ucode panel:status width:60 height:10 bg:#000000
   */
  parseParams(infoString) {
    const params = {
      panel: 'default',
      width: this.options.defaultWidth,
      height: this.options.defaultHeight,
      bg: this.options.defaultBg,
      fg: this.options.defaultFg
    };

    if (!infoString) return params;

    // Split by whitespace
    const parts = infoString.split(/\s+/);

    parts.forEach(part => {
      const [key, value] = part.split(':');
      if (key && value) {
        params[key.toLowerCase()] = value;
      }
    });

    // Convert numeric strings to numbers
    if (params.width) params.width = parseInt(params.width, 10);
    if (params.height) params.height = parseInt(params.height, 10);

    return params;
  }

  /**
   * Create a panel element from uCODE block
   */
  createPanel(content, params) {
    const panel = document.createElement('div');
    panel.className = 'ucode-panel';
    panel.dataset.panel = params.panel;
    panel.dataset.width = params.width;
    panel.dataset.height = params.height;

    // Apply custom background if specified
    if (params.bg) {
      panel.style.backgroundColor = params.bg;
    }

    if (params.fg) {
      panel.style.color = params.fg;
    }

    // Apply syntax highlighting if enabled
    if (this.options.syntaxHighlight) {
      panel.innerHTML = this.highlightUCode(content);
    } else {
      panel.textContent = content;
    }

    // Store panel reference
    this.panels.set(params.panel, panel);

    return panel;
  }

  /**
   * Syntax highlight uCODE content
   */
  highlightUCode(content) {
    // Escape HTML first
    let html = this.escapeHtml(content);

    // Highlight uCODE patterns: [MODULE|COMMAND*PARAM1*PARAM2]
    html = html.replace(
      /\[([A-Z_]+)\|([A-Z_]+)((?:\*[^\]]*)*)\]/g,
      (match, module, command, params) => {
        let result = '<span class="ucode-bracket">[</span>';
        result += `<span class="ucode-module">${module}</span>`;
        result += '<span class="ucode-pipe">|</span>';
        result += `<span class="ucode-command">${command}</span>`;

        if (params) {
          // Highlight parameters
          const paramParts = params.split('*').filter(p => p);
          paramParts.forEach(param => {
            result += '<span class="ucode-star">*</span>';

            // Check if parameter is a string (quoted)
            if (param.match(/^".*"$/)) {
              result += `<span class="ucode-string">${param}</span>`;
            }
            // Check if parameter is a number
            else if (param.match(/^\d+$/)) {
              result += `<span class="ucode-number">${param}</span>`;
            }
            // Otherwise, treat as identifier
            else {
              result += `<span class="ucode-param">${param}</span>`;
            }
          });
        }

        result += '<span class="ucode-bracket">]</span>';
        return result;
      }
    );

    // Highlight box-drawing characters
    html = html.replace(
      /([┌┐└┘├┤┬┴┼─│╔╗╚╝╠╣╦╩╬═║┏┓┗┛┣┫┳┻╋━┃])/g,
      '<span class="box-char">$1</span>'
    );

    // Highlight status icons
    html = html.replace(
      /([✓✗⚠ℹ⏳⏸⏹])/g,
      '<span class="status-icon">$1</span>'
    );

    return html;
  }

  /**
   * Escape HTML special characters
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Process all uCODE blocks in the document
   */
  processCodeBlocks(container = document) {
    const codeBlocks = container.querySelectorAll('pre code.language-ucode, pre code.ucode');

    codeBlocks.forEach(block => {
      const pre = block.parentElement;
      const content = block.textContent;

      // Get parameters from code block's class or data attributes
      const classList = block.className.split(/\s+/);
      const ucodeClass = classList.find(c => c.startsWith('language-ucode'));

      let infoString = '';
      if (ucodeClass) {
        // Extract info string after language-ucode
        infoString = ucodeClass.replace('language-ucode', '').trim();
      }

      // Also check for data attributes
      const dataParams = {
        panel: block.dataset.panel,
        width: block.dataset.width,
        height: block.dataset.height,
        bg: block.dataset.bg,
        fg: block.dataset.fg
      };

      // Merge info string params with data params
      const params = { ...this.parseParams(infoString), ...dataParams };

      // Create panel and replace pre block
      const panel = this.createPanel(content, params);
      pre.replaceWith(panel);
    });
  }

  /**
   * Set active theme
   */
  setTheme(themeName) {
    this.currentTheme = themeName.toUpperCase();
    document.documentElement.dataset.theme = this.currentTheme;

    // Update all panels with theme
    this.panels.forEach(panel => {
      panel.dataset.theme = this.currentTheme;
    });
  }

  /**
   * Get panel by name
   */
  getPanel(name) {
    return this.panels.get(name);
  }

  /**
   * Show panel
   */
  showPanel(name) {
    const panel = this.getPanel(name);
    if (panel) {
      panel.classList.remove('hidden');
    }
  }

  /**
   * Hide panel
   */
  hidePanel(name) {
    const panel = this.getPanel(name);
    if (panel) {
      panel.classList.add('hidden');
    }
  }

  /**
   * Update panel content
   */
  updatePanel(name, content) {
    const panel = this.getPanel(name);
    if (panel) {
      if (this.options.syntaxHighlight) {
        panel.innerHTML = this.highlightUCode(content);
      } else {
        panel.textContent = content;
      }
    }
  }

  /**
   * Initialize the panel system
   */
  init() {
    // Process code blocks on load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.processCodeBlocks();
      });
    } else {
      this.processCodeBlocks();
    }

    // Set up mutation observer for dynamically added code blocks
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.processCodeBlocks(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
}

// Create global instance
window.UDOSPanels = new UDOSPanelSystem();

// Auto-initialize on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.UDOSPanels.init();
  });
} else {
  window.UDOSPanels.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = UDOSPanelSystem;
}
