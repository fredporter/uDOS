# uDOS Core Dashboard

A retro-futuristic web dashboard that combines the nostalgic aesthetics of NES.css, Teletext, and classic interfaces with modern web technologies.

## 🎮 Features

### **Multi-Framework Integration**
- **NES.css**: Authentic 8-bit NES styling with pixel-perfect fonts and color schemes
- **Teletext Framework**: BBC Teletext-inspired data presentation with mosaic graphics
- **Typography System**: Classic computer fonts with themed configurations
- **Responsive Design**: Adapts from desktop to mobile while maintaining retro authenticity

### **Real-Time Monitoring**
- System performance metrics (CPU, Memory, Disk)
- Network activity tracking
- Process monitoring
- Live system logs
- uDOS command execution

### **Interactive Modules**
1. **System Monitor** - Real-time CPU, memory, and disk usage tracking
2. **Process Manager** - Active process monitoring and management
3. **Network Analyzer** - Upload/download speeds, connections
4. **File Browser** - Integrated file system navigation
5. **Terminal Emulator** - Retro-style command line interface
6. **Command Center** - Execute uDOS commands directly
7. **Knowledge Browser** - Access uDOS knowledge bank
8. **Configuration Panel** - Manage uDOS settings

### **Visual Effects**
- Authentic NES-style pixel graphics
- Animated data streams
- Pixel-perfect retro fonts
- Smooth transitions with period-appropriate styling

## 🚀 Installation

The dashboard is included in uDOS core extensions. No additional installation needed.

1. **Verify File Structure**:
   ```
   extensions/core/dashboard/
   ├── index.html              # Main dashboard interface
   ├── dashboard-api.js        # Core API and module system
   ├── dashboard-builder.js    # Dashboard builder interface
   ├── dashboard-styles.css    # Core styling
   ├── config.json            # Configuration settings
   ├── manifest.json          # Extension manifest
   ├── app.py                 # Python Flask backend
   ├── start.sh               # Startup script
   ├── static/                # Static assets
   ├── routes/                # API routes
   ├── server/                # Server components
   ├── services/              # Backend services
   └── fonts/                 # Retro fonts
   ```

2. **Launch Dashboard**:

   **From uDOS CLI:**
   ```bash
   DASH WEB
   # or
   OUTPUT START dashboard
   ```

   **Manual Start:**
   ```bash
   cd /Users/fredbook/Code/uDOS/extensions/core/dashboard
   ./start.sh
   # Then open: http://localhost:5555
   ```

## 🎨 Retro Themes

### **Theme Support**
- **NES Classic** - Authentic 8-bit NES aesthetic with pixel fonts
- **Teletext** - BBC Teletext-inspired data visualization
- **uDOS Foundation** - Classic uDOS green-on-dark theme
- **Galaxy** - Space-themed dark interface
- **Science** - Technical/scientific aesthetic

### **Theme Features**
- **Seamless Switching** - Cycle through themes with the Theme button
- **Authentic Typography** - Period-accurate fonts for each theme
- **Interactive Elements** - Theme-specific buttons and UI controls

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Cycle themes |
| `F1` | Help |
| `F5` | Refresh data |
| `Ctrl+K` | Command palette |

## 🖥️ Modules

### **System Monitor**
Real-time system performance with animated progress bars and live metrics.

### **Command Center**
Execute uDOS commands directly from the dashboard:
- Command history
- Syntax highlighting
- Real-time output
- Integration with uDOS core

### **Knowledge Browser**
Access the uDOS knowledge bank:
- Browse categories (water, fire, shelter, food, navigation, medical)
- Search knowledge base
- View guides with proper formatting
- Quick reference cards

### **Terminal Emulator**
Retro-style command-line interface:
- Full uDOS command support
- Command history
- Autocomplete
- Color-coded output

## 🔧 Configuration

Edit `config.json` to customize:

### **Server Settings**
```json
{
  "server": {
    "port": 5555,
    "host": "localhost"
  },
  "themes": {
    "default": "nes-classic"
  }
}
```

### **Module Configuration**
```json
{
  "modules": {
    "system-monitor": {
      "enabled": true,
      "refresh_rate": 1000
    },
    "knowledge-browser": {
      "enabled": true,
      "categories": ["water", "fire", "shelter", "food", "navigation", "medical"]
    }
  }
}
```
## 🌐 API Reference

### **Dashboard API**
```javascript
// Initialize dashboard
await DashboardAPI.init();

// Execute uDOS command
const result = await DashboardAPI.executeCommand('HELP');

// Get system metrics
const metrics = await DashboardAPI.getSystemMetrics();

// Browse knowledge
const guides = await DashboardAPI.getKnowledgeCategory('water');
```

### **Backend API Endpoints**
```
GET  /api/system/metrics      - Get system performance data
POST /api/command/execute     - Execute uDOS command
GET  /api/knowledge/categories - List knowledge categories
GET  /api/knowledge/:category  - Get guides in category
GET  /api/config               - Get current configuration
POST /api/config               - Update configuration
```

## 🎵 Retro Authenticity

### **Visual Effects**
- Authentic NES-style pixel graphics
- 8-bit color palettes from period hardware
- Pixel-perfect bitmap fonts
- Classic UI elements (windows, buttons, dialogs)

## 🔌 Integration with uDOS

The dashboard integrates seamlessly with uDOS core:

### **Command Integration**
- Execute any uDOS command from dashboard
- Real-time command output streaming
- Command history and autocomplete
- Full access to uDOS functionality

### **Data Sources**
- Live system metrics from uDOS core
- Knowledge bank integration (6 categories, 136+ guides)
- Configuration management
- File system access
- Process monitoring via uDOS services

### **Server Management**
Start/stop from uDOS:
```bash
# Start dashboard server
OUTPUT START dashboard
DASH WEB

# Stop dashboard server
OUTPUT STOP dashboard

# Check server status
STATUS
## 🎯 Future Enhancements

### **Planned Features**
- Mobile app companion (PWA)
- Real-time collaboration features
- Plugin system for custom modules
- Enhanced knowledge browser with search
# Check server status
STATUS
```

## 🎯 Future Enhancements

### **Planned Features**
- Mobile app companion (PWA)
- Real-time collaboration features
- Plugin system for custom modules
- Enhanced knowledge browser with search
- Command builder interface
Part of the uDOS project. Integrates:
- NES.css (by B.C.Rikko - MIT License)
- MODE7 fonts (Various licenses)
- Custom uDOS components (uDOS License)

## 🤝 Contributing

1. Fork the uDOS repository
2. Create feature branch: `git checkout -b feature/dashboard-enhancement`
3. Make changes to `extensions/core/dashboard/`
4. Test with multiple browsers and screen sizes
5. Submit pull request with detailed description

## 🐛 Troubleshooting
**Commands not executing**: Verify uDOS core is accessible and Python backend is running

**Fonts not loading**: Check that font files exist in `fonts/` directory

**Layout broken**: Check browser compatibility (Chrome 80+, Firefox 75+, Safari 13+)

### **Debug Mode**
Set in `config.json`:
```json
{
  "debug": true,
  "logging": {
    "level": "DEBUG",
    "console": true
  }
}
```

### **Server Logs**
Check logs in:
- `sandbox/logs/dashboard-server.log`
- Browser console (F12)
- Terminal output when running `./start.sh`

---

**Made with 💚 for the uDOS community**

*A retro dashboard for offline-first survival computing*
