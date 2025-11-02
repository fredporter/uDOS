/**
 * uDOS Advanced Dashboard API
 * Combines C64 CSS3, Teletext, and modern web technologies
 * Version 1.0.10
 */

class DashboardAPI {
    constructor() {
        this.modules = new Map();
        this.themes = ['retro', 'c64', 'teletext', 'system7', 'modern'];
        this.currentTheme = 'retro';
        this.wsConnection = null;
        this.dataStreams = new Map();
        this.isInitialized = false;
    }

    /**
     * Initialize the dashboard system
     */
    async init() {
        if (this.isInitialized) return;

        console.log('🚀 Initializing uDOS Advanced Dashboard...');

        // Initialize core systems
        await this.initializeWebSocket();
        await this.loadModules();
        this.setupEventListeners();
        this.startDataStreams();

        this.isInitialized = true;
        console.log('✅ Dashboard initialization complete');
    }

    /**
     * WebSocket connection for real-time data
     */
    async initializeWebSocket() {
        try {
            // In a real implementation, this would connect to uDOS backend
            console.log('🔌 Attempting WebSocket connection...');

            // Mock WebSocket for demonstration
            this.wsConnection = {
                send: (data) => console.log('📤 Sending:', data),
                close: () => console.log('🔌 Connection closed'),
                readyState: 1 // OPEN
            };

            console.log('✅ WebSocket connection established');
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            // Fallback to polling mode
            this.setupPolling();
        }
    }

    /**
     * Load available dashboard modules
     */
    async loadModules() {
        const coreModules = [
            'system-monitor',
            'process-manager',
            'network-analyzer',
            'file-browser',
            'terminal-emulator',
            'c64-simulator',
            'teletext-decoder',
            'system7-interface',
            'performance-tracker'
        ];

        for (const moduleName of coreModules) {
            try {
                const module = await this.loadModule(moduleName);
                this.modules.set(moduleName, module);
                console.log(`📦 Loaded module: ${moduleName}`);
            } catch (error) {
                console.warn(`⚠️ Failed to load module ${moduleName}:`, error);
            }
        }
    }

    /**
     * Load a specific module
     */
    async loadModule(moduleName) {
        // Mock module loading - in real implementation would fetch from server
        return {
            name: moduleName,
            version: '1.0.0',
            status: 'loaded',
            api: this.createModuleAPI(moduleName)
        };
    }

