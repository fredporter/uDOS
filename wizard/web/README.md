# Wizard Server Web GUI

**FastAPI-based browser interface for Wizard Server administration**

Version: v1.0.0.0  
Stack: FastAPI + HTMX + Alpine.js + Tailwind CSS

---

## Overview

Browser-based administration interface for Wizard Server. No Tauri required - just point your browser at `http://wizard-ip:8080`.

**Features:**
- Dashboard (system status, logs, health metrics)
- POKE Server (host files/pages from Wizard)
- Webhook Receiver (external integrations)
- Device Monitor (paired mesh devices, status)
- Log Viewer (real-time log streaming)

---

## Architecture

### Stack

- **Backend:** FastAPI (async, WebSocket support)
- **Templates:** Jinja2 (server-side rendering)
- **Frontend:** HTMX + Alpine.js (no build step required)
- **Styling:** Tailwind CSS (CDN, utility-first)

### Why This Stack?

**No Build Step:**
- HTMX, Alpine.js, Tailwind all loaded from CDN
- No npm, webpack, or complex build pipeline
- Edit HTML templates and see changes immediately

**Lightweight:**
- HTMX: 14KB (reactive updates without heavy frameworks)
- Alpine.js: 15KB (minimal client-side state)
- Tailwind: Utility CSS (no custom CSS needed)

**Perfect for Wizard Server:**
- Runs on always-on server (no desktop app needed)
- Accessible from any browser (desktop, mobile, tablet)
- Real-time updates via WebSocket + HTMX polling

---

## Directory Structure

```
wizard/web/
├── app.py                    # FastAPI application
├── templates/
│   ├── base.html            # Base template (nav, footer)
│   ├── dashboard.html       # Main dashboard
│   ├── poke.html            # POKE server management
│   ├── webhooks.html        # Webhook configuration
│   ├── devices.html         # Device monitoring
│   └── logs.html            # Log viewer
├── static/
│   ├── css/
│   │   └── wizard.css       # Custom styles
│   └── js/
│       └── wizard.js        # Minimal client-side JS
├── poke_commands.py         # POKE server logic
├── tunnel_manager.py        # Secure tunnel management
└── web_service.py           # Original web service (legacy)
```

---

## Routes

### Dashboard
- `GET /` - Main dashboard page
- `GET /api/stats` - System statistics (JSON)
- `WebSocket /ws` - Real-time updates

### POKE Server
- `GET /poke` - POKE management page
- `POST /api/poke/upload` - Upload file for hosting
- `GET /p/{path}` - Serve hosted file

### Webhooks
- `GET /webhooks` - Webhook management page
- `POST /webhook/{webhook_id}` - Receive webhook

### Devices
- `GET /devices` - Device monitoring page
- `GET /api/devices` - Device list (JSON)

### Logs
- `GET /logs` - Log viewer page
- `GET /api/logs` - Log entries (JSON, filterable)

### Hotkeys
- `GET /hotkeys` - Hotkey Center (live key bindings + keymap runtime state)
- `GET /hotkeys/data` - Hotkey payload + keymap runtime (JSON)

### Health
- `GET /health` - Health check endpoint

---

## Usage

### Start Server

```bash
# From wizard directory
python web/app.py

# Or from uDOS root
python -m wizard.web.app

# Custom host/port
python -m wizard.web.app --host 0.0.0.0 --port 8080
```

### Access Dashboard

```
http://localhost:8080/          # Main dashboard
http://localhost:8080/poke      # POKE server
http://localhost:8080/devices   # Device monitor
http://localhost:8080/logs      # Log viewer
```

### On Local Network

```
# Find Wizard Server IP
ip addr show

# Access from other devices
http://192.168.1.100:8080/
```

---

## HTMX Integration

**Auto-refreshing stats:**

```html
<div 
    hx-get="/api/stats"
    hx-trigger="every 5s"
    hx-swap="innerHTML"
>
    <!-- Stats content auto-updates every 5 seconds -->
</div>
```

**Lazy-loaded device list:**

```html
<div 
    hx-get="/api/devices"
    hx-trigger="load"
    hx-swap="innerHTML"
>
    Loading...
</div>
```

