/**
 * uDOS v1.2 Controls
 * Unified theme switcher and font selector for all web extensions
 */

// ============================================
// Theme Management
// ============================================

const UDOS_THEMES = {
    dark: {
        name: 'GitHub Dark',
        icon: '🌙',
        description: 'Modern dark theme'
    },
    light: {
        name: 'GitHub Light',
        icon: '☀️',
        description: 'Modern light theme'
    },
    c64: {
        name: 'Commodore 64',
        icon: '🎮',
        description: 'Classic C64 blue'
    },
    green: {
        name: 'Green Phosphor',
        icon: '💚',
        description: 'Retro CRT green'
    },
    amber: {
        name: 'Amber Phosphor',
        icon: '🟧',
        description: 'Retro CRT amber'
    },
    apple2: {
        name: 'Apple II',
        icon: '🍏',
        description: 'Apple II green'
    }
};

function initializeTheme() {
    const savedTheme = localStorage.getItem('udos-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
}

function setTheme(themeKey) {
    const theme = UDOS_THEMES[themeKey];
    if (!theme) return;

    document.documentElement.setAttribute('data-theme', themeKey);
    localStorage.setItem('udos-theme', themeKey);
    updateThemeButton(themeKey);

    // Update active state in dropdown
    const options = document.querySelectorAll('.theme-option');
    options.forEach(opt => {
        opt.classList.toggle('active', opt.dataset.theme === themeKey);
    });

    // Close dropdown
    const dropdown = document.getElementById('theme-dropdown');
    if (dropdown) {
        dropdown.classList.remove('show');
    }

    // Dispatch custom event for extensions that need to know
    window.dispatchEvent(new CustomEvent('udos-theme-change', {
        detail: { theme: themeKey }
    }));
}

function toggleTheme() {
    // Quick toggle between dark and light only
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function toggleThemeDropdown() {
    const dropdown = document.getElementById('theme-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function updateThemeButton(themeKey) {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        const theme = UDOS_THEMES[themeKey] || UDOS_THEMES.dark;
        btn.innerHTML = `<span class="theme-icon">${theme.icon}</span>`;
        btn.setAttribute('title', theme.name);
    }
}

// ============================================
// Font Management
// ============================================

const MONASPACE_FONTS = {
    neon: {
        name: 'Monaspace Neon',
        family: 'var(--font-neon)',
        description: 'Default - Neo-grotesque sans'
    },
    argon: {
        name: 'Monaspace Argon',
        family: 'var(--font-argon)',
        description: 'Humanist sans-serif'
    },
    xenon: {
        name: 'Monaspace Xenon',
        family: 'var(--font-xenon)',
        description: 'Slab-serif monospace'
    },
    radon: {
        name: 'Monaspace Radon',
        family: 'var(--font-radon)',
        description: 'Handwriting monospace'
    },
    krypton: {
        name: 'Monaspace Krypton',
        family: 'var(--font-krypton)',
        description: 'Mechanical monospace'
    }
};

function initializeFont() {
    const savedFont = localStorage.getItem('udos-font') || 'neon';
    applyFont(savedFont);
    updateFontButton(savedFont);
}

function applyFont(fontKey) {
    const font = MONASPACE_FONTS[fontKey];
    if (!font) return;

    // Apply font to body and all monospace elements
    document.body.style.fontFamily = font.family;
    document.documentElement.style.setProperty('--font-mono', font.family);

    // Apply to code elements
    const codeElements = document.querySelectorAll('code, pre, .font-mono');
    codeElements.forEach(el => {
        el.style.fontFamily = font.family;
    });

    localStorage.setItem('udos-font', fontKey);

    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('udos-font-change', {
        detail: { font: fontKey, family: font.family }
    }));
}

function updateFontButton(fontKey) {
    const btn = document.getElementById('font-selector-btn');
    if (btn) {
        const font = MONASPACE_FONTS[fontKey];
        btn.textContent = font ? font.name : 'Monaspace Neon';
    }
}

function toggleFontDropdown() {
    const dropdown = document.getElementById('font-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function selectFont(fontKey) {
    applyFont(fontKey);
    updateFontButton(fontKey);

    // Update active state
    const options = document.querySelectorAll('.font-option');
    options.forEach(opt => {
        opt.classList.toggle('active', opt.dataset.font === fontKey);
    });

    // Close dropdown
    toggleFontDropdown();
}

// ============================================
// UI Components Creation
// ============================================

function createThemeToggle() {
    const toggle = document.createElement('div');
    toggle.className = 'theme-toggle';

    const currentTheme = localStorage.getItem('udos-theme') || 'dark';
    const themeOptions = Object.entries(UDOS_THEMES).map(([key, theme]) => `
        <div class="theme-option ${key === currentTheme ? 'active' : ''}"
             data-theme="${key}"
             onclick="setTheme('${key}')">
            <div class="theme-option-icon">${theme.icon}</div>
            <div class="theme-option-info">
                <div class="theme-option-name">${theme.name}</div>
                <div class="theme-option-desc">${theme.description}</div>
            </div>
        </div>
    `).join('');

    toggle.innerHTML = `
        <button id="theme-toggle-btn" onclick="toggleThemeDropdown()" title="Change theme">
            <span class="theme-icon">🌙</span>
        </button>
        <div id="theme-dropdown" class="theme-dropdown">
            ${themeOptions}
        </div>
    `;
    document.body.appendChild(toggle);

    // Update button with current theme
    updateThemeButton(currentTheme);

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown && !toggle.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

function createFontSelector() {
    const selector = document.createElement('div');
    selector.className = 'font-selector';

    const currentFont = localStorage.getItem('udos-font') || 'neon';
    const fontOptions = Object.entries(MONASPACE_FONTS).map(([key, font]) => `
        <div class="font-option ${key === currentFont ? 'active' : ''}"
             data-font="${key}"
             onclick="selectFont('${key}')">
            <div class="font-option-name" style="font-family: ${font.family}">${font.name}</div>
            <div class="font-option-desc">${font.description}</div>
        </div>
    `).join('');

    selector.innerHTML = `
        <button id="font-selector-btn" onclick="toggleFontDropdown()">
            ${MONASPACE_FONTS[currentFont].name}
        </button>
        <div id="font-dropdown" class="font-dropdown">
            ${fontOptions}
        </div>
    `;

    document.body.appendChild(selector);

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('font-dropdown');
        const btn = document.getElementById('font-selector-btn');
        if (dropdown && !selector.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

// ============================================
// Keyboard Shortcuts
// ============================================

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+Shift+T or Cmd+Shift+T - Toggle theme
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            toggleTheme();
        }

        // Ctrl+Shift+F or Cmd+Shift+F - Toggle font selector
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
            e.preventDefault();
            toggleFontDropdown();
        }

        // Escape - Close font dropdown
        if (e.key === 'Escape') {
            const dropdown = document.getElementById('font-dropdown');
            if (dropdown && dropdown.classList.contains('show')) {
                dropdown.classList.remove('show');
            }
        }
    });
}

// ============================================
// Initialization
// ============================================

function initializeUDOSControls(options = {}) {
    const {
        includeThemeToggle = true,
        includeFontSelector = true,
        enableKeyboardShortcuts = true
    } = options;

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        initializeTheme();
        initializeFont();

        if (includeThemeToggle) {
            createThemeToggle();
        }

        if (includeFontSelector) {
            createFontSelector();
        }

        if (enableKeyboardShortcuts) {
            initializeKeyboardShortcuts();
        }
    }
}// Auto-initialize by default
// Extensions can disable by setting data-udos-auto-init="false" on html element
if (!document.documentElement.dataset.udosAutoInit ||
    document.documentElement.dataset.udosAutoInit !== 'false') {
    initializeUDOSControls();
}

// Export for manual initialization
window.uDOSControls = {
    initializeTheme,
    toggleTheme,
    initializeFont,
    applyFont,
    selectFont,
    toggleFontDropdown,
    createThemeToggle,
    createFontSelector,
    initialize: initializeUDOSControls
};
