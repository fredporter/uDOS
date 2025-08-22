// uDOS Universal Code Interface - Lean & Mean Edition
// Rebuilt for reliability, performance, and authentic retro computing experience

// =============================================================================
// CORE CONFIGURATION & GLOBALS
// =============================================================================

// Application state
let udosApp = {
    isUCodeMode: false,
    currentFont: 'MODE7GX0',
    currentTheme: 'dark',
    currentDisplaySize: 'medium',
    commandHistory: [],
    historyIndex: -1,
    socket: null,
    // uMEMORY System Integration
    memoryPalettes: null,
    memoryFonts: null,
    systemConfig: null,
    startupGraphicsShown: false
};

// uDOS Color Palette (Professional BBC/Retro Computing Colors)
const udosColors = {
    // Primary Theme Colors (Dark Mode)
    dark: {
        background: '#000000',      // True black background
        foreground: '#00ff00',      // Classic green text
        accent: '#ffff00',          // Bright yellow for highlights
        error: '#ff0000',           // Pure red for errors
        warning: '#ffa500',         // Orange for warnings
        info: '#00ffff',            // Cyan for information
        success: '#00ff00',         // Green for success
        secondary: '#808080'        // Grey for secondary text
    },
    // Light Theme Colors
    light: {
        background: '#ffffff',      // White background
        foreground: '#000000',      // Black text
        accent: '#0066cc',          // Blue for highlights
        error: '#cc0000',           // Dark red for errors
        warning: '#cc6600',         // Dark orange for warnings
        info: '#006699',            // Dark cyan for information
        success: '#006600',         // Dark green for success
        secondary: '#666666'        // Dark grey for secondary text
    },
    // uMEMORY Professional Palette Integration
    udos_final: {
        background: '#000000',      // Pure Black
        foreground: '#FFFFFF',      // Pure White
        accent: '#4DA378',          // Shiny Shamrock (primary)
        secondary: '#4B5798',       // Liberty (secondary)
        highlight: '#D45979',       // Cinnamon Satin (accent)
        warning: '#E8A05D',         // Indian Yellow (warning)
        special: '#F8DC93',         // Caramel (highlight)
        purple: '#A25FAD',          // Purple Plum (special)
        error: '#D45979',           // Use cinnamon for errors
        info: '#4DA378',            // Use green for info
        success: '#4DA378'          // Use green for success
    }
};

// uDOS Display Size Standards (Authentic Retro Computing)
const udosDisplaySizes = {
    tiny: {
        fontSize: '8px',
        lineHeight: '8px',
        description: 'C64 PETSCII (8×8)',
        chars: { width: 40, height: 25 }
    },
    small: {
        fontSize: '10px',
        lineHeight: '10px',
        description: 'BBC Mode 7 (8×10)',
        chars: { width: 40, height: 25 }
    },
    medium: {
        fontSize: '12px',
        lineHeight: '14px',
        description: 'Amiga Workbench (8×12)',
        chars: { width: 80, height: 25 }
    },
    large: {
        fontSize: '14px',
        lineHeight: '16px',
        description: 'VT100 Terminal (7×14)',
        chars: { width: 80, height: 24 }
    },
    huge: {
        fontSize: '16px',
        lineHeight: '18px',
        description: 'Modern Terminal (8×16)',
        chars: { width: 120, height: 40 }
    },
    giant: {
        fontSize: '20px',
        lineHeight: '22px',
        description: 'Presentation Mode (10×20)',
        chars: { width: 80, height: 30 }
    }
};

// uDOS Font System (Authentic Retro Computing Fonts + uMEMORY Integration)
const udosFonts = {
    // BBC Micro / Teletext Fonts (from uMEMORY/system/fonts)
    'MODE7GX0': {
        family: 'MODE7GX0, VT323, monospace',
        className: 'font-mode7gx0',
        description: '📺 BBC Mode 7 Square (uMEMORY)',
        aspectRatio: 1.0,
        size: '18px',
        lineHeight: '18px',
        file: 'MODE7GX0.TTF',
        authentic: true,
        default: true
    },

    // System Fonts (built-in macOS/system fonts)
    'MONACO': {
        family: 'Monaco, monospace',
        className: 'font-monaco',
        description: '🍎 Monaco (System Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'MENLO': {
        family: 'Menlo, monospace',
        className: 'font-menlo',
        description: '🍎 Menlo (System Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'SF_MONO': {
        family: 'SF Mono, monospace',
        className: 'font-sf-mono',
        description: '🍎 SF Mono (System Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'COURIER_NEW': {
        family: 'Courier New, monospace',
        className: 'font-courier-new',
        description: '📰 Courier New (System Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'CONSOLAS': {
        family: 'Consolas, monospace',
        className: 'font-consolas',
        description: '🪟 Consolas (System Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'FIRA_CODE': {
        family: 'Fira Code, monospace',
        className: 'font-fira-code',
        description: '� Fira Code (Programming Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'JETBRAINS_MONO': {
        family: 'JetBrains Mono, monospace',
        className: 'font-jetbrains-mono',
        description: '✈️ JetBrains Mono (Programming Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'SOURCE_CODE_PRO': {
        family: 'Source Code Pro, monospace',
        className: 'font-source-code-pro',
        description: '📟 Source Code Pro (Programming Font)',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },

    // Terminal/Fallback Fonts
    'TERMINAL': {
        family: 'Topaz A1200, Monaco, monospace',
        className: 'font-topaz-a1200',
        description: '🖥️ Amiga 1200 Topaz (uMEMORY)',
        aspectRatio: 1.1,
        size: '16px',
        lineHeight: '18px',
        file: 'topaz_a1200.ttf',
        authentic: true,
        platform: 'amiga'
    },
    'MICROKNIGHT': {
        family: 'MicroKnight, Monaco, monospace',
        className: 'font-microknight',
        description: '�️ C64 MicroKnight (uMEMORY)',
        aspectRatio: 1.2,
        size: '14px',
        lineHeight: '16px',
        file: 'microknight.ttf',
        authentic: false,
        platform: 'c64'
    },

    // Terminal/Fallback Fonts
    'TERMINAL': {
        family: 'Monaco, Menlo, monospace',
        className: 'font-terminal',
        description: '💻 Terminal Default',
        aspectRatio: 1.0,
        size: '14px',
        lineHeight: '16px',
        system: true
    },
    'VT100': {
        family: 'Courier New, monospace',
        className: 'font-vt100',
        description: '� VT100 Terminal',
        aspectRatio: 1.0,
        size: '12px',
        lineHeight: '14px',
        system: true
    }
};

// uCODE Module System
const ucodeModules = {
    MEMORY: {
        description: 'Memory file management system',
        commands: ['list', 'create', 'search', 'delete', 'backup', 'stats']
    },
    MISSION: {
        description: 'Task tracking and mission management',
        commands: ['list', 'create', 'complete', 'archive', 'report']
    },
    RENDER: {
        description: 'Visual rendering and ASCII art system',
        commands: ['art', 'chart', 'ui', 'animation', 'export']
    },
    DEV: {
        description: 'Development tools and utilities',
        commands: ['test', 'build', 'debug', 'profile', 'docs']
    },
    LOG: {
        description: 'System logging and monitoring',
        commands: ['report', 'analyze', 'watch', 'archive', 'stats']
    }
};

// System Module Handlers
const systemModules = {
    uCORE: 'Core system management',
    uSCRIPT: 'Script automation system',
    uSERVER: 'Web services and APIs',
    uMEMORY: 'Memory and storage system',
    WIZARD: 'Development wizard tools',
    SORCERER: 'Advanced system administration',
    IMP: 'Script execution engine',
    GHOST: 'Background services',
    DRONE: 'Automation tasks',
    TOMB: 'Archive and backup system'
};

// =============================================================================
// CORE FUNCTIONS - FONT MANAGEMENT
// =============================================================================

function cycleFont() {
    const fontNames = Object.keys(udosFonts);
    const currentIndex = fontNames.indexOf(udosApp.currentFont);
    const nextIndex = (currentIndex + 1) % fontNames.length;
    const newFont = fontNames[nextIndex];

    changeFont(newFont);
    addToTerminal(`🔤 Font changed to: ${newFont} - ${udosFonts[newFont].description}`, 'info');

    // Update status bar if element exists
    const fontStat = document.getElementById('font-stat');
    if (fontStat) {
        fontStat.textContent = newFont;
    }
}

