// Mission Control Dashboard
class MissionControlDashboard {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 5000;
        this.config = {
            autoRefresh: 5000,
            celebrationDuration: 3000,
            maxTimelineItems: 50
        };
        this.timeline = [];
        this.init();
    }

    init() {
        console.log('Initializing Mission Control Dashboard...');
        this.connectWebSocket();
        this.loadAllData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    // WebSocket Connection
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/updates`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    handleWebSocketMessage(data) {
        console.log('WebSocket message:', data);

        switch (data.type) {
            case 'mission_update':
                this.updateMission(data.mission);
                break;
            case 'mission_completed':
                this.handleMissionCompleted(data.mission);
                break;
            case 'schedule_update':
                this.loadSchedules();
                break;
            case 'resource_update':
                this.updateResources(data.resources);
                break;
            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');

        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Disconnected';
        }
    }

    // Data Loading
    async loadAllData() {
        try {
            await Promise.all([
                this.loadMissions(),
                this.loadSchedules(),
                this.loadResources()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadMissions() {
        try {
            const response = await fetch('/api/missions');
            const data = await response.json();

            if (data.success) {
                this.renderMissions(data.missions);
                this.renderNextMission(data.next_mission);
            }
        } catch (error) {
            console.error('Error loading missions:', error);
        }
    }

    async loadSchedules() {
        try {
            const response = await fetch('/api/schedules');
            const data = await response.json();

            if (data.success) {
                this.renderSchedules(data.schedules);
            }
        } catch (error) {
            console.error('Error loading schedules:', error);
        }
    }

    async loadResources() {
        try {
            const response = await fetch('/api/resources');
            const data = await response.json();

            if (data.success) {
                this.renderResources(data.resources);
            }
        } catch (error) {
            console.error('Error loading resources:', error);
        }
    }

    // Rendering Methods
    renderMissions(missions) {
        const container = document.getElementById('missions-list');

        if (!missions || missions.length === 0) {
            container.innerHTML = '<div class="empty-state">No active missions</div>';
            return;
        }

        container.innerHTML = missions.map(mission => this.createMissionCard(mission)).join('');
        this.addTimelineEvent('📋 Missions refreshed', `${missions.length} active`);
    }

    createMissionCard(mission) {
        const priorityClass = `priority-${mission.priority.toLowerCase()}`;
        const progress = Math.round((mission.completed_steps / mission.total_steps) * 100);

        return `
            <div class="mission-card" data-mission-id="${mission.id}">
                <div class="mission-header">
                    <div class="mission-title">
                        ${this.getPriorityEmoji(mission.priority)} ${mission.name}
                    </div>
                    <span class="priority-badge ${priorityClass}">${mission.priority}</span>
                </div>
                <div class="mission-status">
                    Status: ${mission.status} • ${mission.completed_steps}/${mission.total_steps} steps
                </div>
                <div class="progress-container">
                    <div class="progress-info">
                        <span>Progress</span>
                        <span>${progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                </div>
            </div>
        `;
    }

    renderNextMission(nextMission) {
        const container = document.getElementById('next-mission');

        if (!nextMission) {
            container.innerHTML = '<div class="empty-state">No missions queued</div>';
            return;
        }

        container.innerHTML = `
            <div class="next-mission-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>🎯 ${nextMission.name}</strong>
                    <span class="priority-badge priority-${nextMission.priority.toLowerCase()}">
                        ${nextMission.priority}
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 8px;">
                    ${nextMission.total_steps} steps • Starts when current mission completes
                </div>
            </div>
        `;
    }

    renderSchedules(schedules) {
        const container = document.getElementById('schedules-list');

        if (!schedules || schedules.length === 0) {
            container.innerHTML = '<div class="empty-state">No scheduled tasks</div>';
            return;
        }

        container.innerHTML = schedules.map(schedule => `
            <div class="schedule-item">
                <div class="schedule-header">
                    <span class="schedule-task">⏰ ${schedule.name}</span>
                    <span class="schedule-time">${this.formatNextRun(schedule.next_run)}</span>
                </div>
                <div class="schedule-pattern">${schedule.pattern}</div>
            </div>
        `).join('');
    }

    renderResources(resources) {
        // API Quotas
        const apiContainer = document.getElementById('api-quotas');
        if (resources.api_quotas) {
            apiContainer.innerHTML = Object.entries(resources.api_quotas).map(([provider, quota]) => {
                const percentage = Math.round((quota.used / quota.limit) * 100);
                const status = this.getResourceStatus(percentage);

                return `
                    <div class="resource-item">
                        <div class="resource-label">
                            <span class="resource-name">${provider.toUpperCase()}</span>
                            <span class="resource-value">${quota.used}/${quota.limit}</span>
                        </div>
                        <div class="resource-bar">
                            <div class="resource-fill ${status}" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        // Disk Usage
        const diskContainer = document.getElementById('disk-usage');
        if (resources.disk) {
            const percentage = Math.round(resources.disk.used_percent);
            const status = this.getResourceStatus(percentage);

            diskContainer.innerHTML = `
                <div class="resource-item">
                    <div class="resource-label">
                        <span class="resource-name">Sandbox</span>
                        <span class="resource-value">${this.formatBytes(resources.disk.used)} / ${this.formatBytes(resources.disk.total)}</span>
                    </div>
                    <div class="resource-bar">
                        <div class="resource-fill ${status}" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }

        // System Resources
        const systemContainer = document.getElementById('system-resources');
        if (resources.system) {
            const cpuStatus = this.getResourceStatus(resources.system.cpu_percent);
            const memStatus = this.getResourceStatus(resources.system.memory_percent);

            systemContainer.innerHTML = `
                <div class="resource-item">
                    <div class="resource-label">
                        <span class="resource-name">CPU</span>
                        <span class="resource-value">${resources.system.cpu_percent.toFixed(1)}%</span>
                    </div>
                    <div class="resource-bar">
                        <div class="resource-fill ${cpuStatus}" style="width: ${resources.system.cpu_percent}%"></div>
                    </div>
                </div>
                <div class="resource-item">
                    <div class="resource-label">
                        <span class="resource-name">Memory</span>
                        <span class="resource-value">${resources.system.memory_percent.toFixed(1)}%</span>
                    </div>
                    <div class="resource-bar">
                        <div class="resource-fill ${memStatus}" style="width: ${resources.system.memory_percent}%"></div>
                    </div>
                </div>
            `;
        }
    }

    renderTimeline() {
        const container = document.getElementById('timeline-container');

        if (this.timeline.length === 0) {
            container.innerHTML = '<div class="empty-state">No recent events</div>';
            return;
        }

        container.innerHTML = this.timeline.slice(-this.config.maxTimelineItems).reverse().map(event => `
            <div class="timeline-item">
                <div class="timeline-time">${event.time}</div>
                <div class="timeline-content">
                    <div class="timeline-event">${event.event}</div>
                    ${event.details ? `<div class="timeline-details">${event.details}</div>` : ''}
                </div>
            </div>
        `).join('');
    }

    // Update Methods
    updateMission(mission) {
        const card = document.querySelector(`[data-mission-id="${mission.id}"]`);
        if (card) {
            const progress = Math.round((mission.completed_steps / mission.total_steps) * 100);
            const progressFill = card.querySelector('.progress-fill');
            const progressText = card.querySelector('.progress-info span:last-child');
            const statusText = card.querySelector('.mission-status');

            if (progressFill) progressFill.style.width = `${progress}%`;
            if (progressText) progressText.textContent = `${progress}%`;
            if (statusText) statusText.textContent = `Status: ${mission.status} • ${mission.completed_steps}/${mission.total_steps} steps`;
        }

        this.addTimelineEvent('🔄 Mission updated', mission.name);
    }

    updateResources(resources) {
        this.renderResources(resources);
    }

    handleMissionCompleted(mission) {
        this.showCelebration(mission);
        this.addTimelineEvent('✅ Mission completed', mission.name);
        setTimeout(() => this.loadMissions(), 1000);
    }

    showCelebration(mission) {
        const overlay = document.getElementById('celebration-overlay');
        const title = overlay.querySelector('h2');

        title.textContent = `Mission Complete: ${mission.name}`;
        overlay.classList.remove('hidden');

        setTimeout(() => {
            overlay.classList.add('hidden');
        }, this.config.celebrationDuration);
    }

    // Helper Methods
    addTimelineEvent(event, details = '') {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        this.timeline.push({ event, details, time, timestamp: now });

        // Keep only max items
        if (this.timeline.length > this.config.maxTimelineItems) {
            this.timeline = this.timeline.slice(-this.config.maxTimelineItems);
        }

        this.renderTimeline();
    }

    getPriorityEmoji(priority) {
        const emojis = {
            CRITICAL: '⚡',
            HIGH: '🔥',
            MEDIUM: '📊',
            LOW: '🔧'
        };
        return emojis[priority] || '📋';
    }

    getResourceStatus(percentage) {
        if (percentage >= 90) return 'critical';
        if (percentage >= 75) return 'warning';
        return 'ok';
    }

    formatNextRun(isoString) {
        if (!isoString) return 'Not scheduled';

        const date = new Date(isoString);
        const now = new Date();
        const diff = date - now;

        if (diff < 0) return 'Overdue';
        if (diff < 60000) return 'Starting soon';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
        return date.toLocaleDateString();
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
    }

    setupEventListeners() {
        // Close celebration overlay on click
        const overlay = document.getElementById('celebration-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                overlay.classList.add('hidden');
            });
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            if (this.ws && this.ws.readyState !== WebSocket.OPEN) {
                this.loadAllData();
            }
        }, this.config.autoRefresh);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new MissionControlDashboard();
});
