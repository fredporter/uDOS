// uDOS Classicy Desktop - Enhanced File Operations
// Integration with uDOS FILE commands and drag-drop support

class ClassicyFileManager {
  constructor() {
    this.selectedFiles = new Set();
    this.currentPath = '/';
    this.fileHistory = [];
    this.bookmarks = [];
    this.initializeDragDrop();
  }

  // Initialize drag and drop functionality
  initializeDragDrop() {
    const desktop = document.getElementById('desktop');
    const fileWindow = document.getElementById('file-window');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      desktop.addEventListener(eventName, this.preventDefaults, false);
      fileWindow?.addEventListener(eventName, this.preventDefaults, false);
    });

    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
      desktop.addEventListener(eventName, this.highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      desktop.addEventListener(eventName, this.unhighlight, false);
    });

    // Handle dropped files
    desktop.addEventListener('drop', this.handleDrop.bind(this), false);
  }

  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  highlight(e) {
    e.target.classList.add('drag-over');
  }

  unhighlight(e) {
    e.target.classList.remove('drag-over');
  }

  async handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      await this.uploadFiles(files);
    }
  }

  // File upload handling
  async uploadFiles(files) {
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        this.showNotification(`Uploaded ${files.length} file(s) successfully`);
        this.refreshFileList();
      } else {
        this.showNotification('Upload failed', 'error');
      }
    } catch (error) {
      this.showNotification('Upload error: ' + error.message, 'error');
    }
  }

  // FILE command implementations
  async executeFilePick(pattern = '') {
    try {
      const response = await fetch('/api/files/pick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern })
      });

      if (response.ok) {
        const files = await response.json();
        this.displayFilePickerDialog(files);
      } else {
        this.simulateFilePick(pattern);
      }
    } catch (error) {
      this.simulateFilePick(pattern);
    }
  }

  async executeFileRecent(count = 10) {
    try {
      const response = await fetch(`/api/files/recent?count=${count}`);
      if (response.ok) {
        const files = await response.json();
        this.displayRecentFiles(files);
      } else {
        this.simulateFileRecent();
      }
    } catch (error) {
      this.simulateFileRecent();
    }
  }

  async executeFileBookmarks(action = 'LIST', filename = '') {
    try {
      let url = '/api/files/bookmarks';
      let options = { method: 'GET' };

      if (action === 'ADD' && filename) {
        options = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        };
      } else if (action === 'REMOVE' && filename) {
        options = {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        };
      }

      const response = await fetch(url, options);
      if (response.ok) {
        const bookmarks = await response.json();
        this.displayBookmarks(bookmarks);
      } else {
        this.simulateBookmarks();
      }
    } catch (error) {
      this.simulateBookmarks();
    }
  }

  async executeFileBatch(operation, pattern, destination = '') {
    try {
      const response = await fetch('/api/files/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ operation, pattern, destination })
      });

      if (response.ok) {
        const result = await response.json();
        this.showNotification(`Batch ${operation}: ${result.affected_files} files processed`);
        this.refreshFileList();
      } else {
        this.simulateBatchOperation(operation, pattern);
      }
    } catch (error) {
      this.simulateBatchOperation(operation, pattern);
    }
  }

  // UI Display Methods
  displayFilePickerDialog(files) {
    const dialog = this.createDialog('File Picker', 500, 400);
    const content = dialog.querySelector('.classic-content');

    content.innerHTML = `
      <div style="margin-bottom: 8px;">
        <input type="text" class="classic-input" id="file-search" placeholder="Search files..." style="width: 100%;">
      </div>
      <div class="classic-file-browser" style="height: 250px; overflow-y: auto; border: 1px solid #808080;">
        ${files.map(file => `
          <div class="classic-file-item" onclick="selectFileInPicker(this, '${file.path}')" ondblclick="openFileFromPicker('${file.path}')">
            <div class="classic-file-icon"></div>
            ${this.getFileIcon(file.type)} ${file.name}
            <div style="margin-left: auto; font-size: 8px; color: #666;">${file.size}</div>
          </div>
        `).join('')}
      </div>
      <div style="margin-top: 8px; text-align: right;">
        <button class="classic-button" onclick="closeDialog()">Cancel</button>
        <button class="classic-button default" onclick="openSelectedFile()">Open</button>
      </div>
    `;
  }

  displayRecentFiles(files) {
    const output = document.getElementById('main-output');
    output.textContent += '\nRecent Files:\n';
    files.forEach((file, index) => {
      output.textContent += `${index + 1}. ${file.name} (${file.last_accessed})\n`;
    });
    output.scrollTop = output.scrollHeight;
  }

  displayBookmarks(bookmarks) {
    const dialog = this.createDialog('Bookmarks', 400, 300);
    const content = dialog.querySelector('.classic-content');

    content.innerHTML = `
      <div class="classic-file-browser" style="height: 200px; overflow-y: auto; border: 1px solid #808080;">
        ${bookmarks.map(bookmark => `
          <div class="classic-file-item" onclick="selectFile(this)" ondblclick="openBookmark('${bookmark.path}')">
            <div class="classic-file-icon"></div>
            ⭐ ${bookmark.name}
            <div style="margin-left: auto; font-size: 8px; color: #666;">${bookmark.tags || ''}</div>
          </div>
        `).join('')}
      </div>
      <div style="margin-top: 8px;">
        <button class="classic-button" onclick="addCurrentToBookmarks()">Add Current</button>
        <button class="classic-button" onclick="removeSelectedBookmark()">Remove</button>
        <button class="classic-button" onclick="closeDialog()">Close</button>
      </div>
    `;
  }

  // Utility Methods
  createDialog(title, width, height) {
    const dialog = document.createElement('div');
    dialog.className = 'classic-window';
    dialog.style.cssText = `
      width: ${width}px;
      height: ${height}px;
      top: ${50 + Math.random() * 100}px;
      left: ${50 + Math.random() * 100}px;
      z-index: 300;
    `;

    dialog.innerHTML = `
      <div class="classic-titlebar active">
        <div class="classic-close-box" onclick="closeDialog()"></div>
        <div style="flex: 1; text-align: center;">${title}</div>
      </div>
      <div class="classic-content"></div>
    `;

    document.body.appendChild(dialog);
    makeWindowDraggable(dialog);
    return dialog;
  }

  getFileIcon(type) {
    const icons = {
      'folder': '📁',
      'python': '🐍',
      'javascript': '📜',
      'css': '🎨',
      'html': '🌐',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'image': '🖼️',
      'video': '🎬',
      'audio': '🎵'
    };
    return icons[type] || '📄';
  }

  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 30px;
      right: 20px;
      background: ${type === 'error' ? '#ffebee' : '#e8f5e8'};
      border: 1px solid ${type === 'error' ? '#f44336' : '#4caf50'};
      padding: 8px 12px;
      font-size: 9px;
      z-index: 1000;
      box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;

    document.body.appendChild(notification);
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 3000);
  }

  async refreshFileList() {
    try {
      const response = await fetch('/api/files/list');
      if (response.ok) {
        const files = await response.json();
        this.updateFileListDisplay(files);
      }
    } catch (error) {
      console.log('Using demo file list');
    }
  }

  // Demo/Simulation Methods
  simulateFilePick(pattern) {
    const demoFiles = [
      { name: 'uDOS.py', path: '/uDOS.py', type: 'python', size: '15.2KB' },
      { name: 'README.MD', path: '/README.MD', type: 'md', size: '8.1KB' },
      { name: 'core/', path: '/core', type: 'folder', size: '—' },
      { name: 'extensions/', path: '/extensions', type: 'folder', size: '—' }
    ];

    const filtered = pattern ?
      demoFiles.filter(f => f.name.toLowerCase().includes(pattern.toLowerCase())) :
      demoFiles;

    this.displayFilePickerDialog(filtered);
  }

  simulateFileRecent() {
    const demoRecent = [
      { name: 'core/uDOS_main.py', last_accessed: '2 hours ago' },
      { name: 'extensions/web/classicy-desktop/index.html', last_accessed: '4 hours ago' },
      { name: 'memory/config/user.json', last_accessed: '1 day ago' }
    ];
    this.displayRecentFiles(demoRecent);
  }

  simulateBookmarks() {
    const demoBookmarks = [
      { name: 'Main Config', path: '/memory/config/user.json', tags: 'config' },
      { name: 'Core System', path: '/core/uDOS_main.py', tags: 'core,system' },
      { name: 'Web Extensions', path: '/extensions/web', tags: 'web,extensions' }
    ];
    this.displayBookmarks(demoBookmarks);
  }

  simulateBatchOperation(operation, pattern) {
    const count = Math.floor(Math.random() * 10) + 1;
    this.showNotification(`Batch ${operation}: ${count} files processed (demo)`);
  }
}

