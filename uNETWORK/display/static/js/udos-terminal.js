/*
 * uDOS Terminal Module
 * Interactive terminal with shell integration and smart input
 * Universal Device Operating System v1.0.4.1
 */

class UDOSTerminal {
    constructor(socket) {
        this.socket = socket;
        this.currentDirectory = '/uMEMORY/user';
        this.commandHistory = [];
        this.historyIndex = -1;
        this.isConnected = false;
        this.promptFormat = 'uDOS$';
        this.outputBuffer = [];
        this.maxBufferSize = 1000;

        this.init();
    }

    init() {
        console.log('💻 Initializing uDOS Terminal...');

        this.setupEventListeners();
        this.loadCommandHistory();
        this.setupSocketListeners();
        this.updatePrompt();

        // Welcome message
        this.addOutput('🌐 uDOS Interactive Terminal Ready', 'info');
        this.addOutput('Universal Device Operating System v1.0.4.1', 'info');
        this.addOutput('Type "help" for available commands', 'info');
        this.addOutput('', 'info'); // Empty line
    }

    setupEventListeners() {
        const terminalInput = document.getElementById('terminalInputField');
        if (!terminalInput) return;

        // Handle enter key and command execution
        terminalInput.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    this.executeCommand(terminalInput.value);
                    break;

                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateHistory(-1);
                    break;

                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateHistory(1);
                    break;

                case 'Tab':
                    e.preventDefault();
                    this.handleTabCompletion(terminalInput.value);
                    break;

                case 'Escape':
                    e.preventDefault();
                    terminalInput.value = '';
                    break;
            }
        });

        // Handle input changes for autocomplete
        terminalInput.addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });

        // Terminal control buttons
        document.getElementById('termClear')?.addEventListener('click', () => {
            this.clearTerminal();
        });

        document.getElementById('termFont')?.addEventListener('click', () => {
            this.cycleFontSize();
        });

        document.getElementById('termTheme')?.addEventListener('click', () => {
            this.cycleTheme();
        });
    }

    setupSocketListeners() {
        if (!this.socket) return;

        this.socket.on('terminal_output', (data) => {
            this.handleTerminalOutput(data);
        });

        this.socket.on('terminal_error', (data) => {
            this.addOutput(data.message, 'error');
        });

        this.socket.on('command_complete', (data) => {
            this.handleCommandComplete(data);
        });

        this.socket.on('directory_changed', (data) => {
            this.currentDirectory = data.path;
            this.updatePrompt();
        });

        this.socket.on('connect', () => {
            this.isConnected = true;
            this.addOutput('🟢 Connected to uDOS server', 'success');
        });

        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.addOutput('🔴 Disconnected from uDOS server', 'error');
        });
    }

    executeCommand(command) {
        if (!command.trim()) return;

        // Add command to display
        this.addOutput(`${this.promptFormat} ${command}`, 'command');

        // Add to history
        this.addToHistory(command);

        // Clear input
        const input = document.getElementById('terminalInputField');
        if (input) input.value = '';

        // Reset history navigation
        this.historyIndex = -1;

        // Process command
        this.processCommand(command.trim());
    }

    processCommand(command) {
        const parts = command.split(' ');
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1);

        // Handle built-in commands
        switch (cmd) {
            case 'clear':
                this.clearTerminal();
                return;

            case 'help':
                this.showHelp();
                return;

            case 'history':
                this.showHistory();
                return;

            case 'pwd':
                this.addOutput(this.currentDirectory, 'info');
                return;

            case 'theme':
                if (args.length > 0) {
                    this.changeTheme(args[0]);
                } else {
                    this.showThemes();
                }
                return;

            case 'font':
                if (args.length > 0) {
                    this.changeFont(args[0]);
                } else {
                    this.showFonts();
                }
                return;

            case 'status':
                this.showSystemStatus();
                return;

            case 'ls':
            case 'dir':
                this.listDirectory(args[0] || this.currentDirectory);
                return;

            case 'cd':
                this.changeDirectory(args[0] || '/uMEMORY/user');
                return;

            case 'cat':
            case 'type':
                if (args.length > 0) {
                    this.displayFile(args[0]);
                } else {
                    this.addOutput('Usage: cat <filename>', 'error');
                }
                return;

            case 'grid':
                this.showGrid(args[0] || 'medium');
                return;

            case 'map':
                this.showMap(args[0] || 'local');
                return;

            default:
                // Send to server for processing
                if (this.socket && this.isConnected) {
                    this.socket.emit('execute_command', {
                        command: command,
                        directory: this.currentDirectory
                    });
                } else {
                    this.addOutput(`Command not found: ${cmd}`, 'error');
                    this.addOutput('Type "help" for available commands', 'info');
                }
        }
    }

    addOutput(text, type = 'info') {
        const output = document.getElementById('terminalOutput');
        if (!output) return;

        const line = document.createElement('div');
        line.className = 'terminal-line';

        // Create output based on type
        switch (type) {
            case 'command':
                line.innerHTML = `<span class="term-prompt">${this.promptFormat}</span><span class="term-command">${text.replace(this.promptFormat, '').trim()}</span>`;
                break;
            case 'error':
                line.innerHTML = `<span class="term-error">${text}</span>`;
                break;
            case 'success':
                line.innerHTML = `<span class="term-success">${text}</span>`;
                break;
            case 'warning':
                line.innerHTML = `<span class="term-warning">${text}</span>`;
                break;
            case 'info':
            default:
                line.innerHTML = `<span class="term-info">${text}</span>`;
                break;
        }

        output.appendChild(line);

        // Add to buffer
        this.outputBuffer.push({ text, type, timestamp: Date.now() });

        // Limit buffer size
        if (this.outputBuffer.length > this.maxBufferSize) {
            this.outputBuffer = this.outputBuffer.slice(-this.maxBufferSize);

            // Remove old DOM elements
            while (output.children.length > this.maxBufferSize) {
                output.removeChild(output.firstChild);
            }
        }

        // Auto-scroll to bottom
        this.scrollToBottom();
    }

    scrollToBottom() {
        const display = document.getElementById('terminalDisplay');
        if (display) {
            display.scrollTop = display.scrollHeight;
        }
    }

    addToHistory(command) {
        // Avoid duplicate consecutive commands
        if (this.commandHistory[0] !== command) {
            this.commandHistory.unshift(command);
        }

        // Limit history size
        if (this.commandHistory.length > 100) {
            this.commandHistory = this.commandHistory.slice(0, 100);
        }

        this.saveCommandHistory();
    }

    navigateHistory(direction) {
        const input = document.getElementById('terminalInputField');
        if (!input || this.commandHistory.length === 0) return;

        if (direction === -1) { // Up arrow
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
            }
        } else if (direction === 1) { // Down arrow
            if (this.historyIndex > -1) {
                this.historyIndex--;
            }
        }

        if (this.historyIndex === -1) {
            input.value = '';
        } else {
            input.value = this.commandHistory[this.historyIndex];
        }
    }

    handleTabCompletion(input) {
        const parts = input.split(' ');
        const currentWord = parts[parts.length - 1];

        // Command completion
        if (parts.length === 1) {
            const commands = this.getAvailableCommands();
            const matches = commands.filter(cmd => cmd.startsWith(currentWord.toLowerCase()));

            if (matches.length === 1) {
                const inputField = document.getElementById('terminalInputField');
                if (inputField) {
                    inputField.value = matches[0] + ' ';
                }
            } else if (matches.length > 1) {
                this.addOutput(`Possible completions: ${matches.join(', ')}`, 'info');
            }
        }
        // File/path completion would go here
    }

    getAvailableCommands() {
        return [
            'help', 'clear', 'history', 'pwd', 'ls', 'dir', 'cd', 'cat', 'type',
            'status', 'theme', 'font', 'grid', 'map', 'backup', 'logs', 'memory',
            'role', 'workflow', 'get', 'set', 'data', 'template', 'export'
        ];
    }

    clearTerminal() {
        const output = document.getElementById('terminalOutput');
        if (output) {
            output.innerHTML = '';
        }
        this.outputBuffer = [];
        this.addOutput('Terminal cleared', 'info');
    }

    showHelp() {
        const helpText = `
Available Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Commands:
  help              Show this help message
  status            Display system status
  clear             Clear terminal screen
  history           Show command history

File System:
  pwd               Show current directory
  ls, dir           List directory contents
  cd <path>         Change directory
  cat, type <file>  Display file contents

uDOS Features:
  grid [size]       Show grid display (small/medium/large)
  map [region]      Show map tiles (local/global/custom)
  theme [name]      Change color theme
  font [name]       Change font family

Data Commands:
  backup            Create system backup
  logs              View system logs
  memory            Browse uMEMORY system
  role              Show current role
  workflow          Workflow management

Advanced:
  get <variable>    Get system variable
  set <var> <val>   Set system variable
  data <operation>  Data operations
  template <name>   Load template
  export <format>   Export data

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type any command followed by --help for detailed usage`;

        this.addOutput(helpText, 'info');
    }

    showHistory() {
        if (this.commandHistory.length === 0) {
            this.addOutput('No command history available', 'info');
            return;
        }

        this.addOutput('Command History:', 'info');
        this.addOutput('━━━━━━━━━━━━━━━', 'info');

        this.commandHistory.slice(0, 20).forEach((cmd, index) => {
            this.addOutput(`${(index + 1).toString().padStart(3)}: ${cmd}`, 'info');
        });
    }

    showSystemStatus() {
        this.addOutput('uDOS System Status:', 'info');
        this.addOutput('━━━━━━━━━━━━━━━━━━━', 'info');
        this.addOutput(`Current Directory: ${this.currentDirectory}`, 'info');
        this.addOutput(`Connection: ${this.isConnected ? '🟢 Connected' : '🔴 Disconnected'}`, 'info');
        this.addOutput(`Terminal Buffer: ${this.outputBuffer.length}/${this.maxBufferSize}`, 'info');
        this.addOutput(`Command History: ${this.commandHistory.length} commands`, 'info');

        if (window.udosApp) {
            const settings = window.udosApp.getSettings();
            this.addOutput(`Theme: ${settings.theme}`, 'info');
            this.addOutput(`Font: ${settings.font}`, 'info');
            this.addOutput(`Grid Size: ${settings.gridSize}`, 'info');
        }
    }

    showThemes() {
        const themes = [
            'polaroid', 'retro-unicorn', 'nostalgia', 'tropical-sunrise',
            'pastel-power', 'arcade-pastels', 'grayscale', 'solar-punk'
        ];

        this.addOutput('Available Themes:', 'info');
        this.addOutput('━━━━━━━━━━━━━━━━━', 'info');
        themes.forEach(theme => {
            this.addOutput(`  ${theme}`, 'info');
        });
        this.addOutput('Usage: theme <name>', 'info');
    }

    showFonts() {
        const fonts = ['mono', 'roboto', 'space', 'courier'];

        this.addOutput('Available Fonts:', 'info');
        this.addOutput('━━━━━━━━━━━━━━━━', 'info');
        fonts.forEach(font => {
            this.addOutput(`  ${font}`, 'info');
        });
        this.addOutput('Usage: font <name>', 'info');
    }

    changeTheme(theme) {
        if (window.udosApp) {
            window.udosApp.changeTheme(theme);
            this.addOutput(`Theme changed to ${theme}`, 'success');
        } else {
            this.addOutput('Unable to change theme', 'error');
        }
    }

    changeFont(font) {
        if (window.udosApp) {
            window.udosApp.changeFont(font);
            this.addOutput(`Font changed to ${font}`, 'success');
        } else {
            this.addOutput('Unable to change font', 'error');
        }
    }

    cycleFontSize() {
        const display = document.getElementById('terminalDisplay');
        if (!display) return;

        const currentSize = parseFloat(getComputedStyle(display).fontSize);
        const sizes = [12, 14, 16, 18, 20];
        const currentIndex = sizes.findIndex(size => Math.abs(size - currentSize) < 1);
        const nextIndex = (currentIndex + 1) % sizes.length;

        display.style.fontSize = `${sizes[nextIndex]}px`;
        this.addOutput(`Font size changed to ${sizes[nextIndex]}px`, 'info');
    }

    cycleTheme() {
        const themes = [
            'polaroid', 'retro-unicorn', 'nostalgia', 'tropical-sunrise',
            'pastel-power', 'arcade-pastels', 'grayscale', 'solar-punk'
        ];

        const current = document.body.getAttribute('data-theme') || 'polaroid';
        const currentIndex = themes.indexOf(current);
        const nextIndex = (currentIndex + 1) % themes.length;

        this.changeTheme(themes[nextIndex]);
    }

    showGrid(size) {
        if (window.udosApp) {
            window.udosApp.switchTab('grid');
            window.udosApp.changeGridSize(size);
            this.addOutput(`Switched to grid view (${size})`, 'info');
        } else {
            this.addOutput('Grid view not available', 'error');
        }
    }

    showMap(region) {
        if (window.udosApp) {
            window.udosApp.switchTab('map');
            this.addOutput(`Switched to map view (${region})`, 'info');
        } else {
            this.addOutput('Map view not available', 'error');
        }
    }

    listDirectory(path) {
        if (this.socket && this.isConnected) {
            this.socket.emit('list_directory', { path });
        } else {
            this.addOutput('Cannot list directory: not connected to server', 'error');
        }
    }

    changeDirectory(path) {
        if (this.socket && this.isConnected) {
            this.socket.emit('change_directory', { path });
        } else {
            this.currentDirectory = path;
            this.updatePrompt();
            this.addOutput(`Changed directory to ${path}`, 'info');
        }
    }

    displayFile(filename) {
        if (this.socket && this.isConnected) {
            this.socket.emit('read_file', {
                path: `${this.currentDirectory}/${filename}`
            });
        } else {
            this.addOutput('Cannot display file: not connected to server', 'error');
        }
    }

    updatePrompt() {
        const promptElements = document.querySelectorAll('.terminal-prompt-active');
        const shortPath = this.currentDirectory.split('/').slice(-2).join('/') || '/';
        this.promptFormat = `uDOS:${shortPath}$`;

        promptElements.forEach(el => {
            el.textContent = this.promptFormat;
        });
    }

    handleTerminalOutput(data) {
        this.addOutput(data.output, data.type || 'info');
    }

    handleCommandComplete(data) {
        if (data.success) {
            this.addOutput(data.message || 'Command completed', 'success');
        } else {
            this.addOutput(data.message || 'Command failed', 'error');
        }
    }

    handleInputChange(value) {
        // Could implement real-time suggestions here
    }

    focus() {
        const input = document.getElementById('terminalInputField');
        if (input) {
            input.focus();
        }
    }

    loadCommandHistory() {
        const saved = localStorage.getItem('udos-terminal-history');
        if (saved) {
            try {
                this.commandHistory = JSON.parse(saved);
            } catch (error) {
                console.warn('Error loading terminal history:', error);
            }
        }
    }

    saveCommandHistory() {
        localStorage.setItem('udos-terminal-history', JSON.stringify(this.commandHistory.slice(0, 100)));
    }

    // Public API methods
    executeCommandFromExternal(command) {
        this.executeCommand(command);
    }

    getOutput() {
        return [...this.outputBuffer];
    }

    clearOutput() {
        this.clearTerminal();
    }
}

// Export for external use
window.UDOSTerminal = UDOSTerminal;
