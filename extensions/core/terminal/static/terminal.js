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
            splash.style.cssText = 'text-align: center; padding: 20px; font-family: "C64 User Mono", monospace;';

            // uDOS ASCII art logo - simple U
            const logo = [
                '',
                '',
                '  ██       ██',
                '  ██       ██',
                '  ██       ██',
                '  ██       ██',
                '  ██       ██',
                '  ██       ██',
                '  ███████████',
                '',
                '  UNIVERSAL DEVICE OPERATIONS SYSTEM',
                '          VERSION 2.0.0',
                '',
                ''
            ];

            logo.forEach((line, i) => {
                const lineDiv = document.createElement('div');
                lineDiv.textContent = line;
                // U in cyan, text in gray/pink
                if (i >= 2 && i <= 8) {
                    lineDiv.style.color = '#00D9FF'; // Cyan for U
                } else if (i === 10) {
                    lineDiv.style.color = '#A5A5A5'; // Gray for subtitle
                } else if (i === 11) {
                    lineDiv.style.color = '#FD79A8'; // Pink for version
                } else {
                    lineDiv.style.color = '#6C5CE7'; // Purple for empty lines
                }
                splash.appendChild(lineDiv);
            });

            // Loading bar container
            const loaderContainer = document.createElement('div');
            loaderContainer.style.cssText = 'margin: 20px auto; width: 300px;';

            const loaderText = document.createElement('div');
            loaderText.textContent = 'LOADING:';
            loaderText.style.cssText = 'color: #00D9FF; margin-bottom: 10px;';
            loaderContainer.appendChild(loaderText);

            const progressBar = document.createElement('div');
            progressBar.style.cssText = 'font-family: monospace; color: #FD79A8;';
            loaderContainer.appendChild(progressBar);

            splash.appendChild(loaderContainer);
            loadingScreen.appendChild(splash);

            // Animate loader
            let progress = 0;
            const totalSteps = 50;
            const interval = setInterval(() => {
                progress++;
                const filled = '█'.repeat(Math.floor(progress / 2));
                const empty = '░'.repeat(Math.floor((totalSteps - progress) / 2));
                const percent = Math.floor((progress / totalSteps) * 100);

                progressBar.textContent = `[${filled}${empty}] ${percent}%`;

                if (progress >= totalSteps) {
                    clearInterval(interval);
                    setTimeout(() => {
                        resolve();
                    }, 300);
                }
            }, 100); // 5 seconds total
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

        // Welcome message
        printLine('**** uDOS UNIVERSAL DEVICE OPERATIONS ****');
        printLine('TERMINAL MODE v2.0.0');
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
        printLine(`> ${command}`);

        // Local commands
        const cmd = command.toLowerCase();

        if (cmd === 'clear' || cmd === 'cls') {
            output.innerHTML = '';
            return;
        }

        if (cmd === 'help') {
            printLine('AVAILABLE COMMANDS:');
            printLine('  HELP     - SHOW THIS MESSAGE');
            printLine('  CLEAR    - CLEAR SCREEN');
            printLine('  STATUS   - SHOW SYSTEM STATUS');
            printLine('  EXIT     - CLOSE TERMINAL');
            printLine('');
            printLine('USE FUNCTION KEYS FOR QUICK ACCESS');
            return;
        }

        if (cmd === 'status') {
            printLine(`TERMINAL: READY`);
            printLine(`API: ${state.coreConnected ? 'CONNECTED' : 'DISCONNECTED'}`);
            printLine(`HISTORY: ${state.commandHistory.length} COMMANDS`);
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
                printLine('API SERVER: CONNECTED');
            }
        } catch (error) {
            state.coreConnected = false;
            printLine('API SERVER: OFFLINE');
            printLine('START WITH: cd extensions/api && python server.py');
        }
    }

    /**
     * Print line to output
     */
    function printLine(text) {
        const line = document.createElement('div');
        line.textContent = text;
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
