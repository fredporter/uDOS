/**
 * uDOS Terminal - Main Terminal Logic
 * Version: 1.0.24
 * Integrated with uDOS core command system
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
        udosApiUrl: 'http://localhost:8890/api'  // uDOS core API endpoint
    };

    // DOM Elements
    let terminal;
    let commandInput;
    let terminalOutput;
    let statusElement;
    let charReference;
    let terminalViewport;

    /**
     * Initialize terminal
     */
    function init() {
        // Wait for terminal to be ready
        document.addEventListener('udos:terminal:ready', function() {
            setupTerminal();
        });
    }

    /**
     * Setup terminal once splash is complete
     */
    function setupTerminal() {
        console.log('[uDOS Terminal] Initializing...');

        // Get DOM elements
        terminal = document.getElementById('terminalContainer');
        commandInput = document.getElementById('commandInput');
        terminalOutput = document.getElementById('output');
        statusElement = document.getElementById('status');
        charReference = document.getElementById('charReference');
        terminalViewport = document.querySelector('.terminal-viewport');

        // Setup cursor positioning
        setupCursor();

        // Initialize session
        initializeSession();

        // Setup event listeners
        setupEventListeners();

        // Mark as ready
        state.ready = true;
        updateStatus('READY.');

        // Focus input
        commandInput.focus();

        console.log('[uDOS Terminal] Ready');
    }

    /**
     * Setup cursor to follow input
     */
    function setupCursor() {
        const cursor = document.querySelector('.cursor');
        const input = commandInput;

        if (!cursor || !input) return;

        function updateCursorPosition() {
            // Create temporary span to measure text width
            const span = document.createElement('span');
            span.style.font = window.getComputedStyle(input).font;
            span.style.visibility = 'hidden';
            span.style.position = 'absolute';
            span.textContent = input.value || '';
            document.body.appendChild(span);

            const textWidth = span.offsetWidth;
            document.body.removeChild(span);

            // Position cursor after text
            cursor.style.left = textWidth + 'px';
        }

        // Update on input
        input.addEventListener('input', updateCursorPosition);
        input.addEventListener('keydown', () => setTimeout(updateCursorPosition, 0));

        // Initial position
        updateCursorPosition();
    }    /**
     * Initialize session with uDOS core
     */
    async function initializeSession() {
        try {
            // Create a new terminal session
            state.sessionId = 'web-terminal-' + Date.now();

            // Try to ping uDOS core
            const response = await fetch(`${state.udosApiUrl}/status`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('[uDOS Terminal] Connected to core:', data);
                printLine('✓ CONNECTED TO uDOS CORE v' + (data.version || '1.0.24'), 'output-success');
            } else {
                console.warn('[uDOS Terminal] Core not available, running in standalone mode');
                printLine('⚠ RUNNING IN STANDALONE MODE', 'output-warning');
            }
        } catch (error) {
            console.warn('[uDOS Terminal] Core not available:', error.message);
            printLine('⚠ RUNNING IN STANDALONE MODE', 'output-warning');
            printLine('  START uDOS CORE FOR FULL FUNCTIONALITY', 'output-dim');
        }

        printLine('');
    }

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Command input
        if (commandInput) {
            commandInput.addEventListener('keydown', handleKeyDown);
        }

        // Function keys
        const fKeys = document.querySelectorAll('.f-key');
        fKeys.forEach(key => {
            key.addEventListener('click', () => handleFunctionKey(key.dataset.key));
        });

        // Character reference close button
        const closeBtn = document.getElementById('closeCharRef');
        if (closeBtn) {
            closeBtn.addEventListener('click', toggleCharReference);
        }

        // Global keyboard shortcuts
        document.addEventListener('keydown', handleGlobalKeys);

        // Click outside char reference to close
        document.addEventListener('click', (e) => {
            if (!charReference.classList.contains('hidden') &&
                !charReference.contains(e.target) &&
                !e.target.closest('.f-key[data-key="F8"]')) {
                charReference.classList.add('hidden');
            }
        });
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

            case 'Tab':
                e.preventDefault();
                // TODO: Implement tab completion
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
        // Function keys
        if (e.key.startsWith('F') && e.key.length === 2) {
            e.preventDefault();
            handleFunctionKey(e.key);
        }

        // Ctrl+L - Clear screen
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearScreen();
        }
    }

    /**
     * Handle function key press
     */
    function handleFunctionKey(key) {
        console.log('[uDOS Terminal] Function key:', key);

        switch(key) {
            case 'F1':
                executeCommand('HELP');
                break;
            case 'F2':
                executeCommand('KNOWLEDGE');
                break;
            case 'F3':
                executeCommand('LIST');
                break;
            case 'F4':
                printLine('✎ EDIT MODE - Use EDIT <filename> command', 'output-info');
                break;
            case 'F5':
                printLine('▶ RUN MODE - Use RUN <script> command', 'output-info');
                break;
            case 'F6':
                executeCommand('STATUS');
                break;
            case 'F7':
                clearScreen();
                break;
            case 'F8':
                toggleCharReference();
                break;
        }
    }

    /**
     * Execute command
     */
    async function executeCommand(cmdText = null) {
        const command = cmdText || commandInput.value.trim();

        if (!command) {
            printPromptLine('');
            return;
        }

        // Print command with prompt
        printPromptLine(command);

        // Add to history
        if (!cmdText) {
            state.commandHistory.push(command);
            state.historyIndex = state.commandHistory.length;
            commandInput.value = '';
        }

        // Update status
        updateStatus('PROCESSING...');

        // Process command
        await processCommand(command);

        // Reset status
        updateStatus('READY.');

        // Scroll to bottom
        scrollToBottom();

        // Focus input
        commandInput.focus();
    }

    /**
     * Process command (integrate with uDOS core or handle locally)
     */
    async function processCommand(command) {
        const cmd = command.toUpperCase();
        const args = command.split(/\s+/).slice(1);

        // Try to send to uDOS core first
        try {
            const response = await fetch(`${state.udosApiUrl}/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: state.sessionId,
                    command: command,
                    cwd: state.currentDirectory
                })
            });

            if (response.ok) {
                const result = await response.json();
                displayCommandResult(result);
                return;
            }
        } catch (error) {
            console.log('[uDOS Terminal] Core not available, using local handlers');
        }

        // Local command handlers (fallback)
        await handleLocalCommand(cmd, args);
    }

    /**
     * Handle local commands when core is not available
     */
    async function handleLocalCommand(cmd, args) {
        switch(cmd) {
            case 'HELP':
                displayHelp();
                break;

            case 'CLEAR':
            case 'CLS':
                clearScreen();
                break;

            case 'STATUS':
                displayStatus();
                break;

            case 'HISTORY':
                displayHistory();
                break;

            case 'KNOWLEDGE':
                printLine('KNOWLEDGE BASE COMMANDS:', 'output-info');
                printLine('  K-LIST   - List knowledge articles', 'output-dim');
                printLine('  K-SEARCH - Search knowledge base', 'output-dim');
                printLine('  K-READ   - Read knowledge article', 'output-dim');
                break;

            case 'LIST':
            case 'LS':
            case 'DIR':
                printLine('DIRECTORY LISTING: ' + state.currentDirectory, 'output-info');
                printLine('  Use with uDOS Core for full file system access', 'output-dim');
                break;

            case 'GUIDE':
                printLine('uDOS TERMINAL GUIDE:', 'output-info');
                printLine('', 'output-dim');
                printLine('  FUNCTION KEYS:', 'output-dim');
                printLine('    F1 - Help System', 'output-dim');
                printLine('    F2 - Knowledge Base', 'output-dim');
                printLine('    F3 - List Directory', 'output-dim');
                printLine('    F7 - Clear Screen', 'output-dim');
                printLine('    F8 - Character Reference', 'output-dim');
                printLine('', 'output-dim');
                printLine('  NAVIGATION:', 'output-dim');
                printLine('    ↑/↓ - Command History', 'output-dim');
                printLine('    ESC - Clear Input', 'output-dim');
                break;

            case 'CHARS':
            case 'PETSCII':
                toggleCharReference();
                break;

            case 'VER':
            case 'VERSION':
                printLine('uDOS TERMINAL v1.0.24', 'output-success');
                printLine('UNIVERSAL DIGITAL OPERATIONS SYSTEM', 'output-dim');
                break;

            default:
                if (cmd) {
                    printLine('✗ UNKNOWN COMMAND: ' + cmd, 'output-error');
                    printLine('  TYPE "HELP" FOR COMMAND LIST', 'output-dim');
                }
                break;
        }
    }

    /**
     * Display command result from uDOS core
     */
    function displayCommandResult(result) {
        if (result.output) {
            if (Array.isArray(result.output)) {
                result.output.forEach(line => printLine(line));
            } else {
                printLine(result.output);
            }
        }

        if (result.error) {
            printLine('✗ ERROR: ' + result.error, 'output-error');
        }

        if (result.cwd) {
            state.currentDirectory = result.cwd;
        }
    }

    /**
     * Display help
     */
    function displayHelp() {
        printLine('uDOS TERMINAL COMMANDS:', 'output-success');
        printLine('');
        printLine('SYSTEM:', 'output-info');
        printLine('  HELP     - Show this help', 'output-dim');
        printLine('  STATUS   - System status', 'output-dim');
        printLine('  CLEAR    - Clear screen', 'output-dim');
        printLine('  GUIDE    - Terminal guide', 'output-dim');
        printLine('  VERSION  - Show version', 'output-dim');
        printLine('');
        printLine('FILES:', 'output-info');
        printLine('  LIST     - List directory', 'output-dim');
        printLine('  EDIT     - Edit file', 'output-dim');
        printLine('  RUN      - Run script', 'output-dim');
        printLine('');
        printLine('KNOWLEDGE:', 'output-info');
        printLine('  KNOWLEDGE - Knowledge base commands', 'output-dim');
        printLine('  K-LIST    - List articles', 'output-dim');
        printLine('  K-SEARCH  - Search knowledge', 'output-dim');
        printLine('');
        printLine('NOTE: Connect to uDOS Core for full command set', 'output-warning');
    }

    /**
     * Display system status
     */
    function displayStatus() {
        printLine('uDOS TERMINAL STATUS:', 'output-success');
        printLine('');
        printLine('  Version:    1.0.24', 'output-dim');
        printLine('  Session:    ' + state.sessionId, 'output-dim');
        printLine('  Directory:  ' + state.currentDirectory, 'output-dim');
        printLine('  History:    ' + state.commandHistory.length + ' commands', 'output-dim');
        printLine('  Status:     ' + (state.ready ? 'READY' : 'INITIALIZING'), 'output-dim');
    }

    /**
     * Display command history
     */
    function displayHistory() {
        if (state.commandHistory.length === 0) {
            printLine('NO COMMAND HISTORY', 'output-dim');
            return;
        }

        printLine('COMMAND HISTORY:', 'output-info');
        state.commandHistory.forEach((cmd, index) => {
            printLine(`  ${index + 1}. ${cmd}`, 'output-dim');
        });
    }

    /**
     * Navigate command history
     */
    function navigateHistory(direction) {
        if (state.commandHistory.length === 0) return;

        if (direction === 'up') {
            if (state.historyIndex > 0) {
                state.historyIndex--;
                commandInput.value = state.commandHistory[state.historyIndex];
            }
        } else if (direction === 'down') {
            if (state.historyIndex < state.commandHistory.length - 1) {
                state.historyIndex++;
                commandInput.value = state.commandHistory[state.historyIndex];
            } else {
                state.historyIndex = state.commandHistory.length;
                commandInput.value = '';
            }
        }
    }

    /**
     * Clear screen
     */
    function clearScreen() {
        terminalOutput.innerHTML = '';
        updateStatus('SCREEN CLEARED');
        setTimeout(() => updateStatus('READY.'), 1000);
    }

    /**
     * Toggle character reference panel
     */
    function toggleCharReference() {
        charReference.classList.toggle('hidden');
    }

    /**
     * Print line to terminal
     */
    let lineCount = 0;
    function printLine(text, className = '') {
        const line = document.createElement('p');
        line.textContent = text;
        if (className) {
            line.className = className;
        }
        // Add staggered animation delay for smooth reading
        line.style.animationDelay = `${lineCount * 0.05}s`;
        lineCount++;
        terminalOutput.appendChild(line);

        // Reset counter after animation completes
        setTimeout(() => lineCount = 0, 300);
    }

    /**
     * Print command with prompt
     */
    function printPromptLine(command) {
        const line = document.createElement('p');
        line.innerHTML = '<span style="color: var(--term-prompt);">█</span> ' + escapeHtml(command);
        terminalOutput.appendChild(line);
    }

    /**
     * Update status display
     */
    function updateStatus(text) {
        if (statusElement) {
            statusElement.textContent = text;
        }
    }

    /**
     * Scroll terminal to bottom
     */
    function scrollToBottom() {
        if (terminalViewport) {
            terminalViewport.scrollTop = terminalViewport.scrollHeight;
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

    /**
     * Make terminal accessible globally
     */
    window.uDOSTerminal = {
        executeCommand,
        printLine,
        clearScreen,
        getState: () => ({ ...state })
    };

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
