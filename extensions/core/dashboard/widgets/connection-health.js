/**
 * connection-health.js - WebSocket Connection Health Metrics Widget
 * v1.2.8 - Task 7: Connection Health Dashboard
 *
 * Displays real-time connection health metrics:
 * - Uptime counter (time since connect)
 * - Reconnection history (attempts, timestamps)
 * - Event rate (events/minute)
 * - Quality indicator (composite metric)
 */

export class ConnectionHealthWidget {
    constructor(config = {}) {
        this.containerId = config.containerId || 'connection-health-widget';
        this.socket = config.socket || null;
        this.analyticsWidget = config.analyticsWidget || null;

        // Connection tracking
        this.connectionStartTime = null;
        this.uptimeInterval = null;
        this.reconnectionHistory = [];
        this.maxReconnectionHistory = 10;

        // Event rate tracking
        this.eventTimestamps = [];
        this.eventRateWindow = 60000; // 1 minute window
        this.eventRateInterval = null;

        // UI state
        this.isExpanded = true;

        this.init();
    }

    /**
     * Initialize widget
     */
    init() {
        this.render();
        this.attachEventListeners();

        if (this.socket) {
            this.initWebSocket();
        }
    }

    /**
     * Initialize WebSocket event listeners
     */
    initWebSocket() {
        this.socket.on('connect', () => {
            this.handleConnect();
        });

        this.socket.on('disconnect', (reason) => {
            this.handleDisconnect(reason);
        });

        this.socket.on('reconnect_attempt', (attemptNumber) => {
            this.handleReconnectAttempt(attemptNumber);
        });

        this.socket.on('webhook_event', (event) => {
            this.trackEvent(event);
        });
    }

    /**
     * Handle WebSocket connection
     */
    handleConnect() {
        this.connectionStartTime = Date.now();
        this.startUptimeCounter();
        this.startEventRateTracking();
        this.updateQualityIndicator();
    }

    /**
     * Handle WebSocket disconnection
     */
    handleDisconnect(reason) {
        this.stopUptimeCounter();
        this.stopEventRateTracking();

        // Record disconnection in history
        const disconnectRecord = {
            timestamp: Date.now(),
            reason: reason,
            uptime: this.connectionStartTime ? Date.now() - this.connectionStartTime : 0
        };

        this.reconnectionHistory.unshift(disconnectRecord);
        if (this.reconnectionHistory.length > this.maxReconnectionHistory) {
            this.reconnectionHistory.pop();
        }

        this.updateReconnectionHistory();
        this.updateQualityIndicator();
    }

    /**
     * Handle reconnection attempt
     */
    handleReconnectAttempt(attemptNumber) {
        const statusElement = document.querySelector('#connection-health-status');
        if (statusElement) {
            statusElement.textContent = `Reconnecting (attempt ${attemptNumber})...`;
            statusElement.className = 'health-status warning';
        }
    }

    /**
     * Track incoming event for rate calculation
     */
    trackEvent(event) {
        const now = Date.now();
        this.eventTimestamps.push(now);

        // Clean old timestamps (outside window)
        this.eventTimestamps = this.eventTimestamps.filter(
            timestamp => now - timestamp < this.eventRateWindow
        );

        this.updateEventRate();
    }

    /**
     * Start uptime counter
     */
    startUptimeCounter() {
        this.stopUptimeCounter(); // Clear any existing interval

        this.updateUptime();
        this.uptimeInterval = setInterval(() => {
            this.updateUptime();
        }, 1000); // Update every second
    }

    /**
     * Stop uptime counter
     */
    stopUptimeCounter() {
        if (this.uptimeInterval) {
            clearInterval(this.uptimeInterval);
            this.uptimeInterval = null;
        }
    }

    /**
     * Update uptime display
     */
    updateUptime() {
        const uptimeElement = document.querySelector('#connection-uptime');
        if (!uptimeElement || !this.connectionStartTime) return;

        const uptime = Date.now() - this.connectionStartTime;
        uptimeElement.textContent = this.formatUptime(uptime);
    }

    /**
     * Format uptime in human-readable format
     */
    formatUptime(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) {
            return `${days}d ${hours % 24}h`;
        } else if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    /**
     * Start event rate tracking
     */
    startEventRateTracking() {
        this.stopEventRateTracking(); // Clear any existing interval

        this.updateEventRate();
        this.eventRateInterval = setInterval(() => {
            this.updateEventRate();
        }, 5000); // Update every 5 seconds
    }

    /**
     * Stop event rate tracking
     */
    stopEventRateTracking() {
        if (this.eventRateInterval) {
            clearInterval(this.eventRateInterval);
            this.eventRateInterval = null;
        }
    }

    /**
     * Update event rate display
     */
    updateEventRate() {
        const rateElement = document.querySelector('#event-rate');
        if (!rateElement) return;

        const eventsPerMinute = this.eventTimestamps.length;
        rateElement.textContent = `${eventsPerMinute} events/min`;

        // Update quality based on event rate
        this.updateQualityIndicator();
    }

