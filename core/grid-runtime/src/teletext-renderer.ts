/**
 * Teletext Renderer - Unicode block graphics (2×3 pixels → 6-bit encoding)
 * 
 * Tier 2 graphics for uDOS grid runtime (Teletext-style rendering)
 * Uses Unicode teletext characters (U+1FB00–U+1FB3F) for 2×3 pixel patterns
 * 
 * Fallback chain: Teletext → AsciiBlock → Shades → ASCII
 * 
 * @module grid-runtime/teletext-renderer
 */

/**
 * Unicode teletext character lookup (64 possible 2×3 patterns)
 * Bits: [TL, TR, ML, MR, BL, BR] (top-left to bottom-right, row-major)
 * 
 * Example:
 *   Pattern: ██
 *            ░░
 *            ░░
 *   Bits: [1,1,0,0,0,0] → Index 48 → '🬰'
 */
export const TELETEXT_CHARS: string[] = [
  ' ',  '🬀', '🬁', '🬂', '🬃', '🬄', '🬅', '🬆',  // 0x00–0x07
  '🬇', '🬈', '🬉', '🬊', '🬋', '🬌', '🬍', '🬎',  // 0x08–0x0F
  '🬏', '🬐', '🬑', '🬒', '🬓', '▌', '🬔', '🬕',  // 0x10–0x17
  '🬖', '🬗', '🬘', '🬙', '🬚', '🬛', '🬜', '🬝',  // 0x18–0x1F
  '🬞', '🬟', '🬠', '🬡', '🬢', '🬣', '🬤', '🬥',  // 0x20–0x27
  '🬦', '🬧', '▐', '🬨', '🬩', '🬪', '🬫', '🬬',  // 0x28–0x2F
  '🬭', '🬮', '🬯', '🬰', '🬱', '🬲', '🬳', '🬴',  // 0x30–0x37
  '🬵', '🬶', '🬷', '🬸', '🬹', '🬺', '🬻', '█',  // 0x38–0x3F
];

/**
 * AsciiBlock character lookup (4 possible 2×2 patterns)
 * Fallback for terminals without teletext support
 * Bits: [TL, TR, BL, BR]
 */
export const ASCII_BLOCK_CHARS: string[] = [
  ' ',  '▘', '▝', '▀',  // 0b0000, 0b0001, 0b0010, 0b0011
  '▖', '▌', '▞', '▛',  // 0b0100, 0b0101, 0b0110, 0b0111
  '▗', '▚', '▐', '▜',  // 0b1000, 0b1001, 0b1010, 0b1011
  '▄', '▙', '▟', '█',  // 0b1100, 0b1101, 0b1110, 0b1111
];

/**
 * Shade characters (density-based fallback)
 * Used when no block graphics available
 */
export const SHADE_CHARS: string[] = [
  ' ',   // Empty
  '░',   // Light shade (1/4 density)
  '▒',   // Medium shade (1/2 density)
  '▓',   // Dark shade (3/4 density)
  '█',   // Full block
];

/**
 * ASCII fallback characters (ultimate compatibility)
 */
export const ASCII_CHARS: string[] = [
  ' ',   // Empty
  '.',   // Light (1/6 pixels)
  ':',   // Medium (2-3/6 pixels)
  '#',   // Dense (4-5/6 pixels)
  '@',   // Full (6/6 pixels)
];

/**
 * Pixel grid for a single teletext cell (2×3 pixels)
 * Each cell in the grid represents one sub-pixel within the character
 */
export interface PixelGrid {
  topLeft: boolean;
  topRight: boolean;
  middleLeft: boolean;
  middleRight: boolean;
  bottomLeft: boolean;
  bottomRight: boolean;
}

/**
 * Convert 6-bit pattern to teletext index
 * @param grid - 2×3 pixel pattern
 * @returns Index into TELETEXT_CHARS (0-63)
 */
export function pixelGridToIndex(grid: PixelGrid): number {
  return (
    (grid.topLeft ? 32 : 0) +
    (grid.topRight ? 16 : 0) +
    (grid.middleLeft ? 8 : 0) +
    (grid.middleRight ? 4 : 0) +
    (grid.bottomLeft ? 2 : 0) +
    (grid.bottomRight ? 1 : 0)
  );
}

/**
 * Convert teletext index to 6-bit pattern
 * @param index - Index into TELETEXT_CHARS (0-63)
 * @returns 2×3 pixel pattern
 */
export function indexToPixelGrid(index: number): PixelGrid {
  if (index < 0 || index > 63) {
    throw new Error(`Invalid teletext index: ${index} (must be 0-63)`);
  }
  
  return {
    topLeft: (index & 32) !== 0,
    topRight: (index & 16) !== 0,
    middleLeft: (index & 8) !== 0,
    middleRight: (index & 4) !== 0,
    bottomLeft: (index & 2) !== 0,
    bottomRight: (index & 1) !== 0,
  };
}

/**
 * Convert pixel grid to teletext character
 * @param grid - 2×3 pixel pattern
 * @returns Unicode teletext character
 */
export function pixelGridToTeletext(grid: PixelGrid): string {
  const index = pixelGridToIndex(grid);
  return TELETEXT_CHARS[index];
}

/**
 * Convert pixel grid to asciiBlock character (2×2 fallback)
 * @param grid - 2×3 pixel pattern (top 2 rows used)
 * @returns Unicode asciiBlock character
 */
