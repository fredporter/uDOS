
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
    mapElement.className = mapElement.className.replace(/scale-\d+/g, '');

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
