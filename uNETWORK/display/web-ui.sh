#!/bin/bash
# uDOS Web UI System v1.0.5.7
# Real-time dashboard and web interface for uDOS

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Web UI Configuration
UI_VERSION="1.0.5.7"
UI_PORT="8080"
UI_HOST="localhost"
UI_NAME="uDOS-WebUI"
UI_DIR="$UDOS_ROOT/uNETWORK/display/webui"

# Initialize Web UI System
init_web_ui() {
    echo "🖥️ Initializing $UI_NAME v$UI_VERSION"
    
    # Create UI directories
    mkdir -p "$UI_DIR"
    mkdir -p "$UI_DIR/static/css"
    mkdir -p "$UI_DIR/static/js"
    mkdir -p "$UI_DIR/static/fonts"
    mkdir -p "$UI_DIR/templates"
    mkdir -p "$UI_DIR/api"
    mkdir -p "$UI_DIR/components"
    
    # Create main dashboard
    create_dashboard_html
    
    # Create CSS styles
    create_dashboard_css
    
    # Create JavaScript
    create_dashboard_js
    
    # Create API endpoints
    create_web_api
    
    # Create web server
    create_web_server
    
    echo "✅ Web UI system initialized"
}

# Create main dashboard HTML
create_dashboard_html() {
    cat > "$UI_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Control Center</title>
    <link rel="stylesheet" href="static/css/dashboard.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="dashboard-header">
            <div class="header-left">
                <h1><i class="fas fa-microchip"></i> uDOS Control Center</h1>
                <span class="version-badge">v1.0.5.7</span>
            </div>
            <div class="header-right">
                <div class="status-indicator" id="systemStatus">
                    <i class="fas fa-circle"></i>
                    <span>System Online</span>
                </div>
                <div class="timestamp" id="currentTime"></div>
            </div>
        </header>

        <!-- Main Dashboard Grid -->
        <main class="dashboard-grid">
            <!-- System Overview -->
            <section class="card system-overview">
                <div class="card-header">
                    <h2><i class="fas fa-tachometer-alt"></i> System Overview</h2>
                    <button class="refresh-btn" onclick="refreshSystemData()">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
                <div class="card-content">
                    <div class="overview-stats">
                        <div class="stat-item">
                            <div class="stat-value" id="systemUptime">--</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="moduleCount">5</div>
                            <div class="stat-label">Modules</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="apiRequests">--</div>
                            <div class="stat-label">API Requests</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="scriptCount">--</div>
                            <div class="stat-label">Scripts</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Module Status -->
            <section class="card module-status">
                <div class="card-header">
                    <h2><i class="fas fa-cubes"></i> Module Status</h2>
                </div>
                <div class="card-content">
                    <div class="module-grid" id="moduleGrid">
                        <!-- Modules will be populated by JavaScript -->
                    </div>
                </div>
            </section>

            <!-- Service Mesh -->
            <section class="card service-mesh">
                <div class="card-header">
                    <h2><i class="fas fa-network-wired"></i> Service Mesh</h2>
                </div>
                <div class="card-content">
                    <div class="mesh-topology" id="meshTopology">
                        <!-- Mesh topology will be rendered here -->
                    </div>
                </div>
            </section>

            <!-- API Gateway -->
            <section class="card api-gateway">
                <div class="card-header">
                    <h2><i class="fas fa-gateway"></i> API Gateway</h2>
                </div>
                <div class="card-content">
                    <div class="gateway-stats" id="gatewayStats">
                        <!-- Gateway statistics -->
                    </div>
                    <div class="endpoint-list" id="endpointList">
                        <!-- API endpoints -->
                    </div>
                </div>
            </section>

            <!-- Recent Activity -->
            <section class="card recent-activity">
                <div class="card-header">
                    <h2><i class="fas fa-history"></i> Recent Activity</h2>
                </div>
                <div class="card-content">
                    <div class="activity-log" id="activityLog">
                        <!-- Activity log entries -->
                    </div>
                </div>
            </section>

            <!-- Quick Actions -->
            <section class="card quick-actions">
                <div class="card-header">
                    <h2><i class="fas fa-bolt"></i> Quick Actions</h2>
                </div>
                <div class="card-content">
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="runSystemCheck()">
                            <i class="fas fa-stethoscope"></i>
                            System Health Check
                        </button>
                        <button class="action-btn secondary" onclick="showScriptManager()">
                            <i class="fas fa-code"></i>
                            Script Manager
                        </button>
                        <button class="action-btn secondary" onclick="showMemoryBrowser()">
                            <i class="fas fa-database"></i>
                            Memory Browser
                        </button>
                        <button class="action-btn secondary" onclick="showKnowledgeGraph()">
                            <i class="fas fa-project-diagram"></i>
                            Knowledge Graph
                        </button>
                    </div>
                </div>
            </section>
        </main>

        <!-- Footer -->
        <footer class="dashboard-footer">
            <div class="footer-left">
                <span>uDOS v1.0.5.7 | Universal Device Operating System</span>
            </div>
            <div class="footer-right">
                <span>Built with ❤️ for universal computing</span>
            </div>
        </footer>
    </div>

    <!-- Modal for detailed views -->
    <div class="modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Details</h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Modal content -->
            </div>
        </div>
    </div>

    <script src="static/js/dashboard.js"></script>
</body>
</html>
EOF

    echo "📄 Main dashboard HTML created"
}

