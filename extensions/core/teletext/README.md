# Teletext Extension v1.0.26

Authentic Teletext broadcast interface recreation for uDOS (inspired by BBC Teletext), featuring Mallard fonts, Mode 7 graphics, standards compliance, and optional web GUI with REST API.

## 🎯 Status: Optional Extension

⚠️ **This extension is NOT required for CLI operation**

The Teletext web GUI is completely optional. uDOS CLI is fully functional without it. This extension adds browser-based access via REST API.

## Components

### 1. **Teletext Rendering** (Visual)
- Authentic Teletext display system (BBC standard)
- 40×25 character grid
- Mallard fonts, Mode 7 graphics
- 8-color palette

### 2. **API Server** (Web Interface)
- **File**: `api_server.py`
- **Purpose**: Flask REST API for web GUI
- **Endpoints**: 68 HTTP routes + WebSocket
- **Port**: 5001 (default)
- **Status**: Disabled by default

### 3. **API Server Manager** (Lifecycle)
- **File**: `api_server_manager.py`
- **Purpose**: Auto-start, health monitoring, restart
- **Status**: Only loads if API enabled

## 🚀 Quick Start (CLI Only)

No setup needed! uDOS CLI works out of the box without this extension.

## 🌐 Enabling Web GUI

### Method 1: User Settings
Edit `sandbox/user/profile.json`:
```json
{
  "settings": {
    "api_server_enabled": true
  }
}
```

### Method 2: CLI Command
```bash
uDOS> SETTINGS SET api_server_enabled true
uDOS> REBOOT
```

Once enabled:
```
🌐 Starting Web GUI API server... ✓ http://localhost:5001
```

## 🎯 Features

### **Authentic Teletext Rendering**
- **40×25 Character Grid**: Standard Teletext layout (BBC specification)
- **Mallard Fonts**: 6 variants for pixel-perfect rendering
- **Mode 7 Graphics**: Block characters and mosaic support
- **8-Color Palette**: Black, red, green, yellow, blue, magenta, cyan, white
- **Control Codes**: Colors, graphics, flash, double-height, hidden/revealed

### **BBC Standards Compliance**
- **Teletext Level 1**: Full specification support
- **Page System**: 100-899 page numbering
- **Character Set**: Authentic teletext character mapping
- **Block Graphics**: Sixel-style graphics blocks
- **Timing**: Authentic page load simulation

### **Synthwave DOS Enhancement** (Phase 3)
- **Synthwave DOS Integration**: Color palette harmonization
- **Improved Contrast**: Better readability on modern displays
- **Authentic Colors**: Maintains Teletext aesthetic (BBC standard)
- **Documentation**: See `README-POLAROID.md`

## 🚀 Quick Start

### Launch Server (v1.0.25 Unified Server)
```bash
# From teletext directory
./start.sh

# Or from extensions/core directory
./launch.sh teletext

# Or directly with Python
python3 extensions_server.py teletext
```

Opens at: `http://localhost:9002`

### Basic HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="teletext-enhanced.css">
</head>
<body class="teletext-screen">
    <div class="teletext-page">
        <div class="teletext-header">
            <span class="page-number">P100</span>
            <span class="service-name">CEEFAX</span>
            <span class="date-time">17 Nov 22:52</span>
        </div>
        <div class="teletext-content">
            <!-- 40×25 character grid content -->
        </div>
    </div>
    <script src="teletext-enhanced.js"></script>
</body>
</html>
```

### Color Control Codes
```html
<span class="color-red">RED TEXT</span>
<span class="color-green">GREEN TEXT</span>
<span class="color-yellow">YELLOW TEXT</span>
```

### Block Graphics
```html
<span class="graphics-mode">█▀▄▌▐░▒▓</span>
```

## 🎨 Font Variants

The Mallard font family provides 6 variants optimized for different rendering needs:

- **mallard-blocky**: Base version, standard rendering
- **mallard-blockier**: More angular, sharper edges
- **mallard-smooth**: Softened for better screen display
- **mallard-smoother**: Extra smoothing for modern displays
- **mallard-neueue**: Modern interpretation
- **mallard-tiny**: Compact variant for dense layouts

## 📺 Teletext Pages

### Page Numbering
- **100-199**: News and current affairs
- **200-299**: Features and entertainment
- **300-399**: Finance and business
- **400-499**: Sport
- **500-599**: Regional news
- **600-699**: Subtitles
- **700-799**: Miscellaneous
- **800-899**: Promotional

### Special Pages
- **888**: Subtitles index
- **100**: Main index page
- **199**: News headlines

## 🔧 API Reference

### JavaScript Interface

```javascript
// Initialize teletext system
TeletextViewer.init();

