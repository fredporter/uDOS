/**
 * uDOS Desktop v1.0.24
 * Classic Mac OS System 6 Interface
 */

(function() {
    'use strict';

    // Desktop icon definitions
    const desktopIcons = [
        { id: 'markdown', icon: 'icons/cil-book.svg', label: 'Knowledge', action: 'openMarkedViewer' },
        { id: 'teletext', icon: 'icons/cil-tv.svg', label: 'Teletext', port: 9002 },
        { id: 'character', icon: 'icons/cil-text.svg', label: 'Character', action: 'openCharacterEditor' },
        { id: 'dashboard', icon: 'icons/cil-apps.svg', label: 'Dashboard', port: 8888 },
        { id: 'files', icon: 'icons/cil-folder.svg', label: 'Files', action: 'openFilePicker' },
        { id: 'patterns', icon: 'icons/apple.svg', label: 'Patterns', action: 'openPatternSelector' }
    ];

    // Desktop background patterns
    const desktopPatterns = [
        { name: 'Checkerboard (Default)', value: 'linear-gradient(90deg, #fff 21px, transparent 1%) 50%, linear-gradient(#fff 21px, transparent 1%) 50%, #000', size: '22px 22px' },
        { name: 'Fine Dots', value: 'radial-gradient(circle, #000 1px, transparent 1px)', size: '4px 4px' },
        { name: 'Grid Small', value: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', size: '10px 10px' },
        { name: 'Grid Medium', value: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', size: '20px 20px' },
        { name: 'Diagonal Lines', value: 'repeating-linear-gradient(45deg, #000, #000 1px, #fff 1px, #fff 4px)', size: 'auto' },
        { name: 'Crosshatch', value: 'repeating-linear-gradient(0deg, #000, #000 1px, transparent 1px, transparent 4px), repeating-linear-gradient(90deg, #000, #000 1px, transparent 1px, transparent 4px)', size: 'auto' },
        { name: 'Dense Dots', value: 'radial-gradient(circle, #000 1.5px, transparent 1.5px)', size: '6px 6px' },
        { name: 'Sparse Dots', value: 'radial-gradient(circle, #000 1px, transparent 1px)', size: '12px 12px' },
        { name: 'Solid Light', value: '#c0c0c0', size: 'auto' },
        { name: 'Solid Black', value: '#000', size: 'auto' }
    ];

    let currentPatternIndex = 0;

    // Window dragging state
    let draggedWindow = null;
    let dragOffset = { x: 0, y: 0 };
    let highestZIndex = 1000;

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('%c🖥️ uDOS System Desktop v1.0.24', 'font-size: 16px; font-weight: bold; color: #00ffff;');
        console.log('%csystem.css Framework • Chicago Font • Roboto Body', 'color: #888;');

        createDesktopIcons();
        setupCommandPalette();
        makeWindowsDraggable();
        loadPatternPreference();

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                toggleWindow('command-window');
                const input = document.getElementById('cmd-input');
                if (input) input.focus();
            }
        });
    });

    function loadPatternPreference() {
        const saved = localStorage.getItem('desktop-pattern-index');
        if (saved !== null) {
            currentPatternIndex = parseInt(saved);
            applyPattern(currentPatternIndex);
        }
    }

    function applyPattern(index) {
        const pattern = desktopPatterns[index];
        document.body.style.background = pattern.value;
        if (pattern.size !== 'auto') {
            document.body.style.backgroundSize = pattern.size;
            document.body.style.backgroundAttachment = 'fixed';
        }

        // Set text color based on pattern brightness
        // Light backgrounds (Solid Light, sparse patterns) need dark text
        const lightPatterns = [8, 9]; // Solid Light, Solid Black indices
        if (index === 8) {
            // Solid Light - use dark text
            document.body.style.color = '#000';
        } else if (index === 9) {
            // Solid Black - use light text
            document.body.style.color = '#fff';
        } else {
            // Pattern backgrounds - use default
            document.body.style.color = '';
        }
    }

    window.openPatternSelector = function() {
        const message = desktopPatterns.map((p, i) =>
            `${i + 1}. ${p.name}${i === currentPatternIndex ? ' ✓' : ''}`
        ).join('\n');

        const choice = prompt(`Select Desktop Pattern:\n\n${message}\n\nEnter number (1-${desktopPatterns.length}):`);

        if (choice) {
            const index = parseInt(choice) - 1;
            if (index >= 0 && index < desktopPatterns.length) {
                currentPatternIndex = index;
                applyPattern(currentPatternIndex);
                localStorage.setItem('desktop-pattern-index', currentPatternIndex);
            }
        }
    };

    function createDesktopIcons() {
        const container = document.getElementById('desktop-icons');
        if (!container) return;

        desktopIcons.forEach(icon => {
            const iconEl = document.createElement('div');
            iconEl.className = 'desktop-icon';
            iconEl.innerHTML = `
                <img src="${icon.icon}" alt="${icon.label}" class="desktop-icon-image">
                <div class="desktop-icon-label">${icon.label}</div>
            `;
            iconEl.addEventListener('click', () => {
                if (icon.action) {
                    window[icon.action]();
                } else if (icon.port) {
                    openExtension(icon.id, icon.port);
                }
            });
            container.appendChild(iconEl);
        });
    }

    function setupCommandPalette() {
        const input = document.getElementById('cmd-input');
        const output = document.getElementById('cmd-output');

        if (input && output) {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    const cmd = this.value.trim();
                    if (cmd) {
                        executeCommand(cmd, output);
                        this.value = '';
                    }
                }
            });
        }
    }

    function executeCommand(cmd, output) {
        const line = document.createElement('div');
        line.innerHTML = `<span class="command-prompt">$</span> ${cmd}`;
        output.appendChild(line);

        const response = document.createElement('div');
        response.style.color = '#00ff00';
        response.style.marginLeft = '12px';

        if (cmd === 'help') {
            response.innerHTML = `Available commands:
  help        - Show this help
  status      - Show system status
  extensions  - List extensions
  clear       - Clear output
  open [ext]  - Open extension
  editor      - Open character editor`;
        } else if (cmd === 'status') {
            response.innerHTML = `System Status:
  Version: v1.0.24
  Branch: v1.0.24-extensions
  Phase: 8.8 (system.css integration)
  Extensions: 6 active`;
        } else if (cmd === 'extensions') {
            response.innerHTML = `Active Extensions:
  • Markdown Viewer (port 9000)
  • Character Editor
  • Teletext (port 9002)
  • C64 Terminal (port 8889)
  • Dashboard NES (port 8888)
  • System Desktop (current)`;
        } else if (cmd === 'clear') {
            output.innerHTML = '<span class="command-prompt">$</span> ';
            return;
        } else if (cmd === 'editor') {
            openCharacterEditor();
            response.innerHTML = 'Opening Character Editor...';
        } else if (cmd.startsWith('open ')) {
            const ext = cmd.split(' ')[1];
            const ports = {
                'terminal': 8889,
                'markdown': 9000,
                'teletext': 9002,
                'character': null,
                'dashboard': 8888
            };
            if (ext === 'character') {
                openCharacterEditor();
                response.innerHTML = 'Opening Character Editor...';
            } else if (ports[ext]) {
                openExtension(ext, ports[ext]);
                response.innerHTML = `Opening ${ext}...`;
            } else {
                response.innerHTML = `Unknown extension: ${ext}`;
                response.style.color = '#ff0040';
            }
        } else {
            response.innerHTML = `Command not found: ${cmd}
Type 'help' for available commands`;
            response.style.color = '#ff0040';
        }

        output.appendChild(response);
        output.scrollTop = output.scrollHeight;
    }

    window.toggleWindow = function(windowId) {
        const win = document.getElementById(windowId);
        if (win) {
            const isOpening = win.style.display === 'none';
            win.style.display = isOpening ? 'block' : 'none';

            if (isOpening) {
                // Don't auto-fullscreen the about window (it's a toast)
                if (windowId !== 'about-window') {
                    autoFullscreenWindow(win);
                }
                bringToFront(win);
            } else {
                restoreDesktop();
            }
        }
    };

    window.closeWindow = function(windowId) {
        const win = document.getElementById(windowId);
        if (win) {
            win.style.display = 'none';
            restoreDesktop();
        }
    };

    function autoFullscreenWindow(win) {
        // Hide desktop elements
        const menuBar = document.querySelector('ul[role="menu-bar"]');
        const desktopIcons = document.getElementById('desktop-icons');

        if (menuBar) menuBar.style.display = 'none';
        if (desktopIcons) desktopIcons.style.display = 'none';

        // Fullscreen the window
        win.style.left = '0';
        win.style.top = '0';
        win.style.width = '100vw';
        win.style.height = '100vh';
        win.style.margin = '0';
        win.dataset.fullscreened = 'true';
    }

    function restoreDesktop() {
        // Show desktop elements
        const menuBar = document.querySelector('ul[role="menu-bar"]');
        const desktopIcons = document.getElementById('desktop-icons');

        if (menuBar) menuBar.style.display = 'flex';
        if (desktopIcons) desktopIcons.style.display = 'block';
    }

    window.closeCharacterEditor = function() {
        closeWindow('character-editor-window');
        restoreDesktop();
    };

    window.closeFilePicker = function() {
        closeWindow('file-picker-window');
        restoreDesktop();
    };

    window.closeKnowledgePicker = function() {
        closeWindow('knowledge-picker-window');
        restoreDesktop();
    };

    window.maximizeWindow = function(windowId) {
        const win = document.getElementById(windowId);
        if (!win) return;

        const isMaximized = win.dataset.maximized === 'true';

        if (isMaximized) {
            win.style.left = win.dataset.origLeft || '140px';
            win.style.top = win.dataset.origTop || '80px';
            win.style.width = win.dataset.origWidth || '900px';
            win.style.height = win.dataset.origHeight || '700px';
            win.dataset.maximized = 'false';
        } else {
            win.dataset.origLeft = win.style.left;
            win.dataset.origTop = win.style.top;
            win.dataset.origWidth = win.style.width;
            win.dataset.origHeight = win.style.height;

            win.style.left = '10px';
            win.style.top = '30px';
            win.style.width = 'calc(100% - 20px)';
            win.style.height = 'calc(100% - 40px)';
            win.dataset.maximized = 'true';
        }

        bringToFront(win);
    };

    window.openExtension = function(name, port) {
        window.open(`http://localhost:${port}`, '_blank');
    };

    window.openMarkedViewer = function() {
        const win = document.getElementById('knowledge-picker-window');
        if (win) {
            win.style.display = 'block';
            autoFullscreenWindow(win);
            bringToFront(win);
            loadKnowledgeLibrary();
        }
    };

    window.openCharacterEditor = function() {
        const win = document.getElementById('character-editor-window');
        const iframe = document.getElementById('character-editor-iframe');

        if (win && iframe) {
            if (!iframe.src || iframe.src === '' || iframe.src === window.location.href) {
                iframe.src = '/extensions/core/desktop/character-editor.html';
            }
            win.style.display = 'block';
            autoFullscreenWindow(win);
            bringToFront(win);
        }
    };

    window.openFilePicker = function() {
        const win = document.getElementById('file-picker-window');
        if (win) {
            win.style.display = 'block';
            autoFullscreenWindow(win);
            bringToFront(win);
            loadMemoryLibrary();
        }
    };

    window.newDocument = function() {
        alert('New document feature coming soon!');
    };

    window.openDocument = function() {
        alert('Open document feature coming soon!');
    };

    window.showHelp = function() {
        alert('uDOS Desktop Help:\n\n• Use menu bar for navigation\n• Double-click icons to open extensions\n• Cmd/Ctrl+K for command palette\n• Drag windows to move them');
    };

    window.testIcons = function() {
        console.log('%c🎨 Testing system.css Icons', 'font-weight: bold; color: #00ff00;');
        const icons = [
            'apple.svg', 'button.svg', 'button-default.svg', 'checkmark.svg',
            'radio-border.svg', 'radio-border-focused.svg', 'radio-dot.svg',
            'scrollbar-up.svg', 'scrollbar-up-active.svg',
            'scrollbar-down.svg', 'scrollbar-down-active.svg',
            'scrollbar-left.svg', 'scrollbar-left-active.svg',
            'scrollbar-right.svg', 'scrollbar-right-active.svg',
            'select-button.svg'
        ];

        icons.forEach(icon => {
            const img = new Image();
            img.src = `icons/${icon}`;
            img.onload = () => console.log(`✅ ${icon} - OK`);
            img.onerror = () => console.error(`❌ ${icon} - FAILED`);
        });

        alert('Icon test running - check browser console (F12) for results');
    };

    window.testFonts = function() {
        console.log('%c🔤 Testing Fonts', 'font-weight: bold; color: #00ff00;');

        const fonts = [
            { family: 'Chicago', file: 'ChicagoFLF.woff2' },
            { family: 'Roboto', file: 'Roboto-Regular.ttf' }
        ];

        fonts.forEach(font => {
            if (document.fonts.check(`12px ${font.family}`)) {
                console.log(`✅ ${font.family} (${font.file}) - LOADED`);
            } else {
                console.warn(`⚠️  ${font.family} (${font.file}) - NOT LOADED`);
            }
        });

        const testDiv = document.createElement('div');
        testDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;border:2px solid black;padding:20px;z-index:10000;';
        testDiv.innerHTML = `
            <h3 style="font-family: Chicago; margin-bottom: 12px;">Font Test</h3>
            <p style="font-family: Chicago; font-size: 14px; margin: 8px 0;">Chicago (Menus, Titles, Filenames)</p>
            <p style="font-family: Roboto; font-size: 14px; margin: 8px 0;">Roboto (Body text, Articles, Viewports)</p>
            <p style="font-family: Roboto; font-weight: bold; font-size: 14px; margin: 8px 0;">Roboto Bold</p>
            <p style="font-family: Roboto; font-style: italic; font-size: 14px; margin: 8px 0;">Roboto Italic</p>
            <button onclick="this.parentElement.remove()" style="margin-top: 12px;">Close</button>
        `;
        document.body.appendChild(testDiv);

        console.log('Font test overlay displayed');
    };

    function makeWindowsDraggable() {
        const windows = document.querySelectorAll('.window');

        windows.forEach(win => {
            const titleBar = win.querySelector('.title-bar');
            if (titleBar) {
                titleBar.style.cursor = 'move';
                titleBar.addEventListener('mousedown', startDrag);
            }
        });

        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDrag);
    }

    function startDrag(e) {
        if (e.target.tagName === 'BUTTON') return;

        draggedWindow = e.currentTarget.closest('.window');
        if (!draggedWindow) return;

        bringToFront(draggedWindow);

        const rect = draggedWindow.getBoundingClientRect();
        dragOffset.x = e.clientX - rect.left;
        dragOffset.y = e.clientY - rect.top;
    }

    function drag(e) {
        if (!draggedWindow) return;

        e.preventDefault();

        let newX = e.clientX - dragOffset.x;
        let newY = e.clientY - dragOffset.y;

        newX = Math.max(0, Math.min(newX, window.innerWidth - draggedWindow.offsetWidth));
        newY = Math.max(0, Math.min(newY, window.innerHeight - draggedWindow.offsetHeight));

        draggedWindow.style.left = newX + 'px';
        draggedWindow.style.top = newY + 'px';
    }

    function stopDrag() {
        draggedWindow = null;
    }

    function bringToFront(win) {
        if (!win) return;
        highestZIndex++;
        win.style.zIndex = highestZIndex;
    }

    async function loadKnowledgeLibrary() {
        const knowledgeList = document.getElementById('knowledge-list');
        const statusText = document.getElementById('knowledge-status');

        statusText.textContent = 'Loading...';
        knowledgeList.innerHTML = '<div style="padding: 20px; text-align: center;">Loading knowledge library...</div>';

        try {
            const response = await fetch('/knowledge/');
            if (!response.ok) throw new Error('Cannot access knowledge directory');

            const mdFiles = [];
            await scanForMdFiles('knowledge', mdFiles);

            if (mdFiles.length === 0) {
                knowledgeList.innerHTML = '<div style="padding: 20px; text-align: center; color: #808080;">No markdown files found</div>';
                document.getElementById('knowledge-count').textContent = '0 items';
                statusText.textContent = 'Empty';
                return;
            }

            renderKnowledgeList(mdFiles);
            statusText.textContent = 'Ready';
        } catch (error) {
            console.error('Error loading knowledge library:', error);
            knowledgeList.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #ff0000;">
                    <p>Cannot load knowledge library</p>
                    <p style="font-size: 11px; margin-top: 8px;">Error: ${error.message}</p>
                </div>
            `;
            statusText.textContent = 'Error';
        }
    }

    async function loadMemoryLibrary() {
        const fileList = document.getElementById('file-list');
        const statusText = document.getElementById('status-text');

        statusText.textContent = 'Loading...';
        fileList.innerHTML = '<div style="padding: 20px; text-align: center;">Loading memory library...</div>';

        try {
            const response = await fetch('/memory/');
            if (!response.ok) throw new Error('Cannot access memory directory');

            const mdFiles = [];
            await scanForMdFiles('memory', mdFiles);

            if (mdFiles.length === 0) {
                fileList.innerHTML = '<div style="padding: 20px; text-align: center; color: #808080;">No markdown files found</div>';
                document.getElementById('file-count').textContent = '0 items';
                statusText.textContent = 'Empty';
                return;
            }

            renderMemoryList(mdFiles);
            statusText.textContent = 'Ready';
        } catch (error) {
            console.error('Error loading memory library:', error);
            fileList.innerHTML = `
                <div style="padding: 20px; text-align: center; color: #ff0000;">
                    <p>Cannot load memory library</p>
                    <p style="font-size: 11px; margin-top: 8px;">Error: ${error.message}</p>
                </div>
            `;
            statusText.textContent = 'Error';
        }
    }

    async function scanForMdFiles(basePath, results) {
        try {
            const response = await fetch(`/${basePath}/`);
            if (!response.ok) return;

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const links = Array.from(doc.querySelectorAll('a')).filter(a => {
                const href = a.getAttribute('href');
                return href && href !== '../' && !href.startsWith('/');
            });

            for (const link of links) {
                const href = link.getAttribute('href');
                const name = decodeURIComponent(href.replace(/\/$/, ''));
                const isFolder = href.endsWith('/');
                const fullPath = `${basePath}/${name}`;

                if (isFolder) {
                    await scanForMdFiles(fullPath, results);
                } else if (name.endsWith('.md')) {
                    results.push(fullPath);
                }
            }
        } catch (error) {
            console.error(`Error scanning ${basePath}:`, error);
        }
    }

    function renderKnowledgeList(files) {
        const knowledgeList = document.getElementById('knowledge-list');
        knowledgeList.innerHTML = '';

        files.forEach(filePath => {
            const filename = filePath.split('/').pop();
            const item = document.createElement('div');
            item.className = 'file-item';
            item.style.cssText = `
                padding: 8px 12px;
                border-bottom: 1px solid #e0e0e0;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: Chicago, sans-serif;
                font-size: 12px;
            `;

            item.innerHTML = `
                <span style="font-size: 16px;">📝</span>
                <span style="flex: 1;">${filePath.replace('knowledge/', '')}</span>
                <span style="color: #808080; font-size: 10px;">MD</span>
            `;

            item.addEventListener('mouseenter', () => item.style.background = '#f0f0f0');
            item.addEventListener('mouseleave', () => item.style.background = 'transparent');
            item.addEventListener('click', () => {
                document.querySelectorAll('#knowledge-list .file-item').forEach(el => {
                    el.style.background = 'transparent';
                    el.style.color = '#000';
                });
                item.style.background = '#000';
                item.style.color = '#fff';
                document.getElementById('knowledge-selected').textContent = filename;
            });
            item.addEventListener('dblclick', () => {
                const markedUrl = `/extensions/core/desktop/marked-loader.html?file=${encodeURIComponent('/' + filePath)}`;
                window.open(markedUrl, '_blank');
                document.getElementById('knowledge-status').textContent = `Opened: ${filename}`;
            });

            knowledgeList.appendChild(item);
        });

        document.getElementById('knowledge-count').textContent = `${files.length} files`;
    }

    function renderMemoryList(files) {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';

        files.forEach(filePath => {
            const filename = filePath.split('/').pop();
            const item = document.createElement('div');
            item.className = 'file-item';
            item.style.cssText = `
                padding: 8px 12px;
                border-bottom: 1px solid #e0e0e0;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: Chicago, sans-serif;
                font-size: 12px;
            `;

            item.innerHTML = `
                <span style="font-size: 16px;">📝</span>
                <span style="flex: 1;">${filePath.replace('memory/', '')}</span>
                <span style="color: #808080; font-size: 10px;">MD</span>
            `;

            item.addEventListener('mouseenter', () => item.style.background = '#f0f0f0');
            item.addEventListener('mouseleave', () => item.style.background = 'transparent');
            item.addEventListener('click', () => {
                document.querySelectorAll('#file-list .file-item').forEach(el => {
                    el.style.background = 'transparent';
                    el.style.color = '#000';
                });
                item.style.background = '#000';
                item.style.color = '#fff';
                document.getElementById('selected-file').textContent = filename;
            });
            item.addEventListener('dblclick', () => {
                const markedUrl = `/extensions/core/desktop/marked-loader.html?file=${encodeURIComponent('/' + filePath)}`;
                window.open(markedUrl, '_blank');
                document.getElementById('status-text').textContent = `Opened: ${filename}`;
            });

            fileList.appendChild(item);
        });

        document.getElementById('file-count').textContent = `${files.length} files`;
    }

})();
