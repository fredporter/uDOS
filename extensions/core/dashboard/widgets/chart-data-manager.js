/**
 * Chart Data Manager
 *
 * Manages chart datasets in memory for incremental updates.
 * Provides efficient methods to add single data points without full refresh.
 *
 * Part of v1.2.8: Incremental Updates & Event Buffering
 *
 * @version 1.0.0
 * @author uDOS Development Team
 */

class ChartDataManager {
    constructor(config = {}) {
        this.config = {
            maxDataPoints: config.maxDataPoints || 100,      // Keep last N points
            animationDuration: config.animationDuration || 300,  // ms
            animationEasing: config.animationEasing || 'easeInOutQuart',
            ...config
        };

        // Chart instances registry
        this.charts = new Map();

        // Data storage by chart type
        this.datasets = {
            timeline: [],
            platform: new Map(),  // platform -> count
            histogram: [],        // response times
            metrics: {
                totalEvents: 0,
                successCount: 0,
                failureCount: 0,
                totalResponseTime: 0,
                avgResponseTime: 0,
                successRate: 100
            }
        };

        // Performance tracking
        this.stats = {
            updatesCount: 0,
            lastUpdateTime: null,
            avgUpdateDuration: 0
        };
    }

    /**
     * Register a Chart.js instance for management
     *
     * @param {string} type - Chart type (timeline, platform, gauge, histogram)
     * @param {Chart} chartInstance - Chart.js instance
     */
    registerChart(type, chartInstance) {
        if (!chartInstance) {
            console.warn(`Cannot register null chart for type: ${type}`);
            return;
        }

        this.charts.set(type, chartInstance);
        console.log(`Registered ${type} chart for incremental updates`);
    }

