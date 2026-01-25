/**
 * 24×24 Tile Editor - Desktop/Web Mode
 * 
 * Canvas-based tile editor with mouse support, WebSocket sync,
 * and advanced features for Tauri/browser environment.
 * 
 * Part of uDOS v1.2.31 - Editor Suite
 * 
 * Features:
 * - Canvas-based 24×24 grid rendering
 * - Mouse drawing with various tools
 * - uDOS 32-color palette
 * - Font/emoji character palettes
 * - Undo/Redo with keyboard shortcuts
 * - WebSocket sync for live collaboration
 * - Export to PNG, SVG, JSON, ASCII
 * - Grid lines toggle
 * - Zoom controls
 */

import { getAllColors } from "./util/udosPalette";
import { CHARACTER_DATASETS } from "./util/characterDatasets";

class TileEditor {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container not found: ${containerId}`);
        }
        
        // Configuration
        this.gridSize = options.gridSize || 24;
        this.cellSize = options.cellSize || 20;
        this.showGridLines = options.showGridLines !== false;
        this.zoom = options.zoom || 1;
        
        // Colors (uDOS 32-color palette)
        const palette = getAllColors();
        this.colors = {};
        this.colorList = palette.map((c) => {
            this.colors[c.name] = c.hex;
            return c.name;
        });
        
        // Character datasets
        this.datasets = CHARACTER_DATASETS;
        
        // State
        this.grid = this.createEmptyGrid();
        this.currentTool = 'pencil';
        this.currentChar = '█';
        this.currentDataset =
            this.datasets.find((ds) => ds.name.toLowerCase().includes('block')) ||
            this.datasets[0];
        this.fgColor = this.colors["White"] ? "White" : this.colorList[0];
        this.bgColor = this.colors["Black"] ? "Black" : this.colorList[0];

        // Font handling
        this.fonts = [];
        this.currentFontId = null;
        this.currentFontFamily = '"Teletext50", "Noto Color Emoji", "Noto Emoji", monospace';
        
        // Edit state
        this.undoStack = [];
        this.redoStack = [];
        this.modified = false;
        this.currentFile = null;
        
        // Drawing state
        this.isDrawing = false;
        this.lastCell = null;
        this.toolStart = null;
        
        // WebSocket
        this.ws = null;
        this.syncEnabled = false;
        
        // Initialize
        this.setupCanvas();
        this.setupUI();
        this.setupEvents();
        this.render();
        this.loadFontManifest();
    }
    
    createEmptyGrid() {
        const grid = [];
        for (let y = 0; y < this.gridSize; y++) {
            const row = [];
            for (let x = 0; x < this.gridSize; x++) {
                row.push({
                    char: ' ',
                    fg: 'WHITE',
                    bg: 'BLACK'
                });
            }
            grid.push(row);
        }
        return grid;
    }
    
    setupCanvas() {
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.gridSize * this.cellSize * this.zoom;
        this.canvas.height = this.gridSize * this.cellSize * this.zoom;
        this.canvas.style.border = '2px solid #333';
        this.canvas.style.cursor = 'crosshair';
        
        this.ctx = this.canvas.getContext('2d');
        this.ctx.imageSmoothingEnabled = false;
        
        // Create wrapper
        this.canvasWrapper = document.createElement('div');
        this.canvasWrapper.className = 'tile-editor-canvas';
        this.canvasWrapper.appendChild(this.canvas);
        
        this.container.appendChild(this.canvasWrapper);
    }
    
    setupUI() {
        // Create toolbar
        this.toolbar = document.createElement('div');
        this.toolbar.className = 'tile-editor-toolbar';
        this.toolbar.innerHTML = `
            <div class="tool-group">
                <label>Tool:</label>
                <button data-tool="pencil" class="active" title="Pencil (P)">✏️</button>
                <button data-tool="eraser" title="Eraser (E)">🧹</button>
                <button data-tool="fill" title="Fill (F)">🪣</button>
                <button data-tool="line" title="Line (L)">📏</button>
                <button data-tool="rect" title="Rectangle (R)">▢</button>
            </div>
            <div class="tool-group">
                <label>FG:</label>
                ${this.colorList.map((c) => 
                    `<button data-fg="${c}" style="background:${this.colors[c]}" 
                     class="${c === this.fgColor ? 'active' : ''}" title="${c}"></button>`
                ).join('')}
            </div>
            <div class="tool-group">
                <label>BG:</label>
                ${this.colorList.map((c) => 
                    `<button data-bg="${c}" style="background:${this.colors[c]}"
                     class="${c === this.bgColor ? 'active' : ''}" title="${c}"></button>`
                ).join('')}
            </div>
            <div class="tool-group">
                <label>Font:</label>
                <select id="font-select">
                    <option value="">Loading...</option>
                </select>
            </div>
            <div class="tool-group">
                <label>Chars:</label>
                <select id="dataset-select">
                    ${this.datasets.map((ds, i) =>
                        `<option value="${i}">${ds.name}</option>`
                    ).join('')}
                </select>
                <select id="char-select"></select>
            </div>
            <div class="tool-group">
                <button id="btn-undo" title="Undo (Ctrl+Z)">↶</button>
                <button id="btn-redo" title="Redo (Ctrl+Y)">↷</button>
                <button id="btn-clear" title="Clear All">🗑️</button>
            </div>
            <div class="tool-group">
                <button id="btn-grid" title="Toggle Grid">▦</button>
                <button id="btn-zoom-in" title="Zoom In">🔍+</button>
                <button id="btn-zoom-out" title="Zoom Out">🔍-</button>
            </div>
            <div class="tool-group">
                <button id="btn-save" title="Save (Ctrl+S)">💾</button>
                <button id="btn-load" title="Load">📂</button>
                <button id="btn-export" title="Export">📤</button>
            </div>
        `;
        
        this.container.insertBefore(this.toolbar, this.canvasWrapper);
        
        // Create status bar
        this.statusBar = document.createElement('div');
        this.statusBar.className = 'tile-editor-status';
        this.statusBar.innerHTML = `
            <span id="status-pos">Pos: (0, 0)</span>
            <span id="status-file">New Tile</span>
            <span id="status-modified"></span>
            <span id="status-undo">Undo: 0</span>
        `;
        
        this.container.appendChild(this.statusBar);

        const datasetSelect = document.getElementById('dataset-select');
        if (datasetSelect && this.currentDataset) {
            const idx = this.datasets.indexOf(this.currentDataset);
            if (idx >= 0) datasetSelect.value = String(idx);
        }
        this.updateCharSelect();
    }
    
    setupEvents() {
        // Canvas events
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('mouseleave', (e) => this.onMouseUp(e));
        
        // Prevent context menu
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Toolbar events
        this.toolbar.querySelectorAll('[data-tool]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toolbar.querySelectorAll('[data-tool]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTool = btn.dataset.tool;
            });
        });
        
        this.toolbar.querySelectorAll('[data-fg]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toolbar.querySelectorAll('[data-fg]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.fgColor = btn.dataset.fg;
            });
        });
        
        this.toolbar.querySelectorAll('[data-bg]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.toolbar.querySelectorAll('[data-bg]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.bgColor = btn.dataset.bg;
            });
        });
        
        // Font select
        document.getElementById('font-select').addEventListener('change', (e) => {
            this.selectFont(e.target.value);
        });

        // Dataset select
        document.getElementById('dataset-select').addEventListener('change', (e) => {
            const idx = parseInt(e.target.value, 10);
            this.currentDataset = this.datasets[idx] || this.datasets[0];
            this.updateCharSelect();
        });
        
        document.getElementById('char-select').addEventListener('change', (e) => {
            const idx = parseInt(e.target.value, 10);
            const code = this.currentDataset.codes[idx];
            this.currentChar = code ? String.fromCodePoint(code) : ' ';
        });
        
        // Action buttons
        document.getElementById('btn-undo').addEventListener('click', () => this.undo());
        document.getElementById('btn-redo').addEventListener('click', () => this.redo());
        document.getElementById('btn-clear').addEventListener('click', () => this.clear());
        document.getElementById('btn-grid').addEventListener('click', () => this.toggleGrid());
        document.getElementById('btn-zoom-in').addEventListener('click', () => this.zoomIn());
        document.getElementById('btn-zoom-out').addEventListener('click', () => this.zoomOut());
        document.getElementById('btn-save').addEventListener('click', () => this.save());
        document.getElementById('btn-load').addEventListener('click', () => this.load());
        document.getElementById('btn-export').addEventListener('click', () => this.showExportDialog());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.onKeyDown(e));
    }
    
    updateCharSelect() {
        const select = document.getElementById('char-select');
        if (!select || !this.currentDataset) return;
        select.innerHTML = this.currentDataset.codes.map((code, i) => {
            const char = String.fromCodePoint(code);
            const label = char === ' ' ? '␣' : char;
            return `<option value="${i}">${label}</option>`;
        }).join('');
        const firstCode = this.currentDataset.codes.find((code) => code !== 0x20);
        this.currentChar = firstCode ? String.fromCodePoint(firstCode) : ' ';
    }

    async loadFontManifest() {
        try {
            const res = await fetch('/api/v1/fonts/manifest');
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }
            const manifest = await res.json();
            const list = [];
            const collections = manifest.collections || {};
            for (const [category, subcats] of Object.entries(collections)) {
                for (const [subcat, fonts] of Object.entries(subcats || {})) {
                    for (const [fontKey, fontData] of Object.entries(fonts || {})) {
                        if (!fontData?.file) continue;
                        list.push({
                            id: fontKey,
                            name: fontData.name || fontKey,
                            file: fontData.file,
                            category: `${category}/${subcat}`,
                        });
                    }
                }
            }
            this.fonts = list;
            this.updateFontSelect();
            if (!this.currentFontId && list.length) {
                const preferred = list.find((f) => f.name === "Teletext50") || list[0];
                this.selectFont(preferred.id);
            }
        } catch (err) {
            console.error("Pixel editor font manifest load failed:", err);
            this.updateFontSelect(true);
        }
    }

    updateFontSelect(failed = false) {
        const select = document.getElementById('font-select');
        if (!select) return;
        if (failed || this.fonts.length === 0) {
            select.innerHTML = `<option value="">Fonts unavailable</option>`;
            return;
        }
        select.innerHTML = this.fonts.map((font) => {
            const label = `${font.name} (${font.category})`;
            const selected = font.id === this.currentFontId ? 'selected' : '';
            return `<option value="${font.id}" ${selected}>${label}</option>`;
        }).join('');
    }

    async selectFont(fontId) {
        if (!fontId) return;
        const font = this.fonts.find((f) => f.id === fontId);
        if (!font) return;
        this.currentFontId = fontId;
        this.updateFontSelect();
        try {
            const fontFace = new FontFace(
                font.name,
                `url(/api/v1/fonts/file?path=${encodeURIComponent(font.file)})`
            );
            const loaded = await fontFace.load();
            document.fonts.add(loaded);
            this.currentFontFamily = `"${font.name}", "Noto Color Emoji", "Noto Emoji", monospace`;
            this.render();
        } catch (err) {
            console.error("Failed to load font", err);
        }
    }
    
    getCellFromEvent(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((e.clientX - rect.left) / (this.cellSize * this.zoom));
        const y = Math.floor((e.clientY - rect.top) / (this.cellSize * this.zoom));
        
        if (x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize) {
            return { x, y };
        }
        return null;
    }
    
    onMouseDown(e) {
        const cell = this.getCellFromEvent(e);
        if (!cell) return;
        
        this.isDrawing = true;
        this.saveState();
        
        if (this.currentTool === 'fill') {
            this.floodFill(cell.x, cell.y);
        } else if (this.currentTool === 'line' || this.currentTool === 'rect') {
            this.toolStart = cell;
        } else {
            this.drawCell(cell.x, cell.y, e.button === 2);
        }
        
        this.lastCell = cell;
        this.updateStatus(cell);
    }
    
    onMouseMove(e) {
        const cell = this.getCellFromEvent(e);
        if (!cell) return;
        
        this.updateStatus(cell);
        
        if (!this.isDrawing) return;
        
        if (this.currentTool === 'pencil' || this.currentTool === 'eraser') {
            this.drawCell(cell.x, cell.y, this.currentTool === 'eraser');
        } else if (this.currentTool === 'line' || this.currentTool === 'rect') {
            // Preview (would need temporary canvas layer)
        }
        
        this.lastCell = cell;
    }
    
    onMouseUp(e) {
        if (!this.isDrawing) return;
        
        const cell = this.getCellFromEvent(e);
        
        if (this.toolStart && cell) {
            if (this.currentTool === 'line') {
                this.drawLine(this.toolStart.x, this.toolStart.y, cell.x, cell.y);
            } else if (this.currentTool === 'rect') {
                this.drawRect(this.toolStart.x, this.toolStart.y, cell.x, cell.y);
            }
        }
        
        this.isDrawing = false;
        this.toolStart = null;
        this.render();
    }
    
    onKeyDown(e) {
        // Shortcuts
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z') { e.preventDefault(); this.undo(); }
            else if (e.key === 'y') { e.preventDefault(); this.redo(); }
            else if (e.key === 's') { e.preventDefault(); this.save(); }
        } else {
            if (e.key === 'p') this.setTool('pencil');
            else if (e.key === 'e') this.setTool('eraser');
            else if (e.key === 'f') this.setTool('fill');
            else if (e.key === 'l') this.setTool('line');
            else if (e.key === 'r') this.setTool('rect');
        }
    }
    
    setTool(tool) {
        this.currentTool = tool;
        this.toolbar.querySelectorAll('[data-tool]').forEach(b => {
            b.classList.toggle('active', b.dataset.tool === tool);
        });
    }
    
    drawCell(x, y, erase = false) {
        if (erase) {
            this.grid[y][x] = { char: ' ', fg: 'WHITE', bg: 'BLACK' };
        } else {
            this.grid[y][x] = {
                char: this.currentChar,
                fg: this.fgColor,
                bg: this.bgColor
            };
        }
        this.modified = true;
        this.render();
    }
    
    floodFill(startX, startY) {
        const target = { ...this.grid[startY][startX] };
        const fill = { char: this.currentChar, fg: this.fgColor, bg: this.bgColor };
        
        if (target.char === fill.char && target.fg === fill.fg && target.bg === fill.bg) {
            return;
        }
        
        const stack = [[startX, startY]];
        const visited = new Set();
        
        while (stack.length > 0) {
            const [x, y] = stack.pop();
            const key = `${x},${y}`;
            
            if (visited.has(key)) continue;
            if (x < 0 || x >= this.gridSize || y < 0 || y >= this.gridSize) continue;
            
            const cell = this.grid[y][x];
            if (cell.char !== target.char || cell.fg !== target.fg || cell.bg !== target.bg) continue;
            
            visited.add(key);
            this.grid[y][x] = { ...fill };
            
            stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
        }
        
        this.modified = true;
        this.render();
    }
    
    drawLine(x1, y1, x2, y2) {
        // Bresenham's line algorithm
        const dx = Math.abs(x2 - x1);
        const dy = Math.abs(y2 - y1);
        const sx = x1 < x2 ? 1 : -1;
        const sy = y1 < y2 ? 1 : -1;
        let err = dx - dy;
        
        let x = x1, y = y1;
        
        while (true) {
            if (x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize) {
                this.grid[y][x] = {
                    char: this.currentChar,
                    fg: this.fgColor,
                    bg: this.bgColor
                };
            }
            
            if (x === x2 && y === y2) break;
            
            const e2 = 2 * err;
            if (e2 > -dy) { err -= dy; x += sx; }
            if (e2 < dx) { err += dx; y += sy; }
        }
        
        this.modified = true;
    }
    
    drawRect(x1, y1, x2, y2, filled = false) {
        const minX = Math.min(x1, x2);
        const maxX = Math.max(x1, x2);
        const minY = Math.min(y1, y2);
        const maxY = Math.max(y1, y2);
        
        for (let y = minY; y <= maxY; y++) {
            for (let x = minX; x <= maxX; x++) {
                if (filled || x === minX || x === maxX || y === minY || y === maxY) {
                    if (x >= 0 && x < this.gridSize && y >= 0 && y < this.gridSize) {
                        this.grid[y][x] = {
                            char: this.currentChar,
                            fg: this.fgColor,
                            bg: this.bgColor
                        };
                    }
                }
            }
        }
        
        this.modified = true;
    }
    
    saveState() {
        this.undoStack.push(JSON.stringify(this.grid));
        this.redoStack = [];
        
        if (this.undoStack.length > 100) {
            this.undoStack.shift();
        }
        
        this.updateStatus();
    }
    
    undo() {
        if (this.undoStack.length === 0) return;
        
        this.redoStack.push(JSON.stringify(this.grid));
        this.grid = JSON.parse(this.undoStack.pop());
        this.render();
        this.updateStatus();
    }
    
    redo() {
        if (this.redoStack.length === 0) return;
        
        this.undoStack.push(JSON.stringify(this.grid));
        this.grid = JSON.parse(this.redoStack.pop());
        this.render();
        this.updateStatus();
    }
    
    clear() {
        if (confirm('Clear entire canvas?')) {
            this.saveState();
            this.grid = this.createEmptyGrid();
            this.modified = true;
            this.render();
        }
    }
    
    toggleGrid() {
        this.showGridLines = !this.showGridLines;
        this.render();
    }
    
    zoomIn() {
        if (this.zoom < 3) {
            this.zoom += 0.5;
            this.resizeCanvas();
        }
    }
    
    zoomOut() {
        if (this.zoom > 0.5) {
            this.zoom -= 0.5;
            this.resizeCanvas();
        }
    }
    
    resizeCanvas() {
        this.canvas.width = this.gridSize * this.cellSize * this.zoom;
        this.canvas.height = this.gridSize * this.cellSize * this.zoom;
        this.ctx.imageSmoothingEnabled = false;
        this.render();
    }
    
    render() {
        const ctx = this.ctx;
        const size = this.cellSize * this.zoom;
        
        // Clear
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set font for characters
        ctx.font = `${size * 0.8}px ${this.currentFontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw cells
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                const cell = this.grid[y][x];
                const px = x * size;
                const py = y * size;
                
                // Background
                ctx.fillStyle = this.colors[cell.bg] || '#000';
                ctx.fillRect(px, py, size, size);
                
                // Character
                if (cell.char && cell.char !== ' ') {
                    ctx.fillStyle = this.colors[cell.fg] || '#FFF';
                    ctx.fillText(cell.char, px + size/2, py + size/2);
                }
            }
        }
        
        // Grid lines
        if (this.showGridLines) {
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1;
            
            for (let i = 0; i <= this.gridSize; i++) {
                // Vertical
                ctx.beginPath();
                ctx.moveTo(i * size, 0);
                ctx.lineTo(i * size, this.canvas.height);
                ctx.stroke();
                
                // Horizontal
                ctx.beginPath();
                ctx.moveTo(0, i * size);
                ctx.lineTo(this.canvas.width, i * size);
                ctx.stroke();
            }
        }
    }
    
    updateStatus(cell = null) {
        if (cell) {
            document.getElementById('status-pos').textContent = `Pos: (${cell.x}, ${cell.y})`;
        }
        document.getElementById('status-modified').textContent = this.modified ? '*' : '';
        document.getElementById('status-undo').textContent = `Undo: ${this.undoStack.length}`;
    }
    
    // File operations
    async save(filename = null) {
        const data = {
            version: '1.0',
            size: this.gridSize,
            created: new Date().toISOString(),
            grid: this.grid
        };
        
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        
        // Download
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename || 'tile.json';
        a.click();
        
        this.modified = false;
        this.updateStatus();
    }
    
    load() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            try {
                const text = await file.text();
                const data = JSON.parse(text);
                
                if (data.size !== this.gridSize) {
                    alert(`Wrong grid size (expected ${this.gridSize})`);
                    return;
                }
                
                this.saveState();
                this.grid = data.grid;
                this.currentFile = file.name;
                this.modified = false;
                
                document.getElementById('status-file').textContent = file.name;
                this.render();
                this.updateStatus();
            } catch (err) {
                alert(`Error loading file: ${err.message}`);
            }
        });
        
        input.click();
    }
    
    showExportDialog() {
        const format = prompt('Export format (png/svg/ascii/json):', 'png');
        if (!format) return;
        
        switch (format.toLowerCase()) {
            case 'png':
                this.exportPNG();
                break;
            case 'svg':
                this.exportSVG();
                break;
            case 'ascii':
                this.exportASCII();
                break;
            case 'json':
                this.save();
                break;
            default:
                alert('Unknown format');
        }
    }
    
    exportPNG() {
        const a = document.createElement('a');
        a.href = this.canvas.toDataURL('image/png');
        a.download = 'tile.png';
        a.click();
    }
    
    exportSVG() {
        const size = 20; // Fixed size for SVG
        let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${this.gridSize * size} ${this.gridSize * size}">`;
        svg += `<style>text { font-family: ${this.currentFontFamily}; font-size: ${size * 0.8}px; dominant-baseline: middle; text-anchor: middle; }</style>`;
        
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                const cell = this.grid[y][x];
                const px = x * size;
                const py = y * size;
                
                svg += `<rect x="${px}" y="${py}" width="${size}" height="${size}" fill="${this.colors[cell.bg]}"/>`;
                
                if (cell.char && cell.char !== ' ') {
                    const escaped = cell.char.replace(/[&<>"']/g, c => ({
                        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
                    }[c]));
                    svg += `<text x="${px + size/2}" y="${py + size/2}" fill="${this.colors[cell.fg]}">${escaped}</text>`;
                }
            }
        }
        
        svg += '</svg>';
        
        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'tile.svg';
        a.click();
    }
    
    exportASCII() {
        let ascii = '';
        for (let y = 0; y < this.gridSize; y++) {
            for (let x = 0; x < this.gridSize; x++) {
                ascii += this.grid[y][x].char || ' ';
            }
            ascii += '\n';
        }
        
        const blob = new Blob([ascii], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'tile.txt';
        a.click();
    }
    
    // WebSocket sync
    connectSync(url) {
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
            this.syncEnabled = true;
            console.log('Tile editor sync connected');
        };
        
        this.ws.onmessage = (e) => {
            try {
                const msg = JSON.parse(e.data);
                if (msg.type === 'cell_update') {
                    this.grid[msg.y][msg.x] = msg.cell;
                    this.render();
                } else if (msg.type === 'full_sync') {
                    this.grid = msg.grid;
                    this.render();
                }
            } catch (err) {
                console.error('Sync message error:', err);
            }
        };
        
        this.ws.onclose = () => {
            this.syncEnabled = false;
            console.log('Tile editor sync disconnected');
        };
    }
    
    sendSync(type, data) {
        if (this.ws && this.syncEnabled) {
            this.ws.send(JSON.stringify({ type, ...data }));
        }
    }
}

