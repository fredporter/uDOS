/**
 * analytics-widget.js - Webhook Analytics Dashboard Widget (v1.2.6)
 *
 * Displays webhook event analytics with charts and metrics:
 * - Events over time (line chart)
 * - Platform distribution (pie chart)
 * - Success rate gauge
 * - Average response time metric
 * - Recent errors list
 * - Event history table
 */

class AnalyticsWidget {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        this.config = {
            apiBaseUrl: config.apiBaseUrl || 'http://localhost:5001/api',
            refreshInterval: config.refreshInterval || 30000, // 30 seconds
            days: config.days || 7,
            ...config
        };

        this.analytics = null;
        this.events = [];
        this.refreshTimer = null;

        this.init();
    }

    init() {
        this.render();
        this.loadAnalytics();
        this.startAutoRefresh();
    }

    render() {
        this.container.innerHTML = `
            <div class="analytics-widget">
                <div class="widget-header">
                    <h2>📊 Webhook Analytics</h2>
                    <div class="widget-controls">
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

        // Color code success rate
        const successRateEl = document.getElementById('metric-success-rate');
        if (this.analytics.success_rate >= 95) {
            successRateEl.style.color = '#4CAF50'; // Green
        } else if (this.analytics.success_rate >= 80) {
            successRateEl.style.color = '#FF9800'; // Orange
        } else {
            successRateEl.style.color = '#F44336'; // Red
        }
    }

    updateCharts() {
        if (!this.analytics) return;

        this.renderTimelineChart();
        this.renderPlatformChart();
    }

    renderTimelineChart() {
        const ctx = document.getElementById('events-timeline-chart').getContext('2d');

        // Simple timeline (could use Chart.js for better charts)
        // For now, render basic bars
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
        this.container.innerHTML = '';
    }
}

// Make available globally
window.AnalyticsWidget = AnalyticsWidget;
