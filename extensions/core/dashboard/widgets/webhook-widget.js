/**
 * Webhook Management Widget for uDOS Dashboard v1.2.5
 *
 * Features:
 * - List registered webhooks
 * - Register new webhooks
 * - Test webhook endpoints
 * - View event logs
 * - Delete webhooks
 */

class WebhookWidget {
    constructor(container, config = {}) {
        this.container = container;
        this.config = config;
        this.webhooks = [];
        this.apiUrl = config.apiUrl || 'http://localhost:5000';
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.render();
        this.loadWebhooks();

        // Auto-refresh every 30 seconds
        if (this.config.autoRefresh !== false) {
            this.refreshInterval = setInterval(() => this.loadWebhooks(), 30000);
        }
    }

    async loadWebhooks() {
        try {
            const response = await fetch(`${this.apiUrl}/api/webhooks/list`);
            const data = await response.json();

            if (data.status === 'success') {
                this.webhooks = data.webhooks;
                this.updateWebhookList();
                this.updateStats();
            }
        } catch (error) {
            console.error('Failed to load webhooks:', error);
            this.showError('Failed to load webhooks');
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="webhook-widget nes-container is-dark">
                <div class="widget-header">
                    <h3 class="widget-title">🪝 Webhooks</h3>
                    <div class="widget-controls">
                        <button class="nes-btn is-small is-primary" onclick="webhookWidget.showRegisterModal()">
                            ➕ Register
                        </button>
                        <button class="nes-btn is-small" onclick="webhookWidget.refresh()">
                            🔄
                        </button>
                    </div>
                </div>

                <div class="webhook-stats">
                    <div class="stat-box">
                        <div class="stat-label">Total</div>
                        <div class="stat-value" id="webhook-total">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Active</div>
                        <div class="stat-value nes-text is-success" id="webhook-active">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Triggers</div>
                        <div class="stat-value nes-text is-primary" id="webhook-triggers">0</div>
                    </div>
                </div>

                <div class="webhook-list" id="webhook-list">
                    <div class="loading-message">Loading webhooks...</div>
                </div>
            </div>

            <!-- Register Modal -->
            <div id="webhook-register-modal" class="modal" style="display: none;">
                <div class="modal-content nes-container is-dark with-title">
                    <h3 class="title">🪝 Register Webhook</h3>
                    <button class="modal-close nes-btn is-error" onclick="webhookWidget.closeRegisterModal()">✕</button>

                    <div class="modal-body">
                        <div class="nes-field">
                            <label for="webhook-platform">Platform</label>
                            <div class="nes-select">
                                <select id="webhook-platform">
                                    <option value="github">GitHub</option>
                                    <option value="slack">Slack</option>
                                    <option value="notion">Notion</option>
                                    <option value="clickup">ClickUp</option>
                                </select>
                            </div>
                        </div>

                        <div class="nes-field">
                            <label for="webhook-events">Events (comma-separated)</label>
                            <input type="text" id="webhook-events" class="nes-input"
                                   placeholder="push, pull_request, release" />
                        </div>

                        <div class="nes-field">
                            <label for="webhook-workflow">Workflow (optional)</label>
                            <input type="text" id="webhook-workflow" class="nes-input"
                                   placeholder="knowledge-quality-scan" />
                        </div>

                        <div class="modal-actions">
                            <button class="nes-btn is-primary" onclick="webhookWidget.registerWebhook()">
                                ✅ Register
                            </button>
                            <button class="nes-btn" onclick="webhookWidget.closeRegisterModal()">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add widget styles
        this.addStyles();
    }

    updateWebhookList() {
        const listEl = document.getElementById('webhook-list');

        if (this.webhooks.length === 0) {
            listEl.innerHTML = '<div class="empty-message">No webhooks registered</div>';
            return;
        }

        listEl.innerHTML = this.webhooks.map(wh => `
            <div class="webhook-item ${wh.enabled ? 'webhook-enabled' : 'webhook-disabled'}">
                <div class="webhook-info">
                    <div class="webhook-platform">
                        ${this.getPlatformIcon(wh.platform)} ${wh.platform.toUpperCase()}
                    </div>
                    <div class="webhook-id">${wh.id}</div>
                    <div class="webhook-events">
                        ${wh.events.map(e => `<span class="event-tag">${e}</span>`).join('')}
                    </div>
                </div>
                <div class="webhook-stats-inline">
                    <span class="stat-item">
                        🔔 ${wh.trigger_count} triggers
                    </span>
                    <span class="stat-item ${wh.enabled ? 'nes-text is-success' : 'nes-text is-disabled'}">
                        ${wh.enabled ? '✅ Active' : '❌ Disabled'}
                    </span>
                </div>
                <div class="webhook-actions">
                    <button class="nes-btn is-small" onclick="webhookWidget.testWebhook('${wh.id}')">
                        🧪 Test
                    </button>
                    <button class="nes-btn is-small is-error" onclick="webhookWidget.deleteWebhook('${wh.id}')">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateStats() {
        const total = this.webhooks.length;
        const active = this.webhooks.filter(wh => wh.enabled).length;
        const triggers = this.webhooks.reduce((sum, wh) => sum + wh.trigger_count, 0);

        document.getElementById('webhook-total').textContent = total;
        document.getElementById('webhook-active').textContent = active;
        document.getElementById('webhook-triggers').textContent = triggers;
    }

    getPlatformIcon(platform) {
        const icons = {
            github: '🐙',
            slack: '💬',
            notion: '📝',
            clickup: '✓'
        };
        return icons[platform] || '🪝';
    }

    showRegisterModal() {
        document.getElementById('webhook-register-modal').style.display = 'flex';
    }

    closeRegisterModal() {
        document.getElementById('webhook-register-modal').style.display = 'none';
    }

    async registerWebhook() {
        const platform = document.getElementById('webhook-platform').value;
        const eventsStr = document.getElementById('webhook-events').value;
        const workflow = document.getElementById('webhook-workflow').value;

        const events = eventsStr.split(',').map(e => e.trim()).filter(e => e);

        if (events.length === 0) {
            alert('Please enter at least one event');
            return;
        }

        const actions = workflow ? [{
            event: events[0],
            workflow: workflow,
            args: {}
        }] : [];

        try {
            const response = await fetch(`${this.apiUrl}/api/webhooks/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform, events, actions })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showSuccess(`Webhook registered! ID: ${data.webhook.id}`);
                this.closeRegisterModal();
                this.loadWebhooks();

                // Show webhook details
                this.showWebhookDetails(data.webhook);
            } else {
                this.showError(data.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showError('Failed to register webhook');
        }
    }