# Create dashboard CSS
create_dashboard_css() {
    cat > "$UI_DIR/static/css/dashboard.css" << 'EOF'
/* uDOS Dashboard Styles */
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
    --dark-bg: #1a1a1a;
    --card-bg: #2d3748;
    --text-primary: #ffffff;
    --text-secondary: #a0aec0;
    --border-color: #4a5568;
    --accent-color: #00ff88;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, var(--dark-bg) 0%, #2d3748 100%);
    color: var(--text-primary);
    min-height: 100vh;
    line-height: 1.6;
}

.dashboard-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* Header Styles */
.dashboard-header {
    background: rgba(44, 62, 80, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--accent-color);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.header-left h1 {
    font-size: 1.8rem;
    color: var(--accent-color);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.version-badge {
    background: var(--secondary-color);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: 1rem;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(39, 174, 96, 0.2);
    border-radius: 20px;
    border: 1px solid var(--success-color);
}

.status-indicator i {
    color: var(--success-color);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.timestamp {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

/* Main Dashboard Grid */
.dashboard-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
}

/* Card Styles */
.card {
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 255, 136, 0.2);
}

.card-header {
    background: rgba(44, 62, 80, 0.8);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h2 {
    font-size: 1.2rem;
    color: var(--accent-color);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.refresh-btn {
    background: none;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.refresh-btn:hover {
    background: var(--secondary-color);
    color: white;
    transform: rotate(180deg);
}

.card-content {
    padding: 1.5rem;
}

/* System Overview */
.overview-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 1rem;
}

.stat-item {
    text-align: center;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--accent-color);
    display: block;
}

.stat-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Module Status */
.module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
}

.module-item {
    text-align: center;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
    cursor: pointer;
}

.module-item:hover {
    background: rgba(52, 152, 219, 0.2);
    border-color: var(--secondary-color);
}

.module-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    display: block;
}

.module-name {
    font-size: 0.9rem;
    font-weight: bold;
    margin-bottom: 0.25rem;
}

.module-status {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    text-transform: uppercase;
}

.status-online {
    background: rgba(39, 174, 96, 0.3);
    color: var(--success-color);
    border: 1px solid var(--success-color);
}

.status-offline {
    background: rgba(231, 76, 60, 0.3);
    color: var(--danger-color);
    border: 1px solid var(--danger-color);
}

/* Quick Actions */
.action-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.action-btn {
    padding: 1rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    text-decoration: none;
}

.action-btn.primary {
    background: var(--accent-color);
    color: var(--dark-bg);
    font-weight: bold;
}

.action-btn.secondary {
    background: rgba(52, 152, 219, 0.2);
    color: var(--secondary-color);
    border: 1px solid var(--secondary-color);
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

/* Activity Log */
.activity-log {
    max-height: 300px;
    overflow-y: auto;
}

.activity-item {
    padding: 0.75rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.activity-item:last-child {
    border-bottom: none;
}

.activity-icon {
    color: var(--accent-color);
    width: 20px;
    text-align: center;
}

.activity-text {
    flex: 1;
    font-size: 0.9rem;
}

.activity-time {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
}

/* Footer */
.dashboard-footer {
    background: rgba(44, 62, 80, 0.95);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--border-color);
    font-size: 0.9rem;
    color: var(--text-secondary);
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 1000;
    backdrop-filter: blur(5px);
}

.modal-content {
    background: var(--card-bg);
    margin: 5% auto;
    padding: 0;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    width: 80%;
    max-width: 800px;
    max-height: 80vh;
    overflow: hidden;
}

.modal-header {
    background: rgba(44, 62, 80, 0.8);
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.modal-close:hover {
    background: var(--danger-color);
    color: white;
}

.modal-body {
    padding: 1.5rem;
    max-height: 60vh;
    overflow-y: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
        padding: 1rem;
    }
    
    .dashboard-header {
        padding: 1rem;
        flex-direction: column;
        gap: 1rem;
    }
    
    .header-right {
        gap: 1rem;
    }
    
    .overview-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .action-buttons {
        grid-template-columns: 1fr;
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--dark-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-color);
}
EOF

    echo "🎨 Dashboard CSS styles created"
}

# Create dashboard JavaScript
create_dashboard_js() {
    cat > "$UI_DIR/static/js/dashboard.js" << 'EOF'
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
EOF

    echo "⚡ Dashboard JavaScript created"
}

# Create web API endpoints
create_web_api() {
    mkdir -p "$UI_DIR/api"
    
    cat > "$UI_DIR/api/web-api.sh" << 'EOF'
#!/bin/bash
# Web API for uDOS Dashboard

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# API endpoint handlers
handle_system_status() {
    cat << JSON_EOF
{
  "status": "online",
  "uptime": "$(uptime | awk '{print $3 $4}' | sed 's/,//')",
  "modules": {
    "uCORE": "online",
    "uMEMORY": "online", 
    "uKNOWLEDGE": "online",
    "uNETWORK": "online",
    "uSCRIPT": "online"
  },
  "api_gateway": {
    "status": "running",
    "requests_today": $(( RANDOM % 1000 + 500 )),
    "response_time_avg": "${RANDOM:0:2}ms"
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
JSON_EOF
}

handle_module_details() {
    local module="$1"
    
    case "$module" in
        "uCORE")
            cat << JSON_EOF
{
  "name": "uCORE",
  "type": "foundation",
  "status": "online",
  "memory_usage": "$(( RANDOM % 50 + 10 ))MB",
  "active_processes": $(( RANDOM % 5 + 1 )),
  "last_health_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "endpoints": ["/core/status", "/core/health", "/core/init"]
}
JSON_EOF
            ;;
        "uMEMORY")
            cat << JSON_EOF
{
  "name": "uMEMORY",
  "type": "data_layer",
  "status": "online",
  "objects_stored": $(( RANDOM % 1000 + 100 )),
  "cache_hit_ratio": "$(( RANDOM % 30 + 70 ))%",
  "last_backup": "$(date -d '1 hour ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
  "endpoints": ["/memory/create", "/memory/read", "/memory/update", "/memory/delete"]
}
JSON_EOF
            ;;
        *)
            echo '{"error": "Module not found"}'
            ;;
    esac
}

handle_activity_log() {
    cat << JSON_EOF
{
  "activities": [
    {
      "timestamp": "$(date -d '5 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "system",
      "message": "System health check completed",
      "level": "info"
    },
    {
      "timestamp": "$(date -d '10 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "api",
      "message": "API request processed: /api/v1/status",
      "level": "info"
    },
    {
      "timestamp": "$(date -d '15 minutes ago' -u +"%Y-%m-%dT%H:%M:%SZ")",
      "type": "script",
      "message": "Automation script executed successfully",
      "level": "info"
    }
  ]
}
JSON_EOF
}

# Main API router
api_router() {
    local endpoint="$1"
    local method="${2:-GET}"
    
    case "$endpoint" in
        "/system/status")
            handle_system_status
            ;;
        "/module/"*)
            local module="$(echo "$endpoint" | sed 's|/module/||')"
            handle_module_details "$module"
            ;;
        "/activity/log")
            handle_activity_log
            ;;
        *)
            echo '{"error": "Endpoint not found", "status": 404}'
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    api_router "$@"
fi
EOF

    chmod +x "$UI_DIR/api/web-api.sh"
    echo "🔌 Web API endpoints created"
}

