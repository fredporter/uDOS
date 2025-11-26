/**
 * uDOS Markdown Viewer - PANEL Processor
 * Version: 1.0.24
 *
 * Processes PANEL callout blocks in markdown:
 * Format: :::type
 *         content
 *         :::
 *
 * Types: note, warning, danger, success
 *
 * Examples:
 * :::note
 * This is an informational note
 * :::
 *
 * :::warning
 * This is a warning message
 * :::
 */

class PanelProcessor {
  constructor() {
    this.panelPattern = /:::(\w+)\s*\n([\s\S]*?)\n:::/g;
    this.validTypes = ['note', 'warning', 'danger', 'success'];
  }

  /**
   * Process markdown text to convert PANEL syntax to HTML
   * This is called BEFORE markdown parsing
   */
  process(markdown) {
    return markdown.replace(this.panelPattern, (match, type, content) => {
      return this.createPanelHTML(type, content.trim());
    });
  }

  /**
   * Create HTML for a panel
   */
  createPanelHTML(type, content) {
    const normalizedType = type.toLowerCase();

    // Validate type
    if (!this.validTypes.includes(normalizedType)) {
      console.warn(`Invalid panel type: ${type}, defaulting to 'note'`);
      type = 'note';
    }

    const title = this.getPanelTitle(normalizedType);
    const icon = this.getPanelIcon(normalizedType);

    // Create HTML structure that will survive markdown parsing
    return `\n\n<div class="panel panel-${normalizedType}" data-panel-type="${normalizedType}">
  <div class="panel-title">${icon} ${title}</div>
  <div class="panel-content">
${content}
  </div>
</div>\n\n`;
  }

  /**
   * Get panel title based on type
   */
  getPanelTitle(type) {
    const titles = {
      note: 'Note',
      warning: 'Warning',
      danger: 'Danger',
      success: 'Success'
    };

    return titles[type] || 'Info';
  }

  /**
   * Get panel icon based on type
   */
  getPanelIcon(type) {
    const icons = {
      note: 'ℹ️',
      warning: '⚠️',
      danger: '🛑',
      success: '✅'
    };

    return icons[type] || 'ℹ️';
  }

  /**
   * Post-process rendered HTML to enhance panels
   * Call this AFTER markdown is rendered
   */
  enhance(container) {
    const panels = container.querySelectorAll('.panel');

    panels.forEach(panel => {
      const type = panel.dataset.panelType || 'note';

      // Add click-to-copy functionality
      const title = panel.querySelector('.panel-title');
      if (title) {
        title.style.cursor = 'pointer';
        title.title = 'Click to copy panel content';

        title.addEventListener('click', async () => {
          const content = panel.querySelector('.panel-content');
          if (content) {
            try {
              await navigator.clipboard.writeText(content.textContent);
              this.showCopyFeedback(panel);
            } catch (error) {
              console.error('Failed to copy panel content:', error);
            }
          }
        });
      }

      // Add expand/collapse for long panels
      const contentDiv = panel.querySelector('.panel-content');
      if (contentDiv && contentDiv.scrollHeight > 300) {
        panel.classList.add('panel-collapsible');

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'panel-toggle-btn';
        toggleBtn.textContent = '▼ Show more';
        toggleBtn.addEventListener('click', () => {
          panel.classList.toggle('panel-expanded');
          toggleBtn.textContent = panel.classList.contains('panel-expanded')
            ? '▲ Show less'
            : '▼ Show more';
        });

        panel.appendChild(toggleBtn);
      }
    });
  }

