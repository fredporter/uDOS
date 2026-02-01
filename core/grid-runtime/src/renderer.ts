/**
 * Sextant Renderer: Graphics Pipeline
 *
 * Converts tile data → sextant characters with fallback rendering
 * Supports: Sextant (16) → Quadrant (16) → Shade (4) → ASCII (4)
 */

import { Tile, RenderOptions } from "./index";
import { GraphicsMode, SEXTANT_CHARS, QUADRANT_CHARS, SHADE_CHARS, ASCII_CHARS } from "./geometry";

/**
 * Sextant Graphics Character Bank
 *
 * Maps tile data → unicode sextant characters (16 unique)
 */
export class SextantCharacterSet {
  // Map tile properties to sextant indices (0-15)
  static getTileCharIndex(tile: Tile): number {
    // Map tile type/properties to sextant character
    // 0-15: different tile combinations
    // For now: simple mapping based on tile type
    if (tile.type === "sprite") {
      return 8; // Sextant index for sprites
    } else if (tile.type === "marker") {
      return 10; // Sextant index for markers
    } else {
      return Math.min(Math.floor(Math.random() * 8), 7); // Objects: 0-7
    }
  }

  /**
   * Get sextant character for tile
   */
  static getCharacter(tile: Tile): string {
    const index = this.getTileCharIndex(tile);
    return SEXTANT_CHARS[index];
  }
}

/**
 * Simplified renderer that wraps the RenderPipeline with a preset mode.
 */
export class SextantRenderer {
  private pipeline: RenderPipeline;

  constructor(mode: GraphicsMode = GraphicsMode.Sextant) {
    this.pipeline = new RenderPipeline(mode);
  }

  renderCharacter(sextantIndex: number): string {
    return this.pipeline.renderCharacterWithFallback(sextantIndex);
  }

  renderTile(tile: Tile, colorIndex: number = 7) {
    return this.pipeline.renderTile(tile, colorIndex);
  }
}

/**
 * Render Pipeline: Compose viewport layers
 *
 * Handles: tile lookup, character selection, fallback rendering
 */
export class RenderPipeline {
  private renderMode: GraphicsMode = GraphicsMode.Sextant;
  private colorPalette: Map<number, string> = new Map();

  constructor(initialMode: GraphicsMode = GraphicsMode.Sextant) {
    this.renderMode = initialMode;
    this.initializePalette();
  }

  /**
   * Initialize 5-bit color palette (32 colors)
   */
  private initializePalette(): void {
    const colors = [
      "#000000", // 0: black
      "#FF0000", // 1: red
      "#00FF00", // 2: green
      "#FFFF00", // 3: yellow
      "#0000FF", // 4: blue
      "#FF00FF", // 5: magenta
      "#00FFFF", // 6: cyan
      "#FFFFFF", // 7: white
      "#808080", // 8: gray
      "#FF8080", // 9: light red
      "#80FF80", // 10: light green
      "#FFFF80", // 11: light yellow
      "#8080FF", // 12: light blue
      "#FF80FF", // 13: light magenta
      "#80FFFF", // 14: light cyan
      "#C0C0C0", // 15: light gray
      "#400000", // 16: dark red
      "#004000", // 17: dark green
      "#000040", // 18: dark blue
      "#404000", // 19: dark yellow
      "#004040", // 20: dark cyan
      "#400040", // 21: dark magenta
      "#404040", // 22: darker gray
      "#808040", // 23: olive
      "#408080", // 24: teal
      "#804040", // 25: brown
      "#804080", // 26: purple
      "#408040", // 27: forest green
      "#204040", // 28: dark teal
      "#402040", // 29: dark purple
      "#A0A0A0", // 30: medium gray
      "#E0E0E0"  // 31: light gray
    ];

    for (let i = 0; i < colors.length; i++) {
      this.colorPalette.set(i, colors[i]);
    }
  }

  /**
   * Set rendering mode (with automatic fallback)
   */
  setRenderMode(mode: GraphicsMode): void {
    this.renderMode = mode;
  }

  /**
   * Render character with fallback
   *
   * Input: sextant character (0-15 as index)
   * Output: character in current mode, or fallback
   */
  renderCharacterWithFallback(sextantIndex: number): string {
    const index = sextantIndex % 16; // Clamp to 0-15

    switch (this.renderMode) {
      case GraphicsMode.Sextant:
        return SEXTANT_CHARS[index];

      case GraphicsMode.Quadrant:
        // Map sextant → quadrant (every other sextant segment)
        return QUADRANT_CHARS[Math.floor(index / 2) % 16];

      case GraphicsMode.Shade:
        // Map sextant → shade levels (░▒▓█)
        return SHADE_CHARS[Math.floor(index / 4) % 4];

      case GraphicsMode.ASCII:
        // Map sextant → ASCII block characters
        return ASCII_CHARS[Math.floor(index / 8) % 4];

      default:
        return "?";
    }
  }

