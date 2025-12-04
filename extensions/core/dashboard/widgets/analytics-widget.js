/**
 * analytics-widget.js - Webhook Analytics Dashboard Widget (v1.2.8)
 *
 * Displays webhook event analytics with Chart.js visualizations:
 * - Events over time (line chart)
 * - Platform distribution (doughnut chart)
 * - Success rate gauge
 * - Response time histogram
 * - Recent errors list
 * - Event history table
 *
 * v1.2.8 Features:
 * - Incremental chart updates (no full refresh)
 * - Event buffering during disconnection
 * - Connection latency monitoring
 *
 * Requires: Chart.js 4.x, chart-utils.js, chart-data-manager.js
 */

class AnalyticsWidget {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        this.config = {
            apiBaseUrl: config.apiBaseUrl || 'http://localhost:5001/api',
            refreshInterval: config.refreshInterval || 30000, // 30 seconds
            days: config.days || 7,
            useChartJs: config.useChartJs !== false, // Enable Chart.js by default
            useWebSocket: config.useWebSocket !== false, // Enable WebSocket by default
            incrementalUpdates: config.incrementalUpdates !== false, // v1.2.8
            ...config
        };

        this.analytics = null;
        this.events = [];
        this.refreshTimer = null;
        this.charts = {}; // Store Chart.js instances
        this.socket = null; // WebSocket connection
        this.connectionStatus = 'disconnected'; // disconnected | connecting | connected
        this.chartDataManager = null; // v1.2.8: Incremental updates manager
        this.eventBuffer = null; // v1.2.8: Event buffer for disconnection handling
        this.latencyHistory = []; // v1.2.8: Rolling latency measurements
        this.latencyPingInterval = null; // v1.2.8: Ping interval timer
        this.lastPingTime = null; // v1.2.8: Last ping timestamp

        // Check Chart.js availability
        if (this.config.useChartJs && typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded, falling back to canvas rendering');
            this.config.useChartJs = false;
        }

        if (this.config.useChartJs && typeof ChartUtils !== 'undefined') {
            ChartUtils.initDefaults();
        }

        // Initialize ChartDataManager for incremental updates (v1.2.8)
        if (this.config.incrementalUpdates && typeof ChartDataManager !== 'undefined') {
            this.chartDataManager = new ChartDataManager({
                maxDataPoints: 100,
                animationDuration: 300,
                animationEasing: 'easeInOutQuart'
            });
            console.log('Incremental chart updates enabled');
        }

        // Initialize EventBuffer for disconnection handling (v1.2.8)
        if (typeof EventBuffer !== 'undefined') {
            this.eventBuffer = new EventBuffer({
                maxSize: 100,
                persistToStorage: true,
                deduplicateWindow: 5000 // 5 seconds
            });
            console.log('Event buffer initialized');
        }

