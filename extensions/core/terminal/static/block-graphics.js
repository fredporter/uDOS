/**
 * uDOS Terminal - Block Graphics Support
 * C64 PETSCII block characters and drawing functions
 * Version: 1.0.24
 */

(function() {
    'use strict';

    /**
     * C64 Block Graphics Characters
     */
    const BLOCK_CHARS = {
        // Fill blocks
        EMPTY: ' ',
        FULL: '█',
        UPPER_HALF: '▀',
        LOWER_HALF: '▄',
        LEFT_HALF: '▌',
        RIGHT_HALF: '▐',

        // Shading
        LIGHT: '░',
        MEDIUM: '▒',
        DARK: '▓',

        // Quadrants
        QUAD_UL: '▘',
        QUAD_UR: '▝',
        QUAD_LL: '▖',
        QUAD_LR: '▗',
        QUAD_UL_UR: '▀',
        QUAD_LL_LR: '▄',
        QUAD_UL_LL: '▌',
        QUAD_UR_LR: '▐',
        QUAD_UL_UR_LL: '▛',
        QUAD_UL_UR_LR: '▜',
        QUAD_UL_LL_LR: '▙',
        QUAD_UR_LL_LR: '▟',

        // Box drawing
        H_LINE: '─',
        V_LINE: '│',
        TL_CORNER: '┌',
        TR_CORNER: '┐',
        BL_CORNER: '└',
        BR_CORNER: '┘',
        T_DOWN: '┬',
        T_UP: '┴',
        T_RIGHT: '├',
        T_LEFT: '┤',
        CROSS: '┼',

        // Double box drawing
        H_LINE_DBL: '═',
        V_LINE_DBL: '║',
        TL_CORNER_DBL: '╔',
        TR_CORNER_DBL: '╗',
        BL_CORNER_DBL: '╚',
        BR_CORNER_DBL: '╝',
        T_DOWN_DBL: '╦',
        T_UP_DBL: '╩',
        T_RIGHT_DBL: '╠',
        T_LEFT_DBL: '╣',
        CROSS_DBL: '╬',

        // Arrows
        ARROW_UP: '↑',
        ARROW_DOWN: '↓',
        ARROW_LEFT: '←',
        ARROW_RIGHT: '→',
        ARROW_UP_DOWN: '↕',
        ARROW_LEFT_RIGHT: '↔',

        // Misc symbols
        BULLET: '•',
        CIRCLE: '●',
        SQUARE: '■',
        DIAMOND: '◆',
        STAR: '★',
        HEART: '♥',
        CLUB: '♣',
        SPADE: '♠',
        CHECK: '✓',
        CROSS_MARK: '✗',
        MUSIC_NOTE: '♪'
    };

    /**
     * PETSCII Character Set
     */
    const PETSCII_CHARS = {
        // Standard PETSCII characters (subset)
        chars: '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~',

        // Special PETSCII graphics
        graphics: [
            '▘', '▝', '▀', '▖', '▌', '▞', '▛', '▗',
            '▚', '▐', '▜', '▄', '▙', '▟', '█', '░',
            '▒', '▓', '┌', '┐', '└', '┘', '├', '┤',
            '┬', '┴', '┼', '─', '│', '╱', '╲', '╳'
        ]
    };

    /**
     * Block Graphics Drawing Functions
     */
    const BlockGraphics = {
        /**
         * Draw a box with specified characters
         */
        drawBox(width, height, style = 'single') {
            const chars = style === 'double' ? {
                tl: BLOCK_CHARS.TL_CORNER_DBL,
                tr: BLOCK_CHARS.TR_CORNER_DBL,
                bl: BLOCK_CHARS.BL_CORNER_DBL,
                br: BLOCK_CHARS.BR_CORNER_DBL,
                h: BLOCK_CHARS.H_LINE_DBL,
                v: BLOCK_CHARS.V_LINE_DBL
            } : {
                tl: BLOCK_CHARS.TL_CORNER,
                tr: BLOCK_CHARS.TR_CORNER,
                bl: BLOCK_CHARS.BL_CORNER,
                br: BLOCK_CHARS.BR_CORNER,
                h: BLOCK_CHARS.H_LINE,
                v: BLOCK_CHARS.V_LINE
            };

            const lines = [];

            // Top line
            lines.push(chars.tl + chars.h.repeat(width - 2) + chars.tr);

            // Middle lines
            for (let i = 0; i < height - 2; i++) {
                lines.push(chars.v + ' '.repeat(width - 2) + chars.v);
            }

            // Bottom line
            lines.push(chars.bl + chars.h.repeat(width - 2) + chars.br);

            return lines;
        },

        /**
         * Create a progress bar
         */
        progressBar(width, percent, style = 'block') {
            const filled = Math.floor(width * percent / 100);
            const empty = width - filled;

            if (style === 'block') {
                return BLOCK_CHARS.FULL.repeat(filled) + BLOCK_CHARS.LIGHT.repeat(empty);
            } else {
                return '='.repeat(filled) + '-'.repeat(empty);
            }
        },

        /**
         * Create a bar chart
         */
        barChart(value, max, width = 20, char = '█') {
            const filled = Math.floor(width * value / max);
            return char.repeat(filled);
        },

        /**
         * Create a horizontal line
         */
        hLine(width, style = 'single') {
            const char = style === 'double' ? BLOCK_CHARS.H_LINE_DBL : BLOCK_CHARS.H_LINE;
            return char.repeat(width);
        },

        /**
         * Create a separator line with text
         */
        separator(text, width, style = 'single') {
            const chars = style === 'double' ? {
                left: BLOCK_CHARS.T_RIGHT_DBL,
                right: BLOCK_CHARS.T_LEFT_DBL,
                line: BLOCK_CHARS.H_LINE_DBL
            } : {
                left: BLOCK_CHARS.T_RIGHT,
                right: BLOCK_CHARS.T_LEFT,
                line: BLOCK_CHARS.H_LINE
            };

            if (text) {
                const textLen = text.length + 2; // Add spaces around text
                const leftPad = Math.floor((width - textLen) / 2);
                const rightPad = width - textLen - leftPad;

                return chars.left +
                       chars.line.repeat(leftPad) +
                       ' ' + text + ' ' +
                       chars.line.repeat(rightPad) +
                       chars.right;
            } else {
                return chars.left + chars.line.repeat(width - 2) + chars.right;
            }
        }
    };

    /**
     * Initialize character reference grids
     */
    function initCharacterReference() {
        // Wait for terminal ready
        document.addEventListener('udos:terminal:ready', () => {
            const blockGrid = document.getElementById('blockGrid');
            const petsciiGrid = document.getElementById('petsciiGrid');

            if (blockGrid) {
                // Add block graphics
                Object.entries(BLOCK_CHARS).forEach(([name, char]) => {
                    const item = document.createElement('div');
                    item.className = 'char-item';
                    item.textContent = char;
                    item.title = name;
                    item.addEventListener('click', () => copyToClipboard(char, name));
                    blockGrid.appendChild(item);
                });
            }

            if (petsciiGrid) {
                // Add PETSCII characters
                PETSCII_CHARS.graphics.forEach(char => {
                    const item = document.createElement('div');
                    item.className = 'char-item';
                    item.textContent = char;
                    item.addEventListener('click', () => copyToClipboard(char, 'PETSCII'));
                    petsciiGrid.appendChild(item);
                });
            }
        });
    }

    /**
     * Copy character to clipboard
     */
    function copyToClipboard(char, name) {
        navigator.clipboard.writeText(char).then(() => {
            console.log(`[Block Graphics] Copied ${name}: ${char}`);
            if (window.uDOSTerminal) {
                window.uDOSTerminal.printLine(`✓ Copied: ${char} (${name})`, 'output-success');
            }
        }).catch(err => {
            console.error('[Block Graphics] Copy failed:', err);
        });
    }

    // Export to global scope
    window.uDOS = window.uDOS || {};
    window.uDOS.BLOCK_CHARS = BLOCK_CHARS;
    window.uDOS.PETSCII_CHARS = PETSCII_CHARS;
    window.uDOS.BlockGraphics = BlockGraphics;

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCharacterReference);
    } else {
        initCharacterReference();
    }

})();
