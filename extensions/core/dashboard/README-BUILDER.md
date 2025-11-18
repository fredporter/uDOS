# uDOS Dashboard Builder v1.0.25

**NES-Style Customizable Dashboard System**

## Overview

A fully customizable, retro-styled dashboard builder using NES.css framework and Synthwave DOS color palette. Features drag-and-drop widget management, multiple themes, and persistent layouts.

## Features

### 🎮 Widget System
- **12+ Pre-built Widgets**: System Monitor, Quick Actions, Extensions, Activity Feed, Stats, Knowledge Library, Clock, Weather, Tasks, Notes, Terminal, Music Player
- **Drag & Drop**: Rearrange widgets in edit mode
- **Add/Remove**: Customize your dashboard layout
- **Category Organization**: System, Navigation, Info, Productivity, Tools, Entertainment

### 🎨 Themes
1. **Synthwave DOS** - Cyan/magenta cyberpunk aesthetic
2. **Classic NES** - Red/yellow Nintendo vibes
3. **Game Boy** - Green monochrome nostalgia
4. **Commodore 64** - Purple/blue retro computing

### 📐 Layout Options
- **1-4 Column Grids**: Responsive layout system
- **Auto-save**: Layouts saved to localStorage
- **Import/Export**: Share dashboard configurations
- **Reset**: Return to default layout anytime

### 🔧 Customization
- **Edit Mode**: Toggle widget controls
- **Widget Picker**: Browse and add new widgets
- **Settings Panel**: Configure theme, layout, and data
- **Persistent State**: Your preferences saved automatically

## Getting Started

### Launch Server (v1.0.25 Unified Server)
```bash
# From dashboard directory
./start.sh

# Or from extensions/core directory
./launch.sh dashboard

# Or directly with Python
python3 extensions_server.py dashboard
```

Opens at: `http://localhost:8888`

### Quick Actions
1. Click **"Edit Layout"** to enter edit mode
2. Click **"Add Widget"** to browse available widgets
3. Click **"Settings"** to change theme or layout
4. Widgets auto-save as you customize

## Widget Types

### System Widgets

#### System Monitor
- CPU, Memory, Disk usage
- Real-time progress bars
- Uptime tracking
- NES.css progress components

#### Extensions
- Active extension status
- Quick extension info
- Status badges
- Enable/disable tracking

### Navigation Widgets

#### Quick Actions
- 6 Quick-launch buttons
- Terminal, Knowledge, Files, Teletext, Editor, Settings
- Direct extension launching
- Grid layout

#### Knowledge Library
- Document statistics
- Category browser
- Recently viewed files
- Quick access button

### Info Widgets

#### Recent Activity
- Timeline of recent actions
- Commit history
- File modifications
- System events

#### Progress Stats
- Development progress
- XP and level system
- Pixel hearts health display
- Commit tracking

#### Digital Clock
- Real-time clock display
- Date information
- Large retro digits
- Auto-updating

#### Weather
- Current conditions (placeholder)
- Temperature display
- Location info
- Icon representation

### Productivity Widgets

#### Task List
- Checkbox todo items
- Add new tasks
- Task management
- NES.css checkboxes

#### Quick Notes
- Text area for notes
- Save functionality
- Persistent storage
- Quick access

### Tool Widgets

#### Mini Terminal
- Embedded terminal interface
- Command execution
- Output display
- Input field

#### Music Player
- Chiptune player (placeholder)
- Playback controls
- Progress bar
- Track info

## API Reference

### DashboardBuilder Class

```javascript
// Initialize
const builder = new DashboardBuilder();

// Toggle edit mode
builder.toggleEditMode();

// Open widget picker
builder.openWidgetPicker();

// Add widget
builder.addWidget('clock');

// Remove widget
builder.removeWidget('widget-id');

// Move widget
builder.moveWidget('widget-id', 'up');

// Change columns
builder.changeColumns(3);

// Apply theme
builder.applyTheme('synthwave');

// Open extension
builder.openExtension('terminal');

// Save/Load layout
builder.saveLayout();
builder.loadLayout();

// Export/Import
builder.exportLayout();
builder.importLayout();

// Reset
builder.resetLayout();
```

