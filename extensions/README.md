# uDOS Extensions System

## 📁 **Directory Structure**

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
├── templates/                 # Extension scaffolding templates
│   ├── cli-extension-template/   # CLI extension starter
│   └── web-extension-template/   # Web extension starter
├── fonts/                     # Font assets with licensing
│   ├── LICENSE_ASSESSMENT.md # Legal compliance documentation
│   ├── ChicagoFLF.ttf       # Classic Mac font (public domain)
│   ├── chicago-12-1/        # Chicago variant (CC BY-SA)
│   ├── mallard-*/           # Mallard font family (CC BY-SA)
│   └── sysfont/             # System font (OFL)
└── setup/                     # Installation scripts
    ├── setup_all.sh          # Master installer
    ├── setup_micro.sh        # Micro editor setup
    ├── setup_typo.sh         # Typo editor setup
    ├── setup_cmd.sh          # CMD terminal setup
    └── setup_monaspace.sh    # Monaspace fonts setup
```

## 🚀 **Quick Start**

### **Install External Dependencies**
```bash
# Install all essential external tools
./extensions/setup/setup_all.sh

# Or install individually
./extensions/setup/setup_micro.sh       # Modern terminal editor
./extensions/setup/setup_typo.sh        # Web markdown editor
./extensions/setup/setup_classicy.sh    # Mac OS 8 interface
./extensions/setup/setup_c64css3.sh     # C64 styling framework
./extensions/setup/setup_nes.sh         # NES styling framework
./extensions/setup/setup_cmd.sh         # Web terminal (optional)
```

### **Use Bundled Extensions**
All bundled extensions are immediately available:
- Launch web extensions via uDOS dashboard
- Access styling frameworks in web development
- Use shared libraries across projects

## 🎨 **Bundled Web Extensions**

### **Dashboard**
- **Description**: Multi-theme system dashboard interface
- **Technology**: HTML5 + CSS3 + JavaScript
- **Features**: Real-time metrics, file browser integration, customizable widgets
- **Usage**: Core uDOS system interface

### **System Desktop**
- **Description**: System 7 desktop environment recreation
- **Technology**: Pure CSS3 + JavaScript
- **Features**: Authentic Mac window management, classic styling
- **Integration**: Direct uDOS command integration

### **Shared Libraries**
- **Description**: Common CSS/JS frameworks for all extensions
- **Technology**: Modular CSS + JavaScript utilities
- **Features**: Typography system, UI components, grid system
- **Usage**: Foundation for all uDOS web interfaces

### **Teletext Interface**
- **Description**: Broadcast television teletext recreation
- **Technology**: CSS + JavaScript with block character support
- **Features**: Mosaic mode, classic TV styling, authentic rendering
- **Usage**: Retro information display system

## 🛠️ **External Dependencies**

### **Classicy Desktop**
- **Repository**: https://github.com/robbiebyrd/classicy
- **Description**: Authentic Mac OS 8 Platinum interface recreation
- **Features**: React-based, window management, classic Mac styling
- **Installation**: Automatic clone and npm build

### **C64 CSS3**
- **Repository**: https://github.com/RoelN/c64css3
- **Description**: Commodore 64 styling framework
- **Features**: Pixel-perfect C64 colors, fonts, and interface elements
- **Usage**: Import CSS framework in retro projects

### **NES.css**
- **Repository**: https://github.com/nostalgic-css/NES.css
- **Description**: 8-bit Nintendo Entertainment System CSS framework
- **Features**: Authentic NES styling, 8-bit fonts, pixel art support
- **Usage**: Retro gaming interfaces and 8-bit themed projects

### **micro Editor**
- **Repository**: https://github.com/zyedidia/micro
- **Description**: Modern terminal-based text editor
- **Features**: Syntax highlighting, plugin system, modern keybindings
- **Installation**: Automatic binary download or source build

### **typo Editor**
- **Repository**: https://github.com/rossrobino/typo
- **Description**: Minimalist web-based markdown editor
- **Features**: Real-time preview, clean interface, export options
- **Usage**: Web-based editing within uDOS interface

### **CMD Terminal** (Optional)
- **Repository**: https://github.com/mrchimp/cmd
- **Description**: Web-based terminal emulator
- **Features**: Command history, extensible command system
- **Note**: Optional component for web terminal needs

### **Monaspace Fonts**
- **Repository**: https://github.com/githubnext/monaspace
- **Description**: GitHub Next's coding font family
- **Features**: Texture healing, multiple weights, coding ligatures
- **Usage**: Enhanced typography for code editing

## 🔧 **Development Guidelines**

### **Adding Bundled Extensions**
1. Create extension in `bundled/web/[extension-name]/`
2. Include README.md with description and usage
3. Add launch script if needed
4. Update this README with extension details
5. Commit to git repository

### **Adding External Dependencies**
1. Create setup script in `setup/setup_[name].sh`
2. Configure to clone into `cloned/[name]/`
3. Update `setup_all.sh` to include new dependency
4. Test installation process
5. Update documentation

### **Creating New Extensions**

Use the templates in `templates/` to scaffold new extensions:

#### **CLI Extension**
```bash
# Copy template
cp -r extensions/templates/cli-extension-template extensions/my-cli-tool

# Follow instructions in template README
cd extensions/my-cli-tool
```

#### **Web Extension**
```bash
# Copy template
cp -r extensions/templates/web-extension-template extensions/bundled/web/my-extension

# Follow instructions in template README
cd extensions/bundled/web/my-extension
```

See `templates/README.md` for complete scaffolding documentation.

### **Font Management**
1. Add fonts to `fonts/` directory
2. Include license files for each font
3. Update `LICENSE_ASSESSMENT.md` with legal status
4. Reference in typography system CSS
5. Test cross-platform compatibility

## ⚖️ **Legal Compliance**

All bundled fonts are legally distributable:
- **ChicagoFLF**: Public domain
- **Chicago 12.1**: CC BY-SA 3.0
- **Mallard family**: CC BY-SA 3.0
- **sysfont**: SIL Open Font License 1.1

See `fonts/LICENSE_ASSESSMENT.md` for complete legal analysis.

## 🎯 **Platform Support**

### **Tested Platforms**
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Arch)
- ✅ Windows (WSL2 recommended)

### **Browser Compatibility**
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 📚 **Additional Resources**

- **Extension Templates**: `extensions/templates/` - CLI & Web extension scaffolding
- **Example Demos**: `knowledge/demos/` - Working examples and scripts
- **uDOS Wiki**: Complete extension development guides
- **Font Documentation**: Typography system usage
- **API Reference**: Extension integration patterns
- **Community**: GitHub discussions and issues

---

**🎉 The uDOS Extensions system provides a clean separation between bundled content, external dependencies, and templates - ensuring legal compliance while maintaining development flexibility.**
