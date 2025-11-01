// uDOS Web Dashboard JavaScript

// Log to dashboard
function log(message, type = 'info') {
    const logsContainer = document.getElementById('logs');
    const entry = document.createElement('p');
    entry.className = `log-entry ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    logsContainer.appendChild(entry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Check status of all servers via API
async function checkAllStatus() {
    log('Checking all servers via API...');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success) {
            data.servers.forEach(server => {
                updateServerCard(server);
            });
            log(`✓ Status check complete (${data.servers.length} servers checked)`, 'info');
        } else {
            log(`✗ Status check failed: ${data.error}`, 'error');
        }
    } catch (error) {
        log(`✗ API error: ${error.message}`, 'error');
    }
}

// Update a server card with status info
function updateServerCard(server) {
    const card = document.querySelector(`[data-extension="${server.id}"]`);
    if (!card) return;

    const statusElement = card.querySelector('.card-status');
    const indicator = statusElement.querySelector('.status-indicator');
    const text = statusElement.querySelector('.status-text');
    const primaryBtn = card.querySelector('.btn-primary');
    const secondaryBtn = card.querySelector('.btn-secondary');

    // Update visual status
    if (!server.installed) {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        text.textContent = 'Not Installed';
        text.style.color = '#ff6b6b';
        primaryBtn.disabled = true;
        primaryBtn.textContent = 'Not Installed';
        secondaryBtn.disabled = true;
    } else if (server.running) {
        indicator.classList.add('online');
        indicator.classList.remove('offline');
        text.textContent = `Online (${formatUptime(server.uptime)})`;
        text.style.color = '#00ff88';
        primaryBtn.disabled = false;
        primaryBtn.textContent = 'Open';
        primaryBtn.onclick = () => openExtension(server.id, server.url);
        secondaryBtn.disabled = false;
        secondaryBtn.textContent = 'Stop';
        secondaryBtn.onclick = () => stopServer(server.id);
    } else {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        text.textContent = 'Offline';
        text.style.color = '#666';
        primaryBtn.disabled = false;
        primaryBtn.textContent = 'Start';
        primaryBtn.onclick = () => startServer(server.id);
        secondaryBtn.disabled = false;
        secondaryBtn.textContent = 'Check';
        secondaryBtn.onclick = () => checkAllStatus();
    }

    // Store server info on card for later use
    card.dataset.serverInfo = JSON.stringify(server);
}

// Format uptime in human-readable format
function formatUptime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
}

// Start a server via API
async function startServer(serverName) {
    log(`Starting ${serverName}...`);

    const btn = document.querySelector(`[data-extension="${serverName}"] .btn-primary`);
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Starting...';

    try {
        const response = await fetch(`/api/start/${serverName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                no_browser: true  // Don't auto-open browser from API
            })
        });

        const data = await response.json();

        if (data.success) {
            log(`✓ ${serverName} started successfully`, 'info');
            // Wait a moment then check status
            setTimeout(() => {
                checkAllStatus();
            }, 1500);
        } else {
            log(`✗ Failed to start ${serverName}: ${data.message}`, 'error');
            btn.disabled = false;
            btn.textContent = originalText;
        }
    } catch (error) {
        log(`✗ API error: ${error.message}`, 'error');
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// Stop a server via API
async function stopServer(serverName) {
    log(`Stopping ${serverName}...`);

    const btn = document.querySelector(`[data-extension="${serverName}"] .btn-secondary`);
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Stopping...';

    try {
        const response = await fetch(`/api/stop/${serverName}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            log(`✓ ${serverName} stopped successfully`, 'info');
            checkAllStatus();
        } else {
            log(`✗ Failed to stop ${serverName}: ${data.message}`, 'error');
            btn.disabled = false;
            btn.textContent = originalText;
        }
    } catch (error) {
        log(`✗ API error: ${error.message}`, 'error');
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// Open an extension in a new tab
function openExtension(serverName, url) {
    log(`Opening ${serverName} at ${url}...`);
    window.open(url, '_blank');
}

// Stop all extensions
function stopAll() {
    log('To stop all servers, use: OUTPUT STOP <name> in uDOS CLI', 'warning');

    // Or we could iterate and stop each running server
    const cards = document.querySelectorAll('.extension-card');
    const runningServers = [];

    cards.forEach(card => {
        const serverInfo = card.dataset.serverInfo;
        if (serverInfo) {
            const server = JSON.parse(serverInfo);
            if (server.running) {
                runningServers.push(server.id);
            }
        }
    });

    if (runningServers.length > 0) {
        if (confirm(`Stop ${runningServers.length} running server(s)?`)) {
            runningServers.forEach(serverId => {
                stopServer(serverId);
            });
        }
    } else {
        log('No servers currently running', 'info');
    }
}

// Refresh dashboard
function refreshDashboard() {
    log('Refreshing dashboard...');
    location.reload();
}

// Auto-check status on load
window.addEventListener('load', () => {
    log('uDOS Web Dashboard initialized');
    log('Checking extension status...');

    setTimeout(() => {
        checkAllStatus();
    }, 500);

    // Auto-refresh status every 30 seconds
    setInterval(() => {
        checkAllStatus();
    }, 30000);
});

// Keyboard shortcut (Ctrl+Q to show help)
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'q') {
        e.preventDefault();
        log('Tip: Use OUTPUT commands in uDOS CLI to manage outputs', 'info');
    }
});
