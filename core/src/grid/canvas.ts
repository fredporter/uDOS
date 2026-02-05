import {
  BorderStyle,
  TextOptions,
  TableColumn,
  TableOptions,
  MinimapCell,
  MinimapOptions,
  LocIdOverlay,
} from "./types.js";

function pad(s: string, w: number): string {
  if (s.length >= w) return s.slice(0, w);
  return s + " ".repeat(w - s.length);
}

export class Canvas80x30 {
  readonly width = 80 as const;
  readonly height = 30 as const;
  private buf: string[][];

  constructor() {
    this.buf = Array.from({ length: this.height }, () =>
      Array.from({ length: this.width }, () => " "),
    );
  }

  clear(fill = " ") {
    for (let y = 0; y < this.height; y++)
      for (let x = 0; x < this.width; x++) this.buf[y][x] = fill;
  }

  put(x: number, y: number, ch: string) {
    if (x < 0 || y < 0 || x >= this.width || y >= this.height) return;
    this.buf[y][x] = ch[0];
  }

  write(x: number, y: number, s: string) {
    for (let i = 0; i < s.length; i++) this.put(x + i, y, s[i]);
  }

  box(
    x: number,
    y: number,
    w: number,
    h: number,
    style: BorderStyle = "single",
    title?: string,
  ) {
    if (style === "none" || w < 2 || h < 2) return;
    const x2 = x + w - 1;
    const y2 = y + h - 1;

    this.put(x, y, "+");
    this.put(x2, y, "+");
    this.put(x, y2, "+");
    this.put(x2, y2, "+");

    for (let i = 1; i < w - 1; i++) {
      this.put(x + i, y, "-");
      this.put(x + i, y2, "-");
    }
    for (let j = 1; j < h - 1; j++) {
      this.put(x, y + j, "|");
      this.put(x2, y + j, "|");
    }

    if (title) this.write(x + 2, y, title.slice(0, w - 4));
  }

  text(
    x: number,
    y: number,
    w: number,
    h: number,
    content: string,
    opts: TextOptions = {},
  ) {
    const wrap = opts.wrap ?? true;
    const lines = content.split("\n");
    let cy = y;

    for (const line of lines) {
      if (cy >= y + h) break;
      if (!wrap) {
        this.write(x, cy++, pad(line, w));
      } else {
        let s = line;
        while (s.length && cy < y + h) {
          this.write(x, cy++, pad(s.slice(0, w), w));
          s = s.slice(w);
        }
      }
    }
  }

  table(
    x: number,
    y: number,
    w: number,
    h: number,
    columns: TableColumn[],
    rows: any[],
    opts: TableOptions = {},
  ) {
    const showHeader = opts.header ?? true;
    const rowSep = opts.rowSep ?? false;

    // Calculate column widths
    const colCount = columns.length;
    const colWidths = columns.map(
      (c) => c.width || Math.floor((w - 2) / colCount) - 1,
    );

    let cy = y + 1;

    // Draw header
    if (showHeader && cy < y + h) {
      let cx = x + 1;
      for (let i = 0; i < colCount && cx < x + w; i++) {
        const title = pad(columns[i].title, colWidths[i]);
        this.write(cx, cy, title);
        cx += colWidths[i] + 1;
      }
      cy++;

      if (rowSep && cy < y + h) {
        for (let i = x + 1; i < x + w - 1; i++) this.put(i, cy, "-");
        cy++;
      }
    }

    // Draw rows
    for (const row of rows) {
      if (cy >= y + h - 1) break;
      let cx = x + 1;
      for (let i = 0; i < colCount && cx < x + w; i++) {
        const val = String(row[columns[i].key] || "");
        const cell = pad(val, colWidths[i]);
        this.write(cx, cy, cell);
        cx += colWidths[i] + 1;
      }
      cy++;
    }
  }

  minimap(
    x: number,
    y: number,
    w: number,
    h: number,
    cells: Map<string, MinimapCell>,
    opts: MinimapOptions = {},
  ) {
    const cellSize = 2;
    const cols = Math.floor((w - 2) / cellSize);
    const rows = Math.floor((h - 2) / cellSize);

    let idx = 0;
    for (let row = 0; row < rows && y + 1 + row < y + h - 1; row++) {
      for (
        let col = 0;
        col < cols && x + 1 + col * cellSize < x + w - 1;
        col++
      ) {
        const locId = Array.from(cells.keys())[idx++];
        if (!locId) break;

        const cell = cells.get(locId);
        if (!cell) continue;

        const cx = x + 1 + col * cellSize;
        const cy = y + 1 + row;

        // Draw cell marker
        if (cell.type === "selected") {
          this.put(cx, cy, "[");
          this.put(cx + 1, cy, "]");
        } else if (cell.overlay) {
          this.put(cx, cy, cell.overlay.icon);
          this.put(cx + 1, cy, " ");
        } else {
          this.put(cx, cy, ".");
          this.put(cx + 1, cy, " ");
        }
      }
    }

    // Draw legend if overlays present
    const hasOverlays = Array.from(cells.values()).some((c) => c.overlay);
    if (hasOverlays && y + h - 3 >= y) {
      this.write(x + 2, y + h - 3, "T=Task N=Note E=Event !=Alert");
    }
  }

  toLines(): string[] {
    return this.buf.map((r) => r.join(""));
  }
}
