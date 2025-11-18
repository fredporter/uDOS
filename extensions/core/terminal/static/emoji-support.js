/**
 * uDOS Terminal - Monosort Emoji Support
 * Monochrome emoji integration for terminal display
 * Version: 1.0.24
 */

(function() {
    'use strict';

    /**
     * Monosort Emoji Set
     * Monochrome emoji suitable for terminal display
     */
    const MONOSORT_EMOJI = {
        // System & Interface
        ROCKET: '🚀',
        GEAR: '⚙',
        WRENCH: '🔧',
        HAMMER: '🔨',
        KEY: '🔑',
        LOCK: '🔒',
        UNLOCK: '🔓',
        BELL: '🔔',
        MAGNIFY: '🔍',
        BULB: '💡',

        // Status & Indicators
        CHECK: '✅',
        CROSS: '❌',
        WARNING: '⚠',
        INFO: 'ℹ',
        QUESTION: '❓',
        EXCLAIM: '❗',
        STAR: '⭐',
        SPARKLE: '✨',
        ZAP: '⚡',
        FIRE: '🔥',

        // Navigation
        UP: '⬆',
        DOWN: '⬇',
        LEFT: '⬅',
        RIGHT: '➡',
        BACK: '◀',
        FORWARD: '▶',
        PLAY: '▶',
        PAUSE: '⏸',
        STOP: '⏹',
        RECORD: '⏺',

        // Files & Data
        FILE: '📄',
        FOLDER: '📁',
        FOLDER_OPEN: '📂',
        PAGE: '📃',
        BOOK: '📚',
        NOTEBOOK: '📓',
        CLIPBOARD: '📋',
        CHART: '📊',
        GRAPH: '📈',
        DATABASE: '🗄',

        // Communication
        MAIL: '📧',
        MESSAGE: '💬',
        SPEECH: '💭',
        PHONE: '📞',
        BROADCAST: '📡',
        SATELLITE: '🛰',

        // Objects
        COMPUTER: '💻',
        KEYBOARD: '⌨',
        MOUSE: '🖱',
        PRINTER: '🖨',
        DESKTOP: '🖥',
        LAPTOP: '💻',
        MOBILE: '📱',
        BATTERY: '🔋',
        PLUG: '🔌',

        // Misc
        CLOCK: '🕐',
        CALENDAR: '📅',
        PIN: '📌',
        LINK: '🔗',
        CAMERA: '📷',
        VIDEO: '📹',
        MUSIC: '🎵',
        SPEAKER: '🔊',
        MUTE: '🔇',

        // Nature (simplified)
        SUN: '☀',
        MOON: '🌙',
        CLOUD: '☁',
        RAIN: '🌧',
        SNOW: '❄',

        // Symbols
        HEART: '❤',
        DIAMOND: '💎',
        CROWN: '👑',
        TROPHY: '🏆',
        FLAG: '🚩',
        TARGET: '🎯',
        DICE: '🎲',
        JOYSTICK: '🕹',

        // Science & Tech
        ATOM: '⚛',
        DNA: '🧬',
        MAGNET: '🧲',
        MICROSCOPE: '🔬',
        TELESCOPE: '🔭',
        SATELLITE_DISH: '📡',
        ROBOT: '🤖',
        ALIEN: '👽'
    };

    /**
     * Emoji categories for reference panel
     */
    const EMOJI_CATEGORIES = {
        'SYSTEM': ['ROCKET', 'GEAR', 'WRENCH', 'HAMMER', 'KEY', 'LOCK', 'BULB'],
        'STATUS': ['CHECK', 'CROSS', 'WARNING', 'INFO', 'STAR', 'ZAP', 'FIRE'],
        'FILES': ['FILE', 'FOLDER', 'BOOK', 'CLIPBOARD', 'CHART', 'DATABASE'],
        'TECH': ['COMPUTER', 'LAPTOP', 'MOBILE', 'KEYBOARD', 'BATTERY', 'ROBOT'],
        'NAV': ['UP', 'DOWN', 'LEFT', 'RIGHT', 'PLAY', 'PAUSE', 'STOP']
    };

    /**
     * Emoji utility functions
     */
    const EmojiUtils = {
        /**
         * Get emoji by name
         */
        get(name) {
            return MONOSORT_EMOJI[name.toUpperCase()] || '�';
        },

        /**
         * Check if text contains emoji
         */
        hasEmoji(text) {
            const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u;
            return emojiRegex.test(text);
        },

        /**
         * Replace emoji codes in text (:rocket: -> 🚀)
         */
        replaceEmojiCodes(text) {
            return text.replace(/:(\w+):/g, (match, name) => {
                const emoji = MONOSORT_EMOJI[name.toUpperCase()];
                return emoji || match;
            });
        },

        /**
         * Create emoji status indicator
         */
        statusIcon(type) {
            const icons = {
                success: MONOSORT_EMOJI.CHECK,
                error: MONOSORT_EMOJI.CROSS,
                warning: MONOSORT_EMOJI.WARNING,
                info: MONOSORT_EMOJI.INFO,
                loading: MONOSORT_EMOJI.GEAR,
                ready: MONOSORT_EMOJI.ROCKET
            };
            return icons[type] || MONOSORT_EMOJI.INFO;
        },

        /**
         * Create emoji progress indicator
         */
        progressIcon(percent) {
            if (percent >= 100) return MONOSORT_EMOJI.CHECK;
            if (percent >= 75) return MONOSORT_EMOJI.FIRE;
            if (percent >= 50) return MONOSORT_EMOJI.ZAP;
            if (percent >= 25) return MONOSORT_EMOJI.BULB;
            return MONOSORT_EMOJI.CLOCK;
        }
    };

    /**
     * Initialize emoji reference grid
     */
    function initEmojiReference() {
        document.addEventListener('udos:terminal:ready', () => {
            const emojiGrid = document.getElementById('emojiGrid');

            if (emojiGrid) {
                // Create category sections
                Object.entries(EMOJI_CATEGORIES).forEach(([category, emojiNames]) => {
                    const categoryDiv = document.createElement('div');
                    categoryDiv.className = 'emoji-category';

                    const categoryTitle = document.createElement('h5');
                    categoryTitle.textContent = category;
                    categoryTitle.style.cssText = 'margin: 1rem 0 0.5rem; color: var(--color-cyan-bright); font-size: 0.8rem;';
                    emojiGrid.appendChild(categoryTitle);

                    const categoryGrid = document.createElement('div');
                    categoryGrid.className = 'emoji-grid';
                    categoryGrid.style.cssText = 'display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.5rem; margin-bottom: 1rem;';

                    emojiNames.forEach(name => {
                        const emoji = MONOSORT_EMOJI[name];
                        if (emoji) {
                            const item = document.createElement('div');
                            item.className = 'emoji-item';
                            item.textContent = emoji;
                            item.title = name;
                            item.addEventListener('click', () => copyEmoji(emoji, name));
                            categoryGrid.appendChild(item);
                        }
                    });

                    emojiGrid.appendChild(categoryGrid);
                });
            }
        });
    }

    /**
     * Copy emoji to clipboard
     */
    function copyEmoji(emoji, name) {
        navigator.clipboard.writeText(emoji).then(() => {
            console.log(`[Emoji] Copied ${name}: ${emoji}`);
            if (window.uDOSTerminal) {
                window.uDOSTerminal.printLine(`✓ Copied emoji: ${emoji} (${name})`, 'output-success');
            }
        }).catch(err => {
            console.error('[Emoji] Copy failed:', err);
        });
    }

    /**
     * Add emoji support to terminal commands
     */
    function enhanceTerminalWithEmoji() {
        document.addEventListener('udos:terminal:ready', () => {
            // Intercept terminal output to process emoji codes
            if (window.uDOSTerminal) {
                const originalPrintLine = window.uDOSTerminal.printLine;

                window.uDOSTerminal.printLine = function(text, className) {
                    // Replace emoji codes like :rocket: with actual emoji
                    const processedText = EmojiUtils.replaceEmojiCodes(text);
                    originalPrintLine.call(this, processedText, className);
                };
            }
        });
    }

    // Export to global scope
    window.uDOS = window.uDOS || {};
    window.uDOS.MONOSORT_EMOJI = MONOSORT_EMOJI;
    window.uDOS.EmojiUtils = EmojiUtils;

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initEmojiReference();
            enhanceTerminalWithEmoji();
        });
    } else {
        initEmojiReference();
        enhanceTerminalWithEmoji();
    }

})();
