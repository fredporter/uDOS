/**
 * uDOS Teletext - Enhanced JavaScript
 * Version: 1.0.24
 *
 * Features:
 * - Responsive scaling
 * - Clock updates
 * - Command processor
 * - C64 block graphics support
 * - Page navigation
 */

(function() {
    'use strict';

    // State
    let currentPage = 100;
    let commandHistory = [];
    let historyIndex = -1;

    /**
     * Fit teletext to viewport
     */
    function fitTeletext() {
        const root = document.documentElement;
        const vw = window.innerWidth - 32;
        const vh = window.innerHeight - 64;
        const fsWidth = vw / (40 * 1.3);
        const fsHeight = vh / 25;
        const fs = Math.max(8, Math.floor(Math.min(fsWidth, fsHeight)));
        root.style.setProperty('--computed-font-size', fs + 'px');
    }

    /**
     * Update clock display
     */
    function tickClock() {
        const clockElement = document.getElementById('clock');
        if (!clockElement) return;

        const now = new Date();
        const pad = n => String(n).padStart(2, '0');
        clockElement.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    }

    /**
     * Update page number display
     */
    function updatePageNumber(page) {
        const pageElement = document.getElementById('pageNumber');
        if (pageElement) {
            pageElement.textContent = String(page).padStart(3, '0');
        }
        currentPage = page;
    }

    /**
     * Command processor
     */
    function processCommand(cmd) {
        const trimmed = cmd.trim().toUpperCase();

        if (!trimmed) return;

        // Add to history
        commandHistory.push(cmd);
        historyIndex = commandHistory.length;

        // Parse command
        const parts = trimmed.split(/\s+/);
        const command = parts[0];
        const args = parts.slice(1);

        switch (command) {
            case 'PAGE':
            case 'P':
                if (args.length > 0) {
                    const pageNum = parseInt(args[0], 10);
                    if (!isNaN(pageNum) && pageNum >= 100 && pageNum <= 899) {
                        updatePageNumber(pageNum);
                        loadPage(pageNum);
                    } else {
                        showStatus('INVALID PAGE NUMBER (100-899)');
                    }
                } else {
                    showStatus(`CURRENT PAGE: ${currentPage}`);
                }
                break;

            case 'NEXT':
            case 'N':
                updatePageNumber(Math.min(899, currentPage + 1));
                loadPage(currentPage);
                break;

            case 'PREV':
            case 'B':
                updatePageNumber(Math.max(100, currentPage - 1));
                loadPage(currentPage);
                break;

            case 'INDEX':
            case 'I':
                updatePageNumber(100);
                loadPage(100);
                break;

            case 'HELP':
            case 'H':
            case '?':
                showHelp();
                break;

            case 'CLEAR':
            case 'CLS':
                clearContent();
                break;

            case 'COLOR':
            case 'COLOUR':
                if (args.length > 0) {
                    setColor(args[0]);
                } else {
                    showStatus('COLOR COMMANDS: RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, WHITE');
                }
                break;

            case 'DEMO':
                showDemo();
                break;

            case 'REVEAL':
                revealConcealed();
                break;

            default:
                // Try parsing as page number
                const pageNum = parseInt(trimmed, 10);
                if (!isNaN(pageNum) && pageNum >= 100 && pageNum <= 899) {
                    updatePageNumber(pageNum);
                    loadPage(pageNum);
                } else {
                    showStatus(`UNKNOWN COMMAND: ${command}`);
                }
        }
    }

    /**
     * Load page (stub - extend for actual content)
     */
    function loadPage(pageNum) {
        showStatus(`LOADING PAGE ${pageNum}...`);

        // In a full implementation, this would load page content
        // For now, just update the display
        setTimeout(() => {
            showStatus(`PAGE ${pageNum} READY`);
        }, 500);
    }

    /**
     * Show status message
     */
    function showStatus(message) {
        const statusElement = document.getElementById('status');
        if (statusElement) {
            statusElement.textContent = message;
            setTimeout(() => {
                statusElement.textContent = 'READY';
            }, 3000);
        }
    }

    /**
     * Show help
     */
    function showHelp() {
        const content = document.getElementById('content');
        if (!content) return;

        const helpText = [
            '┌────────────────────────────────────┐',
            '│ uDOS TELETEXT COMMANDS             │',
            '├────────────────────────────────────┤',
            '│ PAGE nnn  - Go to page nnn         │',
            '│ NEXT      - Next page              │',
            '│ PREV      - Previous page          │',
            '│ INDEX     - Return to page 100     │',
            '│ HELP      - Show this help         │',
            '│ CLEAR     - Clear content          │',
            '│ COLOR c   - Set text color         │',
            '│ DEMO      - Show graphics demo     │',
            '│ REVEAL    - Reveal concealed text  │',
            '├────────────────────────────────────┤',
            '│ Colors: RED GREEN YELLOW BLUE      │',
            '│         CYAN MAGENTA WHITE         │',
            '├────────────────────────────────────┤',
            '│ Or type page number directly       │',
            '└────────────────────────────────────┘'
        ].join('\n');

        const pre = document.createElement('pre');
        pre.className = 'fg-cyan';
        pre.textContent = helpText;
        content.innerHTML = '';
        content.appendChild(pre);
    }

    /**
     * Clear content area
     */
    function clearContent() {
        const content = document.getElementById('content');
        if (content) {
            content.innerHTML = '';
            showStatus('CONTENT CLEARED');
        }
    }

    /**
     * Set text color
     */
    function setColor(colorName) {
        const content = document.getElementById('content');
        if (!content) return;

        const colorClass = 'fg-' + colorName.toLowerCase();
        content.className = colorClass;
        showStatus(`COLOR SET TO ${colorName}`);
    }

    /**
     * Show graphics demo
     */
    function showDemo() {
        const content = document.getElementById('content');
        if (!content) return;

        const blocks = '█▓▒░▀▄▌▐┌┐└┘├┤┬┴┼─│';
        const demo = [];

        // Title
        demo.push('╔════════════════════════════════════╗');
        demo.push('║  C64 BLOCK GRAPHICS DEMONSTRATION  ║');
        demo.push('╚════════════════════════════════════╝');
        demo.push('');

        // Color bars
        demo.push('█ RED    ▓ GREEN  ▒ YELLOW ░ BLUE');
        demo.push('█ CYAN   ▓ PURPLE ▒ ORANGE ░ WHITE');
        demo.push('');

        // Box demo
        demo.push('┌─────────────────┐');
        demo.push('│ SINGLE BOX      │');
        demo.push('└─────────────────┘');
        demo.push('');
        demo.push('╔═════════════════╗');
        demo.push('║ DOUBLE BOX      ║');
        demo.push('╚═════════════════╝');
        demo.push('');

        // Shading demo
        demo.push('SHADING: █ ▓ ▒ ░ (100% to 25%)');
        demo.push('');

        // Block patterns
        demo.push('PATTERNS:');
        demo.push('▀▀▀▀▀▀▀▀  ▄▄▄▄▄▄▄▄  ▌▌▌▌▌▌▌▌  ▐▐▐▐▐▐▐▐');
        demo.push('');

        // Character set sample
        demo.push('CHARACTERS: ' + blocks);

        const pre = document.createElement('pre');
        pre.className = 'mosaic fg-light-blue';
        pre.textContent = demo.join('\n');
        content.innerHTML = '';
        content.appendChild(pre);

        showStatus('GRAPHICS DEMO LOADED');
    }

    /**
     * Reveal concealed text
     */
    function revealConcealed() {
        const concealed = document.querySelectorAll('.conceal');
        concealed.forEach(el => {
            el.classList.remove('conceal');
            el.classList.add('fg-yellow');
        });
        showStatus(`REVEALED ${concealed.length} CONCEALED ITEMS`);
    }

    /**
     * Handle command input
     */
    function setupCommandInput() {
        const commandInput = document.getElementById('commandInput');
        if (!commandInput) return;

        commandInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const cmd = this.value;
                processCommand(cmd);
                this.value = '';
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    this.value = commandHistory[historyIndex] || '';
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    this.value = commandHistory[historyIndex] || '';
                } else {
                    historyIndex = commandHistory.length;
                    this.value = '';
                }
            }
        });

        // Focus on load
        commandInput.focus();
    }

    /**
     * Initialize
     */
    function init() {
        // Responsive scaling
        fitTeletext();
        window.addEventListener('resize', fitTeletext, { passive: true });

        // Clock
        tickClock();
        setInterval(tickClock, 1000);

        // Command input
        setupCommandInput();

        // Update page number
        updatePageNumber(100);

        // Show initial status
        showStatus('TELETEXT READY - TYPE HELP FOR COMMANDS');

        // Expose API
        window.uDOS = window.uDOS || {};
        window.uDOS.teletext = {
            processCommand,
            loadPage,
            updatePage: updatePageNumber,
            showStatus,
            showHelp,
            showDemo,
            clearContent,
            setColor,
            revealConcealed
        };
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
