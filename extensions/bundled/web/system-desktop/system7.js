/**
 * System 7 JavaScript Framework
 * Classic Macintosh System 7 interface functionality for modern web
 * Version 1.0.0
 */

class System7 {
    constructor() {
        this.windows = new Map();
        this.windowZIndex = 1000;
        this.activeWindow = null;
        this.menuBar = null;
        this.desktop = null;
        this.dragState = null;
        this.init();
    }

    /**
     * Initialize the System 7 interface
     */
    init() {
        this.createDesktop();
        this.createMenuBar();
        this.bindEvents();
        console.log('System 7 interface initialized');
    }

    /**
     * Create the desktop environment
     */
    createDesktop() {
        this.desktop = document.createElement('div');
        this.desktop.className = 'sys7-desktop';
        document.body.appendChild(this.desktop);
    }

    /**
     * Create the menu bar
     */
    createMenuBar() {
        this.menuBar = document.createElement('div');
        this.menuBar.className = 'sys7-menubar';

        // Apple menu
        const appleMenu = document.createElement('div');
        appleMenu.className = 'sys7-apple-menu';
        appleMenu.title = 'Apple Menu';

        // Menu items
        const menuItems = ['File', 'Edit', 'View', 'Special', 'Help'];
        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.className = 'sys7-menu-item';
            menuItem.textContent = item;
            menuItem.addEventListener('click', () => this.showMenu(item));
            this.menuBar.appendChild(menuItem);
        });

        this.menuBar.insertBefore(appleMenu, this.menuBar.firstChild);
        document.body.appendChild(this.menuBar);
    }

    /**
     * Create a new window
     */
    createWindow(options = {}) {
        const windowId = options.id || `window-${Date.now()}`;
        const window = document.createElement('div');
        window.className = 'sys7-window';
        window.id = windowId;

        // Set position and size
        window.style.left = (options.x || 100) + 'px';
        window.style.top = (options.y || 100) + 'px';
        window.style.width = (options.width || 400) + 'px';
        window.style.height = (options.height || 300) + 'px';
        window.style.zIndex = ++this.windowZIndex;

        // Title bar
        const titleBar = document.createElement('div');
        titleBar.className = 'sys7-window-title-bar';

        // Close box
        const closeBox = document.createElement('div');
        closeBox.className = 'sys7-close-box';
        closeBox.addEventListener('click', () => this.closeWindow(windowId));

        // Title
        const title = document.createElement('div');
        title.className = 'sys7-window-title';
        title.textContent = options.title || 'Untitled';

        // Grow box
        const growBox = document.createElement('div');
        growBox.className = 'sys7-grow-box';

        // Content area
        const content = document.createElement('div');
        content.className = 'sys7-window-content';
        if (options.content) {
            if (typeof options.content === 'string') {
                content.innerHTML = options.content;
            } else {
                content.appendChild(options.content);
            }
        }

        titleBar.appendChild(closeBox);
        titleBar.appendChild(title);
        window.appendChild(titleBar);
        window.appendChild(content);
        window.appendChild(growBox);

        // Make window draggable
        this.makeDraggable(window, titleBar);

        // Make window resizable
        this.makeResizable(window, growBox);

        // Window activation
        window.addEventListener('mousedown', () => this.activateWindow(windowId));

        this.desktop.appendChild(window);
        this.windows.set(windowId, {
            element: window,
            titleBar,
            content,
            options
        });

        this.activateWindow(windowId);
        return windowId;
    }

    /**
     * Close a window
     */
    closeWindow(windowId) {
        const windowData = this.windows.get(windowId);
        if (windowData) {
            windowData.element.remove();
            this.windows.delete(windowId);

            if (this.activeWindow === windowId) {
                // Find another window to activate
                const remainingWindows = Array.from(this.windows.keys());
                this.activeWindow = remainingWindows.length > 0 ? remainingWindows[0] : null;
            }
        }
    }

    /**
     * Activate a window
     */
    activateWindow(windowId) {
        // Deactivate current window
        if (this.activeWindow) {
            const currentWindow = this.windows.get(this.activeWindow);
            if (currentWindow) {
                currentWindow.titleBar.style.background = 'var(--sys7-medium-gray)';
                currentWindow.titleBar.style.color = 'var(--sys7-black)';
            }
        }

        // Activate new window
        const windowData = this.windows.get(windowId);
        if (windowData) {
            windowData.element.style.zIndex = ++this.windowZIndex;
            windowData.titleBar.style.background = 'var(--sys7-title-bar)';
            windowData.titleBar.style.color = 'var(--sys7-title-text)';
            this.activeWindow = windowId;
        }
    }

    /**
     * Make an element draggable
     */
    makeDraggable(element, handle) {
        let isDragging = false;
        let dragOffset = { x: 0, y: 0 };

        handle.addEventListener('mousedown', (e) => {
            isDragging = true;
            const rect = element.getBoundingClientRect();
            dragOffset.x = e.clientX - rect.left;
            dragOffset.y = e.clientY - rect.top;

            element.style.cursor = 'move';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const x = e.clientX - dragOffset.x;
            const y = e.clientY - dragOffset.y;

            // Keep window within bounds
            const maxX = window.innerWidth - element.offsetWidth;
            const maxY = window.innerHeight - element.offsetHeight;

            element.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
            element.style.top = Math.max(20, Math.min(y, maxY)) + 'px';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = '';
            }
        });
    }

    /**
     * Make a window resizable
     */
    makeResizable(element, handle) {
        let isResizing = false;

        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const rect = element.getBoundingClientRect();
            const newWidth = e.clientX - rect.left;
            const newHeight = e.clientY - rect.top;

            const minWidth = 200;
            const minHeight = 100;
            const maxWidth = window.innerWidth - rect.left;
            const maxHeight = window.innerHeight - rect.top;

            element.style.width = Math.max(minWidth, Math.min(newWidth, maxWidth)) + 'px';
            element.style.height = Math.max(minHeight, Math.min(newHeight, maxHeight)) + 'px';
        });

        document.addEventListener('mouseup', () => {
            isResizing = false;
        });
    }

    /**
     * Show a menu
     */
    showMenu(menuName) {
        // Remove existing menus
        document.querySelectorAll('.sys7-menu').forEach(menu => menu.remove());

        const menu = document.createElement('div');
        menu.className = 'sys7-menu sys7-fade-in';

        const menuItems = this.getMenuItems(menuName);
        menuItems.forEach(item => {
            if (item === '---') {
                const separator = document.createElement('div');
                separator.className = 'sys7-menu-separator';
                menu.appendChild(separator);
            } else {
                const menuItem = document.createElement('div');
                menuItem.className = 'sys7-menu-item-dropdown';
                menuItem.textContent = item.text || item;

                if (item.disabled) {
                    menuItem.classList.add('disabled');
                } else {
                    menuItem.addEventListener('click', () => {
                        if (item.action) {
                            item.action();
                        } else {
                            this.handleMenuAction(menuName, item.text || item);
                        }
                        menu.remove();
                    });
                }

                menu.appendChild(menuItem);
            }
        });

        // Position menu
        const menuBarRect = this.menuBar.getBoundingClientRect();
        menu.style.left = '20px';
        menu.style.top = menuBarRect.bottom + 'px';

        document.body.appendChild(menu);

        // Close menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeMenu(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenu);
                }
            });
        }, 100);
    }

    /**
     * Get menu items for a specific menu
     */
    getMenuItems(menuName) {
        const menus = {
            'File': [
                { text: 'New', action: () => this.newDocument() },
                { text: 'Open...', action: () => this.openDocument() },
                '---',
                { text: 'Close', action: () => this.closeActiveWindow() },
                { text: 'Save', action: () => this.saveDocument() },
                { text: 'Save As...', action: () => this.saveAsDocument() },
                '---',
                { text: 'Quit', action: () => this.quit() }
            ],
            'Edit': [
                { text: 'Undo', disabled: true },
                '---',
                { text: 'Cut', action: () => this.cut() },
                { text: 'Copy', action: () => this.copy() },
                { text: 'Paste', action: () => this.paste() },
                { text: 'Clear', action: () => this.clear() },
                '---',
                { text: 'Select All', action: () => this.selectAll() }
            ],
            'View': [
                { text: 'by Icon', action: () => this.setViewMode('icon') },
                { text: 'by Name', action: () => this.setViewMode('name') },
                { text: 'by Date', action: () => this.setViewMode('date') },
                { text: 'by Size', action: () => this.setViewMode('size') }
            ],
            'Special': [
                { text: 'Clean Up Desktop', action: () => this.cleanUpDesktop() },
                { text: 'Empty Trash...', action: () => this.emptyTrash() },
                '---',
                { text: 'Restart', action: () => this.restart() },
                { text: 'Shut Down', action: () => this.shutDown() }
            ],
            'Help': [
                { text: 'About System 7...', action: () => this.showAbout() },
                '---',
                { text: 'Help', action: () => this.showHelp() }
            ]
        };

        return menus[menuName] || [];
    }

    /**
     * Handle menu actions
     */
    handleMenuAction(menuName, itemName) {
        console.log(`Menu action: ${menuName} -> ${itemName}`);
    }

    /**
     * Create a button
     */
    createButton(text, onClick, isDefault = false) {
        const button = document.createElement('button');
        button.className = isDefault ? 'sys7-button sys7-button-default' : 'sys7-button';
        button.textContent = text;
        if (onClick) {
            button.addEventListener('click', onClick);
        }
        return button;
    }

    /**
     * Create a text input
     */
    createTextInput(placeholder = '', value = '') {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'sys7-text-input';
        input.placeholder = placeholder;
        input.value = value;
        return input;
    }

    /**
     * Create a checkbox
     */
    createCheckbox(text, checked = false, onChange = null) {
        const label = document.createElement('label');
        label.className = 'sys7-checkbox';

        const input = document.createElement('input');
        input.type = 'checkbox';
        input.checked = checked;
        if (onChange) {
            input.addEventListener('change', onChange);
        }

        const span = document.createElement('span');
        span.textContent = text;

        label.appendChild(input);
        label.appendChild(span);

        return label;
    }

    /**
     * Create a radio button
     */
    createRadio(name, text, value, checked = false, onChange = null) {
        const label = document.createElement('label');
        label.className = 'sys7-radio';

        const input = document.createElement('input');
        input.type = 'radio';
        input.name = name;
        input.value = value;
        input.checked = checked;
        if (onChange) {
            input.addEventListener('change', onChange);
        }

        const span = document.createElement('span');
        span.textContent = text;

        label.appendChild(input);
        label.appendChild(span);

        return label;
    }

    /**
     * Create a list
     */
    createList(items = [], onSelect = null) {
        const list = document.createElement('div');
        list.className = 'sys7-list';

        items.forEach((item, index) => {
            const listItem = document.createElement('div');
            listItem.className = 'sys7-list-item';
            listItem.textContent = typeof item === 'string' ? item : item.text;
            listItem.dataset.value = typeof item === 'string' ? item : item.value;
            listItem.dataset.index = index;

            listItem.addEventListener('click', () => {
                // Remove previous selection
                list.querySelectorAll('.sys7-list-item').forEach(li => {
                    li.classList.remove('selected');
                });

                // Select this item
                listItem.classList.add('selected');

                if (onSelect) {
                    onSelect(listItem.dataset.value, index);
                }
            });

            list.appendChild(listItem);
        });

        return list;
    }

    /**
     * Show a dialog
     */
    showDialog(options = {}) {
        const dialog = document.createElement('div');
        dialog.className = 'sys7-dialog sys7-fade-in';

        if (options.title) {
            const title = document.createElement('div');
            title.className = 'sys7-dialog-title';
            title.textContent = options.title;
            dialog.appendChild(title);
        }

        if (options.content) {
            const content = document.createElement('div');
            content.className = 'sys7-dialog-content';
            if (typeof options.content === 'string') {
                content.innerHTML = options.content;
            } else {
                content.appendChild(options.content);
            }
            dialog.appendChild(content);
        }

        if (options.buttons) {
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'sys7-dialog-buttons';

            options.buttons.forEach(buttonConfig => {
                const button = this.createButton(
                    buttonConfig.text,
                    () => {
                        if (buttonConfig.action) {
                            buttonConfig.action();
                        }
                        dialog.remove();
                    },
                    buttonConfig.default
                );
                buttonContainer.appendChild(button);
            });

            dialog.appendChild(buttonContainer);
        }

        document.body.appendChild(dialog);

        // Focus first button
        const firstButton = dialog.querySelector('.sys7-button');
        if (firstButton) {
            firstButton.focus();
        }

        return dialog;
    }

    /**
     * Show an alert dialog
     */
    alert(message, title = 'Alert') {
        return this.showDialog({
            title: title,
            content: message,
            buttons: [
                { text: 'OK', default: true }
            ]
        });
    }

    /**
     * Show a confirm dialog
     */
    confirm(message, title = 'Confirm', onConfirm = null, onCancel = null) {
        return this.showDialog({
            title: title,
            content: message,
            buttons: [
                {
                    text: 'Cancel',
                    action: onCancel
                },
                {
                    text: 'OK',
                    default: true,
                    action: onConfirm
                }
            ]
        });
    }

    /**
     * Bind global events
     */
    bindEvents() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.metaKey || e.ctrlKey) {
                switch(e.key) {
                    case 'n':
                        e.preventDefault();
                        this.newDocument();
                        break;
                    case 'o':
                        e.preventDefault();
                        this.openDocument();
                        break;
                    case 's':
                        e.preventDefault();
                        this.saveDocument();
                        break;
                    case 'w':
                        e.preventDefault();
                        this.closeActiveWindow();
                        break;
                    case 'q':
                        e.preventDefault();
                        this.quit();
                        break;
                }
            }
        });
    }

    // Menu action implementations
    newDocument() {
        this.createWindow({
            title: 'Untitled',
            content: '<p>New document content...</p>',
            width: 500,
            height: 400
        });
    }

    openDocument() {
        this.alert('Open document functionality not implemented yet.');
    }

    closeActiveWindow() {
        if (this.activeWindow) {
            this.closeWindow(this.activeWindow);
        }
    }

    saveDocument() {
        this.alert('Save functionality not implemented yet.');
    }

    saveAsDocument() {
        this.alert('Save As functionality not implemented yet.');
    }

    quit() {
        this.confirm(
            'Are you sure you want to quit?',
            'Quit Application',
            () => {
                // Close all windows
                this.windows.clear();
                document.body.innerHTML = '';
                this.init();
            }
        );
    }

    cut() { this.alert('Cut functionality not implemented yet.'); }
    copy() { this.alert('Copy functionality not implemented yet.'); }
    paste() { this.alert('Paste functionality not implemented yet.'); }
    clear() { this.alert('Clear functionality not implemented yet.'); }
    selectAll() { this.alert('Select All functionality not implemented yet.'); }

    setViewMode(mode) {
        this.alert(`View mode changed to: ${mode}`);
    }

    cleanUpDesktop() {
        this.alert('Desktop cleaned up.');
    }

    emptyTrash() {
        this.confirm(
            'Are you sure you want to permanently remove the items in the Trash?',
            'Empty Trash',
            () => this.alert('Trash emptied.')
        );
    }

    restart() {
        this.confirm(
            'Are you sure you want to restart?',
            'Restart',
            () => location.reload()
        );
    }

    shutDown() {
        this.confirm(
            'Are you sure you want to shut down?',
            'Shut Down',
            () => window.close()
        );
    }

    showAbout() {
        this.showDialog({
            title: 'About System 7',
            content: `
                <div style="text-align: center;">
                    <div style="font-weight: bold; margin-bottom: 8px;">System 7 Web Framework</div>
                    <div>Version 1.0.0</div>
                    <div style="margin-top: 16px;">A classic Macintosh interface for the modern web.</div>
                </div>
            `,
            buttons: [
                { text: 'OK', default: true }
            ]
        });
    }

    showHelp() {
        const helpContent = document.createElement('div');
        helpContent.innerHTML = `
            <h3>System 7 Help</h3>
            <p><strong>Keyboard Shortcuts:</strong></p>
            <ul style="margin-left: 20px;">
                <li>Cmd/Ctrl+N - New Document</li>
                <li>Cmd/Ctrl+O - Open Document</li>
                <li>Cmd/Ctrl+S - Save Document</li>
                <li>Cmd/Ctrl+W - Close Window</li>
                <li>Cmd/Ctrl+Q - Quit</li>
            </ul>
            <p><strong>Mouse Actions:</strong></p>
            <ul style="margin-left: 20px;">
                <li>Drag title bar to move window</li>
                <li>Drag grow box to resize window</li>
                <li>Click close box to close window</li>
            </ul>
        `;

        this.createWindow({
            title: 'Help',
            content: helpContent,
            width: 400,
            height: 350
        });
    }
}

// Auto-initialize System 7 when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.system7 = new System7();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = System7;
}
