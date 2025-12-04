/**
 * chart-utils.js - Chart.js Utilities for Webhook Analytics (v1.2.7)
 *
 * Provides Chart.js configuration and data transformation utilities
 * for webhook analytics visualizations.
 */

class ChartUtils {
    /**
     * Initialize Chart.js defaults for uDOS theme.
     */
    static initDefaults() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return false;
        }

        // uDOS dark theme defaults
        Chart.defaults.color = '#fff';
        Chart.defaults.borderColor = '#333';
        Chart.defaults.backgroundColor = '#2a2a2a';
        Chart.defaults.font.family = "'Courier New', monospace";
        Chart.defaults.plugins.legend.labels.color = '#fff';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        Chart.defaults.plugins.tooltip.titleColor = '#4CAF50';
        Chart.defaults.plugins.tooltip.bodyColor = '#fff';
        Chart.defaults.plugins.tooltip.borderColor = '#4CAF50';
        Chart.defaults.plugins.tooltip.borderWidth = 1;

        return true;
    }

    /**
     * Platform colors mapping.
     */
    static get platformColors() {
        return {
            'github': '#4CAF50',    // Green
            'slack': '#2196F3',     // Blue
            'notion': '#FF9800',    // Orange
            'clickup': '#9C27B0',   // Purple
            'default': '#607D8B'    // Gray
        };
    }

    /**
     * Get color for platform.
     */
    static getPlatformColor(platform) {
        return this.platformColors[platform] || this.platformColors.default;
    }

    /**
     * Create timeline chart (events over time).
     *
     * @param {string} canvasId - Canvas element ID
     * @param {Array} eventsOverTime - Array of {date, count} objects
     * @param {Object} options - Additional chart options
     * @returns {Chart} Chart.js instance
     */
    static createTimelineChart(canvasId, eventsOverTime, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        const labels = eventsOverTime.map(item => item.date);
        const data = eventsOverTime.map(item => item.count);

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events',
                    data: data,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#4CAF50',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Events: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: '#333',
                            borderColor: '#444'
                        },
                        ticks: {
                            color: '#888',
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#333',
                            borderColor: '#444'
                        },
                        ticks: {
                            color: '#888',
                            precision: 0
                        }
                    }
                },
                ...options
            }
        });
    }

    /**
     * Create platform distribution chart (pie/doughnut).
     *
     * @param {string} canvasId - Canvas element ID
     * @param {Object} platforms - Object with platform:count pairs
     * @param {Object} options - Additional chart options
     * @returns {Chart} Chart.js instance
     */
    static createPlatformChart(canvasId, platforms, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        const platformNames = Object.keys(platforms);
        const counts = Object.values(platforms);
        const colors = platformNames.map(p => this.getPlatformColor(p));

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: platformNames.map(p => p.charAt(0).toUpperCase() + p.slice(1)),
                datasets: [{
                    data: counts,
                    backgroundColor: colors,
                    borderColor: '#1a1a1a',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                ...options
            }
        });
    }

    /**
     * Create success rate gauge chart.
     *
     * @param {string} canvasId - Canvas element ID
     * @param {number} successRate - Success rate percentage (0-100)
     * @param {Object} options - Additional chart options
     * @returns {Chart} Chart.js instance
     */
    static createSuccessRateGauge(canvasId, successRate, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        // Determine color based on success rate
        let color;
        if (successRate >= 95) {
            color = '#4CAF50'; // Green
        } else if (successRate >= 80) {
            color = '#FF9800'; // Orange
        } else {
            color = '#F44336'; // Red
        }

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [successRate, 100 - successRate],
                    backgroundColor: [color, '#333'],
                    borderColor: '#1a1a1a',
                    borderWidth: 2,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                cutout: '70%',
                ...options
            },
            plugins: [{
                id: 'gaugeText',
                afterDraw: (chart) => {
                    const ctx = chart.ctx;
                    const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                    const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2 + 20;

                    ctx.save();
                    ctx.font = 'bold 32px monospace';
                    ctx.fillStyle = color;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(`${successRate.toFixed(1)}%`, centerX, centerY);
                    ctx.restore();
                }
            }]
        });
    }

    /**
     * Create response time histogram.
     *
     * @param {string} canvasId - Canvas element ID
     * @param {Array} events - Array of event objects with execution_time_ms
     * @param {Object} options - Additional chart options
     * @returns {Chart} Chart.js instance
     */
    static createResponseTimeHistogram(canvasId, events, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        // Destroy existing chart
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            existingChart.destroy();
        }

        // Create histogram bins
        const bins = this.createHistogramBins(events.map(e => e.execution_time_ms || 0));

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bins.labels,
                datasets: [{
                    label: 'Events',
                    data: bins.counts,
                    backgroundColor: '#2196F3',
                    borderColor: '#1976D2',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Events: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: '#333',
                            borderColor: '#444'
                        },
                        ticks: {
                            color: '#888'
                        },
                        title: {
                            display: true,
                            text: 'Response Time (ms)',
                            color: '#888'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#333',
                            borderColor: '#444'
                        },
                        ticks: {
                            color: '#888',
                            precision: 0
                        },
                        title: {
                            display: true,
                            text: 'Count',
                            color: '#888'
                        }
                    }
                },
                ...options
            }
        });
    }

    /**
     * Create histogram bins from data.
     *
     * @param {Array} data - Array of numeric values
     * @param {number} binCount - Number of bins (default: 10)
     * @returns {Object} Object with labels and counts arrays
     */
    static createHistogramBins(data, binCount = 10) {
        if (data.length === 0) {
            return { labels: [], counts: [] };
        }

        const min = Math.min(...data);
        const max = Math.max(...data);
        const binSize = (max - min) / binCount;

        const bins = Array(binCount).fill(0);
        const labels = [];

        // Create bin labels
        for (let i = 0; i < binCount; i++) {
            const binStart = min + (i * binSize);
            const binEnd = binStart + binSize;
            labels.push(`${binStart.toFixed(0)}-${binEnd.toFixed(0)}`);
        }

        // Count values in each bin
        data.forEach(value => {
            const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
            bins[binIndex]++;
        });

        return { labels, counts: bins };
    }

    /**
     * Format date for chart labels.
     *
     * @param {string} dateString - ISO date string
     * @param {string} format - Format type: 'short', 'medium', 'long'
     * @returns {string} Formatted date
     */
    static formatDateLabel(dateString, format = 'short') {
        const date = new Date(dateString);

        if (format === 'short') {
            return `${date.getMonth() + 1}/${date.getDate()}`;
        } else if (format === 'medium') {
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return `${months[date.getMonth()]} ${date.getDate()}`;
        } else {
            return date.toLocaleDateString();
        }
    }

    /**
     * Destroy all charts in container.
     *
     * @param {string} containerId - Container element ID
     */
    static destroyAllCharts(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const canvases = container.querySelectorAll('canvas');
        canvases.forEach(canvas => {
            const chart = Chart.getChart(canvas);
            if (chart) {
                chart.destroy();
            }
        });
    }

    /**
     * v1.2.8: Animation configurations for incremental updates
     */

    /**
     * Get optimized animation config for incremental chart updates.
     *
     * @param {string} chartType - Chart type (timeline, platform, gauge, histogram)
     * @param {string} updateMode - 'active' | 'quiet' | 'none'
     * @returns {Object} Animation configuration
     */
    static getIncrementalAnimationConfig(chartType, updateMode = 'active') {
        const baseConfig = {
            duration: 300,
            easing: 'easeInOutQuart'
        };

        if (updateMode === 'none') {
            return { duration: 0 };
        }

        if (updateMode === 'quiet') {
            return { duration: 150, easing: 'easeOutCubic' };
        }

        // Chart-specific optimizations
        const configs = {
            timeline: {
                duration: 300,
                easing: 'easeInOutQuart',
                x: {
                    type: 'number',
                    duration: 200,
                    from: (ctx) => {
                        // Slide in from right for new points
                        const chart = ctx.chart;
                        const meta = chart.getDatasetMeta(0);
                        if (ctx.index === meta.data.length - 1) {
                            return chart.chartArea.right;
                        }
                        return ctx.parsed.x;
                    }
                },
                y: {
                    type: 'number',
                    duration: 300,
                    from: 0
                }
            },
            platform: {
                duration: 400,
                easing: 'easeOutElastic',
                delay: (ctx) => ctx.index * 50 // Stagger animation
            },
            gauge: {
                duration: 600,
                easing: 'easeInOutCubic',
                // Smooth needle sweep
                numbers: {
                    duration: 800,
                    properties: ['circumference', 'rotation']
                }
            },
            histogram: {
                duration: 350,
                easing: 'easeOutBack',
                y: {
                    type: 'number',
                    duration: 350,
                    from: 0,
                    easing: 'easeOutBounce'
                }
            }
        };

        return configs[chartType] || baseConfig;
    }

    /**
     * Configure chart for optimal incremental updates.
     *
     * @param {Chart} chart - Chart.js instance
     * @param {string} chartType - Chart type
     */
    static configureIncrementalUpdates(chart, chartType) {
        if (!chart) return;

        // Set animation config
        chart.options.animation = this.getIncrementalAnimationConfig(chartType);

        // Optimize rendering
        chart.options.animation.onProgress = null; // Remove progress callbacks for performance
        chart.options.animation.onComplete = null;

        // Enable hover animations
        chart.options.hover = {
            animationDuration: 200,
            mode: 'nearest',
            intersect: true
        };

        // Optimize transitions
        chart.options.transitions = {
            active: {
                animation: {
                    duration: 200
                }
            },
            resize: {
                animation: {
                    duration: 0 // No animation on resize
                }
            },
            show: {
                animations: {
                    x: {
                        from: 0
                    },
                    y: {
                        from: 0
                    }
                }
            },
            hide: {
                animations: {
                    x: {
                        to: 0
                    },
                    y: {
                        to: 0
                    }
                }
            }
        };
    }

    /**
     * Create flash animation effect for metric updates.
     *
     * @param {HTMLElement} element - Element to flash
     * @param {string} color - Flash color (default: #4CAF50)
     * @param {number} duration - Animation duration in ms (default: 500)
     */
    static flashElement(element, color = '#4CAF50', duration = 500) {
        if (!element) return;

        const originalColor = element.style.color;
        const originalTransform = element.style.transform;

        // Flash animation
        element.style.transition = `color ${duration}ms ease, transform ${duration}ms ease`;
        element.style.color = color;
        element.style.transform = 'scale(1.1)';

        setTimeout(() => {
            element.style.color = originalColor;
            element.style.transform = originalTransform;

            // Clean up
            setTimeout(() => {
                element.style.transition = '';
            }, duration);
        }, duration / 2);
    }

    /**
     * Smooth scroll animation for charts.
     *
     * @param {Chart} chart - Chart.js instance
     * @param {number} targetIndex - Target data point index
     * @param {number} duration - Scroll duration in ms (default: 400)
     */
    static scrollToDataPoint(chart, targetIndex, duration = 400) {
        if (!chart || targetIndex < 0) return;

        const meta = chart.getDatasetMeta(0);
        if (!meta.data[targetIndex]) return;

        const element = meta.data[targetIndex];
        const chartArea = chart.chartArea;

        // Calculate target position
        const targetX = element.x;
        const centerX = (chartArea.left + chartArea.right) / 2;
        const offsetX = targetX - centerX;

        // Animate pan
        chart.pan({
            x: -offsetX
        }, undefined, duration);
    }
}

// Make available globally
window.ChartUtils = ChartUtils;

// Auto-initialize when Chart.js is available
if (typeof Chart !== 'undefined') {
    ChartUtils.initDefaults();
}
