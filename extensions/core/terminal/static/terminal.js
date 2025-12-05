/**
 * uDOS Terminal v2.0.0 - JavaScript
 * Clean rebuild with uDOS API integration
 */

(function() {
    'use strict';

    // Terminal state
    const state = {
        commandHistory: [],
        historyIndex: -1,
        ready: false,
        coreConnected: false,
        udosApiUrl: 'http://localhost:5001/api'
    };

    // Syntax highlighting patterns (uPY style)
    const syntaxPatterns = {
        command: /\b([A-Z][A-Z_]*)\s*\(/g,              // COMMAND(
        function: /\b([a-z_][a-z0-9_]*)\s*\(/g,         // function(
        string: /(["'])(?:(?=(\\?))\2.)*?\1/g,         // "string" or 'string'
        comment: /#.*$/gm,                              // # comment
        number: /\b\d+\.?\d*\b/g,                      // 123 or 123.45
        variable: /\$[A-Z_][A-Z0-9_.]*/g,               // $VARIABLE or $VAR.PROP
        operator: /[+\-*/=<>!&|]+/g,                    // operators
        bracket: /[\(\)\[\]\{\}]/g,                    // brackets
        separator: /[,;:]/g                             // separators
    };

    // Color utilities (inline color support like teletext)
    const colors = {
        cyan: '#00d4ff',
        green: '#50b818',
        yellow: '#f0e858',
        red: '#e94560',
        purple: '#9d4edd',
        pink: '#ff006e',
        white: '#f1f1f1',
        gray: '#a0a0a0',
        blue: '#181090'
    };

    /**
     * Colorize text with inline color tags
     * Supports: {cyan:text}, {green:text}, {yellow:text}, etc.
     */
    function colorize(text) {
        const colorPattern = /\{(cyan|green|yellow|red|purple|pink|white|gray|blue):([^}]+)\}/g;
        return text.replace(colorPattern, (match, color, content) => {
            return `<span style="color: ${colors[color]}; font-weight: bold;">${content}</span>`;
        });
    }

    // DOM Elements
    let terminal, output, input, loadingScreen, functionKeys;

    /**
     * Show splash screen with uDOS logo and loader
     */
    function showSplashScreen() {
        return new Promise((resolve) => {
            const loadingScreen = document.getElementById('loadingScreen');
            loadingScreen.innerHTML = '';

            // Create splash content
            const splash = document.createElement('div');
            splash.style.cssText = 'text-align: center; padding: 20px; font-family: "C64 User Mono", monospace; line-height: 1.2;';

            // uDOS logo in C64 block graphics (rainbow gradient)
            const logo = [
                { text: '  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄', color: '#FF0000' },
                { text: '  █ █  █ ████   ███   ███                              █', color: '#FF4500' },
                { text: '  █ █  █ █   █ █   █ █                                 █', color: '#FF8C00' },
                { text: '  █ █  █ █   █ █   █  ██                               █', color: '#FFD700' },
                { text: '  █ █  █ █   █ █   █    █                              █', color: '#ADFF2F' },
                { text: '  █ █  █ █   █ █   █ █  █  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█', color: '#00FF00' },
                { text: '  █  ██  ████   ███   ██   █ UNIVERSAL DEVICE OPS █    █', color: '#00CED1' },
                { text: '  █                         █    SYSTEM v2.0.0    █    █', color: '#00BFFF' },
                { text: '  █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█', color: '#9370DB' },
                { text: '', color: '#FF00FF' }
            ];

            logo.forEach(line => {
                const lineDiv = document.createElement('div');
                lineDiv.textContent = line.text;
                lineDiv.style.color = line.color;
                lineDiv.style.fontWeight = 'bold';
                splash.appendChild(lineDiv);
            });

            // Loading bar container
            const loaderContainer = document.createElement('div');
            loaderContainer.style.cssText = 'margin: 30px auto; width: 400px;';

            const loaderText = document.createElement('div');
            loaderText.textContent = '▶ INITIALIZING SYSTEM...';
            loaderText.style.cssText = 'color: #00D9FF; margin-bottom: 10px; font-weight: bold;';
            loaderContainer.appendChild(loaderText);

            const progressBar = document.createElement('div');
            progressBar.style.cssText = 'font-family: monospace; color: #FD79A8; font-size: 14px;';
            loaderContainer.appendChild(progressBar);

            const statusText = document.createElement('div');
            statusText.style.cssText = 'color: #50b818; margin-top: 10px; font-size: 12px;';
            loaderContainer.appendChild(statusText);

            splash.appendChild(loaderContainer);
            loadingScreen.appendChild(splash);

            // Animate loader with status messages
            let progress = 0;
            const totalSteps = 40;
            const statusMessages = [
                'LOADING KERNEL...',
                'INITIALIZING MEMORY...',
                'MOUNTING FILESYSTEMS...',
                'LOADING EXTENSIONS...',
                'CONNECTING TO CORE...',
                'READY TO OPERATE'
            ];
            let statusIndex = 0;

            const interval = setInterval(() => {
                progress++;
                const filled = '█'.repeat(Math.floor(progress * 0.6));
                const empty = '░'.repeat(Math.floor((totalSteps - progress) * 0.6));
                const percent = Math.floor((progress / totalSteps) * 100);

                progressBar.textContent = `[${filled}${empty}] ${percent}%`;

                // Update status message
                if (progress % 7 === 0 && statusIndex < statusMessages.length) {
                    statusText.textContent = '▸ ' + statusMessages[statusIndex];
                    statusIndex++;
                }

                if (progress >= totalSteps) {
                    clearInterval(interval);
                    statusText.textContent = '✓ SYSTEM READY';
                    statusText.style.color = '#00FF00';
                    setTimeout(() => {
                        resolve();
                    }, 500);
                }
            }, 80); // 3.2 seconds total
        });
    }

    /**
     * Initialize
     */
    async function init() {
        // Get elements
        loadingScreen = document.getElementById('loadingScreen');
        terminal = document.getElementById('terminal');
        output = document.getElementById('output');
        input = document.getElementById('input');
        functionKeys = document.getElementById('functionKeys');

        // Show splash screen
        await showSplashScreen();

        // Hide loading, show terminal
        loadingScreen.classList.add('hidden');
        terminal.classList.add('active');
        setupTerminal();
    }

    /**
     * Setup terminal after loading
     */
    function setupTerminal() {
        // Event listeners
        input.addEventListener('keydown', handleKeyDown);
        input.addEventListener('input', handleInputChange);

        // Function key handlers
        functionKeys.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => handleFunctionKey(btn.dataset.key));
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', handleGlobalKeys);

        // Focus input
        input.focus();

        // Welcome message with colors
        printColor('**** uDOS UNIVERSAL DEVICE OPERATIONS ****', 'cyan');
        printColor('TERMINAL MODE v2.0.0', 'purple');
        printLine('');

        // Check API connection
        checkConnection();

        printLine('READY.');
        printLine('');
        state.ready = true;
    }

    /**
     * Handle global keyboard shortcuts
     */
    function handleGlobalKeys(e) {
        // F1-F8 function keys
        if (e.key.startsWith('F') && e.key.length === 2) {
            e.preventDefault();
            handleFunctionKey(e.key.toUpperCase());
        }
    }

    /**
     * Handle input changes for smart suggestions
     */
    function handleInputChange(e) {
        const value = input.value.toLowerCase();
        // Simple autocomplete could be added here
        // For now, just ensure proper input handling
    }

    /**
     * Handle keyboard input
     */
    function handleKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const command = input.value.trim();
            if (command) {
                executeCommand(command);
                state.commandHistory.push(command);
                state.historyIndex = state.commandHistory.length;
            }
            input.value = '';
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (state.historyIndex > 0) {
                state.historyIndex--;
                input.value = state.commandHistory[state.historyIndex] || '';
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (state.historyIndex < state.commandHistory.length) {
                state.historyIndex++;
                input.value = state.commandHistory[state.historyIndex] || '';
            }
        }
    }

    /**
     * Execute command
     */
    async function executeCommand(command) {
        printCommand(command);

        // Local commands
        const cmd = command.toLowerCase();

        if (cmd === 'clear' || cmd === 'cls') {
            output.innerHTML = '';
            return;
        }

        if (cmd === 'help') {
            printColor('AVAILABLE COMMANDS:', 'cyan');
            printLine('{green:  HELP}     - SHOW THIS MESSAGE');
            printLine('{green:  CLEAR}    - CLEAR SCREEN');
            printLine('{green:  STATUS}   - SHOW SYSTEM STATUS');
            printLine('{green:  DEMO}     - SHOW SYNTAX HIGHLIGHTING DEMO');
            printLine('{green:  EXIT}     - CLOSE TERMINAL');
            printLine('');
            printLine('{yellow:USE FUNCTION KEYS FOR QUICK ACCESS}');
            return;
        }

        if (cmd === 'demo') {
            printColor('===== SYNTAX HIGHLIGHTING DEMO =====', 'cyan');
            printLine('');
            printLine('{yellow:uPY COMMAND EXAMPLES:}');
            printLine('');
            printCommand('GUIDE(water)');
            printCommand('SET($LOCATION, "AU-BNE")');
            printCommand('MEMORY STORE("survival_kit", $ITEMS)');
            printCommand('MAP DISPLAY($LOCATION, zoom=5)');
            printCommand('CALC(45 + 67 * 2)');
            printCommand('# This is a comment');
            printLine('');
            printLine('{green:INLINE COLOR EXAMPLES:}');
            printLine('');
            printLine('{cyan:Cyan text} - INFO');
            printLine('{green:Green text} - SUCCESS');
            printLine('{yellow:Yellow text} - WARNING');
            printLine('{red:Red text} - ERROR');
            printLine('{purple:Purple text} - SYSTEM');
            printLine('{pink:Pink text} - HIGHLIGHT');
            printLine('');
            printColor('✓ COLOR SYSTEM ACTIVE', 'green');
            printLine('');
            return;
        }

        if (cmd === 'status') {
            printColor('SYSTEM STATUS:', 'cyan');
            printLine(`{green:TERMINAL:} READY`);
            printLine(`{${state.coreConnected ? 'green' : 'red'}:API:} ${state.coreConnected ? 'CONNECTED' : 'DISCONNECTED'}`);
            printLine(`{purple:HISTORY:} ${state.commandHistory.length} COMMANDS`);
            return;
        }

        if (cmd === 'start') {
            if (state.coreConnected) {
                printLine('STARTING uDOS CORE SYSTEMS...');
                printLine('INITIALIZING KNOWLEDGE BANK...');
                printLine('LOADING EXTENSIONS...');
                printLine('');
                printLine('uCORE READY.');
                printLine('TIP: TYPE "HELP" FOR AVAILABLE COMMANDS');
            } else {
                printLine('UDOS SYSTEMS NOT AVAILABLE');
                printLine('API SERVER REQUIRED FOR FULL FUNCTIONALITY');
                printLine('');
                printLine('START SERVER:');
                printLine('  cd extensions/api && python server.py');
            }
            return;
        }

        if (cmd === 'exit' || cmd === 'quit') {
            printLine('GOODBYE.');
            setTimeout(() => window.close(), 1000);
            return;
        }

        // Try API
        if (state.coreConnected) {
            try {
                const response = await fetch(`${state.udosApiUrl}/command`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command })
                });

                if (response.ok) {
                    const data = await response.json();
                    printLine(data.output || data.message || 'COMMAND EXECUTED');
                    return;
                }
            } catch (error) {
                console.error('[Terminal] API error:', error);
            }
        }

        printLine(`UNKNOWN COMMAND: ${command}`);
        printLine('TYPE "HELP" FOR AVAILABLE COMMANDS');
    }

    /**
     * Handle function keys
     */
    function handleFunctionKey(key) {
        switch(key) {
            case 'F1':
                printLine('===== uDOS HELP SYSTEM =====');
                executeCommand('help');
                break;
            case 'F2':
                printLine('===== KNOWLEDGE BASE =====');
                if (state.coreConnected) {
                    printLine('CATEGORIES: WATER, FIRE, SHELTER, FOOD, MEDICAL, NAVIGATION');
                    printLine('USAGE: KNOW <CATEGORY>');
                } else {
                    printLine('KNOWLEDGE BASE REQUIRES API CONNECTION');
                }
                break;
            case 'F3':
                printLine('===== DIRECTORY LISTING =====');
                if (state.coreConnected) {
                    executeCommand('ls');
                } else {
                    printLine('DIRECTORY ACCESS REQUIRES API CONNECTION');
                }
                break;
            case 'F4':
                printLine('===== EDIT MODE =====');
                printLine('FEATURE IN DEVELOPMENT');
                printLine('COMING SOON: FILE EDITOR');
                break;
            case 'F5':
                printLine('===== RUN SCRIPT =====');
                printLine('FEATURE IN DEVELOPMENT');
                printLine('COMING SOON: uCODE SCRIPT EXECUTION');
                break;
            case 'F6':
                printLine('===== SYSTEM STATUS =====');
                executeCommand('status');
                break;
            case 'F7':
                executeCommand('clear');
                break;
            case 'F8':
                showCharacterMap();
                break;
        }
        input.focus();
    }

    /**
     * Show PETSCII character map
     */
    function showCharacterMap() {
        printLine('===== PETSCII CHARACTER MAP =====');
        printLine('');

        // PETSCII printable characters (32-126, basic ASCII subset)
        printLine('STANDARD CHARACTERS:');
        let line = '';
        for (let i = 32; i <= 126; i++) {
            line += String.fromCharCode(i);
            if ((i - 31) % 40 === 0) {
                printLine(line);
                line = '';
            }
        }
        if (line) printLine(line);

        printLine('');
        printLine('BLOCK GRAPHICS:');
        // Unicode block drawing characters (approximating PETSCII blocks)
        const blocks = '▀▄█▌▐░▒▓■□▪▫';
        printLine(blocks);

        printLine('');
        printLine('BOX DRAWING:');
        const boxes = '─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬';
        printLine(boxes);

        printLine('');
        printLine('PETSCII SYMBOLS:');
        const symbols = '♠♥♦♣●○◆◇★☆▲▼◄►';
        printLine(symbols);

        printLine('');
        printLine('USAGE: Type characters directly in terminal');
        printLine('TIP: Press Ctrl+V then character code for special chars');
        printLine('');
    }

    /**
     * Check API connection
     */
    async function checkConnection() {
        try {
            const response = await fetch(`${state.udosApiUrl}/status`);
            if (response.ok) {
                state.coreConnected = true;
                printColor('✓ API SERVER: CONNECTED', 'green');
            }
        } catch (error) {
            state.coreConnected = false;
            printColor('⚠ API SERVER: OFFLINE', 'yellow');
            printLine('{gray:START WITH: cd extensions/api && python server.py}');
        }
        printLine('');
        printColor('READY.', 'green');
        printLine('');
    }

    /**
     * Highlight syntax in text
     */
    function highlightSyntax(text) {
        // Skip highlighting for plain messages (all lowercase or starting with special chars)
        if (text.startsWith('=') || text.startsWith('*') || text.startsWith('-') ||
            text === text.toLowerCase() || !text.includes('(')) {
            return text; // Return plain text
        }

        let highlighted = text;
        const replacements = [];

        // Detect each pattern and store replacements
        for (const [type, pattern] of Object.entries(syntaxPatterns)) {
            const regex = new RegExp(pattern.source, pattern.flags);
            let match;

            while ((match = regex.exec(text)) !== null) {
                replacements.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    original: match[0],
                    type: type
                });
            }
        }

        // Sort by position (descending) to replace from end to start
        replacements.sort((a, b) => b.start - a.start);

        // Apply highlighting (from end to start to preserve positions)
        for (const repl of replacements) {
            const before = highlighted.substring(0, repl.start);
            const after = highlighted.substring(repl.end);
            const colored = `<span class="syn-${repl.type}">${repl.original}</span>`;
            highlighted = before + colored + after;
        }

        return highlighted;
    }

    /**
     * Print line to output
     */
    function printLine(text, enableHighlight = false) {
        const line = document.createElement('div');

        if (enableHighlight) {
            line.innerHTML = highlightSyntax(text);
        } else {
            // Check for color tags and apply them
            if (text.includes('{') && text.includes(':')) {
                line.innerHTML = colorize(text);
            } else {
                line.textContent = text;
            }
        }

        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    /**
     * Print colored line (convenience function)
     */
    function printColor(text, color) {
        const line = document.createElement('div');
        line.innerHTML = `<span style="color: ${colors[color] || colors.cyan}; font-weight: bold;">${text}</span>`;
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    /**
     * Print highlighted command (for echoing user input)
     */
    function printCommand(command) {
        const line = document.createElement('div');
        line.innerHTML = '<span class="syn-prompt">&gt; </span>' + highlightSyntax(command);
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