  /**
   * Render tile with color information
   *
   * Returns: { char, color, priority }
   */
  renderTile(
    tile: Tile,
    colorIndex: number = 7
  ): { char: string; color: string; priority: number } {
    const sextantIndex = SextantCharacterSet.getTileCharIndex(tile);
    const char = this.renderCharacterWithFallback(sextantIndex);
    const color = this.colorPalette.get(colorIndex) || "#FFFFFF";
    const priority = tile.static ? 10 : 100; // Sprites render on top

    return { char, color, priority };
  }

  /**
   * Render viewport image from layer stack
   *
   * Layers are sorted by priority (back to front)
   * Returns: 2D array of { char, color } objects
   */
  composeLayers(
    layers: Array<{
      tiles: Map<string, string>;
      colors: Map<string, number>;
      priorities: Map<string, number>;
    }>,
    width: number,
    height: number
  ): Array<Array<{ char: string; color: string }>> {
    // Initialize canvas
    const canvas: Array<Array<{ char: string; color: string }>> = Array(height)
      .fill(null)
      .map(() =>
        Array(width)
          .fill(null)
          .map(() => ({ char: " ", color: "#000000" }))
      );

    // Flatten all tiles with priorities
    const allTiles: Array<{
      x: number;
      y: number;
      char: string;
      color: string;
      priority: number;
    }> = [];

    for (const layer of layers) {
      for (const [cellId, char] of layer.tiles.entries()) {
        const color = layer.colors.get(cellId) || 7;
        const priority = layer.priorities.get(cellId) || 10;

        // Parse cell ID (format: "colrow" where col=0-35 base36, row=0-35 base36)
        const x = parseInt(cellId.substring(0, 1), 36);
        const y = parseInt(cellId.substring(1, 2), 36);

        if (x >= 0 && x < width && y >= 0 && y < height) {
          allTiles.push({
            x,
            y,
            char: this.renderCharacterWithFallback(char.charCodeAt(0)),
            color: this.colorPalette.get(color) || "#FFFFFF",
            priority
          });
        }
      }
    }

    // Sort by priority (lower = back, higher = front)
    allTiles.sort((a, b) => a.priority - b.priority);

    // Composite onto canvas (back to front)
    for (const tile of allTiles) {
      canvas[tile.y][tile.x] = {
        char: tile.char,
        color: tile.color
      };
    }

    return canvas;
  }

  /**
   * Render canvas to ANSI string with colors
   */
  canvasToString(
    canvas: Array<Array<{ char: string; color: string }>>
  ): string {
    return canvas
      .map((row) =>
        row
          .map(({ char, color }) => {
            // Simple ANSI color code (256 colors)
            // For now, just return the character
            return char;
          })
          .join("")
      )
      .join("\n");
  }

  /**
   * Get color for tile
   */
  getColorForTile(tile: Tile, index: number = 7): string {
    return this.colorPalette.get(index) || "#FFFFFF";
  }
}

/**
 * Graphics Mode Validator
 *
 * Checks if terminal supports specific render modes
 */
export class GraphicsModeSupport {
  /**
   * Detect terminal capabilities (stub for future)
   */
  static detectTerminalMode(): GraphicsMode {
    // Check terminal env vars: TERM, COLORTERM
    const term = process.env.TERM || "";
    const colorTerm = process.env.COLORTERM || "";

    if (colorTerm.includes("truecolor")) {
      return GraphicsMode.Sextant;
    } else if (colorTerm.includes("256")) {
      return GraphicsMode.Quadrant;
    } else if (term.includes("color")) {
      return GraphicsMode.Shade;
    } else {
      return GraphicsMode.ASCII;
    }
  }

  /**
   * Get fallback chain for mode
   */
  static getFallbackChain(mode: GraphicsMode): GraphicsMode[] {
    switch (mode) {
      case GraphicsMode.Sextant:
        return [GraphicsMode.Sextant, GraphicsMode.Quadrant, GraphicsMode.Shade, GraphicsMode.ASCII];
      case GraphicsMode.Quadrant:
        return [GraphicsMode.Quadrant, GraphicsMode.Shade, GraphicsMode.ASCII];
      case GraphicsMode.Shade:
        return [GraphicsMode.Shade, GraphicsMode.ASCII];
      case GraphicsMode.ASCII:
        return [GraphicsMode.ASCII];
      default:
        return [GraphicsMode.ASCII];
    }
  }
}

if (typeof globalThis !== 'undefined' && !(globalThis as any).SextantCharacterSet) {
  (globalThis as any).SextantCharacterSet = SextantCharacterSet;
}
