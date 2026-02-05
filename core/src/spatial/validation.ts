/**
 * Spatial Validation & Constraints
 *
 * Layer bands, coordinate bounds, and safety checks.
 * Reference: docs/v1-3 UNIVERSE.md
 *
 * @module spatial/validation
 */

import { parseLocId } from "./parse.js";

/**
 * Layer band semantics (v1.3)
 */
export enum LayerBand {
  TERRESTRIAL = "terrestrial", // L300-L305: Earth surface/underground
  REGIONAL = "regional", // L306-L399: Local regions, overlays
  CITIES = "cities", // L400-L499: City/metro overlays
  NATIONS = "nations", // L500-L599: Nation/continent scales
  PLANETARY = "planetary", // L600-L699: Planets, moons, bodies
  ORBITAL = "orbital", // L700-L799: Solar system, orbits
  STELLAR = "stellar", // L800-L899: Stars, exoplanets, catalogues
}

/**
 * Layer band configuration
 */
export interface LayerBandConfig {
  band: LayerBand;
  minLayer: number;
  maxLayer: number;
  description: string;
}

/**
 * Layer band registry (canonical v1.3)
 */
const LAYER_BANDS: Record<LayerBand, LayerBandConfig> = {
  [LayerBand.TERRESTRIAL]: {
    band: LayerBand.TERRESTRIAL,
    minLayer: 300,
    maxLayer: 305,
    description: "Human-scale surface precision (Earth SUR/UDN/SUB)",
  },
  [LayerBand.REGIONAL]: {
    band: LayerBand.REGIONAL,
    minLayer: 306,
    maxLayer: 399,
    description: "Local regions and overlays",
  },
  [LayerBand.CITIES]: {
    band: LayerBand.CITIES,
    minLayer: 400,
    maxLayer: 499,
    description: "City and metro area overlays",
  },
  [LayerBand.NATIONS]: {
    band: LayerBand.NATIONS,
    minLayer: 500,
    maxLayer: 599,
    description: "Nation and continent scale",
  },
  [LayerBand.PLANETARY]: {
    band: LayerBand.PLANETARY,
    minLayer: 600,
    maxLayer: 699,
    description: "Planets, moons, celestial bodies",
  },
  [LayerBand.ORBITAL]: {
    band: LayerBand.ORBITAL,
    minLayer: 700,
    maxLayer: 799,
    description: "Solar system and orbital mechanics",
  },
  [LayerBand.STELLAR]: {
    band: LayerBand.STELLAR,
    minLayer: 800,
    maxLayer: 899,
    description: "Stars, exoplanets, and galactic catalogues",
  },
};

/**
 * Global layer constraints
 */
export const LAYER_CONSTRAINTS = {
  MIN_LAYER: 300,
  MAX_LAYER: 899,
  MAX_DEPTH: 99, // SUB depth D0..D99
};

/**
 * Check if layer is within valid range
 */
export function isValidLayer(layer: number): boolean {
  return (
    Number.isInteger(layer) &&
    layer >= LAYER_CONSTRAINTS.MIN_LAYER &&
    layer <= LAYER_CONSTRAINTS.MAX_LAYER
  );
}

/**
 * Check if depth is valid (for SUB layers)
 */
export function isValidDepth(depth: number): boolean {
  return (
    Number.isInteger(depth) &&
    depth >= 0 &&
    depth <= LAYER_CONSTRAINTS.MAX_DEPTH
  );
}

/**
 * Determine which band a layer belongs to
 */
export function getLayerBand(layer: number): LayerBand | null {
  if (!isValidLayer(layer)) return null;

  for (const band of Object.values(LayerBand)) {
    const config = LAYER_BANDS[band];
    if (layer >= config.minLayer && layer <= config.maxLayer) {
      return band;
    }
  }
  return null;
}

/**
 * Get band config for a layer
 */
export function getLayerBandConfig(layer: number): LayerBandConfig | null {
  const band = getLayerBand(layer);
  return band ? LAYER_BANDS[band] : null;
}

/**
 * List all layer bands
 */
export function listLayerBands(): LayerBandConfig[] {
  return Object.values(LayerBand).map((b) => LAYER_BANDS[b]);
}

/**
 * Check if a place reference is semantically valid
 *
 * Checks:
 * - Anchor exists (if registry provided)
 * - Space is valid (SUR|UDN|SUB)
 * - LocId parses correctly
 * - Layer is in valid range
 * - Depth is valid for SUB anchors
 */
