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
    
    // Add some initial commands to help users
    setTimeout(() => {
        window.udos.addToTerminal('📺 uDOS Teletext Interface - Professional Mode', 'system');
        window.udos.addToTerminal('🌟 Try: help, font teletext, saa5050, theme rainbow', 'system');
        window.udos.addToTerminal('📺 Using authentic Teletext50 BBC Micro Mode 7 font', 'system');
    }, 1000);
});