/**
 * uDOS C64 Terminal - Main Terminal Logic
 * Command handling, history, and terminal operations
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // Terminal state
    const state = {
        commandHistory: [],
        historyIndex: -1,
        currentDirectory: '/',
        ready: false
    };

    // DOM Elements
    let terminal;
    let commandInput;
    let terminalOutput;
    let statusElement;
    let charReference;

    // Initialize terminal
    function init() {
        // Wait for terminal to be ready
        document.addEventListener('udos:terminal:ready', function() {
            setupTerminal();
        });

        // If terminal is already visible, setup immediately
        terminal = document.getElementById('terminal');
        if (terminal && !terminal.classList.contains('hidden')) {
            setupTerminal();
        }
    }

    /**
     * Setup terminal once ready
     */
    function setupTerminal() {
        // Get DOM elements
        commandInput = document.getElementById('commandInput');
        terminalOutput = document.getElementById('output');
        statusElement = document.getElementById('status');
        charReference = document.getElementById('charReference');

        // Setup event listeners
        setupEventListeners();

        // Mark as ready
        state.ready = true;
        updateStatus('READY.');

        console.log('[uDOS Terminal] Initialized and ready');
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Command input
        if (commandInput) {
            commandInput.addEventListener('keydown', handleKeyDown);
            commandInput.addEventListener('input', handleInput);
        }

        // Function keys
        const fKeys = document.querySelectorAll('.f-key');
        fKeys.forEach(key => {
            key.addEventListener('click', handleFunctionKey);
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', handleGlobalKeys);
    }

    /**
     * Handle keyboard input in command line
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

            case 'Tab':
                e.preventDefault();
                autocomplete();
                break;
        }
    }

    /**
     * Handle input changes
     */
    function handleInput(e) {
        // Could add live suggestions here
    }

    /**
     * Execute command
     */
    function executeCommand() {
        const command = commandInput.value.trim();

        if (!command) {
            return;
        }

        // Add to history
        state.commandHistory.push(command);
        state.historyIndex = state.commandHistory.length;

        // Display command
        appendOutput(`<span class="fg-cyan">></span> ${escapeHtml(command)}`);

        // Parse and execute
        const result = processCommand(command);

        if (result) {
            appendOutput(result);
        }

        // Clear input
        commandInput.value = '';

        // Scroll to bottom
        scrollToBottom();
    }

    /**
     * Process command and return output
     */
    function processCommand(command) {
        const parts = command.toUpperCase().split(' ');
        const cmd = parts[0];
        const args = parts.slice(1);

        switch(cmd) {
            case 'HELP':
                return getHelpText();

            case 'LIST':
                return listCommands();

            case 'CLEAR':
            case 'CLS':
                clearScreen();
                return null;

            case 'LOAD':
                return loadProgram(args[0]);

            case 'RUN':
                return runProgram();

            case 'POKE':
                return handlePoke(args);

            case 'PEEK':
                return handlePeek(args);

            case 'SYS':
                return handleSys(args);

            case 'PRINT':
                return args.join(' ') || '';

            case 'COLOR':
                return changeColor(args);

            case 'CHARS':
                toggleCharReference();
                return 'CHARACTER REFERENCE TOGGLED';

            case 'EMOJI':
                return showEmoji();

            default:
                // Check if it's a BASIC command
                if (isBasicCommand(cmd)) {
                    return `BASIC COMMAND: ${command}\n?SYNTAX ERROR`;
                }
                return `?SYNTAX ERROR\nTYPE "HELP" FOR COMMANDS`;
        }
    }

    /**
     * Get help text
     */
    function getHelpText() {
        return `
<span class="fg-cyan">uDOS C64 TERMINAL - COMMAND REFERENCE</span>

<span class="fg-light-green">BASIC COMMANDS:</span>
  LIST        - LIST AVAILABLE COMMANDS
  LOAD "NAME" - LOAD A PROGRAM
  RUN         - RUN LOADED PROGRAM
  PRINT       - PRINT TEXT OR VARIABLES
  CLEAR/CLS   - CLEAR SCREEN

<span class="fg-light-green">SYSTEM COMMANDS:</span>
  POKE ADDR,VAL - WRITE TO MEMORY
  PEEK ADDR     - READ FROM MEMORY
  SYS ADDR      - EXECUTE MACHINE CODE

<span class="fg-light-green">uDOS COMMANDS:</span>
  COLOR FG BG - SET COLORS (0-15)
  CHARS       - TOGGLE CHARACTER REFERENCE
  EMOJI       - SHOW EMOJI PALETTE
  HELP        - SHOW THIS HELP

<span class="fg-yellow">PRESS F1-F7 FOR FUNCTION KEYS</span>
<span class="fg-yellow">PRESS F8 TO TOGGLE CHARACTER PANEL</span>
        `.trim();
    }

    /**
     * List commands
     */
    function listCommands() {
        return `
<span class="fg-cyan">AVAILABLE PROGRAMS:</span>

  "HELLO"     - HELLO WORLD DEMO
  "COLORS"    - COLOR PALETTE DEMO
  "GRAPHICS"  - BLOCK GRAPHICS DEMO
  "EMOJI"     - EMOJI DEMO

<span class="fg-yellow">USE: LOAD "NAME" THEN RUN</span>
        `.trim();
    }

    /**
     * Load program
     */
    function loadProgram(name) {
        if (!name) {
            return '?MISSING FILE NAME';
        }

        // Remove quotes if present
        name = name.replace(/"/g, '');

        const programs = {
            'HELLO': 'HELLO',
            'COLORS': 'COLORS',
            'GRAPHICS': 'GRAPHICS',
            'EMOJI': 'EMOJI'
        };

        if (programs[name.toUpperCase()]) {
            state.loadedProgram = name.toUpperCase();
            return `LOADING ${name}\nREADY.`;
        }

        return `?FILE NOT FOUND: ${name}`;
    }

    /**
     * Run program
     */
    function runProgram() {
        if (!state.loadedProgram) {
            return '?NO PROGRAM LOADED\nUSE: LOAD "NAME"';
        }

        switch(state.loadedProgram) {
            case 'HELLO':
                return runHelloWorld();
            case 'COLORS':
                return runColorDemo();
            case 'GRAPHICS':
                return runGraphicsDemo();
            case 'EMOJI':
                return runEmojiDemo();
            default:
                return '?PROGRAM ERROR';
        }
    }

    /**
     * Demo programs
     */
    function runHelloWorld() {
        return `
<span class="fg-cyan">****************************************</span>
<span class="fg-light-green">*                                      *</span>
<span class="fg-light-green">*     HELLO FROM uDOS C64 TERMINAL!    *</span>
<span class="fg-light-green">*                                      *</span>
<span class="fg-cyan">****************************************</span>

<span class="fg-yellow">WELCOME TO THE UNIVERSAL DIGITAL</span>
<span class="fg-yellow">OPERATIONS SYSTEM - C64 EDITION!</span>

READY.
        `.trim();
    }

    function runColorDemo() {
        const colors = [
            'BLACK', 'WHITE', 'RED', 'CYAN', 'PURPLE', 'GREEN',
            'BLUE', 'YELLOW', 'ORANGE', 'BROWN', 'LIGHT-RED',
            'DARK-GRAY', 'GRAY', 'LIGHT-GREEN', 'LIGHT-BLUE', 'LIGHT-GRAY'
        ];

        let output = '<span class="fg-cyan">C64 SYNTHWAVE DOS COLOR PALETTE:</span>\n\n';

        colors.forEach((color, i) => {
            const className = `fg-${color.toLowerCase().replace('_', '-')}`;
            output += `<span class="${className}">${i.toString().padStart(2, '0')}: ████ ${color}</span>\n`;
        });

        return output + '\nREADY.';
    }

    function runGraphicsDemo() {
        return `
<span class="fg-cyan">PETSCII BLOCK GRAPHICS DEMO:</span>

<span class="fg-light-blue">█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█</span>
<span class="fg-light-blue">█                                 █</span>
<span class="fg-cyan">█   ▄▄▄   █ █ ███ ▄▄▄ ▄▄▄        █</span>
<span class="fg-cyan">█   █ █   █ █ █ █ █ █ █ █        █</span>
<span class="fg-cyan">█   ███   ███ █ █ █ █ ▄▄▄        █</span>
<span class="fg-light-blue">█                                 █</span>
<span class="fg-light-blue">█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█</span>

<span class="fg-yellow">BLOCK CHARACTERS: ▀ ▄ █ ▌ ▐ ░ ▒ ▓</span>

READY.
        `.trim();
    }

    function runEmojiDemo() {
        return `
<span class="fg-cyan">MONOCOLOR EMOJI DEMO:</span>

<span class="fg-yellow">😀 😃 😄 😁 😆 😅 🤣 😂</span>
<span class="fg-light-green">👍 👎 ✌️  ✊ 👊 🙏 💪 🤝</span>
<span class="fg-light-blue">❤️  💙 💚 💛 🧡 💜 🖤 🤍</span>
<span class="fg-orange">⭐ ✨ 💫 ⚡ 🔥 💧 ❄️  🌈</span>

<span class="fg-cyan">TYPE "CHARS" TO SEE ALL CHARACTERS</span>

READY.
        `.trim();
    }

    /**
     * Handle POKE command
     */
    function handlePoke(args) {
        if (args.length < 2) {
            return '?SYNTAX ERROR\nUSAGE: POKE ADDRESS,VALUE';
        }
        return `POKE ${args[0]},${args[1]}\nOK`;
    }

    /**
     * Handle PEEK command
     */
    function handlePeek(args) {
        if (args.length < 1) {
            return '?SYNTAX ERROR\nUSAGE: PEEK ADDRESS';
        }
        const value = Math.floor(Math.random() * 256);
        return ` ${value}`;
    }

    /**
     * Handle SYS command
     */
    function handleSys(args) {
        if (args.length < 1) {
            return '?SYNTAX ERROR\nUSAGE: SYS ADDRESS';
        }
        return `SYS ${args[0]}\nOK`;
    }

    /**
     * Change colors
     */
    function changeColor(args) {
        // Simplified color change
        return `COLOR CHANGE: FG=${args[0]}, BG=${args[1]}\nNOT IMPLEMENTED YET`;
    }

    /**
     * Show emoji
     */
    function showEmoji() {
        toggleCharReference();
        return 'EMOJI PALETTE SHOWN';
    }

    /**
     * Check if BASIC command
     */
    function isBasicCommand(cmd) {
        const basicCmds = [
            'FOR', 'NEXT', 'IF', 'THEN', 'GOTO', 'GOSUB', 'RETURN',
            'DIM', 'DATA', 'READ', 'LET', 'INPUT', 'GET', 'END', 'STOP'
        ];
        return basicCmds.includes(cmd);
    }

    /**
     * Navigate command history
     */
    function navigateHistory(direction) {
        if (state.commandHistory.length === 0) {
            return;
        }

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
     * Autocomplete (basic implementation)
     */
    function autocomplete() {
        const value = commandInput.value.toUpperCase();
        const commands = ['HELP', 'LIST', 'LOAD', 'RUN', 'CLEAR', 'PRINT', 'POKE', 'PEEK', 'SYS', 'COLOR', 'CHARS', 'EMOJI'];

        const matches = commands.filter(cmd => cmd.startsWith(value));

        if (matches.length === 1) {
            commandInput.value = matches[0];
        } else if (matches.length > 1) {
            appendOutput(`MATCHES: ${matches.join(', ')}`);
        }
    }

    /**
     * Clear screen
     */
    function clearScreen() {
        if (terminalOutput) {
            terminalOutput.innerHTML = '';
        }
    }

    /**
     * Append output to terminal
     */
    function appendOutput(text) {
        if (!terminalOutput) return;

        const p = document.createElement('p');
        p.innerHTML = text;
        terminalOutput.appendChild(p);
    }

    /**
     * Scroll to bottom
     */
    function scrollToBottom() {
        const screen = document.querySelector('.terminal-screen');
        if (screen) {
            screen.scrollTop = screen.scrollHeight;
        }
    }

    /**
     * Update status
     */
    function updateStatus(status) {
        if (statusElement) {
            statusElement.textContent = status;
        }
    }

    /**
     * Toggle character reference panel
     */
    function toggleCharReference() {
        if (charReference) {
            charReference.classList.toggle('visible');
            charReference.classList.toggle('hidden');
        }
    }

    /**
     * Handle function keys
     */
    function handleFunctionKey(e) {
        const key = e.currentTarget.dataset.key;

        switch(key) {
            case 'F1':
                commandInput.value = 'HELP';
                executeCommand();
                break;
            case 'F3':
                commandInput.value = 'LIST';
                executeCommand();
                break;
            case 'F5':
                commandInput.value = 'RUN';
                executeCommand();
                break;
            case 'F7':
                clearScreen();
                break;
        }
    }

    /**
     * Handle global keyboard shortcuts
     */
    function handleGlobalKeys(e) {
        // F8 - Toggle character reference
        if (e.key === 'F8') {
            e.preventDefault();
            toggleCharReference();
        }
    }

    /**
     * Escape HTML
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Expose terminal API
    window.uDOS = window.uDOS || {};
    window.uDOS.terminal = {
        executeCommand: processCommand,
        clearScreen: clearScreen,
        appendOutput: appendOutput,
        updateStatus: updateStatus
    };

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