export function validatePlaceRef(
  placeRef: string,
  anchorValidator?: (anchorId: string) => boolean,
): { valid: boolean; error?: string } {
  const parts = placeRef.split(":");

  // Basic structure check
  if (parts.length < 3) {
    return {
      valid: false,
      error: "PlaceRef must have at least 3 colon-separated parts",
    };
  }

  // Parse anchor ID (may be composite like BODY:MOON)
  let anchorId = parts[0];
  let spaceIdx = 1;

  if (anchorId === "BODY" || anchorId === "GAME" || anchorId === "CATALOG") {
    if (parts.length < 4) {
      return {
        valid: false,
        error: `Composite anchor ${anchorId} requires subtype`,
      };
    }
    anchorId = `${parts[0]}:${parts[1]}`;
    spaceIdx = 2;
  }

  // Validate anchor (if validator provided)
  if (anchorValidator && !anchorValidator(anchorId)) {
    return { valid: false, error: `Unknown anchor: ${anchorId}` };
  }

  // Validate space
  const space = parts[spaceIdx];
  if (space !== "SUR" && space !== "UDN" && space !== "SUB") {
    return {
      valid: false,
      error: `Invalid space: ${space} (must be SUR, UDN, or SUB)`,
    };
  }

  // Validate LocId
  const locIdStr = parts[spaceIdx + 1];
  const locId = parseLocId(locIdStr);
  if (!locId) {
    return { valid: false, error: `Invalid LocId: ${locIdStr}` };
  }

  // Validate layer
  if (!isValidLayer(locId.effectiveLayer)) {
    return {
      valid: false,
      error: `Layer ${locId.effectiveLayer} out of range (${LAYER_CONSTRAINTS.MIN_LAYER}-${LAYER_CONSTRAINTS.MAX_LAYER})`,
    };
  }

  // Parse and validate optional tags
  for (const tag of parts.slice(spaceIdx + 2)) {
    if (tag.startsWith("D")) {
      const depthStr = tag.slice(1);
      if (!depthStr.match(/^\d+$/)) {
        return { valid: false, error: `Invalid depth tag: ${tag}` };
      }
      const depth = Number(depthStr);
      if (!isValidDepth(depth)) {
        return {
          valid: false,
          error: `Depth ${depth} out of range (0-${LAYER_CONSTRAINTS.MAX_DEPTH})`,
        };
      }
    } else if (tag.startsWith("I")) {
      // Instance ID: any non-empty string after I
      if (tag.length < 2) {
        return { valid: false, error: "Instance tag I requires a value" };
      }
    } else {
      return { valid: false, error: `Unknown tag: ${tag}` };
    }
  }

  return { valid: true };
}

/**
 * Format a place reference with validation
 *
 * Ensures proper canonicalization:
 * - Normalized layer encoding
 * - Consistent tag ordering (D before I)
 */
export function canonicalizePlace(
  anchorId: string,
  space: string,
  locIdStr: string,
  depth?: number,
  instance?: string,
): string | null {
  // Validate LocId
  const locId = parseLocId(locIdStr);
  if (!locId) return null;

  // Validate layer
  if (!isValidLayer(locId.effectiveLayer)) return null;

  // Validate space
  if (space !== "SUR" && space !== "UDN" && space !== "SUB") return null;

  // Build canonical form
  const parts = [anchorId, space, locIdStr];

  if (depth !== undefined) {
    if (!isValidDepth(depth)) return null;
    parts.push(`D${depth}`);
  }

  if (instance) {
    parts.push(`I${instance}`);
  }

  return parts.join(":");
}

/**
 * Return a human-readable description of a place
 */
export function describePlaceRef(placeRef: string): string {
  const validation = validatePlaceRef(placeRef);
  if (!validation.valid) {
    return `[Invalid: ${validation.error}]`;
  }

  const parts = placeRef.split(":");
  let anchorId = parts[0];
  let spaceIdx = 1;

  if (anchorId === "BODY" || anchorId === "GAME" || anchorId === "CATALOG") {
    anchorId = `${parts[0]}:${parts[1]}`;
    spaceIdx = 2;
  }

  const space = parts[spaceIdx];
  const locIdStr = parts[spaceIdx + 1];
  const locId = parseLocId(locIdStr)!;
  const band = getLayerBandConfig(locId.effectiveLayer);

  const bandDesc = band ? ` [${band.description}]` : "";
  return `${anchorId}/${space}/${locIdStr}${bandDesc}`;
}
