/**
 * uDOS Dashboard Builder v1.0.24
 * Arcade-Style Customizable Dashboard System
 */

class DashboardBuilder {
    constructor() {
        this.widgets = new Map();
        this.layout = this.loadLayout() || this.getDefaultLayout();
        this.editMode = false;
        this.selectedWidget = null;
        this.widgetTemplates = this.getWidgetTemplates();
        this.themes = this.getThemes();
        this.currentTheme = localStorage.getItem('dashboard-theme') || 'synthwave';

        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.renderDashboard();
        this.attachEventListeners();
        this.startAutoUpdates();

        console.log('🎮 Dashboard Builder initialized');
    }

    getDefaultLayout() {
        return {
            columns: 3,
            widgets: [
                { id: 'system-monitor', type: 'system-monitor', position: 0, enabled: true },
                { id: 'quick-actions', type: 'quick-actions', position: 1, enabled: true },
                { id: 'extensions', type: 'extensions', position: 2, enabled: true },
                { id: 'activity', type: 'activity', position: 3, enabled: true },
                { id: 'stats', type: 'stats', position: 4, enabled: true },
                { id: 'knowledge', type: 'knowledge', position: 5, enabled: true }
            ]
        };
    }

    getWidgetTemplates() {
        return {
            'system-monitor': {
                name: 'System Monitor',
                icon: '💻',
                description: 'CPU, Memory, and Disk usage',
                category: 'system',
                render: (widget) => this.renderSystemMonitor(widget)
            },
            'quick-actions': {
                name: 'Quick Actions',
                icon: '⚡',
                description: 'Launch extensions quickly',
                category: 'navigation',
                render: (widget) => this.renderQuickActions(widget)
            },
            'extensions': {
                name: 'Extensions',
                icon: '📦',
                description: 'Active extension status',
                category: 'system',
                render: (widget) => this.renderExtensions(widget)
            },
            'activity': {
                name: 'Recent Activity',
                icon: '📜',
                description: 'Recent commands and changes',
                category: 'info',
                render: (widget) => this.renderActivity(widget)
            },
            'stats': {
                name: 'Progress Stats',
                icon: '📊',
                description: 'Development progress',
                category: 'info',
                render: (widget) => this.renderStats(widget)
            },
            'knowledge': {
                name: 'Knowledge Library',
                icon: '📚',
                description: 'Knowledge base access',
                category: 'navigation',
                render: (widget) => this.renderKnowledge(widget)
            },
            'clock': {
                name: 'Digital Clock',
                icon: '🕐',
                description: 'Current time display',
                category: 'info',
                render: (widget) => this.renderClock(widget)
            },
            'weather': {
                name: 'Weather',
                icon: '🌤️',
                description: 'Weather information',
                category: 'info',
                render: (widget) => this.renderWeather(widget)
            },
            'tasks': {
                name: 'Task List',
                icon: '✓',
                description: 'Todo list and tasks',
                category: 'productivity',
                render: (widget) => this.renderTasks(widget)
            },
            'notes': {
                name: 'Quick Notes',
                icon: '📝',
                description: 'Quick note taking',
                category: 'productivity',
                render: (widget) => this.renderNotes(widget)
            },
            'terminal': {
                name: 'Mini Terminal',
                icon: '💻',
                description: 'Embedded terminal',
                category: 'tools',
                render: (widget) => this.renderMiniTerminal(widget)
            },
            'music': {
                name: 'Music Player',
                icon: '🎵',
                description: 'Chiptune player',
                category: 'entertainment',
                render: (widget) => this.renderMusicPlayer(widget)
            }
        };
    }

