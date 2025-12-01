// File browser functionality
class FileBrowser {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentPath = '';
        this.selectedItems = new Set();
        this.initializeUI();
        this.setupEventListeners();
    }

    initializeUI() {
        this.container.innerHTML = `
            <div class="file-browser-header">
                <div class="breadcrumb"></div>
                <div class="file-actions">
                    <button class="action-btn" data-action="refresh">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                    <button class="action-btn" data-action="upload">
                        <i class="fas fa-upload"></i> Upload
                    </button>
                </div>
            </div>
            <div class="file-browser-split">
                <div class="file-list"></div>
                <div class="file-preview"></div>
            </div>
        `;

        this.breadcrumb = this.container.querySelector('.breadcrumb');
        this.fileList = this.container.querySelector('.file-list');
        this.preview = this.container.querySelector('.file-preview');
    }

    setupEventListeners() {
        this.container.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]')?.dataset.action;
            if (action) {
                this[action](e);
            }
        });

        // Setup drag and drop
        this.fileList.addEventListener('dragstart', (e) => this.handleDragStart(e));
        this.fileList.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.fileList.addEventListener('drop', (e) => this.handleDrop(e));
    }

    async loadDirectory(path = '') {
        try {
            const response = await fetch(`/api/files/list?path=${encodeURIComponent(path)}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.currentPath = path;
                this.updateBreadcrumb();
                this.renderFileList(data.items);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Failed to load directory:', error);
            // Show error in UI
        }
    }

    updateBreadcrumb() {
        const parts = this.currentPath.split('/').filter(Boolean);
        const breadcrumbHtml = parts.map((part, index) => {
            const path = parts.slice(0, index + 1).join('/');
            return `<span class="breadcrumb-item" data-path="${path}">${part}</span>`;
        });

        this.breadcrumb.innerHTML = `
            <span class="breadcrumb-item" data-path="">Home</span>
            ${breadcrumbHtml.join(' / ')}
        `;
    }

    renderFileList(items) {
        this.fileList.innerHTML = items.map(item => this.createFileListItem(item)).join('');
    }

    createFileListItem(item) {
        const icon = item.type === 'directory' ? 'folder' : this.getFileIcon(item.mime_type);
        const gitStatus = item.git_status ? this.getGitStatusIndicator(item.git_status) : '';

        return `
            <div class="file-item ${item.type}"
                 data-path="${item.path}"
                 draggable="true">
                <i class="fas fa-${icon}"></i>
                <span class="file-name">${item.name}</span>
                ${gitStatus}
                <span class="file-meta">
                    ${item.size ? this.formatSize(item.size) : ''}
                    ${item.modified ? this.formatDate(item.modified) : ''}
                </span>
            </div>
        `;
    }

    async loadFilePreview(path) {
        try {
            const response = await fetch(`/api/files/content?path=${encodeURIComponent(path)}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.renderPreview(data.content);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Failed to load file preview:', error);
            // Show error in UI
        }
    }

    renderPreview(content) {
        if (!content) {
            this.preview.innerHTML = '<div class="no-preview">No preview available</div>';
            return;
        }

        if (content.mime_type?.startsWith('image/')) {
            this.preview.innerHTML = `<img src="data:${content.mime_type};base64,${content.content}">`;
        } else if (content.mime_type?.startsWith('text/')) {
            this.preview.innerHTML = `<pre><code>${this.escapeHtml(content.content)}</code></pre>`;
        } else {
            this.preview.innerHTML = '<div class="no-preview">Preview not supported for this file type</div>';
        }
    }

    // Utility methods
    getFileIcon(mimeType) {
        if (!mimeType) return 'file';
        const iconMap = {
            'text/': 'file-alt',
            'image/': 'file-image',
            'application/pdf': 'file-pdf',
            'application/json': 'file-code',
            'application/javascript': 'file-code'
        };

        return Object.entries(iconMap).find(([key]) => mimeType.startsWith(key))?.[1] || 'file';
    }

    getGitStatusIndicator(status) {
        if (!status?.status?.length) return '';

        const statusClass = status.status[0];
        return `<span class="git-status ${statusClass}">${statusClass}</span>`;
    }

    formatSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }

    formatDate(isoDate) {
        return new Date(isoDate).toLocaleString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Drag and drop handlers
    handleDragStart(e) {
        const fileItem = e.target.closest('.file-item');
        if (fileItem) {
            e.dataTransfer.setData('text/plain', fileItem.dataset.path);
            e.dataTransfer.effectAllowed = 'move';
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        const target = e.target.closest('.file-item');
        if (target?.classList.contains('directory')) {
            e.dataTransfer.dropEffect = 'move';
        }
    }

    handleDrop(e) {
        e.preventDefault();
        const target = e.target.closest('.file-item');
        if (!target?.classList.contains('directory')) return;

        const sourcePath = e.dataTransfer.getData('text/plain');
        const targetPath = target.dataset.path;

        // Implement file move operation
        console.log(`Move ${sourcePath} to ${targetPath}`);
    }
}
