/**
 * uDOS Typography Manager - v1.0.10
 * Font loading, switching, and rendering management
 */

class TypographyManager {
  constructor() {
    this.currentTheme = 'classic';
    this.availableFonts = new Map();
    this.loadedFonts = new Set();
    this.fontSettings = {
      teletext: { size: 16, spacing: 1.0 },
      classic: { size: 9, spacing: 1.2 },
      mono: { size: 12, spacing: 1.1 }
    };

    this.initializeFonts();
  }

  async initializeFonts() {
    // Define available font families
    this.availableFonts.set('teletext', {
      name: 'MODE7GX3',
      file: '../teletext/fonts/MODE7GX3.TTF',
      fallback: 'Courier New, monospace',
      type: 'teletext',
      description: 'Classic teletext/videotext font'
    });

    // Classic Mac Fonts from /extensions/fonts
    this.availableFonts.set('chicago', {
      name: 'ChicagoFLF',
      file: '../../fonts/ChicagoFLF.ttf',
      fallback: 'Geneva, Helvetica, sans-serif',
      type: 'classic',
      description: 'Classic Mac Chicago system font'
    });

    this.availableFonts.set('pixel-chicago', {
      name: 'pixChicago',
      file: '../../fonts/pixChicago.ttf',
      fallback: 'ChicagoFLF, monospace',
      type: 'pixel',
      description: 'Pixel-perfect Chicago font'
    });

    this.availableFonts.set('geneva', {
      name: 'Geneva9',
      file: '../../fonts/geneva_9.ttf',
      fallback: 'Geneva, sans-serif',
      type: 'classic',
      description: 'Classic Mac Geneva 9pt font'
    });

    this.availableFonts.set('monaco', {
      name: 'Monaco',
      file: '../../fonts/monaco.ttf',
      fallback: 'Courier New, monospace',
      type: 'classic',
      description: 'Classic Mac Monaco monospace font'
    });

    this.availableFonts.set('athene', {
      name: 'Athene',
      file: '../../fonts/Athene.ttf',
      fallback: 'serif',
      type: 'serif',
      description: 'Athene serif font'
    });

    this.availableFonts.set('lexington-gothic', {
      name: 'LexingtonGothic',
      file: '../../fonts/Lexington-Gothic.ttf',
      fallback: 'sans-serif',
      type: 'gothic',
      description: 'Lexington Gothic display font'
    });

    this.availableFonts.set('liverpool', {
      name: 'Liverpool',
      file: '../../fonts/Liverpool.ttf',
      fallback: 'serif',
      type: 'serif',
      description: 'Liverpool serif font'
    });

    this.availableFonts.set('los-altos', {
      name: 'LosAltos',
      file: '../../fonts/Los Altos.ttf',
      fallback: 'sans-serif',
      type: 'sans',
      description: 'Los Altos display font'
    });

    this.availableFonts.set('parc-place', {
      name: 'ParcPlace',
      file: '../../fonts/Parc Place.ttf',
      fallback: 'sans-serif',
      type: 'sans',
      description: 'Parc Place system font'
    });

    this.availableFonts.set('parc-place-legacy', {
      name: 'ParcPlaceLegacy',
      file: '../../fonts/Parc Place Legacy.ttf',
      fallback: 'sans-serif',
      type: 'sans',
      description: 'Parc Place Legacy system font'
    });

    this.availableFonts.set('sanfrisco', {
      name: 'Sanfrisco',
      file: '../../fonts/Sanfrisco.ttf',
      fallback: 'sans-serif',
      type: 'sans',
      description: 'Sanfrisco display font'
    });

    this.availableFonts.set('torrance', {
      name: 'Torrance',
      file: '../../fonts/Torrance.ttf',
      fallback: 'serif',
      type: 'serif',
      description: 'Torrance serif font'
    });

    this.availableFonts.set('valencia', {
      name: 'Valencia',
      file: '../../fonts/Valencia.ttf',
      fallback: 'serif',
      type: 'serif',
      description: 'Valencia serif font'
    });

    // Monaspace Variable Fonts
    this.availableFonts.set('mono-neon', {
      name: 'MonaspaceNeon',
      file: '../../clone/monaspace-fonts/fonts/Variable Fonts/MonaspaceNeon-Variable.ttf',
      fallback: 'Courier New, monospace',
      type: 'variable',
      description: 'Monaspace Neon - Variable width coding font'
    });

    this.availableFonts.set('mono-xenon', {
      name: 'MonaspaceXenon',
      file: '../../clone/monaspace-fonts/fonts/Variable Fonts/MonaspaceXenon-Variable.ttf',
      fallback: 'Courier New, monospace',
      type: 'variable',
      description: 'Monaspace Xenon - Serif coding font'
    });

    this.availableFonts.set('mono-krypton', {
      name: 'MonaspaceKrypton',
      file: '../../clone/monaspace-fonts/fonts/Variable Fonts/MonaspaceKrypton-Variable.ttf',
      fallback: 'Courier New, monospace',
      type: 'variable',
      description: 'Monaspace Krypton - Mechanical coding font'
    });

    // Load fonts asynchronously
    await this.loadAllFonts();

    // Apply default theme
    this.applyTheme(this.currentTheme);
  }

