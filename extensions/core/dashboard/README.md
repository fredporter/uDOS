# uDOS Advanced Dashboard

A retro-futuristic web dashboard that combines the nostalgic aesthetics of Commodore 64, BBC Teletext, and classic Mac interfaces with modern web technologies.

## 🎮 Features

### **Multi-Framework Integration**
- **C64 CSS3**: Authentic Commodore 64 styling with pixel-perfect fonts and color schemes
- **Teletext Framework**: BBC Teletext-inspired data presentation with mosaic graphics
- **Typography System**: 15+ classic computer fonts with 8 themed configurations
- **Responsive Design**: Adapts from desktop to mobile while maintaining retro authenticity

### **Real-Time Monitoring**
- System performance metrics (CPU, Memory, Disk)
- Network activity tracking
- Process monitoring
- Live system logs
- Temperature and load monitoring

### **Interactive Modules** (8 Core Modules)
1. **System Monitor** - Real-time CPU, memory, and disk usage tracking
2. **Process Manager** - Active process monitoring and management
3. **Network Analyzer** - Upload/download speeds, connections, packet analysis
4. **File Browser** - Integrated file system navigation and management
5. **Terminal Emulator** - C64-style command line interface with authentic commands
6. **C64 Simulator** - Authentic Commodore 64 BASIC command processing
7. **Teletext Decoder** - BBC Teletext page decoding and data stream visualization
8. **System7 Interface** - Classic Macintosh window management and file operations

### **Visual Effects**
- Authentic CRT scanlines and glow effects
- Animated data streams
- Rainbow color cycling
- Pixel-perfect retro fonts
- Smooth transitions with period-appropriate styling

## 🚀 Installation

1. **Clone C64 CSS3 Framework** (already done):
   ```bash
   cd /Users/fredbook/Code/uDOS/extensions/web
   git clone https://github.com/RoelN/c64css3.git
   ```

2. **Verify File Structure**:
   ```
   extensions/web/advanced-dashboard/
   ├── index.html              # Main dashboard interface
   ├── dashboard-api.js        # Core API and module system
   ├── config.json            # Configuration settings
   └── README.md              # This file

   extensions/web/c64css3/     # C64 CSS3 framework
   ├── css.css                # C64 styling
   ├── C64_User_Mono_v1.0-STYLE.*  # C64 fonts
   └── giana.*                # Additional C64 fonts

   extensions/web/teletext/    # Teletext framework
   ├── teletext-enhanced.css   # Teletext styling
   ├── teletext-api.js        # Teletext API
   └── fonts/MODE7GX3.TTF     # Teletext font

   extensions/web/system7-css/ # System 7 framework
   ├── system7.css            # Classic Mac styling
   ├── system7.js             # Window management system
   ├── index.html             # Demo page
   └── README.md              # Framework documentation
   ```

3. **Launch Dashboard**:
   ```bash
   cd /Users/fredbook/Code/uDOS/extensions/web
   python3 -m http.server 8080
   # Then open: http://localhost:8080/advanced-dashboard/
   ```

## 🎨 Multiple Retro Themes

### **Theme Support**
- **Retro Classic** - Classic uDOS green-on-dark aesthetic
- **Commodore 64** - Authentic C64 blue color scheme with pixel fonts
- **Teletext** - BBC Teletext-inspired data visualization with MODE7 fonts
- **System 7** - Classic Macintosh interface with authentic window chrome and Geneva/Chicago fonts
- **Modern Dark** - Contemporary dark theme for modern sensibilities

### **Theme Features**
- **Seamless Switching** - Cycle through themes with the Theme button or Ctrl+T
- **Framework Integration** - Each theme integrates with corresponding CSS frameworks
- **Authentic Typography** - Period-accurate fonts and styling for each theme
- **Interactive Elements** - Theme-specific buttons, windows, and UI controls

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Cycle themes |
| `Alt+1` | System Monitor |
| `Alt+2` | Process Manager |
| `Alt+3` | Network Analyzer |
| `Alt+4` | Terminal |
| `Alt+5` | C64 Simulator |
| `Alt+6` | Teletext Decoder |
| `Alt+7` | System 7 Interface |
| `Alt+8` | File Browser |
| `Alt+9` | Performance Tracker |
| `F1` | Help |

## 🖥️ Modules

### **System Monitor**
Real-time system performance with animated progress bars and live metrics.

### **C64 Simulator**
Working Commodore 64 BASIC interpreter supporting:
- `LIST` - Show program listing
- `RUN` - Execute program
- `LOAD` - Load programs
- `CATALOG` - Show directory
- `SYS 64738` - Memory info
- `HELP` - Command reference