**Click to load logs:**

```html
<button 
    hx-get="/api/logs?level=error"
    hx-target="#log-container"
>
    Show Errors
</button>
```

---

## Alpine.js Components

**Dashboard with WebSocket:**

```html
<div x-data="dashboard()">
    <div x-text="status"></div>
</div>

<script>
function dashboard() {
    return {
        status: 'connecting',
        init() {
            const ws = new WebSocket('ws://localhost:8080/ws');
            ws.onmessage = (e) => {
                this.status = JSON.parse(e.data).status;
            };
        }
    }
}
</script>
```

---

## Styling (Tailwind)

**Stat Card:**

```html
<div class="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
    <h3 class="text-gray-400 text-sm font-medium">Devices</h3>
    <p class="text-3xl font-semibold text-white mt-3">5</p>
</div>
```

**Custom Classes (wizard.css):**

```css
.stat-card {
    @apply bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700;
}

.nav-link {
    @apply px-3 py-2 rounded-md text-sm font-medium text-gray-300 
           hover:bg-gray-700 hover:text-white transition-colors;
}
```

---

## WebSocket Real-time Updates

**Server broadcasts:**

```python
# Broadcast event to all connected clients
await broadcast_event('device_connected', {
    'device_id': 'node-alpha',
    'name': 'Desktop Node'
})
```

**Client receives:**

```javascript
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'device_connected') {
        showNotification(`Device ${message.data.name} connected`);
        htmx.trigger('body', 'refresh-devices');
    }
};
```

---

## Development

### Hot Reload

FastAPI auto-reloads on file changes:

```bash
# Development mode with auto-reload
uvicorn wizard.web.app:app --reload --host 127.0.0.1 --port 8080
```

### Add New Page

1. **Create template** (`templates/new_page.html`)
2. **Add route** to `app.py`:
   ```python
   @app.get("/new-page", response_class=HTMLResponse)
   async def new_page(request: Request):
       return templates.TemplateResponse("new_page.html", {
           "request": request,
           "page_title": "New Page"
       })
   ```
3. **Add nav link** to `base.html`

### Add API Endpoint

```python
@app.get("/api/custom-data")
async def get_custom_data():
    data = {"key": "value"}
    return JSONResponse(data)
```

Use with HTMX:

```html
<div hx-get="/api/custom-data" hx-trigger="load"></div>
```

---

## Security

**Localhost Only (Default):**

```python
start_web_server(host="127.0.0.1", port=8080)
```

**Local Network Access:**

```python
start_web_server(host="0.0.0.0", port=8080)
```

**CORS Configuration:**

```python
# Restrict to local network
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.*.*", "http://10.*.*.*"],
    allow_credentials=True
)
```

**Future: Authentication:**

```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.get("/admin")
async def admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Verify credentials
    pass
```

---

## Testing

```bash
# Run server
python wizard/web/app.py

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/api/stats

# WebSocket test (websocat tool)
websocat ws://localhost:8080/ws
```

---

## Production Deployment

**With systemd:**

```ini
# /etc/systemd/system/udos-wizard-web.service
[Unit]
Description=uDOS Wizard Server Web Interface
After=network.target

[Service]
Type=simple
User=udos
WorkingDirectory=/opt/udos
ExecStart=/opt/udos/venv/bin/python -m wizard.web.app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable udos-wizard-web
sudo systemctl start udos-wizard-web
```

---

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Dashboard with stats
- ✅ POKE server routes
- ✅ Webhook receiver
- ✅ Device monitor
- ✅ Log viewer
- ✅ WebSocket real-time updates

### Phase 2: Enhanced UI (Next)
- Plugin manager page
- OK gateway UI
- Cost tracking graphs
- Advanced filtering/search

### Phase 3: Community Features
- User authentication
- Multi-user support
- Shared device management
- Plugin marketplace UI

---

## References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [HTMX Docs](https://htmx.org/)
- [Alpine.js Docs](https://alpinejs.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/)

---

*Last Updated: 2026-01-05*  
*Version: v1.0.0.0*
