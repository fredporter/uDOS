// Initialize the System7 interface
document.addEventListener('DOMContentLoaded', () => {
    initializeSystem();
    initializeEventListeners();
    checkUrlParameters();
});

function initializeSystem() {
    initializeClock();
    initializeDesktop();
    if (typeof MenuManager !== 'undefined') {
        MenuManager.init();
    }
}

function checkUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    if (page) {
        openPage(page);
    }
}

// Clock functionality
function initializeClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.textContent = `${hours}:${minutes}`;
    }
}

// Background Management
function setBackground(image) {
    const desktop = document.getElementById('desktop');
    const viewMenuItems = document.querySelectorAll('#view-menu .dropdown-item');

    // Remove checkmarks from all items
    viewMenuItems.forEach(item => {
        item.textContent = item.textContent.replace('✔ ', '');
    });

    const backgrounds = {
        MacOS: { url: 'MacOS.jpg', repeat: 'no-repeat center center fixed', size: 'cover' },
        cats: { url: 'cats.png', repeat: 'repeat', size: 'auto' },
        circuits: { url: 'circuits.png', repeat: 'repeat', size: 'auto' },
        grass: { url: 'grass.png', repeat: 'repeat', size: 'auto' },
        pebbles: { url: 'pebbles.png', repeat: 'repeat', size: 'auto' },
        plaid: { url: 'plaid.png', repeat: 'repeat', size: 'auto' }
    };

    const bg = backgrounds[image];
    if (bg) {
        desktop.style.background = `url('assets/images/backgrounds/${bg.url}') ${bg.repeat}`;
        desktop.style.backgroundSize = bg.size;

        // Add checkmark to selected item
        viewMenuItems.forEach(item => {
            if (item.textContent.trim() === image) {
                item.textContent = `✔ ${image}`;
            }
        });

        // Save state after background change
        if (typeof StateManager !== 'undefined') {
            StateManager.saveState();
        }
    }
}

// About Window
function showAboutWindow() {
    const content = `
        <div style="display: flex; align-items: center; padding: 20px;">
            <img src="assets/images/system7-icon.png" alt="System 7" style="width: 64px; height: 64px; margin-right: 20px;">
            <div>
                <h3 style="margin: 0 0 10px 0;">uDOS System 7 Interface</h3>
                <p style="margin: 5px 0;">Based on Brian Benchoff's System 7 Recreation</p>
                <p style="margin: 5px 0;">Adapted for the uDOS Project</p>
                <p style="margin: 15px 0 5px 0; font-size: 12px; color: #666;">
                    This is a faithful recreation of the classic Macintosh System 7 interface,
                    built with CSS and JavaScript for modern browsers.
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    Original implementation by Brian Benchoff<br>
                    uDOS integration by the uDOS Team
                </p>
            </div>
        </div>
    `;

    const aboutWindow = new Window(
        'About This System',
        content,
        'about',
        window.innerWidth / 2 - 250,
        window.innerHeight / 2 - 150
    );

    // Configure the about window
    aboutWindow.element.style.resize = 'none';
    aboutWindow.element.style.width = '500px';
    aboutWindow.element.style.height = '250px';

    // Remove resize handle
    aboutWindow.element.querySelector('.window-resizer')?.remove();
    aboutWindow.element.querySelector('.window-content').style.overflow = 'hidden';

    // Play sound if available
    if (typeof SoundManager !== 'undefined') {
        SoundManager.play('click');
    }
}

// Sound Management
function toggleSound() {
    const enabled = localStorage.getItem('soundEnabled') !== 'false';
    localStorage.setItem('soundEnabled', !enabled);

    if (typeof SoundManager !== 'undefined') {
        SoundManager.setVolume(!enabled ? 0.5 : 0);
    }

    // Update menu checkmark
    if (typeof StateManager !== 'undefined') {
        StateManager.updateSoundMenuCheck(!enabled);
    }
}

// Theme Toggle
function toggleTheme() {
    window.location.href = '../advanced-dashboard/';
}

// Initialize desktop and event listeners
function initializeEventListeners() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Global shortcuts
        if (e.metaKey || e.ctrlKey) {
            switch(e.key) {
                case 'n':
                    e.preventDefault();
                    // New window/document
                    break;
                case 'o':
                    e.preventDefault();
                    // Open document
                    break;
                case 's':
                    e.preventDefault();
                    // Save document
                    break;
                case 'q':
                    e.preventDefault();
                    // Quit application
                    break;
            }
        }

        // Function keys
        switch(e.key) {
            case 'F1':
                e.preventDefault();
                showAboutWindow();
                break;
        }
    });

    // Prevent right-click context menu for authentic Mac feel
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        // Adjust window positions if they're off-screen
        document.querySelectorAll('.window').forEach(window => {
            const rect = window.getBoundingClientRect();
            if (rect.left > window.innerWidth - 100) {
                window.style.left = (window.innerWidth - 200) + 'px';
            }
            if (rect.top > window.innerHeight - 50) {
                window.style.top = '50px';
            }
        });
    });
}

// Utility functions
function createNewDocument() {
    const content = `
        <div style="padding: 20px;">
            <h2>New Document</h2>
            <p>This would be a text editor or document viewer in a real System 7 implementation.</p>
            <textarea style="width: 100%; height: 200px; font-family: Monaco, monospace; font-size: 12px; border: 1px inset #ccc; padding: 5px;" placeholder="Enter your text here..."></textarea>
        </div>
    `;

    new Window('Untitled', content, 'document', 100 + Math.random() * 200, 80 + Math.random() * 100);
}

function openSystemInformation() {
    const content = `
        <div style="padding: 20px;">
            <h2>System Information</h2>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="border-bottom: 1px solid #ccc;">
                    <td style="padding: 5px; font-weight: bold;">System:</td>
                    <td style="padding: 5px;">uDOS System 7 Interface</td>
                </tr>
                <tr style="border-bottom: 1px solid #ccc;">
                    <td style="padding: 5px; font-weight: bold;">Version:</td>
                    <td style="padding: 5px;">1.0 (Based on Brian Benchoff's Recreation)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ccc;">
                    <td style="padding: 5px; font-weight: bold;">Memory:</td>
                    <td style="padding: 5px;">8 MB (Virtual)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ccc;">
                    <td style="padding: 5px; font-weight: bold;">Engine:</td>
                    <td style="padding: 5px;">Modern Web Browser</td>
                </tr>
                <tr>
                    <td style="padding: 5px; font-weight: bold;">Built:</td>
                    <td style="padding: 5px;">November 2024</td>
                </tr>
            </table>
        </div>
    `;

    new Window('System Information', content, 'document', 120, 90);
}

// Desktop interaction
function handleDesktopClick(e) {
    if (e.target === document.getElementById('desktop')) {
        // Deselect all icons
        document.querySelectorAll('.desktop-icon').forEach(icon => {
            icon.classList.remove('selected');
        });
    }
}

// Add desktop click handler
document.addEventListener('DOMContentLoaded', () => {
    const desktop = document.getElementById('desktop');
    if (desktop) {
        desktop.addEventListener('click', handleDesktopClick);
    }
});
