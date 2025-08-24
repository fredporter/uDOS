/**
 * uDOS v1.4 Dashboard JavaScript
 * Real-time dashboard with WebSocket integration
 */

class UDOSDashboard {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.statusUpdateInterval = null;
        this.activityLog = [];

        this.init();
    }

    init() {
        this.initWebSocket();
        this.initEventListeners();
        this.startStatusUpdates();
        this.logActivity('Dashboard initialized');
    }

    initWebSocket() {
        try {
            this.socket = io();

            this.socket.on('connect', () => {
                this.connected = true;
                this.updateConnectionStatus(true);
                this.logActivity('Connected to uDOS server');
            });

            this.socket.on('disconnect', () => {
                this.connected = false;
                this.updateConnectionStatus(false);
                this.logActivity('Disconnected from uDOS server');
            });

            this.socket.on('system_update', (data) => {
                this.updateSystemMetrics(data);
            });

        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.logActivity('Failed to connect to server');
        }
    }

    initEventListeners() {
        // Refresh button
        const refreshBtn = document.querySelector('#refreshStatus');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshStatus());
        }
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');

        if (statusIndicator && statusText) {
            if (connected) {
                statusIndicator.classList.remove('offline');
                statusText.textContent = 'Connected';
            } else {
                statusIndicator.classList.add('offline');
                statusText.textContent = 'Disconnected';
            }
        }
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.updateSystemMetrics(data);
            this.updateUDOSInfo(data);
            this.logActivity('System status refreshed');

        } catch (error) {
            console.error('Failed to refresh status:', error);
            this.logActivity(`Failed to refresh status: ${error.message}`);
        }
    }

    updateSystemMetrics(data) {
        if (!data.system) return;

        // Update CPU
        this.updateMetric('cpu', data.system.cpu_percent);

        // Update Memory
        this.updateMetric('memory', data.system.memory_percent);

        // Update Disk
        this.updateMetric('disk', data.system.disk_percent);
    }

    updateMetric(type, percentage) {
        const bar = document.querySelector(`#${type}Bar`);
        const value = document.querySelector(`#${type}Value`);

        if (bar && value) {
            bar.style.width = `${percentage}%`;
            value.textContent = `${Math.round(percentage)}%`;

            // Color coding
            if (percentage > 80) {
                bar.style.background = 'var(--polaroid-orange)';
            } else if (percentage > 60) {
                bar.style.background = 'var(--polaroid-yellow)';
            } else {
                bar.style.background = 'var(--polaroid-lime)';
            }
        }
    }

    updateUDOSInfo(data) {
        if (!data.udos) return;

        const elements = {
            'udosVersion': data.udos.version,
            'activeSessions': data.udos.active_sessions,
            'memoryStatus': data.udos.memory_status,
            'serverPath': data.udos.root_path
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.querySelector(`#${id}`);
            if (element) {
                element.textContent = value;
            }
        });
    }

    logActivity(message) {
        const timestamp = new Date().toLocaleTimeString();
        this.activityLog.unshift({ time: timestamp, message });

        // Keep only last 10 activities
        if (this.activityLog.length > 10) {
            this.activityLog = this.activityLog.slice(0, 10);
        }

        this.updateActivityDisplay();
    }

    updateActivityDisplay() {
        const activityList = document.querySelector('#activityList');
        if (!activityList) return;

        activityList.innerHTML = this.activityLog.map(activity => `
            <div class="activity-item">
                <span class="activity-time">${activity.time}</span>
                <span class="activity-text">${activity.message}</span>
            </div>
        `).join('');
    }

    startStatusUpdates() {
        // Initial refresh
        this.refreshStatus();

        // Periodic updates every 5 seconds
        this.statusUpdateInterval = setInterval(() => {
            if (this.connected) {
                this.refreshStatus();
            }
        }, 5000);
    }

    stopStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
    }
}

// Global action functions for buttons
function openTerminal() {
    window.open('/terminal', '_blank');
}

function browseMemory() {
    window.open('/memory', '_blank');
}

function viewLogs() {
    // TODO: Implement log viewer
    alert('Log viewer coming soon in v1.4!');
}

function refreshStatus() {
    if (window.dashboard) {
        window.dashboard.refreshStatus();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new UDOSDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.stopStatusUpdates();
        if (window.dashboard.socket) {
            window.dashboard.socket.disconnect();
        }
    }
});