  async loadAllFonts() {
    const fontPromises = [];

    for (const [key, font] of this.availableFonts) {
      fontPromises.push(this.loadFont(key, font));
    }

    try {
      await Promise.allSettled(fontPromises);
      this.logFontLoadingResults();
    } catch (error) {
      console.warn('Some fonts failed to load:', error);
    }
  }

  async loadFont(key, fontConfig) {
    try {
      // Use CSS Font Loading API if available
      if ('fonts' in document) {
        const fontFace = new FontFace(
          fontConfig.name,
          `url(${fontConfig.file})`,
          { display: 'swap' }
        );

        await fontFace.load();
        document.fonts.add(fontFace);
        this.loadedFonts.add(key);

        console.log(`✅ Loaded font: ${fontConfig.name}`);
        return true;
      } else {
        // Fallback for older browsers
        return this.loadFontFallback(key, fontConfig);
      }
    } catch (error) {
      console.warn(`❌ Failed to load font ${fontConfig.name}:`, error);
      return false;
    }
  }

  loadFontFallback(key, fontConfig) {
    return new Promise((resolve) => {
      const testString = 'abcdefghijklmnopqrstuvwxyz0123456789';
      const fallbackFont = fontConfig.fallback.split(',')[0];

      // Create test elements
      const fallback = document.createElement('div');
      const target = document.createElement('div');

      fallback.style.fontFamily = fallbackFont;
      target.style.fontFamily = `${fontConfig.name}, ${fallbackFont}`;

      [fallback, target].forEach(el => {
        el.style.fontSize = '16px';
        el.style.position = 'absolute';
        el.style.left = '-9999px';
        el.style.visibility = 'hidden';
        el.textContent = testString;
        document.body.appendChild(el);
      });

      const fallbackWidth = fallback.offsetWidth;

      // Check if font loaded (width changed)
      const checkFont = () => {
        if (target.offsetWidth !== fallbackWidth) {
          this.loadedFonts.add(key);
          cleanup();
          resolve(true);
        }
      };

      const cleanup = () => {
        document.body.removeChild(fallback);
        document.body.removeChild(target);
      };

      // Poll for font load
      const interval = setInterval(checkFont, 100);

      // Timeout after 3 seconds
      setTimeout(() => {
        clearInterval(interval);
        cleanup();
        resolve(false);
      }, 3000);
    });
  }

  logFontLoadingResults() {
    console.log('📝 Font Loading Results:');
    for (const [key, font] of this.availableFonts) {
      const status = this.loadedFonts.has(key) ? '✅' : '❌';
      console.log(`  ${status} ${font.name} (${key})`);
    }
  }

  // Theme Management
  applyTheme(themeName) {
    const themes = {
      classic: {
        primary: 'var(--font-classic)',
        mono: 'var(--font-monaco)',
        size: '9px',
        effects: []
      },
      retro: {
        primary: 'var(--font-teletext)',
        mono: 'var(--font-teletext)',
        size: '16px',
        effects: ['retro-glow']
      },
      pixel: {
        primary: 'var(--font-pixel)',
        mono: 'var(--font-pixel)',
        size: '9px',
        effects: ['retro-shadow']
      },
      geneva: {
        primary: 'var(--font-geneva)',
        mono: 'var(--font-monaco)',
        size: '9px',
        effects: []
      },
      modern: {
        primary: 'var(--font-mono-neon)',
        mono: 'var(--font-mono-neon)',
        size: '12px',
        effects: []
      },
      hacker: {
        primary: 'var(--font-mono-xenon)',
        mono: 'var(--font-mono-xenon)',
        size: '12px',
        effects: ['terminal-glow']
      },
      gothic: {
        primary: 'var(--font-gothic)',
        mono: 'var(--font-monaco)',
        size: '12px',
        effects: []
      },
      serif: {
        primary: 'var(--font-valencia)',
        mono: 'var(--font-monaco)',
        size: '12px',
        effects: []
      }
    };

    const theme = themes[themeName];
    if (!theme) {
      console.warn(`Theme "${themeName}" not found`);
      return;
    }

    // Apply theme to document
    document.documentElement.style.setProperty('--primary-font', theme.primary);
    document.documentElement.style.setProperty('--mono-font', theme.mono);
    document.documentElement.style.setProperty('--font-size-base', theme.size);

    // Remove old theme classes
    document.body.classList.remove(
      'theme-classic', 'theme-retro', 'theme-pixel', 'theme-geneva',
      'theme-modern', 'theme-hacker', 'theme-gothic', 'theme-serif'
    );

    // Add new theme class
    document.body.classList.add(`theme-${themeName}`);

    this.currentTheme = themeName;

    console.log(`🎨 Applied typography theme: ${themeName}`);
  }

