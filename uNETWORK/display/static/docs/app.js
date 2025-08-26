// uDOS Documentation Browser - Main Application
class uDOSDocumentationBrowser {
    constructor() {
        this.currentDocument = null;
        this.fileTree = [];
        this.searchIndex = [];
        this.darkMode = localStorage.getItem('udos-dark-mode') === 'true';
        this.fontSize = parseInt(localStorage.getItem('udos-font-size')) || 14;
        this.showToc = localStorage.getItem('udos-show-toc') !== 'false';

        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.loadSettings();
        this.configureMermaid();
        this.configureMarked();
        await this.loadFileTree();
        this.updateConnectionStatus();
    }

    setupEventListeners() {
        // Header controls
        document.getElementById('refreshBtn').addEventListener('click', () => this.refresh());
        document.getElementById('searchBtn').addEventListener('click', () => this.focusSearch());
        document.getElementById('settingsBtn').addEventListener('click', () => this.showSettings());

        // Search
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.performSearch(e.target.value);
        });

        // Display controls
        document.getElementById('darkModeToggle').addEventListener('change', (e) => {
            this.toggleDarkMode(e.target.checked);
        });

        document.getElementById('fontSizeSlider').addEventListener('input', (e) => {
            this.updateFontSize(parseInt(e.target.value));
        });

        document.getElementById('tocToggle').addEventListener('change', (e) => {
            this.toggleToc(e.target.checked);
        });

        // Document actions
        document.getElementById('copyMarkdownBtn').addEventListener('click', () => this.copyMarkdown());
        document.getElementById('copyHtmlBtn').addEventListener('click', () => this.copyHtml());
        document.getElementById('printBtn').addEventListener('click', () => this.printDocument());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    loadSettings() {
        // Apply dark mode
        if (this.darkMode) {
            document.body.setAttribute('data-theme', 'dark');
            document.getElementById('darkModeToggle').checked = true;
        }

        // Apply font size
        document.documentElement.style.setProperty('--base-font-size', `${this.fontSize}px`);
        document.getElementById('fontSizeSlider').value = this.fontSize;

        // Apply TOC visibility
        if (!this.showToc) {
            document.getElementById('tocPanel').classList.add('hidden');
        }
        document.getElementById('tocToggle').checked = this.showToc;
    }

    configureMermaid() {
        mermaid.initialize({
            startOnLoad: true,
            theme: this.darkMode ? 'dark' : 'default',
            themeVariables: {
                primaryColor: '#0969da',
                primaryTextColor: this.darkMode ? '#f0f6fc' : '#24292f',
                primaryBorderColor: this.darkMode ? '#30363d' : '#d0d7de',
                lineColor: this.darkMode ? '#6e7681' : '#656d76'
            }
        });
    }

    configureMarked() {
        // Configure marked for GitHub-compatible markdown
        marked.setOptions({
            gfm: true,
            breaks: false,
            pedantic: false,
            sanitize: false,
            smartypants: false,
            highlight: function (code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) { }
                }
                return hljs.highlightAuto(code).value;
            }
        });

        // Custom renderer for better GitHub compatibility
        const renderer = new marked.Renderer();

        // Custom heading renderer with anchor links
        renderer.heading = function (text, level) {
            const id = text.toLowerCase().replace(/[^\w]+/g, '-');
            return `<h${level} id="${id}">
                        <a href="#${id}" class="header-link">${text}</a>
                    </h${level}>`;
        };

        // Custom checkbox renderer for task lists
        renderer.listitem = function (text) {
            if (/^\s*\[[x ]\]\s*/.test(text)) {
                text = text
                    .replace(/^\s*\[ \]\s*/, '<input type="checkbox" class="task-list-item-checkbox" disabled> ')
                    .replace(/^\s*\[x\]\s*/, '<input type="checkbox" class="task-list-item-checkbox" checked disabled> ');
                return `<li class="task-list-item">${text}</li>`;
            }
            return `<li>${text}</li>`;
        };

        // Custom table renderer
        renderer.table = function (header, body) {
            return `<div class="table-wrapper">
                        <table>
                            <thead>${header}</thead>
                            <tbody>${body}</tbody>
                        </table>
                    </div>`;
        };

        marked.use({ renderer });
    }

    async loadFileTree() {
        try {
            // This would normally fetch from the server
            // For now, we'll simulate with a static tree
            this.fileTree = await this.fetchFileTree();
            this.renderFileTree();
            this.buildSearchIndex();
        } catch (error) {
            console.error('Error loading file tree:', error);
            this.showError('Failed to load documentation files');
        }
    }

    async fetchFileTree() {
        try {
            const response = await fetch('/api/docs/tree');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching file tree:', error);
            throw error;
        }
    }

    renderFileTree() {
        const container = document.getElementById('fileTree');
        container.innerHTML = '';

        const renderNode = (node, level = 0) => {
            const item = document.createElement('div');
            item.className = 'tree-item';
            item.style.paddingLeft = `${level * 16}px`;

            if (node.type === 'folder') {
                item.innerHTML = `<span class="icon">📁</span> ${node.name}`;
                container.appendChild(item);

                if (node.children) {
                    node.children.forEach(child => renderNode(child, level + 1));
                }
            } else {
                item.innerHTML = `<span class="icon">📄</span> ${node.name}`;
                item.addEventListener('click', () => this.loadDocument(node.path));
                container.appendChild(item);
            }
        };

        this.fileTree.forEach(node => renderNode(node));
    }

    buildSearchIndex() {
        // Build search index for quick searching
        this.searchIndex = [];

        const indexNode = (node, path = '') => {
            if (node.type === 'file' && node.name.endsWith('.md')) {
                this.searchIndex.push({
                    name: node.name,
                    path: node.path,
                    fullPath: path + '/' + node.name
                });
            } else if (node.type === 'folder' && node.children) {
                node.children.forEach(child =>
                    indexNode(child, path + '/' + node.name)
                );
            }
        };

        this.fileTree.forEach(node => indexNode(node));
    }

    async loadDocument(path) {
        try {
            document.getElementById('documentPath').textContent = path;

            // This would normally fetch from the server
            const markdown = await this.fetchDocument(path);
            const html = marked.parse(markdown);

            const contentDiv = document.getElementById('documentContent');
            contentDiv.innerHTML = html;

            // Re-initialize highlighting
            contentDiv.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });

            // Re-initialize mermaid
            contentDiv.querySelectorAll('.mermaid').forEach(element => {
                mermaid.init(undefined, element);
            });

            // Update TOC
            this.generateTableOfContents(contentDiv);

            // Update document stats
            this.updateDocumentStats(markdown);

            // Highlight active file in tree
            this.highlightActiveFile(path);

            this.currentDocument = { path, markdown, html };

        } catch (error) {
            console.error('Error loading document:', error);
            this.showError(`Failed to load document: ${path}`);
        }
    }

    async fetchDocument(path) {
        try {
            const response = await fetch(`/api/docs/content?path=${encodeURIComponent(path)}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            return data.content;
        } catch (error) {
            console.error('Error fetching document:', error);
            throw error;
        }
    }

    generateTableOfContents(contentDiv) {
        const headings = contentDiv.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const tocContent = document.getElementById('tocContent');

        if (headings.length === 0) {
            tocContent.innerHTML = '<div class="toc-empty">No headings found</div>';
            return;
        }

        tocContent.innerHTML = '';

        headings.forEach(heading => {
            const level = parseInt(heading.tagName.substring(1));
            const text = heading.textContent;
            const id = heading.id || text.toLowerCase().replace(/[^\w]+/g, '-');

            if (!heading.id) {
                heading.id = id;
            }

            const tocItem = document.createElement('a');
            tocItem.className = `toc-item level-${level}`;
            tocItem.href = `#${id}`;
            tocItem.textContent = text;
            tocItem.addEventListener('click', (e) => {
                e.preventDefault();
                heading.scrollIntoView({ behavior: 'smooth' });
            });

            tocContent.appendChild(tocItem);
        });
    }

    async handleSearch(query) {
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }

        try {
            const response = await fetch(`/api/docs/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            this.showSearchResults(data.results, query);
        } catch (error) {
            console.error('Error searching:', error);
            this.showSearchResults([], query);
        }
    }

    showSearchResults(results, query) {
        const container = document.getElementById('searchResults');
        container.innerHTML = '';

        if (results.length === 0) {
            container.innerHTML = '<div class="search-result">No results found</div>';
        } else {
            results.forEach(result => {
                const item = document.createElement('div');
                item.className = 'search-result';

                if (result.type === 'filename') {
                    item.innerHTML = `
                        <div style="font-weight: 500;">📄 ${result.name}</div>
                        <div style="font-size: 11px; color: var(--text-tertiary);">${result.path}</div>
                    `;
                } else {
                    item.innerHTML = `
                        <div style="font-weight: 500;">📄 ${result.name}</div>
                        <div style="font-size: 11px; color: var(--text-secondary); margin: 2px 0;">${result.match}</div>
                        <div style="font-size: 10px; color: var(--text-tertiary);">${result.path}:${result.line}</div>
                    `;
                }

                item.addEventListener('click', () => {
                    this.loadDocument(result.path);
                    this.hideSearchResults();
                });
                container.appendChild(item);
            });
        }

        container.style.display = 'block';
    }

    hideSearchResults() {
        document.getElementById('searchResults').style.display = 'none';
    }

    toggleDarkMode(enabled) {
        this.darkMode = enabled;
        localStorage.setItem('udos-dark-mode', enabled);

        if (enabled) {
            document.body.setAttribute('data-theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
        }

        // Reconfigure mermaid for theme change
        this.configureMermaid();

        // Re-render any mermaid diagrams
        document.querySelectorAll('.mermaid').forEach(element => {
            mermaid.init(undefined, element);
        });
    }

    updateFontSize(size) {
        this.fontSize = size;
        localStorage.setItem('udos-font-size', size);
        document.documentElement.style.setProperty('--base-font-size', `${size}px`);
    }

    toggleToc(show) {
        this.showToc = show;
        localStorage.setItem('udos-show-toc', show);

        const tocPanel = document.getElementById('tocPanel');
        if (show) {
            tocPanel.classList.remove('hidden');
        } else {
            tocPanel.classList.add('hidden');
        }
    }

    copyMarkdown() {
        if (!this.currentDocument) return;

        navigator.clipboard.writeText(this.currentDocument.markdown).then(() => {
            this.showNotification('Markdown copied to clipboard');
        });
    }

    copyHtml() {
        if (!this.currentDocument) return;

        navigator.clipboard.writeText(this.currentDocument.html).then(() => {
            this.showNotification('HTML copied to clipboard');
        });
    }

    printDocument() {
        window.print();
    }

    focusSearch() {
        document.getElementById('searchInput').focus();
    }

    refresh() {
        location.reload();
    }

    showSettings() {
        alert('Settings panel would open here');
    }

    handleKeyboard(e) {
        // Ctrl/Cmd + F for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            this.focusSearch();
        }

        // Ctrl/Cmd + D for dark mode toggle
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const toggle = document.getElementById('darkModeToggle');
            toggle.checked = !toggle.checked;
            this.toggleDarkMode(toggle.checked);
        }

        // Escape to close search results
        if (e.key === 'Escape') {
            this.hideSearchResults();
        }
    }

    updateDocumentStats(markdown) {
        const words = markdown.split(/\s+/).length;
        const chars = markdown.length;
        const lines = markdown.split('\n').length;

        document.getElementById('documentStats').textContent =
            `${words} words • ${lines} lines • ${chars} characters`;
    }

    highlightActiveFile(path) {
        // Remove previous active state
        document.querySelectorAll('.tree-item.active').forEach(item => {
            item.classList.remove('active');
        });

        // Add active state to current file
        document.querySelectorAll('.tree-item').forEach(item => {
            if (item.textContent.trim().endsWith(path.split('/').pop())) {
                item.classList.add('active');
            }
        });
    }

    updateConnectionStatus() {
        document.getElementById('connectionStatus').textContent = '🌐 Connected to uDOS';
    }

    showError(message) {
        document.getElementById('documentContent').innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--accent-red);">
                <h2>❌ Error</h2>
                <p>${message}</p>
                <button onclick="location.reload()" style="margin-top: 16px; padding: 8px 16px; border: 1px solid var(--accent-red); background: transparent; color: var(--accent-red); border-radius: 4px; cursor: pointer;">
                    Retry
                </button>
            </div>
        `;
    }

    showNotification(message) {
        // Simple notification - could be enhanced with a proper notification system
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-green);
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new uDOSDocumentationBrowser();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
