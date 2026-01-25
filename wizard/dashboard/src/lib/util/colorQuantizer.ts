/**
 * Color Quantization to uDOS Palette
 *
 * Maps arbitrary colors to the nearest uDOS 32-color palette using perceptual color distance (CIEDE2000)
 */

import { getAllColors } from "./udosPalette";

export type RGB = [number, number, number];
export type Lab = [number, number, number];

// Get palette as array
const PALETTE_COLORS = getAllColors();
export const UDOS_PALETTE = PALETTE_COLORS.map((c) => c.hex);

/**
 * Convert RGB to Lab color space (perceptually uniform)
 */
export function rgbToLab(rgb: RGB): Lab {
  // RGB to XYZ
  let [r, g, b] = rgb.map((v) => {
    v = v / 255;
    return v > 0.04045 ? Math.pow((v + 0.055) / 1.055, 2.4) : v / 12.92;
  }) as RGB;

  const x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375;
  const y = r * 0.2126729 + g * 0.7151522 + b * 0.072175;
  const z = r * 0.0193339 + g * 0.119192 + b * 0.9503041;

  // XYZ to Lab
  const xn = 0.95047;
  const yn = 1.0;
  const zn = 1.08883;

  const fx =
    x / xn > 0.008856 ? Math.pow(x / xn, 1 / 3) : (7.787 * x) / xn + 16 / 116;
  const fy =
    y / yn > 0.008856 ? Math.pow(y / yn, 1 / 3) : (7.787 * y) / yn + 16 / 116;
  const fz =
    z / zn > 0.008856 ? Math.pow(z / zn, 1 / 3) : (7.787 * z) / zn + 16 / 116;

  const L = 116 * fy - 16;
  const a = 500 * (fx - fy);
  const b2 = 200 * (fy - fz);

  return [L, a, b2];
}

/**
 * CIEDE2000 color difference formula
 * Industry standard for perceptual color distance
 */
export function ciede2000(lab1: Lab, lab2: Lab): number {
  const [L1, a1, b1] = lab1;
  const [L2, a2, b2] = lab2;

  const deltaL = L2 - L1;
  const avgL = (L1 + L2) / 2;

  const C1 = Math.sqrt(a1 * a1 + b1 * b1);
  const C2 = Math.sqrt(a2 * a2 + b2 * b2);
  const avgC = (C1 + C2) / 2;

  const G =
    0.5 *
    (1 - Math.sqrt(Math.pow(avgC, 7) / (Math.pow(avgC, 7) + Math.pow(25, 7))));

  const a1Prime = (1 + G) * a1;
  const a2Prime = (1 + G) * a2;

  const C1Prime = Math.sqrt(a1Prime * a1Prime + b1 * b1);
  const C2Prime = Math.sqrt(a2Prime * a2Prime + b2 * b2);

  const avgCPrime = (C1Prime + C2Prime) / 2;
  const deltaC = C2Prime - C1Prime;

  const h1Prime = (Math.atan2(b1, a1Prime) * 180) / Math.PI;
  const h2Prime = (Math.atan2(b2, a2Prime) * 180) / Math.PI;

  let deltaH;
  if (C1Prime * C2Prime === 0) {
    deltaH = 0;
  } else if (Math.abs(h2Prime - h1Prime) <= 180) {
    deltaH = h2Prime - h1Prime;
  } else if (h2Prime - h1Prime > 180) {
    deltaH = h2Prime - h1Prime - 360;
  } else {
    deltaH = h2Prime - h1Prime + 360;
  }

  const deltaHPrime =
    2 * Math.sqrt(C1Prime * C2Prime) * Math.sin(((deltaH / 2) * Math.PI) / 180);

  const avgHPrime =
    Math.abs(h1Prime - h2Prime) > 180
      ? (h1Prime + h2Prime + 360) / 2
      : (h1Prime + h2Prime) / 2;

  const T =
    1 -
    0.17 * Math.cos(((avgHPrime - 30) * Math.PI) / 180) +
    0.24 * Math.cos((2 * avgHPrime * Math.PI) / 180) +
    0.32 * Math.cos(((3 * avgHPrime + 6) * Math.PI) / 180) -
    0.2 * Math.cos(((4 * avgHPrime - 63) * Math.PI) / 180);

  const SL =
    1 +
    (0.015 * (avgL - 50) * (avgL - 50)) /
      Math.sqrt(20 + (avgL - 50) * (avgL - 50));
  const SC = 1 + 0.045 * avgCPrime;
  const SH = 1 + 0.015 * avgCPrime * T;

  const RT =
    -2 *
    Math.sqrt(
      Math.pow(avgCPrime, 7) / (Math.pow(avgCPrime, 7) + Math.pow(25, 7))
    ) *
    Math.sin(
      (60 * Math.exp(-Math.pow((avgHPrime - 275) / 25, 2)) * Math.PI) / 180
    );

  const deltaE = Math.sqrt(
    Math.pow(deltaL / SL, 2) +
      Math.pow(deltaC / SC, 2) +
      Math.pow(deltaHPrime / SH, 2) +
      RT * (deltaC / SC) * (deltaHPrime / SH)
  );

  return deltaE;
}

