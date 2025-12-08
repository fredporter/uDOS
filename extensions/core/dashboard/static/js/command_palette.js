/**
 * Command Palette Service
 * Provides fuzzy search and quick access to dashboard features
 */

class CommandPalette {
    constructor() {
        this.commands = new Map();
        this.categories = new Set();
        this.visible = false;
        this.currentResults = [];
        this.selectedIndex = 0;
        this.setupUI();
        this.registerBuiltInCommands();
    }

    setupUI() {
        // Create command palette HTML
        const palette = document.createElement('div');
        palette.id = 'command-palette';
        palette.className = 'command-palette hidden';
        palette.innerHTML = `
            <div class="command-palette-content">
                <div class="command-input-wrapper">
                    <i class="fas fa-search"></i>
                    <input type="text" class="command-input" placeholder="Type a command or search...">
                    <span class="command-shortcut">ESC to close</span>
                </div>
                <div class="command-results"></div>
            </div>
        `;
        document.body.appendChild(palette);

        this.paletteEl = palette;
        this.inputEl = palette.querySelector('.command-input');
        this.resultsEl = palette.querySelector('.command-results');

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Global shortcut (Cmd/Ctrl + K)
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
        });

        // Close on Escape
        this.inputEl.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Escape':
                    this.hide();
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.selectNext();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.selectPrevious();
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.executeSelected();
                    break;
            }
        });

        // Search on input
        this.inputEl.addEventListener('input', () => {
            this.search(this.inputEl.value);
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.paletteEl.contains(e.target)) {
                this.hide();
            }
        });
    }

    registerBuiltInCommands() {
        // System commands
        this.registerCommand('system', 'Toggle Theme', 'Switch between available themes', () => window.dashboardAPI.toggleTheme());
        this.registerCommand('system', 'Refresh Dashboard', 'Reload all dashboard data', () => window.dashboardAPI.refreshData());
        this.registerCommand('system', 'Open Settings', 'Configure dashboard settings', () => window.dashboardAPI.openSettings());

        // View commands
        this.registerCommand('view', 'Show System Metrics', 'Display CPU, memory, and disk usage', () => this.focusWidget('system-metrics'));
        this.registerCommand('view', 'Show File Browser', 'Open the file browser interface', () => this.focusWidget('file-browser'));
        this.registerCommand('view', 'Show Process List', 'View running processes', () => this.focusWidget('process-list'));
        this.registerCommand('view', 'Show Network Stats', 'View network statistics', () => this.focusWidget('network-stats'));

        // File operations
        this.registerCommand('files', 'Refresh Files', 'Reload file browser', () => window.dashboardAPI.fileBrowser?.loadDirectory());
        this.registerCommand('files', 'Go to Home', 'Navigate to home directory', () => window.dashboardAPI.fileBrowser?.loadDirectory(''));

        // Server management
        this.registerCommand('server', 'Server Status', 'View all server statuses', () => window.dashboardAPI.showServerStatus());
        this.registerCommand('server', 'Start All Servers', 'Start all available servers', () => window.dashboardAPI.startAllServers());
        this.registerCommand('server', 'Stop All Servers', 'Stop all running servers', () => window.dashboardAPI.stopAllServers());
    }

    registerCommand(category, name, description, action) {
        this.commands.set(name, { category, description, action });
        this.categories.add(category);
    }

    search(query) {
        if (!query) {
            this.showAllCommands();
            return;
        }

        const results = Array.from(this.commands.entries())
            .map(([name, cmd]) => ({
                name,
                score: this.fuzzyScore(query, name),
                ...cmd
            }))
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score);

        this.currentResults = results;
        this.selectedIndex = 0;
        this.renderResults();
    }

    fuzzyScore(query, text) {
        const queryLower = query.toLowerCase();
        const textLower = text.toLowerCase();
        let score = 0;
        let lastIndex = -1;

        for (let i = 0; i < queryLower.length; i++) {
            const char = queryLower[i];
            const index = textLower.indexOf(char, lastIndex + 1);

            if (index === -1) return 0;

            score += 1;
            // Bonus points for consecutive matches and matches after spaces
            if (index === lastIndex + 1) score += 2;
            if (index === 0 || textLower[index - 1] === ' ') score += 3;

            lastIndex = index;
        }

        return score;
    }

    showAllCommands() {
        this.currentResults = Array.from(this.commands.entries())
            .map(([name, cmd]) => ({ name, ...cmd }))
            .sort((a, b) => a.category.localeCompare(b.category));
        this.selectedIndex = 0;
        this.renderResults();
    }

    renderResults() {
        const html = this.currentResults.map((result, index) => `
            <div class="command-result ${index === this.selectedIndex ? 'selected' : ''}"
                 data-index="${index}">
                <div class="command-result-content">
                    <i class="fas fa-${this.getCategoryIcon(result.category)}"></i>
                    <div class="command-info">
                        <div class="command-name">${result.name}</div>
                        <div class="command-description">${result.description}</div>
                    </div>
                </div>
                <div class="command-category">${result.category}</div>
            </div>
        `).join('');

        this.resultsEl.innerHTML = html;

        // Ensure selected item is visible
        const selectedEl = this.resultsEl.querySelector('.selected');
        if (selectedEl) {
            selectedEl.scrollIntoView({ block: 'nearest' });
        }
    }

    getCategoryIcon(category) {
        const icons = {
            system: 'cog',
            view: 'eye',
            files: 'folder',
            server: 'server'
        };
        return icons[category] || 'chevron-right';
    }

    selectNext() {
        this.selectedIndex = (this.selectedIndex + 1) % this.currentResults.length;
        this.renderResults();
    }

    selectPrevious() {
        this.selectedIndex = (this.selectedIndex - 1 + this.currentResults.length) % this.currentResults.length;
        this.renderResults();
    }

    executeSelected() {
        const selected = this.currentResults[this.selectedIndex];
        if (selected) {
            this.hide();
            selected.action();
        }
    }

    toggle() {
        this.visible ? this.hide() : this.show();
    }

    show() {
        this.visible = true;
        this.paletteEl.classList.remove('hidden');
        this.inputEl.value = '';
        this.inputEl.focus();
        this.showAllCommands();
    }

    hide() {
        this.visible = false;
        this.paletteEl.classList.add('hidden');
        this.inputEl.value = '';
        this.currentResults = [];
        this.selectedIndex = 0;
    }

    focusWidget(widgetId) {
        const widget = document.getElementById(widgetId);
        if (widget) {
            widget.scrollIntoView({ behavior: 'smooth', block: 'center' });
            widget.classList.add('widget-highlight');
            setTimeout(() => widget.classList.remove('widget-highlight'), 2000);
        }
    }
}
