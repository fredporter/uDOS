/**
 * uDOS Standard 32-Color Palette
 *
 * Non-editable standard palette used across Pixel Editor and rendering systems.
 * Balances synthwave aesthetics with emoji skin tones, shading, and monochrome graphics.
 *
 * Transparency: Binary on/off (clear) only. No percentage-based alpha.
 *
 * @version 1.0.0
 */

export interface ColorDefinition {
  id: number;
  name: string;
  hex: string;
  rgb: [number, number, number];
}

export interface UDOSPalette {
  version: string;
  totalColors: number;
  transparency: "binary";
  groups: {
    terrain: ColorDefinition[];
    markers: ColorDefinition[];
    greyscale: ColorDefinition[];
    accents: ColorDefinition[];
  };
}

/**
 * The uDOS Standard 32-Color Palette
 *
 * Groups:
 * - Terrain (0-7): Natural colors for maps - grass, water, earth, sand
 * - Markers (8-15): Bright UI colors for waypoints, danger, safe zones, alerts
 * - Greyscale (16-23): Monochrome for backgrounds, text, and shading
 * - Accents (24-31): Skin tones and synthwave highlights
 */
export const UDOS_PALETTE: UDOSPalette = {
  version: "2.0.0",
  totalColors: 32,
  transparency: "binary",
  groups: {
    terrain: [
      { id: 0, name: "Forest Green", hex: "#2D5016", rgb: [45, 80, 22] },
      { id: 1, name: "Grass Green", hex: "#4C9A2A", rgb: [76, 154, 42] },
      { id: 2, name: "Deep Water", hex: "#1B4965", rgb: [27, 73, 101] },
      { id: 3, name: "Water Blue", hex: "#3A86FF", rgb: [58, 134, 255] },
      { id: 4, name: "Earth Brown", hex: "#6B4423", rgb: [107, 68, 35] },
      { id: 5, name: "Sand Tan", hex: "#D4A574", rgb: [212, 165, 116] },
      { id: 6, name: "Mountain Grey", hex: "#5A6F7D", rgb: [90, 111, 125] },
      { id: 7, name: "Snow White", hex: "#E8F1F5", rgb: [232, 241, 245] },
    ],
    markers: [
      { id: 8, name: "Danger Red", hex: "#DC2626", rgb: [220, 38, 38] },
      { id: 9, name: "Alert Orange", hex: "#FB5607", rgb: [251, 86, 7] },
      { id: 10, name: "Waypoint Yellow", hex: "#FFBE0B", rgb: [255, 190, 11] },
      { id: 11, name: "Safe Green", hex: "#06FFA5", rgb: [6, 255, 165] },
      { id: 12, name: "Objective Cyan", hex: "#00D9FF", rgb: [0, 217, 255] },
      { id: 13, name: "Neon Purple", hex: "#8338EC", rgb: [131, 56, 236] },
      { id: 14, name: "Neon Pink", hex: "#FF006E", rgb: [255, 0, 110] },
      { id: 15, name: "Hot Magenta", hex: "#FF1FB3", rgb: [255, 31, 179] },
    ],
    greyscale: [
      { id: 16, name: "Black", hex: "#000000", rgb: [0, 0, 0] },
      { id: 17, name: "Dark Grey", hex: "#1A1A1A", rgb: [26, 26, 26] },
      { id: 18, name: "Charcoal", hex: "#333333", rgb: [51, 51, 51] },
      { id: 19, name: "Medium Grey", hex: "#666666", rgb: [102, 102, 102] },
      { id: 20, name: "Steel Grey", hex: "#999999", rgb: [153, 153, 153] },
      { id: 21, name: "Light Grey", hex: "#CCCCCC", rgb: [204, 204, 204] },
      { id: 22, name: "Off White", hex: "#E6E6E6", rgb: [230, 230, 230] },
      { id: 23, name: "White", hex: "#FFFFFF", rgb: [255, 255, 255] },
    ],
    accents: [
      { id: 24, name: "Very Light", hex: "#FFE0BD", rgb: [255, 224, 189] },
      { id: 25, name: "Light", hex: "#FFCD94", rgb: [255, 205, 148] },
      { id: 26, name: "Medium", hex: "#D2A679", rgb: [210, 166, 121] },
      { id: 27, name: "Dark", hex: "#8D5524", rgb: [141, 85, 36] },
      { id: 28, name: "Lava Red", hex: "#FF4500", rgb: [255, 69, 0] },
      { id: 29, name: "Ice Blue", hex: "#A7C7E7", rgb: [167, 199, 231] },
      { id: 30, name: "Toxic Green", hex: "#39FF14", rgb: [57, 255, 20] },
      { id: 31, name: "Deep Sea", hex: "#003366", rgb: [0, 51, 102] },
    ],
  },
};

