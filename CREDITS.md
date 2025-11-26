# uDOS Credits & Attributions

## 🎯 Core Project

**uDOS** - Secure Dual-Interface CLI Framework
- **Author**: Fred Porter
- **License**: See LICENSE.txt
- **Repository**: https://github.com/fredporter/uDOS
- **Version**: v1.1.0 (First Stable Public Release)
- **Test Coverage**: 1,810 tests (100% passing)

---

## 👥 Contributors

### Lead Developer
- **Fred Porter** - Project creator, architecture, and implementation

### Development Assistance
- **GitHub Copilot** - AI assistant for development, refactoring, code review, and test generation

### Special Thanks
- All contributors to the v1.1.x milestone releases
- Testing community for cross-platform validation
- Open-source community for dependencies and frameworks

---

## 📦 Python Dependencies

### Core Dependencies

#### prompt_toolkit
- **License**: BSD-3-Clause
- **Purpose**: Terminal UI, input handling, autocomplete
- **URL**: https://github.com/prompt-toolkit/python-prompt-toolkit

#### python-dotenv
- **License**: BSD-3-Clause
- **Purpose**: Environment variable management
- **URL**: https://github.com/theskumar/python-dotenv

#### psutil
- **License**: BSD-3-Clause
- **Purpose**: System and process monitoring
- **URL**: https://github.com/giampaolo/psutil

#### requests
- **License**: Apache-2.0
- **Purpose**: HTTP library for API calls
- **URL**: https://github.com/psf/requests

#### cryptography
- **License**: Apache-2.0 / BSD-3-Clause
- **Purpose**: AES-256/AES-128 encryption for 4-tier memory system
- **URL**: https://github.com/pyca/cryptography
- **Used in**: v1.1.2 4-tier memory encryption (Tier 1 & 2)

### Web GUI Dependencies (Optional)

#### Flask
- **License**: BSD-3-Clause
- **Purpose**: Web server framework
- **URL**: https://github.com/pallets/flask
- **Used in**: v1.1.1 web GUI, teletext display

#### Flask-CORS
- **License**: MIT
- **Purpose**: Cross-Origin Resource Sharing support
- **URL**: https://github.com/corydolphin/flask-cors

#### Flask-SocketIO
- **License**: MIT
- **Purpose**: WebSocket support for real-time CLI↔Web sync
- **URL**: https://github.com/miguelgrinberg/Flask-SocketIO
- **Used in**: v1.1.1 state synchronization engine

### AI Integration (Optional)

#### google-generativeai
- **License**: Apache-2.0
- **Purpose**: OK Assistant integration for assistant features
- **URL**: https://github.com/google/generative-ai-python
- **Used in**: v1.1.0 AI assistant, offline-first fallback

### Development Dependencies

#### pytest
- **License**: MIT
- **Purpose**: Testing framework
- **URL**: https://github.com/pytest-dev/pytest
- **Tests**: 1,062 tests in v1.1.0-v1.1.2

#### pytest-cov
- **License**: MIT
- **Purpose**: Code coverage reporting
- **URL**: https://github.com/pytest-dev/pytest-cov

---

## 🔧 Bundled Extensions

All extensions are maintained as part of the uDOS project for stability and integration.

### Dashboard - Web Interface
- **License**: MIT
- **Copyright**: © 2024-2025 Fred Porter
- **Purpose**: Modern web-based dashboard interface for uDOS
- **Location**: extensions/bundled/web/dashboard

### Font Editor - Typography Tool
- **License**: MIT
- **Copyright**: © 2024-2025 Fred Porter
- **Purpose**: Web-based font creation and editing tool
- **Location**: extensions/bundled/web/font-editor

### System Desktop - Classic Interface
- **License**: MIT
- **Copyright**: © 2024-2025 Fred Porter
- **Purpose**: Classic desktop-style interface for uDOS
- **Location**: extensions/bundled/web/system-desktop

### Teletext - Retro Display
- **License**: MIT
- **Copyright**: © 2024-2025 Fred Porter
- **Purpose**: Teletext-style display and content creation system
- **Location**: extensions/bundled/web/teletext

---

## 🎨 CSS Frameworks

### classic.css - Mac OS 8.1 Interface
- **Original**: https://github.com/npjg/classic.css
- **License**: MIT
- **Author**: npjg
- **Purpose**: Authentic Mac OS 8.1 interface components for web applications
- **Acknowledgements**: Built upon after-dark-css, ChicagoFLF font (public domain)

**License Summary**: Generate a Classic Mac interface in your browser with authentic window styling and controls.

### NES.css - 8-bit Nintendo Style
- **Original**: https://github.com/nostalgic-css/NES.css
- **License**: MIT
- **Copyright**: © 2018 B.C.Rikko
- **Purpose**: NES-style (8bit-like) CSS Framework for retro gaming interfaces
- **Font Recommendation**: Press Start 2P (Google Fonts)

**License Summary**: Code released under MIT License. Documentation under Creative Commons.

### system.css - Classic Mac System 6
- **Original**: https://github.com/sakofchit/system.css
- **License**: MIT
- **Author**: Sakun Srivatsa (@sakofchit)
- **Purpose**: Apple System OS interface (1984-1991) based on System 6
- **Fonts**: Chicago 12pt and Geneva 9pt recreations by @blogmywiki

**License Summary**: CSS library for building monochrome classic Mac interfaces without JavaScript.

### after-dark-css - Screensaver Animations
- **Original**: https://github.com/bryanbraun/after-dark-css
- **License**: MIT (code), SIL OFL (fonts), Berkeley Systems (images)
- **Author**: Bryan Braun
- **Purpose**: After Dark™ screensaver recreations using pure CSS animations
- **Font**: ChicagoFLF (public domain by Robin Casady)

