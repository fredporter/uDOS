/**
 * uDOS Font Manager - Bitmap Editor
 * Version: 1.0.24
 *
 * 16×16 grid bitmap font editor
 */

class BitmapEditor {
    constructor() {
        this.canvas = document.getElementById('gridCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;

        this.gridSize = 16;
        this.cellSize = 32; // Canvas pixels per grid cell
        this.currentChar = 'A';
        this.currentTool = 'draw';
        this.isDrawing = false;
        this.clipboard = null;
        this.undoStack = [];

        // Font data storage
        this.fontData = this.loadFromLocalStorage() || this.createEmptyFont();

        this.init();
    }

    /**
     * Initialize editor
     */
    init() {
        if (!this.canvas || !this.ctx) return;

        this.setupEventListeners();
        this.populateCharSelect();
        this.populateCharset();
        this.renderGrid();
        this.updateStats();
    }

    /**
     * Create empty font data
     */
    createEmptyFont() {
        const font = {
            name: 'Untitled Font',
            version: '1.0.0',
            gridSize: 16,
            glyphs: {}
        };

        // Initialize empty grids for common characters
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';
        chars.split('').forEach(char => {
            font.glyphs[char] = this.createEmptyGrid();
        });

        return font;
    }

    /**
     * Create empty grid
     */
    createEmptyGrid() {
        return Array(this.gridSize).fill(null).map(() =>
            Array(this.gridSize).fill(0)
        );
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Canvas drawing
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseleave', () => this.stopDrawing());
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // Character selection
        document.getElementById('charSelect')?.addEventListener('change', (e) => {
            this.currentChar = e.target.value;
            this.renderGrid();
        });

        document.getElementById('btnPrevChar')?.addEventListener('click', () => this.prevChar());
        document.getElementById('btnNextChar')?.addEventListener('click', () => this.nextChar());

        // Tools
        document.getElementById('btnDraw')?.addEventListener('click', () => this.setTool('draw'));
        document.getElementById('btnErase')?.addEventListener('click', () => this.setTool('erase'));
        document.getElementById('btnFill')?.addEventListener('click', () => this.fillGrid());
        document.getElementById('btnLine')?.addEventListener('click', () => this.setTool('line'));

        // Transforms
        document.getElementById('btnFlipH')?.addEventListener('click', () => this.flipHorizontal());
        document.getElementById('btnFlipV')?.addEventListener('click', () => this.flipVertical());
        document.getElementById('btnRotateCW')?.addEventListener('click', () => this.rotate(90));
        document.getElementById('btnRotateCCW')?.addEventListener('click', () => this.rotate(-90));
        document.getElementById('btnInvert')?.addEventListener('click', () => this.invert());

        // Edit
        document.getElementById('btnClear')?.addEventListener('click', () => this.clearGrid());
        document.getElementById('btnCopy')?.addEventListener('click', () => this.copy());
        document.getElementById('btnPaste')?.addEventListener('click', () => this.paste());
        document.getElementById('btnUndo')?.addEventListener('click', () => this.undo());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    /**
     * Set current tool
     */
    setTool(tool) {
        this.currentTool = tool;

        // Update button states
        document.querySelectorAll('.btn-tool').forEach(btn => {
            btn.classList.remove('active');
        });

        const toolMap = {
            draw: 'btnDraw',
            erase: 'btnErase',
            line: 'btnLine'
        };

        if (toolMap[tool]) {
            document.getElementById(toolMap[tool])?.classList.add('active');
        }
    }

    /**
     * Start drawing
     */
    startDrawing(e) {
        this.isDrawing = true;
        this.saveToUndo();
        this.draw(e);
    }

    /**
     * Draw on grid
     */
    draw(e) {
        if (!this.isDrawing) return;

        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / this.cellSize);
        const y = Math.floor((e.clientY - rect.top) / this.cellSize);

        if (x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize) {
            const grid = this.getCharGrid();

            if (this.currentTool === 'draw' || e.buttons === 1) {
                grid[y][x] = 1;
            } else if (this.currentTool === 'erase' || e.buttons === 2) {
                grid[y][x] = 0;
            }

            this.renderGrid();
            this.updateCharset();
            this.saveToLocalStorage();
        }
    }

    /**
     * Stop drawing
     */
    stopDrawing() {
        this.isDrawing = false;
    }

    /**
     * Render grid
     */
    renderGrid() {
        if (!this.ctx) return;

        const grid = this.getCharGrid();

        // Clear canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw cells
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                if (grid[y][x] === 1) {
                    this.ctx.fillStyle = '#AAFFEE'; // C64 Cyan
                    this.ctx.fillRect(
                        x * this.cellSize,
                        y * this.cellSize,
                        this.cellSize,
                        this.cellSize
                    );
                }
            }
        }