// Global file manager instance
window.fileManager = new ClassicyFileManager();

// Enhanced FILE command functions
window.executeFilePick = function(pattern = '') {
  window.fileManager.executeFilePick(pattern);
};

window.executeFileRecent = function(count = 10) {
  window.fileManager.executeFileRecent(count);
};

window.executeFileBookmarks = function(action = 'LIST', filename = '') {
  window.fileManager.executeFileBookmarks(action, filename);
};

window.executeFileBatch = function(operation, pattern, destination = '') {
  window.fileManager.executeFileBatch(operation, pattern, destination);
};

// Dialog management
window.closeDialog = function() {
  const dialogs = document.querySelectorAll('.classic-window');
  dialogs.forEach(dialog => {
    if (dialog.style.zIndex === '300') {
      document.body.removeChild(dialog);
    }
  });
};

// CSS for drag and drop
const dragDropStyles = `
  .drag-over {
    background-color: rgba(74, 144, 226, 0.1) !important;
    border: 2px dashed #4A90E2 !important;
  }

  .file-drop-zone {
    min-height: 100px;
    border: 2px dashed #ccc;
    border-radius: 4px;
    text-align: center;
    padding: 20px;
    margin: 10px 0;
    background: #f9f9f9;
    transition: all 0.3s ease;
  }

  .file-drop-zone.drag-over {
    border-color: #4A90E2;
    background: #e8f4fd;
  }
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = dragDropStyles;
document.head.appendChild(styleSheet);