**License Summary**: HTML & CSS under MIT. Images copyright Berkeley Systems. Full reuse probably ok, use at own risk.

---

### System Style - Theme Framework
- **License**: MIT
- **Copyright**: © 2024-2025 Fred Porter
- **Purpose**: Theme and style management system for web interfaces
- **Location**: extensions/bundled/web/system-style

**License Summary**: Permission granted to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies.

---

## 🎨 Assets & Resources

### CSS Frameworks

#### classic.css
- **Author**: npjg
- **License**: MIT
- **URL**: https://github.com/npjg/classic.css
- **Purpose**: Mac OS 8.1-inspired retro interface styling
- **Used in**: Dashboard web interface

#### NES.css
- **Author**: nostalgic-css
- **License**: MIT
- **URL**: https://github.com/nostalgic-css/NES.css
- **Purpose**: NES-style (8bit-like) CSS framework
- **Used in**: Retro-themed interface components

#### system.css
- **Author**: sakofchit
- **License**: MIT
- **URL**: https://github.com/sakofchit/system.css
- **Purpose**: Windows-inspired CSS framework
- **Used in**: System-themed UI components

---

## 🔤 Font Licenses

### Monaspace Font Family
- **Original**: https://github.com/githubnext/monaspace
- **uDOS Fork**: https://github.com/fredporter/udos-fonts
- **License**: SIL Open Font License (OFL) 1.1
- **Copyright**: © 2023 GitHub Next
- **Variants**: Neon, Argon, Xenon, Radon, Krypton

**OFL 1.1 License Summary:**
- ✅ **Permitted**: Use, study, modify, redistribute freely
- ✅ **Commercial Use**: Allowed in any software (free or commercial)
- ✅ **Bundling**: Can be bundled with software of any license
- ✅ **Modification**: Can create derivative works
- ❌ **Standalone Sale**: Cannot sell fonts by themselves as a product
- ⚠️  **Renaming Required**: Modified versions must use different font name
- ⚠️  **No Endorsement**: Cannot use GitHub's name without permission

**Full OFL License**: See `extensions/forks/fonts/monaspace/LICENSE`

**Font Files Included**:
- Monaspace Neon (WOFF2, OTF) - Neo-grotesque sans
- Monaspace Argon (WOFF2, OTF) - Humanist sans
- Monaspace Xenon (WOFF2, OTF) - Slab serif
- Monaspace Radon (WOFF2, OTF) - Handwriting style
- Monaspace Krypton (WOFF2, OTF) - Mechanical sans

---

## 📐 Unicode Character Sets

### Box Drawing Characters (U+2500 - U+257F)
- **Standard**: Unicode 3.0
- **Copyright**: Unicode Consortium
- **License**: Unicode License Agreement (Public domain for display)
- **Purpose**: Terminal UI borders, boxes, and frames

### Block Elements (U+2580 - U+259F)
- **Standard**: Unicode 3.0
- **Copyright**: Unicode Consortium
- **License**: Unicode License Agreement (Public domain for display)
- **Purpose**: Pixel art, progress bars, visual indicators

**Examples Used**:
- ╔═╗╚═╝║ - Box drawing (double lines)
- ─│┌┐└┘├┤┬┴┼ - Box drawing (single lines)
- █▓▒░ - Block elements (shading)
- ▀▄ - Half blocks

---

## 🙏 Special Thanks

- **The Open Source Community** - For creating and maintaining the incredible tools we build upon
- **GitHub Next** - For Monaspace fonts and advancing developer tools
- **Terminal Emulator Developers** - For pushing the boundaries of what's possible in the terminal
- **Unicode Consortium** - For standardizing character sets that make CLI graphics possible
- **Python Community** - For building excellent libraries and maintaining a welcoming ecosystem
- **Early Testers** - For feedback and suggestions that shaped uDOS

---

## 📜 License Compliance

### MIT-Licensed Components
All MIT-licensed components in this project grant the following permissions:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ⚠️  Must include original copyright notice and license

### OFL-Licensed Fonts
The Monaspace fonts are licensed under SIL OFL 1.1:
- ✅ Free to use in any software
- ✅ Can be bundled with uDOS distribution
- ❌ Cannot be sold as standalone font products
- ⚠️  Modified versions require name change

### Apache 2.0 Licensed Components
The Google Generative AI library:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Patent grant
- ⚠️  Must include NOTICE file if one exists

---

## 📋 Full License Texts

All component licenses are preserved in their original locations:

- **uDOS**: `LICENSE.txt` (MIT)
- **Python dependencies**: See PyPI package pages
- **micro**: `extensions/forks/micro/LICENSE`
- **typo**: `extensions/forks/typo/LICENSE`
- **cmd.js**: `extensions/forks/cmd/LICENSE`
- **Monaspace**: `extensions/forks/fonts/monaspace/LICENSE` (OFL)
- **CSS Frameworks**: See individual framework repositories

---

## 🔍 Credits Version

**Credits Version**: 1.0.0
**Last Updated**: November 1, 2025
**Maintained By**: Fred Porter

---

## 📧 Contact & Contributions

For questions about licensing or attribution:
- **GitHub Issues**: https://github.com/fredporter/uDOS/issues
- **Repository**: https://github.com/fredporter/uDOS
- **Contributing Guide**: See [CONTRIBUTING.md](wiki/Contributing)

---

**Thank you to everyone who made uDOS possible!** 🎉
