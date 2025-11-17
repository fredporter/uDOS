/**
 * uDOS Markdown Viewer - Main Application Logic
 * Version: 1.0.24
 */

class MarkdownViewer {
  constructor() {
    this.currentFile = null;
    this.currentTheme = localStorage.getItem('md-theme') || 'dark';
    this.currentView = 'rendered';
    this.files = [];
    this.ucodeProcessor = new UCodeProcessor();
    this.panelProcessor = new PanelProcessor();

    this.init();
  }

  /**
   * Initialize the application
   */
  init() {
    // Set initial theme
    document.documentElement.setAttribute('data-theme', this.currentTheme);
    document.getElementById('currentTheme').textContent = this.currentTheme.toUpperCase();

    // Bind event listeners
    this.bindEvents();

    // Load file list
    this.loadFileList();

    // Initialize Marked.js settings
    marked.setOptions({
      highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
      },
      breaks: true,
      gfm: true
    });
  }

  /**
   * Bind all event listeners
   */
  bindEvents() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());

    // Panel toggles
    document.getElementById('ucodeToggle').addEventListener('click', () => this.togglePanel('ucode'));
    document.getElementById('panelToggle').addEventListener('click', () => this.togglePanel('info'));

    // View mode selector
    document.getElementById('viewMode').addEventListener('change', (e) => this.setViewMode(e.target.value));

    // Search input
    document.getElementById('searchInput').addEventListener('input', (e) => this.handleSearch(e.target.value));

    // Toolbar actions
    document.getElementById('copyBtn').addEventListener('click', () => this.copyMarkdown());
    document.getElementById('downloadBtn').addEventListener('click', () => this.downloadFile());
    document.getElementById('printBtn').addEventListener('click', () => window.print());

    // Panel close buttons
    document.querySelectorAll('.btn-close').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const panel = e.target.closest('.ucode-panel, .info-panel');
        if (panel) panel.remove();
      });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));
  }

  /**
   * Toggle light/dark theme
   */
  toggleTheme() {
    this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', this.currentTheme);
    document.getElementById('currentTheme').textContent = this.currentTheme.toUpperCase();
    localStorage.setItem('md-theme', this.currentTheme);
  }

  /**
   * Toggle side panels
   */
  togglePanel(type) {
    const content = document.querySelector('.viewer-content');
    if (type === 'ucode') {
      const panel = document.querySelector('.ucode-panel');
      panel.classList.toggle('hidden');
      content.classList.toggle('with-ucode');
    } else if (type === 'info') {
      const panel = document.querySelector('.info-panel');
      panel.classList.toggle('hidden');
      content.classList.toggle('with-info');
    }
  }

  /**
   * Set view mode (rendered/split/source)
   */
  setViewMode(mode) {
    this.currentView = mode;
    const rendered = document.getElementById('renderedView');
    const source = document.getElementById('sourceView');

    rendered.classList.add('hidden');
    source.classList.add('hidden');

    if (mode === 'rendered') {
      rendered.classList.remove('hidden');
    } else if (mode === 'source') {
      source.classList.remove('hidden');
    } else if (mode === 'split') {
      rendered.classList.remove('hidden');
      source.classList.remove('hidden');
      rendered.style.width = '50%';
      source.style.width = '50%';
    }
  }

  /**
   * Handle keyboard shortcuts
   */
  handleKeyboard(e) {
    if (e.ctrlKey || e.metaKey) {
      switch(e.key) {
        case '/':
          e.preventDefault();
          this.toggleTheme();
          break;
        case 'u':
          e.preventDefault();
          this.togglePanel('ucode');
          break;
        case 'p':
          e.preventDefault();
          this.togglePanel('info');
          break;
        case 'f':
          e.preventDefault();
          document.getElementById('searchInput').focus();
          break;
        case 's':
          e.preventDefault();
          this.downloadFile();
          break;
      }
    }
  }

  /**
   * Load file list from server
   */
  async loadFileList() {
    try {
      const response = await fetch('/api/files');
      const data = await response.json();
      this.files = data.files || [];
      this.renderFileTree();
    } catch (error) {
      console.error('Error loading file list:', error);
      this.showError('Failed to load file list');
    }
  }

  /**
   * Render file tree in sidebar
   */
  renderFileTree() {
    const tree = document.getElementById('categoryTree');
    const categories = this.groupByCategory(this.files);

    tree.innerHTML = '';

    for (const [category, files] of Object.entries(categories)) {
      const categoryDiv = document.createElement('div');
      categoryDiv.className = 'category-item';

      const header = document.createElement('div');
      header.className = 'category-header';
      header.innerHTML = `<span>▶</span> ${category}`;
      header.addEventListener('click', () => {
        categoryDiv.classList.toggle('expanded');
        header.querySelector('span').textContent =
          categoryDiv.classList.contains('expanded') ? '▼' : '▶';
      });

      const filesDiv = document.createElement('div');
      filesDiv.className = 'category-files';

      files.forEach(file => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.textContent = file.name;
        fileDiv.dataset.path = file.path;
        fileDiv.addEventListener('click', () => this.loadFile(file));
        filesDiv.appendChild(fileDiv);
      });

      categoryDiv.appendChild(header);
      categoryDiv.appendChild(filesDiv);
      tree.appendChild(categoryDiv);
    }
  }

  /**
   * Group files by category
   */
  groupByCategory(files) {
    const categories = {};

    files.forEach(file => {
      const category = file.category || 'Uncategorized';
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(file);
    });

    return categories;
  }

  /**
   * Handle fuzzy search
   */
  handleSearch(query) {
    if (!query || query.length < 2) {
      document.getElementById('searchResults').classList.add('hidden');
      return;
    }

    const results = this.files.filter(file =>
      file.name.toLowerCase().includes(query.toLowerCase()) ||
      file.path.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);

    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';

    if (results.length === 0) {
      resultsDiv.innerHTML = '<div class="empty-state">No results found</div>';
    } else {
      results.forEach(file => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
          <div class="search-result-name">${file.name}</div>
          <div class="search-result-path">${file.path}</div>
        `;
        item.addEventListener('click', () => {
          this.loadFile(file);
          resultsDiv.classList.add('hidden');
          document.getElementById('searchInput').value = '';
        });
        resultsDiv.appendChild(item);
      });
    }

    resultsDiv.classList.remove('hidden');
  }

  /**
   * Load and render a markdown file
   */
  async loadFile(file) {
    this.currentFile = file;

    try {
      const response = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
      const data = await response.json();

      if (!data.content) {
        throw new Error('No content received');
      }

      // Update breadcrumb
      document.getElementById('breadcrumb').innerHTML = `
        <span>${file.category || 'Uncategorized'}</span>
        <span>${file.name}</span>
      `;

      // Highlight active file
      document.querySelectorAll('.file-item').forEach(item => {
        item.classList.toggle('active', item.dataset.path === file.path);
      });

      // Render markdown
      this.renderMarkdown(data.content);

      // Update source view
      document.getElementById('sourceEditor').value = data.content;

      // Update document info
      this.updateDocumentInfo(data.content, file);

    } catch (error) {
      console.error('Error loading file:', error);
      this.showError('Failed to load file: ' + file.name);
    }
  }

  /**
   * Render markdown content
   */
  renderMarkdown(content) {
    // Process uCODE and PANEL syntax
    let processed = this.panelProcessor.process(content);

    // Parse markdown
    const html = marked.parse(processed);

    // Inject into rendered view
    const rendered = document.getElementById('renderedView');
    rendered.innerHTML = `<div class="markdown-body">${html}</div>`;

    // Process uCODE commands
    this.ucodeProcessor.process(rendered);

    // Generate table of contents
    this.generateTOC(rendered);

    // Update uCODE panel
    this.updateUCodePanel();

    // Scroll to top
    rendered.scrollTop = 0;
  }

  /**
   * Generate table of contents from headings
   */
  generateTOC(container) {
    const headings = container.querySelectorAll('h1, h2, h3, h4');
    const tocContent = document.getElementById('tocContent');

    if (headings.length === 0) {
      tocContent.innerHTML = '<div class="empty-state">No headings found</div>';
      return;
    }

    const ul = document.createElement('ul');

    headings.forEach((heading, index) => {
      const id = `heading-${index}`;
      heading.id = id;

      const li = document.createElement('li');
      li.className = `toc-${heading.tagName.toLowerCase()}`;

      const a = document.createElement('a');
      a.href = `#${id}`;
      a.textContent = heading.textContent;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });

      li.appendChild(a);
      ul.appendChild(li);
    });

    tocContent.innerHTML = '';
    tocContent.appendChild(ul);
  }

  /**
   * Update document info panel
   */
  updateDocumentInfo(content, file) {
    const lines = content.split('\n').length;
    const words = content.split(/\s+/).filter(w => w.length > 0).length;
    const chars = content.length;
    const headings = (content.match(/^#+\s/gm) || []).length;
    const codeBlocks = (content.match(/```/g) || []).length / 2;
    const ucodeCmds = (content.match(/\[[\w-]+\|[^\]]*\]/g) || []).length;

    document.getElementById('infoFile').textContent = file.name;
    document.getElementById('infoCategory').textContent = file.category || 'N/A';
    document.getElementById('infoSize').textContent = this.formatFileSize(chars);
    document.getElementById('infoLines').textContent = lines.toLocaleString();
    document.getElementById('infoWords').textContent = words.toLocaleString();
    document.getElementById('infoChars').textContent = chars.toLocaleString();
    document.getElementById('infoHeadings').textContent = headings;
    document.getElementById('infoCode').textContent = Math.floor(codeBlocks);
    document.getElementById('infoUcode').textContent = ucodeCmds;
  }

  /**
   * Update uCODE panel with command list
   */
  updateUCodePanel() {
    const commands = this.ucodeProcessor.getCommands();
    const list = document.getElementById('ucodeList');

    if (commands.length === 0) {
      list.innerHTML = '<div class="empty-state">No uCODE commands found</div>';
      return;
    }

    list.innerHTML = '';

    commands.forEach(cmd => {
      const item = document.createElement('div');
      item.className = 'ucode-command';
      item.textContent = `${cmd.command} | ${cmd.arg || ''} | ${cmd.value || ''}`;
      item.addEventListener('click', () => this.ucodeProcessor.execute(cmd));
      list.appendChild(item);
    });
  }

  /**
   * Copy markdown to clipboard
   */
  async copyMarkdown() {
    const content = document.getElementById('sourceEditor').value;
    try {
      await navigator.clipboard.writeText(content);
      this.showMessage('Markdown copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy:', error);
      this.showError('Failed to copy to clipboard');
    }
  }

  /**
   * Download current file
   */
  downloadFile() {
    if (!this.currentFile) {
      this.showError('No file loaded');
      return;
    }

    const content = document.getElementById('sourceEditor').value;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = this.currentFile.name;
    a.click();
    URL.revokeObjectURL(url);

    this.showMessage('File downloaded!');
  }

  /**
   * Format file size
   */
  formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  /**
   * Show success message
   */
  showMessage(message) {
    // TODO: Implement toast notification
    console.log('✓', message);
  }

  /**
   * Show error message
   */
  showError(message) {
    // TODO: Implement toast notification
    console.error('✗', message);
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.markdownViewer = new MarkdownViewer();
});