    /**
     * Create module-specific API
     */
    createModuleAPI(moduleName) {
        const apis = {
            'system-monitor': {
                getCPUUsage: () => Math.floor(Math.random() * 100),
                getMemoryUsage: () => Math.floor(Math.random() * 100),
                getDiskUsage: () => Math.floor(Math.random() * 100),
                getProcessCount: () => Math.floor(Math.random() * 50) + 20
            },
            'network-analyzer': {
                getUploadSpeed: () => (Math.random() * 10).toFixed(2),
                getDownloadSpeed: () => (Math.random() * 50).toFixed(2),
                getConnectionCount: () => Math.floor(Math.random() * 100),
                getPacketCount: () => Math.floor(Math.random() * 10000)
            },
            'c64-simulator': {
                executeCommand: (cmd) => this.processC64Command(cmd),
                getMemoryMap: () => this.generateC64MemoryMap(),
                loadProgram: (program) => `LOADING "${program}"...`
            },
            'teletext-decoder': {
                decodePage: (pageNum) => this.generateTeletextPage(pageNum),
                getCurrentPage: () => '100',
                getPageList: () => ['100', '101', '102', '200', '300']
            },
            'system7-interface': {
                createWindow: (options) => {
                    if (typeof window.system7 !== 'undefined') {
                        return window.system7.createWindow(options);
                    }
                    return null;
                },
                showDialog: (options) => {
                    if (typeof window.system7 !== 'undefined') {
                        return window.system7.showDialog(options);
                    }
                },
                getSystemInfo: () => ({
                    version: 'System 7.1',
                    memory: '8 MB',
                    finder: 'Finder 7.1.5'
                })
            }
        };

        return apis[moduleName] || {};
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Theme switching
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.cycleTheme();
            }
        });

        // Module hotkeys
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                const moduleKeys = {
                    '1': 'system-monitor',
                    '2': 'process-manager',
                    '3': 'network-analyzer',
                    '4': 'terminal-emulator',
                    '5': 'c64-simulator',
                    '6': 'teletext-decoder',
                    '7': 'system7-interface',
                    '8': 'file-browser',
                    '9': 'performance-tracker'
                };

                if (moduleKeys[e.key]) {
                    e.preventDefault();
                    this.activateModule(moduleKeys[e.key]);
                }
            }
        });

        // Window resize handling
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * Start real-time data streams
     */
    startDataStreams() {
        // System metrics stream
        this.dataStreams.set('system-metrics', setInterval(() => {
            this.updateSystemMetrics();
        }, 1000));

        // Network activity stream
        this.dataStreams.set('network-activity', setInterval(() => {
            this.updateNetworkActivity();
        }, 2000));

        // Teletext data stream
        this.dataStreams.set('teletext-stream', setInterval(() => {
            this.updateTeletextStream();
        }, 5000));
    }

    /**
     * Update system metrics in real-time
     */
    updateSystemMetrics() {
        if (!this.modules.has('system-monitor')) return;

        const systemAPI = this.modules.get('system-monitor').api;
        const metrics = {
            cpu: systemAPI.getCPUUsage(),
            memory: systemAPI.getMemoryUsage(),
            disk: systemAPI.getDiskUsage(),
            processes: systemAPI.getProcessCount()
        };

        this.broadcastUpdate('system-metrics', metrics);
    }

    /**
     * Update network activity
     */
    updateNetworkActivity() {
        if (!this.modules.has('network-analyzer')) return;

        const networkAPI = this.modules.get('network-analyzer').api;
        const activity = {
            upload: networkAPI.getUploadSpeed(),
            download: networkAPI.getDownloadSpeed(),
            connections: networkAPI.getConnectionCount(),
            packets: networkAPI.getPacketCount()
        };

        this.broadcastUpdate('network-activity', activity);
    }

    /**
     * Update teletext data stream
     */
    updateTeletextStream() {
        if (!this.modules.has('teletext-decoder')) return;

        const teletextAPI = this.modules.get('teletext-decoder').api;
        const currentPage = teletextAPI.getCurrentPage();
        const pageData = teletextAPI.decodePage(currentPage);

        this.broadcastUpdate('teletext-stream', { page: currentPage, data: pageData });
    }

    /**
     * Broadcast updates to UI components
     */
    broadcastUpdate(streamName, data) {
        const event = new CustomEvent('dashboard-update', {
            detail: { stream: streamName, data: data }
        });
        document.dispatchEvent(event);
    }

    /**
     * Cycle through available themes
     */
    cycleTheme() {
        const currentIndex = this.themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % this.themes.length;
        this.currentTheme = this.themes[nextIndex];

        this.applyTheme(this.currentTheme);
        console.log(`🎨 Theme changed to: ${this.currentTheme}`);
    }

    /**
     * Apply a specific theme
     */
    applyTheme(themeName) {
        document.body.className = `theme-${themeName}`;

        // Theme-specific styling
        const root = document.documentElement;

        switch(themeName) {
            case 'c64':
                root.style.setProperty('--primary-color', '#6076c5');
                root.style.setProperty('--secondary-color', '#20398d');
                root.style.setProperty('--accent-color', '#00ff41');
                break;
            case 'teletext':
                root.style.setProperty('--primary-color', '#00ff41');
                root.style.setProperty('--secondary-color', '#000000');
                root.style.setProperty('--accent-color', '#ffff00');
                break;
            case 'system7':
                root.style.setProperty('--primary-color', '#DDDDDD');
                root.style.setProperty('--secondary-color', '#AAAAAA');
                root.style.setProperty('--accent-color', '#316AC5');
                root.style.setProperty('--bg-color', '#C6C6C6');
                root.style.setProperty('--text-color', '#000000');
                // Apply System 7 font
                document.body.style.fontFamily = 'Chicago, Geneva, monospace';
                break;
            case 'modern':
                root.style.setProperty('--primary-color', '#2196f3');
                root.style.setProperty('--secondary-color', '#1976d2');
                root.style.setProperty('--accent-color', '#4caf50');
                break;
            default: // retro
                root.style.setProperty('--primary-color', '#6076c5');
                root.style.setProperty('--secondary-color', '#20398d');
                root.style.setProperty('--accent-color', '#00ff41');
        }
    }

    /**
     * Activate a specific module
     */
    activateModule(moduleName) {
        if (!this.modules.has(moduleName)) {
            console.warn(`⚠️ Module not found: ${moduleName}`);
            return;
        }

        console.log(`🔧 Activating module: ${moduleName}`);

        // Hide all module panels
        document.querySelectorAll('.module-panel').forEach(panel => {
            panel.style.display = 'none';
        });

        // Show the requested module panel
        const modulePanel = document.getElementById(`${moduleName}-panel`);
        if (modulePanel) {
            modulePanel.style.display = 'block';
        }

        // Update navigation
        document.querySelectorAll('.sidebar-item').forEach(item => {
            item.classList.remove('active');
        });

        const navItem = document.querySelector(`[onclick="loadModule('${moduleName}')"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
    }

    /**
     * Process C64-style commands
     */
    processC64Command(command) {
        const cmd = command.toUpperCase().trim();

        const commands = {
            'HELP': 'AVAILABLE COMMANDS:\nLIST, LOAD, RUN, NEW, SAVE, CATALOG, SYS',
            'LIST': 'PROGRAM LISTING:\n10 PRINT "HELLO UDOS"\n20 GOTO 10',
            'RUN': 'RUNNING PROGRAM...\nHELLO UDOS\nHELLO UDOS\nHELLO UDOS',
            'NEW': 'NEW PROGRAM READY',
            'CATALOG': 'DISK DIRECTORY:\nUDOS.PRG\nDASHBOARD.PRG\nTELETEXT.PRG',
            'SYS 64738': '*** COMMODORE 64 BASIC V2 ***\n64K RAM SYSTEM  38911 BASIC BYTES FREE',
            'LOAD"*",8,1': 'SEARCHING FOR *\nLOADING\nREADY.',
            'STATUS': 'SYSTEM STATUS: ALL SYSTEMS OPERATIONAL'
        };

        return commands[cmd] || `?SYNTAX ERROR: ${command}`;
    }

    /**
     * Generate C64 memory map
     */
    generateC64MemoryMap() {
        const map = [];
        for (let i = 0; i < 65536; i += 256) {
            const address = i.toString(16).toUpperCase().padStart(4, '0');
            const usage = i < 2048 ? 'RAM' : i < 40960 ? 'BASIC' : 'KERNAL';
            map.push({ address: `$${address}`, usage, size: 256 });
        }
        return map;
    }

    /**
     * Generate teletext page content
     */
    generateTeletextPage(pageNum) {
        const pages = {
            '100': [
                '█ uDOS TELETEXT SERVICE █',
                '■ Main Menu              ■',
                '  100 - Main Index       ',
                '  101 - System Status    ',
                '  102 - News & Updates   ',
                '  200 - Weather Data     ',
                '  300 - Sports Results   ',
                '█████████████████████████'
            ],
            '101': [
                '█ SYSTEM STATUS         █',
                '■ Server Health: ████████',
                '■ CPU Usage: 42% ████████',
                '■ Memory: 67% ███████████',
                '■ Disk Space: 23% ███████',
                '■ Network: ONLINE ███████',
                '■ Last Update: 12:34:56 █',
                '█████████████████████████'
            ],
            '102': [
                '█ NEWS & UPDATES        █',
                '■ uDOS v1.0.10 Released!',
                '■ New Dashboard Features',
                '■ C64 CSS3 Integration  ',
                '■ Teletext Web Framework',
                '■ Enhanced Typography   ',
                '■ Performance Improvements',
                '█████████████████████████'
            ]
        };

        return pages[pageNum] || ['█ PAGE NOT FOUND █'];
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Adjust layout for different screen sizes
        const width = window.innerWidth;
        const container = document.querySelector('.dashboard-container');

        if (width < 768) {
            container.style.gridTemplateColumns = '1fr';
            container.style.gridTemplateAreas = '"header" "main" "footer"';
        } else if (width < 1200) {
            container.style.gridTemplateColumns = '250px 1fr';
            container.style.gridTemplateAreas = '"header header" "sidebar main" "footer footer"';
        } else {
            container.style.gridTemplateColumns = '300px 1fr 250px';
            container.style.gridTemplateAreas = '"header header header" "sidebar main rightpanel" "footer footer footer"';
        }
    }

    /**
     * Setup polling mode (fallback for WebSocket)
     */
    setupPolling() {
        console.log('🔄 Setting up polling mode...');

        setInterval(() => {
            this.updateSystemMetrics();
            this.updateNetworkActivity();
        }, 5000);
    }

    /**
     * Cleanup and shutdown
     */
    shutdown() {
        console.log('🛑 Shutting down dashboard...');

        // Clear all data streams
        this.dataStreams.forEach((interval, name) => {
            clearInterval(interval);
            console.log(`🗑️ Cleared stream: ${name}`);
        });

        // Close WebSocket connection
        if (this.wsConnection && this.wsConnection.readyState === 1) {
            this.wsConnection.close();
        }

        // Clear modules
        this.modules.clear();

        this.isInitialized = false;
        console.log('✅ Dashboard shutdown complete');
    }
}

// Global dashboard instance
window.DashboardAPI = new DashboardAPI();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.DashboardAPI.init();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardAPI;
}
