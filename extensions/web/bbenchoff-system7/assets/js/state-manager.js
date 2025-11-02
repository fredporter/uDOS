// State management for System 7 interface
const StateManager = {
    STATE_KEY: 'system7State',
    AUTO_SAVE_INTERVAL: 5000,

    saveState() {
        const windows = Array.from(document.querySelectorAll('.window')).map(window => ({
            title: window.querySelector('.window-title').textContent,
            content: window.querySelector('.window-content').innerHTML,
            position: {
                left: window.style.left,
                top: window.style.top,
                width: window.style.width,
                height: window.style.height,
                zIndex: window.style.zIndex
            },
            isActive: !window.querySelector('.window-titlebar').classList.contains('inactive'),
            type: window.classList.contains('folder-window') ? 'folder' :
                  window.classList.contains('calculator-window') ? 'calculator' : 'document'
        }));

        const state = {
            windows,
            desktop: {
                background: document.getElementById('desktop').style.background || ''
            },
            menuState: {
                activeApp: document.querySelector('#current-app-name')?.textContent || 'Finder'
            },
            settings: {
                soundEnabled: localStorage.getItem('soundEnabled') !== 'false'
            },
            timestamp: Date.now()
        };

        try {
            localStorage.setItem(this.STATE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('Could not save state to localStorage:', e);
        }
    },

    loadState() {
        try {
            const savedState = localStorage.getItem(this.STATE_KEY);
            if (!savedState) return;

            const state = JSON.parse(savedState);

            // Don't load states older than 24 hours
            if (Date.now() - state.timestamp > 24 * 60 * 60 * 1000) {
                localStorage.removeItem(this.STATE_KEY);
                return;
            }

            // Restore desktop background
            if (state.desktop && state.desktop.background) {
                const desktop = document.getElementById('desktop');
                if (desktop) {
                    desktop.style.background = state.desktop.background;

                    // Update view menu checkmark
                    const backgroundName = this.getBackgroundNameFromStyle(state.desktop.background);
                    if (backgroundName) {
                        this.updateBackgroundMenuCheckmark(backgroundName);
                    }
                }
            }

            // Restore windows
            if (state.windows && state.windows.length > 0) {
                state.windows.forEach((windowState, index) => {
                    setTimeout(() => {
                        const window = new Window(
                            windowState.title,
                            windowState.content,
                            windowState.type,
                            parseInt(windowState.position.left) || 50,
                            parseInt(windowState.position.top) || 80
                        );

                        // Restore window properties
                        if (windowState.position.width) {
                            window.element.style.width = windowState.position.width;
                        }
                        if (windowState.position.height) {
                            window.element.style.height = windowState.position.height;
                        }
                        if (windowState.position.zIndex) {
                            window.element.style.zIndex = windowState.position.zIndex;
                        }

                        // Set active state
                        const titlebar = window.element.querySelector('.window-titlebar');
                        if (windowState.isActive) {
                            titlebar.classList.remove('inactive');
                            titlebar.style.background = 'var(--system7-titlebar-active)';
                        } else {
                            titlebar.classList.add('inactive');
                            titlebar.style.background = 'var(--system7-titlebar-inactive)';
                        }
                    }, index * 100); // Stagger window creation
                });
            }

            // Restore settings
            if (state.settings) {
                localStorage.setItem('soundEnabled', state.settings.soundEnabled);
                this.updateSoundMenuCheck(state.settings.soundEnabled);
            }

        } catch (e) {
            console.warn('Could not load state from localStorage:', e);
            localStorage.removeItem(this.STATE_KEY);
        }
    },

    getBackgroundNameFromStyle(backgroundStyle) {
        if (backgroundStyle.includes('MacOS.jpg')) return 'MacOS';
        if (backgroundStyle.includes('cats.png')) return 'cats';
        if (backgroundStyle.includes('circuits.png')) return 'circuits';
        if (backgroundStyle.includes('grass.png')) return 'grass';
        if (backgroundStyle.includes('pebbles.png')) return 'pebbles';
        if (backgroundStyle.includes('plaid.png')) return 'plaid';
        return 'MacOS'; // default
    },

    updateBackgroundMenuCheckmark(backgroundName) {
        const viewMenuItems = document.querySelectorAll('#view-menu .dropdown-item');
        viewMenuItems.forEach(item => {
            const text = item.textContent.replace('✔ ', '');
            if (text === backgroundName) {
                item.textContent = `✔ ${text}`;
            } else {
                item.textContent = text;
            }
        });
    },

    updateSoundMenuCheck(enabled) {
        const soundMenuItem = document.querySelector('#apple-menu .dropdown-item[onclick*="toggleSound"]');
        if (soundMenuItem) {
            soundMenuItem.textContent = enabled ? '✔ Sound' : 'Sound';
        }
    },

    startAutoSave() {
        setInterval(() => {
            this.saveState();
        }, this.AUTO_SAVE_INTERVAL);
    },

    clearState() {
        localStorage.removeItem(this.STATE_KEY);
        location.reload();
    }
};

// Initialize state management when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    StateManager.loadState();
    StateManager.startAutoSave();
});
