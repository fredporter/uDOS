/**
 * Font to SVG Converter
 *
 * Extracts individual glyphs from TTF/OTF fonts and converts them to SVG
 * Uses opentype.js to read font files and extract glyph paths
 */

import opentype from "opentype.js";

export interface GlyphSvg {
  unicode: number;
  char: string;
  svg: string;
  width: number;
  height: number;
}

/**
 * Load a font file and extract glyphs as SVGs
 */
export async function extractGlyphsFromFont(
  fontPath: string,
  unicodeCodes: number[]
): Promise<GlyphSvg[]> {
  console.log(`[FontToSVG] Loading font from: ${fontPath}`);
  console.log(`[FontToSVG] Extracting ${unicodeCodes.length} glyphs`);

  try {
    // Fetch the font file
    const response = await fetch(fontPath);
    if (!response.ok) {
      throw new Error(`Failed to fetch font: ${response.statusText}`);
    }

    const arrayBuffer = await response.arrayBuffer();

    let font: opentype.Font;
    try {
      font = opentype.parse(arrayBuffer);
    } catch (parseError: any) {
      // Check for specific font format errors
      if (parseError.message?.includes("TrueType or CFF outlines")) {
        throw new Error(
          `Font format not supported: This appears to be a CBDT bitmap emoji font. ` +
            `Use NotoEmoji-Regular.ttf (outline font) instead of NotoColorEmoji.ttf for SVG extraction.`
        );
      }
      if (parseError.message?.includes("Unsupported OpenType signature")) {
        throw new Error(
          `Font format not supported: Unsupported OpenType signature. ` +
            `The font may be compressed (WOFF/WOFF2) or corrupted. ` +
            `Try downloading the uncompressed TTF version.`
        );
      }
      throw parseError;
    }

    console.log(
      `[FontToSVG] Font loaded: ${font.names.fullName?.en || "Unknown"}`
    );
    console.log(`[FontToSVG] Num glyphs in font: ${font.numGlyphs}`);

    const results: GlyphSvg[] = [];

    for (const code of unicodeCodes) {
      try {
        const char = String.fromCodePoint(code);
        const glyph = font.charToGlyph(char);

        if (!glyph || glyph.index === 0) {
          console.warn(
            `[FontToSVG] Glyph not found for U+${code.toString(16)}`
          );
          continue;
        }

        // Fixed 24x24 viewBox with baseline alignment and consistent scaling
        const emSquare = font.unitsPerEm || 1000;
        const ascent = font.ascender ?? emSquare * 0.8;
        const descent = font.descender ?? -emSquare * 0.2; // typically negative
        const totalHeight = ascent - descent; // ascender - (-descender)

        // Target pixel grid and margins (leave room top/bottom for optical balance)
        const target = 24;
        const margin = 2; // px
        const content = target - margin * 2; // usable vertical space

        // Choose fontSize such that (ascent - descent) maps to content height
        const fontSize = (content * emSquare) / totalHeight; // path scale factor basis
        const scale = fontSize / emSquare; // convenience

        // Build path at baseline y=0; we'll translate to target baseline later
        const path = glyph.getPath(0, 0, fontSize);

        // Use glyph bbox in font units to compute horizontal centering
        const bbox = glyph.getBoundingBox();
        const glyphWidth = (bbox.x2 - bbox.x1) * scale;

        // Baseline position within 24x24
        const baselineY = margin + ascent * scale;

        // Center horizontally: shift bbox center to 12
        const centerX = (target - glyphWidth) / 2 - bbox.x1 * scale;

        // Translate so baseline sits at baselineY
        const translateY = baselineY;

        const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${target} ${target}">
  <path d="${path.toPathData(2)}" fill="currentColor" transform="translate(${Math.round(centerX)}, ${Math.round(translateY)})"/>
</svg>`;

        results.push({
          unicode: code,
          char,
          svg,
          width: target,
          height: target,
        });

        console.log(
          `[FontToSVG] Extracted glyph for ${char} (U+${code.toString(16)})`
        );
      } catch (glyphError) {
        console.error(
          `[FontToSVG] Error extracting glyph U+${code.toString(16)}:`,
          glyphError
        );
      }
    }

    console.log(`[FontToSVG] Successfully extracted ${results.length} glyphs`);
    return results;
  } catch (error) {
    console.error(`[FontToSVG] Failed to load font:`, error);
    throw error;
  }
}

/**
 * Save SVG glyphs to a downloadable file (browser context).
 * Wizard dashboard runs in the browser, so we expose a download helper instead.
 */
export async function saveGlyphSvg(
  glyph: GlyphSvg,
  filename: string
): Promise<void> {
  const blob = new Blob([glyph.svg], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

/**
 * Load cached SVG or extract from font
 */
export async function getOrCreateGlyphSvg(
  unicode: number,
  fontPath: string,
  cachePath?: string
): Promise<GlyphSvg> {
  // Try to load from cache first
  if (cachePath) {
    try {
      const response = await fetch(cachePath);
      if (response.ok) {
        const svg = await response.text();
        console.log(`[FontToSVG] Loaded cached SVG from: ${cachePath}`);
        return {
          unicode,
          char: String.fromCodePoint(unicode),
          svg,
          width: 1024,
          height: 1024,
        };
      }
    } catch (error) {
      console.log(
        `[FontToSVG] Cache miss for U+${unicode.toString(16)}, extracting from font`
      );
    }
  }

  // Extract from font
  const glyphs = await extractGlyphsFromFont(fontPath, [unicode]);
  if (glyphs.length === 0) {
    throw new Error(`Failed to extract glyph U+${unicode.toString(16)}`);
  }

  return glyphs[0];
}
