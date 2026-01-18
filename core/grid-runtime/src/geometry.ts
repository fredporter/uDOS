/**
 * Grid Geometry Constants
 * 
 * Defines the canonical specifications for uDOS spatial grid system
 * Based on: dev/roadmap/u_dos_spatial_text_graphics_brief.md
 */

// Tile Geometry
export const TILE_WIDTH = 16;    // pixels
export const TILE_HEIGHT = 24;   // pixels

// Viewport Dimensions
export const VIEWPORT_STANDARD = {
  cols: 80,
  rows: 30
};

export const VIEWPORT_MINI = {
  cols: 40,
  rows: 15
};

// Content Layout
export const RIGHT_MARGIN = 2;
export const CONTENT_WIDTH = VIEWPORT_STANDARD.cols - RIGHT_MARGIN; // 78

export const COLUMN_WIDTHS = [12, 24]; // allowed widths
export const DEFAULT_COLUMN_WIDTH = 24;

// Layer Bands (Real-World Precision Layers)
export const LAYER_BANDS = {
  SUR: { min: 300, max: 305, label: "Surface" },        // L300–L305
  UDN: { min: 294, max: 299, label: "Upside Down" },    // L299–L294 (reversed)
  SUB: { min: -Infinity, max: 293, label: "Subterranean" } // L293+
};

// Grid Cell Format: AA10 (2 letters + 2 decimal digits)
export const GRID_CELL_COLS = 80;  // AA (0) to DC (79)
export const GRID_CELL_ROWS = 30;  // 10–39
export const GRID_CELL_ROW_OFFSET = 10; // rows start at 10

// Color/Palette
export const PALETTE_DEPTH = 5; // 5-bit palette (0–31)
export const PALETTE_SIZE = 1 << PALETTE_DEPTH; // 32 colors

// Tile Footprints
export const FOOTPRINT_STANDARD = { width: 1, height: 1 }; // 16×24 px
export const FOOTPRINT_WIDE = { width: 2, height: 1 };      // 32×24 px (emoji, heroes)

// Graphics Fallback Ladder
export enum GraphicsMode {
  Sextant = "sextant",    // Unicode block sextants (canonical)
  Quadrant = "quadrant",  // Unicode quadrant/half blocks
  Shade = "shade",        // ASCII density: ░ ▒ ▓ █
  ASCII = "ascii"         // ASCII fallback: . : # @
}

// Sextant Unicode Points
export const SEXTANT_CHARS = [
  "\u0020", // 0 (empty)
  "\u1FB88", // 1 (top-right)
  "\u1FB84", // 2 (bottom-right)
  "\u1FB8C", // 3 (right)
  "\u1FB82", // 4 (bottom-left)
  "\u1FB8A", // 5 (bottom-right + bottom-left)
  "\u1FB86", // 6 (left + bottom-right)
  "\u1FB8E", // 7 (all except top-left)
  "\u1FB81", // 8 (top-left)
  "\u1FB89", // 9 (top-left + top-right)
  "\u1FB85", // 10 (top-left + bottom-right)
  "\u1FB8D", // 11 (all except bottom-left)
  "\u1FB83", // 12 (left + top-right)
  "\u1FB8B", // 13 (all except bottom-right)
  "\u1FB87", // 14 (all except top-right)
  "\u1FB8F"  // 15 (full block)
];

export const QUADRANT_CHARS: Record<number, string> = {
  0: " ",   // empty
  1: "▖",   // bottom-left
  2: "▝",   // bottom-right
  3: "▄",   // bottom
  4: "▗",   // top-left
  5: "▟",   // all except top-right
  6: "▞",   // top and bottom-right
  7: "▌",   // right
  8: "▘",   // top-right
  9: "▚",   // top-left and bottom-right
  10: "▐",  // left
  11: "▜",  // top-left and bottom
  12: "▀",  // top
  13: "▛",  // all except bottom-left
  14: "▙",  // all except top-right
  15: "█"   // full block
};

export const SHADE_CHARS = ["░", "▒", "▓", "█"];
export const ASCII_CHARS = [".", ":", "#", "@"];