// Load a page
TeletextViewer.loadPage(100);

// Navigate pages
TeletextViewer.nextPage();
TeletextViewer.previousPage();

// Set service
TeletextViewer.setService('CEEFAX'); // or 'ORACLE'
```

### CSS Classes

- `.teletext-screen`: Main container
- `.teletext-page`: Page wrapper
- `.teletext-header`: Header bar with page number
- `.teletext-content`: 40×25 content grid
- `.color-red`, `.color-green`, etc.: Text colors
- `.graphics-mode`: Block graphics mode
- `.double-height`: Double-height text
- `.flash`: Flashing text
- `.hidden`: Hidden/revealed text

## 📁 Files

```
teletext/
├── index.html                  # Main teletext viewer
├── index-synthwave.html         # Synthwave DOS color variant
├── knowledge.html              # Knowledge page demo
├── teletext-enhanced.css       # Main stylesheet
├── teletext-web.css            # Legacy styles
├── teletext-enhanced.js        # Core JavaScript
├── teletext-shell.js           # Shell integration
├── api_server.py               # API backend (optional)
├── fonts/                      # Mallard fonts (symlink to /extensions/fonts/mallard/)
├── mosaic_codepoints_E200-E3FF.csv  # Character mappings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── README-POLAROID.md          # Synthwave DOS enhancement docs
└── CREDITS.md                  # Attribution
```

## 🎨 Synthwave DOS Colors (Synthwave DOS Palette)

The Synthwave DOS enhancement integrates Synthwave DOS colors while maintaining Teletext authenticity (BBC standard):

- **Background**: Deep black with slight warmth
- **Text**: Crisp white with subtle glow
- **Colors**: Adjusted for modern displays, authentic BBC palette
- **Contrast**: Enhanced readability

See `README-POLAROID.md` for technical details.

## 📚 Historical Context

### BBC CEEFAX (1974-2012)
- World's first teletext service
- News, weather, sports, TV listings
- Transmitted via TV vertical blanking interval
- Iconic UK broadcasting history

### Oracle (ITV, 1974-1992)
- Independent television teletext service
- Similar format to CEEFAX
- Commercial news and information

### Technical Specifications
- **Character Set**: 40 columns × 25 rows
- **Transmission**: 25 frames/second
- **Data Rate**: 7.2 kbit/s (2 × 3.6 kbit/s streams)
- **Pages**: Up to 800 pages per service
- **Graphics**: 2×3 sixel blocks

## 🔧 Development

### v1.0.24 Implementation
- **Phase 3** (Commit 9afaf4b): Synthwave DOS enhancement
- **Mallard Fonts**: 6 variants consolidated in `/extensions/fonts/mallard/`
- **Standards**: Full Teletext Level 1 compliance (BBC specification)
- **Integration**: uDOS knowledge system, API backend

### Future Enhancements
- Level 2 Teletext support (DRCS, additional control codes)
- FLOF (Fastext) navigation
- Subtitle timing and positioning
- Archive page playback

## 📖 References

- **Teletext Specification**: Level 1 (BBC, 1976)
- **Fonts**: Mallard family by gid (FontStruct.com), CC BY-SA 3.0
- **Colors**: Synthwave DOS palette integration
- **Historical**: CEEFAX and Oracle UK broadcast services

## 📄 License

See main uDOS LICENSE and CREDITS.md for font attribution.

---

**Version**: v1.0.24
**Phase 3**: Synthwave DOS Enhancement
**Commit**: 9afaf4b
**Font License**: Mallard family - CC BY-SA 3.0 (gid, FontStruct.com)
