// Window Management System for System 7 Recreation
class Window {
    constructor(title, content, type = 'document', x = 20, y = 50) {
        this.id = 'window_' + Math.random().toString(36).substr(2, 9);
        this.title = title;
        this.type = type;
        this.isActive = true;

        this.element = document.createElement('div');
        this.element.className = 'window';
        this.element.id = this.id;

        if (type === 'folder') {
            this.element.classList.add('folder-window');
        }
        if (type === 'calculator') {
            this.element.classList.add('calculator-window');
        }

        this.element.innerHTML = `
            <div class="window-titlebar">
                <div class="window-close"></div>
                <div class="window-title">${title}</div>
            </div>
            <div class="window-content">${content}</div>
            <div class="window-resizer"></div>
        `;

        // Position the window
        this.element.style.left = x + 'px';
        this.element.style.top = y + 'px';

        // Add to desktop
        document.getElementById('desktop').appendChild(this.element);

        // Make functional
        this.makeDraggable();
        this.makeCloseable();
        this.makeActivatable();
        this.makeResizable();
        this.bringToFront();

        // Update menu system
        if (typeof MenuManager !== 'undefined') {
            MenuManager.updateApplicationMenu();
        }
    }

    makeDraggable() {
        const titlebar = this.element.querySelector('.window-titlebar');
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;

        titlebar.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('window-close')) return;

            isDragging = true;
            initialX = e.clientX - this.element.offsetLeft;
            initialY = e.clientY - this.element.offsetTop;

            this.bringToFront();
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;

                this.element.style.left = currentX + 'px';
                this.element.style.top = Math.max(22, currentY) + 'px'; // Don't go above menubar
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }

    makeCloseable() {
        const closeButton = this.element.querySelector('.window-close');
        closeButton.addEventListener('click', () => {
            this.close();
        });
    }

    makeActivatable() {
        this.element.addEventListener('mousedown', () => {
            this.bringToFront();
        });
    }

    makeResizable() {
        if (this.type === 'calculator') return; // Calculator shouldn't be resizable

        const resizer = this.element.querySelector('.window-resizer');
        let isResizing = false;

        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const rect = this.element.getBoundingClientRect();
            const newWidth = e.clientX - rect.left;
            const newHeight = e.clientY - rect.top;

            if (newWidth > 200) {
                this.element.style.width = newWidth + 'px';
            }
            if (newHeight > 100) {
                this.element.style.height = newHeight + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            isResizing = false;
        });
    }

    bringToFront() {
        // Deactivate all windows
        document.querySelectorAll('.window').forEach(win => {
            const titlebar = win.querySelector('.window-titlebar');
            titlebar.classList.add('inactive');
            titlebar.style.background = 'var(--system7-titlebar-inactive)';
        });

        // Activate this window
        const titlebar = this.element.querySelector('.window-titlebar');
        titlebar.classList.remove('inactive');
        titlebar.style.background = 'var(--system7-titlebar-active)';

        // Bring to front
        const highestZ = Math.max(
            ...Array.from(document.querySelectorAll('.window')).map(w =>
                parseInt(w.style.zIndex) || 100
            )
        );
        this.element.style.zIndex = highestZ + 1;
        this.isActive = true;

        // Update menu system
        if (typeof MenuManager !== 'undefined') {
            MenuManager.updateApplicationMenu();
        }
    }

    close() {
        this.element.remove();

        // Update menu system
        if (typeof MenuManager !== 'undefined') {
            MenuManager.updateApplicationMenu();
        }

        // Save state
        if (typeof StateManager !== 'undefined') {
            StateManager.saveState();
        }
    }

    getInfo() {
        return {
            id: this.id,
            title: this.title,
            type: this.type,
            isActive: this.isActive,
            element: this.element
        };
    }
}

