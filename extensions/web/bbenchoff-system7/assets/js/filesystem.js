// File System Structure for uDOS System 7 Interface
const fileSystem = {
    'Macintosh HD': {
        type: 'folder',
        icon: 'hd-icon.png',
        contents: {
            'uDOS': {
                type: 'folder',
                icon: 'folder-icon.png',
                contents: {
                    'Advanced Dashboard': {
                        type: 'document',
                        icon: 'dashboard-icon.png',
                        file: 'Advanced-Dashboard'
                    },
                    'Typography System': {
                        type: 'document',
                        icon: 'font-icon.png',
                        file: 'Typography-System'
                    },
                    'Web Extensions': {
                        type: 'folder',
                        icon: 'folder-icon.png',
                        contents: {
                            'C64 CSS3': {
                                type: 'document',
                                icon: 'c64-icon.png',
                                file: 'C64-CSS3'
                            },
                            'Teletext Framework': {
                                type: 'document',
                                icon: 'teletext-icon.png',
                                file: 'Teletext-Framework'
                            },
                            'System 7 CSS': {
                                type: 'document',
                                icon: 'system7-icon.png',
                                file: 'System7-CSS'
                            }
                        }
                    },
                    'Configuration': {
                        type: 'document',
                        icon: 'config-icon.png',
                        file: 'Config-Manager'
                    },
                    'Terminal': {
                        type: 'document',
                        icon: 'terminal-icon.png',
                        file: 'Terminal'
                    }
                }
            },
            'System Folder': {
                type: 'folder',
                icon: 'system-folder-icon.png',
                contents: {
                    'Finder': {
                        type: 'application',
                        icon: 'finder-icon.png',
                        file: 'Finder'
                    },
                    'Extensions': {
                        type: 'folder',
                        icon: 'folder-icon.png',
                        contents: {}
                    },
                    'Control Panels': {
                        type: 'folder',
                        icon: 'folder-icon.png',
                        contents: {}
                    }
                }
            },
            'Applications': {
                type: 'folder',
                icon: 'applications-icon.png',
                contents: {
                    'Calculator': {
                        type: 'application',
                        icon: 'calculator-icon.png',
                        file: 'Calculator'
                    },
                    'Text Editor': {
                        type: 'application',
                        icon: 'textedit-icon.png',
                        file: 'TextEditor'
                    }
                }
            },
            'Documents': {
                type: 'folder',
                icon: 'documents-icon.png',
                contents: {
                    'README': {
                        type: 'document',
                        icon: 'document-icon.png',
                        file: 'README'
                    },
                    'System Info': {
                        type: 'document',
                        icon: 'document-icon.png',
                        file: 'System-Info'
                    }
                }
            }
        }
    }
};

// Desktop icons (what appears on the desktop)
const desktopIcons = [
    {
        name: 'Macintosh HD',
        icon: 'hd-icon.png',
        type: 'folder',
        x: 20,
        y: 50
    },
    {
        name: 'uDOS',
        icon: 'folder-icon.png',
        type: 'alias',
        x: 20,
        y: 150,
        target: 'uDOS'
    },
    {
        name: 'Trash',
        icon: 'trash-icon.png',
        type: 'special',
        x: 20,
        y: 250
    }
];

// Initialize desktop icons
function initializeDesktop() {
    const desktop = document.getElementById('desktop');

    desktopIcons.forEach(iconData => {
        const icon = createDesktopIcon(iconData);
        desktop.appendChild(icon);
    });
}

// Create a desktop icon element
function createDesktopIcon(iconData) {
    const icon = document.createElement('div');
    icon.className = 'desktop-icon';
    if (iconData.type === 'alias') {
        icon.classList.add('alias');
    }

    icon.style.right = iconData.x + 'px';
    icon.style.top = iconData.y + 'px';

    icon.innerHTML = `
        <img src="assets/images/${iconData.icon}" alt="${iconData.name}">
        <div class="desktop-icon-label">${iconData.name}</div>
    `;

    // Add click handlers
    icon.addEventListener('click', () => handleIconClick(iconData));
    icon.addEventListener('dblclick', () => handleIconDoubleClick(iconData));

    return icon;
}

// Handle icon click
function handleIconClick(iconData) {
    // Select the icon (visual feedback)
    document.querySelectorAll('.desktop-icon').forEach(icon => {
        icon.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
}

// Handle icon double-click
function handleIconDoubleClick(iconData) {
    if (iconData.type === 'folder' || iconData.type === 'alias') {
        if (iconData.name === 'Macintosh HD') {
            openFolderWindow('Macintosh HD', fileSystem['Macintosh HD'].contents);
        } else if (iconData.name === 'uDOS') {
            openFolderWindow('uDOS', fileSystem['Macintosh HD'].contents.uDOS.contents);
        } else if (iconData.name === 'Trash') {
            openTrashWindow();
        }
    }
}

// Open a folder window
function openFolderWindow(folderName, contents) {
    let html = '';

    Object.entries(contents).forEach(([name, item]) => {
        html += `
            <div class="desktop-icon" data-name="${name}" data-type="${item.type}">
                <img src="assets/images/${item.icon}" alt="${name}">
                <div class="desktop-icon-label">${name}</div>
            </div>
        `;
    });

    const window = new Window(folderName, html, 'folder', 100 + Math.random() * 200, 100 + Math.random() * 100);

    // Add double-click handlers to folder items
    setTimeout(() => {
        const folderIcons = window.element.querySelectorAll('.desktop-icon');
        folderIcons.forEach(icon => {
            icon.addEventListener('dblclick', () => {
                const itemName = icon.dataset.name;
                const itemType = icon.dataset.type;
                handleFolderItemDoubleClick(itemName, itemType, contents[itemName]);
            });
        });
    }, 100);
}

// Handle double-click on items within folder windows
function handleFolderItemDoubleClick(itemName, itemType, itemData) {
    if (itemType === 'folder') {
        openFolderWindow(itemName, itemData.contents);
    } else if (itemType === 'document') {
        openPage(itemData.file);
    } else if (itemType === 'application') {
        if (itemName === 'Calculator') {
            createCalculator();
        } else {
            openPage(itemData.file);
        }
    }
}

// Open trash window
function openTrashWindow() {
    const trashContent = `
        <div style="text-align: center; padding: 40px;">
            <img src="assets/images/trash-icon.png" alt="Trash" style="width: 64px; height: 64px; margin-bottom: 20px;">
            <p>The Trash is empty.</p>
            <p style="font-size: 12px; color: #666;">Items you delete will appear here until you empty the Trash.</p>
        </div>
    `;

    new Window('Trash', trashContent, 'folder', 150, 120);
}
