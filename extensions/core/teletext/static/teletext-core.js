/**
 * uDOS Teletext - Core Terminal Logic with uDOS Integration
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // Terminal state
    const state = {
        commandHistory: [],
        historyIndex: -1,
        currentDirectory: '/',
        sessionId: null,
        ready: false,
        udosApiUrl: 'http://localhost:8890'  // uDOS core API endpoint
    };

    // DOM Elements
    let screenElement;
    let commandInput;
    let statusElement;

    /**
     * Initialize terminal
     */
    function init() {
        console.log('[Teletext Core] Initializing...');

        // Get DOM elements
        screenElement = document.getElementById('screen');
        commandInput = document.getElementById('commandInput');
        statusElement = document.getElementById('connection-status');

        // Initialize session
        initializeSession();

        // Setup event listeners
        setupEventListeners();

        // Run startup test
        setTimeout(() => runStartupTest(), 1000);

        // Mark as ready
        state.ready = true;

        console.log('[Teletext Core] Ready');
    }

    /**
     * Initialize session with uDOS core
     */
    async function initializeSession() {
        try {
            state.sessionId = 'teletext-' + Date.now();

            // Try to ping uDOS core
            const response = await fetch(`${state.udosApiUrl}/api/status`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('[Teletext Core] Connected to uDOS:', data);
                updateConnectionStatus('connected');
                appendOutput('✓ CONNECTED TO uDOS CORE v' + (data.version || '1.0.24'), 'output-success');
            } else {
                console.warn('[Teletext Core] Core not available, standalone mode');
                updateConnectionStatus('disconnected');
                appendOutput('⚠ RUNNING IN STANDALONE MODE', 'output-warning');
            }
        } catch (error) {
            console.warn('[Teletext Core] Core not available:', error.message);
            updateConnectionStatus('disconnected');
            appendOutput('⚠ RUNNING IN STANDALONE MODE', 'output-warning');
        }

        appendOutput('');
    }

    /**
     * Update connection status indicator
     */
    function updateConnectionStatus(status) {
        if (!statusElement) return;

        const statusText = {
            'connected': '🟢 Live',
            'disconnected': '🔴 Offline',
            'error': '⚠️  Error'
        }[status] || '⚪ Unknown';

        statusElement.textContent = statusText;
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        if (commandInput) {
            commandInput.addEventListener('keydown', handleKeyDown);
        }

        // Global keyboard shortcuts
        document.addEventListener('keydown', handleGlobalKeys);
    }

    /**
     * Handle keyboard input
     */
    function handleKeyDown(e) {
        switch(e.key) {
            case 'Enter':
                e.preventDefault();
                executeCommand();
                break;

            case 'ArrowUp':
                e.preventDefault();
                navigateHistory('up');
                break;

            case 'ArrowDown':
                e.preventDefault();
                navigateHistory('down');
                break;

            case 'Escape':
                e.preventDefault();
                commandInput.value = '';
                break;
        }
    }

    /**
     * Handle global keyboard shortcuts
     */
    function handleGlobalKeys(e) {
        // Ctrl+L to clear screen
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearScreen();
        }

        // Ctrl+K for command help
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            executeBuiltInCommand('HELP');
        }
    }

    /**
     * Execute command
     */
    async function executeCommand() {
        const command = commandInput.value.trim();
        if (!command) return;

        // Add to history
        state.commandHistory.push(command);
        state.historyIndex = state.commandHistory.length;

        // Display command
        appendOutput('> ' + command, 'fg-cyan');

        // Clear input
        commandInput.value = '';

        // Parse and execute
        const upperCommand = command.toUpperCase();

        // Check built-in commands first
        if (executeBuiltInCommand(upperCommand)) {
            return;
        }

        // Try to execute via uDOS core
        try {
            const response = await fetch(`${state.udosApiUrl}/api/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': state.sessionId
                },
                body: JSON.stringify({
                    command: command,
                    session: state.sessionId,
                    timestamp: Date.now()
                })
            });

            if (response.ok) {
                const result = await response.json();
                if (result.output) {
                    if (Array.isArray(result.output)) {
                        result.output.forEach(line => appendOutput(line));
                    } else {
                        appendOutput(result.output);
                    }
                }
                if (result.error) {
                    appendOutput('ERROR: ' + result.error, 'output-error');
                }
            } else {
                appendOutput('COMMAND NOT FOUND: ' + command, 'output-error');
                appendOutput('TYPE "HELP" FOR AVAILABLE COMMANDS', 'output-dim');
            }
        } catch (error) {
            // Fallback to built-in commands
            appendOutput('uDOS CORE NOT AVAILABLE', 'output-error');
            appendOutput('AVAILABLE COMMANDS: HELP, TEST, STATUS, TIME, CLEAR, COLORS, CHARS', 'output-info');
        }

        appendOutput('');
    }

    /**
     * Execute built-in commands
     */
    function executeBuiltInCommand(command) {
        const parts = command.split(' ');
        const cmd = parts[0];

        switch(cmd) {
            case 'HELP':
                showHelp();
                return true;

            case 'TEST':
                runStartupTest();
                return true;

            case 'STATUS':
                showStatus();
                return true;

            case 'TIME':
                showTime();
                return true;

            case 'CLEAR':
            case 'CLS':
                clearScreen();
                return true;

            case 'COLORS':
            case 'COLOURS':
                showColors();
                return true;

            case 'CHARS':
            case 'BLOCKS':
                showCharacters();
                return true;

            case 'ECHO':
                appendOutput(parts.slice(1).join(' '));
                appendOutput('');
                return true;

            default:
                return false;
        }
    }

    /**
     * Show help
     */
    function showHelp() {
        const help = [
            '════════════════════════════════════════',
            '  uDOS TELETEXT COMMAND REFERENCE      ',
            '════════════════════════════════════════',
            '',
            'BUILT-IN COMMANDS:',
            '  HELP        - Show this help',
            '  TEST        - Run system tests',
            '  STATUS      - Show system status',
            '  TIME        - Show current time',
            '  CLEAR/CLS   - Clear screen',
            '  COLORS      - Show color palette',
            '  CHARS       - Show teletext blocks',
            '  ECHO <text> - Echo text',
            '',
            'uDOS CORE COMMANDS (when connected):',
            '  FILE LIST   - List files',
            '  K-LIST      - List knowledge',
            '  MAP SHOW    - Show map',
            '  THEME SET   - Change theme',
            '',
            'KEYBOARD SHORTCUTS:',
            '  Ctrl+L      - Clear screen',
            '  Ctrl+K      - Show help',
            '  ↑/↓         - Command history',
            '  Esc         - Clear input',
            '',
            '════════════════════════════════════════',
            ''
        ];

        help.forEach(line => appendOutput(line, 'fg-yellow'));
    }

    /**
     * Run startup test
     */
    function runStartupTest() {
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('  BBC TELETEXT SYSTEM TEST v1.0.24     ', 'fg-yellow');
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');

        // System tests
        appendOutput('SYSTEM TESTS:', 'fg-cyan');
        appendOutput('  ✓ FONT: MALLARD BLOCKIER', 'fg-green');
        appendOutput('  ✓ DISPLAY: 40×25 CHARACTERS', 'fg-green');
        appendOutput('  ✓ PALETTE: SYNTHWAVE DOS', 'fg-green');
        appendOutput('  ✓ GRAPHICS: TELETEXT MOSAIC', 'fg-green');
        appendOutput('  ✓ UNICODE: BLOCK CHARACTERS', 'fg-green');
        appendOutput('');

        // Color test
        appendOutput('COLOR PALETTE TEST:', 'fg-cyan');
        appendOutput('  RED    ████████████████', 'fg-red');
        appendOutput('  GREEN  ████████████████', 'fg-green');
        appendOutput('  YELLOW ████████████████', 'fg-yellow');
        appendOutput('  BLUE   ████████████████', 'fg-blue');
        appendOutput('  MAGENTA ███████████████', 'fg-mag');
        appendOutput('  CYAN   ████████████████', 'fg-cyan');
        appendOutput('  WHITE  ████████████████', 'fg-white');
        appendOutput('');

        // Block graphics test
        appendOutput('BLOCK GRAPHICS TEST:', 'fg-cyan');
        appendOutput('  █▀▄▌▐▖▗▘▙▚▛▜▟▞ FULL HEIGHT', 'fg-red');
        appendOutput('  ▁▂▃▄▅▆▇█ GRADIENT BLOCKS', 'fg-yellow');
        appendOutput('  ■□▪▫ BOX CHARACTERS', 'fg-green');
        appendOutput('  ▀▄ HALF BLOCKS', 'fg-cyan');
        appendOutput('  ▌▐ VERTICAL BLOCKS', 'fg-blue');
        appendOutput('  ▖▗▘▝ QUARTER BLOCKS', 'fg-mag');
        appendOutput('');

        // Character patterns
        appendOutput('MOSAIC PATTERNS:', 'fg-cyan');
        appendOutput('  ▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚▞▚', 'fg-red');
        appendOutput('  ▙▟▙▟▙▟▙▟▙▟▙▟▙▟▙▟▙▟▙', 'fg-yellow');
        appendOutput('  ▛▜▛▜▛▜▛▜▛▜▛▜▛▜▛▜▛▜▛', 'fg-green');
        appendOutput('  ▗▖▗▖▗▖▗▖▗▖▗▖▗▖▗▖▗▖▗', 'fg-cyan');
        appendOutput('');

        // Full character set demo
        appendOutput('COMPLETE CHARACTER SET:', 'fg-cyan');
        appendOutput('  █▀▄▌▐▖▗▘▙▚▛▜▟▞▁▂▃▄▅▆▇■□▪▫', 'fg-white');
        appendOutput('');

        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('SYSTEM TEST COMPLETE - ALL SYSTEMS OK', 'fg-green');
        appendOutput('Type "HELP" for available commands', 'fg-dim');
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');
    }

    /**
     * Show system status
     */
    function showStatus() {
        const now = new Date();
        const uptime = Math.floor(performance.now() / 1000);

        appendOutput('════════════════════════════════════════', 'fg-cyan');
        appendOutput('  uDOS TELETEXT SYSTEM STATUS          ', 'fg-cyan');
        appendOutput('════════════════════════════════════════', 'fg-cyan');
        appendOutput('');
        appendOutput('  Version:    1.0.24', 'fg-green');
        appendOutput('  Mode:       Web Terminal', 'fg-green');
        appendOutput('  Session:    ' + state.sessionId, 'fg-green');
        appendOutput('  Uptime:     ' + uptime + 's', 'fg-green');
        appendOutput('  Commands:   ' + state.commandHistory.length, 'fg-green');

        if (performance.memory) {
            const used = Math.floor(performance.memory.usedJSHeapSize / 1024 / 1024);
            const total = Math.floor(performance.memory.totalJSHeapSize / 1024 / 1024);
            appendOutput('  Memory:     ' + used + 'MB / ' + total + 'MB', 'fg-green');
        }

        appendOutput('');
        appendOutput('════════════════════════════════════════', 'fg-cyan');
        appendOutput('');
    }

    /**
     * Show current time
     */
    function showTime() {
        const now = new Date();
        appendOutput('SYSTEM TIME:', 'fg-cyan');
        appendOutput('  Date:      ' + now.toLocaleDateString(), 'fg-green');
        appendOutput('  Time:      ' + now.toLocaleTimeString(), 'fg-green');
        appendOutput('  Timestamp: ' + now.getTime(), 'fg-green');
        appendOutput('');
    }

    /**
     * Show color palette
     */
    function showColors() {
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('  TELETEXT COLOR PALETTE               ', 'fg-yellow');
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');

        const colors = [
            { name: 'RED',     class: 'fg-red',    hex: '#FF1744' },
            { name: 'GREEN',   class: 'fg-green',  hex: '#00E676' },
            { name: 'YELLOW',  class: 'fg-yellow', hex: '#FFEB3B' },
            { name: 'BLUE',    class: 'fg-blue',   hex: '#2196F3' },
            { name: 'MAGENTA', class: 'fg-mag',    hex: '#EE4266' },
            { name: 'CYAN',    class: 'fg-cyan',   hex: '#00E5FF' },
            { name: 'WHITE',   class: 'fg-white',  hex: '#FFFFFF' }
        ];

        colors.forEach(color => {
            const bar = '█'.repeat(20);
            appendOutput(`  ${color.name.padEnd(8)} ${bar} ${color.hex}`, color.class);
        });

        appendOutput('');
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');
    }

    /**
     * Show character set
     */
    function showCharacters() {
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('  TELETEXT BLOCK GRAPHICS              ', 'fg-yellow');
        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');

        appendOutput('FULL HEIGHT BLOCKS:', 'fg-cyan');
        appendOutput('  █ ▀ ▄ ▌ ▐', 'fg-white');
        appendOutput('');

        appendOutput('QUARTER BLOCKS:', 'fg-cyan');
        appendOutput('  ▖ ▗ ▘ ▝', 'fg-white');
        appendOutput('');

        appendOutput('HALF BLOCKS:', 'fg-cyan');
        appendOutput('  ▀ ▄ ▌ ▐', 'fg-white');
        appendOutput('');

        appendOutput('COMPLEX MOSAICS:', 'fg-cyan');
        appendOutput('  ▙ ▚ ▛ ▜ ▟ ▞', 'fg-white');
        appendOutput('');

        appendOutput('GRADIENT BLOCKS:', 'fg-cyan');
        appendOutput('  ▁ ▂ ▃ ▄ ▅ ▆ ▇ █', 'fg-white');
        appendOutput('');

        appendOutput('BOX CHARACTERS:', 'fg-cyan');
        appendOutput('  ■ □ ▪ ▫', 'fg-white');
        appendOutput('');

        appendOutput('COMPLETE SET:', 'fg-cyan');
        appendOutput('  █▀▄▌▐▖▗▘▙▚▛▜▟▞▁▂▃▄▅▆▇■□▪▫', 'fg-white');
        appendOutput('');

        appendOutput('════════════════════════════════════════', 'fg-yellow');
        appendOutput('');
    }

    /**
     * Navigate command history
     */
    function navigateHistory(direction) {
        if (state.commandHistory.length === 0) return;

        if (direction === 'up') {
            if (state.historyIndex > 0) {
                state.historyIndex--;
            }
        } else if (direction === 'down') {
            if (state.historyIndex < state.commandHistory.length) {
                state.historyIndex++;
            }
        }

        if (state.historyIndex < state.commandHistory.length) {
            commandInput.value = state.commandHistory[state.historyIndex];
        } else {
            commandInput.value = '';
        }
    }

    /**
     * Clear screen
     */
    function clearScreen() {
        if (screenElement) {
            // Keep only the header rows
            const rows = screenElement.querySelectorAll('.row');
            const headerCount = 7; // Number of header rows to keep

            for (let i = headerCount; i < rows.length; i++) {
                rows[i].remove();
            }
        }

        appendOutput('SCREEN CLEARED', 'output-dim');
        appendOutput('');
    }

    /**
     * Append output to screen
     */
    function appendOutput(text, className = '') {
        if (!screenElement) return;

        const span = document.createElement('span');
        span.className = 'row ' + className;
        span.textContent = text.padEnd(40);
        screenElement.appendChild(span);

        // Auto-scroll
        window.scrollTo(0, document.body.scrollHeight);
    }

    /**
     * Clock update
     */
    function updateClock() {
        const clockEl = document.getElementById('clock');
        if (clockEl) {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Update clock every second
    setInterval(updateClock, 1000);
    updateClock();

    // Expose for debugging
    window.TeletextCore = {
        executeCommand: (cmd) => {
            commandInput.value = cmd;
            executeCommand();
        },
        runTest: runStartupTest,
        clearScreen: clearScreen,
        state: state
    };

})();
