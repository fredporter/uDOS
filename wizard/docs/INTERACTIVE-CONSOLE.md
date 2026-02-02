# Wizard Server Interactive Console

## Overview

The Wizard Server now includes an **interactive command prompt** that runs while the FastAPI servers are active. This allows real-time monitoring, configuration management, and system administration without interrupting service.

## Features

### 🖥️ Startup Dashboard

When the Wizard Server starts, it displays a comprehensive dashboard showing:

- **Server version and status** (production v1.1.0.0)
- **Enabled services** with versions:

  - Plugin Repository (v1.1.0) - Distribution and updates
  - AI Gateway (v1.1.0) - Model routing (Ollama/OpenRouter)
  - Web Proxy (v1.0.0) - Web content fetching
  - Gmail Relay (v1.0.0) - Email relay service
  - GitHub Monitor (v1.0.0) - CI/CD self-healing
  - Rate Limiter (v1.1.0) - Request throttling
  - Cost Tracker (v1.0.0) - API cost monitoring
  - Device Auth (v1.0.0) - Device authentication
  - WebSocket (v1.0.0) - Real-time updates

- **Configuration summary**:

  - Rate limits (per minute/hour)
  - AI budgets (daily/monthly)
  - Debug mode status

- **API endpoints**:
  - Health check
  - REST API
  - WebSocket
  - API documentation

### 💬 Interactive Commands

While servers are running, type commands at the `wizard>` prompt:

| Command         | Description                                             |
| --------------- | ------------------------------------------------------- |
| `status`        | Show server status, uptime, active services             |
| `services`      | List all services with versions and status              |
| `config`        | Display current configuration (rates, budgets, toggles) |
| `health`        | Run health checks (directories, config, services)       |
| `reload`        | Reload configuration from disk without restart          |
| `github`        | Show GitHub Actions status and recent workflow runs     |
| `workflows`     | Alias for `github` command                              |
| `help`          | Show command reference                                  |
| `exit` / `quit` | Shutdown server gracefully                              |

### 🔔 GitHub Actions Self-Healing

The Wizard Server can now monitor GitHub Actions workflows and automatically respond to failures:

#### Webhook Endpoint

**URL:** `http://[wizard-host]:8765/api/github/webhook`

**Subscribe at:** https://github.com/[owner]/[repo]/settings/hooks

**Events to enable:**

- `workflow_run` (completed, requested)
- `check_run` (completed)

**Content type:** `application/json`

#### Auto-Healing Features

1. **Transient Failure Detection**

   - Network errors → Auto-retry workflow
   - Timeouts → Auto-retry workflow
   - Connection issues → Auto-retry workflow

2. **Test Flakiness Handling**

   - Detects intermittent test failures
   - Auto-retries up to 2 times for suspected flaky tests
   - Tracks failure patterns to identify chronic issues

3. **Pattern Analysis**

   - Logs failure reasons (test_failure, build_failure, timeout, network_error)
   - Counts occurrences of each pattern
   - View patterns with `github` command

4. **Manual Intervention Notifications**
   - Prints alerts to wizard console for failures requiring human action
   - Provides failure reason and GitHub Actions URL
   - Tracks manual vs auto-fixed failure ratio

#### GitHub CLI Integration