    /**
     * Update reconnection history display
     */
    updateReconnectionHistory() {
        const historyElement = document.querySelector('#reconnection-history');
        if (!historyElement) return;

        if (this.reconnectionHistory.length === 0) {
            historyElement.innerHTML = '<div class="history-empty">No disconnections</div>';
            return;
        }

        const historyHTML = this.reconnectionHistory.map((record, index) => {
            const timeAgo = this.formatTimeAgo(Date.now() - record.timestamp);
            const uptimeFormatted = this.formatUptime(record.uptime);

            return `
                <div class="history-item">
                    <span class="history-time">${timeAgo}</span>
                    <span class="history-reason">${record.reason}</span>
                    <span class="history-uptime">Lasted: ${uptimeFormatted}</span>
                </div>
            `;
        }).join('');

        historyElement.innerHTML = historyHTML;
    }

    /**
     * Format time ago in human-readable format
     */
    formatTimeAgo(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return `${seconds}s ago`;
    }

    /**
     * Update quality indicator
     * Composite metric based on latency, uptime, and event rate
     */
    updateQualityIndicator() {
        const qualityElement = document.querySelector('#connection-quality');
        const statusElement = document.querySelector('#connection-health-status');
        if (!qualityElement || !statusElement) return;

        let quality = 100;
        let qualityClass = 'excellent';
        let statusText = 'Excellent';

        // Get latency from analytics widget if available
        let avgLatency = 0;
        if (this.analyticsWidget && this.analyticsWidget.latencyHistory.length > 0) {
            avgLatency = this.analyticsWidget.latencyHistory.reduce((sum, val) => sum + val, 0) /
                         this.analyticsWidget.latencyHistory.length;
        }

        // Deduct points for high latency
        if (avgLatency > 500) {
            quality -= 40;
        } else if (avgLatency > 200) {
            quality -= 20;
        } else if (avgLatency > 100) {
            quality -= 10;
        }

        // Deduct points for recent disconnections
        const recentDisconnects = this.reconnectionHistory.filter(
            record => Date.now() - record.timestamp < 300000 // Last 5 minutes
        ).length;
        quality -= recentDisconnects * 15;

        // Deduct points for low event rate (if connected for more than 1 minute)
        const uptime = this.connectionStartTime ? Date.now() - this.connectionStartTime : 0;
        if (uptime > 60000 && this.eventTimestamps.length === 0) {
            quality -= 10;
        }

        // Cap quality at 0-100
        quality = Math.max(0, Math.min(100, quality));

        // Determine quality class and status text
        if (quality >= 80) {
            qualityClass = 'excellent';
            statusText = 'Excellent';
        } else if (quality >= 60) {
            qualityClass = 'good';
            statusText = 'Good';
        } else if (quality >= 40) {
            qualityClass = 'fair';
            statusText = 'Fair';
        } else {
            qualityClass = 'poor';
            statusText = 'Poor';
        }

        qualityElement.textContent = `${quality}%`;
        qualityElement.className = `quality-score ${qualityClass}`;

        statusElement.textContent = statusText;
        statusElement.className = `health-status ${qualityClass}`;
    }

    /**
     * Toggle widget expanded/collapsed
     */
    toggleExpanded() {
        this.isExpanded = !this.isExpanded;

        const container = document.getElementById(this.containerId);
        const content = container.querySelector('.health-content');
        const toggleBtn = container.querySelector('.toggle-btn');

        if (this.isExpanded) {
            content.style.display = 'block';
            toggleBtn.textContent = '▼';
        } else {
            content.style.display = 'none';
            toggleBtn.textContent = '▶';
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const toggleBtn = document.querySelector(`#${this.containerId} .toggle-btn`);
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleExpanded());
        }
    }

    /**
     * Render widget HTML
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container #${this.containerId} not found`);
            return;
        }

        container.innerHTML = `
            <div class="health-widget">
                <div class="health-header">
                    <h3>Connection Health</h3>
                    <button class="toggle-btn">▼</button>
                </div>

                <div class="health-content">
                    <div class="health-metrics">
                        <div class="health-metric">
                            <span class="metric-label">Status</span>
                            <span id="connection-health-status" class="health-status">Disconnected</span>
                        </div>

                        <div class="health-metric">
                            <span class="metric-label">Quality</span>
                            <span id="connection-quality" class="quality-score">--</span>
                        </div>

                        <div class="health-metric">
                            <span class="metric-label">Uptime</span>
                            <span id="connection-uptime" class="uptime-value">--</span>
                        </div>

                        <div class="health-metric">
                            <span class="metric-label">Event Rate</span>
                            <span id="event-rate" class="rate-value">0 events/min</span>
                        </div>
                    </div>

                    <div class="health-section">
                        <h4>Recent Disconnections</h4>
                        <div id="reconnection-history" class="reconnection-history">
                            <div class="history-empty">No disconnections</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Destroy widget and cleanup
     */
    destroy() {
        this.stopUptimeCounter();
        this.stopEventRateTracking();

        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
}