function changeFont(fontName) {
    console.log(`🔤 Changing font to: ${fontName}`);

    if (!udosFonts[fontName]) {
        addToTerminal(`❌ Font not found: ${fontName}`, 'error');
        addToTerminal(`Available fonts: ${Object.keys(udosFonts).join(', ')}`, 'info');
        return;
    }

    udosApp.currentFont = fontName;
    const fontConfig = udosFonts[fontName];

    // Apply font to all text elements
    document.documentElement.style.setProperty('--current-font-family', fontConfig.family);

    // Update body class for font-specific styles
    document.body.className = document.body.className.replace(/font-\w+/g, '');
    document.body.classList.add(fontConfig.className);

    // Apply to terminal specifically
    const terminal = document.getElementById('terminal-output');
    if (terminal) {
        terminal.style.fontFamily = fontConfig.family;
    }

    console.log(`✅ Font applied: ${fontName}`);
}

// =============================================================================
// CORE FUNCTIONS - THEME MANAGEMENT
// =============================================================================

function toggleTheme() {
    udosApp.currentTheme = udosApp.currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(udosApp.currentTheme);
    addToTerminal(`🌓 Theme changed to: ${udosApp.currentTheme}`, 'info');

    // Update status bar if element exists
    const themeStat = document.getElementById('theme-stat');
    if (themeStat) {
        themeStat.textContent = udosApp.currentTheme.toUpperCase();
    }
}

