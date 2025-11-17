/**
 * uDOS Font Editor - Grid Editor
 * 16×16 pixel grid for bitmap font editing
 */

class GridEditor {
    constructor(canvasId, size = 16) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = size;           // 16×16
        this.pixelSize = 20;            // 20px per cell = 320×320 canvas
        this.pixels = this.initGrid();  // 2D array
        this.currentGlyph = 0x0041;     // Start with 'A'
        this.setupEventListeners();
        this.drawGrid();
    }

    initGrid() {
        return Array(this.gridSize).fill(0)
            .map(() => Array(this.gridSize).fill(0));
    }

    drawGrid() {
        // Draw background
        this.ctx.fillStyle = '#1a1a1a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw pixels
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                if (this.pixels[y][x]) {
                    this.ctx.fillStyle = '#00ff00'; // Green pixels
                    this.ctx.fillRect(
                        x * this.pixelSize,
                        y * this.pixelSize,
                        this.pixelSize - 1,
                        this.pixelSize - 1
                    );
                }
            }
        }

        // Draw grid lines
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= this.gridSize; i++) {
            const pos = i * this.pixelSize;
            this.ctx.beginPath();
            this.ctx.moveTo(pos, 0);
            this.ctx.lineTo(pos, this.canvas.height);
            this.ctx.stroke();

            this.ctx.beginPath();
            this.ctx.moveTo(0, pos);
            this.ctx.lineTo(this.canvas.width, pos);
            this.ctx.stroke();
        }
    }

    setupEventListeners() {
        let isDrawing = false;
        let drawMode = true; // true = draw, false = erase

        this.canvas.addEventListener('mousedown', (e) => {
            isDrawing = true;
            const rect = this.canvas.getBoundingClientRect();
            const x = Math.floor((e.clientX - rect.left) / this.pixelSize);
            const y = Math.floor((e.clientY - rect.top) / this.pixelSize);

            // Right-click = erase
            if (e.button === 2) {
                drawMode = false;
            } else {
                drawMode = true;
            }

            this.setPixel(x, y, drawMode ? 1 : 0);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (!isDrawing) return;
            const rect = this.canvas.getBoundingClientRect();
            const x = Math.floor((e.clientX - rect.left) / this.pixelSize);
            const y = Math.floor((e.clientY - rect.top) / this.pixelSize);
            this.setPixel(x, y, drawMode ? 1 : 0);
        });

        this.canvas.addEventListener('mouseup', () => {
            isDrawing = false;
        });

        this.canvas.addEventListener('mouseleave', () => {
            isDrawing = false;
        });

        // Prevent context menu
        this.canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
    }

    setPixel(x, y, value) {
        if (x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize) {
            this.pixels[y][x] = value;
            this.drawGrid();
            this.onPixelChange?.(x, y, value);
        }
    }

    clear() {
        this.pixels = this.initGrid();
        this.drawGrid();
        this.onPixelChange?.();
    }

    fill() {
        this.pixels = Array(this.gridSize).fill(1)
            .map(() => Array(this.gridSize).fill(1));
        this.drawGrid();
        this.onPixelChange?.();
    }

    flipH() {
        this.pixels = this.pixels.map(row => row.reverse());
        this.drawGrid();
        this.onPixelChange?.();
    }

    flipV() {
        this.pixels = this.pixels.reverse();
        this.drawGrid();
        this.onPixelChange?.();
    }

    rotate90() {
        const rotated = Array(this.gridSize).fill(0)
            .map(() => Array(this.gridSize).fill(0));

        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                rotated[x][this.gridSize - 1 - y] = this.pixels[y][x];
            }
        }

        this.pixels = rotated;
        this.drawGrid();
        this.onPixelChange?.();
    }

    invert() {
        this.pixels = this.pixels.map(row =>
            row.map(p => p ? 0 : 1)
        );
        this.drawGrid();
        this.onPixelChange?.();
    }

    toJSON() {
        // Convert to binary string format
        return this.pixels.map(row =>
            row.map(p => p ? '1' : '0').join('')
        );
    }

    fromJSON(data) {
        // Load from binary string format
        if (!data || data.length === 0) {
            this.clear();
            return;
        }

        this.pixels = data.map(row =>
            row.split('').map(c => c === '1' ? 1 : 0)
        );
        this.drawGrid();
    }
}
