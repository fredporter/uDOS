/**
 * uDOS Font Editor - Font Manager
 * Manages font data, save/load, and export
 */

class FontManager {
    constructor() {
        this.fontData = {
            fontName: "uDOS Custom",
            gridSize: "16x16",
            baseline: 9,
            created: new Date().toISOString(),
            modified: new Date().toISOString(),
            version: "1.0",
            author: "",
            glyphs: {}
        };
        this.loadFromLocalStorage();
    }

    saveGlyph(codepoint, pixelData) {
        const unicode = `U+${codepoint.toString(16).toUpperCase().padStart(4, '0')}`;
        this.fontData.glyphs[unicode] = pixelData;
        this.fontData.modified = new Date().toISOString();
        this.saveToLocalStorage();
    }

    loadGlyph(codepoint) {
        const unicode = `U+${codepoint.toString(16).toUpperCase().padStart(4, '0')}`;
        return this.fontData.glyphs[unicode] || null;
    }

    deleteGlyph(codepoint) {
        const unicode = `U+${codepoint.toString(16).toUpperCase().padStart(4, '0')}`;
        delete this.fontData.glyphs[unicode];
        this.fontData.modified = new Date().toISOString();
        this.saveToLocalStorage();
    }

    getGlyphCount() {
        return Object.keys(this.fontData.glyphs).length;
    }

    setFontName(name) {
        this.fontData.fontName = name;
        this.fontData.modified = new Date().toISOString();
        this.saveToLocalStorage();
    }

    setAuthor(author) {
        this.fontData.author = author;
        this.fontData.modified = new Date().toISOString();
        this.saveToLocalStorage();
    }

    saveToLocalStorage() {
        localStorage.setItem('udos-font-editor', JSON.stringify(this.fontData));
    }

    loadFromLocalStorage() {
        const saved = localStorage.getItem('udos-font-editor');
        if (saved) {
            try {
                this.fontData = JSON.parse(saved);
                // Ensure all required fields exist
                if (!this.fontData.modified) {
                    this.fontData.modified = new Date().toISOString();
                }
                if (!this.fontData.version) {
                    this.fontData.version = "1.0";
                }
            } catch (e) {
                console.error('Failed to load font data:', e);
            }
        }
    }

    exportJSON() {
        const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '');
        const filename = `uFONT-${timestamp}-${this.fontData.fontName.replace(/\s+/g, '-')}.json`;

        const blob = new Blob([JSON.stringify(this.fontData, null, 2)],
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();

        URL.revokeObjectURL(url);

        return filename;
    }

    importJSON(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const imported = JSON.parse(e.target.result);
                // Validate structure
                if (imported.gridSize && imported.glyphs) {
                    this.fontData = imported;
                    this.fontData.modified = new Date().toISOString();
                    this.saveToLocalStorage();
                    window.location.reload(); // Refresh UI
                } else {
                    alert('Invalid font file format');
                }
            } catch (err) {
                alert('Error loading font file: ' + err.message);
            }
        };
        reader.readAsText(file);
    }

    reset() {
        if (confirm('Clear all glyphs? This cannot be undone.')) {
            this.fontData = {
                fontName: "uDOS Custom",
                gridSize: "16x16",
                baseline: 9,
                created: new Date().toISOString(),
                modified: new Date().toISOString(),
                version: "1.0",
                author: "",
                glyphs: {}
            };
            this.saveToLocalStorage();
            window.location.reload();
        }
    }

    copyGlyph(fromCodepoint, toCodepoint) {
        const data = this.loadGlyph(fromCodepoint);
        if (data) {
            this.saveGlyph(toCodepoint, data);
            return true;
        }
        return false;
    }
}
