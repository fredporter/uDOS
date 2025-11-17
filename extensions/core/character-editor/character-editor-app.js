/**
 * uDOS Font Manager - Main Application
 * Version: 1.0.24
 */

class FontManagerApp {
    constructor() {
        this.bitmapEditor = null;
        this.ttfProcessor = null;
        this.currentTab = 'bitmap';
        this.fontLibrary = [];
        this.userProfile = null;  // Font profile from template

        this.init();
    }

    /**
     * Initialize application
     */
    init() {
        this.loadFontLibrary();
        this.loadFontSystemConfig();
        this.setupTabs();
        this.setupButtons();
        this.initializeEditors();
    }

    /**
     * Setup tab switching
     */
    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    /**
     * Switch active tab
     */
    switchTab(tab) {
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`)?.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`tab-${tab}`)?.classList.add('active');

        this.currentTab = tab;

        // Initialize tab-specific components
        if (tab === 'bitmap' && !this.bitmapEditor) {
            this.bitmapEditor = new BitmapEditor();
        } else if (tab === 'ttf' && !this.ttfProcessor) {
            this.ttfProcessor = new TTFProcessor();
        }
    }

    /**
     * Setup button handlers
     */
    setupButtons() {
        // Header buttons
        document.getElementById('btnNewFont')?.addEventListener('click', () => this.newFont());
        document.getElementById('btnLoadFont')?.addEventListener('click', () => this.loadFont());
        document.getElementById('btnLoadProfile')?.addEventListener('click', () => this.loadUserProfile());
        document.getElementById('btnSaveProfile')?.addEventListener('click', () => this.saveUserProfile());

        // Export buttons
        document.getElementById('btnExportJSON')?.addEventListener('click', () => this.exportJSON());
        document.getElementById('btnSaveToSandbox')?.addEventListener('click', () => this.saveToSandbox());
        document.getElementById('btnExportBitmap')?.addEventListener('click', () => this.exportBitmap());

        // Font upload
        document.getElementById('fontUpload')?.addEventListener('change', (e) => this.handleFontUpload(e));

        // TTF preview controls
        document.getElementById('ttfSize')?.addEventListener('input', () => {
            if (this.ttfProcessor) this.ttfProcessor.renderPreview();
        });
        document.getElementById('ttfText')?.addEventListener('input', () => {
            if (this.ttfProcessor) this.ttfProcessor.renderPreview();
        });
    }

    /**
     * Initialize editors
     */
    initializeEditors() {
        // Start with bitmap editor
        this.bitmapEditor = new BitmapEditor();
    }

    /**
     * New font
     */
    newFont() {
        if (confirm('Create new font? Current work will be saved to library.')) {
            if (this.bitmapEditor) {
                this.bitmapEditor.fontData = this.bitmapEditor.createEmptyFont();
                this.bitmapEditor.saveToLocalStorage();
                this.bitmapEditor.populateCharSelect();
                this.bitmapEditor.populateCharset();
                this.bitmapEditor.renderGrid();
                this.bitmapEditor.updateStats();
                this.bitmapEditor.showStatus('New font created');
            }
        }
    }

    /**
     * Load font from file
     */
    loadFont() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                try {
                    const text = await file.text();
                    const fontData = JSON.parse(text);

                    if (this.bitmapEditor) {
                        this.bitmapEditor.fontData = fontData;
                        this.bitmapEditor.saveToLocalStorage();
                        this.bitmapEditor.populateCharSelect();
                        this.bitmapEditor.populateCharset();
                        this.bitmapEditor.renderGrid();
                        this.bitmapEditor.updateStats();
                        this.bitmapEditor.showStatus('Font loaded');
                    }
                } catch (error) {
                    alert('Error loading font: ' + error.message);
                }
            }
        };
        input.click();
    }

    /**
     * Handle font file upload (TTF/OTF)
     */
    async handleFontUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        try {
            // Switch to TTF tab
            this.switchTab('ttf');

            // Initialize TTF processor if needed
            if (!this.ttfProcessor) {
                this.ttfProcessor = new TTFProcessor();
            }

            // Load the font
            await this.ttfProcessor.loadFont(file);
            this.showStatus(`Loaded: ${file.name}`);
        } catch (error) {
            alert('Error loading font: ' + error.message);
        }
    }

    /**
     * Export current font as JSON
     */
    exportJSON() {
        if (this.bitmapEditor) {
            this.bitmapEditor.exportJSON();
        }
    }

    /**
     * Save to sandbox
     */
    saveToSandbox() {
        if (this.bitmapEditor) {
            this.bitmapEditor.saveToSandbox();
        }
    }

    /**
     * Export TTF to bitmap
     */
    exportBitmap() {
        if (this.ttfProcessor) {
            const bitmapFont = this.ttfProcessor.exportToBitmap();

            if (bitmapFont) {
                // Switch to bitmap editor and load the converted font
                this.switchTab('bitmap');

                if (this.bitmapEditor) {
                    this.bitmapEditor.fontData = bitmapFont;
                    this.bitmapEditor.saveToLocalStorage();
                    this.bitmapEditor.populateCharSelect();
                    this.bitmapEditor.populateCharset();
                    this.bitmapEditor.renderGrid();
                    this.bitmapEditor.updateStats();
                    this.bitmapEditor.showStatus('TTF converted to bitmap');
                }
            }
        }
    }

    /**
     * Load font library from storage
     */
    loadFontLibrary() {
        // Load from localStorage or initialize empty
        try {
            const stored = localStorage.getItem('udos-font-library');
            this.fontLibrary = stored ? JSON.parse(stored) : [];
        } catch (e) {
            this.fontLibrary = [];
        }

        this.renderFontLibrary();
    }

    /**
     * Render font library list
     */
    renderFontLibrary() {
        const listEl = document.getElementById('fontList');
        if (!listEl) return;

        listEl.innerHTML = '';

        if (this.fontLibrary.length === 0) {
            listEl.innerHTML = '<div style="padding: 20px; color: #777; text-align: center;">No fonts in library<br/>Upload or create a font</div>';
            return;
        }

        this.fontLibrary.forEach((font, idx) => {
            const item = document.createElement('div');
            item.className = 'font-item';
            item.innerHTML = `
                <div class="font-item-name">${font.name}</div>
                <div class="font-item-meta">${font.version || '1.0.0'} • ${Object.keys(font.glyphs || {}).length} chars</div>
            `;

            item.addEventListener('click', () => this.loadFontFromLibrary(idx));
            listEl.appendChild(item);
        });
    }

    /**
     * Load font from library
     */
    loadFontFromLibrary(idx) {
        const font = this.fontLibrary[idx];
        if (!font) return;

        if (this.bitmapEditor) {
            this.bitmapEditor.fontData = font;
            this.bitmapEditor.saveToLocalStorage();
            this.bitmapEditor.populateCharSelect();
            this.bitmapEditor.populateCharset();
            this.bitmapEditor.renderGrid();
            this.bitmapEditor.updateStats();
            this.bitmapEditor.showStatus(`Loaded: ${font.name}`);
        }

        this.switchTab('bitmap');
    }

    /**
     * Show status message
     */
    showStatus(message) {
        const statusEl = document.getElementById('statusMessage');
        if (statusEl) {
            statusEl.textContent = message;
            setTimeout(() => {
                statusEl.textContent = 'Ready';
            }, 3000);
        }
    }

    /**
     * Load font system configuration
     */
    async loadFontSystemConfig() {
        try {
            const response = await fetch('../../knowledge/system/font-system.json');
            if (response.ok) {
                this.fontSystemConfig = await response.json();
                console.log('✅ Loaded font system configuration');
            }
        } catch (error) {
            console.warn('⚠️ Could not load font system config:', error);
        }
    }

    /**
     * Load user font profile template
     */
    async loadUserProfile() {
        try {
            // Try to load existing profile from memory/user/
            let response = await fetch('../../memory/user/font-profile-template.json');

            if (!response.ok) {
                // Fall back to system template
                response = await fetch('../../data/templates/font-profile-template.json');
            }

            if (response.ok) {
                this.userProfile = await response.json();
                this.applyUserProfile();
                this.showStatus('Font profile loaded');
            } else {
                alert('Font profile not found. Please ensure template exists in data/templates/');
            }
        } catch (error) {
            alert('Error loading profile: ' + error.message);
        }
    }

    /**
     * Apply user profile settings to editor
     */
    applyUserProfile() {
        if (!this.userProfile) return;

        console.log('Applying profile:', this.userProfile.metadata.name);

        // Apply font settings to editor
        if (this.userProfile.font_settings && this.bitmapEditor) {
            // Could update editor defaults here
        }

        // Apply color scheme
        if (this.userProfile.color_scheme) {
            this.applyColorScheme(this.userProfile.color_scheme);
        }

        this.showStatus(`Profile: ${this.userProfile.metadata.name}`);
    }

    /**
     * Apply color scheme from profile
     */
    applyColorScheme(colorScheme) {
        if (!colorScheme.custom_colors) return;

        // Update CSS variables
        const root = document.documentElement;
        Object.entries(colorScheme.custom_colors).forEach(([name, color]) => {
            if (color.hex) {
                root.style.setProperty(`--profile-${name}`, color.hex);
            }
        });
    }

    /**
     * Save user profile
     */
    async saveUserProfile() {
        if (!this.userProfile) {
            alert('No profile loaded. Load a template first with "Load Profile"');
            return;
        }

        // Update metadata
        this.userProfile.metadata.modified_date = new Date().toISOString();

        // Export as JSON file
        const blob = new Blob([JSON.stringify(this.userProfile, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `font-profile-${this.userProfile.metadata.name.toLowerCase().replace(/\s+/g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showStatus('Profile saved!');
    }

    /**
     * Create new profile from template
     */
    async createProfileFromTemplate() {
        try {
            const response = await fetch('../../data/templates/font-profile-template.json');
            if (response.ok) {
                const template = await response.json();

                // Prompt for profile name
                const profileName = prompt('Enter profile name:', 'My Custom Profile');
                if (!profileName) return;

                // Duplicate template
                this.userProfile = JSON.parse(JSON.stringify(template));
                this.userProfile.metadata.name = profileName;
                this.userProfile.metadata.created_date = new Date().toISOString();
                this.userProfile.metadata.modified_date = new Date().toISOString();
                this.userProfile.metadata.author = prompt('Author name (optional):', '') || '';

                this.showStatus(`Created profile: ${profileName}`);
                this.applyUserProfile();
            }
        } catch (error) {
            alert('Error creating profile: ' + error.message);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.fontManagerApp = new FontManagerApp();
});
