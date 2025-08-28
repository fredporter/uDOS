/*
 * uDOS Grid System Module
 * Interactive grid displays and map tile visualization
 * Universal Device Operating System v1.0.4.1
 */

class UDOSGrid {
    constructor() {
        this.currentSize = 'medium';
        this.gridData = new Map();
        this.mapTiles = new Map();
        this.activeGrid = null;
        this.selectedCells = new Set();
        this.isSelectionMode = false;
        this.gridPatterns = new Map();

        this.init();
    }

    init() {
        console.log('⚡ Initializing uDOS Grid System...');

        this.setupEventListeners();
        this.initializePatterns();
        this.loadGridData();

        // Generate initial grid
        this.generateGrid('medium');
    }

    setupEventListeners() {
        // Grid controls
        document.getElementById('gridSize')?.addEventListener('change', (e) => {
            this.changeGridSize(e.target.value);
        });

        document.getElementById('gridGenerate')?.addEventListener('click', () => {
            this.generateGrid(this.currentSize);
        });

        document.getElementById('gridClear')?.addEventListener('click', () => {
            this.clearGrid();
        });

        // Map controls
        document.getElementById('mapRegion')?.addEventListener('change', (e) => {
            this.loadMapRegion(e.target.value);
        });

        document.getElementById('mapLoad')?.addEventListener('click', () => {
            const region = document.getElementById('mapRegion')?.value || 'local';
            this.loadMapRegion(region);
        });

        document.getElementById('mapTiles')?.addEventListener('click', () => {
            this.showTileGrid();
        });

        // Keyboard shortcuts for grid operations
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('gridTab')?.classList.contains('active')) {
                this.handleGridKeyboard(e);
            }
        });
    }

    initializePatterns() {
        // Define grid patterns for different data types
        this.gridPatterns.set('system', {
            name: 'System Status',
            pattern: (x, y, size) => {
                const center = Math.floor(size / 2);
                const distance = Math.sqrt((x - center) ** 2 + (y - center) ** 2);
                return distance < size / 4 ? 'active' : 'inactive';
            },
            colors: ['var(--accent-green)', 'var(--bg-secondary)']
        });

        this.gridPatterns.set('memory', {
            name: 'Memory Usage',
            pattern: (x, y, size) => {
                const usage = Math.random();
                if (usage > 0.8) return 'error';
                if (usage > 0.6) return 'warning';
                if (usage > 0.3) return 'active';
                return 'inactive';
            },
            colors: ['var(--accent-red)', 'var(--accent-yellow)', 'var(--accent-green)', 'var(--bg-secondary)']
        });

        this.gridPatterns.set('network', {
            name: 'Network Topology',
            pattern: (x, y, size) => {
                const isNode = (x + y) % 3 === 0;
                const isConnection = x % 2 === 0 || y % 2 === 0;
                if (isNode) return 'active';
                if (isConnection) return 'data';
                return 'inactive';
            },
            colors: ['var(--accent-blue)', 'var(--accent-cyan)', 'var(--bg-secondary)']
        });

        this.gridPatterns.set('geographic', {
            name: 'Geographic Data',
            pattern: (x, y, size) => {
                const terrain = Math.sin(x / size * Math.PI * 2) * Math.cos(y / size * Math.PI * 2);
                if (terrain > 0.5) return 'mountain';
                if (terrain > 0) return 'land';
                if (terrain > -0.5) return 'water';
                return 'deep';
            },
            colors: ['var(--accent-purple)', 'var(--accent-green)', 'var(--accent-blue)', 'var(--accent-cyan)']
        });
    }

    generateGrid(size) {
        this.currentSize = size;
        const container = document.getElementById('gridContainer');
        if (!container) return;

        // Clear existing grid
        container.innerHTML = '';

        // Determine grid dimensions
        const dimensions = this.getGridDimensions(size);
        const { rows, cols, cellSize } = dimensions;

        // Create grid wrapper
        const gridWrapper = document.createElement('div');
        gridWrapper.className = `grid-${rows}x${cols}`;
        gridWrapper.style.cssText = `
            display: grid;
            grid-template-columns: repeat(${cols}, ${cellSize}px);
            grid-template-rows: repeat(${rows}, ${cellSize}px);
            gap: 2px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            background: var(--bg-primary);
        `;

        // Generate cells
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const cell = this.createGridCell(x, y, rows);
                gridWrapper.appendChild(cell);
            }
        }

        container.appendChild(gridWrapper);
        this.activeGrid = gridWrapper;

        // Apply pattern
        this.applyPattern('system');

        console.log(`📊 Generated ${rows}x${cols} grid`);
    }

    getGridDimensions(size) {
        const sizes = {
            small: { rows: 8, cols: 8, cellSize: 24 },
            medium: { rows: 16, cols: 16, cellSize: 20 },
            large: { rows: 32, cols: 32, cellSize: 16 }
        };
        return sizes[size] || sizes.medium;
    }

    createGridCell(x, y, gridSize) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.dataset.x = x;
        cell.dataset.y = y;
        cell.dataset.coord = `${x},${y}`;

        // Add coordinate display for debugging
        if (gridSize <= 16) {
            cell.textContent = `${x},${y}`;
            cell.style.fontSize = '0.6rem';
        }

        // Event listeners
        cell.addEventListener('click', (e) => {
            this.handleCellClick(e, x, y);
        });

        cell.addEventListener('mouseenter', (e) => {
            this.handleCellHover(e, x, y);
        });

        cell.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.handleCellRightClick(e, x, y);
        });

        return cell;
    }

    handleCellClick(event, x, y) {
        const cell = event.target;
        const coord = `${x},${y}`;

        if (this.isSelectionMode) {
            if (this.selectedCells.has(coord)) {
                this.selectedCells.delete(coord);
                cell.classList.remove('selected');
            } else {
                this.selectedCells.add(coord);
                cell.classList.add('selected');
            }
        } else {
            // Single cell interaction
            this.showCellInfo(x, y);

            // Cycle through states
            const currentClass = this.getCellState(cell);
            const nextClass = this.getNextCellState(currentClass);
            this.setCellState(cell, nextClass);
        }

        this.updateGridInfo();
    }

    handleCellHover(event, x, y) {
        const cell = event.target;

        // Show tooltip with cell information
        this.showCellTooltip(cell, x, y);

        // Highlight related cells (e.g., same row/column)
        this.highlightRelatedCells(x, y);
    }

    handleCellRightClick(event, x, y) {
        // Show context menu for cell operations
        this.showCellContextMenu(event, x, y);
    }

    getCellState(cell) {
        if (cell.classList.contains('active')) return 'active';
        if (cell.classList.contains('data')) return 'data';
        if (cell.classList.contains('error')) return 'error';
        if (cell.classList.contains('warning')) return 'warning';
        return 'inactive';
    }

    getNextCellState(currentState) {
        const states = ['inactive', 'active', 'data', 'warning', 'error'];
        const currentIndex = states.indexOf(currentState);
        return states[(currentIndex + 1) % states.length];
    }

    setCellState(cell, state) {
        // Remove all state classes
        cell.classList.remove('active', 'data', 'error', 'warning', 'inactive');

        // Add new state class
        if (state !== 'inactive') {
            cell.classList.add(state);
        }
    }

    applyPattern(patternName) {
        const pattern = this.gridPatterns.get(patternName);
        if (!pattern || !this.activeGrid) return;

        const cells = this.activeGrid.querySelectorAll('.grid-cell');
        const dimensions = this.getGridDimensions(this.currentSize);

        cells.forEach(cell => {
            const x = parseInt(cell.dataset.x);
            const y = parseInt(cell.dataset.y);
            const state = pattern.pattern(x, y, dimensions.rows);
            this.setCellState(cell, state);
        });

        console.log(`🎨 Applied pattern: ${pattern.name}`);
    }

    clearGrid() {
        if (!this.activeGrid) return;

        const cells = this.activeGrid.querySelectorAll('.grid-cell');
        cells.forEach(cell => {
            this.setCellState(cell, 'inactive');
            cell.classList.remove('selected');
        });

        this.selectedCells.clear();
        this.updateGridInfo();

        console.log('🧹 Grid cleared');
    }

    changeGridSize(size) {
        this.currentSize = size;
        document.body.setAttribute('data-grid-size', size);
        this.generateGrid(size);

        if (window.udosApp) {
            window.udosApp.changeGridSize(size);
        }
    }

    showCellInfo(x, y) {
        const coord = `${x},${y}`;
        const data = this.gridData.get(coord);

        console.log(`📍 Cell Info: ${coord}`, data);

        // Could show in a popup or info panel
        if (window.udosApp) {
            window.udosApp.logActivity(`Selected cell: ${coord}`);
        }
    }

    showCellTooltip(cell, x, y) {
        // Simple tooltip implementation
        cell.title = `Cell (${x},${y}) - ${this.getCellState(cell)}`;
    }

    highlightRelatedCells(x, y) {
        if (!this.activeGrid) return;

        // Remove existing highlights
        this.activeGrid.querySelectorAll('.grid-cell.highlight').forEach(cell => {
            cell.classList.remove('highlight');
        });

        // Highlight same row and column
        this.activeGrid.querySelectorAll('.grid-cell').forEach(cell => {
            const cellX = parseInt(cell.dataset.x);
            const cellY = parseInt(cell.dataset.y);

            if (cellX === x || cellY === y) {
                cell.classList.add('highlight');
            }
        });
    }

    showCellContextMenu(event, x, y) {
        // Simple context menu - could be enhanced
        const actions = [
            `Set as Active`,
            `Set as Data`,
            `Set as Error`,
            `Clear Cell`,
            `Get Cell Info`
        ];

        const selection = prompt(`Cell (${x},${y}) Actions:\n${actions.join('\n')}\n\nEnter action number (1-${actions.length}):`);

        if (selection) {
            const actionIndex = parseInt(selection) - 1;
            if (actionIndex >= 0 && actionIndex < actions.length) {
                this.executeCellAction(actionIndex, x, y);
            }
        }
    }

    executeCellAction(actionIndex, x, y) {
        const cell = this.activeGrid?.querySelector(`[data-x="${x}"][data-y="${y}"]`);
        if (!cell) return;

        const actions = ['active', 'data', 'error', 'inactive', 'info'];
        const action = actions[actionIndex];

        if (action === 'info') {
            this.showCellInfo(x, y);
        } else {
            this.setCellState(cell, action);
        }
    }

    handleGridKeyboard(event) {
        switch (event.key) {
            case 'c':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.copySelectedCells();
                }
                break;

            case 'v':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.pasteSelectedCells();
                }
                break;

            case 'Delete':
            case 'Backspace':
                this.clearSelectedCells();
                break;

            case 'a':
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                    this.selectAllCells();
                }
                break;

            case 'Escape':
                this.clearSelection();
                break;
        }
    }

    copySelectedCells() {
        const cellData = Array.from(this.selectedCells).map(coord => {
            const [x, y] = coord.split(',').map(Number);
            const cell = this.activeGrid?.querySelector(`[data-coord="${coord}"]`);
            return {
                x, y, state: this.getCellState(cell)
            };
        });

        localStorage.setItem('udos-grid-clipboard', JSON.stringify(cellData));
        console.log(`📋 Copied ${cellData.length} cells`);
    }

    pasteSelectedCells() {
        const clipboardData = localStorage.getItem('udos-grid-clipboard');
        if (!clipboardData) return;

        try {
            const cellData = JSON.parse(clipboardData);
            cellData.forEach(({ x, y, state }) => {
                const cell = this.activeGrid?.querySelector(`[data-x="${x}"][data-y="${y}"]`);
                if (cell) {
                    this.setCellState(cell, state);
                }
            });
            console.log(`📋 Pasted ${cellData.length} cells`);
        } catch (error) {
            console.error('Error pasting cells:', error);
        }
    }

    clearSelectedCells() {
        this.selectedCells.forEach(coord => {
            const cell = this.activeGrid?.querySelector(`[data-coord="${coord}"]`);
            if (cell) {
                this.setCellState(cell, 'inactive');
            }
        });
        console.log(`🧹 Cleared ${this.selectedCells.size} selected cells`);
    }

    selectAllCells() {
        if (!this.activeGrid) return;

        this.selectedCells.clear();
        this.activeGrid.querySelectorAll('.grid-cell').forEach(cell => {
            const coord = cell.dataset.coord;
            this.selectedCells.add(coord);
            cell.classList.add('selected');
        });

        this.isSelectionMode = true;
        console.log(`✅ Selected all ${this.selectedCells.size} cells`);
    }

    clearSelection() {
        this.selectedCells.clear();
        this.isSelectionMode = false;

        if (this.activeGrid) {
            this.activeGrid.querySelectorAll('.grid-cell.selected').forEach(cell => {
                cell.classList.remove('selected');
            });
        }

        console.log('❌ Selection cleared');
    }

    updateGridInfo() {
        const activeCells = this.activeGrid?.querySelectorAll('.grid-cell.active').length || 0;
        const dataCells = this.activeGrid?.querySelectorAll('.grid-cell.data').length || 0;
        const errorCells = this.activeGrid?.querySelectorAll('.grid-cell.error').length || 0;
        const selectedCells = this.selectedCells.size;

        console.log(`📊 Grid Stats: ${activeCells} active, ${dataCells} data, ${errorCells} errors, ${selectedCells} selected`);
    }

    // Map tile functions
    loadMapRegion(region) {
        console.log(`🗺️ Loading map region: ${region}`);

        const container = document.getElementById('mapContainer');
        if (!container) return;

        container.innerHTML = '';

        // Generate map tiles based on region
        const tiles = this.generateMapTiles(region);
        const mapGrid = document.createElement('div');
        mapGrid.className = 'map-grid';

        tiles.forEach(tile => {
            const tileElement = this.createMapTile(tile);
            mapGrid.appendChild(tileElement);
        });

        container.appendChild(mapGrid);
    }

    generateMapTiles(region) {
        const tileConfigs = {
            global: [
                { id: 'uTILE-000001', name: 'North America', icon: '🌎', coords: 'N40 W100' },
                { id: 'uTILE-000002', name: 'Europe', icon: '🏰', coords: 'N50 E10' },
                { id: 'uTILE-000003', name: 'Asia', icon: '🏯', coords: 'N35 E105' },
                { id: 'uTILE-000004', name: 'Africa', icon: '🦁', coords: 'S10 E20' },
                { id: 'uTILE-000005', name: 'South America', icon: '🦜', coords: 'S15 W60' },
                { id: 'uTILE-000006', name: 'Australia', icon: '🦘', coords: 'S25 E135' },
                { id: 'uTILE-000007', name: 'Antarctica', icon: '🐧', coords: 'S75 E0' },
                { id: 'uTILE-000008', name: 'Pacific', icon: '🌊', coords: 'N0 W150' }
            ],
            local: [
                { id: 'uTILE-100001', name: 'City Center', icon: '🏙️', coords: 'Local-01' },
                { id: 'uTILE-100002', name: 'Residential', icon: '🏘️', coords: 'Local-02' },
                { id: 'uTILE-100003', name: 'Industrial', icon: '🏭', coords: 'Local-03' },
                { id: 'uTILE-100004', name: 'Commercial', icon: '🏢', coords: 'Local-04' },
                { id: 'uTILE-100005', name: 'Parks', icon: '🌳', coords: 'Local-05' },
                { id: 'uTILE-100006', name: 'Transport', icon: '🚇', coords: 'Local-06' }
            ],
            custom: [
                { id: 'uTILE-200001', name: 'Data Center', icon: '💾', coords: 'Custom-A1' },
                { id: 'uTILE-200002', name: 'Network Hub', icon: '🌐', coords: 'Custom-B2' },
                { id: 'uTILE-200003', name: 'User Space', icon: '👤', coords: 'Custom-C3' },
                { id: 'uTILE-200004', name: 'Archive', icon: '📚', coords: 'Custom-D4' }
            ]
        };

        return tileConfigs[region] || tileConfigs.local;
    }

    createMapTile(tileData) {
        const tile = document.createElement('div');
        tile.className = 'map-tile';
        tile.dataset.tileId = tileData.id;
        tile.dataset.coords = tileData.coords;

        tile.innerHTML = `
            <div class="tile-coords">${tileData.coords}</div>
            <div class="tile-icon">${tileData.icon}</div>
            <div class="tile-label">${tileData.name}</div>
        `;

        tile.addEventListener('click', () => {
            this.selectMapTile(tileData);
        });

        return tile;
    }

    selectMapTile(tileData) {
        // Remove existing selection
        document.querySelectorAll('.map-tile.active').forEach(tile => {
            tile.classList.remove('active');
        });

        // Select new tile
        const tileElement = document.querySelector(`[data-tile-id="${tileData.id}"]`);
        if (tileElement) {
            tileElement.classList.add('active');
        }

        console.log(`🗺️ Selected tile: ${tileData.name} (${tileData.id})`);

        if (window.udosApp) {
            window.udosApp.logActivity(`Selected map tile: ${tileData.name}`);
        }
    }

    showTileGrid() {
        // Switch to grid view with geographic pattern
        this.applyPattern('geographic');

        if (window.udosApp) {
            window.udosApp.switchTab('grid');
        }
    }

    loadGridData() {
        // Load any saved grid data
        const saved = localStorage.getItem('udos-grid-data');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                data.forEach(({ coord, state, data }) => {
                    this.gridData.set(coord, { state, data });
                });
                console.log(`📊 Loaded ${this.gridData.size} grid data entries`);
            } catch (error) {
                console.warn('Error loading grid data:', error);
            }
        }
    }

    saveGridData() {
        const data = Array.from(this.gridData.entries()).map(([coord, cellData]) => ({
            coord, ...cellData
        }));
        localStorage.setItem('udos-grid-data', JSON.stringify(data));
        console.log(`💾 Saved ${data.length} grid data entries`);
    }

    // Public API methods
    refresh() {
        this.generateGrid(this.currentSize);
    }

    setPattern(patternName) {
        this.applyPattern(patternName);
    }

    exportGrid() {
        const gridState = [];
        if (this.activeGrid) {
            this.activeGrid.querySelectorAll('.grid-cell').forEach(cell => {
                const x = parseInt(cell.dataset.x);
                const y = parseInt(cell.dataset.y);
                const state = this.getCellState(cell);
                if (state !== 'inactive') {
                    gridState.push({ x, y, state });
                }
            });
        }
        return gridState;
    }

    importGrid(gridState) {
        if (!Array.isArray(gridState) || !this.activeGrid) return;

        this.clearGrid();
        gridState.forEach(({ x, y, state }) => {
            const cell = this.activeGrid.querySelector(`[data-x="${x}"][data-y="${y}"]`);
            if (cell) {
                this.setCellState(cell, state);
            }
        });
    }

    handleResize() {
        // Responsive adjustments
        const container = document.getElementById('gridContainer');
        if (container && window.innerWidth < 768) {
            // Adjust for mobile
            this.generateGrid('small');
        }
    }
}

// Export for external use
window.UDOSGrid = UDOSGrid;