// CSS styles
const tileEditorStyles = `
.tile-editor-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px;
    background: #222;
    border-radius: 5px 5px 0 0;
}

.tile-editor-toolbar .tool-group {
    display: flex;
    align-items: center;
    gap: 5px;
}

.tile-editor-toolbar label {
    color: #888;
    font-size: 12px;
}

.tile-editor-toolbar button {
    width: 30px;
    height: 30px;
    border: 1px solid #444;
    background: #333;
    color: #fff;
    cursor: pointer;
    border-radius: 3px;
    font-size: 14px;
}

.tile-editor-toolbar button.active {
    border-color: #0af;
    background: #046;
}

.tile-editor-toolbar button:hover {
    background: #444;
}

.tile-editor-toolbar select {
    background: #333;
    color: #fff;
    border: 1px solid #444;
    padding: 5px;
    border-radius: 3px;
}

.tile-editor-canvas {
    background: #111;
    padding: 10px;
    text-align: center;
}

.tile-editor-status {
    display: flex;
    gap: 20px;
    padding: 8px 10px;
    background: #222;
    color: #888;
    font-size: 12px;
    font-family: monospace;
    border-radius: 0 0 5px 5px;
}
`;

// Export for module use
if (typeof module !== 'undefined') {
    module.exports = { TileEditor, tileEditorStyles };
}

export { TileEditor, tileEditorStyles };
