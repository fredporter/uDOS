/**
 * uDOS Dashboard - Real-time Updates
 * v1.1.14
 */

const REFRESH_INTERVAL = 5000; // 5 seconds

// Update timestamp display
function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('timestamp').textContent = timeString;
}

// Fetch and update dashboard data
async function updateDashboard() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update missions
        updateMissions(data.missions);

        // Update checklists
        updateChecklists(data.checklists);

        // Update workflow
        updateWorkflow(data.workflow);

        // Update XP
        updateXP(data.xp);

        // Update timestamp
        updateTimestamp();

    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

function updateMissions(missions) {
    const container = document.getElementById('missions-container');

    if (!missions.active_missions || missions.active_missions.length === 0) {
        container.innerHTML = '<div class="stat"><span class="stat-label">No active missions</span></div>';
    } else {
        container.innerHTML = missions.active_missions.map(mission => `
            <div class="mission-item">
                <div class="mission-header">
                    <span class="priority-${mission.priority}">${mission.title}</span>
                    <span class="stat-value">${mission.progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${mission.progress}%"></div>
                    <div class="progress-text">${mission.completed_steps}/${mission.total_steps} steps</div>
                </div>
            </div>
        `).join('');
    }

    document.getElementById('total-missions').textContent = missions.total_missions;
    document.getElementById('completed-missions').textContent = missions.completed_missions;
}

function updateChecklists(checklists) {
    const container = document.getElementById('checklists-container');

    if (!checklists.active_checklists || checklists.active_checklists.length === 0) {
        container.innerHTML = '<div class="stat"><span class="stat-label">No active checklists</span></div>';
    } else {
        container.innerHTML = checklists.active_checklists.map(checklist => `
            <div class="checklist-item">
                <div style="margin-bottom: 5px;">${checklist.title}</div>
                <div class="progress-bar" style="height: 20px;">
                    <div class="progress-fill" style="width: ${checklist.progress}%"></div>
                    <div class="progress-text" style="font-size: 9px;">${checklist.completed_items}/${checklist.total_items}</div>
                </div>
            </div>
        `).join('');
    }

    document.getElementById('total-items').textContent = checklists.total_items;
    document.getElementById('completed-items').textContent = checklists.total_completed;
}

function updateWorkflow(workflow) {
    const currentWorkflow = workflow.current_workflow || 'None';
    const phase = workflow.phase || 'IDLE';

    document.getElementById('current-workflow').textContent = currentWorkflow;
    document.getElementById('workflow-phase').textContent = phase;
    document.getElementById('checkpoints').textContent = workflow.checkpoints_saved || 0;
    document.getElementById('perfect-streak').textContent = workflow.perfect_streak || 0;

    // Update phase status color
    const phaseElement = document.getElementById('workflow-phase');
    if (phase === 'IDLE') {
        phaseElement.className = 'stat-value status-idle';
    } else {
        phaseElement.className = 'stat-value status-active';
    }
}

function updateXP(xp) {
    document.getElementById('total-xp').textContent = `${xp.total_xp} XP`;

    const achievementsContainer = document.getElementById('achievements-container');

    if (!xp.achievements || xp.achievements.length === 0) {
        achievementsContainer.innerHTML = '<div style="font-size: 10px; color: #6c757d;">No achievements yet</div>';
    } else {
        achievementsContainer.innerHTML = xp.achievements.map(achievement => `
            <div class="achievement">🏆 ${achievement}</div>
        `).join('');
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    updateDashboard();

    // Set up auto-refresh
    setInterval(updateDashboard, REFRESH_INTERVAL);

    console.log('🎮 uDOS Dashboard initialized');
    console.log(`Auto-refresh enabled: ${REFRESH_INTERVAL/1000}s`);
});