        // Draw grid lines
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;

        for (let i = 0; i <= this.gridSize; i++) {
            // Vertical lines
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.cellSize, 0);
            this.ctx.lineTo(i * this.cellSize, this.canvas.height);
            this.ctx.stroke();

            // Horizontal lines
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.cellSize);
            this.ctx.lineTo(this.canvas.width, i * this.cellSize);
            this.ctx.stroke();
        }

        // Update character display
        document.getElementById('charDisplay').textContent = this.currentChar;
    }

    /**
     * Get current character grid
     */
    getCharGrid() {
        if (!this.fontData.glyphs[this.currentChar]) {
            this.fontData.glyphs[this.currentChar] = this.createEmptyGrid();
        }
        return this.fontData.glyphs[this.currentChar];
    }

    /**
     * Populate character select
     */
    populateCharSelect() {
        const select = document.getElementById('charSelect');
        if (!select) return;

        select.innerHTML = '';

        const chars = Object.keys(this.fontData.glyphs).sort();
        chars.forEach(char => {
            const option = document.createElement('option');
            option.value = char;
            option.textContent = `${char} (${char.charCodeAt(0)})`;
            select.appendChild(option);
        });

        select.value = this.currentChar;
    }

    /**
     * Populate character set preview
     */
    populateCharset() {
        const grid = document.getElementById('charsetGrid');
        if (!grid) return;

        grid.innerHTML = '';

        const chars = Object.keys(this.fontData.glyphs).sort();
        chars.forEach(char => {
            const item = document.createElement('div');
            item.className = 'charset-item';
            item.textContent = char;
            item.title = char;

            if (char === this.currentChar) {
                item.classList.add('active');
            }

            item.addEventListener('click', () => {
                this.currentChar = char;
                document.getElementById('charSelect').value = char;
                this.renderGrid();
                this.populateCharset();
            });

            grid.appendChild(item);
        });
    }

    /**
     * Update character in charset preview
     */
    updateCharset() {
        this.populateCharset();
    }

    /**
     * Transform operations
     */
    flipHorizontal() {
        this.saveToUndo();
        const grid = this.getCharGrid();
        grid.forEach(row => row.reverse());
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
    }

    flipVertical() {
        this.saveToUndo();
        const grid = this.getCharGrid();
        grid.reverse();
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
    }

    rotate(degrees) {
        this.saveToUndo();
        const grid = this.getCharGrid();
        const newGrid = this.createEmptyGrid();

        if (degrees === 90) {
            for (let y = 0; y < this.gridSize; y++) {
                for (let x = 0; x < this.gridSize; x++) {
                    newGrid[x][this.gridSize - 1 - y] = grid[y][x];
                }
            }
        } else if (degrees === -90) {
            for (let y = 0; y < this.gridSize; y++) {
                for (let x = 0; x < this.gridSize; x++) {
                    newGrid[this.gridSize - 1 - x][y] = grid[y][x];
                }
            }
        }

        this.fontData.glyphs[this.currentChar] = newGrid;
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
    }

    invert() {
        this.saveToUndo();
        const grid = this.getCharGrid();
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                grid[y][x] = grid[y][x] === 1 ? 0 : 1;
            }
        }
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
    }

    /**
     * Edit operations
     */
    clearGrid() {
        if (confirm('Clear current character?')) {
            this.saveToUndo();
            this.fontData.glyphs[this.currentChar] = this.createEmptyGrid();
            this.renderGrid();
            this.updateCharset();
            this.saveToLocalStorage();
        }
    }

    fillGrid() {
        this.saveToUndo();
        const grid = this.getCharGrid();
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                grid[y][x] = 1;
            }
        }
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
    }

    copy() {
        this.clipboard = JSON.parse(JSON.stringify(this.getCharGrid()));
        this.showStatus('Character copied');
    }

    paste() {
        if (!this.clipboard) {
            this.showStatus('Nothing to paste');
            return;
        }

        this.saveToUndo();
        this.fontData.glyphs[this.currentChar] = JSON.parse(JSON.stringify(this.clipboard));
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
        this.showStatus('Character pasted');
    }

    undo() {
        if (this.undoStack.length === 0) {
            this.showStatus('Nothing to undo');
            return;
        }

        this.fontData.glyphs[this.currentChar] = this.undoStack.pop();
        this.renderGrid();
        this.updateCharset();
        this.saveToLocalStorage();
        this.showStatus('Undone');
    }

    saveToUndo() {
        this.undoStack.push(JSON.parse(JSON.stringify(this.getCharGrid())));
        if (this.undoStack.length > 20) {
            this.undoStack.shift();
        }
    }

    /**
     * Navigation
     */
    prevChar() {
        const chars = Object.keys(this.fontData.glyphs).sort();
        const idx = chars.indexOf(this.currentChar);
        if (idx > 0) {
            this.currentChar = chars[idx - 1];
            document.getElementById('charSelect').value = this.currentChar;
            this.renderGrid();
            this.populateCharset();
        }
    }

    nextChar() {
        const chars = Object.keys(this.fontData.glyphs).sort();
        const idx = chars.indexOf(this.currentChar);
        if (idx < chars.length - 1) {
            this.currentChar = chars[idx + 1];
            document.getElementById('charSelect').value = this.currentChar;
            this.renderGrid();
            this.populateCharset();
        }
    }

    /**
     * Keyboard shortcuts
     */
    handleKeyboard(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch (e.key.toLowerCase()) {
            case 'd':
                this.setTool('draw');
                break;
            case 'e':
                this.setTool('erase');
                break;
            case 'f':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.fillGrid();
                }
                break;
            case 'c':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.copy();
                }
                break;
            case 'v':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.paste();
                }
                break;
            case 'z':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.undo();
                }
                break;
            case 'arrowleft':
                e.preventDefault();
                this.prevChar();
                break;
            case 'arrowright':
                e.preventDefault();
                this.nextChar();
                break;
        }
    }

    /**
     * Update statistics
     */
    updateStats() {
        const total = Object.keys(this.fontData.glyphs).length;
        let defined = 0;

        Object.values(this.fontData.glyphs).forEach(grid => {
            const hasPixels = grid.some(row => row.some(cell => cell === 1));
            if (hasPixels) defined++;
        });

        document.getElementById('statChars').textContent = total;
        document.getElementById('statDefined').textContent = defined;
        document.getElementById('statEmpty').textContent = total - defined;
    }

    /**
     * Show status message
     */
    showStatus(message) {
        const statusEl = document.getElementById('statusMessage');
        if (statusEl) {
            statusEl.textContent = message;
            setTimeout(() => {
                statusEl.textContent = 'Ready';
            }, 2000);
        }
    }

    /**
     * Save/Load from localStorage
     */
    saveToLocalStorage() {
        try {
            localStorage.setItem('udos-font-data', JSON.stringify(this.fontData));
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
        }
    }

    loadFromLocalStorage() {
        try {
            const data = localStorage.getItem('udos-font-data');
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('Failed to load from localStorage:', e);
            return null;
        }
    }

    /**
     * Export font data
     */
    exportJSON() {
        const json = JSON.stringify(this.fontData, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.fontData.name.replace(/\s+/g, '-')}.json`;
        a.click();

        URL.revokeObjectURL(url);
        this.showStatus('Font exported');
    }

    /**
     * Save to sandbox
     */
    saveToSandbox() {
        // Prepare for /memory/sandbox export
        const sandboxData = {
            type: 'bitmap-font',
            version: '1.0.24',
            timestamp: new Date().toISOString(),
            ...this.fontData
        };

        console.log('Saving to sandbox:', sandboxData);
        alert('Font saved to /memory/sandbox (console log)');
        this.showStatus('Saved to sandbox');
    }
}

// Export for use in main app
window.BitmapEditor = BitmapEditor;
