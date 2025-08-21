// uDOS Professional Console - Integrated uCODE & Modular Commands System
// Enhanced command system with all uCODE modules and system integration

// Font Management System - Locked to Hybrid Mode
let currentFontMode = 'hybrid'; // Always hybrid mode
let currentFont = 'JetBrains Mono';
let currentDisplaySize = 'medium'; // Track current display size

// Enhanced font mode configuration with actual available fonts
const fontModes = {
    hybrid: {
        aspectRatio: 1.0,           
        blockRatio: 1.3,           
        defaultFont: 'JetBrains Mono',
        description: '📺⌨️ Hybrid Mode - 1:1 text + 1:1.3 blocks',
        fonts: [
            'JetBrains Mono',
            'MODE7GX0.TTF',
            'Pet Me 64',
            'Monaco',
            'Menlo',
            'Consolas',
            'SF Mono',
            'Courier New',
            'monospace'
        ]
    },
    monospace: {
        aspectRatio: 1.0,
        blockRatio: 1.0,
        defaultFont: 'topaz_a500.ttf',
        description: '⌨️ Pure Monospace - 1:1 uniform',
        fonts: [
            'topaz_a500.ttf',
            'topaz_a1200.ttf',
            'microknight.ttf',
            'Pet Me 64',
            'Pet Me 128',
            'SF Mono',
            'Monaco',
            'Menlo',
            'Consolas',
            'Courier New',
            'monospace'
        ]
    },
    retro: {
        aspectRatio: 1.0,
        blockRatio: 1.0,
        defaultFont: 'pot_noodle.ttf',
        description: '🎮 Retro Computing - Authentic classics',
        fonts: [
            'pot_noodle.ttf',
            'microknight.ttf',
            'topaz_a500.ttf',
            'topaz_a1200.ttf',
            'Pet Me 64',
            'Pet Me 128',
            'Mallard Neueue',
            'Mallard Blocky',
            'MODE7GX0.TTF',
            'Nova Mono',
            'Space Mono',
            'VT323',
            'Share Tech Mono'
        ]
    },
    system: {
        aspectRatio: 1.0,
        defaultFont: 'SF Pro Display',
        fonts: [
            'SF Pro Display',
            'SF Pro Text',
            'Helvetica Neue',
            'Helvetica',
            'Arial',
            'sans-serif'
        ]
    }
};

// Display size configurations
const displaySizes = {
    tiny: { size: '10px', lineHeight: 1.2, description: 'Tiny - Dense information' },
    small: { size: '12px', lineHeight: 1.3, description: 'Small - Compact display' },
    normal: { size: '14px', lineHeight: 1.4, description: 'Normal - Standard reading' },
    medium: { size: '16px', lineHeight: 1.4, description: 'Medium - Comfortable reading' },
    large: { size: '18px', lineHeight: 1.5, description: 'Large - Easy reading' },
    huge: { size: '20px', lineHeight: 1.5, description: 'Huge - Headers' },
    giant: { size: '24px', lineHeight: 1.6, description: 'Giant - Major headings' }
};

// Emoji support system
const emojiSystem = {
    whirl: '🌀',
    gear: '⚙️',
    lightning: '⚡',
    rocket: '🚀',
    arrows: {
        right: '▶',
        down: '▼', 
        up: '▲',
        left: '◀',
        double: '»',
        triple: '⟩'
    },
    status: {
        success: '✅',
        error: '❌', 
        warning: '⚠️',
        info: 'ℹ️',
        loading: '🔄'
    }
};

// Comprehensive uCODE Command System
class UDOSCommandSystem {
    constructor() {
        this.ucodeMode = false;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentMode = 'CONSOLE';
        this.socket = null;
        this.promptStyle = 'whirl'; // Default WHIRL emoji prompt
        this.fontSize = 'medium';
        this.bulletStyle = 'arrows'; // Use arrows for bullet points
        
        // Complete uCODE module definitions
        this.ucodeModules = {
            MEMORY: {
                description: 'Memory file management system',
                commands: {
                    list: 'List all memory files',
                    create: 'Create new memory file',
                    search: 'Search memory files',
                    delete: 'Delete memory file',
                    backup: 'Backup memory files',
                    restore: 'Restore from backup',
                    stats: 'Memory usage statistics',
                    optimize: 'Optimize memory storage'
                }
            },
            MISSION: {
                description: 'Task tracking and mission management',
                commands: {
                    list: 'List active missions',
                    create: 'Create new mission',
                    update: 'Update mission status',
                    complete: 'Mark mission complete',
                    delete: 'Delete mission',
                    track: 'Track mission progress',
                    priority: 'Set mission priority',
                    assign: 'Assign mission to user'
                }
            },
            PACKAGE: {
                description: 'Package management system',
                commands: {
                    install: 'Install package',
                    remove: 'Remove package',
                    list: 'List installed packages',
                    search: 'Search available packages',
                    update: 'Update packages',
                    info: 'Package information',
                    depends: 'Show dependencies',
                    clean: 'Clean package cache'
                }
            },
            LOG: {
                description: 'Advanced logging and analysis system',
                commands: {
                    report: 'Generate log report',
                    analyze: 'Analyze log patterns',
                    export: 'Export logs',
                    clean: 'Clean old logs',
                    filter: 'Filter log entries',
                    watch: 'Watch live logs',
                    archive: 'Archive old logs',
                    stats: 'Log statistics'
                }
            },
            DEV: {
                description: 'Development tools and utilities',
                commands: {
                    test: 'Run tests',
                    build: 'Build project',
                    deploy: 'Deploy application',
                    debug: 'Debug mode',
                    profile: 'Performance profiling',
                    lint: 'Code linting',
                    format: 'Code formatting',
                    docs: 'Generate documentation'
                }
            },
            RENDER: {
                description: 'Visual rendering and ASCII art system',
                commands: {
                    art: 'Generate ASCII art',
                    chart: 'Create charts',
                    ui: 'Render UI elements',
                    animation: 'Create animations',
                    gallery: 'Art gallery browser',
                    export: 'Export rendered content',
                    template: 'Use render templates',
                    preview: 'Preview render output'
                }
            },
            DASH: {
                description: 'Live dashboard and monitoring system',
                commands: {
                    live: 'Live dashboard view',
                    performance: 'Performance metrics',
                    system: 'System status',
                    network: 'Network monitoring',
                    processes: 'Process monitoring',
                    alerts: 'System alerts',
                    history: 'Historical data',
                    export: 'Export dashboard data'
                }
            },
            PANEL: {
                description: 'Interactive control panels',
                commands: {
                    system: 'System control panel',
                    user: 'User management panel',
                    network: 'Network control panel',
                    security: 'Security panel',
                    backup: 'Backup control panel',
                    monitor: 'Monitoring panel',
                    config: 'Configuration panel',
                    tools: 'System tools panel'
                }
            },
            TREE: {
                description: 'Structure visualization and analysis',
                commands: {
                    generate: 'Generate structure tree',
                    analyze: 'Analyze structure',
                    visualize: 'Visual tree representation',
                    export: 'Export tree structure',
                    compare: 'Compare structures',
                    search: 'Search in tree',
                    stats: 'Structure statistics',
                    optimize: 'Optimize structure'
                }
            }
        };
        
        // System modules (non-uCODE)
        this.systemModules = {
            uCORE: 'Core system management',
            uSCRIPT: 'Script automation system',
            uSERVER: 'Web services and APIs',
            uMEMORY: 'Memory and storage system',
            uKNOWLEDGE: 'Knowledge base system',
            WIZARD: 'Development wizard tools',
            SORCERER: 'Advanced system administration',
            IMP: 'Script execution engine',
            GHOST: 'Background services',
            DRONE: 'Automation tasks',
            TOMB: 'Archive and backup system'
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeSocket();
    }
    
    setupEventListeners() {
        // Command input handling
        const input = document.getElementById('command-input');
        if (input) {
            input.addEventListener('keydown', (e) => this.handleKeyDown(e));
            input.addEventListener('input', (e) => this.handleInput(e));
        }
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleGlobalShortcuts(e));
    }
    
    handleKeyDown(e) {
        const input = e.target;
        
        switch(e.key) {
            case 'Enter':
                this.executeCommand(input.value.trim());
                input.value = '';
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateHistory(-1, input);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.navigateHistory(1, input);
                break;
            case 'Tab':
                e.preventDefault();
                this.autoComplete(input);
                break;
            case 'Escape':
                input.value = '';
                this.hideSuggestions();
                break;
        }
    }
    
    handleInput(e) {
        this.showSuggestions(e.target.value);
        this.updateTypingIndicator();
    }
    
    navigateHistory(direction, input) {
        if (direction === -1 && this.historyIndex < this.commandHistory.length - 1) {
            this.historyIndex++;
            input.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
        } else if (direction === 1 && this.historyIndex > 0) {
            this.historyIndex--;
            input.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
        } else if (direction === 1 && this.historyIndex === 0) {
            this.historyIndex = -1;
            input.value = '';
        }
    }
    
    executeCommand(command) {
        if (!command) return;
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = -1;
        
        // Display command
        this.addToTerminal(`$ ${command}`, 'command');
        
        // Process command
        if (this.ucodeMode) {
            this.handleUCodeCommand(command);
        } else {
            this.handleSystemCommand(command);
        }
    }
    
    handleSystemCommand(command) {
        const cmd = command.toLowerCase().trim();
        const parts = command.trim().split(' ');
        const mainCmd = parts[0].toUpperCase();
        const action = parts[1] ? parts[1].toLowerCase() : '';
        const args = parts.slice(2);
        
        // System commands
        switch(cmd) {
            case 'help':
                this.showSystemHelp();
                break;
            case 'clear':
                this.clearTerminal();
                break;
            case 'history':
                this.showCommandHistory();
                break;
            case 'ucode':
                this.enterUCodeMode();
                break;
            case 'status':
                this.showSystemStatus();
                break;
            case 'modules':
                this.listModules();
                break;
            case 'blocks':
                this.showBlockGraphicsDemo();
                break;
            case 'font':
                this.handleFontCommand(parts.slice(1));
                break;
            case 'size':
                this.handleSizeCommand(parts.slice(1));
                break;
            default:
                // Check if it's a uCODE module command
                if (this.ucodeModules[mainCmd]) {
                    this.executeUCodeModule(mainCmd, action, args);
                } else if (this.systemModules[mainCmd]) {
                    this.executeSystemModule(mainCmd, action, args);
                } else {
                    // Try to send to server
                    this.sendToServer(command);
                }
        }
    }
    
    handleUCodeCommand(command) {
        const cmd = command.trim();
        const parts = cmd.split(' ');
        const module = parts[0].toUpperCase();
        const action = parts[1] ? parts[1].toLowerCase() : 'help';
        const args = parts.slice(2);
        
        // Special uCODE commands
        if (cmd.toLowerCase() === 'exit' || cmd.toLowerCase() === 'quit') {
            this.exitUCodeMode();
            return;
        }
        
        if (cmd.toLowerCase() === 'help') {
            this.showUCodeHelp();
            return;
        }
        
        if (cmd.toLowerCase() === 'status') {
            this.showUCodeStatus();
            return;
        }
        
        if (cmd.toLowerCase() === 'list') {
            this.listUCodeModules();
            return;
        }
        
        // Module commands
        if (this.ucodeModules[module]) {
            this.executeUCodeModule(module, action, args);
        } else {
            this.addToTerminal(`❌ Unknown uCODE module: ${module}`, 'error');
            this.addToTerminal('💡 Type "help" for available commands', 'info');
        }
    }
    
    executeUCodeModule(module, action, args) {
        const moduleInfo = this.ucodeModules[module];
        if (!moduleInfo) {
            this.addToTerminal(`❌ Module ${module} not found`, 'error');
            return;
        }
        
        this.addToTerminal(`🔄 Executing ${module}.${action}...`, 'info');
        
        if (!action || action === 'help') {
            this.showModuleHelp(module);
            return;
        }
        
        // Module-specific command handling
        switch(module) {
            case 'MEMORY':
                this.handleMemoryCommand(action, args);
                break;
            case 'MISSION':
                this.handleMissionCommand(action, args);
                break;
            case 'PACKAGE':
                this.handlePackageCommand(action, args);
                break;
            case 'LOG':
                this.handleLogCommand(action, args);
                break;
            case 'DEV':
                this.handleDevCommand(action, args);
                break;
            case 'RENDER':
                this.handleRenderCommand(action, args);
                break;
            case 'DASH':
                this.handleDashCommand(action, args);
                break;
            case 'PANEL':
                this.handlePanelCommand(action, args);
                break;
            case 'TREE':
                this.handleTreeCommand(action, args);
                break;
            default:
                this.addToTerminal(`❌ Module ${module} handler not implemented`, 'error');
        }
    }
    
