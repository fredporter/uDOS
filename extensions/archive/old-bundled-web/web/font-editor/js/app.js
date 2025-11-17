/**
 * uDOS Font Editor - Main Application
 * Initializes all components and wires up event handlers
 */

// Global state
let editor;
let fontManager;
let preview;
let currentGlyph = 0x0041; // Start with 'A'
let glyphStats = { total: 0, edited: 0 };

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔮 uDOS Font Editor starting...');

    // Initialize components
    editor = new GridEditor('grid-editor', 16);
    fontManager = new FontManager();
    preview = new FontPreview('preview-canvas', fontManager);

    // Setup event handlers
    setupGlyphSelector();
    setupTools();
    setupFileOperations();
    setupKeyboardShortcuts();
    setupMetadata();

    // Load initial glyph
    loadCurrentGlyph();
    updateStats();
    preview.render();

    console.log('✅ Font Editor ready!');
});

/**
 * Setup glyph selector dropdown
 */
function setupGlyphSelector() {
    const select = document.getElementById('glyph-select');

    // Populate ASCII printable characters (32-126)
    const asciiGroup = document.createElement('optgroup');
    asciiGroup.label = 'ASCII Printable';
    for (let code = 32; code <= 126; code++) {
        const char = String.fromCharCode(code);
        const option = document.createElement('option');
        option.value = code;
        option.textContent = `${char} (U+${code.toString(16).toUpperCase().padStart(4, '0')})`;
        asciiGroup.appendChild(option);
    }
    select.appendChild(asciiGroup);

    // Box Drawing Characters (U+2500-2510)
    const boxGroup = document.createElement('optgroup');
    boxGroup.label = 'Box Drawing';
    const boxChars = [
        0x2500, 0x2502, 0x250C, 0x2510, 0x2514, 0x2518, 0x251C, 0x2524,
        0x252C, 0x2534, 0x253C, 0x2550, 0x2551, 0x2552, 0x2553, 0x2554, 0x2555
    ];
    boxChars.forEach(code => {
        const char = String.fromCharCode(code);
        const option = document.createElement('option');
        option.value = code;
        option.textContent = `${char} (U+${code.toString(16).toUpperCase().padStart(4, '0')})`;
        boxGroup.appendChild(option);
    });
    select.appendChild(boxGroup);

    // Block Elements (U+2580-2588)
    const blockGroup = document.createElement('optgroup');
    blockGroup.label = 'Block Elements';
    const blockChars = [0x2580, 0x2584, 0x2588, 0x258C, 0x2590, 0x2591, 0x2592, 0x2593];
    blockChars.forEach(code => {
        const char = String.fromCharCode(code);
        const option = document.createElement('option');
        option.value = code;
        option.textContent = `${char} (U+${code.toString(16).toUpperCase().padStart(4, '0')})`;
        blockGroup.appendChild(option);
    });
    select.appendChild(blockGroup);

    // Change handler
    select.addEventListener('change', (e) => {
        currentGlyph = parseInt(e.target.value);
        loadCurrentGlyph();
        updateCurrentGlyphDisplay();
    });

    // Set initial value
    select.value = currentGlyph;

    // Navigation buttons
    document.getElementById('prev-glyph').addEventListener('click', () => {
        navigateGlyph(-1);
    });

    document.getElementById('next-glyph').addEventListener('click', () => {
        navigateGlyph(1);
    });
}

/**
 * Load current glyph from font manager
 */
function loadCurrentGlyph() {
    const data = fontManager.loadGlyph(currentGlyph);
    if (data) {
        editor.fromJSON(data);
    } else {
        editor.clear();
    }
}

/**
 * Setup tool buttons
 */
function setupTools() {
    // Auto-save on any pixel change
    editor.onPixelChange = () => {
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
        updateStats();
    };

    // Clear button
    document.getElementById('clear').addEventListener('click', () => {
        editor.clear();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
        updateStats();
    });

    // Fill button
    document.getElementById('fill').addEventListener('click', () => {
        editor.fill();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
        updateStats();
    });

    // Flip horizontal
    document.getElementById('flip-h').addEventListener('click', () => {
        editor.flipH();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
    });

    // Flip vertical
    document.getElementById('flip-v').addEventListener('click', () => {
        editor.flipV();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
    });

    // Rotate 90°
    document.getElementById('rotate').addEventListener('click', () => {
        editor.rotate90();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
    });

    // Invert
    document.getElementById('invert').addEventListener('click', () => {
        editor.invert();
        fontManager.saveGlyph(currentGlyph, editor.toJSON());
        preview.render();
    });
}

/**
 * Setup file operation buttons
 */
