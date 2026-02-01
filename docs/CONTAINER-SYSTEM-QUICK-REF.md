# Container System Quick Reference

**Purpose:** Manage home-assistant, songscribe, and other containerized plugins  
**Endpoints:** `/api/v1/containers/` + `/ui/`  
**Status:** Implemented & Ready for Testing

---

## API Endpoints

### Launch Container
```bash
POST /api/v1/containers/{container_id}/launch

curl -X POST http://localhost:8765/api/v1/containers/home-assistant/launch
```

Response:
```json
{
  "success": true,
  "status": "launching",
  "container_id": "home-assistant",
  "name": "Home Assistant",
  "port": 8123,
  "browser_route": "/ui/home-assistant",
  "message": "Launching Home Assistant..."
}
```

### Check Status
```bash
GET /api/v1/containers/{container_id}/status

curl http://localhost:8765/api/v1/containers/home-assistant/status
```

Response:
```json
{
  "success": true,
  "container_id": "home-assistant",
  "name": "Home Assistant",
  "running": true,
  "port": 8123,
  "browser_route": "/ui/home-assistant"
}
```

### Stop Container
```bash
POST /api/v1/containers/{container_id}/stop

curl -X POST http://localhost:8765/api/v1/containers/home-assistant/stop
```

### List Available Containers
```bash
GET /api/v1/containers/list/available

curl http://localhost:8765/api/v1/containers/list/available
```

Response:
```json
{
  "success": true,
  "containers": [
    {
      "id": "home-assistant",
      "name": "Home Assistant",
      "port": 8123,
      "browser_route": "/ui/home-assistant",
      "running": true
    },
    {
      "id": "songscribe",
      "name": "Songscribe",
      "port": 3000,
      "browser_route": "/ui/songscribe",
      "running": false
    }
  ]
}
```

---

## Browser Access

Once container is running, access via:

### Home Assistant
```
http://wizard:8765/ui/home-assistant
http://wizard:8765/ui/home-assistant/dashboard
http://wizard:8765/ui/home-assistant/api/config
```

### Songscribe
```
http://wizard:8765/ui/songscribe
http://wizard:8765/ui/songscribe/api/transcribe
http://wizard:8765/ui/songscribe/results
```

---

## Containers Available

### home-assistant
| Property | Value |
|----------|-------|
| **ID** | `home-assistant` |
| **Port** | 8123 |
| **Browser Route** | `/ui/home-assistant` |
| **Status** | Ready (needs initialization) |
| **Commands** | `HOME START`, `HOME STATUS` |

### songscribe
| Property | Value |
|----------|-------|
| **ID** | `songscribe` |
| **Port** | 3000 |
| **Browser Route** | `/ui/songscribe` |
| **Status** | Ready for testing |
| **Commands** | `MUSIC TRANSCRIBE <file>` |

---

## uCODE Integration

### Commands

#### Home Assistant
```ucode
HOME START
HOME RESTART
HOME STATUS
HOME SHOW <entity_id>
```

#### Songscribe
```ucode
MUSIC TRANSCRIBE <file.mp3>
MUSIC TRANSCRIBE <youtube_url>
MUSIC SEPARATE <file.mp3> --preset full_band
MUSIC STEMS <file.mp3>
MUSIC SCORE <file.mid>
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User Browser (Wizard Dashboard)                             │
└────────────────┬────────────────────────────────────────────┘
                 │ https://wizard:8765
                 │
┌────────────────▼────────────────────────────────────────────┐
│ Wizard Server (FastAPI)                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Router: /ui/                                         │  │
│  │ ├─ /{container_id}/...      [container_proxy.py]   │  │
│  │ └─ Proxies to localhost:PORT                        │  │
│  │                                                      │  │
│  │ Router: /api/v1/containers/                         │  │
│  │ ├─ /{container_id}/launch  [launcher.py]           │  │
│  │ ├─ /{container_id}/stop    [launcher.py]           │  │
│  │ ├─ /{container_id}/status  [launcher.py]           │  │
│  │ └─ /list/available         [launcher.py]           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │ localhost:8123 (HA)
                 │ localhost:3000 (Songscribe)
                 │
     ┌───────────┴──────────────┐
     │                          │
┌────▼─────────────────┐  ┌────▼──────────────────┐
│ home-assistant:8123  │  │ songscribe:3000      │
│                      │  │                      │
│ - Config             │  │ - Frontend (UI)      │
│ - API                │  │ - Transcription API  │
│ - Entities           │  │ - Results storage    │
└──────────────────────┘  └──────────────────────┘
```

---

## Container Requirements

### home-assistant
- **Python:** 3.11+
- **Memory:** 1GB+ recommended
- **Storage:** 2GB+ for config/databases
- **Network:** Requires internet for integrations

### songscribe
- **Node.js:** 18+ (frontend)
- **Python:** 3.11+ (backend ML)
- **Memory:** 8GB+ for ML models
- **GPU:** Optional (CUDA accelerates processing)
- **Storage:** 2GB+ for model cache

---

## Troubleshooting

### Container won't start
```bash
# Check if port is in use
lsof -i :8123  # home-assistant
lsof -i :3000  # songscribe

# Check logs
tail -f memory/logs/containers.log
```

### Proxy connection failed
```json
{
  "status_code": 503,
  "detail": "Container home-assistant is not running. Use /api/v1/containers/home-assistant/launch to start it."
}
```
→ Launch the container first using `/api/v1/containers/{id}/launch`

### Health check timeout
Container started but isn't responding to HTTP. Common causes:
- Service initialization incomplete
- Binding to wrong interface
- Port not accessible from Wizard server

---

## Files Reference

| File | Purpose |
|------|---------|
| `wizard/routes/container_launcher_routes.py` | Container lifecycle management |
| `wizard/routes/container_proxy_routes.py` | Browser proxy to services |
| `distribution/plugins/home-assistant/manifest.json` | Home Assistant plugin index |
| `distribution/plugins/songscribe/manifest.json` | Songscribe plugin index |
| `library/home-assistant/container.json` | Home Assistant container metadata |
| `library/songscribe/container.json` | Songscribe container metadata |

---

## Configuration

### Adding New Container

1. Create directory: `library/{container_id}/`
2. Create metadata: `library/{container_id}/container.json`
3. Create manifest: `distribution/plugins/{container_id}/manifest.json`
4. Add to `ContainerLauncher.CONTAINER_CONFIGS` in `container_launcher_routes.py`:
   ```python
   "{container_id}": {
       "name": "Display Name",
       "port": 8000,
       "service_path": "wizard/services/{container_id}",
       "launch_command": ["python", "-m", "..."],
       "health_check_url": "http://localhost:8000/health",
       "browser_route": "/ui/{container_id}",
   }
   ```
5. Update `ContainerProxy.CONTAINER_PORTS` with port mapping

---

**Last Updated:** 2026-02-01  
**Status:** Ready for Integration Testing
