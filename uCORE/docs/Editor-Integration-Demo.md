# uDOS Editor Integration Demo

```ascii
    ███████╗██████╗ ██╗████████╗ ██████╗ ██████╗ ███████╗
    ██╔════╝██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
    █████╗  ██║  ██║██║   ██║   ██║   ██║██████╔╝███████╗
    ██╔══╝  ██║  ██║██║   ██║   ██║   ██║██╔══██╗╚════██║
    ███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║███████║
    ╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝

    Three Powerful Editors for uDOS v1.2
    ═════════════════════════════════════════════════════
```

## 🎯 Available Editors

### 📝 Micro Editor (Terminal-Based)
**Best for**: Quick edits, command-line workflow, uScript development

**Features**:
- Native terminal integration
- Syntax highlighting for Markdown and uScript
- uDOS shortcode recognition: `[COMMAND|ARGS]`
- Template variable highlighting: `{{VARIABLE}}`
- Instant startup, no dependencies

**Commands**:
```bash
[EDIT|MARKDOWN|filename.md]    # Edit markdown in micro
[EDIT|USCRIPT|script.us]       # Edit uScript in micro
[EDIT|CONFIG]                  # Configure micro
[NEW|MARKDOWN]                 # Create new markdown file
[NEW|USCRIPT]                  # Create new uScript file
```

### 🌐 Typo Web Editor (Browser-Based)
**Best for**: Rich markdown editing, live preview, visual workflow

**Features**:
- Modern web interface
- Live markdown preview
- File browser integration
- Export capabilities
- Responsive design for any screen size

**Commands**:
```bash
[TYPO|EDIT|filename.md]        # Edit in web browser
[TYPO|NEW|document]            # Create and edit new file
[TYPO|SERVER]                  # Start development server
```

**Access**: Open http://localhost:5173 in your browser

### 🎨 ASCII Art Generator
**Best for**: Creating visual elements, logos, banners

**Features**:
- Text to ASCII conversion
- Image to ASCII conversion
- Multiple font styles
- Integration with documentation

**Commands**:
```bash
[ASCII|TEXT|Hello World]       # Generate ASCII text
[ASCII|LOGO|uDOS]              # Generate system logo
[ASCII|BANNER|Title|Subtitle]  # Create banner
[ASCII|IMAGE|photo.jpg]        # Convert image to ASCII
```

## 🚀 Quick Start Examples

### Create a New Document
```bash
# Terminal editing with micro
NEW MARKDOWN my-document.md

# Web editing with Typo
TYPO NEW my-document.md
```

### Edit Existing Files
```bash
# Open in micro (terminal)
EDIT MARKDOWN docs/User-Manual.md

# Open in Typo (web browser)
TYPO EDIT docs/User-Manual.md
```

### Generate ASCII Art
```bash
# Create a logo
ASCII LOGO "My Project"

# Generate a banner
ASCII BANNER "Welcome" "to uDOS"

# Convert an image
ASCII IMAGE ~/Pictures/logo.png
```

## 🎛️ Mode Switching

uDOS supports seamless switching between editing modes:

```bash
MODE MARKDOWN    # Switch to markdown mode (micro integration)
MODE USCRIPT     # Switch to uScript mode (micro integration)  
MODE COMMAND     # Return to native uCODE command mode
```

## 🔧 Configuration

### Micro Editor Configuration
```bash
EDIT CONFIG      # Edit micro settings
```

### Typo Server Management
```bash
TYPO SERVER      # Start development server
# Then open http://localhost:5173 in browser
```

## 💡 Pro Tips

1. **Use micro for quick edits** - Perfect for command-line workflows
2. **Use Typo for rich editing** - Great for documentation with live preview
3. **Generate ASCII art first** - Create visual elements before writing
4. **Combine tools** - Create in micro, preview in Typo, enhance with ASCII

## 🌟 Integration Features

- **Shortcode Support**: All editors recognize `[COMMAND|ARGS]` syntax
- **Template Variables**: Support for `{{VARIABLE}}` replacement
- **uDOS Ecosystem**: Seamless integration with memory, missions, packages
- **Cross-Platform**: Works on macOS, Linux, and Windows (where supported)

---

*This document demonstrates the new editing capabilities in uDOS v1.2*  
*Generated on: {{DATE}}*  
*User: {{USER_NAME}}*
