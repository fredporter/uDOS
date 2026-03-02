/**
 * Tile Editor - Canvas-based tile/pixel editor
 */

export class TileEditor {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.gridSize = options.gridSize || 16;
    this.cellSize = options.cellSize || 20;
    this.canvas = null;
    this.ctx = null;
    this.tiles = new Map();
    this.selectedChar = ' ';
    this.selectedFg = '#ffffff';
    this.selectedBg = '#000000';
  }

  init() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    this.canvas = document.createElement('canvas');
    this.canvas.width = this.gridSize * this.cellSize;
    this.canvas.height = this.gridSize * this.cellSize;
    this.canvas.style.border = '1px solid #334155';
    this.canvas.style.cursor = 'crosshair';

    container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');

    this.canvas.addEventListener('click', (e) => this.handleClick(e));
    this.render();
  }

  handleClick(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / this.cellSize);
    const y = Math.floor((event.clientY - rect.top) / this.cellSize);

    const key = `${x},${y}`;
    this.tiles.set(key, {
      x, y,
      char: this.selectedChar,
      fg: this.selectedFg,
      bg: this.selectedBg
    });
    this.render();
  }

  render() {
    if (!this.ctx) return;

    this.ctx.fillStyle = '#000000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw grid
    this.ctx.strokeStyle = '#1e293b';
    for (let i = 0; i <= this.gridSize; i++) {
      this.ctx.beginPath();
      this.ctx.moveTo(i * this.cellSize, 0);
      this.ctx.lineTo(i * this.cellSize, this.canvas.height);
      this.ctx.stroke();

      this.ctx.beginPath();
      this.ctx.moveTo(0, i * this.cellSize);
      this.ctx.lineTo(this.canvas.width, i * this.cellSize);
      this.ctx.stroke();
    }

    // Draw tiles
    this.ctx.font = `${this.cellSize - 4}px monospace`;
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';

    for (const [key, tile] of this.tiles) {
      const x = tile.x * this.cellSize;
      const y = tile.y * this.cellSize;

      this.ctx.fillStyle = tile.bg;
      this.ctx.fillRect(x, y, this.cellSize, this.cellSize);

      this.ctx.fillStyle = tile.fg;
      this.ctx.fillText(
        tile.char,
        x + this.cellSize / 2,
        y + this.cellSize / 2
      );
    }
  }

  setSelectedChar(char) {
    this.selectedChar = char;
  }

  setSelectedColor(fg, bg) {
    this.selectedFg = fg;
    this.selectedBg = bg;
  }

  exportTiles() {
    return Array.from(this.tiles.values());
  }

  importTiles(tiles) {
    this.tiles.clear();
    for (const tile of tiles) {
      this.tiles.set(`${tile.x},${tile.y}`, tile);
    }
    this.render();
  }

  clear() {
    this.tiles.clear();
    this.render();
  }
}

export const tileEditorStyles = `
  .tile-editor-container {
    display: flex;
    gap: 20px;
  }
  .tile-editor-canvas {
    border: 1px solid #334155;
    background: #000;
  }
  .tile-editor-controls {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
`;
