/*
 * uDOS Application JavaScript
 * Universal Device Operating System v1.0.4.1
 * Main application controller with tab management, theming, and WebSocket integration
 */

class UDOSApp {
    constructor() {
        this.socket = null;
        this.currentTab = 'dashboard';
        this.currentTheme = 'polaroid';
        this.currentGridSize = 'medium';
        this.currentFont = 'mono';
        this.systemData = {};
        this.isLoading = true;
        this.settings = {
            theme: 'polaroid',
            gridSize: 'medium',
            font: 'mono',
            layout: 'grid'
        };

        this.init();
    }

    async init() {
        console.log('🎯 Initializing uDOS Application...');

        // Show loading screen
        this.showLoadingScreen();

        // Load settings from localStorage
        this.loadSettings();

        // Initialize WebSocket connection
        this.initWebSocket();

        // Set up event listeners
        this.initEventListeners();

        // Apply initial theme and settings
        this.applySettings();

        // Initialize modules
        this.initModules();

        // Initialize role-based prompt
        this.initRolePrompt();

        // Hide loading screen after initialization
        setTimeout(() => {
            this.hideLoadingScreen();
        }, 2500);
    }

    showLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        const progressBar = document.getElementById('loadingProgress');

        if (loadingScreen && progressBar) {
            loadingScreen.style.display = 'flex';
            progressBar.style.width = '100%';
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        const mainApp = document.getElementById('mainApp');

        if (loadingScreen && mainApp) {
            loadingScreen.style.display = 'none';
            mainApp.style.display = 'block';
            this.isLoading = false;

            // Trigger initial data load
            this.refreshSystemData();
            this.logActivity('uDOS Application Ready');
        }
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('udos-settings');
        if (savedSettings) {
            try {
                this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
                console.log('📝 Loaded settings:', this.settings);
            } catch (error) {
                console.warn('⚠️ Error loading settings:', error);
            }
        }
    }

    saveSettings() {
        localStorage.setItem('udos-settings', JSON.stringify(this.settings));
        console.log('💾 Settings saved:', this.settings);
    }

    applySettings() {
        const { theme, gridSize, font, layout } = this.settings;

        // Apply theme
        document.body.setAttribute('data-theme', theme);
        this.currentTheme = theme;

        // Apply grid size
        document.body.setAttribute('data-grid-size', gridSize);
        this.currentGridSize = gridSize;

        // Apply font
        document.body.classList.remove('font-mono', 'font-roboto', 'font-space', 'font-courier');
        document.body.classList.add(`font-${font}`);
        this.currentFont = font;

        // Update UI controls
        this.updateSettingsUI();
    }

    updateSettingsUI() {
        const themeSelector = document.getElementById('themeSelector');
        const gridSizeSelector = document.getElementById('gridSizeSelector');
        const fontSelector = document.getElementById('fontSelector');
        const layoutSelector = document.getElementById('layoutSelector');

        if (themeSelector) themeSelector.value = this.settings.theme;
        if (gridSizeSelector) gridSizeSelector.value = this.settings.gridSize;
        if (fontSelector) fontSelector.value = this.settings.font;
        if (layoutSelector) layoutSelector.value = this.settings.layout;
    }