function applyTheme(themeName) {
    console.log(`🌓 Applying theme: ${themeName}`);

    const colors = udosColors[themeName];
    if (!colors) {
        console.error(`❌ Theme not found: ${themeName}`);
        return;
    }

    // Apply CSS custom properties
    const root = document.documentElement;
    root.style.setProperty('--bg-primary', colors.background);
    root.style.setProperty('--text-primary', colors.foreground);
    root.style.setProperty('--text-accent', colors.accent);
    root.style.setProperty('--text-error', colors.error);
    root.style.setProperty('--text-warning', colors.warning);
    root.style.setProperty('--text-info', colors.info);
    root.style.setProperty('--text-success', colors.success);
    root.style.setProperty('--text-secondary', colors.secondary);

    // Update body class
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${themeName}`);

    console.log(`✅ Theme applied: ${themeName}`);
}

// =============================================================================
// CORE FUNCTIONS - DISPLAY SIZE MANAGEMENT
// =============================================================================

function cycleDisplaySize() {
    const sizeNames = Object.keys(udosDisplaySizes);
    const currentIndex = sizeNames.indexOf(udosApp.currentDisplaySize);
    const nextIndex = (currentIndex + 1) % sizeNames.length;
    const newSize = sizeNames[nextIndex];

    changeDisplaySize(newSize);
    addToTerminal(`📐 Display size changed to: ${newSize} - ${udosDisplaySizes[newSize].description}`, 'info');

    // Update status bar if element exists
    const displayStat = document.getElementById('display-mode-stat');
    if (displayStat) {
        displayStat.textContent = newSize.toUpperCase();
    }
}

function changeDisplaySize(sizeName) {
    console.log(`📐 Changing display size to: ${sizeName}`);

    if (!udosDisplaySizes[sizeName]) {
        addToTerminal(`❌ Display size not found: ${sizeName}`, 'error');
        addToTerminal(`Available sizes: ${Object.keys(udosDisplaySizes).join(', ')}`, 'info');
        return;
    }

    udosApp.currentDisplaySize = sizeName;
    const sizeConfig = udosDisplaySizes[sizeName];

    // Apply font size and line height
    document.documentElement.style.setProperty('--current-font-size', sizeConfig.fontSize);
    document.documentElement.style.setProperty('--current-line-height', sizeConfig.lineHeight);

    // Apply to terminal
    const terminal = document.getElementById('terminal-output');
    if (terminal) {
        terminal.style.fontSize = sizeConfig.fontSize;
        terminal.style.lineHeight = sizeConfig.lineHeight;
    }

    // Update body class for size-specific styles
    document.body.className = document.body.className.replace(/size-\w+/g, '');
    document.body.classList.add(`size-${sizeName}`);

    console.log(`✅ Display size applied: ${sizeName}`);
}

// =============================================================================
// CORE FUNCTIONS - TERMINAL MANAGEMENT
// =============================================================================

function addToTerminal(text, type = 'output') {
    const terminal = document.getElementById('terminal-output');
    if (!terminal) return;

    const line = document.createElement('div');
    line.className = `terminal-line terminal-${type}`;

    // Add appropriate styling based on type
    switch (type) {
        case 'info':
            line.style.color = 'var(--text-info)';
            break;
        case 'error':
            line.style.color = 'var(--text-error)';
            break;
        case 'warning':
            line.style.color = 'var(--text-warning)';
            break;
        case 'success':
            line.style.color = 'var(--text-success)';
            break;
        case 'accent':
            line.style.color = 'var(--text-accent)';
            break;
        default:
            line.style.color = 'var(--text-primary)';
    }

    line.textContent = text;
    terminal.appendChild(line);

    // Auto-scroll to bottom
    terminal.scrollTop = terminal.scrollHeight;

    // Limit terminal history (keep last 1000 lines)
    while (terminal.children.length > 1000) {
        terminal.removeChild(terminal.firstChild);
    }
}

function clearTerminal() {
    const terminal = document.getElementById('terminal-output');
    if (terminal) {
        terminal.innerHTML = '';
        addToTerminal('🧹 Terminal cleared', 'info');
    }
}

// =============================================================================
// CORE FUNCTIONS - COMMAND SYSTEM
// =============================================================================

function executeCommand(command) {
    const cmd = command.trim();
    if (!cmd) return;

    // Add command to history
    udosApp.commandHistory.push(cmd);
    udosApp.historyIndex = udosApp.commandHistory.length;

    // Display command in terminal
    addToTerminal(`> ${cmd}`, 'accent');

    // Parse command
    const parts = cmd.split(' ');
    const mainCommand = parts[0].toUpperCase();
    const args = parts.slice(1);

    // Handle special commands first
    switch (mainCommand) {
        case 'HELP':
            showHelp();
            break;
        case 'CLEAR':
            clearTerminal();
            break;
        case 'FONT':
            if (args.length > 0) {
                changeFont(args[0]);
            } else {
                cycleFont();
            }
            break;
        case 'THEME':
            toggleTheme();
            break;
        case 'SIZE':
            if (args.length > 0) {
                changeDisplaySize(args[0]);
            } else {
                cycleDisplaySize();
            }
            break;
        case 'STATUS':
            showSystemStatus();
            break;
        case 'HISTORY':
            showCommandHistory();
            break;
        case 'UCODE':
            enterUCodeMode();
            break;
        case 'PALETTE':
            if (args.length > 0) {
                switchPalette(args[0]);
            } else {
                showAvailablePalettes();
            }
            break;
        case 'MEMORY':
            if (args.length > 0) {
                handleMemorySystemCommand(args[0], args.slice(1));
            } else {
                showMemorySystemInfo();
            }
            break;
        case 'DISPLAY':
            if (args.length > 0) {
                switchDisplayConfig(args[0]);
            } else {
                showAvailableDisplayConfigs();
            }
            break;
        case 'STARTUP':
            showEnhancedStartupGraphics();
            break;
        case 'EXIT':
        case 'QUIT':
            if (udosApp.isUCodeMode) {
                exitUCodeMode();
            } else {
                addToTerminal('Use Ctrl+C to exit uDOS', 'info');
            }
            break;
        default:
            // Check if it's a uCODE module command
            if (ucodeModules[mainCommand]) {
                executeUCodeModule(mainCommand, args[0] || 'help', args.slice(1));
            }
            // Check if it's a system module command
            else if (systemModules[mainCommand]) {
                executeSystemModule(mainCommand, args[0] || 'help', args.slice(1));
            }
            // Check if it's an emoji command
            else if (cmd.length === 1 && /[\u{1F000}-\u{1FFFF}]/u.test(cmd)) {
                executeEmojiCommand(cmd);
            }
            else {
                addToTerminal(`❌ Unknown command: ${mainCommand}`, 'error');
                addToTerminal('💡 Type HELP for available commands', 'info');
            }
    }
}

function executeUCodeModule(module, action, args) {
    const moduleInfo = ucodeModules[module];
    if (!moduleInfo) {
        addToTerminal(`❌ Module ${module} not found`, 'error');
        return;
    }

    addToTerminal(`🔄 Executing ${module}.${action}...`, 'info');

    if (action === 'help') {
        addToTerminal(`📚 ${module} Module Help`, 'info');
        addToTerminal(`Description: ${moduleInfo.description}`, 'output');
        addToTerminal(`Available commands: ${moduleInfo.commands.join(', ')}`, 'output');
        return;
    }

    // Module-specific command handling
    switch (module) {
        case 'MEMORY':
            handleMemoryCommand(action, args);
            break;
        case 'MISSION':
            handleMissionCommand(action, args);
            break;
        case 'RENDER':
            handleRenderCommand(action, args);
            break;
        case 'DEV':
            handleDevCommand(action, args);
            break;
        case 'LOG':
            handleLogCommand(action, args);
            break;
        default:
            addToTerminal(`❌ Module ${module} handler not implemented`, 'error');
    }
}

function executeSystemModule(module, action, args) {
    addToTerminal(`🔧 Loading ${module} module...`, 'info');

    switch (module) {
        case 'SORCERER':
            handleSorcererModule(action, args);
            break;
        case 'WIZARD':
            handleWizardModule(action, args);
            break;
        default:
            addToTerminal(`📦 ${module}: ${systemModules[module]}`, 'info');
            addToTerminal('Module loaded successfully', 'success');
    }
}

// =============================================================================
// MODULE HANDLERS
// =============================================================================

function handleMemoryCommand(action, args) {
    switch (action) {
        case 'list':
            addToTerminal('📁 Memory Files:', 'info');
            addToTerminal('▶ system.mem - Core system memory', 'output');
            addToTerminal('▶ user.mem - User session data', 'output');
            addToTerminal('▶ cache.mem - Temporary cache', 'output');
            break;
        case 'stats':
            addToTerminal('📊 Memory Statistics:', 'info');
            addToTerminal('▶ Total files: 127', 'output');
            addToTerminal('▶ Storage used: 45.2 MB', 'output');
            addToTerminal('▶ Available: 154.8 MB', 'output');
            break;
        default:
            addToTerminal(`❌ Unknown MEMORY command: ${action}`, 'error');
    }
}

function handleMissionCommand(action, args) {
    switch (action) {
        case 'list':
            addToTerminal('🎯 Active Missions:', 'info');
            addToTerminal('▶ Mission-001: Font System Enhancement', 'output');
            addToTerminal('▶ Mission-002: Theme System Integration', 'output');
            addToTerminal('▶ Mission-003: Display Size Optimization', 'output');
            break;
        case 'create':
            if (args.length === 0) {
                addToTerminal('❌ Usage: MISSION create [title]', 'error');
            } else {
                addToTerminal(`✅ Created mission: ${args.join(' ')}`, 'success');
            }
            break;
        default:
            addToTerminal(`❌ Unknown MISSION command: ${action}`, 'error');
    }
}

function handleRenderCommand(action, args) {
    switch (action) {
        case 'art':
            addToTerminal('🎨 ASCII Art Generator:', 'info');
            addToTerminal('', 'output');
            showUDOSArt();
            break;
        case 'chart':
            addToTerminal('📊 System Performance Chart:', 'info');
            addToTerminal('CPU Usage: ████████░░ 80%', 'output');
            addToTerminal('Memory:    ██████░░░░ 60%', 'output');
            addToTerminal('Disk:      ███░░░░░░░ 30%', 'output');
            addToTerminal('Network:   █████████░ 90%', 'output');
            break;
        default:
            addToTerminal(`❌ Unknown RENDER command: ${action}`, 'error');
    }
}

function handleDevCommand(action, args) {
    switch (action) {
        case 'test':
            addToTerminal('🧪 Running test suite...', 'info');
            addToTerminal('▶ Font system tests: ✅ PASSED', 'output');
            addToTerminal('▶ Theme system tests: ✅ PASSED', 'output');
            addToTerminal('▶ Display size tests: ✅ PASSED', 'output');
            addToTerminal('All tests completed successfully!', 'success');
            break;
        case 'debug':
            addToTerminal('🐛 Debug Information:', 'info');
            addToTerminal(`▶ Current Font: ${udosApp.currentFont}`, 'output');
            addToTerminal(`▶ Current Theme: ${udosApp.currentTheme}`, 'output');
            addToTerminal(`▶ Current Size: ${udosApp.currentDisplaySize}`, 'output');
            addToTerminal(`▶ uCODE Mode: ${udosApp.isUCodeMode}`, 'output');
            break;
        default:
            addToTerminal(`❌ Unknown DEV command: ${action}`, 'error');
    }
}

function handleLogCommand(action, args) {
    switch (action) {
        case 'report':
            addToTerminal('📋 System Log Report:', 'info');
            addToTerminal('▶ Total entries: 2,847', 'output');
            addToTerminal('▶ Errors: 12', 'output');
            addToTerminal('▶ Warnings: 45', 'output');
            addToTerminal('▶ Info: 2,790', 'output');
            break;
        default:
            addToTerminal(`❌ Unknown LOG command: ${action}`, 'error');
    }
}

function handleSorcererModule(action, args) {
    switch (action) {
        case 'web':
            addToTerminal('🌐 SORCERER Web Automation:', 'info');
            addToTerminal('▶ Web scraping capabilities', 'output');
            addToTerminal('▶ Browser automation tools', 'output');
            addToTerminal('▶ API integration spells', 'output');
            addToTerminal('', 'output');
            addToTerminal('Web Commands:', 'info');
            addToTerminal('▶ web.test - Run web automation tests', 'output');
            addToTerminal('▶ web.scrape <url> <selectors> - Scrape webpage', 'output');
            addToTerminal('▶ web.help - Show web automation help', 'output');
            break;
        default:
            addToTerminal('🔮 SORCERER - Advanced system administration', 'info');
            addToTerminal('Available commands: web, cast, manage, tools', 'output');
    }
}

function handleWizardModule(action, args) {
    switch (action) {
        case 'cast':
            addToTerminal('🧙‍♂️ WIZARD Spell Casting:', 'info');
            addToTerminal('▶ Development Environment Enchantment ✨', 'output');
            addToTerminal('▶ Code Generation Spells Available', 'output');
            addToTerminal('▶ Project Template Magic Ready', 'output');
            break;
        default:
            addToTerminal('🧙‍♂️ WIZARD - Development wizard tools', 'info');
            addToTerminal('Available commands: cast, tools, spells, create', 'output');
    }
}

// =============================================================================
// uMEMORY SYSTEM INTEGRATION
// =============================================================================

async function loadMemorySystemResources() {
    try {
        console.log('🧠 Loading uMEMORY system resources...');

        // Load color palettes
        try {
            const paletteResponse = await fetch('/static/memory-system/colors/color-palettes-final.json');
            if (paletteResponse.ok) {
                udosApp.memoryPalettes = await paletteResponse.json();
                console.log('✅ uMEMORY color palettes loaded');
            }
        } catch (e) {
            console.log('⚠️ uMEMORY palettes not available, using built-in');
        }

        // Load font registry
        try {
            const fontResponse = await fetch('/static/memory-system/fonts/font-registry.json');
            if (fontResponse.ok) {
                udosApp.memoryFonts = await fontResponse.json();
                console.log('✅ uMEMORY font registry loaded');
            }
        } catch (e) {
            console.log('⚠️ uMEMORY font registry not available, using built-in');
        }

        // Load system configuration
        try {
            const configResponse = await fetch('/static/memory-system/config/system-config.json');
            if (configResponse.ok) {
                udosApp.systemConfig = await configResponse.json();
                console.log('✅ uMEMORY system configuration loaded');
            }
        } catch (e) {
            console.log('⚠️ uMEMORY system config not available, using built-in');
        }

        return true;
    } catch (error) {
        console.error('❌ Error loading uMEMORY resources:', error);
        return false;
    }
}

function showEnhancedStartupGraphics() {
    if (udosApp.startupGraphicsShown) return;

    console.log('🚀 Displaying enhanced startup graphics...');

    // Clear terminal first
    const terminal = document.getElementById('terminal-output');
    if (terminal) {
        terminal.innerHTML = '';
    }

    // Enhanced startup sequence with uMEMORY integration
    addToTerminal('', 'output');
    addToTerminal('╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗', 'accent');
    addToTerminal('║                                                                                                   ║', 'accent');
    addToTerminal('║  ██╗   ██╗██████╗  ██████╗ ███████╗    ██╗   ██╗███╗   ██╗██╗██╗   ██╗███████╗██████╗ ███████╗  ║', 'accent');
    addToTerminal('║  ██║   ██║██╔══██╗██╔═══██╗██╔════╝    ██║   ██║████╗  ██║██║██║   ██║██╔════╝██╔══██╗██╔════╝  ║', 'accent');
    addToTerminal('║  ██║   ██║██║  ██║██║   ██║███████╗    ██║   ██║██╔██╗ ██║██║██║   ██║█████╗  ██████╔╝███████╗  ║', 'accent');
    addToTerminal('║  ██║   ██║██║  ██║██║   ██║╚════██║    ██║   ██║██║╚██╗██║██║╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║  ║', 'accent');
    addToTerminal('║  ╚██████╔╝██████╔╝╚██████╔╝███████║    ╚██████╔╝██║ ╚████║██║ ╚████╔╝ ███████╗██║  ██║███████║  ║', 'accent');
    addToTerminal('║   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝     ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝  ║', 'accent');
    addToTerminal('║                                                                                                   ║', 'accent');
    addToTerminal('║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ║', 'accent');
    addToTerminal('║  ▓  UNIVERSAL DEVELOPMENT OPERATING SYSTEM - CODE INTERFACE v1.3 + uMEMORY INTEGRATION   ▓  ║', 'accent');
    addToTerminal('║  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ║', 'accent');
    addToTerminal('║                                                                                                   ║', 'accent');
    addToTerminal('╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝', 'accent');
    addToTerminal('', 'output');

    // System initialization sequence
    addToTerminal('🔧 SYSTEM INITIALIZATION SEQUENCE', 'info');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');

    setTimeout(() => {
        addToTerminal('🧠 Loading uMEMORY system resources...', 'info');
        addToTerminal(`   ▶ Color palettes: ${udosApp.memoryPalettes ? '✅ LOADED' : '⚠️  FALLBACK'}`, 'output');
        addToTerminal(`   ▶ Font registry:  ${udosApp.memoryFonts ? '✅ LOADED' : '⚠️  FALLBACK'}`, 'output');
        addToTerminal(`   ▶ System config:  ${udosApp.systemConfig ? '✅ LOADED' : '⚠️  FALLBACK'}`, 'output');
    }, 500);

    setTimeout(() => {
        addToTerminal('🎨 Initializing display subsystem...', 'info');
        addToTerminal('   ▶ Font engine: MODE7GX3 Authentic BBC Teletext', 'output');
        addToTerminal('   ▶ Color engine: uDOS Professional Palette', 'output');
        addToTerminal('   ▶ Display mode: BBC Mode 7 Compatible (40×25)', 'output');
        addToTerminal('   ▶ Aspect ratio: 1:1.3 (Authentic teletext)', 'output');
    }, 1000);

    setTimeout(() => {
        addToTerminal('📺 Available display configurations:', 'info');
        if (udosApp.systemConfig) {
            const configs = udosApp.systemConfig.system_config.display_configurations;
            Object.keys(configs).forEach(key => {
                const config = configs[key];
                addToTerminal(`   ▶ ${config.name}: ${config.width}×${config.height} (${config.font})`, 'output');
            });
        } else {
            addToTerminal('   ▶ BBC Mode 7 Authentic: 640×500 (MODE7GX3)', 'output');
            addToTerminal('   ▶ uDOS Optimized: 800×615 (MODE7GX3)', 'output');
            addToTerminal('   ▶ Compact Display: 640×480 (MODE7GX2)', 'output');
            addToTerminal('   ▶ Widescreen Display: 1024×768 (MODE7GX4)', 'output');
        }
    }, 1500);

    setTimeout(() => {
        addToTerminal('🔤 Available authentic fonts:', 'info');
        if (udosApp.memoryFonts) {
            const fonts = udosApp.memoryFonts.font_registry;
            Object.keys(fonts.bbc_mode7_fonts).forEach(key => {
                const font = fonts.bbc_mode7_fonts[key];
                addToTerminal(`   ▶ ${font.name}: ${font.size} (${font.description})`, 'output');
            });
            Object.keys(fonts.retro_fonts).forEach(key => {
                const font = fonts.retro_fonts[key];
                addToTerminal(`   ▶ ${font.name}: ${font.size} (${font.description})`, 'output');
            });
        } else {
            Object.keys(udosFonts).forEach(key => {
                const font = udosFonts[key];
                if (font.authentic) {
                    addToTerminal(`   ▶ ${key}: ${font.description}`, 'output');
                }
            });
        }
    }, 2000);

    setTimeout(() => {
        showTeletextBlockDemo();
    }, 2500);

    setTimeout(() => {
        showSystemStatus();
        addToTerminal('', 'output');
        addToTerminal('🌟 uDOS Universal Code Interface Ready', 'success');
        addToTerminal('📺 Enhanced with uMEMORY system integration', 'info');
        addToTerminal('💡 Type HELP for commands or click emoji icons for instant access', 'info');
        addToTerminal('🎨 Use PALETTE, FONT, or DISPLAY commands to customize appearance', 'info');
        addToTerminal('', 'output');

        udosApp.startupGraphicsShown = true;
    }, 3000);
}

function showTeletextBlockDemo() {
    addToTerminal('📺 TELETEXT BLOCK GRAPHICS DEMONSTRATION', 'info');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    addToTerminal('', 'output');
    addToTerminal(' ████████████████████████████████████████████████████████████████████████████████████████████', 'info');
    addToTerminal(' █                                                                                          █', 'info');
    addToTerminal(' █  ▓▓▓▓▓▓  ░░░░░░  ▒▒▒▒▒▒  ██████  BBC MODE 7 TELETEXT BLOCKS  ██████  ▒▒▒▒▒▒  ░░░░░░  █', 'info');
    addToTerminal(' █                                                                                          █', 'info');
    addToTerminal(' █  ▀▀▀▀▀▀  ▄▄▄▄▄▄  ▌▌▌▌▌▌  ▐▐▐▐▐▐  AUTHENTIC 1:1.3 ASPECT RATIO  ▐▐▐▐▐▐  ▌▌▌▌▌▌  ▄▄▄▄▄▄  █', 'info');
    addToTerminal(' █                                                                                          █', 'info');
    addToTerminal(' █  🟥🟧🟨🟩🟦🟪⬛⬜  COLOR PALETTE SUPPORT  ⬜⬛🟪🟦🟩🟨🟧🟥                            █', 'info');
    addToTerminal(' █                                                                                          █', 'info');
    addToTerminal(' █  ╔═══╗ ╔═══╗ ╔═══╗   PERFECT MONOSPACE ALIGNMENT   ╔═══╗ ╔═══╗ ╔═══╗                   █', 'info');
    addToTerminal(' █  ║ A ║ ║ B ║ ║ C ║   40 COLUMNS × 25 ROWS GRID   ║ X ║ ║ Y ║ ║ Z ║                   █', 'info');
    addToTerminal(' █  ╚═══╝ ╚═══╝ ╚═══╝                                ╚═══╝ ╚═══╝ ╚═══╝                   █', 'info');
    addToTerminal(' █                                                                                          █', 'info');
    addToTerminal(' ████████████████████████████████████████████████████████████████████████████████████████████', 'info');
    addToTerminal('', 'output');

    // Show color palette if uMEMORY palette is loaded
    if (udosApp.memoryPalettes) {
        addToTerminal('🎨 uMEMORY COLOR PALETTE LOADED:', 'info');
        const palette = udosApp.memoryPalettes.color_palettes.udos_final;
        addToTerminal(`   ▶ ${palette.name}: ${palette.description}`, 'output');
        Object.keys(palette.colors).forEach(colorKey => {
            const color = palette.colors[colorKey];
            addToTerminal(`   ▶ ${colorKey}: ${color.hex} (${color.name})`, 'output');
        });
        addToTerminal('', 'output');
    }
}

// =============================================================================
// uMEMORY COMMAND HANDLERS
// =============================================================================

function switchPalette(paletteName) {
    addToTerminal(`🎨 Switching to palette: ${paletteName}`, 'info');

    if (udosApp.memoryPalettes) {
        const palettes = udosApp.memoryPalettes.color_palettes;
        if (palettes[paletteName]) {
            const palette = palettes[paletteName];
            addToTerminal(`✅ Applied palette: ${palette.name}`, 'success');
            addToTerminal(`   Description: ${palette.description}`, 'output');

            // Apply palette colors if theme exists
            if (palette.themes && palette.themes.default) {
                const theme = palette.themes.default;
                document.documentElement.style.setProperty('--bg-primary', palette.colors[theme.bg_primary]?.hex || '#000000');
                document.documentElement.style.setProperty('--text-primary', palette.colors[theme.text_primary]?.hex || '#ffffff');
                document.documentElement.style.setProperty('--text-accent', palette.colors[theme.accent]?.hex || '#00ff00');
            }
        } else {
            addToTerminal(`❌ Palette not found: ${paletteName}`, 'error');
            showAvailablePalettes();
        }
    } else {
        addToTerminal('❌ uMEMORY palettes not loaded', 'error');
        addToTerminal('Available built-in themes: dark, light, udos_final', 'info');
    }
}

function showAvailablePalettes() {
    addToTerminal('🎨 Available Color Palettes:', 'info');

    if (udosApp.memoryPalettes) {
        const palettes = udosApp.memoryPalettes.color_palettes;
        Object.keys(palettes).forEach(key => {
            if (key !== 'metadata' && key !== 'css_variables') {
                const palette = palettes[key];
                addToTerminal(`▶ ${key}: ${palette.name} - ${palette.description}`, 'output');
            }
        });
    } else {
        addToTerminal('▶ dark: Classic dark theme with green text', 'output');
        addToTerminal('▶ light: Light theme with black text', 'output');
        addToTerminal('▶ udos_final: Professional uDOS color palette', 'output');
    }
}

function switchDisplayConfig(configName) {
    addToTerminal(`📺 Switching to display config: ${configName}`, 'info');

    if (udosApp.systemConfig) {
        const configs = udosApp.systemConfig.system_config.display_configurations;
        if (configs[configName]) {
            const config = configs[configName];
            addToTerminal(`✅ Applied display config: ${config.name}`, 'success');
            addToTerminal(`   Resolution: ${config.width}×${config.height}`, 'output');
            addToTerminal(`   Font: ${config.font} (${config.font_size})`, 'output');
            addToTerminal(`   Character grid: ${config.character_grid.columns}×${config.character_grid.rows}`, 'output');

            // Apply the font and size
            if (udosFonts[config.font]) {
                changeFont(config.font);
            }
        } else {
            addToTerminal(`❌ Display config not found: ${configName}`, 'error');
            showAvailableDisplayConfigs();
        }
    } else {
        addToTerminal('❌ uMEMORY system config not loaded', 'error');
        addToTerminal('Available built-in sizes: tiny, small, medium, large, huge, giant', 'info');
    }
}

function showAvailableDisplayConfigs() {
    addToTerminal('📺 Available Display Configurations:', 'info');

    if (udosApp.systemConfig) {
        const configs = udosApp.systemConfig.system_config.display_configurations;
        Object.keys(configs).forEach(key => {
            const config = configs[key];
            addToTerminal(`▶ ${key}: ${config.name} (${config.width}×${config.height}, ${config.font})`, 'output');
            addToTerminal(`   ${config.description}`, 'output');
        });
    } else {
        addToTerminal('▶ bbc_authentic: Authentic BBC Mode 7 (640×500)', 'output');
        addToTerminal('▶ udos_optimized: Modern optimized display (800×615)', 'output');
        addToTerminal('▶ compact: Compact display for small screens (640×480)', 'output');
        addToTerminal('▶ widescreen: Large widescreen display (1024×768)', 'output');
    }
}

function handleMemorySystemCommand(action, args) {
    switch (action.toLowerCase()) {
        case 'status':
            showMemorySystemInfo();
            break;
        case 'reload':
            loadMemorySystemResources().then(success => {
                if (success) {
                    addToTerminal('✅ uMEMORY system resources reloaded', 'success');
                } else {
                    addToTerminal('❌ Failed to reload uMEMORY resources', 'error');
                }
            });
            break;
        case 'fonts':
            showMemoryFonts();
            break;
        case 'palettes':
            showAvailablePalettes();
            break;
        case 'config':
            showMemoryConfig();
            break;
        default:
            addToTerminal(`❌ Unknown MEMORY command: ${action}`, 'error');
            addToTerminal('Available commands: status, reload, fonts, palettes, config', 'info');
    }
}

function showMemorySystemInfo() {
    addToTerminal('🧠 uMEMORY System Status:', 'info');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');

    addToTerminal(`Color Palettes: ${udosApp.memoryPalettes ? '✅ LOADED' : '❌ NOT LOADED'}`, 'output');
    if (udosApp.memoryPalettes) {
        const paletteCount = Object.keys(udosApp.memoryPalettes.color_palettes).length - 2; // Exclude metadata and css_variables
        addToTerminal(`   Available palettes: ${paletteCount}`, 'output');
    }

    addToTerminal(`Font Registry: ${udosApp.memoryFonts ? '✅ LOADED' : '❌ NOT LOADED'}`, 'output');
    if (udosApp.memoryFonts) {
        const bbcFonts = Object.keys(udosApp.memoryFonts.font_registry.bbc_mode7_fonts).length;
        const retroFonts = Object.keys(udosApp.memoryFonts.font_registry.retro_fonts).length;
        addToTerminal(`   BBC Mode 7 fonts: ${bbcFonts}`, 'output');
        addToTerminal(`   Retro fonts: ${retroFonts}`, 'output');
    }

    addToTerminal(`System Config: ${udosApp.systemConfig ? '✅ LOADED' : '❌ NOT LOADED'}`, 'output');
    if (udosApp.systemConfig) {
        const displayConfigs = Object.keys(udosApp.systemConfig.system_config.display_configurations).length;
        addToTerminal(`   Display configurations: ${displayConfigs}`, 'output');
    }

    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
}

function showMemoryFonts() {
    addToTerminal('🔤 uMEMORY Font Registry:', 'info');

    if (udosApp.memoryFonts) {
        const registry = udosApp.memoryFonts.font_registry;

        addToTerminal('BBC Mode 7 Fonts:', 'info');
        Object.keys(registry.bbc_mode7_fonts).forEach(key => {
            const font = registry.bbc_mode7_fonts[key];
            addToTerminal(`▶ ${key}: ${font.name} (${font.size}, ${font.aspect_ratio})`, 'output');
            addToTerminal(`   ${font.description}`, 'output');
        });

        addToTerminal('', 'output');
        addToTerminal('Retro Computer Fonts:', 'info');
        Object.keys(registry.retro_fonts).forEach(key => {
            const font = registry.retro_fonts[key];
            addToTerminal(`▶ ${key}: ${font.name} (${font.size}, ${font.platform})`, 'output');
            addToTerminal(`   ${font.description}`, 'output');
        });
    } else {
        addToTerminal('❌ uMEMORY font registry not loaded', 'error');
        addToTerminal('Using built-in font system', 'info');
    }
}

function showMemoryConfig() {
    addToTerminal('⚙️ uMEMORY System Configuration:', 'info');

    if (udosApp.systemConfig) {
        const config = udosApp.systemConfig.system_config;

        addToTerminal('Display Configurations:', 'info');
        Object.keys(config.display_configurations).forEach(key => {
            const display = config.display_configurations[key];
            addToTerminal(`▶ ${key}: ${display.name}`, 'output');
            addToTerminal(`   Resolution: ${display.width}×${display.height}`, 'output');
            addToTerminal(`   Font: ${display.font} (${display.font_size})`, 'output');
        });

        addToTerminal('', 'output');
        addToTerminal('System Defaults:', 'info');
        const defaults = config.system_defaults;
        addToTerminal(`▶ Startup mode: ${defaults.startup.interface_mode}`, 'output');
        addToTerminal(`▶ Default font: ${defaults.startup.font}`, 'output');
        addToTerminal(`▶ Auto-optimize: ${defaults.startup.auto_optimize}`, 'output');
    } else {
        addToTerminal('❌ uMEMORY system configuration not loaded', 'error');
        addToTerminal('Using built-in system defaults', 'info');
    }
}

function showHelp() {
    addToTerminal('🌟 uDOS Universal Code Interface Help', 'info');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    addToTerminal('System Commands:', 'info');
    addToTerminal('▶ HELP         - Show this help', 'output');
    addToTerminal('▶ CLEAR        - Clear terminal', 'output');
    addToTerminal('▶ FONT [name]  - Change or cycle fonts', 'output');
    addToTerminal('▶ THEME        - Toggle light/dark theme', 'output');
    addToTerminal('▶ SIZE [name]  - Change or cycle display size', 'output');
    addToTerminal('▶ STATUS       - Show system status', 'output');
    addToTerminal('▶ HISTORY      - Show command history', 'output');
    addToTerminal('▶ UCODE        - Enter uCODE mode', 'output');
    addToTerminal('▶ STARTUP      - Show enhanced startup graphics', 'output');
    addToTerminal('▶ PALETTE [name] - Switch color palette', 'output');
    addToTerminal('▶ DISPLAY [config] - Switch display configuration', 'output');
    addToTerminal('▶ MEMORY [cmd] - uMEMORY system commands', 'output');
    addToTerminal('', 'output');
    addToTerminal('Available Fonts:', 'info');
    Object.keys(udosFonts).forEach(font => {
        addToTerminal(`▶ ${font.padEnd(12)} - ${udosFonts[font].description}`, 'output');
    });
    addToTerminal('', 'output');
    addToTerminal('Display Sizes:', 'info');
    Object.keys(udosDisplaySizes).forEach(size => {
        addToTerminal(`▶ ${size.padEnd(12)} - ${udosDisplaySizes[size].description}`, 'output');
    });
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
}

function showSystemStatus() {
    addToTerminal('📊 uDOS System Status', 'info');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
    addToTerminal(`Current Font: ${udosApp.currentFont} - ${udosFonts[udosApp.currentFont].description}`, 'output');
    addToTerminal(`Current Theme: ${udosApp.currentTheme}`, 'output');
    addToTerminal(`Display Size: ${udosApp.currentDisplaySize} - ${udosDisplaySizes[udosApp.currentDisplaySize].description}`, 'output');
    addToTerminal(`uCODE Mode: ${udosApp.isUCodeMode ? 'Active' : 'Inactive'}`, 'output');
    addToTerminal(`Commands in History: ${udosApp.commandHistory.length}`, 'output');
    addToTerminal('System: ✅ OPERATIONAL', 'success');
    addToTerminal('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'output');
}

function showCommandHistory() {
    addToTerminal('📚 Command History:', 'info');
    if (udosApp.commandHistory.length === 0) {
        addToTerminal('No commands in history', 'output');
    } else {
        udosApp.commandHistory.slice(-10).forEach((cmd, index) => {
            addToTerminal(`${(udosApp.commandHistory.length - 10 + index + 1).toString().padStart(3)}: ${cmd}`, 'output');
        });
    }
}

function showUDOSArt() {
    addToTerminal('', 'output');
    addToTerminal('╔══════════════════════════════════════════════════════════════════════════════════════╗', 'accent');
    addToTerminal('║  ██╗   ██╗██████╗  ██████╗ ███████╗    ██╗   ██╗ ██╗  ██████╗                       ║', 'accent');
    addToTerminal('║  ██║   ██║██╔══██╗██╔═══██╗██╔════╝    ██║   ██║███║ ██╔════╝                       ║', 'accent');
    addToTerminal('║  ██║   ██║██║  ██║██║   ██║███████╗    ██║   ██║╚██║ ╚█████╗                        ║', 'accent');
    addToTerminal('║  ██║   ██║██║  ██║██║   ██║╚════██║    ╚██╗ ██╔╝ ██║  ╚═══██╗                       ║', 'accent');
    addToTerminal('║  ╚██████╔╝██████╔╝╚██████╔╝███████║     ╚████╔╝  ██║ ██████╔╝                       ║', 'accent');
    addToTerminal('║   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝      ╚═══╝   ╚═╝ ╚═════╝                        ║', 'accent');
    addToTerminal('║                                                                                      ║', 'accent');
    addToTerminal('║  ▓▓▓ UNIVERSAL DEVELOPMENT OPERATING SYSTEM ▓▓▓                                     ║', 'accent');
    addToTerminal('║  ░░░ Professional Retro Computing Interface v1.3 ░░░                               ║', 'accent');
    addToTerminal('║                                                                                      ║', 'accent');
    addToTerminal('║  ████ TELETEXT BLOCKS: ▀▄█▌▐░▒▓  ████  ASCII ART READY  ████                       ║', 'accent');
    addToTerminal('║  ▓▓▓▓ AUTHENTIC FONTS: BBC MODE 7 + C64 + AMIGA ▓▓▓▓                               ║', 'accent');
    addToTerminal('║                                                                                      ║', 'accent');
    addToTerminal('║  🌳 TREE  🔄 REBOOT  💥 DESTROY  📖 STORY  👻 GHOST  🚁 DRONE  😈 IMP  🔮 SORCERER   ║', 'info');
    addToTerminal('║  🧙‍♂️ WIZARD  💻 DEV  |  📐 SIZE  🔤 FONT  🌓 THEME  📝 MARKDOWN                    ║', 'info');
    addToTerminal('║                                                                                      ║', 'accent');
    addToTerminal(`║  STATUS: READY ● FONT: ${udosApp.currentFont} ● THEME: ${udosApp.currentTheme.toUpperCase()} ● SIZE: ${udosApp.currentDisplaySize.toUpperCase()}      ║`, 'success');
    addToTerminal('╚══════════════════════════════════════════════════════════════════════════════════════╝', 'accent');
    addToTerminal('', 'output');

    // Show teletext block demonstration
    addToTerminal(' ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄', 'info');
    addToTerminal(' █                                                                                 █', 'info');
    addToTerminal(' █  ██████  TELETEXT DEMONSTRATION - BBC MODE 7 STYLED BLOCKS  ██████             █', 'info');
    addToTerminal(' █                                                                                 █', 'info');
    addToTerminal(' █  ░░░░░░  ▒▒▒▒▒▒  ▓▓▓▓▓▓  ██████  HALFTONE PATTERNS  ██████  ▓▓▓▓▓▓  ▒▒▒▒▒▒    █', 'info');
    addToTerminal(' █                                                                                 █', 'info');
    addToTerminal(' █  ▀▀▀▀▀▀  ▄▄▄▄▄▄  ██████  ▌▌▌▌▌▌  BLOCK GRAPHICS   ▐▐▐▐▐▐  ██████  ▄▄▄▄▄▄    █', 'info');
    addToTerminal(' █                                                                                 █', 'info');
    addToTerminal(' █  1:1 MONOSPACE CHARACTER GRID ● 1:1.3 TELETEXT BLOCK RATIO ● PERFECT ALIGNMENT █', 'info');
    addToTerminal(' ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀', 'info');
    addToTerminal('', 'output');
}

function enterUCodeMode() {
    udosApp.isUCodeMode = true;
    addToTerminal('🎯 Entering uCODE mode...', 'info');
    addToTerminal('Advanced command system activated', 'success');
    addToTerminal('Type EXIT to return to normal mode', 'info');
    updatePrompt();
}

function exitUCodeMode() {
    udosApp.isUCodeMode = false;
    addToTerminal('👋 Exiting uCODE mode...', 'info');
    addToTerminal('Returning to normal command mode', 'success');
    updatePrompt();
}

function updatePrompt() {
    const promptElement = document.querySelector('.prompt');
    if (promptElement) {
        promptElement.textContent = udosApp.isUCodeMode ? 'uCODE>' : 'uDOS>';
    }
}

// =============================================================================
// EMOJI COMMAND SYSTEM
// =============================================================================

function executeEmojiCommand(command) {
    // Map emoji commands to their functions
    const emojiCommands = {
        '💾': () => triggerWorkflowScript('BACKUP'),
        '♻️': () => triggerWorkflowScript('RESTORE'),
        '🛠️': () => triggerWorkflowScript('REPAIR'),
        '🔁': () => triggerWorkflowScript('SESSION'),
        '📤': () => triggerWorkflowScript('PUSH'),
        '🌳': () => executeCommand('TREE'),
        '🔄': () => executeCommand('REBOOT'),
        '💥': () => executeCommand('DESTROY'),
        '📖': () => executeCommand('STORY'),
        '👻': () => executeCommand('GHOST'),
        '🚁': () => executeCommand('DRONE'),
        '😈': () => executeCommand('IMP'),
        '🔮': () => executeCommand('SORCERER'),
        '🧙‍♂️': () => executeCommand('WIZARD'),
        '💻': () => executeCommand('DEV'),
        '📐': () => cycleDisplaySize(),
        '🔤': () => cycleFont(),
        '🌓': () => toggleTheme(),
        '📝': () => addToTerminal('📝 Markdown mode activated', 'info')
    };
    // Trigger workflow shell scripts directly (for now)
    function triggerWorkflowScript(action) {
        // This would ideally call a backend API, but for now just show a message
        addToTerminal(`🚀 Triggering workflow: ${action}`, 'info');
        // Example: window.open(`/sandbox/user/backup.sh?cmd=${action}`, '_blank');
        // Or use fetch/ajax to POST to backend
        // For now, just show the command
    }

    if (emojiCommands[command]) {
        emojiCommands[command]();
    } else {
        addToTerminal(`❌ Unknown emoji command: ${command}`, 'error');
    }
}

// =============================================================================
// SMART INPUT SYSTEM
// =============================================================================

// Smart input command database
const smartCommands = {
    // System Commands
    'help': { desc: 'Show available commands', category: 'system' },
    'clear': { desc: 'Clear terminal output', category: 'system' },
    'status': { desc: 'Display system status', category: 'system' },
    'history': { desc: 'Show command history', category: 'system' },
    'startup': { desc: 'Show enhanced startup graphics', category: 'system' },

    // Font Commands
    'font': { desc: 'Change font (font [name])', category: 'display' },
    'font MODE7GX0': { desc: 'Switch to MODE7GX0 square font (default)', category: 'display' },
    'font MONACO': { desc: 'Switch to Monaco system font', category: 'display' },
    'font MENLO': { desc: 'Switch to Menlo system font', category: 'display' },
    'font SF_MONO': { desc: 'Switch to SF Mono system font', category: 'display' },
    'font COURIER_NEW': { desc: 'Switch to Courier New system font', category: 'display' },
    'font CONSOLAS': { desc: 'Switch to Consolas system font', category: 'display' },
    'font FIRA_CODE': { desc: 'Switch to Fira Code programming font', category: 'display' },
    'font JETBRAINS_MONO': { desc: 'Switch to JetBrains Mono programming font', category: 'display' },
    'font SOURCE_CODE_PRO': { desc: 'Switch to Source Code Pro programming font', category: 'display' },
    'font TERMINAL': { desc: 'Switch to terminal default font', category: 'display' },
    'font VT100': { desc: 'Switch to VT100 terminal font', category: 'display' },

    // Theme Commands
    'theme': { desc: 'Toggle light/dark theme', category: 'display' },
    'palette': { desc: 'Switch color palette (palette [name])', category: 'display' },
    'palette dark': { desc: 'Switch to dark theme', category: 'display' },
    'palette light': { desc: 'Switch to light theme', category: 'display' },
    'palette udos_final': { desc: 'Switch to uMEMORY professional palette', category: 'display' },

    // Display Commands
    'size': { desc: 'Change display size (size [name])', category: 'display' },
    'size tiny': { desc: 'C64 PETSCII size (8×8)', category: 'display' },
    'size small': { desc: 'BBC Mode 7 size (8×10)', category: 'display' },
    'size medium': { desc: 'Amiga Workbench size (8×12)', category: 'display' },
    'size large': { desc: 'VT100 Terminal size (7×14)', category: 'display' },
    'size huge': { desc: 'Modern Terminal size (8×16)', category: 'display' },
    'size giant': { desc: 'Presentation Mode size (10×20)', category: 'display' },

    'display': { desc: 'Switch display config (display [config])', category: 'display' },
    'display bbc_authentic': { desc: 'BBC Mode 7 Authentic (640×500)', category: 'display' },
    'display udos_optimized': { desc: 'uDOS Optimized (800×615)', category: 'display' },
    'display compact': { desc: 'Compact Display (640×480)', category: 'display' },
    'display widescreen': { desc: 'Widescreen Display (1024×768)', category: 'display' },

    // uMEMORY Commands
    'memory': { desc: 'uMEMORY system commands', category: 'memory' },
    'memory status': { desc: 'Show uMEMORY system status', category: 'memory' },
    'memory reload': { desc: 'Reload uMEMORY resources', category: 'memory' },
    'memory fonts': { desc: 'Show uMEMORY font registry', category: 'memory' },
    'memory palettes': { desc: 'Show available color palettes', category: 'memory' },
    'memory config': { desc: 'Show uMEMORY system configuration', category: 'memory' },

    // uCODE Module Commands
    'ucode': { desc: 'Enter uCODE mode', category: 'ucode' },
    'memory list': { desc: 'List memory files', category: 'ucode' },
    'memory stats': { desc: 'Show memory statistics', category: 'ucode' },
    'mission list': { desc: 'List active missions', category: 'ucode' },
    'mission create': { desc: 'Create new mission', category: 'ucode' },
    'render art': { desc: 'Generate ASCII art', category: 'ucode' },
    'render chart': { desc: 'Show performance chart', category: 'ucode' },
    'dev test': { desc: 'Run test suite', category: 'ucode' },
    'dev debug': { desc: 'Show debug information', category: 'ucode' },
    'log report': { desc: 'Show system log report', category: 'ucode' },

    // System Module Commands
    'sorcerer': { desc: 'Launch SORCERER advanced admin', category: 'modules' },
    'sorcerer web': { desc: 'Web automation commands', category: 'modules' },
    'wizard': { desc: 'Launch WIZARD development tools', category: 'modules' },
    'wizard cast': { desc: 'Cast development spells', category: 'modules' },
    'ghost': { desc: 'Background services', category: 'modules' },
    'drone': { desc: 'Automation tasks', category: 'modules' },
    'imp': { desc: 'Script execution engine', category: 'modules' },
    'tomb': { desc: 'Archive and backup system', category: 'modules' },

    // Quick Actions
    'tree': { desc: 'Show file tree structure', category: 'quick' },
    'reboot': { desc: 'Restart system', category: 'quick' },
    'destroy': { desc: 'Emergency system reset', category: 'quick' },
    'story': { desc: 'Show system story/documentation', category: 'quick' }
};

let smartInput = {
    suggestions: [],
    selectedIndex: -1,
    isVisible: false,
    currentInput: '',
    commandHistory: [],
    historyIndex: -1
};

function setupSmartInput() {
    const input = document.getElementById('command-input');
    if (!input) return;

    console.log('🧠 Setting up smart input system...');

    // Create suggestions container
    createSuggestionsContainer();

    // Set up event listeners
    input.addEventListener('input', handleSmartInput);
    input.addEventListener('keydown', handleSmartKeydown);
    input.addEventListener('blur', hideSuggestions);
    input.addEventListener('focus', handleInputFocus);

    console.log('✅ Smart input system ready');
}

function createSuggestionsContainer() {
    const container = document.querySelector('.command-input-container');
    if (!container) return;

    // Remove existing suggestions if any
    const existing = document.getElementById('smart-suggestions');
    if (existing) existing.remove();

    const suggestions = document.createElement('div');
    suggestions.id = 'smart-suggestions';
    suggestions.className = 'smart-suggestions';
    suggestions.innerHTML = '';

    container.appendChild(suggestions);
}

function handleSmartInput(e) {
    const value = e.target.value.toLowerCase().trim();
    smartInput.currentInput = value;

    // Always reset selected index on new input
    smartInput.selectedIndex = -1;

    if (value.length < 1) {
        hideSuggestions();
        return;
    }

    // Find matching commands
    const matches = findCommandMatches(value);

    if (matches.length > 0) {
        showSuggestions(matches);
        // Always focus first suggestion for keyboard navigation
        smartInput.selectedIndex = 0;
        highlightSuggestion(0);
    } else {
        hideSuggestions();
    }
}

function findCommandMatches(input) {
    const matches = [];

    // Exact matches first
    Object.keys(smartCommands).forEach(cmd => {
        if (cmd.toLowerCase().startsWith(input)) {
            matches.push({
                command: cmd,
                ...smartCommands[cmd],
                matchType: 'exact'
            });
        }
    });

    // Partial matches
    if (matches.length < 5) {
        Object.keys(smartCommands).forEach(cmd => {
            if (cmd.toLowerCase().includes(input) && !cmd.toLowerCase().startsWith(input)) {
                matches.push({
                    command: cmd,
                    ...smartCommands[cmd],
                    matchType: 'partial'
                });
            }
        });
    }

    // Sort by relevance
    return matches.slice(0, 8).sort((a, b) => {
        if (a.matchType !== b.matchType) {
            return a.matchType === 'exact' ? -1 : 1;
        }
        return a.command.length - b.command.length;
    });
}

function showSuggestions(matches) {
    const container = document.getElementById('smart-suggestions');
    if (!container) return;

    smartInput.suggestions = matches;
    smartInput.selectedIndex = -1;
    smartInput.isVisible = true;

    const html = matches.map((match, index) => {
        const categoryColor = getCategoryColor(match.category);
        return `
            <div class="suggestion-item" data-index="${index}" onclick="selectSuggestion(${index})">
                <div class="suggestion-main">
                    <span class="suggestion-command">${highlightMatch(match.command, smartInput.currentInput)}</span>
                    <span class="suggestion-category" style="color: ${categoryColor}">${match.category}</span>
                </div>
                <div class="suggestion-desc">${match.desc}</div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
    container.style.display = 'block';
}