The self-healing system uses GitHub CLI (`gh`) for workflow management:

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Test (manual)
gh run list --repo owner/repo
gh run view [run-id]
gh run rerun [run-id]
```

**Note:** The monitor will function without `gh`, but auto-healing features (retry, fix) require it.

## Usage

### Starting Wizard Server

**Interactive mode (default):**

```bash
python -m wizard.server
# or
python wizard/server.py
```

**Daemon mode (no console):**

```bash
python wizard/server.py --no-interactive
```

**With options:**

```bash
python wizard/server.py --host 0.0.0.0 --port 8765 --debug
```

### Example Session

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🧙  uDOS WIZARD SERVER  v1.1.0.0                               ║
║                                                                  ║
║   Production Server - Port 8765                                  ║
║   2026-01-16 14:30:00                                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

📊 CAPABILITIES:
  ✅ Plugin Repository    v1.1.0       Plugin distribution and updates
  ✅ AI Gateway           v1.1.0       AI model routing (Ollama/OpenRouter)
  ✅ Web Proxy            v1.0.0       Web content fetching
  ⏸️  Gmail Relay         v1.0.0       Email relay service
  ✅ GitHub Monitor       v1.0.0       CI/CD self-healing (Actions webhooks)
  ✅ Rate Limiter         v1.1.0       Request rate limiting
  ✅ Cost Tracker         v1.0.0       API cost monitoring
  ✅ Device Auth          v1.0.0       Device authentication
  ✅ WebSocket            v1.0.0       Real-time updates

⚙️  CONFIGURATION:
  • Rate Limit: 60/min, 1000/hour
  • AI Budget: $10.0/day, $100.0/month
  • Debug Mode: Disabled

🌐 ENDPOINTS:
  • Health:         http://0.0.0.0:8765/health
  • API:            http://0.0.0.0:8765/api/
  • WebSocket:      ws://0.0.0.0:8765/ws
  • Documentation:  http://0.0.0.0:8765/docs

💬 INTERACTIVE MODE: Type 'help' for commands, 'exit' to shutdown
====================================================================

wizard> status

📊 SERVER STATUS:
  • Uptime: < 1 hour
  • Port: 8765
  • Debug: No
  • Active Services: 8/9

wizard> github

📦 GITHUB ACTIONS:
  Fetching recent workflow runs...

  Recent Runs (5):
    ✅ CI Tests                        main            success
    ✅ Build Core                      main            success
    ✅ Wizard Integration             main            success
    ❌ Deploy                          release/v1.0.3  failure
    ✅ Lint                            main            success

  Failure Patterns:
    • Deploy:build_failure: 3x
    • CI Tests:test_failure: 1x

  Webhook URL: http://0.0.0.0:8765/api/github/webhook
  Configure at: https://github.com/[owner]/[repo]/settings/hooks

wizard> 🔔 GitHub Webhook Received:
   Event: workflow_run
   Delivery: abc123-def456

🔔 GitHub Actions: Deploy
   Status: completed - failure
   Branch: release/v1.0.3
   URL: https://github.com/owner/repo/actions/runs/12345
   ❌ Workflow failed - analyzing...
   🔄 Detected transient failure - attempting auto-retry...
   ✅ Workflow re-triggered successfully

wizard> exit

🛑 Shutting down Wizard Server...
✅ Wizard Server shutdown complete
```

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Wizard Server                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI App (Port 8765)                         │  │
│  │  • REST API endpoints                            │  │
│  │  • WebSocket connections                         │  │
│  │  • GitHub webhook receiver                       │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                              │
│                           │ asyncio                      │
│                           ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Interactive Console (WizardConsole)             │  │
│  │  • Command parser                                │  │
│  │  • Status queries                                │  │
│  │  • GitHub CLI integration                        │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                              │
│                           ▼                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  GitHub Actions Monitor                          │  │
│  │  • Webhook handler                               │  │
│  │  • Failure pattern detection                     │  │
│  │  • Auto-retry logic                              │  │
│  │  • GitHub CLI commands (gh run rerun)            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Files Modified/Created

1. **`wizard/services/interactive_console.py`** (NEW)

   - WizardConsole class with command handlers
   - Startup banner with capabilities dashboard
   - Async command loop (non-blocking)
   - GitHub status integration

2. **`wizard/services/github_monitor.py`** (NEW)

   - GitHubActionsMonitor class
   - Webhook handler for workflow_run events
   - Failure analysis and pattern tracking
   - Auto-retry and auto-fix logic
   - GitHub CLI integration

3. **`wizard/server.py`** (MODIFIED)
   - Added `interactive` parameter to `run()` method
   - Async server startup with concurrent console
   - New CLI flag: `--no-interactive`
   - New webhook endpoint: `/api/github/webhook`

### Async Design

The system uses Python's `asyncio` to run both the FastAPI server and interactive console concurrently:

```python
async def run_with_console():
    # Start FastAPI server in background
    server_task = asyncio.create_task(server.serve())

    # Run interactive console in foreground
    console_task = asyncio.create_task(console.run())

    # Wait for user to type 'exit'
    await console_task

    # Shutdown server gracefully
    server.should_exit = True
    await server_task

asyncio.run(run_with_console())
```

This allows:

- Server continues handling requests while console is interactive
- Webhook notifications appear in console in real-time
- Commands execute without blocking server
- Graceful shutdown propagates to both tasks

## Configuration

### Wizard Config (`wizard/config/wizard.json`)

No new configuration options required - interactive mode is default.

To disable interactive mode, use `--no-interactive` flag or set environment variable:

```bash
export WIZARD_NO_INTERACTIVE=1
python wizard/server.py
```

### GitHub Webhook Secret (Optional)

To validate GitHub webhook signatures:

1. Generate secret: `openssl rand -hex 32`
2. Add to `wizard/config/secrets.json` (gitignored):
   ```json
   {
     "github_webhook_secret": "your-secret-here"
   }
   ```
3. Configure same secret in GitHub webhook settings

**Note:** Signature validation is currently a TODO in the code.

## Future Enhancements

- [ ] Track actual server uptime (start time timestamp)
- [ ] Add `logs` command to tail recent logs
- [ ] Add `metrics` command for performance stats
- [ ] Implement GitHub webhook signature validation
- [ ] Add `retry [run-id]` command for manual workflow retry
- [ ] Support custom auto-fix scripts per failure pattern
- [ ] Dashboard web UI (alternative to CLI)

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-16  
**Status:** Production-ready
