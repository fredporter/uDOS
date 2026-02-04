import { BorderStyle, TextOptions } from "./types.js";

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
      Array.from({ length: this.width }, () => " ")
    );
  }

  clear(fill = " ") {
    for (let y = 0; y < this.height; y++)
      for (let x = 0; x < this.width; x++)
        this.buf[y][x] = fill;
  }

  put(x: number, y: number, ch: string) {
    if (x < 0 || y < 0 || x >= this.width || y >= this.height) return;
    this.buf[y][x] = ch[0];
  }

  write(x: number, y: number, s: string) {
    for (let i = 0; i < s.length; i++) this.put(x + i, y, s[i]);
  }

  box(x: number, y: number, w: number, h: number, style: BorderStyle = "single", title?: string) {
    if (style === "none" || w < 2 || h < 2) return;
    const x2 = x + w - 1;
    const y2 = y + h - 1;

    this.put(x, y, "+"); this.put(x2, y, "+");
    this.put(x, y2, "+"); this.put(x2, y2, "+");

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

  text(x: number, y: number, w: number, h: number, content: string, opts: TextOptions = {}) {
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

  toLines(): string[] {
    return this.buf.map(r => r.join(""));
  }
}