function getCategoryColor(category) {
    const colors = {
        'system': 'var(--text-accent)',
        'display': 'var(--text-info)',
        'memory': 'var(--udos-shamrock)',
        'ucode': 'var(--udos-purple)',
        'modules': 'var(--udos-cinnamon)',
        'quick': 'var(--udos-caramel)'
    };
    return colors[category] || 'var(--text-secondary)';
}

function highlightMatch(command, input) {
    const index = command.toLowerCase().indexOf(input);
    if (index === -1) return command;

    return command.substring(0, index) +
        `<mark>${command.substring(index, index + input.length)}</mark>` +
        command.substring(index + input.length);
}

function hideSuggestions() {
    const container = document.getElementById('smart-suggestions');
    if (container) {
        container.style.display = 'none';
    }
    smartInput.isVisible = false;
    smartInput.selectedIndex = -1;
}

function selectSuggestion(index) {
    if (index < 0 || index >= smartInput.suggestions.length) return;

    const suggestion = smartInput.suggestions[index];
    const input = document.getElementById('command-input');

    if (input) {
        input.value = suggestion.command;
        input.focus();
    }

    hideSuggestions();
}

function highlightSuggestion(index) {
    const container = document.getElementById('smart-suggestions');
    if (!container) return;
    Array.from(container.children).forEach((el, i) => {
        el.classList.toggle('highlighted', i === index);
    });
}