    initWebSocket() {
        try {
            this.socket = io();

            this.socket.on('connect', () => {
                console.log('🌐 WebSocket connected');
                this.updateConnectionStatus(true);
                this.logActivity('Connected to uDOS Server');
            });

            this.socket.on('disconnect', () => {
                console.log('🌐 WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.logActivity('Disconnected from uDOS Server');
            });

            this.socket.on('system_update', (data) => {
                this.handleSystemUpdate(data);
            });

            this.socket.on('command_result', (data) => {
                this.handleCommandResult(data);
            });

            this.socket.on('error', (error) => {
                console.error('❌ WebSocket error:', error);
                this.logActivity(`Error: ${error.message}`, 'error');
            });

        } catch (error) {
            console.error('❌ WebSocket initialization failed:', error);
            this.updateConnectionStatus(false);
        }
    }

    initEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Command input with enhanced features
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            // Initialize cursor and smart input
            this.initCommandCursor();
            this.initSmartInput();

            commandInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.executeCommand(e.target.value);
                } else if (e.key === '/') {
                    this.showCommandSuggestions();
                } else if (e.key === 'Tab') {
                    e.preventDefault();
                    this.handleTabCompletion();
                }
            });

            commandInput.addEventListener('input', (e) => {
                this.handleCommandInput(e.target.value);
                this.updateCursor();
            });

            commandInput.addEventListener('focus', () => {
                this.activateCursor();
            });

            commandInput.addEventListener('blur', () => {
                this.deactivateCursor();
            });
        }

        // Command buttons
        document.getElementById('executeBtn')?.addEventListener('click', () => {
            const input = document.getElementById('commandInput');
            if (input) this.executeCommand(input.value);
        });

        document.getElementById('clearBtn')?.addEventListener('click', () => {
            const input = document.getElementById('commandInput');
            if (input) input.value = '';
        });

        document.getElementById('historyBtn')?.addEventListener('click', () => {
            this.showCommandHistory();
        });

        // Settings panel
        document.getElementById('settingsBtn')?.addEventListener('click', () => {
            this.toggleSettings();
        });

        document.getElementById('settingsClose')?.addEventListener('click', () => {
            this.closeSettings();
        });

        // Settings controls
        document.getElementById('themeSelector')?.addEventListener('change', (e) => {
            this.changeTheme(e.target.value);
        });

        document.getElementById('gridSizeSelector')?.addEventListener('change', (e) => {
            this.changeGridSize(e.target.value);
        });

        document.getElementById('fontSelector')?.addEventListener('change', (e) => {
            this.changeFont(e.target.value);
        });

        document.getElementById('layoutSelector')?.addEventListener('change', (e) => {
            this.changeLayout(e.target.value);
        });

        // Quick actions
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.getAttribute('data-action');
                this.executeQuickAction(action);
            });
        });

        // Panel toggles
        document.querySelectorAll('.panel-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const panel = e.currentTarget.getAttribute('data-panel');
                this.togglePanel(panel);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    initModules() {
        // Initialize terminal module
        if (window.UDOSTerminal) {
            this.terminal = new UDOSTerminal(this.socket);
        }

        // Initialize grid module
        if (window.UDOSGrid) {
            this.grid = new UDOSGrid();
        }

        // Initialize smart input module
        if (window.UDOSSmartInput) {
            this.smartInput = new UDOSSmartInput();
        }
    }

    switchTab(tabName) {
        if (this.currentTab === tabName) return;

        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}Tab`)?.classList.add('active');

        this.currentTab = tabName;
        this.logActivity(`Switched to ${tabName} tab`);

        // Tab-specific initialization
        switch (tabName) {
            case 'terminal':
                this.terminal?.focus();
                break;
            case 'grid':
                this.grid?.refresh();
                break;
            case 'memory':
                this.loadMemoryBrowser();
                break;
            case 'map':
                this.loadMapTiles();
                break;
        }
    }

    executeCommand(command) {
        if (!command.trim()) return;

        this.logActivity(`Executing: ${command}`);

        // Clear input
        const input = document.getElementById('commandInput');
        if (input) input.value = '';

        // Send command to server
        if (this.socket) {
            this.socket.emit('execute_command', { command });
        } else {
            this.logActivity('Error: Not connected to server', 'error');
        }

        // Add to command history
        this.addToCommandHistory(command);
    }

    handleCommandInput(value) {
        if (value.startsWith('/')) {
            this.showCommandSuggestions(value.slice(1));
        } else {
            this.hideCommandSuggestions();
        }
    }

    showCommandSuggestions(query = '') {
        const suggestions = this.getCommandSuggestions(query);
        const container = document.getElementById('commandSuggestions');

        if (!container) return;

        if (suggestions.length > 0) {
            container.innerHTML = suggestions.map(cmd =>
                `<div class="suggestion-item" data-command="${cmd.command}">
                    <strong>${cmd.command}</strong> - ${cmd.description}
                </div>`
            ).join('');

            container.style.display = 'block';

            // Add click handlers
            container.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const input = document.getElementById('commandInput');
                    if (input) {
                        input.value = item.getAttribute('data-command');
                        input.focus();
                    }
                    this.hideCommandSuggestions();
                });
            });
        } else {
            this.hideCommandSuggestions();
        }
    }

    hideCommandSuggestions() {
        const container = document.getElementById('commandSuggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    getCommandSuggestions(query) {
        const commands = [
            { command: 'status', description: 'Show system status' },
            { command: 'help', description: 'Show help information' },
            { command: 'backup', description: 'Create system backup' },
            { command: 'logs', description: 'View system logs' },
            { command: 'memory', description: 'Show memory usage' },
            { command: 'grid', description: 'Display grid view' },
            { command: 'map', description: 'Show map tiles' },
            { command: 'theme', description: 'Change color theme' },
            { command: 'clear', description: 'Clear terminal' },
            { command: 'exit', description: 'Exit application' }
        ];

        if (!query) return commands.slice(0, 5);

        return commands.filter(cmd =>
            cmd.command.toLowerCase().includes(query.toLowerCase()) ||
            cmd.description.toLowerCase().includes(query.toLowerCase())
        );
    }

    addToCommandHistory(command) {
        let history = JSON.parse(localStorage.getItem('udos-command-history') || '[]');
        history.unshift(command);
        history = history.slice(0, 50); // Keep last 50 commands
        localStorage.setItem('udos-command-history', JSON.stringify(history));
    }

    showCommandHistory() {
        const history = JSON.parse(localStorage.getItem('udos-command-history') || '[]');

        if (history.length === 0) {
            this.logActivity('No command history available');
            return;
        }

        // Create history modal or display
        const historyText = history.slice(0, 10).join('\n');
        this.logActivity(`Recent commands:\n${historyText}`);
    }

    executeQuickAction(action) {
        const actions = {
            status: () => this.executeCommand('status'),
            backup: () => this.executeCommand('backup'),
            logs: () => this.executeCommand('logs'),
            help: () => this.executeCommand('help')
        };

        if (actions[action]) {
            actions[action]();
        } else {
            this.logActivity(`Unknown action: ${action}`, 'error');
        }
    }

    togglePanel(panelName) {
        const panel = document.querySelector(`.panel.${panelName}`);
        const toggle = document.querySelector(`[data-panel="${panelName}"]`);

        if (panel && toggle) {
            const content = panel.querySelector('.panel-content');
            const isCollapsed = content.style.display === 'none';

            content.style.display = isCollapsed ? 'block' : 'none';
            toggle.textContent = isCollapsed ? '−' : '+';
        }
    }

    changeTheme(theme) {
        this.settings.theme = theme;
        this.applySettings();
        this.saveSettings();
        this.logActivity(`Theme changed to ${theme}`);
    }

    changeGridSize(size) {
        this.settings.gridSize = size;
        this.applySettings();
        this.saveSettings();
        this.logActivity(`Grid size changed to ${size}`);
    }

    changeFont(font) {
        this.settings.font = font;
        this.applySettings();
        this.saveSettings();
        this.logActivity(`Font changed to ${font}`);
    }

    changeLayout(layout) {
        this.settings.layout = layout;
        this.saveSettings();
        this.logActivity(`Layout changed to ${layout}`);
    }

    toggleSettings() {
        const panel = document.getElementById('settingsPanel');
        if (panel) {
            panel.classList.toggle('open');
        }
    }

    closeSettings() {
        const panel = document.getElementById('settingsPanel');
        if (panel) {
            panel.classList.remove('open');
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + shortcuts
        if (e.metaKey || e.ctrlKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.switchTab('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.switchTab('terminal');
                    break;
                case '3':
                    e.preventDefault();
                    this.switchTab('memory');
                    break;
                case '4':
                    e.preventDefault();
                    this.switchTab('grid');
                    break;
                case '5':
                    e.preventDefault();
                    this.switchTab('map');
                    break;
                case ',':
                    e.preventDefault();
                    this.toggleSettings();
                    break;
            }
        }

        // Escape key
        if (e.key === 'Escape') {
            this.closeSettings();
            this.hideCommandSuggestions();
        }
    }

    handleResize() {
        // Handle responsive adjustments
        if (this.grid) {
            this.grid.handleResize();
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.querySelector('.status-indicator');
        const text = document.querySelector('.status-text');

        if (indicator && text) {
            if (connected) {
                indicator.classList.add('online');
                indicator.classList.remove('offline');
                text.textContent = 'Connected';
            } else {
                indicator.classList.remove('online');
                indicator.classList.add('offline');
                text.textContent = 'Disconnected';
            }
        }
    }

    handleSystemUpdate(data) {
        this.systemData = { ...this.systemData, ...data };
        this.updateSystemMetrics(data);

        if (data.type === 'stats') {
            this.updateStats(data);
        }
    }

    handleCommandResult(data) {
        this.logActivity(`Command result: ${data.result}`);

        if (this.terminal) {
            this.terminal.addOutput(data.result, data.type || 'info');
        }
    }

    updateSystemMetrics(data) {
        if (data.cpu !== undefined) {
            this.updateMetric('cpu', data.cpu);
        }

        if (data.memory !== undefined) {
            this.updateMetric('memory', data.memory);
        }

        if (data.storage !== undefined) {
            this.updateMetric('storage', data.storage);
        }
    }

    updateMetric(type, percentage) {
        const stat = document.getElementById(`${type}Stat`);
        const bar = document.getElementById(`${type}Bar`);

        if (stat && bar) {
            stat.textContent = `${percentage}%`;
            bar.style.width = `${percentage}%`;

            // Color coding based on usage
            let color = 'var(--accent-green)';
            if (percentage > 80) color = 'var(--accent-red)';
            else if (percentage > 60) color = 'var(--accent-yellow)';

            bar.style.background = `linear-gradient(90deg, ${color}, var(--accent-blue))`;
        }
    }

    updateStats(data) {
        // Update ASCII display
        this.updateASCIIDisplay(data);
    }

    updateASCIIDisplay(data) {
        const container = document.getElementById('asciiArt');
        if (!container) return;

        const status = data.status || 'Unknown';
        const memory = data.memory || 0;
        const network = data.network || 'Offline';

        const asciiContent = `
┌─────────────────────────────────────┐
│  uDOS Operating System Dashboard    │
├─────────────────────────────────────┤
│  ██ CORE    │ ██ MEMORY │ ██ NET   │
│  ░░ ${status.padEnd(6)} │ ░░ ${memory}%    │ ░░ ${network.padEnd(4)} │
│                                     │
│  [●] Active [●] Online [●] Ready    │
└─────────────────────────────────────┘`;

        container.textContent = asciiContent;
    }

    refreshSystemData() {
        if (this.socket) {
            this.socket.emit('get_system_status');
        }

        // Update timestamp
        const now = new Date();
        this.logActivity(`System data refreshed at ${now.toLocaleTimeString()}`);
    }

    loadMemoryBrowser() {
        // Load memory browser content
        if (this.socket) {
            this.socket.emit('get_memory_structure');
        }
    }

    loadMapTiles() {
        // Load map tiles
        if (this.socket) {
            this.socket.emit('get_map_tiles');
        }
    }

    logActivity(message, type = 'info') {
        const log = document.getElementById('activityLog');
        if (!log) return;

        const now = new Date();
        const timeStr = now.toLocaleTimeString();

        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="log-time">${timeStr}</span>
            <span class="log-type">${type.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;

        log.insertBefore(entry, log.firstChild);

        // Keep only last 50 entries
        while (log.children.length > 50) {
            log.removeChild(log.lastChild);
        }

        console.log(`📝 ${type.toUpperCase()}: ${message}`);
    }

    // Command cursor management
    initCommandCursor() {
        this.cursorPosition = 0;
        this.cursorElement = document.getElementById('inputCursor');
        this.inputElement = document.getElementById('commandInput');

        if (this.cursorElement && this.inputElement) {
            // Position cursor initially
            this.updateCursor();

            // Show ready animation when input is focused
            setTimeout(() => {
                this.showReadyAnimation();
            }, 500);
        }
    }

    updateCursor() {
        if (!this.cursorElement || !this.inputElement) return;

        const input = this.inputElement;
        const cursor = this.cursorElement;

        // Create a temporary element to measure text width
        const temp = document.createElement('span');
        temp.style.visibility = 'hidden';
        temp.style.position = 'absolute';
        temp.style.font = window.getComputedStyle(input).font;
        temp.textContent = input.value.substring(0, input.selectionStart);
        document.body.appendChild(temp);

        const textWidth = temp.offsetWidth;
        document.body.removeChild(temp);

        // Position cursor
        cursor.style.left = `${textWidth + 2}px`;
    }

    activateCursor() {
        if (this.cursorElement) {
            this.cursorElement.classList.add('active');
            this.cursorElement.classList.remove('ready');
        }
    }

    deactivateCursor() {
        if (this.cursorElement) {
            this.cursorElement.classList.remove('active');
        }
    }

    showReadyAnimation() {
        if (this.cursorElement) {
            this.cursorElement.classList.add('ready');
            setTimeout(() => {
                this.cursorElement.classList.remove('ready');
            }, 1800); // 3 blinks × 0.6s
        }
    }

    // Role-based prompt management
    initRolePrompt() {
        this.userRole = 'wizard'; // Default role, should be fetched from server
        this.updatePrompt();
    }

    updatePrompt() {
        const promptEmoji = document.getElementById('promptEmoji');
        const promptText = document.getElementById('promptText');
        const promptContainer = document.getElementById('commandPrompt');

        if (!promptEmoji || !promptText || !promptContainer) return;

        const roleConfig = this.getRoleConfig(this.userRole);

        promptEmoji.textContent = roleConfig.emoji;
        promptText.textContent = `${this.userRole}$`;

        // Update CSS class for role-based styling
        promptContainer.className = `command-prompt role-${this.userRole}`;
    }

    getRoleConfig(role) {
        const roleConfigs = {
            wizard: { emoji: '🧙‍♂️', color: 'var(--accent-purple)' },
            sorcerer: { emoji: '🔮', color: 'var(--accent-blue)' },
            knight: { emoji: '⚔️', color: 'var(--accent-green)' },
            imp: { emoji: '👺', color: 'var(--accent-yellow)' },
            drone: { emoji: '🤖', color: 'var(--accent-cyan)' },
            crypt: { emoji: '🏰', color: 'var(--accent-red)' },
            tomb: { emoji: '⚰️', color: 'var(--text-secondary)' },
            ghost: { emoji: '👻', color: 'var(--text-muted)' }
        };

        return roleConfigs[role] || roleConfigs.ghost;
    }

    // Smart input initialization
    initSmartInput() {
        if (typeof UDOSSmartInput !== 'undefined') {
            this.smartInput = new UDOSSmartInput();
            this.smartInput.attachToInput('commandInput');
            console.log('🧠 Smart Input System attached to command bar');
        } else {
            console.warn('⚠️ UDOSSmartInput class not found');
        }
    }

    // Tab completion
    handleTabCompletion() {
        if (this.smartInput) {
            this.smartInput.performTabCompletion();
        }
    }

    // Enhanced command handling
    handleCommandInput(value) {
        if (this.smartInput) {
            this.smartInput.processInput(value);
        }

        // Update suggestions based on input
        this.updateCommandSuggestions(value);
    }

    updateCommandSuggestions(value) {
        const suggestionsElement = document.getElementById('commandSuggestions');
        if (!suggestionsElement) return;

        if (value.length < 2) {
            suggestionsElement.style.display = 'none';
            return;
        }

        // Basic command suggestions (enhanced by smart input)
        const commonCommands = [
            '[STATUS]', '[HELP]', '[EDIT]', '[SHOW]', '[GRID]', '[MAP]',
            '[BACKUP]', '[ROLE]', '[WORKFLOW]', '[TEMPLATE]'
        ];

        const matches = commonCommands.filter(cmd =>
            cmd.toLowerCase().includes(value.toLowerCase())
        );

        if (matches.length > 0) {
            suggestionsElement.innerHTML = matches
                .slice(0, 5)
                .map(cmd => `<div class="suggestion-item">${cmd}</div>`)
                .join('');
            suggestionsElement.style.display = 'block';
        } else {
            suggestionsElement.style.display = 'none';
        }
    }

    // Public methods for external access
    getSocket() {
        return this.socket;
    }

    getCurrentTab() {
        return this.currentTab;
    }

    getSettings() {
        return { ...this.settings };
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 uDOS Application Starting...');
    window.udosApp = new UDOSApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.udosApp && window.udosApp.socket) {
        window.udosApp.socket.disconnect();
    }
});
