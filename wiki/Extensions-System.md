# Extensions System

The uDOS Extensions System provides a clean separation between bundled native extensions and external dependencies, ensuring legal compliance and maintainable development.

## 📁 Directory Structure

```
extensions/
├── bundled/                    # uDOS-native extensions (git tracked)
│   └── web/                   # Web-based UI extensions
│       ├── dashboard/        # System dashboard interface
│       ├── font-editor/      # Web-based font editing tools
│       ├── shared/           # Shared CSS/JS libraries
│       ├── system-desktop/   # System 7 desktop environment
│       ├── system-style/     # OS styling frameworks
│       └── teletext/         # Broadcast TV interface
├── cloned/                    # External repositories (git ignored)
│   ├── micro/                # Modern terminal editor
│   ├── typo/                 # Web-based markdown editor
│   ├── monaspace-fonts/      # GitHub Next monospace fonts
│   ├── classicy-desktop/     # Mac OS 8 Platinum interface
│   ├── c64css3/              # Commodore 64 CSS framework
│   ├── nes-css/              # 8-bit Nintendo CSS framework
│   └── cmd/                  # Web terminal (optional)
├── fonts/                     # Font assets with licensing
└── setup/                     # Installation scripts
```

## 🚀 Quick Start

### Install External Dependencies
```bash
# Install all essential external tools
./extensions/setup/setup_all.sh

# Or install individually
./extensions/setup/setup_micro.sh       # Modern terminal editor
./extensions/setup/setup_typo.sh        # Web markdown editor
./extensions/setup/setup_classicy.sh    # Mac OS 8 interface
./extensions/setup/setup_c64css3.sh     # C64 styling framework
./extensions/setup/setup_nes.sh         # NES styling framework
```

### Use Bundled Extensions
```bash
# Launch web extensions
cd extensions/bundled/web/dashboard && python3 -m http.server 8080
cd extensions/bundled/web/system-desktop && python3 -m http.server 8082
cd extensions/bundled/web/teletext && python3 -m http.server 8081
```

## 🎨 Bundled Web Extensions

### Dashboard
- **Purpose**: Multi-theme system dashboard interface
- **Technology**: HTML5 + CSS3 + JavaScript
- **Features**: Real-time metrics, file browser integration
- **Status**: ✅ Tested & Working (Port 8080)

### System Desktop
- **Purpose**: System 7 desktop environment recreation
- **Technology**: Pure CSS3 + JavaScript
- **Features**: Classic Mac window management
- **Status**: ✅ Tested & Working (Port 8082)

### Teletext
- **Purpose**: Broadcast television teletext interface
- **Technology**: CSS + JavaScript with block characters
- **Features**: Mosaic mode, classic TV styling
- **Status**: ✅ Tested & Working (Port 8081)

### Shared Libraries
- **Purpose**: Common CSS/JS frameworks for all extensions
- **Components**: Typography system, UI components, grid system
- **Usage**: Foundation for all uDOS web interfaces

## 🛠️ External Dependencies

### Classicy Desktop
- **Repository**: https://github.com/robbiebyrd/classicy
- **Description**: Authentic Mac OS 8 Platinum interface
- **Features**: React-based, window management, classic styling

### C64 CSS3
- **Repository**: https://github.com/RoelN/c64css3
- **Description**: Commodore 64 styling framework
- **Features**: Pixel-perfect C64 colors, fonts, interface elements

### NES.css
- **Repository**: https://github.com/nostalgic-css/NES.css
- **Description**: 8-bit Nintendo Entertainment System CSS framework
- **Features**: Authentic NES styling, 8-bit fonts, pixel art support

### micro Editor
- **Repository**: https://github.com/zyedidia/micro
- **Description**: Modern terminal-based text editor
- **Features**: Syntax highlighting, plugin system, modern keybindings

### typo Editor
- **Repository**: https://github.com/rossrobino/typo
- **Description**: Minimalist web-based markdown editor
- **Features**: Real-time preview, clean interface, export options

## ⚖️ Legal Compliance

All bundled fonts are legally distributable:
- **ChicagoFLF**: Public domain
- **Chicago 12.1**: CC BY-SA 3.0
- **Mallard family**: CC BY-SA 3.0
- **sysfont**: SIL Open Font License 1.1

See `extensions/fonts/LICENSE_ASSESSMENT.md` for complete legal analysis.

## 🔧 Development Guidelines

### Adding Bundled Extensions
1. Create extension in `bundled/web/[extension-name]/`
2. Include README.md with description and usage
3. Add launch script if needed
4. Update main README with extension details
5. Commit to git repository

### Adding External Dependencies
1. Create setup script in `setup/setup_[name].sh`
2. Configure to clone into `cloned/[name]/`
3. Update `setup_all.sh` to include new dependency
4. Test installation process
5. Update documentation

## 📱 Platform Support

### Tested Platforms
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Arch)
- ✅ Windows (WSL2 recommended)

### Browser Compatibility
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

---

The uDOS Extensions system provides a clean separation between bundled content and external dependencies, ensuring legal compliance while maintaining development flexibility.
