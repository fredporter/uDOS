// Additional metric update functions
function updateCPUDetails(cpuData) {
    const cpuCard = document.getElementById('cpu-usage');
    const detailsDiv = cpuCard.querySelector('.metric-details') || createDetailsDiv(cpuCard);

    detailsDiv.innerHTML = `
        <div class="detail-item">
            <span>Cores:</span> ${cpuData.count}
        </div>
        ${cpuData.freq ? `
        <div class="detail-item">
            <span>Frequency:</span> ${(cpuData.freq.current / 1000).toFixed(2)} GHz
        </div>` : ''}
    `;
}

function updateMemoryDetails(memData) {
    const memCard = document.getElementById('memory-usage');
    const detailsDiv = memCard.querySelector('.metric-details') || createDetailsDiv(memCard);

    const totalGB = (memData.total / (1024 * 1024 * 1024)).toFixed(2);
    const usedGB = (memData.used / (1024 * 1024 * 1024)).toFixed(2);

    detailsDiv.innerHTML = `
        <div class="detail-item">
            <span>Total:</span> ${totalGB} GB
        </div>
        <div class="detail-item">
            <span>Used:</span> ${usedGB} GB
        </div>
    `;
}

function updateDiskDetails(diskData) {
    const diskCard = document.getElementById('disk-usage');
    const detailsDiv = diskCard.querySelector('.metric-details') || createDetailsDiv(diskCard);

    const totalGB = (diskData.total / (1024 * 1024 * 1024)).toFixed(2);
    const freeGB = (diskData.free / (1024 * 1024 * 1024)).toFixed(2);

    detailsDiv.innerHTML = `
        <div class="detail-item">
            <span>Total:</span> ${totalGB} GB
        </div>
        <div class="detail-item">
            <span>Free:</span> ${freeGB} GB
        </div>
    `;
}

function updateProcessList(processes) {
    const processList = document.getElementById('process-list') || createProcessList();

    processList.innerHTML = `
        <h3>Top Processes</h3>
        <table class="process-table">
            <thead>
                <tr>
                    <th>PID</th>
                    <th>Name</th>
                    <th>CPU %</th>
                    <th>Memory %</th>
                </tr>
            </thead>
            <tbody>
                ${processes.map(proc => `
                    <tr>
                        <td>${proc.pid}</td>
                        <td>${proc.name}</td>
                        <td>${proc.cpu_percent?.toFixed(1) || 0}</td>
                        <td>${proc.memory_percent?.toFixed(1) || 0}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function updateNetworkStats(netData) {
    const netStats = document.getElementById('network-stats') || createNetworkStats();

    const mbSent = (netData.bytes_sent / (1024 * 1024)).toFixed(2);
    const mbRecv = (netData.bytes_recv / (1024 * 1024)).toFixed(2);

    netStats.innerHTML = `
        <h3>Network Traffic</h3>
        <div class="network-stats-grid">
            <div class="stat-item">
                <span>Sent:</span> ${mbSent} MB
            </div>
            <div class="stat-item">
                <span>Received:</span> ${mbRecv} MB
            </div>
            <div class="stat-item">
                <span>Packets Sent:</span> ${netData.packets_sent}
            </div>
            <div class="stat-item">
                <span>Packets Received:</span> ${netData.packets_recv}
            </div>
        </div>
    `;
}

function createDetailsDiv(parentElement) {
    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'metric-details';
    parentElement.appendChild(detailsDiv);
    return detailsDiv;
}

function createProcessList() {
    const processList = document.createElement('div');
    processList.id = 'process-list';
    document.querySelector('.metrics-panel').appendChild(processList);
    return processList;
}

function createNetworkStats() {
    const netStats = document.createElement('div');
    netStats.id = 'network-stats';
    document.querySelector('.metrics-panel').appendChild(netStats);
    return netStats;
}
