// ============================================
// uDOS v1.2 Dashboard - Modern JavaScript
// GitHub-inspired theme with server management
// ============================================

// Extension configuration
const EXTENSIONS = {
    'cmd': { port: 8890, name: 'Web Terminal', path: '/extensions/web/terminal' },
    'markdown-viewer': { port: 8889, name: 'Markdown Viewer', path: '/extensions/web/markdown-viewer' },
    'font-editor': { port: 8888, name: 'Font Editor', path: '/extensions/web/font-editor' },
    'typo': { port: 5173, name: 'Typo Editor', path: '/extensions/web/typo' },
    'micro': { port: 8891, name: 'Micro Editor', path: '/extensions/web/micro' },
    'dashboard': { port: 8887, name: 'Dashboard', path: '/extensions/web/dashboard' }
};

// ========== Theme Management ==========
function initializeTheme() {
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('udos-theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('udos-theme', newTheme);
    updateThemeIcon(newTheme);

    addLog(`Switched to ${newTheme} theme`, 'success');
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// ========== Activity Log ==========
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('activity-log');
    if (!logContainer) return;

    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'log-time';
    timeSpan.textContent = new Date().toLocaleTimeString();

    const messageSpan = document.createElement('span');
    messageSpan.className = 'log-message';
    messageSpan.textContent = message;

    logEntry.appendChild(timeSpan);
    logEntry.appendChild(messageSpan);

    // Add to top
    logContainer.insertBefore(logEntry, logContainer.firstChild);

    // Limit to 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// ========== Server Management ==========
async function handleExtension(extension, action) {
    const config = EXTENSIONS[extension];
    if (!config) {
        addLog(`Unknown extension: ${extension}`, 'error');
        return;
    }

    if (action === 'start') {
        await startExtension(extension);
    } else if (action === 'open') {
        await openExtension(extension);
    } else if (action === 'stop') {
        await stopExtension(extension);
    }
}

async function openExtension(extension) {
    const config = EXTENSIONS[extension];
    const url = `http://localhost:${config.port}`;

    // Check if server is running first
    const statusResponse = await fetch('/api/status');
    const statusData = await statusResponse.json();

    if (statusData.success) {
        const server = statusData.servers.find(s => s.id === extension);
        if (server && !server.running) {
            // Server not running, start it first with browser open
            addLog(`Starting ${extension} before opening...`, 'info');
            try {
                const response = await fetch(`/api/start/${extension}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ no_browser: false })
                });
                const data = await response.json();

                if (data.success) {
                    addLog(`✓ ${extension} started and opened`, 'success');
                    updateExtensionStatus(extension, 'online');
                    // Server startup will open browser automatically
                    return;
                } else {
                    addLog(`✗ Failed to start ${extension}: ${data.message || data.error}`, 'error');
                    return;
                }
            } catch (error) {
                addLog(`✗ Error starting ${extension}: ${error.message}`, 'error');
                return;
            }
        }
    }

    // Server is running or status check failed, just open it
    window.open(url, '_blank');
    addLog(`Opened ${extension} in new tab`, 'info');
}

async function startExtension(extension) {
    // Check if tile is marked as unavailable
    const tile = document.querySelector(`[data-extension="${extension}"]`);
    if (tile && tile.classList.contains('unavailable')) {
        const installCmd = tile.getAttribute('title') || 'Extension not installed';

        // Check if this extension can be auto-installed
        if (extension === 'typo' || extension === 'micro') {
            const shouldInstall = confirm(`${extension} is not installed. Install it now?\n\nThis will clone from GitHub and set up dependencies.`);
            if (shouldInstall) {
                await installExtension(extension);
                return;
            }
        }

        addLog(`⚠️ ${extension} not installed - ${installCmd}`, 'warning');
        return;
    }

    addLog(`Starting ${extension}...`, 'info');

    try {
        const response = await fetch(`/api/start/${extension}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            addLog(`✓ ${extension} started on port ${data.port}`, 'success');
            updateExtensionStatus(extension, 'online');
            // Remove unavailable class if it was set
            if (tile) tile.classList.remove('unavailable');
        } else {
            const errorMsg = data.message || data.error || 'Unknown error';
            // Check if extension is not installed
            if (errorMsg.includes('not installed') || errorMsg.includes('not found') || errorMsg.includes('Unknown server')) {
                addLog(`⚠️ ${extension} not available`, 'warning');
                // Mark tile as unavailable
                if (tile) tile.classList.add('unavailable');
            } else {
                addLog(`✗ Failed to start ${extension}: ${errorMsg}`, 'error');
            }
        }
    } catch (error) {
        addLog(`✗ Error starting ${extension}: ${error.message}`, 'error');
    }
}

async function installExtension(extension) {
    addLog(`📦 Installing ${extension}...`, 'info');

    try {
        const response = await fetch(`/api/install/${extension}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            addLog(`✓ Installation started for ${extension}`, 'success');

            // Show progress modal
            showInstallProgress(extension);

            // Poll for progress updates
            const progressInterval = setInterval(async () => {
                try {
                    const progressResponse = await fetch(`/api/install/progress/${extension}`);
                    const progressData = await progressResponse.json();

                    if (progressData.success) {
                        updateInstallProgress(extension, progressData);

                        // Check if completed or failed
                        if (progressData.status === 'completed') {
                            clearInterval(progressInterval);
                            addLog(`✓ ${extension} installed successfully!`, 'success');
                            setTimeout(() => {
                                hideInstallProgress();
                                checkAllStatus(); // Refresh to show as available
                            }, 2000);
                        } else if (progressData.status === 'failed') {
                            clearInterval(progressInterval);
                            addLog(`✗ ${extension} installation failed: ${progressData.message}`, 'error');
                            setTimeout(() => hideInstallProgress(), 3000);
                        }
                    }
                } catch (error) {
                    console.error('Progress check error:', error);
                }
            }, 1000); // Check every second

            // Timeout after 10 minutes
            setTimeout(() => {
                clearInterval(progressInterval);
                addLog(`⚠️ Installation timeout for ${extension}`, 'warning');
            }, 600000);

        } else {
            addLog(`✗ Failed to start installation: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`✗ Error installing ${extension}: ${error.message}`, 'error');
    }
}

function showInstallProgress(extension) {
    // Create progress modal if it doesn't exist
    let modal = document.getElementById('install-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'install-modal';
        modal.innerHTML = `
            <div class="install-modal-content">
                <h3 id="install-title">Installing...</h3>
                <div class="progress-container">
                    <div class="progress-bar" id="install-progress-bar"></div>
                    <span class="progress-text" id="install-progress-text">0%</span>
                </div>
                <p class="progress-message" id="install-message">Starting...</p>
                <div class="progress-output" id="install-output"></div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('install-title').textContent = `Installing ${extension}`;
    document.getElementById('install-progress-bar').style.width = '0%';
    document.getElementById('install-progress-text').textContent = '0%';
    document.getElementById('install-message').textContent = 'Starting...';
    document.getElementById('install-output').innerHTML = '';
    modal.style.display = 'flex';
}

function updateInstallProgress(extension, data) {
    const progressBar = document.getElementById('install-progress-bar');
    const progressText = document.getElementById('install-progress-text');
    const message = document.getElementById('install-message');
    const output = document.getElementById('install-output');

    if (progressBar) progressBar.style.width = data.progress + '%';
    if (progressText) progressText.textContent = data.progress + '%';
    if (message) message.textContent = data.message || 'Processing...';

    // Show last few lines of output
    if (output && data.output && data.output.length > 0) {
        const lastLines = data.output.slice(-5).map(line =>
            `<div class="output-line">${escapeHtml(line)}</div>`
        ).join('');
        output.innerHTML = lastLines;
    }

    // Change color based on status
    if (data.status === 'completed') {
        progressBar.style.background = 'var(--accent-green)';
        message.textContent = '✓ Installation completed!';
    } else if (data.status === 'failed') {
        progressBar.style.background = 'var(--accent-red)';
    }
}

function hideInstallProgress() {
    const modal = document.getElementById('install-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}function updateExtensionStatus(extension, status) {
    const statusBadge = document.getElementById(`status-${extension}`);
    if (!statusBadge) return;

    if (status === 'online') {
        statusBadge.classList.remove('offline');
        statusBadge.classList.add('online');
    } else {
        statusBadge.classList.remove('online');
        statusBadge.classList.add('offline');
    }
}

function clearLog() {
    const logContainer = document.getElementById('activity-log');
    if (logContainer) {
        logContainer.innerHTML = '';
        addLog('Log cleared', 'info');
    }
}

// ========== Status Checking ==========
async function checkAllStatus() {
    addLog('Checking server status...', 'info');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success && data.servers) {
            let onlineCount = 0;
            let installedCount = 0;

            data.servers.forEach(server => {
                const tile = document.querySelector(`[data-extension="${server.id}"]`);

                // Check installation status
                if (!server.installed) {
                    if (tile) {
                        tile.classList.add('unavailable');
                        tile.setAttribute('title', `Not installed. Run: ${server.setup_script || 'See docs'}`);
                    }
                    addLog(`⚠️ ${server.id} not installed`, 'warning');
                } else {
                    installedCount++;
                    if (tile) {
                        tile.classList.remove('unavailable');
                        tile.removeAttribute('title');
                    }

                    // Update running status
                    if (server.running) {
                        updateExtensionStatus(server.id, 'online');
                        onlineCount++;
                    } else {
                        updateExtensionStatus(server.id, 'offline');
                    }
                }
            });

            updateServerCount(onlineCount, installedCount);
            addLog(`✓ Status check complete: ${onlineCount}/${installedCount} servers online`, 'success');
        } else {
            addLog(`Status check unavailable`, 'warning');
        }
    } catch (error) {
        addLog(`Status check failed: ${error.message}`, 'warning');
    }
}

function updateServerCount(online, installed) {
    const serverCountEl = document.getElementById('server-count');
    if (serverCountEl) {
        serverCountEl.textContent = `${online}/${installed}`;
    }
}

// ========== Bulk Actions ==========
async function startAll() {
    const extensions = Object.keys(EXTENSIONS).filter(e => e !== 'dashboard');
    addLog(`Starting all ${extensions.length} extensions...`, 'info');

    for (const ext of extensions) {
        await startExtension(ext);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Delay between starts
    }

    setTimeout(checkAllStatus, 2000);
}

async function stopAll() {
    if (!confirm('Stop all running servers?')) return;

    const extensions = Object.keys(EXTENSIONS).filter(e => e !== 'dashboard');
    addLog(`Stopping all extensions...`, 'warning');

    for (const ext of extensions) {
        await stopExtension(ext);
    }

    setTimeout(checkAllStatus, 2000);
}

// ========== Utility Functions ==========
function updateClock() {
    const clockEl = document.getElementById('current-time');
    if (clockEl) {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString();
    }
}

function openDocs() {
    window.open('https://github.com/fredporter/uDOS/wiki', '_blank');
    addLog('Opened documentation', 'info');
}

function showHelp() {
    const helpText = `
uDOS v1.2 Dashboard Help
========================

Commands:
- Click theme toggle (top-right) to switch Dark/Light
- Start/Open buttons control individual extensions
- Use Quick Actions for bulk operations
- Activity log shows recent events

Extensions:
- Web Terminal: Full xterm.js terminal with uDOS
- Markdown Viewer: GitHub-style markdown with uCODE
- Font Editor: 16×16 bitmap font creator
- Dashboard: This control center

Keyboard:
- No special shortcuts (pure web interface)

For more help, visit the Documentation link.
    `.trim();

    alert(helpText);
}

// ========== Settings Modal ==========
function showSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        loadSettings();
        modal.classList.add('show');
        addLog('Opened settings panel', 'info');
    }
}

function closeSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

function loadSettings() {
    // Load from localStorage
    const editorFont = localStorage.getItem('udos-editor-font') || 'neon';
    const colorTheme = localStorage.getItem('udos-color-theme') || 'dark';
    const autoRefresh = localStorage.getItem('udos-auto-refresh') || '10';

    // Set form values
    const editorFontEl = document.getElementById('editor-font');
    const colorThemeEl = document.getElementById('color-theme');
    const autoRefreshEl = document.getElementById('auto-refresh');

    if (editorFontEl) editorFontEl.value = editorFont;
    if (colorThemeEl) colorThemeEl.value = colorTheme;
    if (autoRefreshEl) autoRefreshEl.value = autoRefresh;
}

function saveSettings() {
    const editorFont = document.getElementById('editor-font')?.value;
    const colorTheme = document.getElementById('color-theme')?.value;
    const autoRefresh = document.getElementById('auto-refresh')?.value;

    if (editorFont) localStorage.setItem('udos-editor-font', editorFont);
    if (colorTheme) {
        localStorage.setItem('udos-color-theme', colorTheme);
        document.documentElement.setAttribute('data-theme', colorTheme);
        updateThemeIcon(colorTheme);
    }
    if (autoRefresh) localStorage.setItem('udos-auto-refresh', autoRefresh);

    addLog('Settings saved', 'success');
    closeSettings();
}

function saveAndCloseSettings() {
    saveSettings();

    // Also save to backend
    saveSettingsToBackend();

    closeSettings();
}

async function saveSettingsToBackend() {
    try {
        const settings = {
            EDITOR_PREFERENCES: {
                CLI_EDITOR: localStorage.getItem('udos-terminal-editor') || 'nano',
                WEB_EDITOR: localStorage.getItem('udos-web-editor') || 'markdown-viewer'
            },
            SESSION_PREFERENCES: {
                THEME: localStorage.getItem('udos-theme')?.toUpperCase() || 'DUNGEON_CRAWLER'
            },
            LOCATION_DATA: {
                CURRENT_CITY: localStorage.getItem('udos-user-location') || ''
            }
        };

        const response = await fetch('/api/settings/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (response.ok) {
            addLog('Settings saved to backend', 'success');
        }
    } catch (error) {
        console.log('Backend save failed (offline mode):', error);
    }
}

// ========== World Map Modal ==========
let worldMapData = null;

function showMap() {
    const modal = document.getElementById('map-modal');
    if (modal) {
        modal.classList.add('show');
        if (!worldMapData) {
            loadMapData();
        } else {
            renderMap();
        }
        addLog('Opened world map', 'info');
    }
}

function closeMap() {
    const modal = document.getElementById('map-modal');
    if (modal) {
        modal.classList.remove('show');
    }
}

async function loadMapData() {
    try {
        const response = await fetch('/api/worldmap');
        if (response.ok) {
            worldMapData = await response.json();
            renderMap();
            addLog('World map data loaded', 'success');
        }
    } catch (error) {
        console.error('Failed to load map data:', error);
        // Fallback to embedded data
        loadFallbackMapData();
    }
}

function loadFallbackMapData() {
    // Simplified fallback map data
    worldMapData = {
        CITIES: {
            'New York': { latitude: 40.7128, longitude: -74.0060, grid_mapping: { x: -74, y: 41 }, dungeon_entrance: {} },
            'London': { latitude: 51.5074, longitude: -0.1278, grid_mapping: { x: 0, y: 52 }, dungeon_entrance: {} },
            'Tokyo': { latitude: 35.6762, longitude: 139.6503, grid_mapping: { x: 140, y: 36 }, dungeon_entrance: {} },
            'San Francisco': { latitude: 37.7749, longitude: -122.4194, grid_mapping: { x: -122, y: 38 }, dungeon_entrance: {} },
            'Paris': { latitude: 48.8566, longitude: 2.3522, grid_mapping: { x: 2, y: 49 } },
            'Berlin': { latitude: 52.5200, longitude: 13.4050, grid_mapping: { x: 13, y: 53 } },
            'Sydney': { latitude: -33.8688, longitude: 151.2093, grid_mapping: { x: 151, y: -34 } },
            'Mumbai': { latitude: 19.0760, longitude: 72.8777, grid_mapping: { x: 73, y: 19 } }
        },
        VIRTUAL_LAYERS: {
            SURFACE: { depth: 0, type: 'PHYSICAL' },
            CLOUD: { depth: 10, type: 'VIRTUAL' },
            SATELLITE: { depth: 100, type: 'VIRTUAL' },
            'DUNGEON-1': { depth: -1, type: 'VIRTUAL' }
        }
    };
    renderMap();
}

function renderMap() {
    const canvas = document.getElementById('map-canvas');
    if (!canvas || !worldMapData) return;

    // Clear canvas
    canvas.innerHTML = '';

    // Get active layers
    const showSurface = document.getElementById('layer-surface')?.checked ?? true;
    const showCloud = document.getElementById('layer-cloud')?.checked ?? false;
    const showSatellite = document.getElementById('layer-satellite')?.checked ?? false;
    const showDungeon = document.getElementById('layer-dungeon')?.checked ?? false;

    // Create ASCII world map grid (simplified lat/lon grid)
    const gridHtml = createWorldGrid();
    canvas.innerHTML = gridHtml;

    // Update info
    const userLocation = localStorage.getItem('udos-user-location') || 'Auto-detect';
    document.getElementById('current-city').innerHTML = `Location: <strong>${userLocation}</strong>`;
}

function createWorldGrid() {
    if (!worldMapData || !worldMapData.CITIES) return '<p>Loading map data...</p>';

    let html = '<div style="font-family: monospace; line-height: 1.4; color: var(--gh-fg-default);">';

    // ASCII map header
    html += '<div style="text-align: center; margin-bottom: 20px; font-size: 1.2rem; color: var(--gh-accent-fg);">';
    html += '━━━━━━━━━━━━━━━━━ WORLD MAP (SURFACE LAYER) ━━━━━━━━━━━━━━━━━<br>';
    html += '</div>';

    // Create a simple ASCII representation
    const cities = Object.entries(worldMapData.CITIES);
    const userLocation = localStorage.getItem('udos-user-location');

    html += '<div style="display: grid; gap: 15px; max-width: 900px; margin: 0 auto;">';

    cities.forEach(([cityName, cityData]) => {
        const isUserLocation = cityName === userLocation;
        const hasDungeon = cityData.dungeon_entrance && Object.keys(cityData.dungeon_entrance).length > 0;

        const lat = cityData.latitude.toFixed(2);
        const lon = cityData.longitude.toFixed(2);
        const coords = `${lat}°, ${lon}°`;

        html += `<div class="map-cell ${isUserLocation ? 'player' : 'city'}"
                      onclick="selectCity('${cityName}')"
                      title="${cityName}: ${coords}">
                    ${isUserLocation ? '📍' : '🏙️'}
                    <strong>${cityName}</strong>
                    ${hasDungeon ? '⚔️' : ''}
                    <span style="color: var(--gh-fg-muted); font-size: 0.85rem; margin-left: 10px;">${coords}</span>
                </div>`;
    });

    html += '</div>';
    html += '</div>';

    return html;
}

function updateMapLayers() {
    renderMap();
    addLog('Map layers updated', 'info');
}

function selectCity(cityName) {
    localStorage.setItem('udos-user-location', cityName);
    document.getElementById('current-city').innerHTML = `Location: <strong>${cityName}</strong>`;

    const cityData = worldMapData.CITIES[cityName];
    if (cityData && cityData.grid_mapping) {
        const coords = `${cityData.grid_mapping.x}, ${cityData.grid_mapping.y}`;
        document.getElementById('current-coords').innerHTML = `Coordinates: <strong>${coords}</strong>`;
    }

    renderMap();
    addLog(`Moved to ${cityName}`, 'success');
}

// ========== Initialization ==========
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initializeTheme();

    // Setup theme toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Start clock
    updateClock();
    setInterval(updateClock, 1000);

    // Initial status check
    setTimeout(checkAllStatus, 500);

    // Auto-refresh status every 30 seconds
    setInterval(checkAllStatus, 30000);

    // Welcome log
    addLog('Dashboard initialized', 'success');

    console.log('🌀 uDOS v1.2 Dashboard loaded');
});
