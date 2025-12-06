"""
Webhook Test Panel

Interactive web-based UI for testing webhook integration system.
Provides payload generation, signature verification, and event simulation.

Features:
- Generate realistic webhook payloads
- Test HMAC signature verification
- Simulate webhook delivery
- View event history
- Inspect route matching
- Debug event processing

Usage:
    from extensions.core.webhooks.test_panel import WebhookTestPanel

    panel = WebhookTestPanel(api_url="http://localhost:5090")
    panel.run(port=5091)

    # Open browser to http://localhost:5091
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS

from .simulator import WebhookSimulator
from .client import WebhookClient


class WebhookTestPanel:
    """Interactive web UI for webhook testing."""

    HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webhook Test Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .panel {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }

        select, input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }

        select:focus, input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea {
            font-family: 'Courier New', monospace;
            resize: vertical;
            min-height: 200px;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: 500;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            margin-left: 10px;
        }

        .response {
            background: #f8f9fa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }

        .response pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .success { color: #28a745; }
        .error { color: #dc3545; }
        .warning { color: #ffc107; }

        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }

        .status-success { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .event-list {
            list-style: none;
        }

        .event-item {
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }

        .event-meta {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Webhook Test Panel</h1>

        <!-- Statistics -->
        <div class="panel">
            <h2>System Statistics</h2>
            <div class="grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalEvents">-</div>
                    <div class="stat-label">Total Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="activeRoutes">-</div>
                    <div class="stat-label">Active Routes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="errorCount">-</div>
                    <div class="stat-label">Errors</div>
                </div>
            </div>
        </div>

        <!-- Event Generator -->
        <div class="panel">
            <h2>Generate & Send Event</h2>
            <div class="form-group">
                <label for="platform">Platform:</label>
                <select id="platform" onchange="updateEventTypes()">
                    <option value="github">GitHub</option>
                    <option value="slack">Slack</option>
                    <option value="notion">Notion</option>
                    <option value="clickup">ClickUp</option>
                </select>
            </div>

            <div class="form-group">
                <label for="eventType">Event Type:</label>
                <select id="eventType"></select>
            </div>

            <div class="form-group">
                <label for="customParams">Custom Parameters (JSON):</label>
                <textarea id="customParams" placeholder='{"key": "value"}'>{}</textarea>
            </div>

            <button class="btn" onclick="generatePayload()">Generate Payload</button>
            <button class="btn btn-secondary" onclick="sendEvent()">Send to API</button>

            <div id="generatedPayload"></div>
        </div>

        <!-- Recent Events -->
        <div class="panel">
            <h2>Recent Events <button class="btn" onclick="loadEvents()" style="float: right; padding: 6px 15px; font-size: 14px;">Refresh</button></h2>
            <ul class="event-list" id="eventList">
                <li class="loading">Loading events...</li>
            </ul>
        </div>

        <!-- Active Routes -->
        <div class="panel">
            <h2>Active Routes <button class="btn" onclick="loadRoutes()" style="float: right; padding: 6px 15px; font-size: 14px;">Refresh</button></h2>
            <ul class="event-list" id="routeList">
                <li class="loading">Loading routes...</li>
            </ul>
        </div>
    </div>

    <script>
        const API_URL = '{{ api_url }}';
        let currentPayload = null;
        let currentSignature = null;

        const EVENT_TYPES = {
            github: ['push', 'pull_request', 'issues', 'release'],
            slack: ['message', 'reaction_added', 'app_mention'],
            notion: ['page_created', 'page_updated', 'database_updated'],
            clickup: ['task_created', 'task_updated', 'task_status_changed']
        };

        function updateEventTypes() {
            const platform = document.getElementById('platform').value;
            const eventTypeSelect = document.getElementById('eventType');
            eventTypeSelect.innerHTML = '';

            EVENT_TYPES[platform].forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                eventTypeSelect.appendChild(option);
            });
        }

        async function generatePayload() {
            const platform = document.getElementById('platform').value;
            const eventType = document.getElementById('eventType').value;
            const customParams = document.getElementById('customParams').value;

            try {
                const params = JSON.parse(customParams);
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({platform, event_type: eventType, params})
                });

                const data = await response.json();
                currentPayload = data.payload;
                currentSignature = data.signature;

                document.getElementById('generatedPayload').innerHTML = `
                    <div class="response">
                        <strong class="success">✓ Payload Generated</strong>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } catch (error) {
                document.getElementById('generatedPayload').innerHTML = `
                    <div class="response">
                        <strong class="error">✗ Error:</strong> ${error.message}
                    </div>
                `;
            }
        }

        async function sendEvent() {
            if (!currentPayload) {
                alert('Generate a payload first!');
                return;
            }

            const platform = document.getElementById('platform').value;
            const eventType = document.getElementById('eventType').value;

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        platform,
                        event_type: eventType,
                        payload: currentPayload,
                        signature: currentSignature
                    })
                });

                const data = await response.json();

                document.getElementById('generatedPayload').innerHTML = `
                    <div class="response">
                        <strong class="${data.success ? 'success' : 'error'}">
                            ${data.success ? '✓' : '✗'} ${data.message}
                        </strong>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;

                // Refresh events and stats
                loadEvents();
                loadStats();
            } catch (error) {
                document.getElementById('generatedPayload').innerHTML = `
                    <div class="response">
                        <strong class="error">✗ Error:</strong> ${error.message}
                    </div>
                `;
            }
        }

        async function loadStats() {
            try {
                const response = await fetch(`${API_URL}/api/stats`);
                const stats = await response.json();

                document.getElementById('totalEvents').textContent = stats.total_events || 0;
                document.getElementById('activeRoutes').textContent = stats.active_routes || 0;
                document.getElementById('errorCount').textContent = stats.processing_errors || 0;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }

        async function loadEvents() {
            try {
                const response = await fetch(`${API_URL}/api/events?limit=10`);
                const events = await response.json();

                const eventList = document.getElementById('eventList');
                if (events.length === 0) {
                    eventList.innerHTML = '<li class="event-item">No events yet</li>';
                    return;
                }

                eventList.innerHTML = events.map(event => `
                    <li class="event-item">
                        <strong>${event.platform}.${event.event_type}</strong>
                        <div class="event-meta">
                            ${new Date(event.timestamp).toLocaleString()} •
                            ID: ${event.event_id.substring(0, 8)}...
                        </div>
                    </li>
                `).join('');
            } catch (error) {
                document.getElementById('eventList').innerHTML =
                    '<li class="event-item error">Failed to load events</li>';
            }
        }

        async function loadRoutes() {
            try {
                const response = await fetch(`${API_URL}/api/routes`);
                const routes = await response.json();

                const routeList = document.getElementById('routeList');
                if (routes.length === 0) {
                    routeList.innerHTML = '<li class="event-item">No routes configured</li>';
                    return;
                }

                routeList.innerHTML = routes.map(route => `
                    <li class="event-item">
                        <strong>${route.route_id}</strong> • Pattern: <code>${route.pattern}</code>
                        <div class="event-meta">
                            Action: ${route.action} • Priority: ${route.priority} •
                            Active: ${route.active ? '✓' : '✗'}
                        </div>
                    </li>
                `).join('');
            } catch (error) {
                document.getElementById('routeList').innerHTML =
                    '<li class="event-item error">Failed to load routes</li>';
            }
        }

        // Initialize
        updateEventTypes();
        loadStats();
        loadEvents();
        loadRoutes();

        // Auto-refresh every 5 seconds
        setInterval(() => {
            loadStats();
            loadEvents();
        }, 5000);
    </script>
</body>
</html>
    """

    def __init__(self, api_url: str = "http://localhost:5090"):
        """
        Initialize webhook test panel.

        Args:
            api_url: Base URL of the webhook API server
        """
        self.api_url = api_url
        self.simulator = WebhookSimulator()
        self.client = WebhookClient(base_url=api_url)
        self.app = Flask(__name__)
        CORS(self.app)

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for test panel."""

        @self.app.route('/')
        def index():
            """Render test panel UI."""
            return render_template_string(self.HTML_TEMPLATE, api_url=self.api_url)

        @self.app.route('/generate', methods=['POST'])
        def generate():
            """Generate webhook payload."""
            data = request.json
            platform = data.get('platform')
            event_type = data.get('event_type')
            params = data.get('params', {})

            try:
                event = self.simulator.generate_with_signature(
                    platform, event_type, **params
                )
                return jsonify(event.to_dict())
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        @self.app.route('/send', methods=['POST'])
        def send():
            """Send webhook event to API server."""
            data = request.json
            platform = data.get('platform')
            event_type = data.get('event_type')
            payload = data.get('payload')
            signature = data.get('signature')

            try:
                # Simulate webhook delivery
                event = self.simulator.generate_with_signature(
                    platform, event_type
                )

                # Send to simulate endpoint
                result = self.client.simulate_event(
                    platform=platform,
                    event_type=event_type,
                    payload=payload or event.payload
                )

                return jsonify({
                    'success': True,
                    'message': 'Event sent successfully',
                    'result': result
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Failed to send event: {str(e)}'
                }), 500

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'ok', 'timestamp': datetime.now(timezone.utc).isoformat()})

    def run(self, host: str = '0.0.0.0', port: int = 5091, debug: bool = False):
        """
        Run test panel server.

        Args:
            host: Host to bind to
            port: Port to listen on
            debug: Enable debug mode
        """
        print(f"\n🔗 Webhook Test Panel starting...")
        print(f"📊 Panel URL: http://localhost:{port}")
        print(f"🔌 API URL: {self.api_url}")
        print(f"\n✨ Open your browser to start testing!\n")

        self.app.run(host=host, port=port, debug=debug)


def create_test_panel(api_url: str = "http://localhost:5090") -> WebhookTestPanel:
    """
    Create webhook test panel instance.

    Args:
        api_url: Base URL of the webhook API server

    Returns:
        WebhookTestPanel instance
    """
    return WebhookTestPanel(api_url=api_url)


if __name__ == '__main__':
    # Example usage
    panel = create_test_panel()
    panel.run(debug=True)