### Widget Template Structure

```javascript
{
    'widget-type': {
        name: 'Widget Name',
        icon: '🎮',
        description: 'Widget description',
        category: 'system|navigation|info|productivity|tools|entertainment',
        render: (config) => HTMLElement
    }
}
```

## File Structure

```
dashboard/
├── index.html                  # Main dashboard HTML
├── index-old.html              # Legacy dashboard (backup)
├── index-builder.html          # Reference NES template
├── dashboard-builder.js        # Core builder logic
├── dashboard-styles.css        # NES-styled CSS
├── dashboard-api.js            # API client (legacy)
├── app.py                      # Python backend
├── launch.sh                   # Launch script
├── README.md                   # This file
└── static/
    └── css/
        └── file_browser.css    # Legacy styles
```

## Customization

### Creating Custom Widgets

Add to `widgetTemplates` in `dashboard-builder.js`:

```javascript
'my-widget': {
    name: 'My Custom Widget',
    icon: '🎯',
    description: 'Does something cool',
    category: 'productivity',
    render: (config) => {
        const template = this.widgetTemplates[config.type];
        const { widget, body } = this.createWidget(config, template);

        body.innerHTML = `
            <div class="custom-content">
                <!-- Your widget content -->
            </div>
        `;

        return widget;
    }
}
```

### Adding Themes

Add to `getThemes()` in `dashboard-builder.js`:

```javascript
'my-theme': {
    name: 'My Theme',
    primary: '#ff0000',
    secondary: '#00ff00',
    background: 'linear-gradient(135deg, #000 0%, #fff 100%)'
}
```

## Extension Integration

### Launching Extensions

```javascript
dashboardBuilder.openExtension('extension-name');
```

**Available Extensions:**
- `terminal` - Port 8889
- `markdown` - Port 9000
- `files` - Port 8000
- `teletext` - Port 9002
- `character` - Port 8891
- `settings` - Port 8888

### Adding Extension Buttons

Modify `renderQuickActions()` widget:

```javascript
const actions = [
    { name: 'My Extension', icon: '🎯', action: 'my-extension' }
];
```

Then add port mapping in `openExtension()`:

```javascript
const ports = {
    'my-extension': 9999
};
```

## Storage

### LocalStorage Keys
- `dashboard-layout` - Widget configuration
- `dashboard-theme` - Active theme name

### Layout Format
```json
{
    "columns": 3,
    "widgets": [
        {
            "id": "system-monitor",
            "type": "system-monitor",
            "position": 0,
            "enabled": true
        }
    ]
}
```

## Keyboard Shortcuts

- **F12** - Open browser DevTools
- **Ctrl/Cmd + S** - Export layout (when focused on export button)
- **Esc** - Close modals (browser default)

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive)

## Performance

- **Lightweight**: ~150KB total assets (excluding NES.css CDN)
- **Fast Loading**: < 1s initial load
- **Auto-updates**: 3s system metrics, 1s clock
- **Lazy Rendering**: Widgets created on-demand

## Development

### Testing
```bash
# Local server
python3 -m http.server 8888

# With Python backend
python app.py
```

### Debugging
```javascript
// Enable in console
localStorage.setItem('debug', 'true');

// View current layout
console.log(dashboardBuilder.layout);

// View all widgets
console.log(dashboardBuilder.widgets);
```

## Credits

- **NES.css**: https://nostalgic-css.github.io/NES.css/
- **Press Start 2P Font**: Google Fonts
- **Synthwave DOS Colors**: uDOS Extensions Framework
- **Widget Icons**: Unicode/Emoji

## Version History

### v1.0.24 (Current)
- ✨ Complete dashboard builder
- 🎮 NES.css framework integration
- 🎨 4 retro themes
- 📦 12+ widget types
- 💾 Import/export layouts
- ⚙️ Full customization

### Future Plans
- Drag-and-drop widget rearrangement
- Custom widget builder UI
- Widget size/span options
- Dashboard sharing/marketplace
- Real-time collaboration
- Mobile app (PWA)

## License

MIT License - Part of uDOS v1.0.24

---

**READY.**