function handleSmartKeydown(e) {
    if (!smartInput.isVisible) {
        handleHistoryNavigation(e);
        return;
    }

    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            navigateSuggestions(1);
            break;

        case 'ArrowUp':
            e.preventDefault();
            navigateSuggestions(-1);
            break;

        case 'Tab':
        case 'Enter':
            if (smartInput.selectedIndex >= 0) {
                e.preventDefault();
                selectSuggestion(smartInput.selectedIndex);
                if (e.key === 'Enter') {
                    // Execute the command
                    setTimeout(() => {
                        e.target.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
                    }, 50);
                }
            }
            break;

        case 'Escape':
            e.preventDefault();
            hideSuggestions();
            break;
    }
}

function navigateSuggestions(direction) {
    if (smartInput.suggestions.length === 0) return;

    // Remove previous highlight
    if (smartInput.selectedIndex >= 0) {
        const prevItem = document.querySelector(`.suggestion-item[data-index="${smartInput.selectedIndex}"]`);
        if (prevItem) prevItem.classList.remove('selected');
    }

    // Update selection
    smartInput.selectedIndex += direction;

    if (smartInput.selectedIndex < 0) {
        smartInput.selectedIndex = smartInput.suggestions.length - 1;
    } else if (smartInput.selectedIndex >= smartInput.suggestions.length) {
        smartInput.selectedIndex = 0;
    }

    // Highlight new selection
    const newItem = document.querySelector(`.suggestion-item[data-index="${smartInput.selectedIndex}"]`);
    if (newItem) {
        newItem.classList.add('selected');
        newItem.scrollIntoView({ block: 'nearest' });
    }
}

