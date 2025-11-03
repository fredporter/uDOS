# uDOS Bundled Web Extensions

**Native uDOS web-based extensions providing retro computing interfaces and tools.**

## 🎯 **Current Extensions**

### 📊 **Dashboard**
- **Purpose**: Multi-theme system dashboard interface
- **Technology**: HTML5 + CSS3 + JavaScript
- **Features**: Real-time metrics, file browser integration, customizable widgets
- **Status**: ✅ **Tested & Working** (Port 8080)
- **Launch**: `python3 -m http.server 8080`

### 🖥️ **System Desktop** 
- **Purpose**: System 7 desktop environment recreation
- **Technology**: Pure CSS3 + JavaScript with authentic Mac styling
- **Features**: Classic Mac window management, System 7 interface
- **Status**: ✅ **Tested & Working** (Port 8082)
- **Launch**: `python3 -m http.server 8082`

### 📺 **Teletext**
- **Purpose**: Broadcast television teletext interface recreation
- **Technology**: CSS + JavaScript with block character support
- **Features**: Mosaic mode, classic TV styling, authentic rendering
- **Status**: ✅ **Tested & Working** (Port 8081)
- **Launch**: `python3 -m http.server 8081`

### 🎨 **Shared Libraries**
- **Purpose**: Common CSS/JS frameworks for all extensions
- **Technology**: Modular CSS + JavaScript utilities
- **Components**: Typography system, UI components, grid system
- **Usage**: Foundation for all uDOS web interfaces

### 🔧 **Font Editor**
- **Purpose**: Web-based font editing tools
- **Technology**: HTML5 Canvas + JavaScript
- **Features**: Bitmap and vector font editing
- **Integration**: Typography system integration

### 🎨 **System Style**
- **Purpose**: OS styling frameworks for different themes
- **Technology**: CSS frameworks for Mac OS, Windows, Unix interfaces
- **Features**: Responsive design patterns, authentic recreations

## 🚀 **Quick Start**

### **Launch All Extensions**
```bash
# From extensions/bundled/web/ directory
./launch.sh
```

### **Individual Extension Testing**
```bash
# Dashboard
cd dashboard && python3 -m http.server 8080

# System Desktop  
cd system-desktop && python3 -m http.server 8082

# Teletext
cd teletext && python3 -m http.server 8081
```

### **Access Extensions**
- **Dashboard**: http://localhost:8080
- **System Desktop**: http://localhost:8082  
- **Teletext**: http://localhost:8081

## 🛠️ **Development**

### **Extension Structure**
```
extension-name/
├── index.html          # Main interface
├── README.md          # Extension documentation
├── *.css             # Styling
├── *.js              # Functionality
└── assets/           # Images, fonts, resources
```

### **Adding New Extensions**
1. Create directory in `/bundled/web/[extension-name]/`
2. Follow standard structure with index.html
3. Include README.md with features and usage
4. Test with local HTTP server
5. Update this main README

### **Integration with uDOS**
- Extensions can access uDOS commands via JavaScript API
- Shared styling from `/shared/` directory
- Typography system for consistent fonts
- CSS grid system for responsive layouts

## 📋 **Extension Status**

| Extension | Status | Port | Features |
|-----------|--------|------|----------|
| Dashboard | ✅ Working | 8080 | Multi-theme, widgets, metrics |
| System Desktop | ✅ Working | 8082 | Mac System 7, windows |  
| Teletext | ✅ Working | 8081 | BBC teletext, mosaic |
| Shared | ✅ Active | N/A | Typography, components |
| Font Editor | 🔧 Development | TBD | Font editing tools |
| System Style | 🔧 Development | TBD | OS theme frameworks |

## 🎨 **Styling Guidelines**

### **Typography**
- Use fonts from `/shared/typography-system.css`
- Chicago, Geneva, Monaco for Mac themes
- VT323, Monaco for terminal themes
- Consistent font sizing and spacing

### **Colors**
- System 7: Grays, whites, classic Mac palette
- C64: Blues, light blues, authentic C64 colors
- Teletext: Primary colors, high contrast
- Terminal: Green on black, amber variants

### **Responsive Design**
- Mobile-first approach
- Use shared grid system from `/shared/`
- Test on multiple screen sizes
- Graceful degradation for older browsers

---

**✅ All extensions tested and working as of latest commit**  
**🔧 Ready for integration with external cloned dependencies**  
**📱 Responsive and cross-browser compatible**