// Menu System Management for System 7 Interface
const MenuManager = {
    init() {
        this.initializeMenuListeners();
        this.updateApplicationMenu();
        this.addMenuStyles();
    },

    hideProgram(programName) {
        const windows = this.getWindowsByProgram(programName);
        windows.forEach(window => {
            window.style.display = 'none';
        });
        this.updateApplicationMenu();
    },

    hideOthers() {
        const activeProgram = this.getActiveProgram();
        const allPrograms = this.getOpenPrograms();

        allPrograms.forEach(program => {
            if (program.name !== activeProgram) {
                this.hideProgram(program.name);
            }
        });
    },

    showAll() {
        document.querySelectorAll('.window').forEach(window => {
            window.style.display = 'block';
        });
        this.updateApplicationMenu();
    },

    initializeMenuListeners() {
        // Menu bar click handlers
        document.querySelectorAll('.menubar-item[data-menu]').forEach(item => {
            item.addEventListener('click', (e) => {
                const menuId = item.dataset.menu + '-menu';
                const menu = document.getElementById(menuId);

                if (menu) {
                    this.closeAllMenus();
                    this.showMenu(menu, item);
                }
            });
        });

        // Close menus when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.menubar-item') && !e.target.closest('.dropdown-menu')) {
                this.closeAllMenus();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.metaKey || e.ctrlKey) {
                switch(e.key) {
                    case 'w':
                        e.preventDefault();
                        this.closeActiveWindow();
                        break;
                    case 'h':
                        e.preventDefault();
                        if (e.altKey) {
                            this.hideOthers();
                        } else {
                            const activeProgram = this.getActiveProgram();
                            if (activeProgram) {
                                this.hideProgram(activeProgram);
                            }
                        }
                        break;
                }
            }
        });
    },

    showMenu(menu, trigger) {
        const rect = trigger.getBoundingClientRect();
        menu.style.display = 'block';
        menu.style.left = rect.left + 'px';
        menu.style.top = rect.bottom + 'px';
    },

    closeAllMenus() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
    },

    getOpenPrograms() {
        const windows = Array.from(document.querySelectorAll('.window'));
        const programs = new Map();

        windows.forEach(window => {
            const title = window.querySelector('.window-title').textContent;
            const isHidden = window.style.display === 'none';
            const isActive = !window.querySelector('.window-titlebar').classList.contains('inactive');

            if (!programs.has(title)) {
                programs.set(title, {
                    name: title,
                    icon: 'document-icon.png',
                    hidden: isHidden,
                    active: isActive,
                    windows: []
                });
            }

            programs.get(title).windows.push(window);
        });

        return Array.from(programs.values());
    },

    updateApplicationMenu() {
        const programs = this.getOpenPrograms();
        const menu = document.getElementById('application-menu');

        if (!menu) return;

        let menuHTML = '';

        // Add Finder first (always present)
        menuHTML += `
            <div class="dropdown-item" onclick="MenuManager.switchToProgram('Finder')">
                <span style="width: 16px; text-align: center;">
                    ${programs.length === 0 ? '✓' : ''}
                </span>
                <img src="assets/images/finder-icon.png" class="menu-icon">
                <span>Finder</span>
            </div>
        `;

        if (programs.length > 0) {
            menuHTML += '<div class="dropdown-divider"></div>';
        }

        programs.forEach(program => {
            const checkmark = program.active ? '✓' : '';
            const hiddenClass = program.hidden ? 'hidden-program' : '';

            menuHTML += `
                <div class="dropdown-item ${hiddenClass}" onclick="MenuManager.switchToProgram('${program.name}')">
                    <span style="width: 16px; text-align: center;">${checkmark}</span>
                    <img src="assets/images/${program.icon}" class="menu-icon">
                    <span>${program.name}</span>
                </div>
            `;
        });

        if (programs.length > 0) {
            menuHTML += '<div class="dropdown-divider"></div>';
            menuHTML += `
                <div class="dropdown-item" onclick="MenuManager.hideOthers()">Hide Others</div>
                <div class="dropdown-item" onclick="MenuManager.showAll()">Show All</div>
            `;
        }

        menu.innerHTML = menuHTML;

        // Update current app display
        const activeProgram = this.getActiveProgram() || 'Finder';
        const appIcon = document.getElementById('current-app-icon');
        const appName = document.getElementById('current-app-name');

        if (appIcon && appName) {
            appName.textContent = activeProgram;
            if (activeProgram === 'Finder') {
                appIcon.src = 'assets/images/finder-icon.png';
            } else {
                appIcon.src = 'assets/images/document-icon.png';
            }
        }
    },

    switchToProgram(programName) {
        if (programName === 'Finder') {
            // Deactivate all windows
            document.querySelectorAll('.window').forEach(window => {
                const titlebar = window.querySelector('.window-titlebar');
                titlebar.classList.add('inactive');
                titlebar.style.background = 'var(--system7-titlebar-inactive)';
            });
        } else {
            // Show and activate program windows
            const windows = this.getWindowsByProgram(programName);
            windows.forEach(window => {
                window.style.display = 'block';
                const titlebar = window.querySelector('.window-titlebar');
                titlebar.classList.remove('inactive');
                titlebar.style.background = 'var(--system7-titlebar-active)';
            });

            // Bring the most recent window to front
            if (windows.length > 0) {
                const highestZ = this.getHighestZIndex();
                windows[0].style.zIndex = highestZ + 1;
            }
        }

        this.updateApplicationMenu();
        this.closeAllMenus();
    },

    getWindowsByProgram(programName) {
        return Array.from(document.querySelectorAll('.window')).filter(window => {
            const title = window.querySelector('.window-title').textContent;
            return title === programName;
        });
    },

    getHighestZIndex() {
        return Math.max(
            ...Array.from(document.querySelectorAll('.window')).map(w =>
                parseInt(w.style.zIndex) || 100
            )
        );
    },

    closeActiveWindow() {
        const activeWindow = this.getActiveWindow();
        if (activeWindow) {
            activeWindow.remove();
            this.updateApplicationMenu();
        }
    },

    getActiveWindow() {
        return document.querySelector('.window .window-titlebar:not(.inactive)')?.closest('.window');
    },

    getActiveProgram() {
        const activeWindow = this.getActiveWindow();
        if (activeWindow) {
            return activeWindow.querySelector('.window-title').textContent;
        }
        return null;
    },

    addMenuStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .dropdown-item {
                display: flex;
                align-items: center;
                gap: 5px;
                padding: 2px 10px;
                cursor: default;
                white-space: nowrap;
            }

            .dropdown-item.disabled {
                color: #808080;
                cursor: default;
            }

            .dropdown-item.hidden-program {
                color: #808080;
            }

            .menu-icon {
                width: 16px;
                height: 16px;
                object-fit: contain;
            }

            .dropdown-divider {
                height: 1px;
                background: var(--system7-border);
                margin: 2px 0;
            }

            .window.hidden {
                display: none;
            }
        `;
        document.head.appendChild(style);
    }
};

// Initialize menu system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    MenuManager.init();
});