function setupFileOperations() {
    const fileInput = document.getElementById('file-input');

    // Export JSON
    document.getElementById('export-json').addEventListener('click', () => {
        fontManager.exportJSON();
        showStatus('Font exported to JSON');
    });

    // Import JSON
    document.getElementById('import-json').addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
            fontManager.importJSON(e.target.files[0]);
            // Page will reload after import
        }
    });

    // Reset all
    document.getElementById('reset').addEventListener('click', () => {
        if (confirm('Clear all glyphs? This cannot be undone.')) {
            fontManager.reset();
            // Page will reload after reset
        }
    });

    // Copy glyph
    document.getElementById('copy-glyph').addEventListener('click', () => {
        const data = editor.toJSON();
        localStorage.setItem('udos-font-clipboard', JSON.stringify(data));
        showStatus('Glyph copied to clipboard');
    });

    // Paste glyph
    document.getElementById('paste-glyph').addEventListener('click', () => {
        const data = localStorage.getItem('udos-font-clipboard');
        if (data) {
            editor.fromJSON(JSON.parse(data));
            fontManager.saveGlyph(currentGlyph, editor.toJSON());
            preview.render();
            updateStats();
            showStatus('Glyph pasted');
        } else {
            showStatus('No glyph in clipboard');
        }
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Don't trigger shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        // Prevent default for handled keys
        const handled = ['Space', 'KeyC', 'KeyF', 'KeyH', 'KeyV', 'KeyR', 'KeyI',
                         'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
        if (handled.includes(e.code)) {
            e.preventDefault();
        }

        switch (e.code) {
            case 'Space':
                editor.clear();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                updateStats();
                break;

            case 'KeyC':
                const data = editor.toJSON();
                localStorage.setItem('udos-font-clipboard', JSON.stringify(data));
                showStatus('Copied');
                break;

            case 'KeyF':
                editor.fill();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                updateStats();
                break;

            case 'KeyH':
                editor.flipH();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                break;

            case 'KeyV':
                editor.flipV();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                break;

            case 'KeyR':
                editor.rotate90();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                break;

            case 'KeyI':
                editor.invert();
                fontManager.saveGlyph(currentGlyph, editor.toJSON());
                preview.render();
                break;

            case 'ArrowLeft':
                navigateGlyph(-1);
                break;

            case 'ArrowRight':
                navigateGlyph(1);
                break;

            case 'ArrowUp':
                navigateGlyph(-16);
                break;

            case 'ArrowDown':
                navigateGlyph(16);
                break;
        }
    });
}

/**
 * Navigate to adjacent glyph
 */
function navigateGlyph(offset) {
    const select = document.getElementById('glyph-select');
    const options = Array.from(select.options);
    const currentIndex = options.findIndex(opt => parseInt(opt.value) === currentGlyph);

    if (currentIndex !== -1) {
        const newIndex = currentIndex + offset;
        if (newIndex >= 0 && newIndex < options.length) {
            currentGlyph = parseInt(options[newIndex].value);
            select.value = currentGlyph;
            loadCurrentGlyph();
            updateCurrentGlyphDisplay();
        }
    }
}

/**
 * Setup metadata inputs
 */
function setupMetadata() {
    const fontNameInput = document.getElementById('font-name');
    const fontAuthorInput = document.getElementById('font-author');

    // Load saved values
    fontNameInput.value = fontManager.fontData.fontName || 'uDOS Custom';
    fontAuthorInput.value = fontManager.fontData.author || '';

    // Save on change
    fontNameInput.addEventListener('change', (e) => {
        fontManager.fontData.fontName = e.target.value;
        fontManager.fontData.modified = new Date().toISOString();
        fontManager.saveToLocalStorage();
    });

    fontAuthorInput.addEventListener('change', (e) => {
        fontManager.fontData.author = e.target.value;
        fontManager.fontData.modified = new Date().toISOString();
        fontManager.saveToLocalStorage();
    });

    // Preview text input
    const previewInput = document.getElementById('preview-text');
    previewInput.addEventListener('input', (e) => {
        preview.setPreviewText(e.target.value);
        preview.render();
    });
}

/**
 * Update statistics display
 */
function updateStats() {
    const glyphCount = Object.keys(fontManager.fontData.glyphs).length;
    document.getElementById('glyph-count').textContent = glyphCount;
    updateCurrentGlyphDisplay();
}

/**
 * Update current glyph unicode display
 */
function updateCurrentGlyphDisplay() {
    const unicode = `U+${currentGlyph.toString(16).toUpperCase().padStart(4, '0')}`;
    const char = String.fromCharCode(currentGlyph);
    document.getElementById('current-unicode').textContent = `${char} ${unicode}`;
}

/**
 * Show temporary status message
 */
function showStatus(message) {
    const status = document.getElementById('status-message');
    if (status) {
        status.textContent = message;
        status.style.display = 'block';
        setTimeout(() => {
            status.style.display = 'none';
        }, 2000);
    } else {
        console.log(`📌 ${message}`);
    }
}
