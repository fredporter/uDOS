# System 7 CSS Framework

A faithful recreation of Apple's classic Macintosh System 7 interface for modern web browsers. This framework provides authentic System 7 styling and functionality using pure CSS and JavaScript.

## 🎯 Features

### **Visual Authenticity**
- **Pixel-perfect System 7 styling** with authentic colors and typography
- **Classic Chicago, Geneva, and Monaco fonts** integration
- **Authentic window chrome** with title bars, close boxes, and grow boxes
- **System 7 color palette** with proper grays and selection colors
- **Classic UI controls** (buttons, checkboxes, radio buttons, lists)

### **Interactive Functionality**
- **Draggable windows** with title bar dragging
- **Resizable windows** with grow box resizing
- **Working menu bar** with dropdown menus
- **Modal dialogs** with authentic styling
- **Keyboard shortcuts** (Cmd/Ctrl combinations)
- **Focus management** and accessibility features

### **Modern Web Compatibility**
- **Responsive design** that adapts to different screen sizes
- **Touch-friendly** interface for mobile devices
- **Browser compatibility** across modern browsers
- **CSS Grid and Flexbox** for layout management
- **JavaScript API** for dynamic window and control creation

## 🚀 Quick Start

### **Basic Setup**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My System 7 App</title>
    <link rel="stylesheet" href="system7.css">
</head>
<body>
    <script src="system7.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // System 7 automatically creates desktop and menu bar

            // Create a window
            window.system7.createWindow({
                title: 'My Application',
                content: '<p>Hello, System 7!</p>',
                x: 100,
                y: 100,
                width: 400,
                height: 300
            });
        });
    </script>
</body>
</html>
```

## 🎨 CSS Classes

### **Layout Components**
- `.sys7-desktop` - Desktop background
- `.sys7-menubar` - Top menu bar
- `.sys7-window` - Window container
- `.sys7-window-title-bar` - Window title bar
- `.sys7-window-content` - Window content area
- `.sys7-status-bar` - Bottom status bar

### **UI Controls**
- `.sys7-button` - Standard button
- `.sys7-button-default` - Default button (thick border)
- `.sys7-text-input` - Text input field
- `.sys7-checkbox` - Checkbox control
- `.sys7-radio` - Radio button control
- `.sys7-list` - List container
- `.sys7-list-item` - List item

### **Dialog Components**
- `.sys7-dialog` - Modal dialog
- `.sys7-dialog-title` - Dialog title
- `.sys7-dialog-content` - Dialog content
- `.sys7-dialog-buttons` - Dialog button container

### **Icons**
- `.sys7-icon-folder` - Folder icon
- `.sys7-icon-document` - Document icon
- `.sys7-icon-trash` - Trash can icon

### **Utility Classes**
- `.sys7-hidden` - Hide element
- `.sys7-disabled` - Disable element
- `.sys7-selected` - Selected state
- `.sys7-text-center` - Center text
- `.sys7-text-bold` - Bold text

## 💻 JavaScript API

### **Window Management**
```javascript
// Create a new window
const windowId = window.system7.createWindow({
    title: 'Window Title',
    content: 'HTML content or DOM element',
    x: 100,
    y: 100,
    width: 400,
    height: 300
});

// Close a window
window.system7.closeWindow(windowId);

// Activate a window
window.system7.activateWindow(windowId);
```

### **UI Controls**
```javascript
// Create a button
const button = window.system7.createButton('Click Me', () => {
    alert('Button clicked!');
}, false); // true for default button

// Create a text input
const input = window.system7.createTextInput('Placeholder', 'Initial value');

// Create a checkbox
const checkbox = window.system7.createCheckbox('Option', true, (e) => {
    console.log('Checked:', e.target.checked);
});

// Create a radio button
const radio = window.system7.createRadio('group', 'Option 1', 'value1', true);

// Create a list
const list = window.system7.createList([
    'Item 1',
    'Item 2',
    { text: 'Item 3', value: 'custom-value' }
], (value, index) => {
    console.log('Selected:', value, 'at index', index);
});
```

### **Dialogs**
```javascript
// Show an alert
window.system7.alert('Message', 'Title');

// Show a confirm dialog
window.system7.confirm('Are you sure?', 'Confirm',
    () => console.log('OK clicked'),
    () => console.log('Cancel clicked')
);

