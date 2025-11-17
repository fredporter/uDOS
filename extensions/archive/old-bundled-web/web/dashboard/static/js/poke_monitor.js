/**
 * POKE Monitor Component
 * Real-time memory visualization and manipulation
 */

class POKEMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.poke = window.dashboardAPI.poke;
        this.selectedCell = null;
        this.setup();
    }

    setup() {
        this.createUI();
        this.setupEventListeners();
        this.setupMemorySubscription();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="poke-monitor">
                <div class="poke-monitor-header">
                    <div class="poke-monitor-title">Memory Monitor</div>
                    <div class="poke-controls">
                        <div class="poke-input-group">
                            <label>Address:</label>
                            <input type="text" class="poke-input" id="poke-address" placeholder="$0000">
                        </div>
                        <div class="poke-input-group">
                            <label>Value:</label>
                            <input type="text" class="poke-input" id="poke-value" placeholder="$00">
                        </div>
                        <button class="poke-btn" id="poke-set">POKE</button>
                        <button class="poke-btn" id="poke-watch">Watch</button>
                    </div>
                </div>
                <div class="poke-memory-grid" id="memory-grid"></div>
                <div class="poke-watches">
                    <h3>Active Watches</h3>
                    <div class="poke-watch-list" id="watch-list"></div>
                </div>
            </div>
        `;

        this.renderMemoryGrid();
    }

    renderMemoryGrid() {
        const grid = document.getElementById('memory-grid');
        grid.innerHTML = '';

        // Show a 16x16 grid of memory cells (256 bytes)
        for (let i = 0; i < 256; i++) {
            const cell = document.createElement('div');
            cell.className = 'poke-memory-cell';
            cell.dataset.address = i;
            cell.innerHTML = `
                ${DashboardPOKE.formatValue(this.poke.peek(i) || 0)}
                <div class="poke-tooltip">
                    Address: ${DashboardPOKE.formatAddress(i)}
                    Value: ${DashboardPOKE.formatValue(this.poke.peek(i) || 0)}
                </div>
            `;
            grid.appendChild(cell);
        }
    }

    setupEventListeners() {
        // POKE button
        document.getElementById('poke-set').addEventListener('click', () => {
            const address = this.parseHexInput(document.getElementById('poke-address').value);
            const value = this.parseHexInput(document.getElementById('poke-value').value);

            if (address !== null && value !== null) {
                this.poke.poke(address, value);
            }
        });

        // Watch button
        document.getElementById('poke-watch').addEventListener('click', () => {
            const address = this.parseHexInput(document.getElementById('poke-address').value);
            if (address !== null) {
                this.addWatch(address);
            }
        });

        // Memory grid cell clicks
        document.getElementById('memory-grid').addEventListener('click', (e) => {
            const cell = e.target.closest('.poke-memory-cell');
            if (cell) {
                const address = parseInt(cell.dataset.address);
                document.getElementById('poke-address').value = DashboardPOKE.formatAddress(address);
                this.selectCell(cell);
            }
        });
    }

    setupMemorySubscription() {
        this.poke.subscribe((data) => {
            if (data.type === 'update') {
                this.updateCell(data.address, data.value);
            }
        });
    }

    updateCell(address, value) {
        const cell = document.querySelector(`.poke-memory-cell[data-address="${address}"]`);
        if (cell) {
            cell.innerHTML = `
                ${DashboardPOKE.formatValue(value)}
                <div class="poke-tooltip">
                    Address: ${DashboardPOKE.formatAddress(address)}
                    Value: ${DashboardPOKE.formatValue(value)}
                </div>
            `;
            cell.classList.add('modified');
            setTimeout(() => cell.classList.remove('modified'), 1000);
        }
    }

    selectCell(cell) {
        if (this.selectedCell) {
            this.selectedCell.classList.remove('selected');
        }
        cell.classList.add('selected');
        this.selectedCell = cell;
    }

    addWatch(address) {
        const watchList = document.getElementById('watch-list');
        const watchItem = document.createElement('div');
        watchItem.className = 'poke-watch-item';
        watchItem.innerHTML = `
            <span class="poke-watch-address">${DashboardPOKE.formatAddress(address)}</span>
            <span class="poke-watch-value">${DashboardPOKE.formatValue(this.poke.peek(address) || 0)}</span>
            <span class="poke-watch-remove">×</span>
        `;

        const cleanup = this.poke.watchAddress(address, (data) => {
            const valueSpan = watchItem.querySelector('.poke-watch-value');
            valueSpan.textContent = DashboardPOKE.formatValue(data.value);
            valueSpan.classList.add('modified');
            setTimeout(() => valueSpan.classList.remove('modified'), 1000);
        });

        watchItem.querySelector('.poke-watch-remove').addEventListener('click', () => {
            cleanup();
            watchItem.remove();
        });

        watchList.appendChild(watchItem);
    }

    parseHexInput(input) {
        input = input.replace(/[\$\s]/g, '');
        const value = parseInt(input, 16);
        return isNaN(value) ? null : value;
    }
}
