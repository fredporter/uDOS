/**
 * uDOS File Picker v1.3
 * Deep-linked file browser with CLI integration
 */

class uDOSFilePicker {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: options.apiEndpoint || 'http://localhost:8890/api',
            theme: options.theme || 'dark',
            onFileSelect: options.onFileSelect || null,
            allowedExtensions: options.allowedExtensions || null, // null = all files
            rootPath: options.rootPath || '.',
            ...options
        };

        this.currentPath = this.options.rootPath;
        this.files = [];
        this.selectedFile = null;

        this.init();
    }

    init() {
        this.createPickerHTML();
        this.attachEventListeners();
    }

    createPickerHTML() {
        const picker = document.createElement('div');
        picker.className = 'udos-file-picker';
        picker.id = 'udosFilePicker';
        picker.innerHTML = `
            <div class="picker-overlay"></div>
            <div class="picker-dialog">
                <div class="picker-header">
                    <div class="picker-title">
                        <span class="picker-icon">📁</span>
                        <span class="picker-label">uDOS FILE BROWSER</span>
                    </div>
                    <button class="picker-close" id="pickerClose">✕</button>
                </div>

                <div class="picker-toolbar">
                    <div class="picker-breadcrumb" id="pickerBreadcrumb">
                        <span class="breadcrumb-item active">~</span>
                    </div>
                    <div class="picker-actions">
                        <button class="picker-btn" id="pickerRefresh" title="Refresh">
                            <span>⟳</span>
                        </button>
                        <button class="picker-btn" id="pickerUp" title="Parent Directory">
                            <span>↑</span>
                        </button>
                    </div>
                </div>

                <div class="picker-body" id="pickerBody">
                    <div class="picker-loading">
                        <div class="loading-spinner">⟳</div>
                        <div class="loading-text">Loading files...</div>
                    </div>
                </div>

                <div class="picker-footer">
                    <div class="picker-info" id="pickerInfo">
                        <span class="info-label">Selected:</span>
                        <span class="info-value" id="selectedPath">None</span>
                    </div>
                    <div class="picker-footer-actions">
                        <button class="picker-btn-primary" id="pickerOpen" disabled>
                            OPEN FILE
                        </button>
                        <button class="picker-btn-secondary" id="pickerCancel">
                            CANCEL
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(picker);
        this.pickerElement = picker;
    }

    attachEventListeners() {
        // Close buttons
        document.getElementById('pickerClose').addEventListener('click', () => this.close());
        document.getElementById('pickerCancel').addEventListener('click', () => this.close());

        // Overlay click to close
        this.pickerElement.querySelector('.picker-overlay').addEventListener('click', () => this.close());

        // Action buttons
        document.getElementById('pickerRefresh').addEventListener('click', () => this.loadFiles());
        document.getElementById('pickerUp').addEventListener('click', () => this.navigateUp());
        document.getElementById('pickerOpen').addEventListener('click', () => this.openFile());

        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.pickerElement.classList.contains('active')) {
                this.close();
            }
        });
    }

    async open() {
        this.pickerElement.classList.add('active');
        await this.loadFiles();
    }

    close() {
        this.pickerElement.classList.remove('active');
        this.selectedFile = null;
        this.updateSelectedDisplay();
    }

    async loadFiles() {
        const bodyElement = document.getElementById('pickerBody');
        bodyElement.innerHTML = `
            <div class="picker-loading">
                <div class="loading-spinner">⟳</div>
                <div class="loading-text">Loading files...</div>
            </div>
        `;

        try {
            // Call uDOS CLI to list files
            const response = await fetch(`${this.options.apiEndpoint}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: `ls -la "${this.currentPath}"`
                })
            });

            if (!response.ok) throw new Error('Failed to load files');

            const data = await response.json();
            this.parseFileList(data.output || '');
            this.renderFiles();

        } catch (error) {
            console.error('File picker error:', error);
            bodyElement.innerHTML = `
                <div class="picker-error">
                    <div class="error-icon">⚠</div>
                    <div class="error-text">Failed to load files</div>
                    <div class="error-detail">${error.message}</div>
                </div>
            `;
        }
    }

    parseFileList(output) {
        // Parse ls -la output
        const lines = output.split('\n').slice(1); // Skip total line
        this.files = [];

        for (const line of lines) {
            if (!line.trim()) continue;

            const parts = line.trim().split(/\s+/);
            if (parts.length < 9) continue;

            const permissions = parts[0];
            const size = parts[4];
            const name = parts.slice(8).join(' ');

            if (name === '.' || name === '..') continue;

            const isDir = permissions.startsWith('d');
            const extension = name.includes('.') ? name.split('.').pop() : '';

            // Filter by allowed extensions
            if (!isDir && this.options.allowedExtensions) {
                if (!this.options.allowedExtensions.includes(extension)) {
                    continue;
                }
            }

            this.files.push({
                name,
                size,
                isDir,
                extension,
                permissions
            });
        }

        // Sort: directories first, then alphabetically
        this.files.sort((a, b) => {
            if (a.isDir && !b.isDir) return -1;
            if (!a.isDir && b.isDir) return 1;
            return a.name.localeCompare(b.name);
        });
    }

    renderFiles() {
        const bodyElement = document.getElementById('pickerBody');

        if (this.files.length === 0) {
            bodyElement.innerHTML = `
                <div class="picker-empty">
                    <div class="empty-icon">📂</div>
                    <div class="empty-text">No files found</div>
                </div>
            `;
            return;
        }

        const fileListHTML = this.files.map(file => {
            const icon = file.isDir ? '📁' : this.getFileIcon(file.extension);
            const sizeDisplay = file.isDir ? '---' : this.formatSize(file.size);

            return `
                <div class="file-item" data-file='${JSON.stringify(file)}'>
                    <div class="file-icon">${icon}</div>
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-meta">${sizeDisplay}</div>
                    </div>
                </div>
            `;
        }).join('');

        bodyElement.innerHTML = `<div class="file-list">${fileListHTML}</div>`;

        // Attach click handlers
        bodyElement.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', () => this.selectFile(item));
            item.addEventListener('dblclick', () => this.handleDoubleClick(item));
        });
    }

    selectFile(itemElement) {
        // Clear previous selection
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));

        // Select new item
        itemElement.classList.add('selected');
        this.selectedFile = JSON.parse(itemElement.dataset.file);
        this.updateSelectedDisplay();

        // Enable/disable open button
        document.getElementById('pickerOpen').disabled = false;
    }

    handleDoubleClick(itemElement) {
        const file = JSON.parse(itemElement.dataset.file);

        if (file.isDir) {
            this.navigateInto(file.name);
        } else {
            this.openFile();
        }
    }

    navigateInto(dirname) {
        this.currentPath = `${this.currentPath}/${dirname}`.replace('//', '/');
        this.updateBreadcrumb();
        this.loadFiles();
    }

    navigateUp() {
        const parts = this.currentPath.split('/').filter(p => p);
        parts.pop();
        this.currentPath = parts.length > 0 ? parts.join('/') : '.';
        this.updateBreadcrumb();
        this.loadFiles();
    }

    updateBreadcrumb() {
        const breadcrumb = document.getElementById('pickerBreadcrumb');
        const parts = this.currentPath.split('/').filter(p => p && p !== '.');

        let html = '<span class="breadcrumb-item" data-path=".">~</span>';
        let currentPath = '';

        for (const part of parts) {
            currentPath += `/${part}`;
            html += `<span class="breadcrumb-sep">›</span>`;
            html += `<span class="breadcrumb-item" data-path="${currentPath}">${part}</span>`;
        }

        breadcrumb.innerHTML = html;

        // Add click handlers
        breadcrumb.querySelectorAll('.breadcrumb-item').forEach(item => {
            item.addEventListener('click', () => {
                this.currentPath = item.dataset.path;
                this.updateBreadcrumb();
                this.loadFiles();
            });
        });
    }

    updateSelectedDisplay() {
        const pathElement = document.getElementById('selectedPath');
        if (this.selectedFile) {
            const fullPath = `${this.currentPath}/${this.selectedFile.name}`.replace('//', '/');
            pathElement.textContent = fullPath;
            pathElement.style.color = 'var(--polaroid-cyan)';
        } else {
            pathElement.textContent = 'None';
            pathElement.style.color = 'var(--text-secondary)';
        }
    }

    async openFile() {
        if (!this.selectedFile || this.selectedFile.isDir) return;

        const fullPath = `${this.currentPath}/${this.selectedFile.name}`.replace('//', '/');

        if (this.options.onFileSelect) {
            await this.options.onFileSelect(fullPath, this.selectedFile);
        }

        this.close();
    }

    getFileIcon(extension) {
        const iconMap = {
            'md': '📝',
            'txt': '📄',
            'udo': '🔮',
            'udt': '🗂️',
            'usc': '⚙️',
            'uscript': '📜',
            'py': '🐍',
            'js': '📜',
            'json': '{}',
            'css': '🎨',
            'html': '🌐',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'gif': '🖼️'
        };

        return iconMap[extension.toLowerCase()] || '📄';
    }

    formatSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Export for use
window.uDOSFilePicker = uDOSFilePicker;