    executeSystemModule(module, action, args) {
        this.addToTerminal(`🔧 Loading ${module} module...`, 'info');
        
        switch(module) {
            case 'uCORE':
                this.handleUCoreModule(action, args);
                break;
            case 'uSCRIPT':
                this.handleUScriptModule(action, args);
                break;
            case 'uSERVER':
                this.handleUServerModule(action, args);
                break;
            case 'uMEMORY':
                this.handleUMemoryModule(action, args);
                break;
            case 'WIZARD':
                this.handleWizardModule(action, args);
                break;
            case 'SORCERER':
                this.handleSorcererModule(action, args);
                break;
            case 'IMP':
                this.handleImpModule(action, args);
                break;
            default:
                this.addToTerminal(`📦 ${module}: ${this.systemModules[module]}`, 'info');
                this.addToTerminal('Module loading...', 'output');
        }
    }

    
    // Memory module command handler
    handleMemoryCommand(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('📁 Memory Files:', 'info');
                this.addToTerminal('▶ system.mem - Core system memory', 'output');
                this.addToTerminal('▶ user.mem - User session data', 'output');
                this.addToTerminal('▶ cache.mem - Temporary cache', 'output');
                break;
            case 'create':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: MEMORY create [filename]', 'error');
                } else {
                    this.addToTerminal(`✅ Created memory file: ${args[0]}.mem`, 'success');
                }
                break;
            case 'search':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: MEMORY search [term]', 'error');
                } else {
                    this.addToTerminal(`🔍 Searching for: ${args.join(' ')}`, 'info');
                    this.addToTerminal('▶ Found 3 matches in system.mem', 'output');
                }
                break;
            case 'stats':
                this.addToTerminal('📊 Memory Statistics:', 'info');
                this.addToTerminal('▶ Total files: 127', 'output');
                this.addToTerminal('▶ Storage used: 45.2 MB', 'output');
                this.addToTerminal('▶ Available: 154.8 MB', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown MEMORY command: ${action}`, 'error');
                this.showModuleHelp('MEMORY');
        }
    }
    
    // Mission module command handler
    handleMissionCommand(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('🎯 Active Missions:', 'info');
                this.addToTerminal('▶ [001] uCODE Integration - In Progress', 'output');
                this.addToTerminal('▶ [002] Console UI Redesign - Complete', 'output');
                this.addToTerminal('▶ [003] Font System Enhancement - Complete', 'output');
                break;
            case 'create':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: MISSION create [name]', 'error');
                } else {
                    const missionId = String(Math.floor(Math.random() * 1000)).padStart(3, '0');
                    this.addToTerminal(`✅ Created mission [${missionId}]: ${args.join(' ')}`, 'success');
                }
                break;
            case 'track':
                this.addToTerminal('📈 Mission Progress Tracking:', 'info');
                this.addToTerminal('▶ UI Components: 100% ████████████', 'output');
                this.addToTerminal('▶ Command System: 75% █████████░░░', 'output');
                this.addToTerminal('▶ Integration: 50% ██████░░░░░░', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown MISSION command: ${action}`, 'error');
                this.showModuleHelp('MISSION');
        }
    }
    
    // Package module command handler
    handlePackageCommand(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('📦 Installed Packages:', 'info');
                this.addToTerminal('▶ ucore-engine v2.1.3', 'output');
                this.addToTerminal('▶ font-manager v1.0.2', 'output');
                this.addToTerminal('▶ command-parser v3.0.1', 'output');
                break;
            case 'install':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: PACKAGE install [name]', 'error');
                } else {
                    this.addToTerminal(`📥 Installing package: ${args[0]}`, 'info');
                    this.addToTerminal('✅ Installation complete', 'success');
                }
                break;
            case 'search':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: PACKAGE search [term]', 'error');
                } else {
                    this.addToTerminal(`🔍 Searching packages for: ${args.join(' ')}`, 'info');
                    this.addToTerminal('▶ ucode-extensions - Advanced uCODE modules', 'output');
                    this.addToTerminal('▶ render-toolkit - Enhanced rendering tools', 'output');
                }
                break;
            default:
                this.addToTerminal(`❌ Unknown PACKAGE command: ${action}`, 'error');
                this.showModuleHelp('PACKAGE');
        }
    }
    
    // Log module command handler
    handleLogCommand(action, args) {
        switch(action) {
            case 'report':
                this.addToTerminal('📋 Generating log report...', 'info');
                this.addToTerminal('▶ Total entries: 2,847', 'output');
                this.addToTerminal('▶ Errors: 12', 'output');
                this.addToTerminal('▶ Warnings: 45', 'output');
                this.addToTerminal('▶ Info: 2,790', 'output');
                break;
            case 'analyze':
                this.addToTerminal('🔬 Analyzing log patterns...', 'info');
                this.addToTerminal('▶ Most active time: 14:30-16:00', 'output');
                this.addToTerminal('▶ Common errors: Authentication (8), Network (4)', 'output');
                this.addToTerminal('▶ Performance: Average response 120ms', 'output');
                break;
            case 'watch':
                this.addToTerminal('👁️ Starting live log watch...', 'info');
                this.addToTerminal('[2024-01-15 14:30:12] INFO: Command executed successfully', 'output');
                this.addToTerminal('[2024-01-15 14:30:15] INFO: Font mode changed to teletext', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown LOG command: ${action}`, 'error');
                this.showModuleHelp('LOG');
        }
    }
    
    // Dev module command handler
    handleDevCommand(action, args) {
        switch(action) {
            case 'test':
                this.addToTerminal('🧪 Running test suite...', 'info');
                this.addToTerminal('▶ Font system tests: ✅ PASSED', 'output');
                this.addToTerminal('▶ Command parser tests: ✅ PASSED', 'output');
                this.addToTerminal('▶ UI component tests: ✅ PASSED', 'output');
                this.addToTerminal('All tests completed successfully!', 'success');
                break;
            case 'build':
                this.addToTerminal('🔨 Building project...', 'info');
                this.addToTerminal('▶ Compiling assets... ✅', 'output');
                this.addToTerminal('▶ Optimizing CSS... ✅', 'output');
                this.addToTerminal('▶ Bundling JavaScript... ✅', 'output');
                this.addToTerminal('Build completed successfully!', 'success');
                break;
            case 'debug':
                this.addToTerminal('🐛 Entering debug mode...', 'info');
                this.addToTerminal('Debug console enabled', 'output');
                this.addToTerminal('Type "debug help" for debug commands', 'info');
                break;
            default:
                this.addToTerminal(`❌ Unknown DEV command: ${action}`, 'error');
                this.showModuleHelp('DEV');
        }
    }
    
    // Render module command handler
    handleRenderCommand(action, args) {
        switch(action) {
            case 'art':
                this.addToTerminal('🎨 ASCII Art Generator:', 'info');
                this.addToTerminal('', 'output');
                this.addToTerminal('  ██╗   ██╗██████╗  ██████╗ ███████╗', 'output');
                this.addToTerminal('  ██║   ██║██╔══██╗██╔═══██╗██╔════╝', 'output');
                this.addToTerminal('  ██║   ██║██║  ██║██║   ██║███████╗', 'output');
                this.addToTerminal('  ██║   ██║██║  ██║██║   ██║╚════██║', 'output');
                this.addToTerminal('  ╚██████╔╝██████╔╝╚██████╔╝███████║', 'output');
                this.addToTerminal('   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝', 'output');
                this.addToTerminal('', 'output');
                break;
            case 'chart':
                this.addToTerminal('📊 System Performance Chart:', 'info');
                this.addToTerminal('CPU Usage: ████████░░ 80%', 'output');
                this.addToTerminal('Memory:    ██████░░░░ 60%', 'output');
                this.addToTerminal('Disk:      ███░░░░░░░ 30%', 'output');
                this.addToTerminal('Network:   █████████░ 90%', 'output');
                break;
            case 'ui':
                this.addToTerminal('🖼️ Rendering UI components...', 'info');
                this.addToTerminal('┌─────────────────────────────┐', 'output');
                this.addToTerminal('│  uDOS Professional Console │', 'output');
                this.addToTerminal('├─────────────────────────────┤', 'output');
                this.addToTerminal('│ [Commands] [Status] [Help]  │', 'output');
                this.addToTerminal('└─────────────────────────────┘', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown RENDER command: ${action}`, 'error');
                this.showModuleHelp('RENDER');
        }
    }
    
    // Dashboard module command handler
    handleDashCommand(action, args) {
        switch(action) {
            case 'live':
                this.addToTerminal('📊 Live System Dashboard', 'info');
                this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
                this.addToTerminal('System Status: ✅ OPERATIONAL    │    Uptime: 2d 14h 32m', 'output');
                this.addToTerminal('Active Users: 3                  │    Load Average: 0.67', 'output');
                this.addToTerminal('Memory Usage: 2.4GB / 8.0GB      │    Disk Free: 156GB', 'output');
                this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
                break;
            case 'performance':
                this.addToTerminal('⚡ Performance Metrics:', 'info');
                this.addToTerminal('• CPU: 68% (4 cores active)', 'output');
                this.addToTerminal('• Memory: 2.4GB used, 5.6GB available', 'output');
                this.addToTerminal('• I/O: 120 ops/sec read, 45 ops/sec write', 'output');
                this.addToTerminal('• Network: 15.2 Mbps in, 8.7 Mbps out', 'output');
                break;
            case 'system':
                this.addToTerminal('💻 System Information:', 'info');
                this.addToTerminal('• OS: uDOS Professional v2.1.3', 'output');
                this.addToTerminal('• Kernel: 5.15.0-ucore', 'output');
                this.addToTerminal('• Architecture: x86_64', 'output');
                this.addToTerminal('• Shell: uSHELL v3.0.1', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown DASH command: ${action}`, 'error');
                this.showModuleHelp('DASH');
        }
    }
    
    // Panel module command handler
    handlePanelCommand(action, args) {
        switch(action) {
            case 'system':
                this.addToTerminal('⚙️ System Control Panel:', 'info');
                this.addToTerminal('[1] Process Manager    [2] Service Control', 'output');
                this.addToTerminal('[3] System Settings    [4] Hardware Info', 'output');
                this.addToTerminal('[5] Network Config     [6] Security Panel', 'output');
                break;
            case 'user':
                this.addToTerminal('👤 User Management Panel:', 'info');
                this.addToTerminal('• Current User: admin (root privileges)', 'output');
                this.addToTerminal('• Active Sessions: 3', 'output');
                this.addToTerminal('• Last Login: 2024-01-15 09:15:32', 'output');
                break;
            case 'network':
                this.addToTerminal('🌐 Network Control Panel:', 'info');
                this.addToTerminal('• Interface: eth0 (192.168.1.100)', 'output');
                this.addToTerminal('• Status: Connected', 'output');
                this.addToTerminal('• Gateway: 192.168.1.1', 'output');
                this.addToTerminal('• DNS: 8.8.8.8, 8.8.4.4', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown PANEL command: ${action}`, 'error');
                this.showModuleHelp('PANEL');
        }
    }
    
    // Tree module command handler
    handleTreeCommand(action, args) {
        switch(action) {
            case 'generate':
                this.addToTerminal('🌳 Generating structure tree...', 'info');
                this.addToTerminal('uDOS/', 'output');
                this.addToTerminal('├── uCORE/', 'output');
                this.addToTerminal('│   ├── launcher/', 'output');
                this.addToTerminal('│   │   └── universal/', 'output');
                this.addToTerminal('│   └── config/', 'output');
                this.addToTerminal('├── uSCRIPT/', 'output');
                this.addToTerminal('├── uMEMORY/', 'output');
                this.addToTerminal('└── extensions/', 'output');
                break;
            case 'analyze':
                this.addToTerminal('🔍 Structure Analysis:', 'info');
                this.addToTerminal('• Total directories: 127', 'output');
                this.addToTerminal('• Total files: 892', 'output');
                this.addToTerminal('• Deepest level: 8', 'output');
                this.addToTerminal('• Largest directory: uCORE (234 files)', 'output');
                break;
            case 'visualize':
                this.addToTerminal('📊 Visual Tree Structure:', 'info');
                this.addToTerminal('', 'output');
                this.addToTerminal('          ┌─ uCORE', 'output');
                this.addToTerminal('          │', 'output');
                this.addToTerminal('   uDOS ──┼─ uSCRIPT', 'output');
                this.addToTerminal('          │', 'output');
                this.addToTerminal('          ├─ uMEMORY', 'output');
                this.addToTerminal('          │', 'output');
                this.addToTerminal('          └─ extensions', 'output');
                this.addToTerminal('', 'output');
                break;
            default:
                this.addToTerminal(`❌ Unknown TREE command: ${action}`, 'error');
                this.showModuleHelp('TREE');
        }
    }

    // System Module Handlers
    // Note: These are separate from uCODE modules and handle legacy system components

    // uCORE System Module Handler
    handleUCoreModule(action, args) {
        switch(action) {
            case 'status':
                this.addToTerminal('🔧 uCORE System Status:', 'info');
                this.addToTerminal('▶ Core Engine: ✅ Running', 'output');
                this.addToTerminal('▶ Configuration: ✅ Loaded', 'output');
                this.addToTerminal('▶ Launcher: ✅ Active', 'output');
                break;
            case 'restart':
                this.addToTerminal('🔄 Restarting uCORE engine...', 'info');
                this.addToTerminal('✅ uCORE engine restarted successfully', 'success');
                break;
            default:
                this.addToTerminal('🔧 uCORE - Core system management', 'info');
                this.addToTerminal('Available commands: status, restart, config, debug', 'output');
        }
    }

    // uSCRIPT System Module Handler
    handleUScriptModule(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('📝 Active Scripts:', 'info');
                this.addToTerminal('▶ setup-environment.sh - Environment setup', 'output');
                this.addToTerminal('▶ test-layout.us - Layout testing', 'output');
                this.addToTerminal('▶ uscript.sh - Main script processor', 'output');
                break;
            case 'run':
                if (args.length === 0) {
                    this.addToTerminal('❌ Usage: uSCRIPT run [script-name]', 'error');
                } else {
                    this.addToTerminal(`🏃 Running script: ${args[0]}`, 'info');
                    this.addToTerminal('Script execution completed', 'success');
                }
                break;
            default:
                this.addToTerminal('📝 uSCRIPT - Script automation system', 'info');
                this.addToTerminal('Available commands: list, run, edit, create', 'output');
        }
    }

    // Help System Functions
    showSystemHelp() {
        this.addToTerminal('🌟 uDOS Professional Console Help', 'info');
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
        this.addToTerminal('System Commands:', 'info');
        this.addToTerminal('▶ help         - Show this help', 'output');
        this.addToTerminal('▶ clear        - Clear terminal', 'output');
        this.addToTerminal('▶ history      - Show command history', 'output');
        this.addToTerminal('▶ status       - System status', 'output');
        this.addToTerminal('▶ modules      - List all modules', 'output');
        this.addToTerminal('▶ blocks       - Block graphics demo (hybrid mode)', 'output');
        this.addToTerminal('▶ font         - Font management (font <name>)', 'output');
        this.addToTerminal('▶ size         - Display size control (size <name> or size cycle)', 'output');
        this.addToTerminal('▶ ucode        - Enter uCODE mode', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('uCODE Modules (can be used directly):', 'info');
        Object.keys(this.ucodeModules).forEach(module => {
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.ucodeModules[module].description}`, 'output');
        });
        this.addToTerminal('', 'output');
        this.addToTerminal('System Modules:', 'info');
        Object.keys(this.systemModules).forEach(module => {
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.systemModules[module]}`, 'output');
        });
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    }

    showUCodeHelp() {
        this.addToTerminal('🎯 uCODE Mode - Advanced Command System', 'info');
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
        this.addToTerminal('Special Commands:', 'info');
        this.addToTerminal('▶ help         - Show this help', 'output');
        this.addToTerminal('▶ list         - List all modules', 'output');
        this.addToTerminal('▶ status       - uCODE system status', 'output');
        this.addToTerminal('▶ exit/quit    - Exit uCODE mode', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('Available Modules:', 'info');
        Object.keys(this.ucodeModules).forEach(module => {
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.ucodeModules[module].description}`, 'output');
        });
        this.addToTerminal('', 'output');
        this.addToTerminal('Usage: [MODULE] [command] [args...]', 'info');
        this.addToTerminal('Example: MEMORY list', 'output');
        this.addToTerminal('Example: MISSION create "New Project"', 'output');
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    }

    showModuleHelp(module) {
        const moduleInfo = this.ucodeModules[module];
        if (!moduleInfo) return;
        
        this.addToTerminal(`📚 ${module} Module Help`, 'info');
        this.addToTerminal(`Description: ${moduleInfo.description}`, 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('Available Commands:', 'info');
        Object.keys(moduleInfo.commands).forEach(cmd => {
            this.addToTerminal(`▶ ${cmd.padEnd(12)} - ${moduleInfo.commands[cmd]}`, 'output');
        });
        this.addToTerminal('', 'output');
        this.addToTerminal(`Usage: ${module} [command] [args...]`, 'info');
    }

    // Mode Management
    enterUCodeMode() {
        this.ucodeMode = true;
        this.currentMode = 'uCODE';
        this.updatePrompt();
        this.addToTerminal('🎯 Entering uCODE mode...', 'info');
        this.addToTerminal('Advanced command system activated', 'success');
        this.addToTerminal('Type "help" for available commands or "exit" to return to normal mode', 'info');
    }

    exitUCodeMode() {
        this.ucodeMode = false;
        this.currentMode = 'CONSOLE';
        this.updatePrompt();
        this.addToTerminal('📤 Exiting uCODE mode...', 'info');
        this.addToTerminal('Returned to standard console mode', 'success');
    }

    updatePrompt() {
        const promptElement = document.querySelector('.prompt-indicator');
        const modeIndicator = document.getElementById('mode-indicator');
        
        if (promptElement) {
            // Use WHIRL emoji for normal mode, special emoji for uCODE mode
            if (this.ucodeMode) {
                promptElement.textContent = '⚡uCODE>';
                promptElement.className = 'prompt-indicator ucode-mode';
            } else {
                promptElement.innerHTML = '🌀'; // WHIRL emoji
                promptElement.className = 'prompt-indicator normal-mode whirl-prompt';
            }
        }
        
        if (modeIndicator) {
            modeIndicator.textContent = this.currentMode;
            modeIndicator.style.color = this.ucodeMode ? 'var(--purple-plum)' : 'var(--caramel)';
        }
    }

    // Terminal Management
    addToTerminal(text, type = 'output') {
        const terminal = document.getElementById('terminal-output');
        if (!terminal) return;
        
        const line = document.createElement('div');
        line.className = `terminal-line ${type}`;
        line.textContent = text;
        
        // Inherit current font family from terminal
        const currentFont = terminal.style.fontFamily;
        if (currentFont) {
            line.style.fontFamily = currentFont;
        }
        
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }

    clearTerminal() {
        const terminal = document.getElementById('terminal-output');
        if (terminal) {
            terminal.innerHTML = '';
            this.addToTerminal('🧹 Terminal cleared', 'info');
        }
    }

    showCommandHistory() {
        this.addToTerminal('📋 Command History:', 'info');
        if (this.commandHistory.length === 0) {
            this.addToTerminal('No commands in history', 'output');
        } else {
            this.commandHistory.slice(-10).forEach((cmd, index) => {
                this.addToTerminal(`${index + 1}. ${cmd}`, 'output');
            });
        }
    }

    showSystemStatus() {
        this.addToTerminal('💻 System Status:', 'info');
        this.addToTerminal(`▶ Mode: ${this.currentMode}`, 'output');
        this.addToTerminal(`▶ Font: ${currentFont}`, 'output');
        this.addToTerminal(`▶ Display Size: ${displaySizes[currentDisplaySize].description}`, 'output');
        this.addToTerminal(`▶ Commands in history: ${this.commandHistory.length}`, 'output');
        this.addToTerminal(`▶ uCODE modules: ${Object.keys(this.ucodeModules).length}`, 'output');
        this.addToTerminal(`▶ System modules: ${Object.keys(this.systemModules).length}`, 'output');
    }

    handleFontCommand(args) {
        if (args.length === 0) {
            // Show current font and available options
            this.addToTerminal('🔤 Font Management:', 'info');
            this.addToTerminal(`▶ Current Font: ${currentFont}`, 'output');
            this.addToTerminal(`▶ Mode: Hybrid (1:1 text + 1:1.3 blocks)`, 'output');
            this.addToTerminal('', 'output');
            this.addToTerminal('▶ Available Fonts:', 'info');
            
            // Get available fonts for hybrid mode
            const availableFonts = fontModes['hybrid'];
            availableFonts.forEach((font, index) => {
                const isActive = font === currentFont ? '● ' : '○ ';
                this.addToTerminal(`${isActive}${font}`, 'output');
            });
            
            this.addToTerminal('', 'output');
            this.addToTerminal('▶ Usage: FONT <fontname>', 'info');
            return;
        }

        // Try to find and set the font
        const targetFont = args.join(' ');
        let fontFound = false;
        
        // Search through hybrid mode fonts
        const fonts = fontModes['hybrid'];
        const matchingFont = fonts.find(font => 
            font.toLowerCase().includes(targetFont.toLowerCase()) ||
            targetFont.toLowerCase().includes(font.toLowerCase())
        );
        
        if (matchingFont) {
            changeFont(matchingFont);
            this.addToTerminal(`✅ Font changed to: ${matchingFont}`, 'success');
            fontFound = true;
        }
        
        if (!fontFound) {
            this.addToTerminal(`❌ Font not found: ${targetFont}`, 'error');
            this.addToTerminal('▶ Use FONT without arguments to see available fonts', 'info');
        }
    }

    handleSizeCommand(args) {
        if (args.length === 0) {
            // Show current size and available options
            this.addToTerminal('📏 Display Size Management:', 'info');
            this.addToTerminal(`▶ Current Size: ${displaySizes[currentDisplaySize].description}`, 'output');
            this.addToTerminal('', 'output');
            this.addToTerminal('▶ Available Sizes:', 'info');
            
            Object.keys(displaySizes).forEach(size => {
                const isActive = size === currentDisplaySize ? '● ' : '○ ';
                this.addToTerminal(`${isActive}${displaySizes[size].description} (${displaySizes[size].size})`, 'output');
            });
            
            this.addToTerminal('', 'output');
            this.addToTerminal('▶ Usage: SIZE <name> or SIZE CYCLE', 'info');
            this.addToTerminal('▶ Names: tiny, small, normal, medium, large, huge, giant', 'info');
            return;
        }

        const command = args[0].toLowerCase();
        
        if (command === 'cycle') {
            cycleDisplaySize();
            return;
        }

        // Try to find and set the size
        const targetSize = command;
        if (displaySizes[targetSize]) {
            currentDisplaySize = targetSize;
            const sizeConfig = displaySizes[targetSize];
            
            // Apply the new size
            const terminalOutput = document.getElementById('terminal-output');
            const commandInput = document.getElementById('command-input');
            
            if (terminalOutput) {
                terminalOutput.style.fontSize = sizeConfig.size;
                terminalOutput.style.lineHeight = sizeConfig.lineHeight;
            }
            
            if (commandInput) {
                commandInput.style.fontSize = sizeConfig.size;
                commandInput.style.lineHeight = sizeConfig.lineHeight;
            }
            
            // Update CSS custom property
            document.documentElement.style.setProperty('--terminal-font-size', sizeConfig.size);
            document.documentElement.style.setProperty('--terminal-line-height', sizeConfig.lineHeight);
            
            this.addToTerminal(`✅ Display size changed to: ${sizeConfig.description}`, 'success');
        } else {
            this.addToTerminal(`❌ Size not found: ${targetSize}`, 'error');
            this.addToTerminal('▶ Use SIZE without arguments to see available sizes', 'info');
        }
    }

    showBlockGraphicsDemo() {
        this.addToTerminal('🧱 Block Graphics Demo - Hybrid Mode (1:1 text + 1:1.3 blocks)', 'info');
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
        this.addToTerminal('', 'output');
        
        // Full blocks example
        this.addToTerminal('▶ Full Blocks:', 'info');
        this.addToTerminal('██████████████████████████████████████████████████████████████████████████', 'output');
        this.addToTerminal('', 'output');
        
        // Half blocks
        this.addToTerminal('▶ Half Blocks (Upper/Lower):', 'info');
        this.addToTerminal('▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀', 'output');
        this.addToTerminal('▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄', 'output');
        this.addToTerminal('', 'output');
        
        // Side blocks
        this.addToTerminal('▶ Side Blocks (Left/Right):', 'info');
        this.addToTerminal('▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌▌', 'output');
        this.addToTerminal('▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐', 'output');
        this.addToTerminal('', 'output');
        
        // Quarter blocks
        this.addToTerminal('▶ Quarter Blocks:', 'info');
        this.addToTerminal('▘▘▘▘▘▘▘▘▘▘ ▝▝▝▝▝▝▝▝▝▝ ▖▖▖▖▖▖▖▖▖▖ ▗▗▗▗▗▗▗▗▗▗', 'output');
        this.addToTerminal('', 'output');
        
        // Shading patterns
        this.addToTerminal('▶ Shading Patterns (BBC Micro style):', 'info');
        this.addToTerminal('░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ Light', 'output');
        this.addToTerminal('▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ Medium', 'output');
        this.addToTerminal('▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ Dark', 'output');
        this.addToTerminal('', 'output');
        
        // Art example
        this.addToTerminal('▶ Block Art Example (2-color display):', 'info');
        this.addToTerminal('██████████████████████████████████████████████████████████████████████████', 'output');
        this.addToTerminal('██▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀██', 'output');
        this.addToTerminal('██▌ uDOS Professional Console - Block Graphics Demo           ▐██', 'output');
        this.addToTerminal('██▌ Hybrid Mode: 1:1 text rendering + 1:1.3 block graphics   ▐██', 'output');
        this.addToTerminal('██▌ Compatible with BBC Micro Mode 7 & Teletext standards    ▐██', 'output');
        this.addToTerminal('██▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄██', 'output');
        this.addToTerminal('██████████████████████████████████████████████████████████████████████████', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('💡 Switch to Hybrid mode in font controls to see optimal block graphics!', 'info');
        this.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    }

    listModules() {
        this.addToTerminal('📦 Available Modules:', 'info');
        this.addToTerminal('', 'output');
        this.addToTerminal('uCODE Modules:', 'info');
        Object.keys(this.ucodeModules).forEach(module => {
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.ucodeModules[module].description}`, 'output');
        });
        this.addToTerminal('', 'output');
        this.addToTerminal('System Modules:', 'info');
        Object.keys(this.systemModules).forEach(module => {
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.systemModules[module]}`, 'output');
        });
    }

    listUCodeModules() {
        this.addToTerminal('🎯 uCODE Modules:', 'info');
        Object.keys(this.ucodeModules).forEach(module => {
            const commandCount = Object.keys(this.ucodeModules[module].commands).length;
            this.addToTerminal(`▶ ${module.padEnd(10)} - ${this.ucodeModules[module].description} (${commandCount} commands)`, 'output');
        });
    }

    showUCodeStatus() {
        this.addToTerminal('🎯 uCODE System Status:', 'info');
        this.addToTerminal(`▶ Mode: ${this.ucodeMode ? 'ACTIVE' : 'INACTIVE'}`, 'output');
        this.addToTerminal(`▶ Available modules: ${Object.keys(this.ucodeModules).length}`, 'output');
        this.addToTerminal(`▶ Total commands: ${Object.values(this.ucodeModules).reduce((sum, module) => sum + Object.keys(module.commands).length, 0)}`, 'output');
        this.addToTerminal(`▶ Commands executed: ${this.commandHistory.length}`, 'output');
    }

    // Auto-completion and suggestions
    showSuggestions(input) {
        // Implementation for command suggestions would go here
        // This is a placeholder for future enhancement
    }

    autoComplete(inputElement) {
        // Implementation for tab completion would go here
        // This is a placeholder for future enhancement
    }

    hideSuggestions() {
        // Implementation for hiding suggestions would go here
    }

    updateTypingIndicator() {
        // Implementation for typing indicator would go here
    }

    // Network communication
    initializeSocket() {
        // Implementation for WebSocket communication would go here
        // This would connect to the uSERVER backend
    }

    sendToServer(command) {
        this.addToTerminal(`🌐 Sending to server: ${command}`, 'info');
        // This would send the command to the backend server
        // For now, just show a placeholder response
        setTimeout(() => {
            this.addToTerminal('Server response: Command processed', 'output');
        }, 500);
    }

    handleGlobalShortcuts(e) {
        // Ctrl+L to clear terminal
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            this.clearTerminal();
        }
        
        // Ctrl+U to toggle uCODE mode
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            if (this.ucodeMode) {
                this.exitUCodeMode();
            } else {
                this.enterUCodeMode();
            }
        }
    }
}

// Initialize the command system
let commandSystem;
document.addEventListener('DOMContentLoaded', () => {
    commandSystem = new UDOSCommandSystem();
    
    // Display welcome message with comprehensive system info
    commandSystem.addToTerminal('🌟 uDOS Professional Console v2.1.3', 'info');
    commandSystem.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    commandSystem.addToTerminal('🚀 Integrated uCODE & Modular Command System Active', 'success');
    commandSystem.addToTerminal('✅ All systems operational with WHIRL emoji prompt 🌀', 'success');
    commandSystem.addToTerminal(`📦 ${Object.keys(commandSystem.ucodeModules).length} uCODE modules loaded: ${Object.keys(commandSystem.ucodeModules).join(', ')}`, 'info');
    commandSystem.addToTerminal(`🔧 ${Object.keys(commandSystem.systemModules).length} system modules available`, 'info');
    commandSystem.addToTerminal('', 'output');
    commandSystem.addToTerminal('💡 Quick Start:', 'info');
    commandSystem.addToTerminal('▶ Type "help" for complete command list', 'output');
    commandSystem.addToTerminal('▶ Type "ucode" for advanced uCODE mode ⚡', 'output');
    commandSystem.addToTerminal('▶ Try: MEMORY list, MISSION track, LOG report, DASH live', 'output');
    commandSystem.addToTerminal('▶ Use quick buttons: TREE, LOG, DEV, DASH, CLEAR', 'output');
    commandSystem.addToTerminal('', 'output');
    commandSystem.addToTerminal('⌨️  Keyboard Shortcuts:', 'info');
    commandSystem.addToTerminal('▶ Ctrl+L = Clear terminal', 'output');
    commandSystem.addToTerminal('▶ Ctrl+U = Toggle uCODE mode', 'output');
    commandSystem.addToTerminal('▶ ↑/↓ = Command history', 'output');
    commandSystem.addToTerminal('▶ Tab = Auto-complete (future)', 'output');
    commandSystem.addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    
    // Focus command input
    document.getElementById('command-input').focus();
});

// Block Graphics Support for Hybrid Mode
function renderBlockGraphics(text, useBlockMode = false) {
    if (!useBlockMode || currentFontMode !== 'hybrid') {
        return text;
    }
    
    // Convert text to block graphics with 1:1.3 aspect ratio
    return text.split('').map(char => {
        // Check if character is a block graphic character
        if (char.charCodeAt(0) >= 0x2580 && char.charCodeAt(0) <= 0x259F) {
            return `<span class="block-char teletext-block">${char}</span>`;
        }
        return char;
    }).join('');
}

// Enhanced block graphics character set
const blockChars = {
    // Full blocks
    'full': '█',
    'upper': '▀',
    'lower': '▄',
    'left': '▌',
    'right': '▐',
    
    // Quarter blocks  
    'tl': '▘',     // top-left
    'tr': '▝',     // top-right
    'bl': '▖',     // bottom-left
    'br': '▗',     // bottom-right
    
    // Half blocks combined
    'top': '▀',    // top half
    'bottom': '▄', // bottom half
    'left_half': '▌',   // left half
    'right_half': '▐',  // right half
    
    // Shading
    'light': '░',
    'medium': '▒',
    'dark': '▓',
    'solid': '█'
};

// Function to create block graphics with 2-color support
function createBlockGraphic(pattern, fgColor = 'white', bgColor = 'black') {
    const char = blockChars[pattern] || pattern;
    return `<span class="block-graphics fg-${fgColor} bg-${bgColor}">${char}</span>`;
}

// Enhanced Font Mode Switching with System Fonts
// Enhanced Font Mode Application with Emoji Support
// Apply hybrid mode styling (locked to hybrid mode)
function applyFontMode() {
    const terminal = document.getElementById('terminal-output');
    
    if (terminal) {
        // Always use hybrid mode: 1:1 text with block graphics capability
        terminal.style.fontStretch = 'normal';
        terminal.style.letterSpacing = '0px';
        terminal.style.lineHeight = '1.2'; // Slightly spaced for block graphics
        terminal.classList.add('hybrid-mode');
        terminal.style.fontWeight = 'bold';
        terminal.style.textRendering = 'optimizeSpeed';
        
        // Add emoji font fallback for enhanced emoji support
        const currentFontFamily = terminal.style.fontFamily || '';
        if (!currentFontFamily.includes('Apple Color Emoji')) {
            terminal.style.fontFamily = currentFontFamily + ', Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji';
        }
    }
    
    // Update CSS custom properties for hybrid mode
    document.documentElement.style.setProperty('--font-aspect-ratio', '1.3');
    document.documentElement.style.setProperty('--current-font-mode', 'hybrid');
    
    console.log('🎨 Applied hybrid font mode with emoji support');
    
    // Apply the current font
    setTimeout(() => changeFont(), 50);
}

// Global font change function for dropdown
function changeFont() {
    const fontSelector = document.getElementById('fontSelector');
    const selectedFont = fontSelector.value;
    const terminal = document.getElementById('terminal-output');
    
    if (!terminal || !selectedFont) return;
    
    console.log(`🔤 Changing font to: ${selectedFont}`);
    
    // Build font family string with fallbacks
    let fontFamily = selectedFont;
    
    // Handle font files vs system fonts
    if (selectedFont.includes('.ttf') || selectedFont.includes('.TTF')) {
        // For font files, remove extension for CSS family name
        const baseName = selectedFont.replace(/\.(ttf|TTF)$/, '');
        fontFamily = baseName;
        
        // Load font if it's a file
        loadCustomFont(selectedFont, baseName);
    } else {
        // For system fonts, use them directly
        fontFamily = selectedFont;
    }
    
    // Add appropriate fallbacks based on font type
    if (selectedFont.includes('MODE7GX') || selectedFont.includes('Teletext')) {
        fontFamily += ', MODE7GX, Teletext50, Share Tech Mono, monospace';
    } else if (selectedFont.includes('topaz')) {
        fontFamily += ', Topaz, Amiga, monospace';
    } else if (selectedFont.includes('Pet Me') || selectedFont.includes('C64')) {
        fontFamily += ', "Pet Me 64", "Pet Me 128", C64, monospace';
    } else if (selectedFont.includes('Mallard')) {
        fontFamily += ', "Mallard Neueue", "Mallard Blocky", monospace';
    } else if (selectedFont.includes('microknight') || selectedFont.includes('MicroKnight')) {
        fontFamily += ', MicroKnight, monospace';
    } else if (selectedFont.includes('pot_noodle')) {
        fontFamily += ', pot_noodle, VT323, monospace';
    } else if (selectedFont === 'Consolas') {
        fontFamily = 'Consolas, "Courier New", monospace';
    } else if (selectedFont === 'Monaco') {
        fontFamily = 'Monaco, "Lucida Console", monospace';
    } else if (selectedFont === 'Menlo') {
        fontFamily = 'Menlo, Monaco, "Courier New", monospace';
    } else if (selectedFont === 'SF Mono') {
        fontFamily = '"SF Mono", Monaco, "Inconsolata", "Roboto Mono", "Source Code Pro", monospace';
    } else if (selectedFont === 'JetBrains Mono') {
        fontFamily = '"JetBrains Mono", "Fira Code", "Source Code Pro", monospace';
    } else {
        fontFamily += ', monospace';
    }
    
    // Add emoji support
    fontFamily += ', Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji';
    
    // Apply font to terminal
    terminal.style.fontFamily = fontFamily;
    
    // Update all terminal lines
    const terminalLines = terminal.querySelectorAll('.terminal-line');
    terminalLines.forEach(line => {
        line.style.fontFamily = fontFamily;
    });
    
    // Store current font for new lines
    if (window.udos && window.udos.changeFont) {
        window.udos.changeFont(selectedFont);
    }
    
    console.log(`✅ Font applied: ${fontFamily}`);
}

// Function to load custom fonts
function loadCustomFont(fileName, familyName) {
    const fontPath = `/static/fonts/${fileName}`;
    
    // Check if font is already loaded
    if (document.querySelector(`style[data-font="${familyName}"]`)) {
        return;
    }
    
    // Create font-face CSS
    const style = document.createElement('style');
    style.setAttribute('data-font', familyName);
    style.textContent = `
        @font-face {
            font-family: '${familyName}';
            src: url('${fontPath}') format('truetype');
            font-display: swap;
        }
    `;
    
    document.head.appendChild(style);
    console.log(`📦 Loaded custom font: ${familyName} from ${fontPath}`);
}

// Font Preview Modal
function showFontPreview() {
    const modal = document.getElementById('fontPreviewModal');
    const modeSelector = document.getElementById('fontModeSelector');
    const fontSelector = document.getElementById('fontSelector');
    
    // Update preview settings
    previewSettings.mode = modeSelector.value;
    previewSettings.font = fontSelector.value;
    previewSettings.aspectRatio = fontModes[previewSettings.mode].aspectRatio;
    
    // Set initial values in modal
    document.getElementById('previewMode').value = previewSettings.mode;
    document.getElementById('previewFont').value = previewSettings.font;
    document.getElementById('previewSize').value = previewSettings.size;
    document.getElementById('fontSizeValue').textContent = previewSettings.size + 'px';
    
    // Update font options in preview
    updatePreviewFontOptions();
    
    // Apply initial preview
    updatePreview();
    
    // Show modal
    modal.style.display = 'flex';
    
    // Add event listeners
    document.getElementById('previewMode').addEventListener('change', updatePreviewMode);
    document.getElementById('previewFont').addEventListener('change', updatePreview);
    document.getElementById('previewSize').addEventListener('input', updatePreviewSize);
}

// Close font preview modal
function closeFontPreview() {
    document.getElementById('fontPreviewModal').style.display = 'none';
}

// Update preview font options based on mode
function updatePreviewFontOptions() {
    const modeSelect = document.getElementById('previewMode');
    const fontSelect = document.getElementById('previewFont');
    const mode = fontModes[modeSelect.value];
    
    fontSelect.innerHTML = '';
    mode.fonts.forEach(font => {
        const option = document.createElement('option');
        option.value = font;
        
        // Create display name with emojis
        let displayName = font;
        if (font.includes('.ttf') || font.includes('.TTF')) {
            displayName = font.replace(/\.(ttf|TTF)$/, '');
        }
        displayName = displayName.replace(/MODE7GX-|Topaz-|MicroKnight-/g, '');
        
        // Add emojis
        if (font.includes('MODE7')) displayName = '📺 ' + displayName;
        else if (font.includes('topaz')) displayName = '🎮 ' + displayName;
        else if (font.includes('microknight')) displayName = '⚔️ ' + displayName;
        else if (font.includes('pot_noodle')) displayName = '🍜 ' + displayName;
        else if (font.includes('JetBrains')) displayName = '✈️ ' + displayName;
        else if (font.includes('Monaco')) displayName = '⌨️ ' + displayName;
        else if (font === 'monospace') displayName = '🔤 System Monospace';
        
        option.textContent = displayName;
        fontSelect.appendChild(option);
    });
    
    // Set current font if it exists in the new mode
    if (mode.fonts.includes(previewSettings.font)) {
        fontSelect.value = previewSettings.font;
    } else {
        fontSelect.value = mode.defaultFont;
        previewSettings.font = mode.defaultFont;
    }
}

// Update preview mode
function updatePreviewMode() {
    const modeSelect = document.getElementById('previewMode');
    previewSettings.mode = modeSelect.value;
    previewSettings.aspectRatio = fontModes[previewSettings.mode].aspectRatio;
    
    updatePreviewFontOptions();
    updatePreview();
}

// Update preview size
function updatePreviewSize() {
    const sizeSlider = document.getElementById('previewSize');
    previewSettings.size = parseInt(sizeSlider.value);
    document.getElementById('fontSizeValue').textContent = previewSettings.size + 'px';
    updatePreview();
}

// Update all preview samples
function updatePreview() {
    const fontSelect = document.getElementById('previewFont');
    const selectedFont = fontSelect.value;
    const samples = document.querySelectorAll('.font-sample');
    
    // Get font family name
    let fontFamily = selectedFont;
    if (selectedFont.includes('.ttf') || selectedFont.includes('.TTF')) {
        fontFamily = selectedFont.replace(/\.(ttf|TTF)$/, '');
        // Load the custom font
        loadCustomFont(selectedFont, fontFamily);
    }
    
    // Build complete font family with fallbacks for different font types
    let completeFontFamily = fontFamily;
    if (selectedFont.includes('MODE7GX') || selectedFont.includes('Teletext')) {
        completeFontFamily += ', MODE7GX, Teletext50, Share Tech Mono, monospace';
    } else if (selectedFont.includes('topaz')) {
        completeFontFamily += ', Topaz, Amiga, monospace';
    } else if (selectedFont.includes('microknight')) {
        completeFontFamily += ', MicroKnight, monospace';
    } else if (selectedFont.includes('pot_noodle')) {
        completeFontFamily += ', pot_noodle, VT323, monospace';
    } else if (selectedFont === 'Consolas') {
        completeFontFamily = 'Consolas, "Courier New", monospace';
    } else if (selectedFont === 'Monaco') {
        completeFontFamily = 'Monaco, "Lucida Console", monospace';
    } else if (selectedFont === 'Menlo') {
        completeFontFamily = 'Menlo, Monaco, "Courier New", monospace';
    } else if (selectedFont === 'SF Mono') {
        completeFontFamily = '"SF Mono", Monaco, "Inconsolata", "Roboto Mono", monospace';
    } else if (selectedFont === 'JetBrains Mono') {
        completeFontFamily = '"JetBrains Mono", "Fira Code", "Source Code Pro", monospace';
    } else {
        completeFontFamily += ', monospace';
    }
    
    // Add emoji support
    completeFontFamily += ', Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji';
    
    samples.forEach(sample => {
        sample.style.fontFamily = completeFontFamily;
        sample.style.fontSize = previewSettings.size + 'px';
        
        // Apply mode-specific styling
        if (previewSettings.mode === 'hybrid') {
            sample.style.lineHeight = '1.2';
            sample.style.letterSpacing = '0px';
        } else if (previewSettings.mode === 'retro') {
            sample.style.lineHeight = '1.0';
            sample.style.letterSpacing = '0px';
        } else {
            sample.style.lineHeight = '1.1';
            sample.style.letterSpacing = '0px';
        }
    });
    
    // Update mode indicator
    const modeIndicator = document.querySelector('.modal-header h2');
    if (modeIndicator) {
        const displayName = selectedFont.includes('.') ? selectedFont.replace(/\.(ttf|TTF)$/, '') : selectedFont;
        modeIndicator.textContent = `🔤 Font Preview - ${previewSettings.mode.toUpperCase()} Mode - ${displayName}`;
    }
    
    console.log(`🔤 Preview updated: ${completeFontFamily}`);
}

// Apply preview settings to main interface
function applyPreviewFont() {
    const modeSelector = document.getElementById('fontModeSelector');
    const fontSelector = document.getElementById('fontSelector');
    
    // Update main selectors
    modeSelector.value = previewSettings.mode;
    fontSelector.value = previewSettings.font;
    
    // Apply hybrid font mode
    applyFontMode();
    
    // Apply font to terminal (if available)
    if (window.udos && window.udos.changeFont) {
        window.udos.changeFont(previewSettings.font.replace('.ttf', ''));
    }
    
    // Close modal
    closeFontPreview();
    
    console.log(`Applied font: ${previewSettings.font} in ${previewSettings.mode} mode`);
}

// Reset preview to current settings
function resetPreview() {
    const modeSelector = document.getElementById('fontModeSelector');
    const fontSelector = document.getElementById('fontSelector');
    
    previewSettings.mode = modeSelector.value;
    previewSettings.font = fontSelector.value;
    previewSettings.aspectRatio = fontModes[previewSettings.mode].aspectRatio;
    
    document.getElementById('previewMode').value = previewSettings.mode;
    document.getElementById('previewFont').value = previewSettings.font;
    document.getElementById('previewSize').value = 20;
    document.getElementById('fontSizeValue').textContent = '20px';
    
    previewSettings.size = 20;
    updatePreview();
}

// Test font in live terminal
function testInTerminal() {
    applyPreviewFont();
    // Focus terminal for immediate testing
    const terminal = document.getElementById('command-input');
    if (terminal) terminal.focus();
}

// uDOS Rainbow Block Graphics Interface JavaScript
class UDOSInterface {
    constructor() {
        this.socket = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentMode = 'DEV';
        this.promptEmojis = {
            'DEV': '🌟',
            'USER': '👤',
            'ADMIN': '⚡',
            'GHOST': '👻',
            'SORCERER': '🔮',
            'IMP': '😈',
            'WIZARD': '🧙‍♂️',
            'RAINBOW': '🌈'
        };
        this.currentFont = 'mode7gx3';  // Default to authentic MODE7GX3 
        this.currentTheme = 'teletext';  // Teletext mode default
        this.displayManager = null;  // Will be initialized in init()
        this.ucodeMode = false;  // Track if we're in uCODE mode
        this.ucodeCommands = [  // Available uCODE commands
            'MEMORY', 'MISSION', 'PACKAGE', 'LOG', 'DEV', 'RENDER', 'DASH', 'PANEL', 'TREE'
        ];
        this.init();
    }

    init() {
        // Initialize Display Manager
        this.displayManager = new uDOSDisplayManager();
        window.uDOSInterface = this; // Make available globally for display manager
        
        // Initialize Socket.IO connection
        this.socket = io();
        this.setupEventListeners();
        this.setupSocketHandlers();
        this.startPromptRotation();
        
        // Set default font and theme
        document.body.classList.add('font-teletext');
        document.body.classList.add('theme-teletext');  // Default to teletext palette
        
        // Focus command input
        document.getElementById('command-input').focus();
    }

    setupEventListeners() {
        const commandInput = document.getElementById('command-input');
        const commandContainer = document.querySelector('.command-input-container');
        
        // Enhanced input field functionality
        let typingTimer;
        let isTyping = false;
        
        commandInput.addEventListener('input', (e) => {
            // Show typing indicator
            if (!isTyping) {
                isTyping = true;
                this.showTypingIndicator(true);
            }
            
            // Clear existing timer
            clearTimeout(typingTimer);
            
            // Set timer to hide typing indicator
            typingTimer = setTimeout(() => {
                isTyping = false;
                this.showTypingIndicator(false);
            }, 500);
            
            // Show command suggestions
            this.showCommandSuggestions(e.target.value);
        });
        
        // Handle command input
        commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                // Show command execution feedback
                commandContainer.classList.add('command-executing');
                setTimeout(() => {
                    commandContainer.classList.remove('command-executing');
                }, 500);
                
                this.executeCommand(commandInput.value.trim());
                commandInput.value = '';
                this.hideCommandSuggestions();
            }
            // Command history navigation
            else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (this.historyIndex < this.commandHistory.length - 1) {
                    this.historyIndex++;
                    commandInput.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
                }
            }
            else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (this.historyIndex > 0) {
                    this.historyIndex--;
                    commandInput.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
                } else {
                    this.historyIndex = -1;
                    commandInput.value = '';
                }
            }
            // Tab completion
            else if (e.key === 'Tab') {
                e.preventDefault();
                this.handleTabCompletion(commandInput);
            }
            // Show history with Ctrl+R
            else if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.showCommandHistory();
            }
            // Escape to hide suggestions
            else if (e.key === 'Escape') {
                this.hideCommandSuggestions();
                this.hideCommandHistory();
            }
        });
        
        // Focus management
        commandInput.addEventListener('focus', () => {
            this.updateInputStatus('focused');
        });
        
        commandInput.addEventListener('blur', () => {
            // Delay hiding suggestions to allow clicking
            setTimeout(() => {
                this.hideCommandSuggestions();
                this.hideCommandHistory();
            }, 200);
            this.updateInputStatus('blurred');
        });
    }

    setupSocketHandlers() {
        // Connection status
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
            this.addToTerminal('🌐 Connected to uDOS server', 'success');
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
            this.addToTerminal('⚠️ Disconnected from server', 'warning');
        });

        // Command responses
        this.socket.on('command_response', (data) => {
            this.addToTerminal(data.output, data.type || 'output');
        });

        // Server messages
        this.socket.on('server_message', (data) => {
            this.addToTerminal(data.message, data.type || 'info');
        });

        // Status updates
        this.socket.on('status_update', (data) => {
            this.updateSystemStatus(data);
        });

        // Font change updates from server
        this.socket.on('font_update', (data) => {
            if (data.font) {
                this.changeFont(data.font);
            }
        });

        // Palette change updates from server
        this.socket.on('palette_update', (data) => {
            if (data.palette) {
                this.changePalette(data.palette);
            }
        });

        // Display mode updates from server
        this.socket.on('display_update', (data) => {
            if (data.mode && this.displayManager) {
                this.displayManager.setDisplayMode(data.mode);
            }
        });

        // Clear terminal command
        this.socket.on('clear_terminal', () => {
            this.clearTerminal();
        });

        // Command result from server
        this.socket.on('command_result', (data) => {
            if (data.result && data.result.output) {
                this.addToTerminal(data.result.output, data.result.success ? 'output' : 'error');
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('status');
        if (connected) {
            statusElement.textContent = '●●● CONNECTED';
            statusElement.className = 'status connected';
        } else {
            statusElement.textContent = '●●● DISCONNECTED';
            statusElement.className = 'status disconnected';
        }
    }

    executeCommand(command) {
        if (!command) return;
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = -1;
        
        // Handle uCODE mode differently
        if (this.ucodeMode) {
            this.addToTerminal(`🌪️ uCODE> ${command}`, 'command');
            this.handleUCodeCommand(command);
        } else {
            // Display command with current mode
            this.addToTerminal(`${this.promptEmojis[this.currentMode]} uDOS:${this.currentMode} $ ${command}`, 'command');
            
            // Handle local commands first
            if (this.handleLocalCommand(command)) {
                return;
            }
            
            // Send to server
            this.socket.emit('execute_command', {
                command: command,
                mode: this.currentMode
            });
        }
    }

    handleLocalCommand(command) {
        const cmd = command.toLowerCase().trim();
        
        if (cmd === 'help') {
            this.addToTerminal('🎮 uDOS Commands:', 'info');
            this.addToTerminal('  help       - Show this help', 'output');
            this.addToTerminal('  status     - Show system status', 'output');
            this.addToTerminal('  ucode      - Enter uCODE whirl prompt', 'output');
            this.addToTerminal('  rainbow    - Activate rainbow mode', 'output');
            this.addToTerminal('  whirlwind  - Activate whirlwind prompts', 'output');
            this.addToTerminal('  font [name] - Change font (teletext/c64/terminal/amiga)', 'output');
            this.addToTerminal('  display [mode] - Set display mode (bbc/c64/amiga/terminal)', 'output');
            this.addToTerminal('  size [WxH] - Set window size (320x200/640x480/etc)', 'output');
            this.addToTerminal('  kiosk [on/off] - Toggle kiosk mode', 'output');
            this.addToTerminal('  pixels [on/off] - Toggle pixel perfect rendering', 'output');
            this.addToTerminal('  saa5050    - Show SAA5050 block graphics', 'output');
            this.addToTerminal('  clear      - Clear terminal', 'output');
            this.addToTerminal('  ascii      - Show ASCII art demo', 'output');
            this.addToTerminal('  theme [name] - Change theme (dark/light/professional/rainbow)', 'output');
            this.addToTerminal('', 'output');
            this.addToTerminal('⚡ Quick Commands (buttons or keyboard):', 'info');
            this.addToTerminal('  TREE       - Generate repository structure (Ctrl+T)', 'output');
            this.addToTerminal('  MEM        - Memory file list (Ctrl+M)', 'output');
            this.addToTerminal('  DASH       - Live dashboard (Ctrl+D)', 'output');
            this.addToTerminal('  LOG        - Log report (Ctrl+L)', 'output');
            this.addToTerminal('  DEV        - Development status', 'output');
            this.addToTerminal('  CLR        - Clear terminal (Ctrl+K)', 'output');
            this.addToTerminal('', 'output');
            this.addToTerminal('📺 Display Sizes (buttons or function keys):', 'info');
            this.addToTerminal('  320×200    - Retro mode (F1)', 'output');
            this.addToTerminal('  640×400    - Classic mode (F2)', 'output');
            this.addToTerminal('  640×500    - Default mode (F3)', 'output');
            this.addToTerminal('  800×600    - Extended mode (F4)', 'output');
            this.addToTerminal('  1024×768   - Full mode (F5)', 'output');
            this.addToTerminal('', 'output');
            this.addToTerminal('💡 Smart Input Features:', 'info');
            this.addToTerminal('  Tab        - Auto-complete commands', 'output');
            this.addToTerminal('  Ctrl+R     - Show command history', 'output');
            this.addToTerminal('  Escape     - Hide suggestions/history', 'output');
            this.addToTerminal('  ↑/↓        - Navigate command history', 'output');
            this.addToTerminal('  Auto-scroll - Terminal scrolls smartly', 'output');
            this.addToTerminal('  Suggestions - Type to see command hints', 'output');
            return true;
        }
        
        if (cmd === 'ucode') {
            this.enterUCodeMode();
            return true;
        }
        
        if (cmd === 'clear') {
            document.getElementById('terminal-output').innerHTML = '';
            return true;
        }
        
        if (cmd.startsWith('font ')) {
            const fontName = cmd.split(' ')[1];
            this.changeFont(fontName);
            return true;
        }
        
        if (cmd.startsWith('display ')) {
            const displayMode = cmd.split(' ')[1];
            if (this.displayManager.setDisplayMode(displayMode)) {
                // Success message is handled by display manager
            } else {
                this.addToTerminal('❌ Available display modes: bbc, c64, amiga, terminal, modern', 'error');
            }
            return true;
        }
        
        if (cmd.startsWith('size ')) {
            const sizeSpec = cmd.split(' ')[1];
            if (this.displayManager.setWindowSize(sizeSpec)) {
                // Success message is handled by display manager
            } else {
                this.addToTerminal('❌ Invalid size format. Use: size 640x480', 'error');
                this.addToTerminal('📏 Available sizes: 320x200, 320x240, 320x250, 640x200, 640x256, 640x400, 640x480, 800x600, 1024x768', 'info');
            }
            return true;
        }
        
        if (cmd.startsWith('kiosk')) {
            const parts = cmd.split(' ');
            const toggle = parts[1] ? parts[1] === 'on' : null;
            const enabled = this.displayManager.toggleKioskMode(toggle);
            // Success message is handled by display manager
            return true;
        }
        
        if (cmd.startsWith('pixels')) {
            const parts = cmd.split(' ');
            const toggle = parts[1] ? parts[1] === 'on' : null;
            const enabled = this.displayManager.togglePixelPerfect(toggle);
            // Success message is handled by display manager
            return true;
        }
        
        if (cmd === 'display') {
            const info = this.displayManager.getDisplayInfo();
            this.addToTerminal('📺 Current Display Configuration:', 'info');
            this.addToTerminal(`   Mode: ${info.mode.toUpperCase()}`, 'output');
            this.addToTerminal(`   Resolution: ${info.width}×${info.height}`, 'output');
            this.addToTerminal(`   Characters: ${info.chars[0]}×${info.chars[1]}`, 'output');
            this.addToTerminal(`   Aspect Ratio: ${info.aspect}:1`, 'output');
            this.addToTerminal(`   Kiosk Mode: ${info.kioskMode ? 'ON' : 'OFF'}`, 'output');
            this.addToTerminal(`   Pixel Perfect: ${info.pixelPerfect ? 'ON' : 'OFF'}`, 'output');
            return true;
        }
        
        if (cmd === 'saa5050') {
            this.showSAA5050Graphics();
            return true;
        }
        
        if (cmd === 'rainbow') {
            this.activateRainbowMode();
            return true;
        }
        
        if (cmd === 'whirlwind') {
            this.activateWhirlwindMode();
            return true;
        }
        
        if (cmd.startsWith('theme ')) {
            const theme = cmd.split(' ')[1];
            this.changeTheme(theme);
            return true;
        }
        
        return false;
    }

    changeMode(mode) {
        this.currentMode = mode.toUpperCase();
        this.updatePrompt();
        this.addToTerminal(`🔄 Mode changed to ${this.currentMode}`, 'success');
        
        // Emit mode change to server
        this.socket.emit('mode_change', { mode: this.currentMode });
    }

    updatePrompt() {
        const promptElement = document.getElementById('dynamic-prompt');
        promptElement.textContent = `${this.promptEmojis[this.currentMode]} uDOS:${this.currentMode} $`;
    }

    startPromptRotation() {
        // Disabled prompt rotation to prevent potential looping issues
        // setInterval(() => {
        //     this.updatePrompt();
        // }, 5000);
        console.log('📋 Prompt rotation disabled for debugging');
    }

    activateRainbowMode() {
        this.addToTerminal('🌈 RAINBOW MODE ACTIVATED!', 'rainbow');
        this.addToTerminal('╔══════════════════════════════════════╗', 'rainbow');
        this.addToTerminal('║  🌈 uDOS Rainbow Block Graphics! 🌈  ║', 'rainbow');
        this.addToTerminal('║  ▓▓▓▓ SPECTACULAR COLORS! ▓▓▓▓      ║', 'rainbow');
        this.addToTerminal('║  ░░░░ BLOCK MAGIC ENABLED ░░░░      ║', 'rainbow');
        this.addToTerminal('╚══════════════════════════════════════╝', 'rainbow');
        
        // Add rainbow styling
        document.body.classList.add('rainbow-mode');
        setTimeout(() => {
            document.body.classList.remove('rainbow-mode');
        }, 5000);
    }

    activateWhirlwindMode() {
        this.addToTerminal('🌪️ WHIRLWIND PROMPT SYSTEM ENGAGED!', 'whirlwind');
        this.addToTerminal('💫 Dynamic prompts now active...', 'whirlwind');
        
        // Rotate through different modes for demo
        const modes = ['DEV', 'GHOST', 'SORCERER', 'IMP', 'WIZARD'];
        let index = 0;
        
        const whirlwindInterval = setInterval(() => {
            this.currentMode = modes[index];
            this.updatePrompt();
            index = (index + 1) % modes.length;
        }, 1000);
        
        // Stop after 10 seconds
        setTimeout(() => {
            clearInterval(whirlwindInterval);
            this.currentMode = 'DEV';
            this.updatePrompt();
            this.addToTerminal('🎯 Whirlwind mode complete - back to DEV', 'success');
        }, 10000);
    }

    addToTerminal(text, type = 'output') {
        const terminal = document.getElementById('terminal-output');
        const line = document.createElement('div');
        
        line.className = `terminal-line ${type}`;
        line.textContent = text;
        
        terminal.appendChild(line);
        
        // Enhanced auto-scroll with smooth behavior
        this.smartAutoScroll(terminal);
        
        // Limit terminal history (keep last 1000 lines)
        this.limitTerminalHistory(terminal, 1000);
    }

    smartAutoScroll(terminal) {
        const isNearBottom = terminal.scrollTop + terminal.clientHeight >= terminal.scrollHeight - 50;
        
        if (isNearBottom) {
            // Show auto-scroll indicator
            terminal.classList.add('auto-scrolling');
            
            // Smooth scroll to bottom
            terminal.scrollTo({
                top: terminal.scrollHeight,
                behavior: 'smooth'
            });
            
            // Remove indicator after animation
            setTimeout(() => {
                terminal.classList.remove('auto-scrolling');
            }, 2000);
        }
    }

    limitTerminalHistory(terminal, maxLines) {
        const lines = terminal.children;
        if (lines.length > maxLines) {
            // Remove oldest lines (keep newest maxLines)
            const linesToRemove = lines.length - maxLines;
            for (let i = 0; i < linesToRemove; i++) {
                terminal.removeChild(lines[0]);
            }
        }
    }

    showTypingIndicator(show) {
        const indicator = document.querySelector('.status-indicator.typing') || 
                         this.createStatusIndicator('typing');
        
        if (show) {
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }

    createStatusIndicator(type) {
        const container = document.querySelector('.input-status') || 
                         this.createStatusContainer();
        
        const indicator = document.createElement('div');
        indicator.className = `status-indicator ${type}`;
        container.appendChild(indicator);
        return indicator;
    }

    createStatusContainer() {
        const container = document.createElement('div');
        container.className = 'input-status';
        
        const inputContainer = document.querySelector('.command-input-container');
        inputContainer.appendChild(container);
        
        // Add connection indicator
        const connectedIndicator = document.createElement('div');
        connectedIndicator.className = 'status-indicator connected';
        container.appendChild(connectedIndicator);
        
        return container;
    }

    showCommandSuggestions(input) {
        if (!input.trim()) {
            this.hideCommandSuggestions();
            return;
        }
        
        const suggestions = this.getCommandSuggestions(input.toLowerCase());
        if (suggestions.length === 0) {
            this.hideCommandSuggestions();
            return;
        }
        
        let suggestionsContainer = document.querySelector('.command-suggestions');
        if (!suggestionsContainer) {
            suggestionsContainer = this.createSuggestionsContainer();
        }
        
        suggestionsContainer.innerHTML = '';
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            if (index === 0) item.classList.add('selected');
            
            item.innerHTML = `
                <span class="command-name">${suggestion.name}</span>
                <span class="command-desc">${suggestion.description}</span>
            `;
            
            item.addEventListener('click', () => {
                document.getElementById('command-input').value = suggestion.name;
                this.hideCommandSuggestions();
                document.getElementById('command-input').focus();
            });
            
            suggestionsContainer.appendChild(item);
        });
        
        suggestionsContainer.classList.add('visible');
    }

    hideCommandSuggestions() {
        const container = document.querySelector('.command-suggestions');
        if (container) {
            container.classList.remove('visible');
        }
    }

    createSuggestionsContainer() {
        const container = document.createElement('div');
        container.className = 'command-suggestions';
        
        const inputContainer = document.querySelector('.command-input-container');
        inputContainer.appendChild(container);
        
        return container;
    }

    getCommandSuggestions(input) {
        const commands = [
            { name: 'help', description: 'Show available commands' },
            { name: 'status', description: 'System status information' },
            { name: 'ucode', description: 'Enter uCODE whirl prompt' },
            { name: 'clear', description: 'Clear terminal output' },
            { name: 'rainbow', description: 'Activate rainbow mode' },
            { name: 'whirlwind', description: 'Whirlwind prompt system' },
            { name: 'saa5050', description: 'Show teletext graphics' },
            { name: 'TREE generate', description: 'Generate repository structure' },
            { name: 'MEMORY list', description: 'List memory files' },
            { name: 'DASH live', description: 'Live system dashboard' },
            { name: 'LOG report', description: 'Generate log report' },
            { name: 'RENDER art gallery', description: 'ASCII art gallery' },
            { name: 'MISSION list', description: 'List active missions' },
            { name: 'DEV status', description: 'Development tools status' }
        ];
        
        return commands
            .filter(cmd => cmd.name.toLowerCase().includes(input))
            .slice(0, 6); // Limit to 6 suggestions
    }

    handleTabCompletion(input) {
        const currentValue = input.value.toLowerCase();
        const suggestions = this.getCommandSuggestions(currentValue);
        
        if (suggestions.length > 0) {
            input.value = suggestions[0].name;
            // Position cursor at end
            input.setSelectionRange(input.value.length, input.value.length);
        }
    }

    showCommandHistory() {
        if (this.commandHistory.length === 0) return;
        
        let historyContainer = document.querySelector('.command-history');
        if (!historyContainer) {
            historyContainer = this.createHistoryContainer();
        }
        
        historyContainer.innerHTML = '';
        this.commandHistory.slice(0, 10).forEach((cmd, index) => {
            const item = document.createElement('div');
            item.className = 'history-item';
            if (index === 0) item.classList.add('selected');
            
            item.textContent = cmd;
            item.addEventListener('click', () => {
                document.getElementById('command-input').value = cmd;
                this.hideCommandHistory();
                document.getElementById('command-input').focus();
            });
            
            historyContainer.appendChild(item);
        });
        
        historyContainer.classList.add('visible');
    }

    hideCommandHistory() {
        const container = document.querySelector('.command-history');
        if (container) {
            container.classList.remove('visible');
        }
    }

    createHistoryContainer() {
        const container = document.createElement('div');
        container.className = 'command-history';
        
        const inputContainer = document.querySelector('.command-input-container');
        inputContainer.appendChild(container);
        
        return container;
    }

    updateInputStatus(status) {
        // Update various status indicators based on input state
        console.log(`📝 Input status: ${status}`);
    }

    clearTerminal() {
        const terminal = document.getElementById('terminal-output');
        
        // Fade out effect
        terminal.style.transition = 'opacity 0.3s ease';
        terminal.style.opacity = '0.5';
        
        setTimeout(() => {
            terminal.innerHTML = '';
            terminal.style.opacity = '1';
        }, 300);
        
        console.log('🧹 Terminal cleared with animation');
    }

    changeFont(fontName) {
        console.log(`🎨 Changing font to: ${fontName}`);
        
        // Prevent rapid font changes
        if (this.fontChangeTimeout) {
            console.log('⚠️ Font change throttled - too rapid');
            return;
        }
        
        this.fontChangeTimeout = setTimeout(() => {
            this.fontChangeTimeout = null;
        }, 100);
        
        // Update debug indicator
        const debugElement = document.getElementById('font-debug');
        if (debugElement) {
            debugElement.textContent = `Font: ${fontName.toUpperCase()}`;
        }
        
        // Remove all font classes
        document.body.classList.remove(
            'font-teletext', 'font-teletext-square', 'font-teletext-wide', 
            'font-acorn', 'font-amiga', 'font-topaz', 'font-topaz-500', 'font-topaz-1200',
            'font-microknight', 'font-pot-noodle', 'font-mallard-neueue', 'font-mallard-blocky',
            'font-c64', 'font-c64-alt', 'font-petscii', 'font-terminal', 'font-terminal-retro', 
            'font-system', 'uDOS-font-mode7gx0', 'uDOS-font-mode7gx2', 'uDOS-font-mode7gx3', 
            'uDOS-font-mode7gx4', 'uDOS-font-teletext50', 'uDOS-font-amiga',
            'uDOS-font-topaz', 'uDOS-font-topaz500', 'uDOS-font-topaz1200',
            'uDOS-font-microknight', 'uDOS-font-pot-noodle', 'uDOS-font-c64', 
            'uDOS-font-petscii', 'uDOS-font-terminal', 'uDOS-font-system'
        );
        
        // Font mapping for commands
        const fontMap = {
            // Teletext fonts
            'teletext': 'font-teletext',
            'mode7': 'font-teletext',
            'mode7gx0': 'font-teletext-square',
            'mode7gx2': 'uDOS-font-mode7gx2', 
            'mode7gx3': 'font-teletext',
            'mode7gx4': 'font-teletext-wide',
            'teletext50': 'uDOS-font-teletext50',
            'square': 'font-teletext-square',
            'wide': 'font-teletext-wide',
            'acorn': 'font-acorn',
            
            // Amiga fonts
            'amiga': 'font-amiga',
            'topaz': 'font-topaz',
            'topaz500': 'font-topaz-500',
            'topaz1200': 'font-topaz-1200',
            'microknight': 'font-microknight',
            'pot-noodle': 'font-pot-noodle',
            'potnoodle': 'font-pot-noodle',
            'scene': 'font-pot-noodle',
            
            // FontStruct experimental fonts
            'mallard': 'font-mallard-neueue',
            'mallard-neueue': 'font-mallard-neueue',
            'neueue': 'font-mallard-neueue',
            'mallard-blocky': 'font-mallard-blocky',
            'blocky': 'font-mallard-blocky',
            'experimental': 'font-mallard-neueue',
            
            // C64 fonts
            'c64': 'font-c64',
            'commodore': 'font-c64',
            'petscii': 'font-petscii',
            'pet': 'font-petscii',
            
            // Terminal fonts
            'terminal': 'font-terminal',
            'modern': 'font-terminal',
            'retro': 'font-terminal-retro',
            
            // System fonts
            'system': 'font-system',
            'default': 'font-system'
        };
        
        const fontClass = fontMap[fontName.toLowerCase()];
        
        if (fontClass) {
            this.currentFont = fontName;
            document.body.classList.add(fontClass);
            console.log(`✅ Applied font class: ${fontClass}`);
            console.log(`📋 Current body classes:`, Array.from(document.body.classList));
            
            // Update debug indicator with success
            if (debugElement) {
                debugElement.textContent = `Font: ${fontName.toUpperCase()} (${fontClass})`;
                debugElement.style.color = '#00ff00';
            }
            
            this.addToTerminal(`🎨 Font changed to ${fontName} (${fontClass})`, 'success');
            
            // Force a style recalculation by requesting computed style
            const computedStyle = window.getComputedStyle(document.body);
            console.log(`💻 Computed font-family:`, computedStyle.fontFamily);
            
            // Notify server of font change
            if (this.socket && this.socket.connected) {
                this.socket.emit('font_change', { font: fontName });
            }
        } else {
            console.log(`❌ Unknown font: ${fontName}`);
            
            // Update debug indicator with error
            if (debugElement) {
                debugElement.textContent = `Font: ${fontName.toUpperCase()} (ERROR)`;
                debugElement.style.color = '#ff0000';
            }
            this.addToTerminal(`❌ Unknown font: ${fontName}`, 'error');
            this.addToTerminal(`📝 Available fonts:`, 'info');
            this.addToTerminal(`📺 Teletext: teletext, mode7, mode7gx0-4, teletext50, square, wide, acorn`, 'info');
            this.addToTerminal(`🖥️  Amiga: amiga, topaz, topaz500, topaz1200, microknight, pot-noodle, scene`, 'info');
            this.addToTerminal(`🧪 Experimental: mallard, mallard-neueue, mallard-blocky, blocky, experimental`, 'info');
            this.addToTerminal(`🕹️  C64: c64, commodore, petscii, pet`, 'info');
            this.addToTerminal(`💻 Terminal: terminal, modern, retro`, 'info');
            this.addToTerminal(`🖥️  System: system, default`, 'info');
        }
    }

    changePalette(paletteName) {
        console.log(`🎨 Changing palette to: ${paletteName}`);
        
        // Remove all theme classes
        document.body.classList.remove(
            'theme-teletext', 'theme-retro', 'theme-professional', 
            'theme-light', 'theme-dark', 'theme-rainbow'
        );
        
        // Palette mapping for commands
        const paletteMap = {
            'teletext': 'theme-teletext',
            'mode7': 'theme-teletext',
            'classic': 'theme-teletext',
            'bbc': 'theme-teletext',
            'retro': 'theme-retro', 
            'professional': 'theme-retro',
            'muted': 'theme-retro',
            'light': 'theme-light',
            'dark': 'theme-dark',
            'rainbow': 'theme-rainbow'
        };
        
        const themeClass = paletteMap[paletteName.toLowerCase()];
        
        if (themeClass) {
            this.currentTheme = paletteName;
            document.body.classList.add(themeClass);
            console.log(`✅ Applied palette class: ${themeClass}`);
            
            this.addToTerminal(`🌈 Color palette changed to ${paletteName} (${themeClass})`, 'success');
            
            // Notify server of palette change
            if (this.socket && this.socket.connected) {
                this.socket.emit('palette_change', { palette: paletteName });
            }
        } else {
            console.log(`❌ Unknown palette: ${paletteName}`);
            this.addToTerminal(`❌ Unknown palette: ${paletteName}`, 'error');
            this.addToTerminal(`🎨 Available palettes: teletext, retro, light, dark, rainbow`, 'info');
        }
    }

    showSAA5050Graphics() {
        this.addToTerminal('📺 SAA5050 Teletext Block Graphics (2×3 blocks):', 'info');
        this.addToTerminal('', 'output');
        
        // SAA5050 2x3 block graphics characters
        const saa5050Blocks = [
            '   🬀 🬁 🬂 🬃 🬄 🬅 🬆 🬇',
            '🬈 🬉 🬊 🬋 🬌 🬍 🬎 🬏',
            '🬐 🬑 🬒 🬓 ▌ 🬔 🬕 🬖',
            '🬗 🬘 🬙 🬚 🬛 🬜 🬝 🬞',
            '🬟 🬠 🬡 🬢 🬣 🬤 🬥 🬦',
            '🬧 ▐ 🬨 🬩 🬪 🬫 🬬 🬭',
            '🬮 🬯 🬰 🬱 🬲 🬳 🬴 🬵',
            '🬶 🬷 🬸 🬹 🬺 🬻 █',
        ];
        
        saa5050Blocks.forEach(line => {
            this.addToTerminal(line, 'output');
        });
        
        this.addToTerminal('', 'output');
        this.addToTerminal('📐 Each character: 12×20 pixels (6×6, 6×8, 6×6 blocks)', 'info');
        this.addToTerminal('🎨 Original Mullard SAA5050 character generator blocks', 'info');
        this.addToTerminal('📺 Used in BBC Micro Mode 7, Teletext, and Viewdata', 'info');
    }

    resetFont() {
        this.currentFont = 'mode7gx3';  // Reset to MODE7GX3 as the default authentic teletext font
        this.changeFont(this.currentFont);
    }

    changeTheme(themeName) {
        // Remove all theme classes
        document.body.classList.remove('theme-dark', 'theme-light', 'theme-professional', 'theme-rainbow');
        
        // Add new theme class
        document.body.classList.add(`theme-${themeName}`);
        this.currentTheme = themeName;
        
        // Update theme buttons
        document.querySelectorAll('.theme-btn').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.getElementById(`theme-${themeName}`);
        if (activeBtn) activeBtn.classList.add('active');
        
        this.addToTerminal(`🎨 Theme changed to ${themeName}`, 'success');
    }

    updateSystemStatus(data) {
        // Update various status displays
        if (data.clients !== undefined) {
            const clientsElement = document.getElementById('clients');
            if (clientsElement) clientsElement.textContent = data.clients;
        }
        
        if (data.modules !== undefined) {
            const modulesElement = document.getElementById('modules');
            if (modulesElement) modulesElement.textContent = data.modules;
        }
        
        if (data.mode !== undefined) {
            const modeElement = document.getElementById('mode');
            if (modeElement) modeElement.textContent = data.mode;
        }
    }

    // uCODE WHIRL PROMPT METHODS
    enterUCodeMode() {
        this.ucodeMode = true;
        this.addToTerminal('🌪️ ═══════════════════════════════════════════════', 'info');
        this.addToTerminal('🌪️ uCODE WHIRL PROMPT v1.3 - ACTIVATED!', 'success');
        this.addToTerminal('🌪️ Universal Code Interpreter & Script Engine', 'info');
        this.addToTerminal('🌪️ ═══════════════════════════════════════════════', 'info');
        this.addToTerminal('📺 BBC Mode 7 Interface | Visual Basic Syntax', 'info');
        this.addToTerminal('', 'output');
        this.addToTerminal('Available uCODE modules:', 'info');
        this.addToTerminal('  MEMORY - Memory file management', 'output');
        this.addToTerminal('  MISSION - Task tracking system', 'output');
        this.addToTerminal('  PACKAGE - Package management', 'output');
        this.addToTerminal('  LOG - Advanced logging system', 'output');
        this.addToTerminal('  DEV - Development tools (wizard)', 'output');
        this.addToTerminal('  RENDER - Visual rendering & ASCII art', 'output');
        this.addToTerminal('  DASH - Live dashboard system', 'output');
        this.addToTerminal('  PANEL - Interactive control panels', 'output');
        this.addToTerminal('  TREE - Structure visualization', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('Commands: help, status, exit', 'info');
        this.addToTerminal('🌪️ uCODE ready - enter Visual Basic commands...', 'success');
        
        // Update prompt display
        this.updatePrompt();
    }

    exitUCodeMode() {
        this.ucodeMode = false;
        this.addToTerminal('🌪️ Exiting uCODE whirl prompt...', 'info');
        this.addToTerminal('✅ Returned to uDOS main system', 'success');
        this.updatePrompt();
    }

    handleUCodeCommand(command) {
        const cmd = command.trim();
        const parts = cmd.split(' ');
        const module = parts[0].toUpperCase();
        const action = parts[1] ? parts[1].toLowerCase() : 'help';
        
        // Handle special commands
        if (cmd.toLowerCase() === 'exit' || cmd.toLowerCase() === 'quit') {
            this.exitUCodeMode();
            return;
        }
        
        if (cmd.toLowerCase() === 'help') {
            this.showUCodeHelp();
            return;
        }
        
        if (cmd.toLowerCase() === 'status') {
            this.showUCodeStatus();
            return;
        }
        
        if (cmd.toLowerCase() === 'list') {
            this.addToTerminal('Available uCODE modules:', 'info');
            this.ucodeCommands.forEach(mod => {
                this.addToTerminal(`  ${mod}`, 'output');
            });
            return;
        }
        
        // Handle module commands
        if (this.ucodeCommands.includes(module)) {
            this.executeUCodeModule(module, action, parts.slice(2));
        } else {
            this.addToTerminal(`❌ Unknown uCODE module: ${module}`, 'error');
            this.addToTerminal('💡 Type "help" for available commands', 'info');
        }
    }

    showUCodeHelp() {
        this.addToTerminal('🌪️ uCODE WHIRL PROMPT HELP', 'info');
        this.addToTerminal('═══════════════════════════', 'info');
        this.addToTerminal('', 'output');
        this.addToTerminal('System Commands:', 'info');
        this.addToTerminal('  help                    - Show this help', 'output');
        this.addToTerminal('  status                  - System status', 'output');
        this.addToTerminal('  list                    - List modules', 'output');
        this.addToTerminal('  exit                    - Exit uCODE mode', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('Module Commands (Visual Basic syntax):', 'info');
        this.addToTerminal('  MEMORY list             - List memory files', 'output');
        this.addToTerminal('  MEMORY create "file"    - Create memory file', 'output');
        this.addToTerminal('  MISSION list            - List missions', 'output');
        this.addToTerminal('  MISSION create "title"  - Create mission', 'output');
        this.addToTerminal('  RENDER art gallery      - ASCII art gallery', 'output');
        this.addToTerminal('  DASH live               - Live dashboard', 'output');
        this.addToTerminal('  DEV test                - Run tests', 'output');
        this.addToTerminal('  LOG report              - Generate report', 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('🌪️ Visual Basic style syntax supported', 'success');
    }

    showUCodeStatus() {
        this.addToTerminal('🌪️ uCODE SYSTEM STATUS', 'info');
        this.addToTerminal('═══════════════════════', 'info');
        this.addToTerminal('', 'output');
        this.addToTerminal(`Mode: uCODE Whirl Prompt v1.3`, 'output');
        this.addToTerminal(`Interface: BBC Mode 7 Teletext`, 'output');
        this.addToTerminal(`Font: ${this.currentFont.toUpperCase()}`, 'output');
        this.addToTerminal(`Theme: ${this.currentTheme}`, 'output');
        this.addToTerminal(`Modules: ${this.ucodeCommands.length} loaded`, 'output');
        this.addToTerminal(`Commands in history: ${this.commandHistory.length}`, 'output');
        this.addToTerminal(`Connection: ${this.socket && this.socket.connected ? 'CONNECTED' : 'OFFLINE'}`, 'output');
        this.addToTerminal('', 'output');
        this.addToTerminal('✅ All systems operational', 'success');
    }

    executeUCodeModule(module, action, args) {
        this.addToTerminal(`🔄 Executing ${module}.${action}...`, 'info');
        
        switch(module) {
            case 'MEMORY':
                this.handleMemoryCommand(action, args);
                break;
            case 'MISSION':
                this.handleMissionCommand(action, args);
                break;
            case 'RENDER':
                this.handleRenderCommand(action, args);
                break;
            case 'DASH':
                this.handleDashCommand(action, args);
                break;
            case 'DEV':
                this.handleDevCommand(action, args);
                break;
            case 'LOG':
                this.handleLogCommand(action, args);
                break;
            case 'PACKAGE':
                this.handlePackageCommand(action, args);
                break;
            case 'PANEL':
                this.handlePanelCommand(action, args);
                break;
            case 'TREE':
                this.handleTreeCommand(action, args);
                break;
            default:
                this.addToTerminal(`❌ Module ${module} not implemented`, 'error');
        }
    }

    handleMemoryCommand(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('📁 Memory Files:', 'info');
                this.addToTerminal('  uLOG-20250821-1B40FF26.md', 'output');
                this.addToTerminal('  system-config.json', 'output');
                this.addToTerminal('  user-profile.dat', 'output');
                this.addToTerminal('  session-history.log', 'output');
                break;
            case 'create':
                const filename = args[0] || 'untitled.md';
                this.addToTerminal(`✅ Created memory file: ${filename}`, 'success');
                break;
            case 'search':
                const term = args[0] || '';
                this.addToTerminal(`🔍 Searching for: ${term}`, 'info');
                this.addToTerminal('Found 3 matches in memory files', 'output');
                break;
            default:
                this.addToTerminal('MEMORY commands: list, create, search', 'info');
        }
    }

    handleMissionCommand(action, args) {
        switch(action) {
            case 'list':
                this.addToTerminal('🎯 Active Missions:', 'info');
                this.addToTerminal('  [001] BBC Mode 7 Interface - COMPLETE', 'output');
                this.addToTerminal('  [002] uCODE Whirl Prompt - IN PROGRESS', 'output');
                this.addToTerminal('  [003] Dashboard Integration - PENDING', 'output');
                break;
            case 'create':
                const title = args.join(' ') || 'New Mission';
                this.addToTerminal(`✅ Created mission: ${title}`, 'success');
                break;
            default:
                this.addToTerminal('MISSION commands: list, create, track, complete', 'info');
        }
    }

    handleRenderCommand(action, args) {
        switch(action) {
            case 'art':
                if (args[0] === 'gallery') {
                    this.addToTerminal('🎨 ASCII Art Gallery:', 'info');
                    this.addToTerminal('', 'output');
                    this.addToTerminal('  ████ uDOS ████', 'output');
                    this.addToTerminal('  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄', 'output');
                    this.addToTerminal('  █ BBC MODE 7 █', 'output');
                    this.addToTerminal('  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀', 'output');
                } else {
                    this.addToTerminal('🎨 Available art: gallery, dragon, logo', 'info');
                }
                break;
            case 'chart':
                this.addToTerminal('📊 Generating chart...', 'info');
                this.addToTerminal('█████████░ 90% Complete', 'output');
                break;
            default:
                this.addToTerminal('RENDER commands: art, chart, ui, animation', 'info');
        }
    }

    handleDashCommand(action, args) {
        switch(action) {
            case 'live':
                this.addToTerminal('📊 LIVE DASHBOARD', 'info');
                this.addToTerminal('═══════════════', 'info');
                this.addToTerminal('System Load: ████░░░░░░ 40%', 'output');
                this.addToTerminal('Memory Usage: ██░░░░░░░░ 20%', 'output');
                this.addToTerminal('uCODE Modules: 9/9 loaded', 'output');
                this.addToTerminal('Active Sessions: 1', 'output');
                break;
            default:
                this.addToTerminal('DASH commands: live, architecture, performance', 'info');
        }
    }

    handleDevCommand(action, args) {
        this.addToTerminal('🧙‍♂️ DEV commands require wizard mode', 'warning');
        this.addToTerminal('Available in development environment', 'info');
    }

    handleLogCommand(action, args) {
        switch(action) {
            case 'report':
                this.addToTerminal('📋 LOG REPORT - Last 24 Hours', 'info');
                this.addToTerminal('Commands executed: 47', 'output');
                this.addToTerminal('Errors: 0', 'output');
                this.addToTerminal('uCODE sessions: 3', 'output');
                break;
            default:
                this.addToTerminal('LOG commands: report, analyze, export', 'info');
        }
    }

    handlePackageCommand(action, args) {
        this.addToTerminal('📦 Package management available', 'info');
        this.addToTerminal('Commands: install, remove, list, search', 'info');
    }

    handlePanelCommand(action, args) {
        this.addToTerminal('🎛️ Control panels available', 'info');
        this.addToTerminal('Commands: system, user, network', 'info');
    }

    handleTreeCommand(action, args) {
        switch(action) {
            case 'generate':
                this.addToTerminal('🌳 Repository Structure:', 'info');
                this.addToTerminal('uDOS/', 'output');
                this.addToTerminal('├── uCORE/', 'output');
                this.addToTerminal('├── uSCRIPT/', 'output');
                this.addToTerminal('├── uMEMORY/', 'output');
                this.addToTerminal('└── extensions/', 'output');
                break;
            default:
                this.addToTerminal('TREE commands: generate, analyze, visualize', 'info');
        }
    }

    updatePrompt() {
        const promptElement = document.getElementById('dynamic-prompt');
        if (this.ucodeMode) {
            promptElement.textContent = '🌪️ uCODE>';
            promptElement.style.color = '#00ff00';
        } else {
            promptElement.textContent = `${this.promptEmojis[this.currentMode]} uDOS:${this.currentMode} $`;
            promptElement.style.color = '#ffffff';
        }
    }
}

// Global functions
function toggleAssist() {
    const assistPanel = document.getElementById('assist-panel');
    assistPanel.classList.toggle('active');
}

function setTheme(themeName) {
    if (window.udos) {
        window.udos.changeTheme(themeName);
    }
}

// Display size control functions
function setDisplaySize(size) {
    console.log(`🖥️ Setting display size to: ${size}`);
    
    // Update active button
    document.querySelectorAll('.size-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Apply size to container
    const container = document.querySelector('.mode7-screen');
    const [width, height] = size.split('x').map(Number);
    
    container.style.width = `${width}px`;
    container.style.height = `${height}px`;
    container.style.maxWidth = `${width}px`;
    container.style.maxHeight = `${height}px`;
    
    // Adjust font size based on screen size
    let fontSize;
    if (width <= 320) {
        fontSize = '14px';
    } else if (width <= 640) {
        fontSize = '16px';
    } else if (width <= 800) {
        fontSize = '18px';
    } else {
        fontSize = '20px';
    }
    
    container.style.fontSize = fontSize;
    
    // Update terminal if exists
    if (window.udos) {
        window.udos.addToTerminal(`📺 Display size changed to ${size}`, 'success');
        window.udos.addToTerminal(`🎨 Font size adjusted to ${fontSize}`, 'info');
    }
    
    // Force layout recalculation
    container.offsetHeight;
}

// Cycle through display sizes with button
function cycleDisplaySize() {
    const sizeOrder = ['tiny', 'small', 'normal', 'medium', 'large', 'huge', 'giant'];
    const currentIndex = sizeOrder.indexOf(currentDisplaySize);
    const nextIndex = (currentIndex + 1) % sizeOrder.length;
    const newSize = sizeOrder[nextIndex];
    
    currentDisplaySize = newSize;
    const sizeConfig = displaySizes[newSize];
    
    console.log(`📏 Cycling display size to: ${newSize} (${sizeConfig.size})`);
    
    // Apply the new size to the terminal container
    const terminalOutput = document.getElementById('terminal-output');
    const commandInput = document.getElementById('command-input');
    
    if (terminalOutput) {
        terminalOutput.style.fontSize = sizeConfig.size;
        terminalOutput.style.lineHeight = sizeConfig.lineHeight;
    }
    
    if (commandInput) {
        commandInput.style.fontSize = sizeConfig.size;
        commandInput.style.lineHeight = sizeConfig.lineHeight;
    }
    
    // Update CSS custom property for consistency
    document.documentElement.style.setProperty('--terminal-font-size', sizeConfig.size);
    document.documentElement.style.setProperty('--terminal-line-height', sizeConfig.lineHeight);
    
    // Update terminal if exists
    if (window.udos) {
        window.udos.addToTerminal(`📏 Display size: ${sizeConfig.description}`, 'success');
    }
    
    console.log(`✅ Display size applied: ${sizeConfig.description}`);
}

// Quick command execution
function executeQuickCommand(command) {
    console.log(`⚡ Executing quick command: ${command}`);
    
    if (window.udos) {
        // Add visual feedback
        event.target.style.transform = 'scale(0.9)';
        setTimeout(() => {
            event.target.style.transform = '';
        }, 100);
        
        // Execute the command
        if (command === 'clear') {
            window.udos.clearTerminal();
        } else {
            // If in uCODE mode, handle uCODE commands
            if (window.udos.ucodeMode) {
                window.udos.handleUCodeCommand(command);
            } else {
                // Execute as regular command
                window.udos.executeCommand(command);
            }
        }
    }
}

// Keyboard shortcuts for quick commands
document.addEventListener('keydown', (e) => {
    // Only handle shortcuts when not typing in input field
    if (e.target.tagName.toLowerCase() !== 'input') {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key.toLowerCase()) {
                case 't':
                    e.preventDefault();
                    executeQuickCommand('TREE generate');
                    break;
                case 'm':
                    e.preventDefault();
                    executeQuickCommand('MEMORY list');
                    break;
                case 'd':
                    e.preventDefault();
                    executeQuickCommand('DASH live');
                    break;
                case 'l':
                    e.preventDefault();
                    executeQuickCommand('LOG report');
                    break;
                case 'k':
                    e.preventDefault();
                    executeQuickCommand('clear');
                    break;
            }
        }
        
        // Function key shortcuts for display sizes
        switch(e.key) {
            case 'F1':
                e.preventDefault();
                setDisplaySize('320x200');
                break;
            case 'F2':
                e.preventDefault();
                setDisplaySize('640x400');
                break;
            case 'F3':
                e.preventDefault();
                setDisplaySize('640x500');
                break;
            case 'F4':
                e.preventDefault();
                setDisplaySize('800x600');
                break;
            case 'F5':
                e.preventDefault();
                setDisplaySize('1024x768');
                break;
        }
    }
});

// Initialize the interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.udos = new UDOSInterface();
    
    // Initialize hybrid font system
    applyFontMode();
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('fontPreviewModal');
        if (modal && event.target === modal) {
            closeFontPreview();
        }
    });
    
    // Keyboard shortcuts for modal
    document.addEventListener('keydown', function(event) {
        const modal = document.getElementById('fontPreviewModal');
        if (modal && modal.style.display === 'flex') {
            if (event.key === 'Escape') {
                closeFontPreview();
            } else if (event.key === 'Enter' && event.ctrlKey) {
                applyPreviewFont();
            }
        }
    });
    
    // Add some initial commands to help users
    setTimeout(() => {
        window.udos.addToTerminal('📺 uDOS Professional Interface - Enhanced Font Management', 'system');
        window.udos.addToTerminal('🔧 Font Modes: Hybrid (1:1 text + 1:1.3 blocks), Monospace, Retro, System', 'system');
        window.udos.addToTerminal('🌟 Try: help, blocks, font preview, or use the font switcher above', 'system');
        
        // Initialize hybrid font system
        applyFontMode();
    }, 1000);
});