  /**
   * Show visual feedback when panel content is copied
   */
  showCopyFeedback(panel) {
    const originalBg = panel.style.backgroundColor;

    // Flash animation
    panel.style.transition = 'background-color 0.3s';
    panel.style.backgroundColor = 'rgba(0, 255, 0, 0.2)';

    setTimeout(() => {
      panel.style.backgroundColor = originalBg;
    }, 300);

    // Show checkmark
    const checkmark = document.createElement('span');
    checkmark.className = 'panel-copy-checkmark';
    checkmark.textContent = '✓ Copied!';
    checkmark.style.cssText = `
      position: absolute;
      top: 10px;
      right: 10px;
      background: #4CAF50;
      color: white;
      padding: 5px 10px;
      border-radius: 3px;
      font-size: 12px;
      animation: fadeInOut 2s;
    `;

    panel.style.position = 'relative';
    panel.appendChild(checkmark);

    setTimeout(() => {
      checkmark.remove();
    }, 2000);
  }

  /**
   * Count panels in markdown
   */
  countPanels(markdown) {
    const matches = markdown.match(this.panelPattern) || [];
    return matches.length;
  }

  /**
   * Get panel statistics from markdown
   */
  getStats(markdown) {
    const stats = {
      total: 0,
      note: 0,
      warning: 0,
      danger: 0,
      success: 0
    };

    let match;
    const regex = new RegExp(this.panelPattern);

    while ((match = regex.exec(markdown)) !== null) {
      stats.total++;
      const type = match[1].toLowerCase();
      if (this.validTypes.includes(type)) {
        stats[type]++;
      }
    }

    return stats;
  }

  /**
   * Validate panel syntax in markdown
   */
  validate(markdown) {
    const errors = [];
    const lines = markdown.split('\n');

    let inPanel = false;
    let panelStartLine = 0;
    let panelType = '';

    lines.forEach((line, index) => {
      const lineNum = index + 1;

      // Check for panel start
      const startMatch = line.match(/^:::(\w+)\s*$/);
      if (startMatch) {
        if (inPanel) {
          errors.push({
            line: lineNum,
            type: 'nested',
            message: `Nested panels are not allowed (panel started at line ${panelStartLine})`
          });
        } else {
          inPanel = true;
          panelStartLine = lineNum;
          panelType = startMatch[1];

          if (!this.validTypes.includes(panelType.toLowerCase())) {
            errors.push({
              line: lineNum,
              type: 'invalid-type',
              message: `Invalid panel type: ${panelType} (valid types: ${this.validTypes.join(', ')})`
            });
          }
        }
      }

      // Check for panel end
      if (line.trim() === ':::') {
        if (!inPanel) {
          errors.push({
            line: lineNum,
            type: 'unmatched-end',
            message: 'Panel end marker without start'
          });
        } else {
          inPanel = false;
          panelType = '';
        }
      }
    });

    // Check for unclosed panels
    if (inPanel) {
      errors.push({
        line: panelStartLine,
        type: 'unclosed',
        message: `Panel started at line ${panelStartLine} was never closed`
      });
    }

    return {
      valid: errors.length === 0,
      errors: errors
    };
  }
}

// Add CSS animation for copy feedback
if (!document.getElementById('panel-animations')) {
  const style = document.createElement('style');
  style.id = 'panel-animations';
  style.textContent = `
    @keyframes fadeInOut {
      0% { opacity: 0; transform: translateY(-10px); }
      15% { opacity: 1; transform: translateY(0); }
      85% { opacity: 1; transform: translateY(0); }
      100% { opacity: 0; transform: translateY(-10px); }
    }

    .panel-collapsible .panel-content {
      max-height: 300px;
      overflow: hidden;
      position: relative;
    }

    .panel-collapsible .panel-content::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 60px;
      background: linear-gradient(transparent, var(--md-canvas-subtle));
    }

    .panel-expanded .panel-content {
      max-height: none;
    }

    .panel-expanded .panel-content::after {
      display: none;
    }

    .panel-toggle-btn {
      background: var(--md-code-bg);
      color: var(--md-accent);
      border: 1px solid var(--md-border);
      padding: 6px 12px;
      margin-top: 10px;
      cursor: pointer;
      font-size: 12px;
      font-family: var(--font-system);
      width: 100%;
      transition: all 0.2s;
    }

    .panel-toggle-btn:hover {
      background: var(--md-accent);
      color: var(--md-bg);
    }
  `;
  document.head.appendChild(style);
}
