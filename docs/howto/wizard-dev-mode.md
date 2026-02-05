# Wizard Server Dev Mode Integration

## Overview

The Wizard Server is fully integrated into uDOS Dev Mode, providing always-on services alongside the API server during development.

## Features

### Auto-Start on Dev Mode Launch

When you run `bin/Launch-Dev-Mode.command`, the Wizard Server automatically starts:

```bash
./Launch-Dev-Mode.command

# Output:
# ✓ Starting API server on port 5001...
# ✓ API server running (PID: xxxxx)
# ✓ Starting Wizard server on port 8765...
# ✓ Wizard server running (PID: xxxxx)
```

### Services Dashboard

The Dev Mode dashboard shows both API and Wizard Server status:

```
  Services Dashboard
  ───────────────────────────────────────
  ● API Server        http://localhost:5001
  ● Wizard Server     http://localhost:8765
  ○ Vite Dev Server   (not started)

  Quick Links
  ───────────────────────────────────────
  API:      http://localhost:5001/api/health
  Wizard:   http://localhost:8765/health
  Swagger:  http://localhost:5001/docs (if enabled)
  Logs:     memory/logs/
```

## Dev Mode Commands

### Management Commands

| Command          | Description              |
| ---------------- | ------------------------ |
| `wizard`         | Launch Wizard Server TUI |
| `wizard-start`   | Start Wizard Server      |
| `wizard-stop`    | Stop Wizard Server       |
| `wizard-restart` | Restart Wizard Server    |

### Usage Examples

```bash
dev> wizard
# Launches interactive Wizard TUI for management

dev> wizard-stop
# ✓ Stopping Wizard Server (PID: xxxxx)...
# ✓ Wizard Server stopped

dev> wizard-start
# ✓ Starting Wizard Server...
# ✓ Wizard Server started (PID: xxxxx)

dev> wizard-restart
# ✓ Restarting Wizard Server...
# ✓ Wizard Server restarted (PID: xxxxx)
```

### Integrated Commands

| Command   | Description                               |
| --------- | ----------------------------------------- |
| `status`  | Show services dashboard (includes Wizard) |
| `restart` | Restart ALL services (API + Wizard)       |
| `logs`    | Tail logs (includes Wizard logs)          |
| `test`    | Test all services (API + Wizard)          |

## Configuration

Wizard Server runs in dev mode with the following configuration:

```python
WizardConfig(
    host="127.0.0.1",        # localhost only
    port=8765,               # default Wizard port
    debug=True,              # debug mode enabled
    plugin_repo_enabled=True,
    web_proxy_enabled=True,
    ai_gateway_enabled=False,  # optional
    gmail_relay_enabled=False, # optional
)
```

## Logs

Wizard Server logs are written to:

```
memory/logs/wizard-dev-YYYY-MM-DD.log
```

View with:

```bash
dev> logs
# Tails all dev logs including Wizard

# Or directly:
tail -f memory/logs/wizard-dev-$(date +%Y-%m-%d).log
```

## Endpoints

Once running, Wizard Server provides:

- `GET /health` - Health check
- `GET /api/status` - Server status (auth required)
- `GET /api/plugin/list` - Plugin repository
- `POST /api/web/fetch` - Web proxy (if enabled)
- `POST /api/ai/chat` - AI gateway (if enabled)
- `POST /api/gmail/send` - Gmail relay (if configured)

## Testing Integration

```bash
# Test Wizard health endpoint
curl http://localhost:8765/health

# Test from Dev Mode
dev> test

# Output:
# API Server:
#   {
#     "status": "ok",
#     "service": "uDOS API"
#   }
#
# Wizard Server:
#   {
#     "status": "ok",
#     "service": "Wizard Server"
#   }
```

## Workflow

### Typical Development Session

1. **Start Dev Mode**

   ```bash
   bin/Launch-Dev-Mode.command
   ```

   Both API and Wizard Server start automatically

2. **Check Status**

   ```bash
   dev> status
   ```

   Verify both services are running

3. **Launch Wizard TUI** (optional)

   ```bash
   dev> wizard
   ```

   Interactive management interface

4. **Develop/Test**

   - Services run in background
   - Logs stream to `memory/logs/`
   - Auto-reload on code changes (Python)

5. **Restart if Needed**

   ```bash
   dev> wizard-restart  # Just Wizard
   dev> restart         # All services
   ```

6. **Exit**
   ```bash
   dev> exit
   ```
   Clean shutdown of all services

## Troubleshooting

### Wizard Server Won't Start

```bash
# Check logs
tail -50 memory/logs/wizard-dev-$(date +%Y-%m-%d).log

# Check if port is in use
lsof -i:8765

# Manual start with debug
python wizard/dev_server.py
```

### Port Conflicts

If port 8765 is in use, modify `WIZARD_PORT` in `bin/Launch-Dev-Mode.command`:

```bash
WIZARD_PORT=8766  # Change to available port
```

### Service Not Responding

```bash
# Check process status
dev> status

# Restart specific service
dev> wizard-restart

# Or restart all
dev> restart
```

## Advanced Usage

### Enabling Optional Services

Edit `wizard/dev_server.py` to enable:

```python
config = WizardConfig(
    # ...
    ai_gateway_enabled=True,    # Enable AI gateway
    gmail_relay_enabled=True,   # Enable Gmail relay
)
```

Requires additional setup:

- **AI Gateway**: Configure `wizard/config/ai_keys.json`
- **Gmail Relay**: Run OAuth flow (see wizard docs)

### Custom Configuration

Override config in Dev Mode:

```bash
# Set environment variables before starting
export WIZARD_PORT=8766
export WIZARD_DEBUG=1
./Launch-Dev-Mode.command
```

## Related Documentation

- [Wizard Server README](../wizard/README.md)
- [Wizard TUI Commands](../wizard/README.md#wizard_tuipy---wizard-server-tui)
- [Dev Mode Launcher](../../bin/Launch-Dev-Mode.command)
- [API Server Integration](../extensions/api/README.md)

---

**Version:** v1.1.0.0  
**Updated:** 2026-01-13