    getThemes() {
        return {
            'synthwave': {
                name: 'Synthwave DOS',
                primary: '#00ffff',
                secondary: '#ff00ff',
                background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
            },
            'classic': {
                name: 'Classic NES',
                primary: '#fc0d1b',
                secondary: '#f8b800',
                background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 100%)'
            },
            'gameboy': {
                name: 'Game Boy',
                primary: '#0f380f',
                secondary: '#306230',
                background: 'linear-gradient(135deg, #9bbc0f 0%, #8bac0f 100%)'
            },
            'retro': {
                name: 'Retro',
                primary: '#7869c4',
                secondary: '#5c4ca8',
                background: 'linear-gradient(135deg, #3e31a2 0%, #2e2192 100%)'
            }
        };
    }

    renderDashboard() {
        const main = document.querySelector('.dashboard-main');
        if (!main) return;

        main.innerHTML = '';
        main.style.gridTemplateColumns = `repeat(${this.layout.columns}, 1fr)`;

        const enabledWidgets = this.layout.widgets
            .filter(w => w.enabled)
            .sort((a, b) => a.position - b.position);

        enabledWidgets.forEach(widgetConfig => {
            const template = this.widgetTemplates[widgetConfig.type];
            if (template) {
                const widgetEl = template.render(widgetConfig);
                main.appendChild(widgetEl);
                this.widgets.set(widgetConfig.id, widgetEl);
            }
        });

        if (this.editMode) {
            this.enableEditMode();
        }
    }

    createWidget(config, template) {
        const widget = document.createElement('div');
        widget.className = 'widget nes-container is-dark';
        widget.dataset.widgetId = config.id;
        widget.dataset.widgetType = config.type;

        const header = document.createElement('div');
        header.className = 'widget-header';
        header.innerHTML = `
            <h2 class="widget-title">${template.icon} ${template.name}</h2>
            ${this.editMode ? `
                <div class="widget-controls">
                    <button class="nes-btn is-small" onclick="dashboardBuilder.moveWidget('${config.id}', 'up')">↑</button>
                    <button class="nes-btn is-small" onclick="dashboardBuilder.moveWidget('${config.id}', 'down')">↓</button>
                    <button class="nes-btn is-error is-small" onclick="dashboardBuilder.removeWidget('${config.id}')">✕</button>
                </div>
            ` : ''}
        `;

        const body = document.createElement('div');
        body.className = 'widget-body';

        widget.appendChild(header);
        widget.appendChild(body);

        return { widget, body };
    }

    // Widget Renderers
    renderSystemMonitor(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="progress-container">
                <div class="progress-label">
                    <span>CPU Usage</span>
                    <span id="cpu-value" class="stat-value">0%</span>
                </div>
                <progress class="nes-progress is-primary" id="cpu-bar" value="0" max="100"></progress>
            </div>

            <div class="progress-container">
                <div class="progress-label">
                    <span>Memory</span>
                    <span id="memory-value" class="stat-value">0 GB</span>
                </div>
                <progress class="nes-progress is-success" id="memory-bar" value="0" max="100"></progress>
            </div>

            <div class="progress-container">
                <div class="progress-label">
                    <span>Disk Space</span>
                    <span id="disk-value" class="stat-value">0 GB</span>
                </div>
                <progress class="nes-progress is-warning" id="disk-bar" value="0" max="100"></progress>
            </div>

            <div class="stat-row">
                <span class="stat-label">Uptime</span>
                <span class="stat-value" id="uptime">--</span>
            </div>
        `;

        return widget;
    }

    renderQuickActions(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        const actions = [
            { name: 'Terminal', icon: '💻', action: 'terminal' },
            { name: 'Knowledge', icon: '📖', action: 'markdown' },
            { name: 'Files', icon: '📁', action: 'files' },
            { name: 'Teletext', icon: '📺', action: 'teletext' },
            { name: 'Editor', icon: '✏️', action: 'character' },
            { name: 'Settings', icon: '⚙️', action: 'settings' }
        ];

        body.innerHTML = `
            <div class="actions-grid">
                ${actions.map(action => `
                    <button class="nes-btn action-btn" onclick="dashboardBuilder.openExtension('${action.action}')">
                        <span class="action-icon">${action.icon}</span>
                        <span class="action-text">${action.name}</span>
                    </button>
                `).join('')}
            </div>
        `;

        return widget;
    }

    renderExtensions(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        const extensions = [
            { name: 'Character Editor', icon: '🎨', active: true },
            { name: 'Markdown Viewer', icon: '📖', active: true },
            { name: 'Teletext', icon: '📺', active: true },
            { name: 'Retro Terminal', icon: '💻', active: true },
            { name: 'System Desktop', icon: '🖥️', active: false }
        ];

        body.innerHTML = extensions.map(ext => `
            <div class="extension-item">
                <span class="extension-name">${ext.icon} ${ext.name}</span>
                <span class="nes-badge ${ext.active ? 'is-success' : 'is-error'}">
                    ${ext.active ? 'ACTIVE' : 'INACTIVE'}
                </span>
            </div>
        `).join('');

        return widget;
    }

    renderActivity(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        const activities = [
            { time: '2 min ago', text: '✅ Phase 5.1 committed: Markdown typography', type: 'success' },
            { time: '15 min ago', text: '📝 Updated CREDITS.md documentation', type: 'info' },
            { time: '32 min ago', text: '🎨 Phase 5 complete: Markdown Viewer v1.0.24', type: 'success' },
            { time: '1 hour ago', text: '⚡ Created uCODE processor', type: 'primary' },
            { time: '2 hours ago', text: '📦 Created PANEL processor', type: 'primary' }
        ];

        body.innerHTML = `
            <div class="activity-list">
                ${activities.map(activity => `
                    <div class="activity-item nes-container is-dark">
                        <div class="activity-time">${activity.time}</div>
                        <div class="activity-text">${activity.text}</div>
                    </div>
                `).join('')}
            </div>
        `;

        return widget;
    }

    renderStats(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="pixel-hearts">
                ${[1,2,3,4].map(() => '<i class="nes-icon is-small heart"></i>').join('')}
                <i class="nes-icon is-small is-transparent heart"></i>
            </div>

            <div class="stat-row">
                <span class="stat-label">Level</span>
                <span class="stat-value">24</span>
            </div>

            <div class="stat-row">
                <span class="stat-label">XP</span>
                <span class="stat-value">15,847 / 20,000</span>
            </div>

            <div class="progress-container">
                <div class="progress-label">
                    <span>Next Level</span>
                    <span class="stat-value">79%</span>
                </div>
                <progress class="nes-progress is-primary" value="79" max="100"></progress>
            </div>

            <div class="stat-row">
                <span class="stat-label">Commits</span>
                <span class="stat-value">9 / 11 phases</span>
            </div>
        `;

        return widget;
    }

    renderKnowledge(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="stat-row">
                <span class="stat-label">Categories</span>
                <span class="stat-value">8</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Documents</span>
                <span class="stat-value">127</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Recently Viewed</span>
                <span class="stat-value">water-purification.md</span>
            </div>
            <button class="nes-btn is-primary" style="width: 100%; margin-top: 15px;" onclick="dashboardBuilder.openExtension('markdown')">
                📖 Open Knowledge Base
            </button>
        `;

        return widget;
    }

    renderClock(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="digital-clock">
                <div class="clock-time" id="clock-time">--:--:--</div>
                <div class="clock-date" id="clock-date">--- -- ----</div>
            </div>
        `;

        return widget;
    }

    renderWeather(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="weather-widget">
                <div class="weather-icon">🌤️</div>
                <div class="weather-temp">72°F</div>
                <div class="weather-desc">Partly Cloudy</div>
                <div class="weather-location">Melbourne, AU</div>
            </div>
        `;

        return widget;
    }

    renderTasks(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="tasks-list">
                <label class="nes-checkbox">
                    <input type="checkbox" checked />
                    <span>Complete dashboard builder</span>
                </label>
                <label class="nes-checkbox">
                    <input type="checkbox" />
                    <span>Add widget templates</span>
                </label>
                <label class="nes-checkbox">
                    <input type="checkbox" />
                    <span>Test on mobile devices</span>
                </label>
            </div>
            <button class="nes-btn is-success" style="width: 100%; margin-top: 10px;">+ Add Task</button>
        `;

        return widget;
    }

    renderNotes(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="nes-field">
                <textarea class="nes-textarea" rows="6" placeholder="Quick notes..."></textarea>
            </div>
            <button class="nes-btn is-primary" style="width: 100%; margin-top: 10px;">Save Note</button>
        `;

        return widget;
    }

    renderMiniTerminal(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="mini-terminal">
                <div class="terminal-output" id="terminal-output">
                    <div>$ uDOS v1.0.24 ready</div>
                    <div>Type 'help' for commands</div>
                </div>
                <div class="terminal-input">
                    <span>$</span>
                    <input type="text" class="nes-input" placeholder="command..." />
                </div>
            </div>
        `;

        return widget;
    }

    renderMusicPlayer(config) {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="music-player">
                <div class="now-playing">🎵 Chiptune Mix 01</div>
                <progress class="nes-progress is-primary" value="45" max="100"></progress>
                <div class="player-controls">
                    <button class="nes-btn is-small">⏮</button>
                    <button class="nes-btn is-primary">▶</button>
                    <button class="nes-btn is-small">⏭</button>
                </div>
            </div>
        `;

        return widget;
    }

    // Builder Controls
    toggleEditMode() {
        this.editMode = !this.editMode;
        const btn = document.getElementById('edit-mode-btn');
        if (btn) {
            btn.textContent = this.editMode ? '💾 Save Layout' : '⚙️ Edit Layout';
            btn.className = this.editMode ? 'nes-btn is-success' : 'nes-btn is-warning';
        }

        if (!this.editMode) {
            this.saveLayout();
        }

        this.renderDashboard();
    }

    enableEditMode() {
        document.querySelectorAll('.widget').forEach(widget => {
            widget.classList.add('editable');
            widget.style.cursor = 'move';
        });
    }

    openWidgetPicker() {
        const modal = document.getElementById('widget-picker-modal');
        const list = document.getElementById('widget-picker-list');

        list.innerHTML = Object.entries(this.widgetTemplates).map(([type, template]) => `
            <div class="widget-picker-item nes-container is-dark" onclick="dashboardBuilder.addWidget('${type}')">
                <span class="widget-icon">${template.icon}</span>
                <div class="widget-info">
                    <div class="widget-name">${template.name}</div>
                    <div class="widget-desc">${template.description}</div>
                    <span class="nes-badge is-primary">${template.category}</span>
                </div>
            </div>
        `).join('');

        modal.style.display = 'flex';
    }

    closeWidgetPicker() {
        document.getElementById('widget-picker-modal').style.display = 'none';
    }

    addWidget(type) {
        const newWidget = {
            id: `${type}-${Date.now()}`,
            type: type,
            position: this.layout.widgets.length,
            enabled: true
        };

        this.layout.widgets.push(newWidget);
        this.closeWidgetPicker();
        this.renderDashboard();
        this.saveLayout();
    }

    removeWidget(id) {
        this.layout.widgets = this.layout.widgets.filter(w => w.id !== id);
        this.renderDashboard();
        this.saveLayout();
    }

    moveWidget(id, direction) {
        const index = this.layout.widgets.findIndex(w => w.id === id);
        if (index === -1) return;

        const newIndex = direction === 'up' ? index - 1 : index + 1;
        if (newIndex < 0 || newIndex >= this.layout.widgets.length) return;

        [this.layout.widgets[index], this.layout.widgets[newIndex]] =
        [this.layout.widgets[newIndex], this.layout.widgets[index]];

        this.layout.widgets.forEach((w, i) => w.position = i);
        this.renderDashboard();
        this.saveLayout();
    }

    changeColumns(cols) {
        this.layout.columns = parseInt(cols);
        this.renderDashboard();
        this.saveLayout();
    }

    applyTheme(themeName) {
        const theme = this.themes[themeName];
        if (!theme) return;

        const root = document.documentElement;
        root.style.setProperty('--theme-primary', theme.primary);
        root.style.setProperty('--theme-secondary', theme.secondary);
        document.body.style.background = theme.background;

        this.currentTheme = themeName;
        localStorage.setItem('dashboard-theme', themeName);
    }

    openSettings() {
        document.getElementById('settings-modal').style.display = 'flex';
    }

    closeSettings() {
        document.getElementById('settings-modal').style.display = 'none';
    }

    // Extension Launcher
    openExtension(name) {
        const ports = {
            'terminal': 8889,
            'markdown': 9000,
            'files': 8000,
            'teletext': 9002,
            'character': 8891,
            'settings': 8888
        };

        const port = ports[name] || 8888;
        window.open(`http://localhost:${port}`, '_blank');
    }

    // Auto Updates
    startAutoUpdates() {
        setInterval(() => this.updateSystemMetrics(), 3000);
        setInterval(() => this.updateClock(), 1000);
        this.updateClock();
    }

    updateSystemMetrics() {
        const cpu = 30 + Math.random() * 40;
        const cpuBar = document.getElementById('cpu-bar');
        const cpuValue = document.getElementById('cpu-value');
        if (cpuBar) cpuBar.value = cpu;
        if (cpuValue) cpuValue.textContent = cpu.toFixed(1) + '%';

        const memory = 30 + Math.random() * 30;
        const memBar = document.getElementById('memory-bar');
        const memValue = document.getElementById('memory-value');
        if (memBar) memBar.value = memory;
        if (memValue) memValue.textContent = `${(memory * 16 / 100).toFixed(1)} / 16 GB`;

        const disk = 20 + Math.random() * 10;
        const diskBar = document.getElementById('disk-bar');
        const diskValue = document.getElementById('disk-value');
        if (diskBar) diskBar.value = disk;
        if (diskValue) diskValue.textContent = `${(disk * 500 / 100).toFixed(0)} / 500 GB`;
    }

    updateClock() {
        const now = new Date();
        const timeEl = document.getElementById('clock-time');
        const dateEl = document.getElementById('clock-date');
        const footerTime = document.getElementById('current-time');

        if (timeEl) {
            timeEl.textContent = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        }

        if (footerTime) {
            footerTime.textContent = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    // Storage
    saveLayout() {
        localStorage.setItem('dashboard-layout', JSON.stringify(this.layout));
        console.log('💾 Layout saved');
    }

    loadLayout() {
        const saved = localStorage.getItem('dashboard-layout');
        return saved ? JSON.parse(saved) : null;
    }

    resetLayout() {
        if (confirm('Reset dashboard to default layout?')) {
            localStorage.removeItem('dashboard-layout');
            this.layout = this.getDefaultLayout();
            this.renderDashboard();
            this.closeSettings();
        }
    }

    exportLayout() {
        const dataStr = JSON.stringify(this.layout, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'udos-dashboard-layout.json';
        link.click();
        URL.revokeObjectURL(url);
    }

    importLayout() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    this.layout = JSON.parse(event.target.result);
                    this.saveLayout();
                    this.renderDashboard();
                    alert('Layout imported successfully!');
                } catch (err) {
                    alert('Error importing layout: ' + err.message);
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    attachEventListeners() {
        // Close modals on outside click
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }
}

// Initialize on load
let dashboardBuilder;
document.addEventListener('DOMContentLoaded', () => {
    dashboardBuilder = new DashboardBuilder();
});