/**
 * Get all colors as a flat array ordered by ID (0-31)
 */
export function getAllColors(): ColorDefinition[] {
  return [
    ...UDOS_PALETTE.groups.terrain,
    ...UDOS_PALETTE.groups.markers,
    ...UDOS_PALETTE.groups.greyscale,
    ...UDOS_PALETTE.groups.accents,
  ].sort((a, b) => a.id - b.id);
}

/**
 * Get color by ID (0-31)
 */
export function getColorById(id: number): ColorDefinition | undefined {
  if (id < 0 || id > 31) return undefined;
  return getAllColors().find((c) => c.id === id);
}

/**
 * Get color by name (case-insensitive)
 */
export function getColorByName(name: string): ColorDefinition | undefined {
  const normalized = name.toLowerCase();
  return getAllColors().find((c) => c.name.toLowerCase() === normalized);
}

/**
 * Get color by index (0-31, alias for getColorById)
 */
export function getColorByIndex(index: number): ColorDefinition | undefined {
  return getColorById(index);
}

/**
 * Get color hex value by ID
 */
export function getColorHex(id: number): string {
  const color = getColorById(id);
  return color?.hex ?? "#000000";
}

/**
 * Get color RGB value by ID
 */
export function getColorRGB(id: number): [number, number, number] {
  const color = getColorById(id);
  return color?.rgb ?? [0, 0, 0];
}

/**
 * Export palette as JSON for static/fonts/udos.md
 */
export function exportPaletteAsJSON(): string {
  const palette = {
    version: UDOS_PALETTE.version,
    totalColors: UDOS_PALETTE.totalColors,
    transparency: UDOS_PALETTE.transparency,
    colors: getAllColors().map((c) => ({
      id: c.id,
      name: c.name,
      hex: c.hex,
      rgb: c.rgb,
      group: getColorGroup(c.id),
    })),
  };
  return JSON.stringify(palette, null, 2);
}

/**
 * Convert hex color to RGB
 */
export function hexToRGB(hex: string): [number, number, number] {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16),
      ]
    : [0, 0, 0];
}

/**
 * Convert RGB to hex color
 */
export function rgbToHex(r: number, g: number, b: number): string {
  return (
    "#" +
    [r, g, b]
      .map((x) => {
        const hex = x.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
      })
      .join("")
      .toUpperCase()
  );
}

/**
 * Default colors
 */
export const DEFAULT_FOREGROUND_ID = 1; // Grass Green
export const DEFAULT_BACKGROUND_ID = 16; // Black
export const DEFAULT_TEXT_ID = 23; // White

/**
 * Get color group name by ID
 */
export function getColorGroup(id: number): string {
  if (id >= 0 && id <= 7) return "terrain";
  if (id >= 8 && id <= 15) return "markers";
  if (id >= 16 && id <= 23) return "greyscale";
  if (id >= 24 && id <= 31) return "accents";
  return "unknown";
}

/**
 * Check if a color ID is valid
 */
export function isValidColorId(id: number): boolean {
  return id >= 0 && id <= 31;
}
