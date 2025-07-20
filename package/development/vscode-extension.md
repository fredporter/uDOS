# uDOS VS Code Extension Package

## 📦 Extension Installation Package

This package provides the uDOS VS Code extension for optimal development experience.

### Features

- **uScript Language Support**: Full syntax highlighting and IntelliSense
- **uDOS Commands**: Integrated command palette with all uDOS operations
- **Template System**: Quick insertion and generation of uDOS templates
- **User Role Integration**: Respects wizard/sorcerer/ghost/imp permissions
- **Chester OK**: Integrated OK companion for assistance
- **Markdown-Native**: Enhanced markdown editing for uDOS documents

### Installation

#### Automatic (Recommended)
```bash
# During uDOS installation
./install-udos.sh
# Extension is installed automatically if VS Code is detected
```

#### Manual Installation
```bash
# Using installation script
./extension/install-extension.sh

# Or using VS Code CLI
code --install-extension ./extension/udos-extension-1.0.0.vsix
```

### Commands Available

- `uDOS: Start uDOS` - Launch uDOS shell
- `uDOS: Create Mission` - Generate new mission from template
- `uDOS: Create Move` - Generate new move from template
- `uDOS: Check Setup` - Run system validation
- `uDOS: Generate Dashboard` - Create project dashboard
- `uDOS: User Role Switch` - Change user role context
- `uDOS: Chester Help` - Get AI assistance
- `uDOS: Template Gallery` - Browse available templates

### File Associations

- `.md` - Enhanced markdown editing with uDOS features
- `.us`, `.uscript` - uScript files with full language support
- `mission-*.md` - Mission templates and instances
- `move-*.md` - Move templates and instances

### Configuration

Extension automatically detects uDOS installation and configures:

- ✅ User role from current session
- ✅ Template paths from uTemplate/
- ✅ Script paths from uScript/
- ✅ Chester AI integration
- ✅ Custom themes and snippets

### Troubleshooting

**Extension not loading?**
```bash
### Installation Options

#### Option 1: Direct Command (Recommended)
```bash
# From uDOS root directory
./extension/install-extension.sh --force
```

#### Option 2: Via VS Code Task
Use the "🔌 Install uDOS VS Code Extension" task in VS Code.
```

**Commands not working?**
```bash
# Check uDOS installation
./uCode/check.sh all
```

**Wrong user role?**
```bash
# Refresh user session
./uCode/ucode.sh refresh-session
```

### Development

For extension development, see `docs/extension-development.md`

---

**Version**: 1.2.0  
**Compatibility**: uDOS v1.2+, VS Code 1.80+  
**License**: MIT
