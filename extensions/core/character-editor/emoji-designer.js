/**
 * uDOS Font Manager - Emoji Designer (Stub)
 * Version: 1.0.24
 *
 * Full-color emoji designer (32×32 grid)
 * To be expanded in future versions
 */

class EmojiDesigner {
    constructor() {
        this.canvas = document.getElementById('emojiCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.gridSize = 32;
        this.cellSize = 16; // 512 / 32
        this.currentColor = '#AAFFEE';
        this.palette = [
            '#000000', '#FFFFFF', '#880000', '#AAFFEE',
            '#CC44CC', '#00CC55', '#0000AA', '#EEEE77',
            '#DD8855', '#664400', '#FF7777', '#333333',
            '#777777', '#AAFF66', '#0088FF', '#BBBBBB'
        ];

        this.init();
    }

    init() {
        if (!this.canvas || !this.ctx) return;

        this.setupPalette();
        this.renderCanvas();
    }

    setupPalette() {
        const paletteGrid = document.getElementById('emojiPalette');
        if (!paletteGrid) return;

        paletteGrid.innerHTML = '';

        this.palette.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'color-swatch';
            swatch.style.backgroundColor = color;
            swatch.title = color;

            swatch.addEventListener('click', () => {
                this.currentColor = color;
                document.querySelectorAll('.color-swatch').forEach(s => {
                    s.classList.remove('active');
                });
                swatch.classList.add('active');
            });

            paletteGrid.appendChild(swatch);
        });

        // Set first color as active
        paletteGrid.querySelector('.color-swatch')?.classList.add('active');
    }

    renderCanvas() {
        if (!this.ctx) return;

        // Clear with white background
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.ctx.strokeStyle = '#DDDDDD';
        this.ctx.lineWidth = 1;

        for (let i = 0; i <= this.gridSize; i++) {
            // Vertical
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.cellSize, 0);
            this.ctx.lineTo(i * this.cellSize, this.canvas.height);
            this.ctx.stroke();

            // Horizontal
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.cellSize);
            this.ctx.lineTo(this.canvas.width, i * this.cellSize);
            this.ctx.stroke();
        }

        // Placeholder text
        this.ctx.fillStyle = '#999999';
        this.ctx.font = '14px monospace';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('Emoji Designer', this.canvas.width / 2, this.canvas.height / 2 - 10);
        this.ctx.fillText('(Coming in v1.0.25)', this.canvas.width / 2, this.canvas.height / 2 + 10);
    }
}

// Export for use in main app
window.EmojiDesigner = EmojiDesigner;

// Auto-initialize when tab is activated
document.addEventListener('DOMContentLoaded', () => {
    const emojiTab = document.querySelector('[data-tab="emoji"]');
    if (emojiTab) {
        emojiTab.addEventListener('click', () => {
            if (!window.emojiDesigner) {
                window.emojiDesigner = new EmojiDesigner();
            }
        });
    }
});
