/**
 * uDOS Display Management System
 * Handles viewport, display modes, and authentic retro computer display standards
 */

class uDOSDisplayManager {
    constructor() {
        this.currentDisplayMode = 'modern';
        this.displayModes = {
            'bbc': { width: 320, height: 250, chars: [40, 25], aspect: 1.28 },
            'c64': { width: 320, height: 200, chars: [40, 25], aspect: 1.6 },
            'amiga-pal': { width: 640, height: 256, chars: [80, 32], aspect: 2.5 },
            'amiga-ntsc': { width: 640, height: 200, chars: [80, 25], aspect: 3.2 },
            'terminal': { width: 720, height: 384, chars: [80, 24], aspect: 1.875 },
            'modern': { width: 1024, height: 768, chars: [80, 40], aspect: 1.33 }
        };
        this.kioskMode = false;
        this.pixelPerfect = false;
        
        this.initializeDisplay();
    }

    initializeDisplay() {
        // Add display CSS if not already included
        if (!document.querySelector('link[href*="display.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'static/display.css';
            document.head.appendChild(link);
        }
    }

    /**
     * Set display mode using uDOS commands
     * DISPLAY BBC, DISPLAY C64, DISPLAY AMIGA, etc.
     */
    setDisplayMode(mode) {
        const modeKey = mode.toLowerCase().replace(/[-_\s]/g, '');
        
        // Handle mode aliases
        const modeAliases = {
            'mode7': 'bbc',
            'teletext': 'bbc',
            'commodore': 'c64',
            'commodore64': 'c64',
            'amiga': 'amiga-pal',
            'workbench': 'amiga-pal',
            'vt100': 'terminal',
            'vt220': 'terminal'
        };
        
        const targetMode = modeAliases[modeKey] || modeKey;
        
        if (!this.displayModes[targetMode]) {
            console.error(`Unknown display mode: ${mode}`);
            return false;
        }

        this.currentDisplayMode = targetMode;
        this.applyDisplayMode(targetMode);
        return true;
    }

    applyDisplayMode(mode) {
        const config = this.displayModes[mode];
        const body = document.body;
        const mainInterface = document.querySelector('.main-interface');
        const terminalOutputs = document.querySelectorAll('.terminal-output');

        // Remove existing display mode classes
        body.classList.remove(...Object.keys(this.displayModes).map(m => `display-mode-${m}`));
        body.classList.remove('viewport-teletext', 'viewport-c64', 'viewport-amiga');

        // Apply new display mode
        body.classList.add(`display-mode-${mode}`);

        // Set viewport optimization
        if (mode === 'bbc') {
            body.classList.add('viewport-teletext');
        } else if (mode === 'c64') {
            body.classList.add('viewport-c64');
        } else if (mode.startsWith('amiga')) {
            body.classList.add('viewport-amiga');
        }

        // Apply terminal sizing
        terminalOutputs.forEach(terminal => {
            terminal.classList.remove('display-bbc', 'display-c64', 'display-amiga');
            if (mode === 'bbc') {
                terminal.classList.add('display-bbc');
            } else if (mode === 'c64') {
                terminal.classList.add('display-c64');
            } else if (mode.startsWith('amiga')) {
                terminal.classList.add('display-amiga');
            }
        });

        // Update CSS custom properties for the current mode
        document.documentElement.style.setProperty('--display-width', `${config.width}px`);
        document.documentElement.style.setProperty('--display-height', `${config.height}px`);
        document.documentElement.style.setProperty('--display-aspect', config.aspect);
        document.documentElement.style.setProperty('--char-cols', config.chars[0]);
        document.documentElement.style.setProperty('--char-rows', config.chars[1]);

        this.logDisplayChange(mode, config);
    }

    /**
     * Set specific window size using uDOS SIZE command
     * SIZE 320x200, SIZE 640x480, etc.
     */
    setWindowSize(sizeSpec) {
        const sizeMatch = sizeSpec.match(/(\d+)x(\d+)/i);
        if (!sizeMatch) {
            console.error(`Invalid size specification: ${sizeSpec}`);
            return false;
        }

        const [, width, height] = sizeMatch;
        const className = `window-size-${width}x${height}`;
        
        // Remove existing size classes
        document.body.classList.remove(...Array.from(document.body.classList).filter(c => c.startsWith('window-size-')));
        
        // Apply new size
        document.body.classList.add(className);
        
        // Update viewport meta tag for specific sizing
        this.updateViewportMeta(parseInt(width), parseInt(height));
        
        this.logSizeChange(width, height);
        return true;
    }

    /**
     * Toggle kiosk mode (fullscreen, no browser UI)
     * KIOSK ON/OFF
     */
    toggleKioskMode(enable = null) {
        this.kioskMode = enable !== null ? enable : !this.kioskMode;
        
        if (this.kioskMode) {
            document.body.classList.add('kiosk-mode');
            // Request fullscreen if available
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log('Fullscreen request failed:', err);
                });
            }
        } else {
            document.body.classList.remove('kiosk-mode');
            // Exit fullscreen if active
            if (document.fullscreenElement && document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
        
        this.logKioskChange();
        return this.kioskMode;
    }

    /**
     * Toggle pixel perfect rendering
     * PIXELS ON/OFF
     */
    togglePixelPerfect(enable = null) {
        this.pixelPerfect = enable !== null ? enable : !this.pixelPerfect;
        
        if (this.pixelPerfect) {
            document.body.classList.add('pixel-perfect');
        } else {
            document.body.classList.remove('pixel-perfect');
        }
        
        this.logPixelChange();
        return this.pixelPerfect;
    }

    /**
     * Update viewport meta tag for specific dimensions
     */
    updateViewportMeta(width, height) {
        let viewportMeta = document.querySelector('meta[name="viewport"]');
        if (!viewportMeta) {
            viewportMeta = document.createElement('meta');
            viewportMeta.name = 'viewport';
            document.head.appendChild(viewportMeta);
        }
        
        // Set viewport for authentic retro experience
        const scale = Math.min(window.innerWidth / width, window.innerHeight / height, 1);
        viewportMeta.content = `width=${width}, height=${height}, initial-scale=${scale}, user-scalable=no`;
    }

    /**
     * Get current display information
     */
    getDisplayInfo() {
        const config = this.displayModes[this.currentDisplayMode];
        return {
            mode: this.currentDisplayMode,
            width: config.width,
            height: config.height,
            chars: config.chars,
            aspect: config.aspect,
            kioskMode: this.kioskMode,
            pixelPerfect: this.pixelPerfect
        };
    }

    /**
     * Create a lean Chromium browser command
     */
    setWindowSize(sizeSpec) {
        // Parse size specification (e.g., "640x480")
        const match = sizeSpec.match(/^(\d+)x(\d+)$/);
        if (!match) return false;
        
        const width = parseInt(match[1]);
        const height = parseInt(match[2]);
        
        // Update CSS custom properties for window size
        document.documentElement.style.setProperty('--window-width', `${width}px`);
        document.documentElement.style.setProperty('--window-height', `${height}px`);
        
        // If we have a browser integration, resize the window
        if (window.uDOSChromium) {
            window.uDOSChromium.resizeWindow(width, height);
        }
        
        this.addMessage(`📏 Window size set to ${width}×${height}`, 'info');
        return true;
    }
    
    togglePixelPerfect(enable = null) {
        if (enable === null) {
            this.pixelPerfect = !this.pixelPerfect;
        } else {
            this.pixelPerfect = enable;
        }
        
        // Apply pixel perfect rendering settings
        if (this.pixelPerfect) {
            document.documentElement.classList.add('pixel-perfect');
            document.documentElement.style.setProperty('--font-smoothing', 'none');
            document.documentElement.style.setProperty('--image-rendering', 'pixelated');
        } else {
            document.documentElement.classList.remove('pixel-perfect');
            document.documentElement.style.setProperty('--font-smoothing', 'auto');
            document.documentElement.style.setProperty('--image-rendering', 'auto');
        }
        
        this.addMessage(`🎨 Pixel perfect rendering ${this.pixelPerfect ? 'enabled' : 'disabled'}`, 'info');
        return this.pixelPerfect;
    }
    
    getDisplayInfo() {
        const currentMode = this.modes[this.currentMode];
        return {
            mode: this.currentMode,
            width: currentMode.width,
            height: currentMode.height,
            chars: currentMode.chars,
            aspect: currentMode.aspect,
            kioskMode: this.kioskMode,
            pixelPerfect: this.pixelPerfect
        };
    }

    // Logging methods
    logDisplayChange(mode, config) {
        if (window.uDOSInterface) {
            window.uDOSInterface.addToTerminal(`📺 Display mode: ${mode.toUpperCase()}`, 'success');
            window.uDOSInterface.addToTerminal(`📐 Resolution: ${config.width}×${config.height} (${config.chars[0]}×${config.chars[1]} chars)`, 'info');
            window.uDOSInterface.addToTerminal(`📏 Aspect ratio: ${config.aspect}:1`, 'info');
        }
    }

    logSizeChange(width, height) {
        if (window.uDOSInterface) {
            window.uDOSInterface.addToTerminal(`📏 Window size: ${width}×${height}`, 'success');
        }
    }

    logKioskChange() {
        if (window.uDOSInterface) {
            const status = this.kioskMode ? 'ON' : 'OFF';
            window.uDOSInterface.addToTerminal(`🖥️  Kiosk mode: ${status}`, 'success');
        }
    }

    logPixelChange() {
        if (window.uDOSInterface) {
            const status = this.pixelPerfect ? 'ON' : 'OFF';
            window.uDOSInterface.addToTerminal(`🔲 Pixel perfect: ${status}`, 'success');
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = uDOSDisplayManager;
} else {
    window.uDOSDisplayManager = uDOSDisplayManager;
}