// Utility functions for opening pages/documents
function openPage(pageName) {
    const pageContent = {
        'uDOS-Main': {
            title: 'uDOS Main System',
            content: `
                <h2>uDOS v1.0.10</h2>
                <p>Universal Development Operating System</p>
                <ul>
                    <li>Typography System: 15+ retro fonts</li>
                    <li>Advanced Dashboard: Multi-framework interface</li>
                    <li>Web Extensions: C64, Teletext, System 7</li>
                    <li>Command System: Interactive terminals</li>
                    <li>Configuration Manager: JSON-based settings</li>
                </ul>
                <p><strong>Status:</strong> Active Development</p>
                <p><strong>Version:</strong> 1.0.10 (System 7 Integration)</p>
            `
        },
        'Advanced-Dashboard': {
            title: 'Advanced Dashboard',
            content: `
                <h2>uDOS Advanced Dashboard</h2>
                <p>Multi-theme retro interface combining:</p>
                <ul>
                    <li><strong>C64 CSS3:</strong> Commodore 64 styling</li>
                    <li><strong>Teletext:</strong> BBC MODE7 visualization</li>
                    <li><strong>System 7:</strong> Classic Mac interface</li>
                    <li><strong>Modern:</strong> Contemporary dark theme</li>
                </ul>
                <p>Features real-time monitoring, interactive modules, and seamless theme switching.</p>
                <button onclick="window.open('../advanced-dashboard/', '_blank')" style="margin-top: 10px; padding: 5px 10px;">Open Dashboard</button>
            `
        },
        'Typography-System': {
            title: 'Typography System',
            content: `
                <h2>uDOS Typography System</h2>
                <p>Complete retro computing font collection:</p>
                <ul>
                    <li><strong>Chicago:</strong> Classic Mac system font</li>
                    <li><strong>Geneva:</strong> Mac interface font</li>
                    <li><strong>Monaco:</strong> Mac monospace font</li>
                    <li><strong>C64_Pro:</strong> Commodore 64 pixel font</li>
                    <li><strong>MODE7:</strong> BBC Teletext font</li>
                    <li><strong>And 10+ more...</strong></li>
                </ul>
                <p>Themed configurations for authentic retro computing experiences.</p>
            `
        },
        'Web-Extensions': {
            title: 'Web Extensions',
            content: `
                <h2>uDOS Web Extensions</h2>
                <p>Modular web interface components:</p>
                <ul>
                    <li><strong>C64 CSS3:</strong> Authentic Commodore styling</li>
                    <li><strong>Teletext Framework:</strong> BBC data visualization</li>
                    <li><strong>System 7 CSS:</strong> Classic Mac interface (this!)</li>
                    <li><strong>BBenchoff System 7:</strong> Original implementation</li>
                    <li><strong>Advanced Dashboard:</strong> Multi-framework hub</li>
                </ul>
                <p>Each extension provides authentic retro computing aesthetics.</p>
            `
        },
        'System-Info': {
            title: 'System Information',
            content: `
                <h2>System Information</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><strong>System:</strong></td><td>uDOS v1.0.10</td></tr>
                    <tr><td><strong>Interface:</strong></td><td>BBenchoff System 7 Recreation</td></tr>
                    <tr><td><strong>Engine:</strong></td><td>Web Browser</td></tr>
                    <tr><td><strong>Memory:</strong></td><td>8 MB (Virtual)</td></tr>
                    <tr><td><strong>Extensions:</strong></td><td>Multiple Loaded</td></tr>
                    <tr><td><strong>Theme:</strong></td><td>Classic Macintosh</td></tr>
                </table>
                <p style="margin-top: 20px;"><em>This is a faithful recreation of the classic Macintosh System 7 interface, adapted for the uDOS project.</em></p>
            `
        }
    };

    const page = pageContent[pageName];
    if (page) {
        new Window(page.title, page.content, 'document', 50 + Math.random() * 100, 80 + Math.random() * 100);
    }
}

// Handle double-click events for desktop icons
function handleDoubleClick(itemName) {
    // This will be implemented when we add the filesystem
    console.log('Double-clicked:', itemName);
}
