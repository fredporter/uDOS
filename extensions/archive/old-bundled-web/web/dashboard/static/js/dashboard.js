const socket = io();
let metricsUpdateInterval;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeMetricsUpdates();
    initializeCommandPalette();
    initializeFileBrowser();
    initializeServerStatus();
});

// Real-time metrics handling
function initializeMetricsUpdates() {
    metricsUpdateInterval = setInterval(() => {
        socket.emit('request_metrics');
    }, 1000);

    socket.on('metrics_update', (data) => {
        const metrics = JSON.parse(data);

        // Update CPU metrics
        if (metrics.cpu) {
            updateMetricDisplay('cpu-usage', metrics.cpu.value.percent);
            updateCPUDetails(metrics.cpu.value);
        }

        // Update Memory metrics
        if (metrics.memory) {
            updateMetricDisplay('memory-usage', metrics.memory.value.percent);
            updateMemoryDetails(metrics.memory.value);
        }

        // Update Disk metrics
        if (metrics.disk) {
            updateMetricDisplay('disk-usage', metrics.disk.value.percent);
            updateDiskDetails(metrics.disk.value);
        }

        // Update Process list
        if (metrics.processes) {
            updateProcessList(metrics.processes.value);
        }

        // Update Network stats
        if (metrics.network) {
            updateNetworkStats(metrics.network.value);
        }
    });
}

function updateMetricDisplay(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.querySelector('.metric-value').textContent = `${value}%`;
        updateMetricChart(element.querySelector('.metric-chart'), value);
    }
}

// Command palette functionality
function initializeCommandPalette() {
    const trigger = document.getElementById('command-palette-trigger');
    const palette = document.getElementById('command-palette');
    const input = palette.querySelector('input');

    trigger.addEventListener('click', () => {
        palette.classList.toggle('hidden');
        if (!palette.classList.contains('hidden')) {
            input.focus();
        }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !palette.classList.contains('hidden')) {
            palette.classList.add('hidden');
        }
    });
}

// Initialize with core functionality, will expand in subsequent tasks
function initializeFileBrowser() {
    // To be implemented
}

function initializeServerStatus() {
    // To be implemented
}