    async testWebhook(webhookId) {
        try {
            const response = await fetch(`${this.apiUrl}/api/webhooks/test/${webhookId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event: 'test',
                    test_data: { test: true, timestamp: new Date().toISOString() }
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showSuccess(`Test successful! Found ${data.actions_found} actions`);
            } else {
                this.showError(data.message || 'Test failed');
            }
        } catch (error) {
            console.error('Test error:', error);
            this.showError('Failed to test webhook');
        }
    }

    async deleteWebhook(webhookId) {
        if (!confirm(`Delete webhook ${webhookId}?`)) return;

        try {
            const response = await fetch(`${this.apiUrl}/api/webhooks/delete/${webhookId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.showSuccess('Webhook deleted');
                this.loadWebhooks();
            } else {
                this.showError(data.message || 'Deletion failed');
            }
        } catch (error) {
            console.error('Deletion error:', error);
            this.showError('Failed to delete webhook');
        }
    }

    showWebhookDetails(webhook) {
        const details = `
Webhook Registered Successfully!

ID: ${webhook.id}
Platform: ${webhook.platform}
URL: ${webhook.url}
Secret: ${webhook.secret}

⚠️ Important: Save the secret key securely!
Configure your ${webhook.platform} webhook with:
- URL: ${webhook.url}
- Secret: ${webhook.secret}
- Events: ${webhook.events.join(', ')}
        `.trim();

        alert(details);
    }

    refresh() {
        this.loadWebhooks();
    }

    showSuccess(message) {
        // Use NES.css dialog if available, otherwise alert
        if (typeof dialogToast !== 'undefined') {
            dialogToast(message, 'success');
        } else {
            alert(`✅ ${message}`);
        }
    }

    showError(message) {
        if (typeof dialogToast !== 'undefined') {
            dialogToast(message, 'error');
        } else {
            alert(`❌ ${message}`);
        }
    }

    addStyles() {
        if (document.getElementById('webhook-widget-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'webhook-widget-styles';
        styles.textContent = `
            .webhook-widget {
                height: 100%;
                display: flex;
                flex-direction: column;
            }

            .widget-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }

            .widget-title {
                margin: 0;
                font-size: 1.2rem;
            }

            .widget-controls {
                display: flex;
                gap: 0.5rem;
            }

            .webhook-stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .stat-box {
                text-align: center;
                padding: 0.5rem;
                background: rgba(0, 0, 0, 0.3);
                border: 2px solid #209cee;
            }

            .stat-label {
                font-size: 0.8rem;
                opacity: 0.8;
            }

            .stat-value {
                font-size: 1.5rem;
                font-weight: bold;
            }

            .webhook-list {
                flex: 1;
                overflow-y: auto;
                padding: 0.5rem;
                background: rgba(0, 0, 0, 0.2);
            }

            .webhook-item {
                padding: 1rem;
                margin-bottom: 0.5rem;
                border: 2px solid #209cee;
                background: rgba(32, 156, 238, 0.1);
            }

            .webhook-item.webhook-disabled {
                opacity: 0.5;
                border-color: #666;
            }

            .webhook-platform {
                font-weight: bold;
                font-size: 1.1rem;
                margin-bottom: 0.25rem;
            }

            .webhook-id {
                font-size: 0.8rem;
                opacity: 0.7;
                margin-bottom: 0.5rem;
            }

            .webhook-events {
                margin-bottom: 0.5rem;
            }

            .event-tag {
                display: inline-block;
                padding: 0.2rem 0.5rem;
                margin-right: 0.25rem;
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid #209cee;
                font-size: 0.8rem;
            }

            .webhook-stats-inline {
                display: flex;
                gap: 1rem;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }

            .webhook-actions {
                display: flex;
                gap: 0.5rem;
            }

            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }

            .modal-content {
                position: relative;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }

            .modal-close {
                position: absolute;
                top: 1rem;
                right: 1rem;
            }

            .modal-body {
                margin-top: 1rem;
            }

            .modal-actions {
                display: flex;
                gap: 0.5rem;
                margin-top: 1rem;
                justify-content: flex-end;
            }

            .nes-field {
                margin-bottom: 1rem;
            }

            .loading-message,
            .empty-message {
                text-align: center;
                padding: 2rem;
                opacity: 0.6;
            }
        `;
        document.head.appendChild(styles);
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Register widget with dashboard builder
if (typeof dashboardBuilder !== 'undefined') {
    dashboardBuilder.registerWidget({
        id: 'webhook-manager',
        name: 'Webhook Manager',
        description: 'Manage GitHub/Slack/Notion webhooks',
        icon: '🪝',
        category: 'automation',
        defaultSize: { width: 6, height: 4 },
        factory: (container, config) => new WebhookWidget(container, config)
    });
}

// Global instance for easy access
let webhookWidget = null;