        this.init();
    }    init() {
        this.render();
        this.loadAnalytics();
        this.startAutoRefresh();

        // Initialize WebSocket connection if enabled
        if (this.config.useWebSocket) {
            this.initWebSocket();
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="analytics-widget">
                <div class="widget-header">
                    <h2>📊 Webhook Analytics</h2>
                    <div class="widget-controls">
                        <span id="connection-status" class="connection-status disconnected" title="WebSocket Disconnected">
                            <span class="status-dot"></span>
                            <span class="status-text">Offline</span>
                        </span>
                        <select id="analytics-period" class="period-selector">
                            <option value="1">Last 24 Hours</option>
                            <option value="7" selected>Last 7 Days</option>
                            <option value="30">Last 30 Days</option>
                        </select>
                        <button id="refresh-analytics" class="btn-icon" title="Refresh">
                            🔄
                        </button>
                    </div>
                </div>
                </div>

                <div class="analytics-grid">
                    <!-- Metrics Cards -->
                    <div class="metrics-row">
                        <div class="metric-card">
                            <div class="metric-label">Total Events</div>
                            <div id="metric-total" class="metric-value">-</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Success Rate</div>
                            <div id="metric-success-rate" class="metric-value">-</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Avg Response Time</div>
                            <div id="metric-avg-time" class="metric-value">-</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Failed Events</div>
                            <div id="metric-errors" class="metric-value">-</div>
                        </div>
                    </div>

                    <!-- Charts -->
                    <div class="charts-row">
                        <div class="chart-container">
                            <h3>Events Over Time</h3>
                            <canvas id="events-timeline-chart"></canvas>
                        </div>
                        <div class="chart-container">
                            <h3>Platform Distribution</h3>
                            <canvas id="platform-chart"></canvas>
                        </div>
                    </div>

                    <!-- Response Time Chart -->
                    <div class="charts-row">
                        <div class="chart-container">
                            <h3>Response Time Distribution</h3>
                            <canvas id="response-time-chart"></canvas>
                        </div>
                    </div>

                    <!-- Recent Events -->
                    <div class="events-section">
                        <div class="section-header">
                            <h3>Recent Events</h3>
                            <button id="view-all-events" class="btn-link">View All →</button>
                        </div>
                        <div id="recent-events" class="events-list">
                            <div class="loading">Loading events...</div>
                        </div>
                    </div>

                    <!-- Recent Errors -->
                    <div class="errors-section">
                        <h3>Recent Errors</h3>
                        <div id="recent-errors" class="errors-list">
                            <div class="loading">No errors</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    attachEventListeners() {
        // Period selector
        document.getElementById('analytics-period').addEventListener('change', (e) => {
            this.config.days = parseInt(e.target.value);
            this.loadAnalytics();
        });

        // Refresh button
        document.getElementById('refresh-analytics').addEventListener('click', () => {
            this.loadAnalytics();
        });

        // View all events
        document.getElementById('view-all-events').addEventListener('click', () => {
            this.showEventsModal();
        });
    }

    async loadAnalytics() {
        try {
            // Fetch analytics
            const analyticsRes = await fetch(
                `${this.config.apiBaseUrl}/webhooks/analytics?days=${this.config.days}`
            );
            const analyticsData = await analyticsRes.json();

            if (analyticsData.status === 'success') {
                this.analytics = analyticsData.analytics;
                this.updateMetrics();
                this.updateCharts();
            }

            // Fetch recent events
            const eventsRes = await fetch(
                `${this.config.apiBaseUrl}/webhooks/events?limit=10`
            );
            const eventsData = await eventsRes.json();

            if (eventsData.status === 'success') {
                this.events = eventsData.events;
                this.updateEventsList();
                this.updateErrorsList();
            }

        } catch (error) {
            console.error('Failed to load analytics:', error);
            this.showError('Failed to load analytics data');
        }
    }

    updateMetrics() {
        if (!this.analytics) return;

        document.getElementById('metric-total').textContent =
            this.analytics.total_events.toLocaleString();

        document.getElementById('metric-success-rate').textContent =
            `${this.analytics.success_rate.toFixed(1)}%`;

        document.getElementById('metric-avg-time').textContent =
            `${this.analytics.avg_execution_time.toFixed(0)}ms`;

        document.getElementById('metric-errors').textContent =
            this.analytics.failed_events.toLocaleString();
    updateCharts() {
        if (!this.analytics) return;

        if (this.config.useChartJs) {
            this.renderTimelineChartJs();
            this.renderPlatformChartJs();
            this.renderSuccessRateGauge();
            this.renderResponseTimeHistogram();
        } else {
            this.renderTimelineChart();
            this.renderPlatformChart();
        }
    }    renderTimelineChartJs() {
        if (typeof ChartUtils === 'undefined') return;

        const eventsOverTime = this.analytics.events_over_time || [];

        // Destroy existing chart
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        // Create new chart
        this.charts.timeline = ChartUtils.createTimelineChart(
            'events-timeline-chart',
            eventsOverTime,
            {
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const date = eventsOverTime[index].date;
                        console.log(`Clicked on ${date}: ${eventsOverTime[index].count} events`);
                        // Could filter events by date here
                    }
                }
            }
        );

        // v1.2.8: Register with ChartDataManager for incremental updates
        if (this.chartDataManager) {
            this.chartDataManager.registerChart('timeline', this.charts.timeline);
        }
    }

    renderTimelineChart() {
        const ctx = document.getElementById('events-timeline-chart').getContext('2d');

        const canvas = ctx.canvas;
        canvas.width = canvas.parentElement.clientWidth - 20;
        canvas.height = 200;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw placeholder
        ctx.fillStyle = '#333';
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Events timeline visualization', canvas.width / 2, canvas.height / 2);
        ctx.fillText(`${this.analytics.total_events} events in last ${this.config.days} days`,
                     canvas.width / 2, canvas.height / 2 + 20);
    }
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw placeholder
        ctx.fillStyle = '#333';
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Events timeline visualization', canvas.width / 2, canvas.height / 2);
        ctx.fillText(`${this.analytics.total_events} events in last ${this.config.days} days`,
                     canvas.width / 2, canvas.height / 2 + 20);
    }

    renderPlatformChartJs() {
        if (typeof ChartUtils === 'undefined') return;

        const platforms = this.analytics.by_platform || {};

        // Destroy existing chart
        if (this.charts.platform) {
            this.charts.platform.destroy();
        }

        // Create new chart
        this.charts.platform = ChartUtils.createPlatformChart(
            'platform-chart',
            platforms,
            {
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const platform = Object.keys(platforms)[index];
                        console.log(`Clicked on ${platform}: ${platforms[platform]} events`);
                        // Could filter events by platform here
                    }
                }
            }
        );

        // v1.2.8: Register with ChartDataManager for incremental updates
        if (this.chartDataManager) {
            this.chartDataManager.registerChart('platform', this.charts.platform);
        }
    }

    renderPlatformChart() {
        const ctx = document.getElementById('platform-chart').getContext('2d');

        const canvas = ctx.canvas;
        canvas.width = canvas.parentElement.clientWidth - 20;
        canvas.height = 200;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const platforms = this.analytics.platforms || {};
        const platformNames = Object.keys(platforms);

        if (platformNames.length === 0) {
            ctx.fillStyle = '#666';
            ctx.font = '14px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('No platform data', canvas.width / 2, canvas.height / 2);
            return;
        }

        // Draw simple pie chart
        const total = Object.values(platforms).reduce((sum, count) => sum + count, 0);
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 30;

        const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'];
        let startAngle = -Math.PI / 2;

        platformNames.forEach((platform, i) => {
            const count = platforms[platform];
            const sliceAngle = (count / total) * 2 * Math.PI;

            // Draw slice
            ctx.fillStyle = colors[i % colors.length];
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();

            // Draw label
            const labelAngle = startAngle + sliceAngle / 2;
            const labelX = centerX + Math.cos(labelAngle) * (radius + 20);
            const labelY = centerY + Math.sin(labelAngle) * (radius + 20);

            ctx.fillStyle = '#fff';
            ctx.font = '12px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(`${platform} (${count})`, labelX, labelY);

            startAngle += sliceAngle;
        });
    }

    renderSuccessRateGauge() {
        if (typeof ChartUtils === 'undefined') return;

        const successRate = this.analytics.success_rate || 0;

        // Add gauge canvas if not exists
        let gaugeContainer = document.querySelector('.success-rate-gauge');
        if (!gaugeContainer) {
            const metricCard = document.getElementById('metric-success-rate').closest('.metric-card');
            if (metricCard) {
                gaugeContainer = document.createElement('div');
                gaugeContainer.className = 'success-rate-gauge';
                gaugeContainer.innerHTML = '<canvas id="success-rate-gauge-chart" width="150" height="100"></canvas>';
                metricCard.appendChild(gaugeContainer);
            }
        }

        // Destroy existing chart
        if (this.charts.successGauge) {
            this.charts.successGauge.destroy();
        }

        // Create gauge chart
        if (document.getElementById('success-rate-gauge-chart')) {
            this.charts.successGauge = ChartUtils.createSuccessRateGauge(
                'success-rate-gauge-chart',
                successRate
            );

            // v1.2.8: Register with ChartDataManager for incremental updates
            if (this.chartDataManager) {
                this.chartDataManager.registerChart('gauge', this.charts.successGauge);
            }
        }
    }

    renderResponseTimeHistogram() {
        if (typeof ChartUtils === 'undefined') return;
        if (!this.events || this.events.length === 0) return;

        // Destroy existing chart
        if (this.charts.responseTime) {
            this.charts.responseTime.destroy();
        }

        // Create histogram chart
        this.charts.responseTime = ChartUtils.createResponseTimeHistogram(
            'response-time-chart',
            this.events.filter(e => e.execution_time_ms),
            {
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        console.log('Clicked on response time bin:', elements[0].index);
                        // Could filter events by response time range
                    }
                }
            }
        );

        // v1.2.8: Register with ChartDataManager for incremental updates
        if (this.chartDataManager) {
            this.chartDataManager.registerChart('histogram', this.charts.responseTime);
        }
    }
    updateEventsList() {
        const container = document.getElementById('recent-events');

        if (this.events.length === 0) {
            container.innerHTML = '<div class="empty-state">No events yet</div>';
            return;
        }

        container.innerHTML = this.events.map(event => `
            <div class="event-item" data-event-id="${event.id}">
                <div class="event-header">
                    <span class="event-platform">${this.getPlatformEmoji(event.platform)} ${event.platform}</span>
                    <span class="event-type">${event.event_type}</span>
                    <span class="event-status ${event.response_status === 'success' ? 'success' : 'error'}">
                        ${event.response_status === 'success' ? '✓' : '✗'}
                    </span>
                </div>
                <div class="event-details">
                    <span class="event-time">${this.formatTimestamp(event.created_at)}</span>
                    <span class="event-timing">${event.execution_time_ms.toFixed(0)}ms</span>
                    ${event.error ? `<span class="event-error">⚠ ${event.error}</span>` : ''}
                </div>
                <div class="event-actions">
                    <button class="btn-sm" onclick="window.analyticsWidget.viewEvent('${event.id}')">View</button>
                    <button class="btn-sm" onclick="window.analyticsWidget.replayEvent('${event.id}')">Replay</button>
                </div>
            </div>
        `).join('');
    }

    updateErrorsList() {
        const container = document.getElementById('recent-errors');
        const errors = this.events.filter(e => e.response_status === 'error').slice(0, 5);

        if (errors.length === 0) {
            container.innerHTML = '<div class="empty-state">✓ No recent errors</div>';
            return;
        }

        container.innerHTML = errors.map(event => `
            <div class="error-item">
                <div class="error-header">
                    <span class="error-platform">${this.getPlatformEmoji(event.platform)} ${event.platform}</span>
                    <span class="error-time">${this.formatTimestamp(event.created_at)}</span>
                </div>
                <div class="error-message">${event.error || 'Unknown error'}</div>
                <button class="btn-sm" onclick="window.analyticsWidget.viewEvent('${event.id}')">Details</button>
            </div>
        `).join('');
    }

    getPlatformEmoji(platform) {
        const emojis = {
            'github': '🐙',
            'slack': '💬',
            'notion': '📝',
            'clickup': '✅'
        };
        return emojis[platform] || '🔔';
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    async viewEvent(eventId) {
        try {
            const res = await fetch(`${this.config.apiBaseUrl}/webhooks/events/${eventId}`);
            const data = await res.json();

            if (data.status === 'success') {
                this.showEventModal(data.event);
            }
        } catch (error) {
            console.error('Failed to load event:', error);
            this.showError('Failed to load event details');
        }
    }

    async replayEvent(eventId) {
        if (!confirm('Replay this webhook event?')) return;

        try {
            const res = await fetch(
                `${this.config.apiBaseUrl}/webhooks/events/${eventId}/replay`,
                { method: 'POST' }
            );
            const data = await res.json();

            if (data.status === 'success') {
                alert(`Event replayed successfully!\nActions triggered: ${data.actions_triggered}`);
                this.loadAnalytics(); // Refresh
            } else {
                alert(`Replay failed: ${data.message}`);
            }
        } catch (error) {
            console.error('Failed to replay event:', error);
            this.showError('Failed to replay event');
        }
    }

    showEventModal(event) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Event Details: ${event.id}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
                </div>
                <div class="modal-body">
                    <div class="event-detail-grid">
                        <div class="detail-item">
                            <label>Platform</label>
                            <div>${this.getPlatformEmoji(event.platform)} ${event.platform}</div>
                        </div>
                        <div class="detail-item">
                            <label>Event Type</label>
                            <div>${event.event_type}</div>
                        </div>
                        <div class="detail-item">
                            <label>Status</label>
                            <div class="${event.response_status === 'success' ? 'success' : 'error'}">
                                ${event.response_status}
                            </div>
                        </div>
                        <div class="detail-item">
                            <label>Execution Time</label>
                            <div>${event.execution_time_ms.toFixed(2)}ms</div>
                        </div>
                        <div class="detail-item">
                            <label>Timestamp</label>
                            <div>${new Date(event.created_at).toLocaleString()}</div>
                        </div>
                        ${event.error ? `
                            <div class="detail-item full-width">
                                <label>Error</label>
                                <div class="error">${event.error}</div>
                            </div>
                        ` : ''}
                    </div>

                    <div class="detail-section">
                        <h4>Payload</h4>
                        <pre>${JSON.stringify(event.payload, null, 2)}</pre>
                    </div>

                    <div class="detail-section">
                        <h4>Response</h4>
                        <pre>${JSON.stringify(event.response_data, null, 2)}</pre>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn" onclick="window.analyticsWidget.replayEvent('${event.id}')">
                        🔄 Replay Event
                    </button>
                    <button class="btn" onclick="this.closest('.modal').remove()">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    showEventsModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content large">
                <div class="modal-header">
                    <h3>All Events</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
                </div>
                <div class="modal-body">
                    <div id="all-events-list" class="events-list">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Load all events
        this.loadAllEvents(document.getElementById('all-events-list'));
    }

    async loadAllEvents(container) {
        try {
            const res = await fetch(`${this.config.apiBaseUrl}/webhooks/events?limit=100`);
            const data = await res.json();

            if (data.status === 'success') {
                this.events = data.events;
                this.updateEventsList();
            }
        } catch (error) {
            container.innerHTML = '<div class="error">Failed to load events</div>';
        }
    }

    showError(message) {
        alert(message);
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadAnalytics();
        }, this.config.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();

        // Disconnect WebSocket
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }

        // Destroy all Chart.js instances
        if (this.config.useChartJs) {
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
            this.charts = {};
        }

        this.container.innerHTML = '';
    }

    /**
     * Initialize WebSocket connection for real-time updates
     */
    initWebSocket() {
        // Check if Socket.IO is available
        if (typeof io === 'undefined') {
            console.warn('Socket.IO not loaded, WebSocket disabled');
            this.config.useWebSocket = false;
            return;
        }

        const serverUrl = this.config.apiBaseUrl.replace('/api', '');
        this.updateConnectionStatus('connecting');

        try {
            this.socket = io(serverUrl, {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: Infinity
            });

            // Connection established
            this.socket.on('connect', () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus('connected');

                // v1.2.8: Replay buffered events on reconnection
                this.replayBufferedEvents();

                // v1.2.8: Start latency measurement
                this.startLatencyMeasurement();
            });

            // Connection lost
            this.socket.on('disconnect', (reason) => {
                console.log('WebSocket disconnected:', reason);
                this.updateConnectionStatus('disconnected');

                // v1.2.8: Stop latency measurement
                this.stopLatencyMeasurement();
            });

            // Reconnecting
            this.socket.on('reconnecting', (attemptNumber) => {
                console.log(`WebSocket reconnecting (attempt ${attemptNumber})`);
                this.updateConnectionStatus('connecting');
            });

            // Webhook event received
            this.socket.on('webhook_event', (event) => {
                console.log('Received webhook event:', event);
                this.handleWebSocketEvent(event);
            });

            // v1.2.8: Pong response for latency measurement
            this.socket.on('pong', (timestamp) => {
                this.handlePongResponse(timestamp);
            });

            // Error handling
            this.socket.on('connect_error', (error) => {
                console.error('WebSocket connection error:', error);
                this.updateConnectionStatus('disconnected');
            });

        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.config.useWebSocket = false;
            this.updateConnectionStatus('disconnected');
        }
    }

    /**
     * Handle incoming WebSocket events
     * v1.2.8: Use incremental updates instead of full refresh
     */
    handleWebSocketEvent(event) {
        // v1.2.8: Buffer events when disconnected
        if (this.connectionStatus === 'disconnected' && this.eventBuffer) {
            const buffered = this.eventBuffer.add(event);
            if (buffered) {
                console.log(`Event buffered (${this.eventBuffer.size()} in buffer)`);
            }
            return;
        }

        // v1.2.8: Incremental update if available
        if (this.chartDataManager) {
            // Add event to charts incrementally
            const result = this.chartDataManager.addEvent(event);

            if (result.success) {
                console.log(`Incremental update: ${result.duration.toFixed(2)}ms (avg: ${this.chartDataManager.stats.avgUpdateDuration.toFixed(2)}ms)`);

                // Update metric cards (no API call needed)
                this.updateMetricCards(this.chartDataManager.getMetrics());

                // Flash animation for visual feedback
                this.flashEventCounter();
            } else {
                console.error('Incremental update failed, falling back to full refresh');
                this.loadAnalytics();
            }
        } else {
            // Legacy: Full refresh
            this.incrementEventCount();
            this.loadAnalytics();
        }
    }

    /**
     * Update metric cards from in-memory metrics (v1.2.8)
     */
    updateMetricCards(metrics) {
        const totalElement = document.getElementById('metric-total');
        const successRateElement = document.getElementById('metric-success-rate');
        const avgTimeElement = document.getElementById('metric-avg-time');
        const errorsElement = document.getElementById('metric-errors');

        if (totalElement) {
            totalElement.textContent = metrics.totalEvents.toLocaleString();
        }

        if (successRateElement) {
            successRateElement.textContent = `${metrics.successRate.toFixed(1)}%`;
            successRateElement.className = `metric-value ${metrics.successRate >= 90 ? 'success' : metrics.successRate >= 75 ? 'warning' : 'error'}`;
        }

        if (avgTimeElement) {
            avgTimeElement.textContent = `${metrics.avgResponseTime.toFixed(0)}ms`;
        }

        if (errorsElement) {
            errorsElement.textContent = metrics.failureCount.toLocaleString();
            errorsElement.className = `metric-value ${metrics.failureCount === 0 ? 'success' : 'error'}`;
        }
    }

    /**
     * Flash animation for event counter (v1.2.8)
     */
    flashEventCounter() {
        const totalElement = document.getElementById('metric-total');
        if (totalElement) {
            totalElement.style.animation = 'none';
            setTimeout(() => {
                totalElement.style.animation = 'flash 0.5s ease';
            }, 10);
        }
    }

    /**
     * Replay buffered events after reconnection (v1.2.8)
     */
    async replayBufferedEvents() {
        if (!this.eventBuffer || this.eventBuffer.isEmpty()) {
            console.log('No buffered events to replay');
            return;
        }

        const bufferedEvents = this.eventBuffer.getAll(false); // Get without clearing
        console.log(`Replaying ${bufferedEvents.length} buffered events...`);

        // Show notification
        this.showNotification(`Replaying ${bufferedEvents.length} buffered events...`, 'info');

        try {
            // Fetch latest events from API to check for duplicates
            const res = await fetch(`${this.config.apiBaseUrl}/webhooks/events?limit=100`);
            const data = await res.json();

            if (data.status === 'success') {
                const apiEventIds = new Set(data.events.map(e => e.id));

                // Filter out events that were already processed by the server
                const uniqueBufferedEvents = bufferedEvents.filter(event => {
                    return !apiEventIds.has(event.id);
                });

                console.log(`${uniqueBufferedEvents.length} unique events to replay (${bufferedEvents.length - uniqueBufferedEvents.length} duplicates removed)`);

                // Apply buffered events to charts
                let successCount = 0;
                let failureCount = 0;

                for (const event of uniqueBufferedEvents) {
                    if (this.chartDataManager) {
                        const result = this.chartDataManager.addEvent(event);
                        if (result.success) {
                            successCount++;
                        } else {
                            failureCount++;
                        }
                    }
                }

                // Update buffer statistics
                this.eventBuffer.markReplayed(successCount);

                // Clear buffer after successful replay
                this.eventBuffer.clear();

                // Update metrics
                if (this.chartDataManager) {
                    this.updateMetricCards(this.chartDataManager.getMetrics());
                }

                // Show completion notification
                if (successCount > 0) {
                    this.showNotification(`✓ Replayed ${successCount} events`, 'success', 3000);
                }

                if (failureCount > 0) {
                    console.warn(`Failed to replay ${failureCount} events`);
                }

                console.log('Event replay complete:', {
                    total: bufferedEvents.length,
                    unique: uniqueBufferedEvents.length,
                    success: successCount,
                    failed: failureCount,
                    bufferStats: this.eventBuffer.getStats()
                });

            } else {
                console.error('Failed to fetch API events for deduplication');
                this.showNotification('Failed to replay buffered events', 'error', 5000);
            }

        } catch (error) {
            console.error('Error replaying buffered events:', error);
            this.showNotification('Error replaying buffered events', 'error', 5000);
        }
    }

    /**
     * Show toast notification (v1.2.8)
     */
    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
            <span class="notification-message">${message}</span>
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Fade in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);

        // Remove after duration
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';

            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(status) {
        this.connectionStatus = status;

        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;

        statusElement.className = `connection-status ${status}`;

        const statusText = statusElement.querySelector('.status-text');
        const statusTitle = {
            connected: 'WebSocket Connected',
            connecting: 'WebSocket Connecting...',
            disconnected: 'WebSocket Disconnected'
        };

        if (statusText) {
            statusText.textContent = {
                connected: 'Live',
                connecting: 'Connecting',
                disconnected: 'Offline'
            }[status];
        }

        statusElement.title = statusTitle[status] || 'Unknown Status';
    }

    /**
     * Start measuring WebSocket latency
     * Sends ping every 10 seconds, server responds with pong
     */
    startLatencyMeasurement() {
        // Clear any existing interval
        this.stopLatencyMeasurement();

        // Send initial ping
        this.sendLatencyPing();

        // Set up periodic pings (every 10 seconds)
        this.latencyPingInterval = setInterval(() => {
            this.sendLatencyPing();
        }, 10000);
    }

    /**
     * Stop measuring WebSocket latency
     */
    stopLatencyMeasurement() {
        if (this.latencyPingInterval) {
            clearInterval(this.latencyPingInterval);
            this.latencyPingInterval = null;
        }
        this.lastPingTime = null;
        this.latencyHistory = [];
    }

    /**
     * Send ping with current timestamp
     */
    sendLatencyPing() {
        if (this.socket && this.socket.connected) {
            this.lastPingTime = Date.now();
            this.socket.emit('ping', this.lastPingTime);
        }
    }

    /**
     * Handle pong response from server
     * @param {number} timestamp - Original timestamp sent with ping
     */
    handlePongResponse(timestamp) {
        if (!this.lastPingTime) return;

        // Calculate round-trip time (RTT) in milliseconds
        const latency = Date.now() - timestamp;

        // Add to history (keep last 10 measurements)
        this.latencyHistory.push(latency);
        if (this.latencyHistory.length > 10) {
            this.latencyHistory.shift();
        }

        // Update display
        this.updateLatencyDisplay();
    }

    /**
     * Update latency display in connection status tooltip
     */
    updateLatencyDisplay() {
        if (this.latencyHistory.length === 0) return;

        // Calculate average latency from last 10 pings
        const avgLatency = Math.round(
            this.latencyHistory.reduce((sum, val) => sum + val, 0) / this.latencyHistory.length
        );

        // Update connection status tooltip with latency info
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;

        const color = this.getLatencyColor(avgLatency);
        const latencyText = `${avgLatency}ms`;

        // Update tooltip with latency information
        const baseTitle = statusElement.title.split('\n')[0]; // Keep first line
        statusElement.title = `${baseTitle}\nLatency: ${latencyText} (avg of ${this.latencyHistory.length} pings)`;

        // Optional: Add visual indicator to status element
        statusElement.setAttribute('data-latency', color);
    }

    /**
     * Get color code based on latency threshold
     * @param {number} latency - Latency in milliseconds
     * @returns {string} Color code: 'green', 'yellow', or 'red'
     */
    getLatencyColor(latency) {
        if (latency < 100) return 'green';      // Excellent: <100ms
        if (latency < 500) return 'yellow';     // Good: 100-500ms
        return 'red';                           // Poor: >500ms
    }

    /**
     * Increment event counter (visual feedback)
     */
    incrementEventCount() {
        const totalElement = document.querySelector('#total-events .metric-value');
        if (totalElement) {
            const current = parseInt(totalElement.textContent.replace(/,/g, '')) || 0;
            totalElement.textContent = (current + 1).toLocaleString();

            // Flash animation
            totalElement.style.animation = 'none';
            setTimeout(() => {
                totalElement.style.animation = 'flash 0.5s ease';
            }, 10);
        }
    }
}

// Make available globally
window.AnalyticsWidget = AnalyticsWidget;

