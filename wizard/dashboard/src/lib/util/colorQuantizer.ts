/**
 * Color Quantizer
 *
 * Utilities for reducing color palettes in images
 */

export interface RGB {
  r: number;
  g: number;
  b: number;
}

export interface ColorFrequency {
  color: RGB;
  count: number;
  hex: string;
}

/**
 * Convert RGB to hex string
 */
export function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b].map(x => x.toString(16).padStart(2, '0')).join('')}`;
}

/**
 * Convert hex string to RGB
 */
export function hexToRgb(hex: string): RGB | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  } : null;
}

/**
 * Calculate Euclidean distance between two colors
 */
export function colorDistance(c1: RGB, c2: RGB): number {
  const dr = c1.r - c2.r;
  const dg = c1.g - c2.g;
  const db = c1.b - c2.b;
  return Math.sqrt(dr * dr + dg * dg + db * db);
}

/**
 * Extract color frequency map from ImageData
 */
export function extractColors(imageData: ImageData): Map<string, ColorFrequency> {
  const colorMap = new Map<string, ColorFrequency>();
  const data = imageData.data;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const a = data[i + 3];

    // Skip fully transparent pixels
    if (a === 0) continue;

    const hex = rgbToHex(r, g, b);
    const existing = colorMap.get(hex);

    if (existing) {
      existing.count++;
    } else {
      colorMap.set(hex, {
        color: { r, g, b },
        count: 1,
        hex,
      });
    }
  }

  return colorMap;
}

/**
 * Reduce palette to N most frequent colors
 */
export function reducePalette(
  colorMap: Map<string, ColorFrequency>,
  maxColors: number
): ColorFrequency[] {
  const sorted = Array.from(colorMap.values()).sort((a, b) => b.count - a.count);
  return sorted.slice(0, maxColors);
}

/**
 * Find nearest color in palette
 */
export function findNearestColor(color: RGB, palette: ColorFrequency[]): RGB {
  let nearest = palette[0].color;
  let minDist = Infinity;

  for (const entry of palette) {
    const dist = colorDistance(color, entry.color);
    if (dist < minDist) {
      minDist = dist;
      nearest = entry.color;
    }
  }

  return nearest;
}

/**
 * Apply quantized palette to ImageData
 */
export function applyQuantizedPalette(
  imageData: ImageData,
  palette: ColorFrequency[]
): ImageData {
  const result = new ImageData(imageData.width, imageData.height);
  const data = imageData.data;
  const outData = result.data;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const a = data[i + 3];

    if (a === 0) {
      outData[i + 3] = 0;
      continue;
    }

    const nearest = findNearestColor({ r, g, b }, palette);
    outData[i] = nearest.r;
    outData[i + 1] = nearest.g;
    outData[i + 2] = nearest.b;
    outData[i + 3] = a;
  }

  return result;
}

/**
 * uDOS Color Palette (terminal-inspired 16-color palette)
 */
const UDOS_PALETTE = [
  { index: 0, name: 'black', hex: '#000000' },
  { index: 1, name: 'red', hex: '#ef4444' },
  { index: 2, name: 'green', hex: '#22c55e' },
  { index: 3, name: 'yellow', hex: '#eab308' },
  { index: 4, name: 'blue', hex: '#3b82f6' },
  { index: 5, name: 'magenta', hex: '#a855f7' },
  { index: 6, name: 'cyan', hex: '#06b6d4' },
  { index: 7, name: 'white', hex: '#e2e8f0' },
  { index: 8, name: 'bright-black', hex: '#475569' },
  { index: 9, name: 'bright-red', hex: '#f87171' },
  { index: 10, name: 'bright-green', hex: '#4ade80' },
  { index: 11, name: 'bright-yellow', hex: '#fbbf24' },
  { index: 12, name: 'bright-blue', hex: '#60a5fa' },
  { index: 13, name: 'bright-magenta', hex: '#c084fc' },
  { index: 14, name: 'bright-cyan', hex: '#22d3ee' },
  { index: 15, name: 'bright-white', hex: '#f8fafc' },
];

/**
 * Quantize a hex color to nearest uDOS palette index
 */
export function quantizeToUdosPalette(hexColor: string): number {
  const rgb = hexToRgb(hexColor);
  if (!rgb) return 0;

  let nearestIndex = 0;
  let minDist = Infinity;

  for (const entry of UDOS_PALETTE) {
    const paletteRgb = hexToRgb(entry.hex);
    if (!paletteRgb) continue;

    const dist = colorDistance(rgb, paletteRgb);
    if (dist < minDist) {
      minDist = dist;
      nearestIndex = entry.index;
    }
  }

  return nearestIndex;
}

/**
 * Get hex color for a palette index
 */
export function getPaletteColor(index: number): string {
  const entry = UDOS_PALETTE.find(p => p.index === index);
  return entry ? entry.hex : '#000000';
}

/**
 * Get color name for a palette index
 */
export function getPaletteColorName(index: number): string {
  const entry = UDOS_PALETTE.find(p => p.index === index);
  return entry ? entry.name : 'unknown';
}

/**
 * Export full palette data
 */
export function exportPaletteData(): Array<{ index: number; name: string; hex: string }> {
  return [...UDOS_PALETTE];
}
