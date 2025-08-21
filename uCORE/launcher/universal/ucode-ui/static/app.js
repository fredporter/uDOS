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
        this.currentFont = 'teletext';  // Default to authentic BBC Micro Mode 7
        this.currentTheme = 'professional';  // Professional mode default
        this.init();
    }

    init() {
        // Initialize Socket.IO connection
        this.socket = io();
        this.setupEventListeners();
        this.setupSocketHandlers();
        this.startPromptRotation();
        
        // Set default font and theme
        document.body.classList.add('font-teletext');
        document.body.classList.add('theme-professional');
        
        // Focus command input
        document.getElementById('command-input').focus();
    }

    setupEventListeners() {
        const commandInput = document.getElementById('command-input');
        
        // Handle command input
        commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.executeCommand(commandInput.value.trim());
                commandInput.value = '';
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
        
        // Display command
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

    handleLocalCommand(command) {
        const cmd = command.toLowerCase().trim();
        
        if (cmd === 'help') {
            this.addToTerminal('🎮 uDOS Commands:', 'info');
            this.addToTerminal('  help       - Show this help', 'output');
            this.addToTerminal('  status     - Show system status', 'output');
            this.addToTerminal('  rainbow    - Activate rainbow mode', 'output');
            this.addToTerminal('  whirlwind  - Activate whirlwind prompts', 'output');
            this.addToTerminal('  font [name] - Change font (teletext/c64/terminal)', 'output');
            this.addToTerminal('  saa5050    - Show SAA5050 block graphics', 'output');
            this.addToTerminal('  clear      - Clear terminal', 'output');
            this.addToTerminal('  ascii      - Show ASCII art demo', 'output');
            this.addToTerminal('  theme [name] - Change theme (dark/light/professional/rainbow)', 'output');
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
        // Optional: Add dynamic prompt effects here
        setInterval(() => {
            this.updatePrompt();
        }, 5000);
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
        terminal.scrollTop = terminal.scrollHeight;
    }

    changeFont(fontName) {
        // Remove all font classes
        document.body.classList.remove('font-teletext', 'font-acorn', 'font-c64', 'font-terminal');
        
        const validFonts = ['teletext', 'c64', 'terminal'];
        if (validFonts.includes(fontName)) {
            this.currentFont = fontName;
            document.body.classList.add(`font-${fontName}`);
            this.addToTerminal(`🎨 Font changed to ${fontName}`, 'success');
        } else {
            this.addToTerminal(`❌ Unknown font: ${fontName}\nAvailable: ${validFonts.join(', ')}`, 'error');
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
        this.currentFont = 'teletext';  // Reset to Teletext50 BBC Micro Mode 7 default
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