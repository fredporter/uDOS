/**
 * uDOS Markdown Viewer - uCODE Processor
 * Version: 1.0.24
 *
 * Processes uCODE commands embedded in markdown:
 * Format: [COMMAND|ARG|VALUE]
 *
 * Examples:
 * - [FILE|READ|/path/to/file.txt]
 * - [SYSTEM|INFO]
 * - [HELP|COMMAND|grep]
 * - [WEB|START|dashboard]
 */

class UCodeProcessor {
  constructor() {
    this.commands = [];
    this.ucodePattern = /\[([A-Z-]+)(?:\|([^\|\]]*?))?(?:\|([^\]]*?))?\]/g;
  }

  /**
   * Process rendered HTML to find and highlight uCODE commands
   */
  process(container) {
    this.commands = [];

    // Find all text nodes
    const walker = document.createTreeWalker(
      container,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
      if (node.textContent.match(this.ucodePattern)) {
        textNodes.push(node);
      }
    }

    // Process each text node
    textNodes.forEach(textNode => {
      const fragment = document.createDocumentFragment();
      let lastIndex = 0;
      let match;

      const regex = new RegExp(this.ucodePattern);
      const text = textNode.textContent;

      while ((match = regex.exec(text)) !== null) {
        // Add text before match
        if (match.index > lastIndex) {
          fragment.appendChild(
            document.createTextNode(text.slice(lastIndex, match.index))
          );
        }

        // Create uCODE command element
        const cmd = {
          command: match[1],
          arg: match[2] || '',
          value: match[3] || '',
          full: match[0]
        };

        this.commands.push(cmd);

        const span = document.createElement('span');
        span.className = 'ucode-command';
        span.textContent = cmd.full;
        span.dataset.command = JSON.stringify(cmd);
        span.addEventListener('click', () => this.execute(cmd));

        fragment.appendChild(span);

        lastIndex = regex.lastIndex;
      }

      // Add remaining text
      if (lastIndex < text.length) {
        fragment.appendChild(
          document.createTextNode(text.slice(lastIndex))
        );
      }

      // Replace text node with processed fragment
      textNode.parentNode.replaceChild(fragment, textNode);
    });
  }

  /**
   * Get all parsed uCODE commands
   */
  getCommands() {
    return this.commands;
  }

  /**
   * Execute a uCODE command
   */
  async execute(cmd) {
    console.log('Executing uCODE command:', cmd);

    try {
      switch (cmd.command) {
        case 'FILE':
          await this.executeFileCommand(cmd);
          break;
        case 'SYSTEM':
          await this.executeSystemCommand(cmd);
          break;
        case 'HELP':
          await this.executeHelpCommand(cmd);
          break;
        case 'WEB':
          await this.executeWebCommand(cmd);
          break;
        case 'SEARCH':
          await this.executeSearchCommand(cmd);
          break;
        case 'COPY':
          await this.executeCopyCommand(cmd);
          break;
        default:
          this.showMessage(`Unknown command: ${cmd.command}`, 'warning');
      }
    } catch (error) {
      console.error('uCODE execution error:', error);
      this.showMessage(`Error executing ${cmd.command}: ${error.message}`, 'error');
    }
  }

  /**
   * FILE commands: READ, WRITE, LIST, etc.
   */
  async executeFileCommand(cmd) {
    const action = cmd.arg?.toUpperCase();
    const path = cmd.value;

    switch (action) {
      case 'READ':
        if (!path) {
          this.showMessage('FILE|READ requires a path', 'error');
          return;
        }

        try {
          const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
          const data = await response.json();

          if (data.content) {
            this.showFileContent(path, data.content);
          } else {
            this.showMessage(`File not found: ${path}`, 'error');
          }
        } catch (error) {
          this.showMessage(`Failed to read file: ${error.message}`, 'error');
        }
        break;

      case 'LIST':
        const dir = path || '/';
        try {
          const response = await fetch(`/api/files?dir=${encodeURIComponent(dir)}`);
          const data = await response.json();
          this.showFileList(dir, data.files);
        } catch (error) {
          this.showMessage(`Failed to list directory: ${error.message}`, 'error');
        }
        break;

      default:
        this.showMessage(`Unknown FILE action: ${action}`, 'warning');
    }
  }

  /**
   * SYSTEM commands: INFO, VERSION, STATUS, etc.
   */
  async executeSystemCommand(cmd) {
    const action = cmd.arg?.toUpperCase() || 'INFO';

    try {
      const response = await fetch(`/api/system/${action.toLowerCase()}`);
      const data = await response.json();
      this.showSystemInfo(action, data);
    } catch (error) {
      this.showMessage(`Failed to get system ${action}: ${error.message}`, 'error');
    }
  }

  /**
   * HELP commands: COMMAND, TOPIC, etc.
   */
  async executeHelpCommand(cmd) {
    const type = cmd.arg?.toUpperCase() || 'GENERAL';
    const topic = cmd.value || '';

    try {
      const response = await fetch(`/api/help?type=${type}&topic=${encodeURIComponent(topic)}`);
      const data = await response.json();
      this.showHelp(type, topic, data.content);
    } catch (error) {
      this.showMessage(`Failed to get help: ${error.message}`, 'error');
    }
  }

  /**
   * WEB commands: START, OPEN, etc.
   */
  async executeWebCommand(cmd) {
    const action = cmd.arg?.toUpperCase();
    const target = cmd.value;

    switch (action) {
      case 'START':
      case 'OPEN':
        if (!target) {
          this.showMessage('WEB command requires a target', 'error');
          return;
        }

        const url = this.resolveWebTarget(target);
        window.open(url, '_blank');
        this.showMessage(`Opening: ${target}`, 'success');
        break;

      default:
        this.showMessage(`Unknown WEB action: ${action}`, 'warning');
    }
  }

  /**
   * SEARCH commands
   */
  async executeSearchCommand(cmd) {
    const query = cmd.arg || cmd.value;

    if (!query) {
      this.showMessage('SEARCH requires a query', 'error');
      return;
    }

    // Trigger search in the file browser
    const searchInput = document.getElementById('searchInput');
    searchInput.value = query;
    searchInput.dispatchEvent(new Event('input'));
    searchInput.focus();

    this.showMessage(`Searching for: ${query}`, 'success');
  }

  /**
   * COPY commands
   */
  async executeCopyCommand(cmd) {
    const content = cmd.arg || cmd.value;

    if (!content) {
      this.showMessage('COPY requires content', 'error');
      return;
    }

    try {
      await navigator.clipboard.writeText(content);
      this.showMessage('Copied to clipboard!', 'success');
    } catch (error) {
      this.showMessage('Failed to copy to clipboard', 'error');
    }
  }

  /**
   * Resolve web target to URL
   */
  resolveWebTarget(target) {
    // Check if it's already a full URL
    if (target.startsWith('http://') || target.startsWith('https://')) {
      return target;
    }

    // Map common uDOS extensions
    const extensionPorts = {
      'dashboard': 8888,
      'markdown-viewer': 9000,
      'teletext': 8890,
      'font-editor': 8891,
      'character-editor': 8891,
      'system-desktop': 8892
    };

    const port = extensionPorts[target.toLowerCase()] || 8888;
    return `http://localhost:${port}`;
  }

  /**
   * Show file content in a modal/overlay
   */
  showFileContent(path, content) {
    // TODO: Implement modal display
    console.log(`File: ${path}\n\n${content}`);
    this.showMessage(`Loaded file: ${path}`, 'success');
  }

  /**
   * Show file list
   */
  showFileList(dir, files) {
    // TODO: Implement modal display
    console.log(`Directory: ${dir}\n${files.map(f => f.name).join('\n')}`);
    this.showMessage(`Listed directory: ${dir}`, 'success');
  }

  /**
   * Show system information
   */
  showSystemInfo(action, data) {
    // TODO: Implement modal display
    console.log(`System ${action}:`, data);
    this.showMessage(`System ${action} retrieved`, 'success');
  }

  /**
   * Show help content
   */
  showHelp(type, topic, content) {
    // TODO: Implement modal display
    console.log(`Help - ${type}: ${topic}\n\n${content}`);
    this.showMessage(`Help displayed: ${topic || type}`, 'success');
  }

  /**
   * Show toast message
   */
  showMessage(message, type = 'info') {
    // TODO: Implement proper toast notification
    const icons = {
      success: '✓',
      error: '✗',
      warning: '⚠',
      info: 'ℹ'
    };

    console.log(`${icons[type] || 'ℹ'} ${message}`);

    // Temporary: Show in status bar
    const status = document.querySelector('.viewer-status .status-left');
    if (status) {
      const originalText = status.textContent;
      status.textContent = `${icons[type]} ${message}`;
      setTimeout(() => {
        status.textContent = originalText;
      }, 3000);
    }
  }
}
