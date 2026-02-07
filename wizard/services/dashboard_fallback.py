"""Fallback dashboard HTML for Wizard server."""

from __future__ import annotations


def get_fallback_dashboard_html() -> str:
    """Return basic HTML dashboard when Svelte build isn't available."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Wizard Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 60px; }
        h1 { font-size: 2.5em; margin-bottom: 10px; color: #60a5fa; }
        .subtitle { font-size: 1.1em; color: #cbd5e1; margin-bottom: 30px; }
        .note { background: #1e293b; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 40px; }
        .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .endpoint { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
        .endpoint h3 { color: #60a5fa; margin-bottom: 10px; font-size: 1.1em; }
        .endpoint p { color: #94a3b8; font-size: 0.9em; line-height: 1.6; }
        .code { background: #0f172a; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 0.85em; margin-top: 10px; color: #86efac; word-break: break-all; }
        .status { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
        .status-dot { width: 12px; height: 12px; border-radius: 50%; background: #10b981; }
        footer { text-align: center; margin-top: 60px; color: #64748b; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧙 uDOS Wizard Server</h1>
            <p class="subtitle">Always-on backend service</p>
        </header>

        <div class="note">
            <strong>ℹ️ Note:</strong> This is a basic fallback dashboard. The full Svelte dashboard hasn't been built yet.
            <br><br>
            <strong>To build the Svelte dashboard:</strong>
            <div class="code">cd wizard/dashboard && npm install && npm run build</div>
        </div>

        <div class="endpoints">
            <div class="endpoint">
                <h3>✅ Health Check</h3>
                <p>Server status and enabled services</p>
                <div class="code">/health</div>
            </div>

            <div class="endpoint">
                <h3>📊 Dashboard Index</h3>
                <p>Features and configuration overview</p>
                <div class="code">/api/index</div>
            </div>

            <div class="endpoint">
                <h3>📡 Server Status</h3>
                <p>Rate limits, sessions, and costs</p>
                <div class="code">/api/status</div>
            </div>

            <div class="endpoint">
                <h3>🤖 AI Models</h3>
                <p>Available AI models for routing</p>
                <div class="code">/api/ai/models</div>
            </div>

            <div class="endpoint">
                <h3>🔌 Port Manager</h3>
                <p>Manage connected devices and ports</p>
                <div class="code">/api/ports/status</div>
            </div>

            <div class="endpoint">
                <h3>🔗 VS Code Bridge</h3>
                <p>Integration with VS Code extension</p>
                <div class="code">/api/vscode/status</div>
            </div>
        </div>

        <div class="status">
            <div class="status-dot"></div>
            <span>Server is running and healthy</span>
        </div>

        <footer>
            <p>uDOS Wizard Server • v1.1.0 • <a href="https://github.com/fredporter/uDOS" style="color: #60a5fa; text-decoration: none;">GitHub</a></p>
        </footer>
    </div>
</body>
</html>"""