  // Font switching utilities
  switchFont(elementSelector, fontKey) {
    const elements = document.querySelectorAll(elementSelector);
    const font = this.availableFonts.get(fontKey);

    if (!font) {
      console.warn(`Font "${fontKey}" not found`);
      return;
    }

    elements.forEach(el => {
      if (this.loadedFonts.has(fontKey)) {
        el.style.fontFamily = `${font.name}, ${font.fallback}`;
      } else {
        el.style.fontFamily = font.fallback;
        console.warn(`Font ${font.name} not loaded, using fallback`);
      }
    });
  }

  // Text effects
  applyTextEffect(elementSelector, effectName) {
    const elements = document.querySelectorAll(elementSelector);
    const effects = {
      'retro-shadow': 'retro-shadow',
      'retro-glow': 'retro-glow',
      'terminal-glow': 'terminal-glow',
      'teletext-double': 'teletext-double'
    };

    const effectClass = effects[effectName];
    if (!effectClass) {
      console.warn(`Effect "${effectName}" not found`);
      return;
    }

    elements.forEach(el => {
      el.classList.add(effectClass);
    });
  }

  // ASCII Art and Block Character utilities
  renderASCII(text, container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }

    if (!container) {
      console.warn('ASCII container not found');
      return;
    }

    container.innerHTML = '';
    container.className += ' ascii-art font-teletext';
    container.textContent = text;
  }

  renderTeletextBlocks(content, container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }

    if (!container) {
      console.warn('Teletext container not found');
      return;
    }

    container.innerHTML = content;
    container.className += ' block-chars font-teletext';
  }

  // Font metrics and sizing
  calculateOptimalSize(containerWidth, containerHeight, textLength) {
    const avgCharWidth = 0.6; // Approximate character width ratio
    const lineHeight = 1.2;

    const maxFontSizeByWidth = containerWidth / (textLength * avgCharWidth);
    const maxFontSizeByHeight = containerHeight / lineHeight;

    return Math.min(maxFontSizeByWidth, maxFontSizeByHeight, 72); // Cap at 72px
  }

  // Viewport-aware text scaling
  scaleTextForViewport() {
    const viewport = this.getViewportInfo();
    const scaleFactor = Math.min(viewport.width / 1920, viewport.height / 1080);

    // Adjust base font sizes
    const newSizes = {
      xs: Math.max(6, 8 * scaleFactor),
      sm: Math.max(7, 9 * scaleFactor),
      md: Math.max(9, 12 * scaleFactor),
      lg: Math.max(11, 14 * scaleFactor),
      xl: Math.max(13, 16 * scaleFactor),
      xxl: Math.max(15, 20 * scaleFactor)
    };

    Object.entries(newSizes).forEach(([size, pixels]) => {
      document.documentElement.style.setProperty(`--font-size-${size}`, `${pixels}px`);
    });
  }

  getViewportInfo() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio || 1
    };
  }

  // Font management utilities
  getFontLoadStatus() {
    const status = {};
    for (const [key, font] of this.availableFonts) {
      status[key] = {
        name: font.name,
        loaded: this.loadedFonts.has(key),
        description: font.description
      };
    }
    return status;
  }

  getAvailableThemes() {
    return ['classic', 'retro', 'pixel', 'geneva', 'modern', 'hacker', 'gothic', 'serif'];
  }

  getCurrentTheme() {
    return this.currentTheme;
  }

  // Export settings
  exportTypographySettings() {
    return {
      theme: this.currentTheme,
      loadedFonts: Array.from(this.loadedFonts),
      fontSettings: this.fontSettings,
      customCSS: this.getCustomCSS()
    };
  }

  getCustomCSS() {
    const computedStyle = getComputedStyle(document.documentElement);
    return {
      primaryFont: computedStyle.getPropertyValue('--primary-font'),
      monoFont: computedStyle.getPropertyValue('--mono-font'),
      baseFontSize: computedStyle.getPropertyValue('--font-size-base')
    };
  }
}

// Initialize typography manager
window.typographyManager = new TypographyManager();

// Global typography functions
window.switchTypographyTheme = function(theme) {
  window.typographyManager.applyTheme(theme);
};

window.applyTextEffect = function(selector, effect) {
  window.typographyManager.applyTextEffect(selector, effect);
};

window.renderASCII = function(text, container) {
  window.typographyManager.renderASCII(text, container);
};

// Auto-scale on resize
window.addEventListener('resize', () => {
  window.typographyManager.scaleTextForViewport();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TypographyManager;
}
