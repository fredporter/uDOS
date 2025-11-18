/**
 * uDOS Markdown Viewer - Main Application Logic
 * Version: 1.0.24
 */

class MarkdownViewer {
  constructor() {
    this.currentFile = null;
    this.currentTheme = localStorage.getItem('md-theme') || 'dark';
    this.currentView = 'rendered';
    this.currentFolder = localStorage.getItem('md-folder') || 'all';
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
    const themeEl = document.getElementById('currentTheme');
    if (themeEl) {
      themeEl.textContent = this.currentTheme.toUpperCase();
    }

    // Restore sidebar state (if toggle button exists)
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
      const sidebarCollapsed = localStorage.getItem('md-sidebar-collapsed') === 'true';
      if (sidebarCollapsed) {
        const content = document.querySelector('.viewer-content');
        if (content) {
          content.classList.add('sidebar-collapsed');
        }
        const icon = toggleBtn.querySelector('i');
        if (icon) {
          icon.className = 'cil-arrow-right';
        }
      }
    }

    // Bind event listeners
    this.bindEvents();

    // Restore folder selection
    const savedFolder = this.currentFolder;
    document.querySelectorAll('.folder-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.folder === savedFolder);
    });

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

    // Sidebar toggle
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => this.toggleSidebar());
    }

    // Panel toggles
    const ucodeToggle = document.getElementById('ucodeToggle');
    const panelToggle = document.getElementById('panelToggle');
    if (ucodeToggle) {
      ucodeToggle.addEventListener('click', () => this.togglePanel('ucode'));
    }
    if (panelToggle) {
      panelToggle.addEventListener('click', () => this.togglePanel('info'));
    }

    // Panel close buttons
    const closeUcode = document.getElementById('closeUcode');
    const closeInfo = document.getElementById('closeInfo');
    if (closeUcode) {
      closeUcode.addEventListener('click', () => this.togglePanel('ucode'));
    }
    if (closeInfo) {
      closeInfo.addEventListener('click', () => this.togglePanel('info'));
    }

    // Refresh files
    document.getElementById('refreshFiles').addEventListener('click', () => {
      this.setStatus('Refreshing...');
      this.loadFileList();
    });

    // View mode selector
    document.getElementById('viewMode').addEventListener('change', (e) => this.setViewMode(e.target.value));

    // Search input
    document.getElementById('searchInput').addEventListener('input', (e) => this.handleSearch(e.target.value));

    // Toolbar actions
    document.getElementById('copyBtn').addEventListener('click', () => this.copyMarkdown());
    document.getElementById('downloadBtn').addEventListener('click', () => this.downloadFile());
    document.getElementById('printBtn').addEventListener('click', () => window.print());

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

    // Update theme icon
    const icon = document.querySelector('#themeToggle i');
    icon.className = this.currentTheme === 'dark' ? 'cil-moon' : 'cil-sun';

    // Update syntax highlighting theme
    const highlightTheme = document.getElementById('highlight-theme');
    highlightTheme.href = this.currentTheme === 'dark'
      ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css'
      : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';

    localStorage.setItem('md-theme', this.currentTheme);
  }

  /**
   * Toggle sidebar visibility
   */
  toggleSidebar() {
    const content = document.querySelector('.viewer-content');
    const icon = document.querySelector('#toggleSidebar i');
    const isCollapsed = content.classList.toggle('sidebar-collapsed');

    // Update icon
    if (icon) {
      icon.className = isCollapsed ? 'cil-arrow-right' : 'cil-menu';
    }

    // Save state
    localStorage.setItem('md-sidebar-collapsed', isCollapsed);
  }

  /**
   * Toggle side panels (ucode or info)
   */
  togglePanel(type) {
    if (type === 'ucode') {
      const panel = document.getElementById('ucodePanel');
      if (panel) {
        panel.classList.toggle('hidden');
      }
    } else if (type === 'info') {
      const panel = document.getElementById('infoPanel');
      if (panel) {
        panel.classList.toggle('hidden');
      }
    }
  }  /**
   * Set view mode (rendered/split/source)
   */
  setViewMode(mode) {
    this.currentView = mode;
    const content = document.querySelector('.markdown-content');
    const rendered = document.getElementById('renderedView');
    const source = document.getElementById('sourceView');

    // Remove all view mode classes
    content.classList.remove('view-rendered', 'view-source', 'view-split');
    rendered.classList.add('hidden');
    source.classList.add('hidden');

    // Reset inline styles
    rendered.style.width = '';
    source.style.width = '';

    // Apply new view mode
    if (mode === 'render' || mode === 'rendered') {
      content.classList.add('view-rendered');
      rendered.classList.remove('hidden');
    } else if (mode === 'source') {
      content.classList.add('view-source');
      source.classList.remove('hidden');
    } else if (mode === 'split') {
      content.classList.add('view-split');
      rendered.classList.remove('hidden');
      source.classList.remove('hidden');
    }

    this.setStatus(`View: ${mode.charAt(0).toUpperCase() + mode.slice(1)}`);
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
        case 'b':
          e.preventDefault();
          this.toggleSidebar();
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
        case 'e':
          e.preventDefault();
          const editBtn = document.getElementById('editBtn');
          if (editBtn && editBtn.style.display !== 'none') {
            editBtn.click();
          }
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
      this.setStatus('Loading files...');
      const response = await fetch('/api/files');
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to load files');
      }

      this.files = data.files || [];
      this.renderFileTree();
      this.setStatus(`Loaded ${this.files.length} files`);
    } catch (error) {
      console.error('Error loading file list:', error);
      this.showError('Failed to load file list: ' + error.message);
      this.setStatus('Error loading files');
    }
  }

  /**
   * Select folder to display
   */
  selectFolder(folder) {
    this.currentFolder = folder;
    localStorage.setItem('md-folder', folder);

    // Update active button
    document.querySelectorAll('.folder-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.folder === folder);
    });

    // Re-render file tree with filter
    this.renderFileTree();

    // Update status
    const folderNames = {
      'all': 'All Files',
      'knowledge': 'Knowledge Base',
      'memory': 'Memory',
      'diagrams': 'Diagrams'
    };
    this.setStatus(`Viewing: ${folderNames[folder]}`);
  }

  /**
   * Render file tree in sidebar
   */
  renderFileTree() {
    const tree = document.getElementById('categoryTree');

    // Filter files by current folder
    let filteredFiles = this.files;
    if (this.currentFolder !== 'all') {
      filteredFiles = this.files.filter(file =>
        file.type === this.currentFolder
      );
    }

    const categories = this.groupByCategory(filteredFiles);

    tree.innerHTML = '';

    // Sort categories alphabetically
    const sortedCategories = Object.entries(categories).sort((a, b) =>
      a[0].localeCompare(b[0])
    );

    for (const [category, files] of sortedCategories) {
      const categoryDiv = document.createElement('div');
      categoryDiv.className = 'category-item';

      const header = document.createElement('div');
      header.className = 'category-header';
      header.innerHTML = `
        <i class="cil-folder category-icon"></i>
        <span class="category-name">${category}</span>
        <span class="file-count">${files.length}</span>
      `;

      header.addEventListener('click', () => {
        const wasExpanded = categoryDiv.classList.contains('expanded');
        categoryDiv.classList.toggle('expanded');

        // Update icon
        const icon = header.querySelector('.category-icon');
        icon.className = wasExpanded ? 'cil-folder category-icon' : 'cil-folder-open category-icon';
      });

      const filesDiv = document.createElement('div');
      filesDiv.className = 'category-files';

      // Sort files alphabetically
      files.sort((a, b) => a.name.localeCompare(b.name));

      files.forEach(file => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item';
        fileDiv.innerHTML = `
          <i class="cil-file file-icon"></i>
          <span class="file-name">${file.name}</span>
          <button class="file-edit-btn" title="Edit in Typo" data-path="${file.path}">
            <i class="cil-pencil"></i>
          </button>
        `;
        fileDiv.dataset.path = file.path;

        // Click on file name to load
        const fileName = fileDiv.querySelector('.file-name');
        fileName.addEventListener('click', (e) => {
          e.stopPropagation();
          this.loadFile(file);
        });

        // Click on edit button to open in Typo
        const editBtn = fileDiv.querySelector('.file-edit-btn');
        editBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.editFile(file);
        });

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
    const resultsDiv = document.getElementById('searchResults');

    if (!query || query.length < 2) {
      resultsDiv.classList.add('hidden');
      return;
    }

    // Filter by current folder first
    let searchFiles = this.files;
    if (this.currentFolder !== 'all') {
      searchFiles = this.files.filter(file => file.type === this.currentFolder);
    }

    const results = searchFiles.filter(file =>
      file.name.toLowerCase().includes(query.toLowerCase()) ||
      file.path.toLowerCase().includes(query.toLowerCase()) ||
      (file.category && file.category.toLowerCase().includes(query.toLowerCase()))
    ).slice(0, 10);

    resultsDiv.innerHTML = '';

    if (results.length === 0) {
      resultsDiv.innerHTML = '<div class="empty-state"><i class="cil-magnifying-glass"></i> No results found</div>';
    } else {
      results.forEach(file => {
        const item = document.createElement('div');
        item.className = 'search-result-item';

        // Highlight matching text
        const nameMatch = this.highlightMatch(file.name, query);

        item.innerHTML = `
          <i class="cil-file"></i>
          <div class="search-result-content">
            <div class="search-result-name">${nameMatch}</div>
            <div class="search-result-path">${file.category || 'Uncategorized'}</div>
          </div>
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
   * Highlight matching text in search results
   */
  highlightMatch(text, query) {
    const index = text.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) return text;

    const before = text.substring(0, index);
    const match = text.substring(index, index + query.length);
    const after = text.substring(index + query.length);

    return `${before}<mark>${match}</mark>${after}`;
  }

  /**
   * Edit file in Typo editor
   */
  editFile(file) {
    const TYPO_PORT = 5173;
    const TYPO_URL = `http://localhost:${TYPO_PORT}`;

    // Open Typo in new tab
    window.open(TYPO_URL, '_blank');

    // Log for debugging/future file system integration
    console.log('Opening Typo for file:', file.path);
    this.setStatus(`Opening ${file.name} in Typo...`);
  }

  /**
   * Load and render a markdown file
   */
  async loadFile(file) {
    this.currentFile = file;

    try {
      this.setStatus(`Loading ${file.name}...`);
      const response = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
      const data = await response.json();

      if (!data.success || !data.content) {
        throw new Error(data.error || 'No content received');
      }

      // Update breadcrumb
      document.getElementById('breadcrumb').innerHTML = `
        <span>${file.category || 'Uncategorized'}</span>
        <span> / </span>
        <span>${file.name}</span>
      `;

      // Show edit button
      const editBtn = document.getElementById('editBtn');
      if (editBtn) {
        editBtn.style.display = 'flex';
      }

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

      this.setStatus(`Loaded: ${file.name}`);

    } catch (error) {
      console.error('Error loading file:', error);
      this.showError('Failed to load file: ' + error.message);
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

    if (!tocContent) return; // Element doesn't exist in minimal design

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

    // Update info panel elements if they exist
    const infoFile = document.getElementById('infoFile');
    const infoCategory = document.getElementById('infoCategory');
    const infoSize = document.getElementById('infoSize');
    const infoLines = document.getElementById('infoLines');
    const infoWords = document.getElementById('infoWords');
    const infoChars = document.getElementById('infoChars');
    const infoHeadings = document.getElementById('infoHeadings');
    const infoCodeBlocks = document.getElementById('infoCodeBlocks');
    const infoUcode = document.getElementById('infoUcode');

    if (infoFile) infoFile.textContent = file.name;
    if (infoCategory) infoCategory.textContent = file.category || 'N/A';
    if (infoSize) infoSize.textContent = this.formatFileSize(chars);
    if (infoLines) infoLines.textContent = lines.toLocaleString();
    if (infoWords) infoWords.textContent = words.toLocaleString();
    if (infoChars) infoChars.textContent = chars.toLocaleString();
    if (infoHeadings) infoHeadings.textContent = headings;
    if (infoCodeBlocks) infoCodeBlocks.textContent = Math.floor(codeBlocks);
    if (infoUcode) infoUcode.textContent = ucodeCmds;
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
   * Set status message
   */
  setStatus(message) {
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
      statusEl.textContent = message;
    }
  }

  /**
   * Show success message
   */
  showMessage(message) {
    this.setStatus(`✓ ${message}`);
    setTimeout(() => this.setStatus('Ready'), 3000);
  }

  /**
   * Show error message
   */
  showError(message) {
    this.setStatus(`✗ ${message}`);
    console.error('Error:', message);
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.markdownViewer = new MarkdownViewer();
});