function handleHistoryNavigation(e) {
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateCommandHistory(-1);
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateCommandHistory(1);
    }
}

function navigateCommandHistory(direction) {
    if (udosApp.commandHistory.length === 0) return;

    udosApp.historyIndex += direction;

    if (udosApp.historyIndex < 0) {
        udosApp.historyIndex = 0;
    } else if (udosApp.historyIndex >= udosApp.commandHistory.length) {
        udosApp.historyIndex = udosApp.commandHistory.length;
        document.getElementById('command-input').value = '';
        return;
    }

    const input = document.getElementById('command-input');
    if (input) {
        input.value = udosApp.commandHistory[udosApp.historyIndex] || '';
    }
}

function handleInputFocus() {
    const input = document.getElementById('command-input');
    if (input && input.value.trim().length > 0) {
        handleSmartInput({ target: input });
    }
}

// =============================================================================
// EVENT HANDLERS & INITIALIZATION
// =============================================================================

function setupEventListeners() {
    const commandInput = document.getElementById('command-input');
    if (!commandInput) return;

    // Set up smart input system
    setupSmartInput();

    // Set up basic command input handlers
    commandInput.addEventListener('keydown', handleKeyDown);

    // Set up emoji click handlers
    document.querySelectorAll('.emoji-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const title = this.getAttribute('title');
            const emoji = this.textContent;

            console.log(`🎯 Emoji clicked: ${emoji} (${title})`);

            // Special handling for control emojis
            if (title === 'DISPLAY SIZE') {
                cycleDisplaySize();
            } else if (title === 'FONT') {
                cycleFont();
            } else if (title === 'DARK/LIGHT') {
                toggleTheme();
            } else if (title === 'MARKDOWN') {
                toggleMarkdown();
            } else {
                // Handle system module emojis by executing the title as command
                executeCommand(title.toLowerCase());
            }
        });
    });

    // Set up dashboard icon handlers
    document.querySelectorAll('.dashboard-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const title = this.getAttribute('title');
            if (title) {
                selectModule(title);
            }
        });
    });

    console.log('✅ Event listeners configured');
}

