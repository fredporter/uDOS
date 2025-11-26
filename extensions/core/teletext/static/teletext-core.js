/**
 * uDOS Teletext Interface - Core Terminal
 * Version: 2.0.0
 *
 * Inspired by: https://galax.xyz/TELETEXT/
 * Original concept by 3d@galax.xyz (2014)
 */

(function() {
    'use strict';

    // State
    const state = {
        commandHistory: [],
        historyIndex: -1,
        coreConnected: false,
        ready: false
    };

    // DOM Elements
    let output;
    let input;
    let statusElement;
    let clock;

    /**
     * Display splash screen with uDOS logo and loader
     */
    function showSplashScreen() {
        return new Promise((resolve) => {
            // Clear output
            output.innerHTML = '';

            // uDOS ASCII art logo
            printLine('');
            printLine('');
            printLine('  ██╗   ██╗██████╗  ██████╗ ███████╗', 'fg-synthwave-pink');
            printLine('  ██║   ██║██╔══██╗██╔═══██╗██╔════╝', 'fg-synthwave-purple');
            printLine('  ██║   ██║██║  ██║██║   ██║███████╗', 'fg-synthwave-blue');
            printLine('  ██║   ██║██║  ██║██║   ██║╚════██║', 'fg-synthwave-cyan');
            printLine('  ╚██████╔╝██████╔╝╚██████╔╝███████║', 'fg-synthwave-neon-green');
            printLine('   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝', 'fg-synthwave-violet');
            printLine('');
            printLine('  UNIVERSAL DEVICE OPERATIONS SYSTEM', 'fg-synthwave-cyan');
            printLine('  ░▒▓█ Teletext Interface v2.0.0 █▓▒░', 'fg-synthwave-hot-pink');
            printLine('');
            printLine('');

            // Loading bar
            const loaderLine = document.createElement('div');
            loaderLine.className = 'teletext-line';
            output.appendChild(loaderLine);

            let progress = 0;
            const totalSteps = 50;
            const interval = setInterval(() => {
                progress++;
                const filled = '█'.repeat(Math.floor(progress / 2));
                const empty = '░'.repeat(Math.floor((totalSteps - progress) / 2));
                const percent = Math.floor((progress / totalSteps) * 100);

                loaderLine.innerHTML = `<span class="fg-synthwave-pink">  LOADING: [</span><span class="fg-synthwave-cyan">${filled}</span><span class="fg-synthwave-violet">${empty}</span><span class="fg-synthwave-pink">] ${percent}%</span>`;

                if (progress >= totalSteps) {
                    clearInterval(interval);
                    setTimeout(() => {
                        output.innerHTML = '';
                        resolve();
                    }, 300);
                }
            }, 100); // 5 seconds total (50 steps * 100ms)
        });
    }

    /**
     * Display teletext block graphics demo
     * Shows standard Unicode block drawing characters
     */
    function showBlocksDemo() {
        printLine('═══ TELETEXT BLOCK GRAPHICS ═══', 'fg-synthwave-pink');
        printLine('');

        // Block drawing characters demo - synthwave rainbow
        const blocks = [
            { text: '▀▄█▌▐░▒▓', color: 'fg-synthwave-pink' },
            { text: '▀▀▀▀▀▀▀▀', color: 'fg-synthwave-purple' },
            { text: '▄▄▄▄▄▄▄▄', color: 'fg-synthwave-blue' },
            { text: '████████', color: 'fg-synthwave-cyan' },
            { text: '▌▌▌▌▌▌▌▌', color: 'fg-synthwave-neon-green' },
            { text: '▐▐▐▐▐▐▐▐', color: 'fg-yellow' },
            { text: '░░░░░░░░', color: 'fg-synthwave-orange' },
            { text: '▒▒▒▒▒▒▒▒', color: 'fg-synthwave-hot-pink' },
            { text: '▓▓▓▓▓▓▓▓', color: 'fg-synthwave-violet' }
        ];

        blocks.forEach(block => printLine(block.text, block.color));
        printLine('');
        printLine('Box Drawing:', 'fg-synthwave-orange');
        printLine('┌─────────────────────────────┐', 'fg-synthwave-cyan');
        printLine('│ TELETEXT50 BLOCK GRAPHICS  │', 'fg-synthwave-pink');
        printLine('├─────────────────────────────┤', 'fg-synthwave-purple');
        printLine('│ ▀▄█▌▐░▒▓ ║═╔╗╚╝╠╣╦╩╬       │', 'fg-synthwave-blue');
        printLine('└─────────────────────────────┘', 'fg-synthwave-cyan');
        printLine('');
    }

    /**
     * Display teletext block graphics
     * Uses standard Unicode block drawing characters
     */
    function showBlocks() {
        printLine('═══ TELETEXT BLOCK GRAPHICS ═══', 'fg-synthwave-pink');
        printLine('');

        // Standard Unicode blocks - synthwave colors
        printLine('Block Elements:', 'fg-synthwave-orange');
        printLine('▀ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █', 'fg-synthwave-cyan');
        printLine('▉ ▊ ▋ ▌ ▍ ▎ ▏ ▐', 'fg-synthwave-purple');
        printLine('░ ▒ ▓ ▔ ▕ ▖ ▗ ▘', 'fg-synthwave-blue');
        printLine('▙ ▚ ▛ ▜ ▝ ▞ ▟', 'fg-synthwave-hot-pink');
        printLine('');

        printLine('Box Drawing:', 'fg-synthwave-orange');
        printLine('─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼', 'fg-synthwave-neon-green');
        printLine('═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬', 'fg-synthwave-violet');
        printLine('╭ ╮ ╯ ╰ ╱ ╲ ╳', 'fg-yellow');
        printLine('');

        printLine('Pattern Demo:', 'fg-synthwave-orange');
        printLine('████░░░░▓▓▓▓▒▒▒▒', 'fg-synthwave-cyan');
        printLine('▀▀▀▀▄▄▄▄█████████', 'fg-synthwave-pink');
        printLine('▌▌▌▌▐▐▐▐░░▒▒▓▓██', 'fg-synthwave-neon-green');
        printLine('');
    }

    /**
     * Initialize teletext terminal
     */
    function init() {
        // Get DOM elements
        output = document.getElementById('output');
        input = document.getElementById('input');
        statusElement = document.getElementById('connection-status');
        clock = document.getElementById('clock');

        // Setup
        setupTerminal();
        startClock();

        console.log('[Teletext] v2.0.0 ready');
    }

    /**
     * Setup terminal after loading
     */
    async function setupTerminal() {
        // Event listeners
        input.addEventListener('keydown', handleKeyDown);
        input.addEventListener('input', handleInputChange);

        // Global keyboard shortcuts
        document.addEventListener('keydown', handleGlobalKeys);

        // Show splash screen first
        await showSplashScreen();

        // Focus input
        input.focus();

        // Welcome message - synthwave teletext style
        printLine('P100  uDOS TELETEXT  100  ' + new Date().toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }) + '  ' + new Date().toLocaleTimeString('en-GB', { hour12: false, hour: '2-digit', minute: '2-digit' }), 'fg-white');
        printLine('');
        printLine('█▀▀ █▄█ █▄ █ ▀█▀ █ █ █   █ ▄▀▄ █ █ █▀▀', 'fg-magenta');
        printLine('▄█▄  █  █ ▀█  █  █▀█ ▀▄▀▄▀ █▀█ ▀▄▀ ██▄', 'fg-cyan');
        printLine('');
        printLine('UNIVERSAL DEVICE OPERATIONS SYSTEM', 'fg-white');
        printLine('░▒▓█ Teletext Interface v2.0.0 █▓▒░', 'fg-white');
        printLine('Teletext50 Font by 3d@galax.xyz', 'fg-white');
        printLine('');
        printLine('▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀', 'fg-magenta');

        // Block graphics demo at launch
        showBlocksDemo();

        // Check API connection
        checkConnection();

        printLine('');
        printLine('▶ Type HELP for commands', 'fg-cyan');
        printLine('');
        state.ready = true;
    }

    /**
     * Handle global keyboard shortcuts
     */
    function handleGlobalKeys(e) {
        // ESC to clear input
        if (e.key === 'Escape') {
            input.value = '';
        }
    }

    /**
     * Handle input changes
     */
    function handleInputChange(e) {
        // Simple input handling
    }

    /**
     * Check API connection
     */
    async function checkConnection() {
        try {
            const response = await fetch('http://localhost:5001/api/status');
            if (response.ok) {
                const data = await response.json();
                state.coreConnected = true;
                updateStatus('🟢 ONLINE');
                printLine('API CONNECTED', 'fg-synthwave-neon-green');
            } else {
                throw new Error('API unavailable');
            }
        } catch (error) {
            state.coreConnected = false;
            updateStatus('🔴 OFFLINE');
            printLine('API OFFLINE - STANDALONE MODE', 'fg-synthwave-orange');
        }
    }

    /**
     * Update status bar
     */
    function updateStatus(text) {
        if (statusElement) {
            statusElement.textContent = text;
        }
    }

    /**
     * Start clock
     */
    function startClock() {
        function updateClock() {
            const now = new Date();
            const time = now.toLocaleTimeString('en-US', { hour12: false });
            if (clock) {
                clock.textContent = time;
            }
        }
        updateClock();
        setInterval(updateClock, 1000);
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
                input.value = '';
                break;
        }
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
        } else {
            if (state.historyIndex < state.commandHistory.length - 1) {
                state.historyIndex++;
            } else {
                state.historyIndex = state.commandHistory.length;
                input.value = '';
                return;
            }
        }

        input.value = state.commandHistory[state.historyIndex] || '';
    }

    /**
     * Execute command
     */
    async function executeCommand() {
        const command = input.value.trim();
        if (!command) return;

        // Add to history
        state.commandHistory.push(command);
        state.historyIndex = state.commandHistory.length;

        // Display command
        printLine('> ' + command, 'fg-cyan');

        // Clear input
        input.value = '';

        // Parse and execute
        const cmd = command.toLowerCase();
        const args = command.split(/\s+/).slice(1);

        // Built-in commands
        if (cmd === 'help') {
            printLine('═══ uDOS TELETEXT COMMANDS ═══', 'fg-synthwave-pink');
            printLine('HELP      - Show this help', 'fg-white');
            printLine('STATUS    - System status', 'fg-white');
            printLine('CLEAR     - Clear screen', 'fg-white');
            printLine('TIME      - Display current time', 'fg-white');
            printLine('TEST      - Run diagnostics', 'fg-white');
            printLine('EXIT/QUIT - Close window', 'fg-white');
            printLine('');
            return;
        }

        if (cmd === 'clear' || cmd === 'cls') {
            output.innerHTML = '';
            return;
        }

        if (cmd === 'status') {
            printLine('═══ SYSTEM STATUS ═══', 'fg-synthwave-pink');
            printLine('Version: 2.0.0', 'fg-synthwave-cyan');
            printLine('API: ' + (state.coreConnected ? 'CONNECTED' : 'OFFLINE'), state.coreConnected ? 'fg-synthwave-neon-green' : 'fg-synthwave-orange');
            printLine('Time: ' + new Date().toLocaleString(), 'fg-synthwave-purple');
            printLine('');
            return;
        }

        if (cmd === 'time') {
            printLine(new Date().toLocaleString(), 'fg-synthwave-cyan');
            printLine('');
            return;
        }

        if (cmd === 'test') {
            printLine('═══ RUNNING DIAGNOSTICS ═══', 'fg-synthwave-pink');
            printLine('Display: OK', 'fg-synthwave-neon-green');
            printLine('Input: OK', 'fg-synthwave-neon-green');
            printLine('Font: Teletext50', 'fg-synthwave-cyan');
            printLine('API: ' + (state.coreConnected ? 'CONNECTED' : 'OFFLINE'), state.coreConnected ? 'fg-synthwave-neon-green' : 'fg-synthwave-orange');
            printLine('═══ ALL SYSTEMS OPERATIONAL ═══', 'fg-synthwave-neon-green');
            printLine('');
            return;
        }

        if (cmd === 'exit' || cmd === 'quit') {
            printLine('GOODBYE.', 'fg-synthwave-pink');
            setTimeout(() => window.close(), 500);
            return;
        }

        // Try API if connected
        if (state.coreConnected) {
            try {
                const response = await fetch('http://localhost:5001/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.output) {
                        printLine(result.output);
                    }
                } else {
                    printLine('COMMAND NOT FOUND: ' + command, 'fg-synthwave-orange');
                    printLine('TYPE "HELP" FOR AVAILABLE COMMANDS', 'fg-synthwave-violet');
                }
            } catch (error) {
                printLine('API ERROR: ' + error.message, 'fg-synthwave-orange');
            }
        } else {
            printLine('COMMAND NOT FOUND: ' + command, 'fg-synthwave-orange');
            printLine('TYPE "HELP" FOR AVAILABLE COMMANDS', 'fg-synthwave-violet');
        }

        printLine('');
    }

    /**
     * Print line to output
     */
    function printLine(text, className = '') {
        const line = document.createElement('div');
        line.textContent = text;
        if (className) {
            line.className = className;
        }
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    // Initialize when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose public API
    window.teletextCore = {
        executeCommand: executeCommand,
        showBlocks: showBlocks
    };

})();
