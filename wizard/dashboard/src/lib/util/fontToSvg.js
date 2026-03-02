/**
 * Font to SVG extraction utilities
 * Note: This is a stub - real implementation would use opentype.js or similar
 */

/**
 * Extract glyphs from a font file as SVG paths
 * @param {File|ArrayBuffer} fontData - Font file data
 * @param {string[]} characters - Characters to extract
 * @returns {Promise<{char: string, svg: string, path: string}[]>}
 */
export async function extractGlyphsFromFont(fontData, characters = []) {
  // This is a placeholder implementation
  // Real implementation would:
  // 1. Parse the font file using opentype.js or similar
  // 2. Extract glyph paths for each character
  // 3. Convert paths to SVG format

  console.warn('extractGlyphsFromFont: Stub implementation - would extract:', characters);

  // Return stub data
  return characters.map(char => ({
    char,
    svg: `<svg viewBox="0 0 100 100"><text x="50" y="50" text-anchor="middle">${char}</text></svg>`,
    path: `M 10 10 L 90 90`, // Placeholder path
    unicode: char.codePointAt(0),
    width: 100,
    height: 100
  }));
}

/**
 * Convert font glyph to SVG string
 * @param {object} glyph - Glyph data from font parser
 * @returns {string} SVG markup
 */
export function glyphToSvg(glyph) {
  if (!glyph || !glyph.path) {
    return '<svg></svg>';
  }

  return `<svg viewBox="0 0 ${glyph.width || 100} ${glyph.height || 100}">
    <path d="${glyph.path}" fill="currentColor" />
  </svg>`;
}

/**
 * Batch export glyphs as SVG files
 * @param {object[]} glyphs - Array of glyph data
 * @param {string} format - Output format ('individual' | 'sprite')
 * @returns {Blob[]} Array of SVG blobs
 */
export function exportGlyphsAsSvg(glyphs, format = 'individual') {
  if (format === 'sprite') {
    // Combine all glyphs into a single SVG sprite
    const symbols = glyphs.map(g =>
      `<symbol id="glyph-${g.unicode}" viewBox="0 0 ${g.width} ${g.height}">
        <path d="${g.path}" />
      </symbol>`
    ).join('\n');

    const sprite = `<svg xmlns="http://www.w3.org/2000/svg">\n${symbols}\n</svg>`;
    return [new Blob([sprite], { type: 'image/svg+xml' })];
  }

  // Individual SVG files
  return glyphs.map(g => {
    const svg = glyphToSvg(g);
    return new Blob([svg], { type: 'image/svg+xml' });
  });
}