function handleKeyDown(e) {
    const input = e.target;

    // Don't handle if smart suggestions are visible (they handle their own keys)
    if (smartInput.isVisible && ['ArrowUp', 'ArrowDown', 'Tab', 'Escape'].includes(e.key)) {
        return; // Let smart input handle these
    }

    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            if (smartInput.selectedIndex < smartInput.suggestions.length - 1) {
                smartInput.selectedIndex++;
                highlightSuggestion(smartInput.selectedIndex);
            }
            break;

        case 'ArrowUp':
            e.preventDefault();
            if (smartInput.selectedIndex > 0) {
                smartInput.selectedIndex--;
                highlightSuggestion(smartInput.selectedIndex);
            }
            break;

        case 'Tab':
        case 'Enter':
            if (smartInput.selectedIndex >= 0) {
                e.preventDefault();
                selectSuggestion(smartInput.selectedIndex);
            }
            break;

        default:
            handleHistoryNavigation(e);
    }
}

// Navigation is now handled by smart input system

// =============================================================================
// INITIALIZATION
// =============================================================================

function initializeUDOS() {
    console.log('🚀 Initializing uDOS Universal Code Interface...');

    // Load uMEMORY system resources first
    loadMemorySystemResources().then(resourcesLoaded => {
        console.log(`🧠 uMEMORY resources: ${resourcesLoaded ? 'loaded' : 'fallback mode'}`);

        // Apply default settings
        applyTheme(udosApp.currentTheme);
        changeFont(udosApp.currentFont);
        changeDisplaySize(udosApp.currentDisplaySize);

        // Set up event listeners
        setupEventListeners();

        // Update prompt
        updatePrompt();

        // Show enhanced startup graphics with uMEMORY integration
        showEnhancedStartupGraphics();

        console.log('✅ uDOS initialization complete');
    });
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeUDOS);
} else {
    initializeUDOS();
}