    /**
     * Add a single event to all relevant charts
     *
     * @param {Object} event - Webhook event data
     * @returns {Object} Update statistics
     */
    addEvent(event) {
        const startTime = performance.now();

        try {
            // Update metrics
            this.updateMetrics(event);

            // Update timeline chart
            this.addToTimeline(event);

            // Update platform distribution
            this.addToPlatformChart(event);

            // Update success gauge
            this.updateGauge();

            // Update histogram
            this.addToHistogram(event);

            // Track performance
            const duration = performance.now() - startTime;
            this.stats.updatesCount++;
            this.stats.lastUpdateTime = new Date();
            this.stats.avgUpdateDuration =
                (this.stats.avgUpdateDuration * (this.stats.updatesCount - 1) + duration) /
                this.stats.updatesCount;

            return {
                success: true,
                duration,
                updatedCharts: Array.from(this.charts.keys())
            };

        } catch (error) {
            console.error('Error adding event to charts:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Update metrics from event
     *
     * @param {Object} event - Event data
     */
    updateMetrics(event) {
        const metrics = this.datasets.metrics;

        metrics.totalEvents++;

        if (event.response_status === 'success') {
            metrics.successCount++;
        } else {
            metrics.failureCount++;
        }

        // Update response time stats
        if (event.execution_time_ms) {
            metrics.totalResponseTime += event.execution_time_ms;
            metrics.avgResponseTime = metrics.totalResponseTime / metrics.totalEvents;
        }

        // Recalculate success rate
        metrics.successRate = (metrics.successCount / metrics.totalEvents) * 100;
    }

    /**
     * Add event to timeline chart
     *
     * @param {Object} event - Event data
     */
    addToTimeline(event) {
        const chart = this.charts.get('timeline');
        if (!chart) return;

        const timestamp = new Date(event.timestamp);
        const dataPoint = {
            x: timestamp,
            y: event.execution_time_ms || 0,
            platform: event.platform,
            status: event.response_status
        };

        // Add to dataset
        this.datasets.timeline.push(dataPoint);

        // Enforce max data points limit
        if (this.datasets.timeline.length > this.config.maxDataPoints) {
            this.datasets.timeline.shift();
            chart.data.datasets[0].data.shift();
        }

        // Add to chart
        chart.data.datasets[0].data.push(dataPoint);

        // Update chart with animation
        chart.update('active');
    }

    /**
     * Add event to platform distribution chart
     *
     * @param {Object} event - Event data
     */
    addToPlatformChart(event) {
        const chart = this.charts.get('platform');
        if (!chart) return;

        const platform = event.platform || 'unknown';

        // Update count
        const currentCount = this.datasets.platform.get(platform) || 0;
        this.datasets.platform.set(platform, currentCount + 1);

        // Find or add platform in chart
        const labels = chart.data.labels;
        const data = chart.data.datasets[0].data;

        const index = labels.indexOf(platform);

        if (index === -1) {
            // New platform - add to chart
            labels.push(platform);
            data.push(1);
        } else {
            // Existing platform - increment
            data[index]++;
        }

        // Update chart with animation
        chart.update('active');
    }

    /**
     * Update success gauge chart
     */
    updateGauge() {
        const chart = this.charts.get('gauge');
        if (!chart) return;

        const successRate = this.datasets.metrics.successRate;

        // Update gauge value
        chart.data.datasets[0].data = [successRate, 100 - successRate];

        // Update chart with smooth animation
        chart.update('active');
    }

    /**
     * Add event to histogram chart
     *
     * @param {Object} event - Event data
     */
    addToHistogram(event) {
        const chart = this.charts.get('histogram');
        if (!chart) return;

        const responseTime = event.execution_time_ms;
        if (!responseTime) return;

        // Add to dataset
        this.datasets.histogram.push(responseTime);

        // Enforce max data points
        if (this.datasets.histogram.length > this.config.maxDataPoints) {
            this.datasets.histogram.shift();
        }

        // Recalculate histogram bins
        const bins = this.calculateHistogramBins(this.datasets.histogram);

        // Update chart data
        chart.data.labels = bins.labels;
        chart.data.datasets[0].data = bins.data;

        // Update chart with animation
        chart.update('active');
    }

    /**
     * Calculate histogram bins from response time data
     *
     * @param {Array} data - Response time values
     * @returns {Object} Bins with labels and counts
     */
    calculateHistogramBins(data) {
        if (data.length === 0) {
            return { labels: [], data: [] };
        }

        // Define bin ranges (ms)
        const binRanges = [
            { min: 0, max: 100, label: '0-100ms' },
            { min: 100, max: 200, label: '100-200ms' },
            { min: 200, max: 500, label: '200-500ms' },
            { min: 500, max: 1000, label: '500-1000ms' },
            { min: 1000, max: Infinity, label: '>1000ms' }
        ];

        // Count values in each bin
        const bins = binRanges.map(range => ({
            label: range.label,
            count: data.filter(val => val >= range.min && val < range.max).length
        }));

        return {
            labels: bins.map(b => b.label),
            data: bins.map(b => b.count)
        };
    }

    /**
     * Get current metrics
     *
     * @returns {Object} Current metrics
     */
    getMetrics() {
        return { ...this.datasets.metrics };
    }

    /**
     * Get performance statistics
     *
     * @returns {Object} Performance stats
     */
    getStats() {
        return { ...this.stats };
    }

    /**
     * Reset all data (for testing or cleanup)
     */
    reset() {
        this.datasets = {
            timeline: [],
            platform: new Map(),
            histogram: [],
            metrics: {
                totalEvents: 0,
                successCount: 0,
                failureCount: 0,
                totalResponseTime: 0,
                avgResponseTime: 0,
                successRate: 100
            }
        };

        this.stats = {
            updatesCount: 0,
            lastUpdateTime: null,
            avgUpdateDuration: 0
        };

        // Clear all charts
        this.charts.forEach((chart, type) => {
            if (chart.data.datasets && chart.data.datasets[0]) {
                chart.data.datasets[0].data = [];
                if (chart.data.labels) {
                    chart.data.labels = [];
                }
                chart.update('none');  // Update without animation
            }
        });

        console.log('Chart data manager reset');
    }

    /**
     * Export current state for debugging
     *
     * @returns {Object} Current state
     */
    exportState() {
        return {
            config: this.config,
            datasets: {
                timeline: this.datasets.timeline,
                platform: Array.from(this.datasets.platform.entries()),
                histogram: this.datasets.histogram,
                metrics: this.datasets.metrics
            },
            stats: this.stats,
            registeredCharts: Array.from(this.charts.keys())
        };
    }

    /**
     * Import state (for recovery or initialization)
     *
     * @param {Object} state - State object from exportState()
     */
    importState(state) {
        if (!state) return;

        // Restore datasets
        if (state.datasets) {
            this.datasets.timeline = state.datasets.timeline || [];
            this.datasets.platform = new Map(state.datasets.platform || []);
            this.datasets.histogram = state.datasets.histogram || [];
            this.datasets.metrics = state.datasets.metrics || this.datasets.metrics;
        }

        // Restore stats
        if (state.stats) {
            this.stats = state.stats;
        }

        console.log('Chart data manager state imported');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartDataManager;
}