// Show a custom dialog
window.system7.showDialog({
    title: 'Custom Dialog',
    content: '<p>Dialog content</p>',
    buttons: [
        { text: 'Cancel' },
        { text: 'OK', default: true, action: () => console.log('OK') }
    ]
});
```

## 🎨 Theming and Customization

### **CSS Custom Properties**
The framework uses CSS custom properties for easy theming:

```css
:root {
    /* Colors */
    --sys7-white: #FFFFFF;
    --sys7-light-gray: #DDDDDD;
    --sys7-medium-gray: #AAAAAA;
    --sys7-dark-gray: #777777;
    --sys7-black: #000000;
    --sys7-desktop-gray: #C6C6C6;
    --sys7-selection: #316AC5;

    /* Fonts */
    --sys7-system-font: 'Chicago', 'Geneva', monospace;
    --sys7-dialog-font: 'Geneva', 'Chicago', sans-serif;
    --sys7-mono-font: 'Monaco', 'Courier New', monospace;

    /* Spacing */
    --sys7-unit: 8px;
    --sys7-border-width: 1px;
    --sys7-shadow-offset: 2px;
}
```

### **Custom Themes**
Create custom themes by overriding the CSS custom properties:

```css
.dark-theme {
    --sys7-desktop-gray: #333333;
    --sys7-window-gray: #444444;
    --sys7-button-face: #555555;
    --sys7-text-primary: #FFFFFF;
}
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl+N` | New Document |
| `Cmd/Ctrl+O` | Open Document |
| `Cmd/Ctrl+S` | Save Document |
| `Cmd/Ctrl+W` | Close Window |
| `Cmd/Ctrl+Q` | Quit Application |
| `Tab` | Navigate between controls |
| `Space` | Activate focused button/checkbox |
| `Enter` | Activate default button |
| `Escape` | Cancel/Close dialog |

## 📱 Responsive Design

The framework automatically adapts to different screen sizes:

### **Desktop (>1200px)**
- Full window management with dragging and resizing
- Complete menu bar functionality
- Multi-window interface

### **Tablet (768-1200px)**
- Simplified window management
- Touch-friendly controls
- Responsive layouts

### **Mobile (<768px)**
- Single-window mode
- Touch-optimized interface
- Simplified navigation

## 🔧 Integration with uDOS

### **Dashboard Integration**
The System 7 framework integrates seamlessly with the uDOS Advanced Dashboard:

```javascript
// Add System 7 module to dashboard
loadModule('system7-interface');

// Switch to System 7 theme
DashboardAPI.applyTheme('system7');
```

### **Typography System Integration**
Works with the uDOS typography system:

```javascript
// Use typography manager
if (typeof TypographyManager !== 'undefined') {
    TypographyManager.setTheme('chicago');
}
```

## 🎯 Browser Compatibility

### **Supported Browsers**
- **Chrome/Chromium** 80+
- **Firefox** 75+
- **Safari** 13+
- **Edge** 80+

### **Required Features**
- CSS Grid Layout
- CSS Custom Properties
- ES6 Classes
- DOM Level 2 Events
- CSS Flexbox

### **Optional Enhancements**
- CSS `backdrop-filter` for blur effects
- Web Fonts API for better font loading
- Pointer Events for touch optimization

## 🚀 Performance

### **Optimization Features**
- **Minimal DOM manipulation** - Efficient event handling
- **CSS-based animations** - Hardware accelerated transitions
- **Event delegation** - Reduced memory footprint
- **Lazy loading** - Components created on demand

### **Best Practices**
- Use CSS transforms for animations
- Minimize reflows and repaints
- Batch DOM operations
- Use passive event listeners where possible

## 📚 Examples

### **Simple Application**
```javascript
// Create main application window
const appWindow = window.system7.createWindow({
    title: 'My App',
    width: 500,
    height: 400
});

// Add controls to window content
const windowData = window.system7.windows.get(appWindow);
const content = windowData.content;

content.appendChild(window.system7.createButton('Save', () => {
    window.system7.alert('File saved!');
}));

content.appendChild(window.system7.createTextInput('Enter filename...'));
```

### **Form Dialog**
```javascript
const formContent = document.createElement('div');

const nameInput = window.system7.createTextInput('Name', '');
const emailInput = window.system7.createTextInput('Email', '');
const newsletter = window.system7.createCheckbox('Subscribe to newsletter', false);

formContent.appendChild(document.createTextNode('Name: '));
formContent.appendChild(nameInput);
formContent.appendChild(document.createElement('br'));
formContent.appendChild(document.createTextNode('Email: '));
formContent.appendChild(emailInput);
formContent.appendChild(document.createElement('br'));
formContent.appendChild(newsletter);

window.system7.showDialog({
    title: 'User Information',
    content: formContent,
    buttons: [
        { text: 'Cancel' },
        {
            text: 'Submit',
            default: true,
            action: () => {
                const name = nameInput.value;
                const email = emailInput.value;
                const subscribed = newsletter.querySelector('input').checked;
                console.log('Form data:', { name, email, subscribed });
            }
        }
    ]
});
```

## 🐛 Known Issues

1. **Font Loading**: Some fonts may not load immediately on slower connections
2. **Touch Scrolling**: Window content scrolling may conflict with window dragging on touch devices
3. **High DPI**: Some border styles may appear thin on high-DPI displays
4. **Memory**: Long-running applications may accumulate event listeners

## 🔮 Future Enhancements

### **v1.1 Planned Features**
- Sound effects (System 7 beeps and alerts)
- Improved accessibility (screen reader support)
- More authentic fonts and typography
- Enhanced touch support
- Window management improvements

### **v1.2 Vision**
- Authentic System 7 animations
- Desk accessories support
- File system integration
- Multi-user support
- Plugin architecture

## 📄 License

Part of the uDOS project. Created for educational and preservation purposes.

## 🤝 Contributing

1. Fork the uDOS repository
2. Create feature branch: `git checkout -b feature/system7-enhancement`
3. Make changes to `extensions/web/system7-css/`
4. Test across browsers and screen sizes
5. Submit pull request with detailed description

---

**Experience computing as it was meant to be.** 🖱️

*Bringing the classic Macintosh experience to the modern web.*