/**
 * Convert hex color to RGB
 */
export function hexToRgb(hex: string): RGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) {
    throw new Error(`Invalid hex color: ${hex}`);
  }
  return [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16),
  ];
}

// Precompute Lab values for palette
const paletteLab: Lab[] = PALETTE_COLORS.map((c) => rgbToLab(c.rgb));

/**
 * Map any color to nearest uDOS palette color
 * Returns palette index (0-31)
 */
export function quantizeToUdosPalette(color: string | RGB): number {
  const rgb = typeof color === "string" ? hexToRgb(color) : color;
  const lab = rgbToLab(rgb);

  let minDistance = Infinity;
  let bestIndex = 0;

  for (let i = 0; i < paletteLab.length; i++) {
    const distance = ciede2000(lab, paletteLab[i]);
    if (distance < minDistance) {
      minDistance = distance;
      bestIndex = i;
    }
  }

  return bestIndex;
}

/**
 * Get hex color from palette index
 */
export function getPaletteColor(index: number): string {
  if (index < 0 || index >= UDOS_PALETTE.length) {
    throw new Error(`Invalid palette index: ${index}`);
  }
  return UDOS_PALETTE[index];
}

/**
 * Quantize entire image data to uDOS palette
 * Returns palette indices for each pixel
 */
export function quantizeImageData(imageData: ImageData): (number | null)[] {
  const pixels: (number | null)[] = [];

  for (let i = 0; i < imageData.data.length; i += 4) {
    const r = imageData.data[i];
    const g = imageData.data[i + 1];
    const b = imageData.data[i + 2];
    const a = imageData.data[i + 3];

    if (a < 128) {
      pixels.push(null); // Transparent
    } else {
      pixels.push(quantizeToUdosPalette([r, g, b]));
    }
  }

  return pixels;
}

/**
 * Quantize pixel grid to uDOS palette
 */
export function quantizePixelGrid(pixels: RGB[][]): (number | null)[][] {
  return pixels.map((row) =>
    row.map((pixel) => (pixel ? quantizeToUdosPalette(pixel) : null))
  );
}

/**
 * Get semantic category for a palette index
 */
export function getPaletteCategory(index: number): string {
  if (index >= 0 && index <= 7) return "terrain";
  if (index >= 8 && index <= 15) return "ui-markers";
  if (index >= 16 && index <= 23) return "greyscale";
  if (index >= 24 && index <= 31) return "accents";
  return "unknown";
}

/**
 * Export palette for external tools
 */
export function exportPaletteData() {
  return PALETTE_COLORS.map((color, i) => {
    const [r, g, b] = color.rgb;
    return {
      index: i,
      name: color.name,
      hex: color.hex,
      rgb: { r, g, b },
      category: getPaletteCategory(i),
    };
  });
}

/**
 * Get palette color name
 */
export function getPaletteColorName(index: number): string {
  return PALETTE_COLORS[index]?.name || "Unknown";
}
