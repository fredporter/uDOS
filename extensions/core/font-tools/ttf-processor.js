/**
 * uDOS Font Manager - TTF Processor
 * Version: 1.0.24
 * 
 * Converts TTF/OTF fonts to bitmap format
 */

class TTFProcessor {
    constructor() {
        this.fontData = null;
        this.fontFace = null;
        this.canvas = document.getElementById('ttfCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    }

    /**
     * Load a font file
     */
    async loadFont(file) {
        try {
            const arrayBuffer = await file.arrayBuffer();
            const blob = new Blob([arrayBuffer], { type: file.type });
            const url = URL.createObjectURL(blob);

            // Create FontFace
            const fontName = file.name.replace(/\.[^/.]+$/, '');
            this.fontFace = new FontFace(fontName, `url(${url})`);
            
            await this.fontFace.load();
            document.fonts.add(this.fontFace);

            this.fontData = {
                name: fontName,
                family: this.fontFace.family,
                style: this.fontFace.style,
                weight: this.fontFace.weight,
                format: file.type,
                size: file.size,
                file: file
            };

            this.updateFontInfo();
            this.renderPreview();
            this.extractGlyphs();

            return this.fontData;
        } catch (error) {
            console.error('Error loading font:', error);
            throw error;
        }
    }

    /**
     * Update font information display
     */
    updateFontInfo() {
        if (!this.fontData) return;

        document.getElementById('fontFamily').textContent = this.fontData.family;
        document.getElementById('fontStyle').textContent = this.fontData.style;
        document.getElementById('fontWeight').textContent = this.fontData.weight;
        document.getElementById('fontFormat').textContent = this.fontData.format;
        document.getElementById('fontSize').textContent = this.formatBytes(this.fontData.size);
    }

    /**
     * Render preview text
     */
    renderPreview() {
        if (!this.ctx || !this.fontData) return;

        const size = parseInt(document.getElementById('ttfSize')?.value || 16);
        const text = document.getElementById('ttfText')?.value || 'The quick brown fox';

        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.font = `${size}px "${this.fontData.family}"`;
        this.ctx.fillStyle = '#AAFFEE';
        this.ctx.textBaseline = 'top';
        
        const lines = text.split('\n');
        const lineHeight = size * 1.2;
        
        lines.forEach((line, i) => {
            this.ctx.fillText(line, 10, 10 + i * lineHeight);
        });
    }

    /**
     * Extract glyphs and display catalog
     */
    extractGlyphs() {
        const glyphGrid = document.getElementById('glyphGrid');
        if (!glyphGrid || !this.fontData) return;

        glyphGrid.innerHTML = '';

        // Common character ranges
        const ranges = [
            { start: 0x20, end: 0x7E, name: 'ASCII' },      // Basic Latin
            { start: 0x2500, end: 0x257F, name: 'Box' },     // Box Drawing
            { start: 0x2580, end: 0x259F, name: 'Block' },   // Block Elements
        ];

        ranges.forEach(range => {
            for (let code = range.start; code <= range.end; code++) {
                const char = String.fromCodePoint(code);
                const item = document.createElement('div');
                item.className = 'glyph-item';
                item.textContent = char;
                item.title = `U+${code.toString(16).toUpperCase().padStart(4, '0')}`;
                item.style.fontFamily = `"${this.fontData.family}"`;
                
                item.addEventListener('click', () => {
                    this.renderGlyphBitmap(char, code);
                });
                
                glyphGrid.appendChild(item);
            }
        });
    }

    /**
     * Render a single glyph as bitmap
     */
    renderGlyphBitmap(char, code) {
        if (!this.ctx) return;

        const size = 16;
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = size;
        tempCanvas.height = size;
        const tempCtx = tempCanvas.getContext('2d');

        tempCtx.font = `${size}px "${this.fontData.family}"`;
        tempCtx.fillStyle = '#FFF';
        tempCtx.textBaseline = 'top';
        tempCtx.fillText(char, 0, 0);

        // Extract pixel data
        const imageData = tempCtx.getImageData(0, 0, size, size);
        const bitmap = this.imageDataToBitmap(imageData, size);

        console.log(`Glyph ${char} (U+${code.toString(16).toUpperCase()}):`, bitmap);
        
        return bitmap;
    }

    /**
     * Convert ImageData to binary bitmap
     */
    imageDataToBitmap(imageData, size) {
        const bitmap = [];
        const threshold = 128;

        for (let y = 0; y < size; y++) {
            const row = [];
            for (let x = 0; x < size; x++) {
                const idx = (y * size + x) * 4;
                const alpha = imageData.data[idx + 3];
                const pixel = alpha > threshold ? 1 : 0;
                row.push(pixel);
            }
            bitmap.push(row);
        }

        return bitmap;
    }

    /**
     * Export entire font to bitmap format
     */
    exportToBitmap() {
        if (!this.fontData) {
            alert('No font loaded');
            return null;
        }

        const bitmapFont = {
            name: this.fontData.name,
            version: '1.0.0',
            gridSize: 16,
            glyphs: {}
        };

        // Process printable ASCII + box drawing
        const ranges = [
            { start: 0x20, end: 0x7E },     // ASCII
            { start: 0x2500, end: 0x257F }, // Box Drawing
            { start: 0x2580, end: 0x259F }, // Block Elements
        ];

        ranges.forEach(range => {
            for (let code = range.start; code <= range.end; code++) {
                const char = String.fromCodePoint(code);
                const bitmap = this.renderGlyphBitmap(char, code);
                bitmapFont.glyphs[char] = bitmap;
            }
        });

        console.log('Exported bitmap font:', bitmapFont);
        alert(`Exported ${Object.keys(bitmapFont.glyphs).length} glyphs to bitmap format`);
        
        return bitmapFont;
    }

    /**
     * Format file size
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
}

// Export for use in main app
window.TTFProcessor = TTFProcessor;