### **Teletext Decoder**
Multi-page information system:
- Page 100: Main menu
- Page 101: System status
- Page 102: News & updates
- Page 200: Weather data
- Page 300: Sports results

### **Terminal Emulator**
Command-line interface with:
- Retro styling
- Command history
- Syntax highlighting
- Integration with uDOS commands

## 🔧 Configuration

Edit `config.json` to customize:

### **Framework Settings**
```json
{
  "frameworks": {
    "c64css3": { "enabled": true },
    "teletext": { "enabled": true },
    "typography": { "enabled": true }
  }
}
```

### **Module Configuration**
```json
{
  "modules": {
    "system-monitor": {
      "enabled": true,
      "hotkey": "Alt+1"
    }
  }
}
```

### **Theme Customization**
```json
{
  "themes": {
    "custom": {
      "colors": {
        "primary": "#custom-color",
        "secondary": "#another-color"
      }
    }
  }
}
```

## 🌐 API Reference

### **Dashboard API**
```javascript
// Initialize dashboard
await DashboardAPI.init();

// Load module
const module = await DashboardAPI.loadModule('system-monitor');

// Change theme
DashboardAPI.applyTheme('c64');

// Get system metrics
const metrics = DashboardAPI.modules.get('system-monitor').api.getCPUUsage();
```

### **Module Development**
```javascript
// Create custom module
const customModule = {
  name: 'my-module',
  api: {
    customFunction: () => 'Hello from custom module!'
  }
};

DashboardAPI.modules.set('my-module', customModule);
```

## 📱 Responsive Design

The dashboard automatically adapts to different screen sizes:

- **Desktop** (1200px+): Full 3-column layout with all panels
- **Tablet** (768-1200px): 2-column layout, right panel hidden
- **Mobile** (<768px): Single column, sidebar becomes overlay

## 🎵 Retro Authenticity

### **Visual Effects**
- CRT scanlines with configurable intensity
- Phosphor glow on text elements
- Authentic color palettes from period hardware
- Pixel-perfect bitmap fonts

### **Sound Effects** (Future Enhancement)
- C64 SID chip sound emulation
- Teletext page loading sounds
- Terminal beep sounds
- Authentic system startup sounds

## 🔌 Integration with uDOS

The dashboard integrates with the main uDOS system:

### **Command Integration**
- Execute uDOS commands from dashboard
- Real-time system data from uDOS core
- File system access through uDOS API
- Process monitoring via uDOS services

### **Data Sources**
- Live system metrics
- Process information
- Network statistics
- Log file monitoring
- Configuration management

## 🚀 Performance

### **Optimization Features**
- Lazy loading of modules
- Efficient data streaming
- Minimal DOM manipulation
- CSS animations over JavaScript
- Debounced update cycles

### **Browser Compatibility**
- Modern browsers (Chrome 80+, Firefox 75+, Safari 13+)
- ES6+ features required
- WebGL for advanced effects (optional)
- Local storage for preferences

## 🎯 Future Enhancements

### **v1.1 Planned Features**
- Sound effects and audio feedback
- More teletext pages and data sources
- Advanced C64 program support
- Plugin system for custom modules
- WebSocket real-time updates
- Mobile app companion

### **v1.2 Vision**
- VR/AR retro computer environment
- Multiplayer teletext chat
- Demo scene integration
- Hardware controller support
- Time-period accurate animations

## 📄 License

Part of the uDOS project. Integrates:
- C64 CSS3 by Roel Nieskens (MIT License)
- MODE7 fonts (Various licenses)
- Custom uDOS components (uDOS License)

## 🤝 Contributing

1. Fork the uDOS repository
2. Create feature branch: `git checkout -b feature/dashboard-enhancement`
3. Make changes to `extensions/web/advanced-dashboard/`
4. Test with multiple browsers and screen sizes
5. Submit pull request with detailed description

## 🐛 Troubleshooting

### **Common Issues**

**Fonts not loading**: Check that font files exist in `../c64css3/` and `../teletext/fonts/`

**Modules not working**: Verify `dashboard-api.js` is loaded and no console errors

**Layout broken**: Check browser compatibility and screen resolution

**Performance issues**: Disable animations in config.json, reduce update frequency

### **Debug Mode**
Add `?debug=true` to URL for:
- Console logging
- Performance metrics
- Module status display
- API call tracing

---

**Made with 💚 for the retro computing community**

*Experience the future as imagined by the past*
