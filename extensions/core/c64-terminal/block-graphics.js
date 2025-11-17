/**
 * uDOS C64 Terminal - Block Graphics Support
 * PETSCII character set and block graphics rendering
 * Version: 1.0.24
 */

(function() {
    'use strict';

    // PETSCII Block Graphics Characters
    const PETSCII_BLOCKS = {
        // Basic blocks
        FULL_BLOCK: '█',
        LIGHT_SHADE: '░',
        MEDIUM_SHADE: '▒',
        DARK_SHADE: '▓',

        // Half blocks
        UPPER_HALF: '▀',
        LOWER_HALF: '▄',
        LEFT_HALF: '▌',
        RIGHT_HALF: '▐',

        // Quarter blocks
        UPPER_LEFT: '▘',
        UPPER_RIGHT: '▝',
        LOWER_LEFT: '▖',
        LOWER_RIGHT: '▗',

        // Box drawing (single)
        BOX_H: '─',
        BOX_V: '│',
        BOX_TL: '┌',
        BOX_TR: '┐',
        BOX_BL: '└',
        BOX_BR: '┘',
        BOX_CROSS: '┼',
        BOX_T_DOWN: '┬',
        BOX_T_UP: '┴',
        BOX_T_RIGHT: '├',
        BOX_T_LEFT: '┤',

        // Box drawing (double)
        DBOX_H: '═',
        DBOX_V: '║',
        DBOX_TL: '╔',
        DBOX_TR: '╗',
        DBOX_BL: '╚',
        DBOX_BR: '╝',
        DBOX_CROSS: '╬',

        // Special characters
        BULLET: '•',
        CIRCLE: '○',
        SQUARE: '□',
        TRIANGLE_UP: '▲',
        TRIANGLE_DOWN: '▼',
        TRIANGLE_LEFT: '◄',
        TRIANGLE_RIGHT: '►',
        HEART: '♥',
        DIAMOND: '♦',
        CLUB: '♣',
        SPADE: '♠',
        NOTE: '♪',
        NOTE2: '♫'
    };

    // Extended character set for graphics
    const GRAPHICS_CHARS = [
        // Row 1: Solid blocks
        '█', '▓', '▒', '░', '▀', '▄', '▌', '▐',
        // Row 2: Box drawing
        '─', '│', '┌', '┐', '└', '┘', '├', '┤',
        // Row 3: Box drawing continued
        '┬', '┴', '┼', '═', '║', '╔', '╗', '╚',
        // Row 4: Double box
        '╝', '╠', '╣', '╦', '╩', '╬', '╭', '╮',
        // Row 5: Rounded corners
        '╯', '╰', '╱', '╲', '╳', '▲', '▼', '◄',
        // Row 6: Triangles and arrows
        '►', '◀', '▶', '▷', '◁', '△', '▽', '◇',
        // Row 7: Shapes
        '◆', '○', '●', '◐', '◑', '◒', '◓', '□',
        // Row 8: More shapes
        '■', '▪', '▫', '▬', '▭', '▮', '▯', '▰',
        // Row 9: Fractions
        '▱', '▲', '△', '▴', '▵', '▶', '▷', '▸',
        // Row 10: More symbols
        '▹', '►', '▻', '▼', '▽', '▾', '▿', '◀',
        // Row 11: Arrows continued
        '◁', '◂', '◃', '◄', '◅', '●', '○', '◎',
        // Row 12: Circles
        '◉', '◊', '○', '◌', '◍', '◎', '●', '◐',
        // Row 13: Special blocks
        '◑', '◒', '◓', '◔', '◕', '◖', '◗', '◘',
        // Row 14: Quarter blocks
        '▖', '▗', '▘', '▙', '▚', '▛', '▜', '▝',
        // Row 15: More blocks
        '▞', '▟', '■', '□', '▢', '▣', '▤', '▥',
        // Row 16: Patterns
        '▦', '▧', '▨', '▩', '▪', '▫', '▬', '▭'
    ];

    /**
     * Initialize block graphics
     */
    function init() {
        // Wait for terminal to be ready
        document.addEventListener('udos:terminal:ready', function() {
            populateCharacterGrid();
        });
    }

    /**
     * Populate the character reference grid
     */
    function populateCharacterGrid() {
        const charGrid = document.getElementById('charGrid');
        if (!charGrid) return;

        charGrid.innerHTML = '';

        GRAPHICS_CHARS.forEach(char => {
            const item = document.createElement('div');
            item.className = 'char-item';
            item.textContent = char;
            item.title = `Unicode: ${char.charCodeAt(0).toString(16)}`;

            // Click to copy
            item.addEventListener('click', function() {
                copyToClipboard(char);
                showCopyNotification(char);
            });

            charGrid.appendChild(item);
        });
    }

    /**
     * Draw a box with title
     */
    function drawBox(width, height, title = '') {
        const chars = PETSCII_BLOCKS;
        let output = '';

        // Top border
        output += chars.DBOX_TL;
        if (title) {
            const titlePad = Math.floor((width - 2 - title.length) / 2);
            output += chars.DBOX_H.repeat(titlePad);
            output += ` ${title} `;
            output += chars.DBOX_H.repeat(width - 2 - titlePad - title.length - 2);
        } else {
            output += chars.DBOX_H.repeat(width - 2);
        }
        output += chars.DBOX_TR + '\n';

        // Middle rows
        for (let i = 0; i < height - 2; i++) {
            output += chars.DBOX_V;
            output += ' '.repeat(width - 2);
            output += chars.DBOX_V + '\n';
        }

        // Bottom border
        output += chars.DBOX_BL;
        output += chars.DBOX_H.repeat(width - 2);
        output += chars.DBOX_BR;

        return output;
    }

    /**
     * Draw a progress bar using block characters
     */
    function drawProgressBar(percent, width = 20) {
        const filled = Math.round((percent / 100) * width);
        const empty = width - filled;

        return PETSCII_BLOCKS.FULL_BLOCK.repeat(filled) +
               PETSCII_BLOCKS.LIGHT_SHADE.repeat(empty);
    }

    /**
     * Create a block pattern
     */
    function createPattern(char, width, height) {
        let output = '';
        for (let y = 0; y < height; y++) {
            output += char.repeat(width);
            if (y < height - 1) output += '\n';
        }
        return output;
    }

    /**
     * Copy to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).catch(err => {
                console.error('Failed to copy:', err);
            });
        } else {
            // Fallback
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    /**
     * Show copy notification
     */
    function showCopyNotification(char) {
        const status = document.getElementById('status');
        if (status) {
            const originalText = status.textContent;
            status.textContent = `COPIED: ${char}`;
            status.style.color = 'var(--c64-yellow)';

            setTimeout(() => {
                status.textContent = originalText;
                status.style.color = '';
            }, 1000);
        }
    }

    // Expose block graphics API
    window.uDOS = window.uDOS || {};
    window.uDOS.blockGraphics = {
        chars: PETSCII_BLOCKS,
        allChars: GRAPHICS_CHARS,
        drawBox: drawBox,
        drawProgressBar: drawProgressBar,
        createPattern: createPattern
    };

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