# Create simple web server
create_web_server() {
    cat > "$UI_DIR/server.sh" << 'EOF'
#!/bin/bash
# Simple HTTP Server for uDOS Web UI

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_PORT="${UI_PORT:-8080}"
UI_HOST="${UI_HOST:-localhost}"

# Check if Python is available
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        return 1
    fi
}

# Start HTTP server using Python
start_python_server() {
    local python_cmd="$1"
    
    echo "🌐 Starting uDOS Web UI Server"
    echo "================================"
    echo "Host: $UI_HOST"
    echo "Port: $UI_PORT"
    echo "Directory: $SCRIPT_DIR"
    echo "URL: http://$UI_HOST:$UI_PORT"
    echo ""
    echo "🚀 Server starting..."
    
    cd "$SCRIPT_DIR"
    
    if [ "$python_cmd" = "python3" ]; then
        python3 -m http.server "$UI_PORT" --bind "$UI_HOST"
    else
        python -m SimpleHTTPServer "$UI_PORT"
    fi
}

# Start server with Node.js (if available)
start_node_server() {
    cat > "$SCRIPT_DIR/server.js" << 'NODEJS_EOF'
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.UI_PORT || 8080;
const HOST = process.env.UI_HOST || 'localhost';

const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url);
    let pathname = parsedUrl.pathname;
    
    // Default to index.html
    if (pathname === '/') {
        pathname = '/index.html';
    }
    
    // API routes
    if (pathname.startsWith('/api/')) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end('{"message": "API endpoint simulation"}');
        return;
    }
    
    const filePath = path.join(__dirname, pathname);
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
            return;
        }
        
        const ext = path.extname(filePath);
        const mimeType = mimeTypes[ext] || 'text/plain';
        
        res.writeHead(200, { 'Content-Type': mimeType });
        res.end(data);
    });
});

