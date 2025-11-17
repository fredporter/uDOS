/**
 * uDOS Font Editor - Preview Renderer
 * Live preview of font rendering
 */

class FontPreview {
    constructor(canvasId, fontManager) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.fontManager = fontManager;
        this.previewText = "THE QUICK BROWN FOX 0123456789";
        this.pixelSize = 2; // Smaller for preview
        this.charWidth = 16;
        this.charHeight = 16;
    }

    setPreviewText(text) {
        this.previewText = text.toUpperCase();
        this.render();
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#1a1a1a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        let x = 0;
        let y = 5; // Top padding

        for (const char of this.previewText) {
            const codepoint = char.charCodeAt(0);
            const glyphData = this.fontManager.loadGlyph(codepoint);

            if (glyphData) {
                this.drawGlyph(x, y, glyphData);
            } else {
                // Draw placeholder for missing glyph
                this.drawPlaceholder(x, y);
            }

            x += this.charWidth * this.pixelSize + 2; // Spacing between chars

            // Wrap to next line if needed
            if (x > this.canvas.width - (this.charWidth * this.pixelSize)) {
                x = 0;
                y += this.charHeight * this.pixelSize + 5;
            }
        }
    }

    drawGlyph(offsetX, offsetY, glyphData) {
        this.ctx.fillStyle = '#00ff00';

        for (let y = 0; y < glyphData.length && y < this.charHeight; y++) {
            const row = glyphData[y];
            for (let x = 0; x < row.length && x < this.charWidth; x++) {
                if (row[x] === '1') {
                    this.ctx.fillRect(
                        offsetX + x * this.pixelSize,
                        offsetY + y * this.pixelSize,
                        this.pixelSize,
                        this.pixelSize
                    );
                }
            }
        }
    }

    drawPlaceholder(offsetX, offsetY) {
        // Draw a box outline for missing glyphs
        this.ctx.strokeStyle = '#333';
        this.ctx.strokeRect(
            offsetX,
            offsetY,
            this.charWidth * this.pixelSize,
            this.charHeight * this.pixelSize
        );
    }
}
