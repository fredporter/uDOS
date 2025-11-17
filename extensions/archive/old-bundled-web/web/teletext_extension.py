#!/usr/bin/env python3
"""
uDOS v1.0.4 - Teletext Web Extension

Web extension for serving teletext-style maps through the uDOS web interface.
Provides interactive teletext map viewing with real-time updates.

Features:
- Teletext map web server
- Real-time map updates
- Interactive controls
- Mobile-responsive design
- WebSocket integration for live updates

Version: 1.0.4
"""

import json
import os
import asyncio
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
import http.server
import socketserver
import threading
import time
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.services.teletext_renderer import TeletextMapIntegration
from core.services.integrated_map_engine import IntegratedMapEngine


class TeletextWebExtension:
    """Web extension for teletext map display and interaction."""

    def __init__(self, port: int = 8080):
        """Initialize teletext web extension."""
        self.port = port
        self.server = None
        self.server_thread = None
        self.teletext_integration = TeletextMapIntegration()
        self.map_engine = IntegratedMapEngine()
        self.web_root = Path("extensions/web/teletext")
        self.output_dir = Path("output/teletext")

        # Ensure directories exist
        self.web_root.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def setup_web_files(self):
        """Set up web files for the teletext extension."""

        # Create main HTML interface
        self._create_index_html()

        # Create API JavaScript
        self._create_api_js()

        # Create enhanced CSS
        self._create_enhanced_css()

        # Copy teletext assets
        self._copy_teletext_assets()

    def _create_index_html(self):
        """Create main teletext web interface."""
        html_content = '''<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>uDOS Teletext Maps</title>
    <link rel="stylesheet" href="./teletext-web.css"/>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🗺️</text></svg>">
</head>
<body class="tt-bg-blk">
    <header class="header">
        <h1>🗺️ uDOS Teletext Maps</h1>
        <div class="status" id="status">Ready</div>
    </header>

    <nav class="controls">
        <div class="control-group">
            <label>Location:</label>
            <select id="location-select">
                <option value="MEL">Melbourne (MEL)</option>
                <option value="SYD">Sydney (SYD)</option>
                <option value="LON">London (LON)</option>
                <option value="NYC">New York (NYC)</option>
                <option value="TYO">Tokyo (TYO)</option>
            </select>
            <button onclick="loadLocation()">Load</button>
        </div>

        <div class="control-group">
            <label>Size:</label>
            <select id="size-select">
                <option value="40,20">Standard (40×20)</option>
                <option value="60,30">Large (60×30)</option>
                <option value="80,40">Extra Large (80×40)</option>
                <option value="30,15">Compact (30×15)</option>
            </select>
        </div>

        <div class="control-group">
            <label>Scale:</label>
            <button onclick="setScale(1)">1×</button>
            <button onclick="setScale(2)">2×</button>
            <button onclick="setScale(3)">3×</button>
            <button onclick="setScale(4)">4×</button>
        </div>

        <div class="control-group">
            <button onclick="toggleMode()">Toggle Mosaic</button>
            <button onclick="refreshMap()">Refresh</button>
            <button onclick="exportMap()">Export</button>
        </div>
    </nav>

    <main class="main-content">
        <div class="map-container">
            <div class="teletext tt-bg-blk tt-fg-wht tt-con" id="teletext-map">
                <div class="loading">Loading teletext map...</div>
            </div>
        </div>

        <aside class="info-panel">
            <h3>Map Information</h3>
            <div id="map-info">
                <p>Select a location to view map details</p>
            </div>

            <h3>Legend</h3>
            <div class="legend">
                <div class="legend-item">
                    <span class="symbol tt-fg-yel">◉</span>
                    <span>Current Position</span>
                </div>
                <div class="legend-item">
                    <span class="symbol tt-fg-red">■</span>
                    <span>MEGA City</span>
                </div>
                <div class="legend-item">
                    <span class="symbol tt-fg-grn">▄</span>
                    <span>MAJOR City</span>
                </div>
                <div class="legend-item">
                    <span class="symbol tt-fg-blu">~</span>
                    <span>Water/Ocean</span>
                </div>
                <div class="legend-item">
                    <span class="symbol tt-fg-grn">.</span>
                    <span>Land/Terrain</span>
                </div>
            </div>

            <h3>Navigation</h3>
            <div class="navigation">
                <div class="nav-grid">
                    <button onclick="navigate('NW')">↖</button>
                    <button onclick="navigate('N')">↑</button>
                    <button onclick="navigate('NE')">↗</button>
                    <button onclick="navigate('W')">←</button>
                    <button onclick="navigate('CENTER')">●</button>
                    <button onclick="navigate('E')">→</button>
                    <button onclick="navigate('SW')">↙</button>
                    <button onclick="navigate('S')">↓</button>
                    <button onclick="navigate('SE')">↘</button>
                </div>
            </div>
        </aside>
    </main>

    <footer class="footer">
        <p>uDOS v1.0.4 - Teletext Mapping System |
           <a href="/api/status">API Status</a> |
           <a href="/docs">Documentation</a>
        </p>
    </footer>

    <script src="./teletext-api.js"></script>
    <script>
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            initializeTeletextMaps();
            loadLocation(); // Load default location
        });
    </script>
</body>
</html>'''

        with open(self.web_root / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _create_api_js(self):
        """Create JavaScript API for teletext map interaction."""
        js_content = '''
// uDOS Teletext Map API
class TeletextMapAPI {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentLocation = 'MEL';
        this.currentSize = [40, 20];
        this.currentScale = 1;
    }

    async loadMap(location, width = 40, height = 20) {
        try {
            updateStatus('Loading map...');

            // Simulate API call (in real implementation, this would call uDOS backend)
            const response = await this.simulateMapGeneration(location, width, height);

            if (response.success) {
                this.displayMap(response.html);
                this.updateMapInfo(response.info);
                updateStatus('Map loaded successfully');
            } else {
                updateStatus('Error loading map: ' + response.error);
            }
        } catch (error) {
            updateStatus('Error: ' + error.message);
        }
    }

    async simulateMapGeneration(location, width, height) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate simulated teletext map
        const mapData = this.generateSimulatedMap(location, width, height);

        return {
            success: true,
            html: mapData.html,
            info: mapData.info
        };
    }

    generateSimulatedMap(location, width, height) {
        const locations = {
            'MEL': { name: 'Melbourne', country: 'Australia', cell: 'JN196', lat: -37.81, lon: 144.96 },
            'SYD': { name: 'Sydney', country: 'Australia', cell: 'JV189', lat: -33.87, lon: 151.21 },
            'LON': { name: 'London', country: 'UK', cell: 'CB54', lat: 51.51, lon: -0.13 },
            'NYC': { name: 'New York', country: 'USA', cell: 'PD68', lat: 40.71, lon: -74.01 },
            'TYO': { name: 'Tokyo', country: 'Japan', cell: 'JF95', lat: 35.68, lon: 139.69 }
        };

        const loc = locations[location] || locations['MEL'];

        // Generate grid
        let grid = '';
        const centerX = Math.floor(width / 2);
        const centerY = Math.floor(height / 2);

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                let char = '';
                let className = 'cell';

                if (x === centerX && y === centerY) {
                    char = '◉';
                    className += ' tt-fg-yel tt-flash tt-con';
                } else if (Math.random() < 0.3) {
                    char = '~';
                    className += ' tt-fg-blu tt-con';
                } else if (Math.random() < 0.1) {
                    char = '■';
                    className += ' tt-fg-grn tt-con';
                } else {
                    char = '.';
                    className += ' tt-fg-grn tt-con';
                }

                grid += `<span class="${className}">${char}</span>`;
            }
        }

        return {
            html: grid,
            info: {
                location: `${loc.name}, ${loc.country}`,
                cell: loc.cell,
                coordinates: `${loc.lat}°, ${loc.lon}°`,
                size: `${width}×${height}`
            }
        };
    }

    displayMap(html) {
        const mapElement = document.getElementById('teletext-map');
        mapElement.innerHTML = html;

        // Update grid size
        mapElement.style.setProperty('--cols', this.currentSize[0]);
        mapElement.style.setProperty('--rows', this.currentSize[1]);
    }

    updateMapInfo(info) {
        const infoElement = document.getElementById('map-info');
        infoElement.innerHTML = `
            <p><strong>Location:</strong> ${info.location}</p>
            <p><strong>Cell:</strong> ${info.cell}</p>
            <p><strong>Coordinates:</strong> ${info.coordinates}</p>
            <p><strong>Size:</strong> ${info.size}</p>
        `;
    }
}

// Global API instance
const mapAPI = new TeletextMapAPI();

// UI Functions
function updateStatus(message) {
    document.getElementById('status').textContent = message;
}

function loadLocation() {
    const location = document.getElementById('location-select').value;
    const size = document.getElementById('size-select').value.split(',').map(Number);

    mapAPI.currentLocation = location;
    mapAPI.currentSize = size;

    mapAPI.loadMap(location, size[0], size[1]);
}

function setScale(scale) {
    const mapElement = document.getElementById('teletext-map');
    mapElement.className = mapElement.className.replace(/scale-\\d+/g, '');

    if (scale > 1) {
        mapElement.classList.add(`scale-${scale}`);
    }

    mapAPI.currentScale = scale;
}

function toggleMode() {
    const mapElement = document.getElementById('teletext-map');
    if (mapElement.classList.contains('tt-con')) {
        mapElement.classList.remove('tt-con');
        mapElement.classList.add('tt-sep');
    } else {
        mapElement.classList.remove('tt-sep');
        mapElement.classList.add('tt-con');
    }
}

function refreshMap() {
    loadLocation();
}

function exportMap() {
    const mapElement = document.getElementById('teletext-map');
    const html = `<!doctype html>
<html><head><title>uDOS Teletext Map</title><style>
${document.querySelector('link[rel="stylesheet"]').href}
</style></head><body>${mapElement.outerHTML}</body></html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `udos-teletext-map-${Date.now()}.html`;
    a.click();
    URL.revokeObjectURL(url);
}

function navigate(direction) {
    updateStatus(`Navigating ${direction}...`);
    // In a real implementation, this would update the map center
    setTimeout(() => {
        refreshMap();
    }, 500);
}

function initializeTeletextMaps() {
    updateStatus('Teletext mapping system initialized');

    // Set up auto-refresh (optional)
    // setInterval(refreshMap, 30000); // Refresh every 30 seconds
}
'''

        with open(self.web_root / "teletext-api.js", 'w', encoding='utf-8') as f:
            f.write(js_content)

    def _create_enhanced_css(self):
        """Create enhanced CSS for teletext web interface."""
        css_content = '''
/* uDOS Teletext Web Extension Styles */

:root {
    --mono: Menlo, SFMono-Regular, ui-monospace,
            "DejaVu Sans Mono", "Liberation Mono",
            Consolas, "Courier New", monospace;
    --bg-primary: #000;
    --bg-secondary: #111;
    --bg-accent: #222;
    --text-primary: #FFF;
    --text-secondary: #CCC;
    --accent-color: #FF0;
    --border-color: #333;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: var(--mono);
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    background: var(--bg-secondary);
    padding: 1rem;
    border-bottom: 2px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    margin: 0;
    color: var(--accent-color);
    font-size: 1.5rem;
}

.status {
    background: var(--bg-accent);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    border: 1px solid var(--border-color);
}

/* Navigation/Controls */
.controls {
    background: var(--bg-secondary);
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.control-group label {
    font-weight: bold;
    color: var(--text-secondary);
    min-width: 60px;
}

.control-group select,
.control-group button {
    background: var(--bg-accent);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 0.5rem;
    border-radius: 4px;
    font-family: var(--mono);
    cursor: pointer;
}

.control-group select:hover,
.control-group button:hover {
    background: var(--border-color);
}

/* Main Content */
.main-content {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 1rem;
    padding: 1rem;
    min-height: 0;
}

.map-container {
    background: var(--bg-secondary);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    overflow: auto;
    display: flex;
    justify-content: center;
    align-items: flex-start;
}

/* Teletext Styles */
.teletext {
    --cols: 40;
    --rows: 24;
    --cell: 1ch;
    --lhpx: 16px;
    display: grid;
    grid-template-columns: repeat(var(--cols), var(--cell));
    grid-auto-rows: var(--lhpx);
    font-size: 16px;
    line-height: var(--lhpx);
    letter-spacing: 0;
    white-space: pre;
    background: #000;
    color: #FFF;
    border: 2px solid var(--accent-color);
    padding: 8px;
    font-family: var(--mono);
}

.teletext .cell {
    width: 1ch;
    height: var(--lhpx);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.teletext.scale-2 { transform: scale(2); transform-origin: top left; }
.teletext.scale-3 { transform: scale(3); transform-origin: top left; }
.teletext.scale-4 { transform: scale(4); transform-origin: top left; }

/* WST Color Palette */
.tt-fg-blk{ color:#000; } .tt-fg-red{ color:#F00; } .tt-fg-grn{ color:#0F0; }
.tt-fg-yel{ color:#FF0; } .tt-fg-blu{ color:#00F; } .tt-fg-mag{ color:#F0F; }
.tt-fg-cyn{ color:#0FF; } .tt-fg-wht{ color:#FFF; }
.tt-bg-blk{ background:#000; } .tt-bg-blu{ background:#00F; } .tt-bg-red{ background:#F00; }
.tt-bg-grn{ background:#0F0; } .tt-bg-yel{ background:#FF0; } .tt-bg-mag{ background:#F0F; }
.tt-bg-cyn{ background:#0FF; } .tt-bg-wht{ background:#FFF; }

/* Mosaic modes */
.tt-con{ font-feature-settings: "ss01" 0; }
.tt-sep{ font-feature-settings: "ss01" 1; }

/* Flashing */
@keyframes tt-flash { 0%, 49% { opacity:1 } 50%, 100% { opacity:0 } }
.tt-flash{ animation: tt-flash 1s step-end infinite; }

/* Info Panel */
.info-panel {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    overflow-y: auto;
    max-height: 80vh;
}

.info-panel h3 {
    color: var(--accent-color);
    margin: 0 0 1rem 0;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
}

.info-panel h3:not(:first-child) {
    margin-top: 2rem;
}

/* Legend */
.legend {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.legend-item .symbol {
    font-family: var(--mono);
    font-weight: bold;
    width: 2ch;
    text-align: center;
}

/* Navigation */
.navigation {
    margin-top: 1rem;
}

.nav-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.25rem;
    max-width: 120px;
}

.nav-grid button {
    background: var(--bg-accent);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-family: var(--mono);
    font-size: 1rem;
}

.nav-grid button:hover {
    background: var(--border-color);
}

/* Footer */
.footer {
    background: var(--bg-secondary);
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    text-align: center;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.footer a {
    color: var(--accent-color);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Loading */
.loading {
    color: var(--text-secondary);
    text-align: center;
    padding: 2rem;
    font-style: italic;
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr;
        grid-template-rows: auto 1fr;
    }

    .controls {
        flex-direction: column;
        align-items: stretch;
    }

    .control-group {
        justify-content: space-between;
    }

    .teletext {
        font-size: 12px;
        --lhpx: 12px;
    }
}

@media (max-width: 480px) {
    .header {
        flex-direction: column;
        gap: 1rem;
    }

    .header h1 {
        font-size: 1.2rem;
    }

    .teletext {
        font-size: 10px;
        --lhpx: 10px;
    }
}
'''

        with open(self.web_root / "teletext-web.css", 'w', encoding='utf-8') as f:
            f.write(css_content)

    def _copy_teletext_assets(self):
        """Copy teletext font and assets if available."""
        # Copy from teletext mono starter if available
        source_dir = Path("examples/teletext_mono_starter")
        if source_dir.exists():
            try:
                # Copy font files
                font_dir = self.web_root / "fonts"
                font_dir.mkdir(exist_ok=True)

                source_fonts = source_dir / "fonts"
                if source_fonts.exists():
                    import shutil
                    shutil.copytree(source_fonts, font_dir, dirs_exist_ok=True)

                # Copy mosaic data
                mosaic_csv = source_dir / "mosaic_codepoints_E200-E3FF.csv"
                if mosaic_csv.exists():
                    shutil.copy2(mosaic_csv, self.web_root)

            except Exception as e:
                print(f"Warning: Could not copy teletext assets: {e}")

    def start_server(self, open_browser: bool = True) -> str:
        """Start the teletext web server."""

        # Set up web files
        self.setup_web_files()

        # Find available port
        for test_port in range(self.port, self.port + 10):
            try:
                import socketserver
                with socketserver.TCPServer(("", test_port), http.server.SimpleHTTPRequestHandler) as httpd:
                    self.port = test_port
                    break
            except OSError:
                continue
        else:
            raise Exception("No available ports found")

        # Change to web directory
        original_cwd = os.getcwd()
        os.chdir(self.web_root)

        # Start server in background thread
        def serve():
            try:
                with socketserver.TCPServer(("", self.port), http.server.SimpleHTTPRequestHandler) as httpd:
                    self.server = httpd
                    httpd.serve_forever()
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                os.chdir(original_cwd)

        self.server_thread = threading.Thread(target=serve, daemon=True)
        self.server_thread.start()

        # Give server time to start
        time.sleep(1)

        server_url = f"http://localhost:{self.port}"

        # Open browser if requested
        if open_browser:
            try:
                webbrowser.open(server_url)
            except Exception as e:
                print(f"Could not open browser: {e}")

        return server_url

    def stop_server(self):
        """Stop the teletext web server."""
        if self.server:
            self.server.shutdown()
            self.server = None

        if self.server_thread:
            self.server_thread.join(timeout=1)
            self.server_thread = None


if __name__ == "__main__":
    # Test teletext web extension
    print("🌐 Starting uDOS Teletext Web Extension")
    print("=" * 40)

    extension = TeletextWebExtension()

    try:
        server_url = extension.start_server()

        print(f"✅ Teletext web server started")
        print(f"🌐 Server URL: {server_url}")
        print(f"📁 Web root: {extension.web_root}")
        print(f"🖥️  Browser should open automatically")
        print(f"🛑 Press Ctrl+C to stop server")

        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            extension.stop_server()
            print("✅ Server stopped")

    except Exception as e:
        print(f"❌ Error starting server: {e}")