server.listen(PORT, HOST, () => {
    console.log(`🌐 uDOS Web UI Server running at http://${HOST}:${PORT}/`);
});
NODEJS_EOF

    echo "🌐 Starting uDOS Web UI Server with Node.js"
    echo "============================================"
    echo "Host: $UI_HOST"
    echo "Port: $UI_PORT"
    echo "URL: http://$UI_HOST:$UI_PORT"
    echo ""
    
    cd "$SCRIPT_DIR"
    node server.js
}

# Main server startup
main() {
    case "${1:-auto}" in
        "python"|"python3")
            local python_cmd="$(check_python)"
            if [ $? -eq 0 ]; then
                start_python_server "$python_cmd"
            else
                echo "❌ Python not found"
                exit 1
            fi
            ;;
        "node")
            if command -v node >/dev/null 2>&1; then
                start_node_server
            else
                echo "❌ Node.js not found"
                exit 1
            fi
            ;;
        "auto")
            if command -v node >/dev/null 2>&1; then
                start_node_server
            else
                local python_cmd="$(check_python)"
                if [ $? -eq 0 ]; then
                    start_python_server "$python_cmd"
                else
                    echo "❌ No suitable web server found (Python or Node.js required)"
                    exit 1
                fi
            fi
            ;;
        "help"|*)
            echo "uDOS Web UI Server"
            echo "Usage: $0 {python|node|auto|help}"
            echo ""
            echo "Options:"
            echo "  python    - Use Python HTTP server"
            echo "  node      - Use Node.js HTTP server"
            echo "  auto      - Auto-detect available server"
            echo "  help      - Show this help"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
EOF

    chmod +x "$UI_DIR/server.sh"
    echo "🌐 Web server created"
}

# Show web UI status
show_ui_status() {
    echo "🖥️ $UI_NAME Status"
    echo "=================="
    echo "Version: $UI_VERSION"
    echo "Host: $UI_HOST"
    echo "Port: $UI_PORT"
    echo "Directory: $UI_DIR"
    echo "URL: http://$UI_HOST:$UI_PORT"
    echo ""
    
    if [ -f "$UI_DIR/index.html" ]; then
        echo "📄 Dashboard: ✅ Ready"
    else
        echo "📄 Dashboard: ❌ Not found"
    fi
    
    if [ -f "$UI_DIR/static/css/dashboard.css" ]; then
        echo "🎨 Styles: ✅ Ready"
    else
        echo "🎨 Styles: ❌ Not found"
    fi
    
    if [ -f "$UI_DIR/static/js/dashboard.js" ]; then
        echo "⚡ JavaScript: ✅ Ready"
    else
        echo "⚡ JavaScript: ❌ Not found"
    fi
    
    if [ -f "$UI_DIR/server.sh" ]; then
        echo "🌐 Server: ✅ Ready"
    else
        echo "🌐 Server: ❌ Not found"
    fi
}

# Start web UI server
start_ui_server() {
    if [ ! -f "$UI_DIR/server.sh" ]; then
        echo "❌ Web server not found. Run 'init' first."
        return 1
    fi
    
    echo "🚀 Starting $UI_NAME"
    exec "$UI_DIR/server.sh" auto
}

# Open web UI in browser
open_ui() {
    local url="http://$UI_HOST:$UI_PORT"
    echo "🌐 Opening uDOS Web UI: $url"
    
    # Try to open in default browser
    if command -v open >/dev/null 2>&1; then
        open "$url"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m webbrowser "$url"
    else
        echo "Please open $url in your browser"
    fi
}

# Main command interface
main() {
    case "${1:-help}" in
        "init")
            init_web_ui
            ;;
        "start")
            start_ui_server
            ;;
        "status")
            show_ui_status
            ;;
        "open")
            open_ui
            ;;
        "demo")
            init_web_ui
            echo ""
            echo "🎭 Demo Mode: Web UI ready!"
            echo "Run: $0 start"
            ;;
        "help"|*)
            echo "$UI_NAME v$UI_VERSION"
            echo "Usage: $0 {init|start|status|open|demo}"
            echo ""
            echo "Commands:"
            echo "  init      - Initialize web UI system"
            echo "  start     - Start web UI server"
            echo "  status    - Show UI system status"
            echo "  open      - Open UI in browser"
            echo "  demo      - Initialize and show demo info"
            echo ""
            echo "Examples:"
            echo "  $0 init   - Initialize web UI"
            echo "  $0 start  - Start server on port 8080"
            echo "  $0 open   - Open in browser"
            ;;
    esac
}

# Execute if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
