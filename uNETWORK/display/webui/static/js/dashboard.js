// uDOS Dashboard JavaScript
class uDOSDashboard {
    constructor() {
        this.apiBase = '/api/v1';
        this.refreshInterval = 30000; // 30 seconds
        this.init();
    }

    async init() {
        console.log('🚀 Initializing uDOS Dashboard');
        
        // Update timestamp
        this.updateTimestamp();
        setInterval(() => this.updateTimestamp(), 1000);
        
        // Load initial data
        await this.loadSystemData();
        await this.loadModuleStatus();
        await this.loadActivityLog();
        
        // Start auto-refresh
        setInterval(() => this.refreshDashboard(), this.refreshInterval);
        
        console.log('✅ Dashboard initialized');
    }

    updateTimestamp() {
        const now = new Date();
        const timestamp = now.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            timeElement.textContent = timestamp;
        }
    }

    async loadSystemData() {
        try {
            // Simulate API calls (would be real in production)
            const systemData = {
                uptime: this.calculateUptime(),
                moduleCount: 5,
                apiRequests: Math.floor(Math.random() * 1000) + 500,
                scriptCount: Math.floor(Math.random() * 50) + 20
            };

            // Update system overview
            document.getElementById('systemUptime').textContent = systemData.uptime;
            document.getElementById('moduleCount').textContent = systemData.moduleCount;
            document.getElementById('apiRequests').textContent = systemData.apiRequests;
            document.getElementById('scriptCount').textContent = systemData.scriptCount;

        } catch (error) {
            console.error('Failed to load system data:', error);
        }
    }

    async loadModuleStatus() {
        const modules = [
            { name: 'uCORE', icon: 'fas fa-microchip', status: 'online', type: 'foundation' },
            { name: 'uMEMORY', icon: 'fas fa-database', status: 'online', type: 'data' },
            { name: 'uKNOWLEDGE', icon: 'fas fa-brain', status: 'online', type: 'graph' },
            { name: 'uNETWORK', icon: 'fas fa-network-wired', status: 'online', type: 'services' },
            { name: 'uSCRIPT', icon: 'fas fa-code', status: 'online', type: 'automation' }
        ];

        const moduleGrid = document.getElementById('moduleGrid');
        if (moduleGrid) {
            moduleGrid.innerHTML = modules.map(module => `
                <div class="module-item" onclick="showModuleDetails('${module.name}')">
                    <i class="module-icon ${module.icon}"></i>
                    <div class="module-name">${module.name}</div>
                    <div class="module-status status-${module.status}">${module.status}</div>
                </div>
            `).join('');
        }

        // Update service mesh
        this.updateServiceMesh();
        
        // Update API gateway stats
        this.updateApiGateway();
    }

    updateServiceMesh() {
        const meshTopology = document.getElementById('meshTopology');
        if (meshTopology) {
            meshTopology.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 1.5rem; margin-bottom: 1rem;">
                        <i class="fas fa-sitemap" style="color: var(--accent-color);"></i>
                    </div>
                    <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">Service Mesh Active</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                        5 services registered<br>
                        Load balancing: Round-robin<br>
                        Health checks: Active
                    </div>
                </div>
            `;
        }
    }

    updateApiGateway() {
        const gatewayStats = document.getElementById('gatewayStats');
        const endpointList = document.getElementById('endpointList');
        
        if (gatewayStats) {
            gatewayStats.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 6px;">
                        <div style="font-size: 1.5rem; color: var(--accent-color);">${Math.floor(Math.random() * 100) + 50}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">Requests/min</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 6px;">
                        <div style="font-size: 1.5rem; color: var(--success-color);">99.9%</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">Uptime</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 6px;">
                        <div style="font-size: 1.5rem; color: var(--secondary-color);">${Math.floor(Math.random() * 20) + 5}ms</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">Avg Response</div>
                    </div>
                </div>
            `;
        }

        if (endpointList) {
            const endpoints = [
                '/api/v1/health',
                '/api/v1/status',
                '/api/v1/memory/*',
                '/api/v1/knowledge/*',
                '/api/v1/scripts/*'
            ];

            endpointList.innerHTML = `
                <div style="font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--text-secondary);">Active Endpoints:</div>
                ${endpoints.map(endpoint => `
                    <div style="padding: 0.5rem; margin: 0.25rem 0; background: rgba(0,0,0,0.2); border-radius: 4px; font-family: monospace; font-size: 0.8rem;">
                        <span style="color: var(--success-color);">●</span> ${endpoint}
                    </div>
                `).join('')}
            `;
        }
    }

    async loadActivityLog() {
        const activities = [
            { icon: 'fas fa-power-off', text: 'System startup completed', time: '09:15:32' },
            { icon: 'fas fa-check', text: 'All modules initialized successfully', time: '09:15:45' },
            { icon: 'fas fa-network-wired', text: 'Service mesh activated', time: '09:16:01' },
            { icon: 'fas fa-shield-alt', text: 'API gateway security enabled', time: '09:16:15' },
            { icon: 'fas fa-sync', text: 'Auto-refresh interval set to 30s', time: '09:16:30' }
        ];

        const activityLog = document.getElementById('activityLog');
        if (activityLog) {
            activityLog.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <i class="activity-icon ${activity.icon}"></i>
                    <div class="activity-text">${activity.text}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            `).join('');
        }
    }

    calculateUptime() {
        // Simulate uptime calculation
        const hours = Math.floor(Math.random() * 24) + 1;
        const minutes = Math.floor(Math.random() * 60);
        return `${hours}h ${minutes}m`;
    }

    async refreshDashboard() {
        console.log('🔄 Refreshing dashboard data...');
        await this.loadSystemData();
        await this.loadModuleStatus();
        
        // Add visual feedback
        const statusIndicator = document.querySelector('.status-indicator i');
        if (statusIndicator) {
            statusIndicator.style.color = 'var(--warning-color)';
            setTimeout(() => {
                statusIndicator.style.color = 'var(--success-color)';
            }, 500);
        }
    }
}

// Global functions for UI interactions
function refreshSystemData() {
    if (window.dashboard) {
        window.dashboard.refreshDashboard();
    }
}

function showModuleDetails(moduleName) {
    const modal = document.getElementById('detailModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = `${moduleName} Module Details`;
    modalBody.innerHTML = `
        <div style="padding: 1rem;">
            <h3 style="color: var(--accent-color); margin-bottom: 1rem;">${moduleName} Status</h3>
            <div style="display: grid; gap: 1rem;">
                <div>
                    <strong>Status:</strong> <span style="color: var(--success-color);">Online</span>
                </div>
                <div>
                    <strong>Last Health Check:</strong> ${new Date().toLocaleTimeString()}
                </div>
                <div>
                    <strong>Memory Usage:</strong> ${Math.floor(Math.random() * 50) + 10}MB
                </div>
                <div>
                    <strong>Active Connections:</strong> ${Math.floor(Math.random() * 10) + 1}
                </div>
                <div style="margin-top: 1rem;">
                    <button class="action-btn primary" onclick="restartModule('${moduleName}')">
                        <i class="fas fa-restart"></i> Restart Module
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'none';
}

function runSystemCheck() {
    alert('🔍 Running system health check...\n\n✅ All systems operational\n✅ All modules responding\n✅ API gateway healthy\n✅ Service mesh active');
}

function showScriptManager() {
    showModuleDetails('Script Manager');
}

function showMemoryBrowser() {
    showModuleDetails('Memory Browser');
}

function showKnowledgeGraph() {
    showModuleDetails('Knowledge Graph');
}

function restartModule(moduleName) {
    alert(`🔄 Restarting ${moduleName} module...\n\n✅ Module restarted successfully`);
    closeModal();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new uDOSDashboard();
});