export function pixelGridToAsciiBlock(grid: PixelGrid): string {
  // AsciiBlock bits: [BL, BR, TL, TR] (bottom-left = bit 3, top-right = bit 0)
  // Map teletext top row → asciiBlock top, middle row → asciiBlock bottom
  const index =
    (grid.middleLeft ? 8 : 0) +   // Bottom-left asciiBlock (bit 3)
    (grid.middleRight ? 4 : 0) +  // Bottom-right asciiBlock (bit 2)
    (grid.topLeft ? 2 : 0) +      // Top-left asciiBlock (bit 1)
    (grid.topRight ? 1 : 0);      // Top-right asciiBlock (bit 0)
  return ASCII_BLOCK_CHARS[index];
}

/**
 * Convert pixel grid to shade character (density-based)
 * @param grid - 2×3 pixel pattern
 * @returns Shade character (░▒▓█)
 */
export function pixelGridToShade(grid: PixelGrid): string {
  const density =
    (grid.topLeft ? 1 : 0) +
    (grid.topRight ? 1 : 0) +
    (grid.middleLeft ? 1 : 0) +
    (grid.middleRight ? 1 : 0) +
    (grid.bottomLeft ? 1 : 0) +
    (grid.bottomRight ? 1 : 0);
  
  if (density === 0) return SHADE_CHARS[0];
  if (density === 1) return SHADE_CHARS[1];
  if (density <= 3) return SHADE_CHARS[2];
  if (density <= 5) return SHADE_CHARS[3];
  return SHADE_CHARS[4];
}

/**
 * Convert pixel grid to ASCII character (ultimate fallback)
 * @param grid - 2×3 pixel pattern
 * @returns ASCII character (. : # @)
 */
export function pixelGridToASCII(grid: PixelGrid): string {
  const density =
    (grid.topLeft ? 1 : 0) +
    (grid.topRight ? 1 : 0) +
    (grid.middleLeft ? 1 : 0) +
    (grid.middleRight ? 1 : 0) +
    (grid.bottomLeft ? 1 : 0) +
    (grid.bottomRight ? 1 : 0);
  
  if (density === 0) return ASCII_CHARS[0];
  if (density === 1) return ASCII_CHARS[1];
  if (density <= 3) return ASCII_CHARS[2];
  if (density <= 5) return ASCII_CHARS[3];
  return ASCII_CHARS[4];
}

/**
 * Rendering quality levels for fallback chain
 */
export enum RenderQuality {
  TELETEXT = 'teletext',   // Unicode 6-bit (2×3 pixels)
  ASCII_BLOCK = 'asciiBlock', // Unicode 4-bit (2×2 pixels)
  SHADE = 'shade',       // Density-based shades
  ASCII = 'ascii',       // Pure ASCII fallback
}

/**
 * Render pixel grid using specified quality level
 * @param grid - 2×3 pixel pattern
 * @param quality - Rendering quality (default: TELETEXT)
 * @returns Rendered character
 */
export function renderPixelGrid(
  grid: PixelGrid,
  quality: RenderQuality = RenderQuality.TELETEXT
): string {
  switch (quality) {
    case RenderQuality.TELETEXT:
      return pixelGridToTeletext(grid);
    case RenderQuality.ASCII_BLOCK:
      return pixelGridToAsciiBlock(grid);
    case RenderQuality.SHADE:
      return pixelGridToShade(grid);
    case RenderQuality.ASCII:
      return pixelGridToASCII(grid);
  }
}

/**
 * Detect terminal teletext support (best-effort)
 * @returns True if terminal likely supports teletext characters
 */
export function detectTeletextSupport(): boolean {
  // In Node.js environment, check TERM environment variable
  if (typeof process !== 'undefined' && process.env.TERM) {
    const term = process.env.TERM.toLowerCase();
    // Modern terminals with Unicode support
    return term.includes('xterm') || term.includes('screen') || term.includes('tmux');
  }
  
  // In browser, check for window object
  if (typeof globalThis !== 'undefined' && 'window' in globalThis) {
    return true;
  }
  
  // Default: assume support
  return true;
}

/**
 * Get recommended render quality for current environment
 * @returns Recommended RenderQuality level
 */
export function getRecommendedQuality(): RenderQuality {
  if (detectTeletextSupport()) {
    return RenderQuality.TELETEXT;
  }
  return RenderQuality.ASCII_BLOCK;
}

/**
 * Create empty pixel grid (all pixels off)
 */
export function createEmptyGrid(): PixelGrid {
  return {
    topLeft: false,
    topRight: false,
    middleLeft: false,
    middleRight: false,
    bottomLeft: false,
    bottomRight: false,
  };
}

/**
 * Create full pixel grid (all pixels on)
 */
export function createFullGrid(): PixelGrid {
  return {
    topLeft: true,
    topRight: true,
    middleLeft: true,
    middleRight: true,
    bottomLeft: true,
    bottomRight: true,
  };
}

/**
 * Merge two pixel grids (logical OR)
 * @param a - First grid
 * @param b - Second grid
 * @returns Merged grid (pixels on if either input has pixel on)
 */
export function mergeGrids(a: PixelGrid, b: PixelGrid): PixelGrid {
  return {
    topLeft: a.topLeft || b.topLeft,
    topRight: a.topRight || b.topRight,
    middleLeft: a.middleLeft || b.middleLeft,
    middleRight: a.middleRight || b.middleRight,
    bottomLeft: a.bottomLeft || b.bottomLeft,
    bottomRight: a.bottomRight || b.bottomRight,
  };
}

/**
 * Invert pixel grid (toggle all pixels)
 * @param grid - Input grid
 * @returns Inverted grid
 */
export function invertGrid(grid: PixelGrid): PixelGrid {
  return {
    topLeft: !grid.topLeft,
    topRight: !grid.topRight,
    middleLeft: !grid.middleLeft,
    middleRight: !grid.middleRight,
    bottomLeft: !grid.bottomLeft,
    bottomRight: !grid.bottomRight,
  };
}
