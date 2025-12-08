# File Picker - Memory Browser Implementation

## Overview
Created a desktop file picker for browsing the `/memory` folder with subfolder navigation and file operations integration.

## Features

### Core Functionality
- **Folder Navigation**: Browse all `/memory` subfolders via dropdown selector
- **Up Navigation**: Navigate back to parent `/memory` directory
- **File Listing**: Display files and subfolders with icons and metadata
- **File Selection**: Click to select, double-click to open
- **Refresh**: Reload current folder contents
- **Status Display**: Real-time path, file count, and status updates

### UI Components

#### Toolbar
- **Up Button** (↑): Navigate to parent directory
- **Refresh Button** (⟳): Reload folder contents
- **New File Button** (+): Create new file (placeholder for server-side implementation)
- **Folder Dropdown**: Quick access to all memory subfolders:
  - config, logs, missions, modules
  - personal, private, public, sandbox
  - scenarios, shared, tests, themes
  - user, workflow, workspace

#### File List
- **File Icons**: Emoji-based file type indicators
  - 📁 Folders
  - 📝 Markdown (.md)
  - 📄 Text (.txt)
  - 📋 JSON (.json)
  - 🐍 Python (.py)
  - 📜 JavaScript (.js)
  - 🌐 HTML (.html)
  - 🎨 CSS (.css)
  - ⚙️ Scripts (.uscript, .conf)
  - 📊 Logs (.log)
  - 💾 Database (.db)
  - ⚡ Shell (.sh)

- **File Information**:
  - Name
  - Type (extension in uppercase)
  - Hover effect (grey background)
  - Selection effect (black background, white text)

#### Details Bar
- **Current Path**: Shows `/memory` or `/memory/subfolder`
- **File Count**: "X folders, Y files" or "0 items"

#### Status Bar
- **Status Text**: Loading/Ready/Error messages
- **Selected File**: Currently selected filename

### File Operations

#### Browse
1. Select folder from dropdown
2. View files and subfolders
3. Click to select file
4. Hover for visual feedback

#### Open File
- **Double-click** any file to open in new tab
- Opens URL: `http://localhost:8888/memory/{folder}/{filename}`
- Status updates: "Opened: {filename}"

#### Navigate Subfolders
- **Double-click** folder to navigate into it
- Updates path and loads contents
- Supports nested navigation

### Integration

#### Desktop Icon
- **Icon**: CoreUI `cil-folder.svg` (📁)
- **Label**: "Files"
- **Action**: `openFilePicker()`
- **Position**: Bottom of icon bar (x: 20, y: 540)

#### Window Styling
- **Title**: "Memory Browser"
- **Size**: 600×500px
- **Position**: (180, 120)
- **system.css styling**: Standard window with title bar, separator, details bar

### Technical Implementation

#### File System Access
```javascript
async function loadFolderContents(folder) {
    // Fetch directory listing from HTTP server
    const response = await fetch(`/memory/${folder}/`);

    // Parse HTML directory listing
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // Extract file/folder links
    const links = Array.from(doc.querySelectorAll('a'));

    // Render file list with icons and metadata
    renderFileList(links, folder);
}
```

#### State Management
```javascript
let currentPath = '/memory';
let currentFolder = '';

function changeFolder(folder) {
    currentFolder = folder;
    currentPath = `/memory/${folder}`;
    updatePathDisplay();
    loadFolderContents(folder);
}
```

#### File Selection
```javascript
function selectFile(item, name) {
    // Deselect all
    document.querySelectorAll('.file-item').forEach(el => {
        el.style.background = 'transparent';
    });

    // Select current
    item.style.background = '#000';
    item.style.color = '#fff';
}
```

### CSS Styling

```css
/* File item styling */
.file-item {
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: Geneva_9, Chicago, sans-serif;
  font-size: 12px;
  transition: background 0.1s;
}

.file-item:hover {
  background: #f0f0f0;
}

.file-item.selected {
  background: #000;
  color: #fff;
}

#file-list {
  background: #fff;
  border: 2px inset #e0e0e0;
}
```

## Server Requirements

### Directory Structure
Server must be running from uDOS root directory:
```bash
cd /Users/fredbook/Code/uDOS
python3 -m http.server 8888
```