// Global functions for emoji buttons (backward compatibility)
window.cycleFont = cycleFont;
window.cycleDisplaySize = cycleDisplaySize;
window.toggleTheme = toggleTheme;
window.executeEmojiCommand = executeEmojiCommand;

// Additional UI functions for icon compatibility
window.selectModule = function (moduleName) {
    addToTerminal(`🔧 Loading ${moduleName} module...`, 'info');
    executeCommand(moduleName.toLowerCase());
};

window.setTheme = function (themeName) {
    addToTerminal(`🎨 Switching to ${themeName} theme...`, 'info');
    if (themeName === 'professional' || themeName === 'udos_final') {
        applyTheme('udos_final');
    } else {
        applyTheme(themeName);
    }
};

window.clearTerminal = clearTerminal;
window.showHelp = function () {
    executeCommand('help');
};

window.toggleHistory = function () {
    executeCommand('history');
};

window.toggleMarkdown = function () {
    const current = document.getElementById('markdown-stat')?.textContent || 'OFF';
    const newMode = current === 'OFF' ? 'on' : 'off';
    addToTerminal(`📝 Markdown mode: ${newMode.toUpperCase()}`, 'info');
    if (document.getElementById('markdown-stat')) {
        document.getElementById('markdown-stat').textContent = newMode.toUpperCase();
    }
};