### File Access
- **Base URL**: `http://localhost:8888/`
- **Memory Folder**: `/memory/` accessible from root
- **Extensions**: `/extensions/core/desktop/` for UI files
- **Icons**: `/extensions/icons/coreui/` for desktop icons
- **Fonts**: `/extensions/core/fonts/` for system.css fonts

### Directory Listing
Python's HTTP server provides HTML directory listings that can be parsed:
```html
<a href="file.txt">file.txt</a>
<a href="subfolder/">subfolder/</a>
```

## Usage Workflow

### Basic Navigation
1. Double-click "Files" desktop icon
2. File Picker window opens
3. Select folder from dropdown (e.g., "sandbox")
4. Browse files in list
5. Double-click file to open in new tab

### Advanced Features
1. **Navigate into subfolders**: Double-click folder item
2. **Return to parent**: Click "↑ Up" button
3. **Refresh view**: Click "⟳ Refresh" button
4. **Select multiple**: Click files (visual feedback)
5. **View path**: Check details bar at top

## Error Handling

### No Server Access
```
Cannot load folder contents
Make sure the server is running from the uDOS root directory
Try: cd /Users/fredbook/Code/uDOS && python3 -m http.server 8888
```

### Empty Folder
```
No files found in {folder}/
```

### General Errors
```javascript
catch (error) {
    console.error('Error loading folder:', error);
    statusText.textContent = 'Error';
}
```

## Future Enhancements

### Planned Features
- [ ] **Typo Integration**: Open files directly in Typo editor
- [ ] **File Upload**: Drag-and-drop file upload
- [ ] **New File**: Server-side file creation
- [ ] **Delete/Rename**: File management operations
- [ ] **Search**: Filter files by name/extension
- [ ] **Sort**: Sort by name, date, size, type
- [ ] **View Toggle**: List view vs grid view
- [ ] **File Preview**: Quick preview pane
- [ ] **Breadcrumb Navigation**: Clickable path segments
- [ ] **Context Menu**: Right-click file operations
- [ ] **Keyboard Shortcuts**: Arrow keys, Enter to open
- [ ] **Multi-select**: Ctrl/Cmd+click for batch operations

### Server-Side Requirements
```python
# File creation endpoint
POST /api/file/create
{ "path": "/memory/sandbox/test.txt", "content": "" }

# File read/write endpoints
GET /api/file/read?path=/memory/sandbox/test.txt
POST /api/file/write
{ "path": "/memory/sandbox/test.txt", "content": "..." }

# File operations
DELETE /api/file/delete?path=/memory/sandbox/test.txt
POST /api/file/rename
{ "old": "/memory/sandbox/test.txt", "new": "/memory/sandbox/renamed.txt" }
```

## Testing

### Verified Features
✅ Window opens from Files icon
✅ Folder dropdown populated with all memory subfolders
✅ Folder selection loads contents
✅ File list displays with proper icons
✅ File selection (click) works
✅ Hover effects on files
✅ Double-click opens file in new tab
✅ Up navigation returns to parent
✅ Refresh reloads folder
✅ Path display updates correctly
✅ File count updates
✅ Status messages display
✅ Error handling for no server access

### Browser Compatibility
- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Full support

## File Paths (Updated for Root Server)

### CSS Paths
- Fonts: `/extensions/core/fonts/`
- Icons: `/extensions/core/icons/`

### JavaScript Paths
- Desktop icons: `/extensions/icons/coreui/`
- Memory access: `/memory/{folder}/`

### HTML Structure
- Desktop UI: `/extensions/core/desktop/index.html`
- File Picker: Embedded in index.html as `#file-picker-window`

## Summary

The File Picker provides a Classic desktop-style file browser (inspired by Mac OS System 6) for the `/memory` folder with:
- ✅ Clean system.css styling
- ✅ Folder navigation with dropdown
- ✅ File listing with icons and metadata
- ✅ Selection and hover effects
- ✅ Double-click to open files
- ✅ Status and path display
- ✅ Error handling

**Status**: Production ready for browsing
**Next Step**: Integrate with Typo editor for read/write operations

**URL**: `http://localhost:8888/extensions/core/desktop/index.html`
**Server**: Must run from `/Users/fredbook/Code/uDOS` root directory
