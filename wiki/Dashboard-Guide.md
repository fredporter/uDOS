# Dashboard Guide

**Version:** 1.1.14
**Extension:** `extensions/web/dashboard/`
**Last Updated:** December 2, 2025

## Overview

The uDOS Dashboard is a **retro-styled web interface** for real-time monitoring of missions, checklists, workflows, and XP progress. Built with Flask and NES.css, it provides a nostalgic 8-bit Nintendo aesthetic while delivering modern real-time updates.

---

## Features

✨ **Real-Time Monitoring**
- Auto-refresh every 5 seconds
- No manual page reload needed
- Live progress bars and metrics

🎮 **Retro Aesthetic**
- NES.css pixel-perfect styling
- 8-bit fonts and UI elements
- Press Start 2P font
- Classic Nintendo color palette

📊 **Four Main Widgets**
- Active Missions (with progress bars)
- Checklists (completion meters)
- Workflow Status (execution phase)
- XP & Achievements (gamification)

🔌 **RESTful API**
- 5 JSON endpoints
- Structured data access
- Easy integration with external tools

---

## Quick Start

### 1. Start the Dashboard

```bash
cd extensions/web/dashboard
python server.py
```

**Output:**

```
 * Serving Flask app 'server'
 * Debug mode: on
 * Running on http://127.0.0.1:5050
Press CTRL+C to quit
```

### 2. Open Browser

Navigate to: `http://127.0.0.1:5050`

### 3. View Real-Time Updates

The dashboard automatically refreshes every 5 seconds to show:
- Active missions with progress bars
- Checklist completion percentages
- Current workflow execution phase
- Total XP and achievement badges

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    uDOS DASHBOARD v1.1.14                   │
│                                                             │
│  Last Updated: 14:30:45 | Auto-refresh: Every 5 seconds    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📋 Active Missions (2)                                      │
│                                                             │
│  [HIGH] Emergency Water System                              │
│  ████████████████████░░░░░░░░░░ 65% (13/20 steps)           │
│                                                             │
│  [MEDIUM] Shelter Winterization                             │
│  ████████░░░░░░░░░░░░░░░░░░░░░░ 33% (5/15 steps)            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ✓ Checklists (3 active)                                    │
│                                                             │
│  water-storage-maintenance       ████████████░░░░░ 67% (20/30)│
│  72-hour-bug-out-bag             ████████████████░░ 85% (28/33)│
│  first-aid-kit-inventory         ████░░░░░░░░░░░░░ 23% (7/30) │
│                                                             │
│  Total: 55/93 items complete (59%)                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Workflow Status                                          │
│                                                             │
│  Current: water-purification-workflow.upy                   │
│  Phase: EXECUTE                                             │
│  Checkpoints Saved: 12                                      │
│  Status: ACTIVE                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🏆 XP & Achievements                                        │
│                                                             │
│  Total XP: 350                                              │
│  Level: 3 (Apprentice)                                      │
│                                                             │
│  🎖️ First Mission   🔥 Perfect Week   ⭐ Fast Learner       │
│                                                             │
│  Perfect Streak: 3 days                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Widget Reference

### 1. Active Missions Widget

**Purpose:** Track mission progress with visual progress bars

**Data Displayed:**
- Mission title
- Priority badge (HIGH, MEDIUM, LOW)
- Progress bar (completed steps / total steps)
- Percentage completion
- Total missions count

**Example:**

```
📋 Active Missions (2)

[HIGH] Emergency Water System
████████████████████░░░░░░░░░░ 65% (13/20 steps)

[MEDIUM] Shelter Winterization
████████░░░░░░░░░░░░░░░░░░░░░░ 33% (5/15 steps)
```

**Data Source:**
- File: `memory/workflows/state/current.json`
- API: `GET /api/missions`

**Metrics:**
```json
{
  "missions_total": 2,
  "missions_completed": 0,
  "missions_failed": 0,
  "current_mission": "water-prep"
}
```

---

### 2. Checklists Widget

**Purpose:** Monitor checklist completion across all active checklists

**Data Displayed:**
- Checklist name (kebab-case ID)
- Progress bar per checklist
- Items complete / total items
- Percentage completion
- Total across all checklists

**Example:**

```
✓ Checklists (3 active)

water-storage-maintenance       ████████████░░░░░ 67% (20/30)
72-hour-bug-out-bag             ████████████████░░ 85% (28/33)
first-aid-kit-inventory         ████░░░░░░░░░░░░░ 23% (7/30)

Total: 55/93 items complete (59%)
```

**Data Source:**
- File: `memory/system/user/checklist_state.json`
- API: `GET /api/checklists`

**Metrics:**
```json
{
  "water-storage-maintenance": {
    "completed_items": ["item1", "item2"],
    "total_items": 30
  }
}
```

---

### 3. Workflow Status Widget

**Purpose:** Show current workflow execution state

**Data Displayed:**
- Current workflow script name
- Execution phase (IDLE, INIT, SETUP, EXECUTE, MONITOR, COMPLETE)
- Checkpoints saved count
- Status (ACTIVE, PAUSED, COMPLETED)

**Example:**

```
⚙️ Workflow Status

Current: water-purification-workflow.upy
Phase: EXECUTE
Checkpoints Saved: 12
Status: ACTIVE
```

**Data Source:**
- File: `memory/workflows/state/current.json`
- API: `GET /api/workflow`

**Phases:**
- `IDLE` - No workflow running
- `INIT` - Initializing
- `SETUP` - Setting up environment
- `EXECUTE` - Running main tasks
- `MONITOR` - Monitoring progress
- `COMPLETE` - Finished

---

### 4. XP & Achievements Widget

**Purpose:** Gamification metrics and motivation

**Data Displayed:**
- Total XP earned
- Level and title (Novice, Apprentice, Expert, Master)
- Achievement badges (emoji icons)
- Perfect streak days

**Example:**

```
🏆 XP & Achievements

Total XP: 350
Level: 3 (Apprentice)

🎖️ First Mission   🔥 Perfect Week   ⭐ Fast Learner

Perfect Streak: 3 days
```

**Data Source:**
- File: `memory/workflows/state/current.json`
- API: `GET /api/xp`

**XP Levels:**
```
0-99:     Novice
100-299:  Apprentice
300-599:  Expert
600+:     Master
```

**Achievements:**
```json
{
  "achievements_unlocked": [
    "First Mission",
    "Perfect Week",
    "Fast Learner",
    "Checkpoint Master"
  ],
  "perfect_streak": 3
}
```

---

## API Reference

### Base URL

```
http://127.0.0.1:5050/api
```

### Endpoints

#### 1. GET /api/status

**Description:** Complete system state (all widgets in one call)

**Response:**

```json
{
  "missions": {
    "current_mission": "water-prep",
    "missions_total": 2,
    "missions_completed": 0,
    "missions_failed": 0
  },
  "checklists": {
    "water-storage-maintenance": {
      "completed_items": ["item1", "item2"],
      "total_items": 30
    }
  },
  "workflow": {
    "status": "ACTIVE",
    "checkpoints_saved": 12
  },
  "xp": {
    "total_xp_earned": 350,
    "achievements_unlocked": ["First Mission"],
    "perfect_streak": 3
  }
}
```

#### 2. GET /api/missions

**Description:** Mission-specific data

**Response:**

```json
{
  "current_mission": "water-prep",
  "status": "ACTIVE",
  "missions_total": 2,
  "missions_completed": 0,
  "missions_failed": 0
}
```

#### 3. GET /api/checklists

**Description:** Checklist progress data

**Response:**

```json
{
  "water-storage-maintenance": {
    "completed_items": ["item1", "item2"],
    "total_items": 30,
    "last_updated": "2025-12-02T14:30:00Z"
  },
  "72-hour-bug-out-bag": {
    "completed_items": ["item1"],
    "total_items": 33,
    "last_updated": "2025-12-02T14:30:00Z"
  }
}
```

#### 4. GET /api/workflow

**Description:** Workflow execution state

**Response:**

```json
{
  "current_mission": "water-prep",
  "status": "ACTIVE",
  "checkpoints_saved": 12
}
```

#### 5. GET /api/xp

**Description:** XP and achievement data

**Response:**

```json
{
  "total_xp_earned": 350,
  "achievements_unlocked": [
    "First Mission",
    "Perfect Week",
    "Fast Learner"
  ],
  "perfect_streak": 3
}
```

---

## Configuration

### Port Configuration

Default port: **5050**

To change:

**Option 1: Edit `server.py`**

```python
if __name__ == "__main__":
    app.run(debug=True, port=8080)  # Change to desired port
```

**Option 2: Environment Variable**

```bash
export FLASK_RUN_PORT=8080
python server.py
```

### Auto-Refresh Interval

Default: **5 seconds**

To change, edit `static/dashboard.js`:

```javascript
// Refresh every 10 seconds instead of 5
setInterval(updateDashboard, 10000);
```

### Debug Mode

Default: **ON** (for development)

To disable for production:

```python
if __name__ == "__main__":
    app.run(debug=False, port=5050)
```

---

## Troubleshooting

### Issue: Dashboard shows "Loading..."

**Cause:** State files don't exist or are invalid JSON

**Solution:**

```bash
# Check if files exist
ls -la memory/workflows/state/current.json
ls -la memory/system/user/checklist_state.json

# Verify JSON is valid
cat memory/workflows/state/current.json | python -m json.tool
```

Create minimal state files if missing:

**`memory/workflows/state/current.json`:**
```json
{
  "current_mission": null,
  "status": "IDLE",
  "missions_total": 0,
  "missions_completed": 0,
  "missions_failed": 0,
  "total_xp_earned": 0,
  "checkpoints_saved": 0,
  "achievements_unlocked": [],
  "perfect_streak": 0
}
```

**`memory/system/user/checklist_state.json`:**
```json
{
  "checklists": {},
  "last_updated": "2025-12-02T00:00:00Z"
}
```

### Issue: Port 5050 already in use

**Cause:** Another process using port 5050

**Solution:**

```bash
# Find process using port 5050
lsof -i :5050

# Kill process
kill -9 <PID>

# Or change port (see Configuration)
```

### Issue: Changes not showing up

**Cause:** Browser caching old data

**Solution:**

```bash
# Hard refresh in browser
# Chrome/Firefox: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# Safari: Cmd+Option+R

# Or clear cache and reload
```

### Issue: Progress bars not updating

**Cause:** Auto-refresh JavaScript not running

**Solution:**

```bash
# Open browser console (F12)
# Look for JavaScript errors

# Check dashboard.js is loading:
curl http://127.0.0.1:5050/static/dashboard.js

# Verify updateDashboard() function exists
```

### Issue: API returns 404

**Cause:** Flask routes not registered

**Solution:**

```bash
# Check server.py has all routes defined
grep "@app.route" extensions/web/dashboard/server.py

# Restart server
# Ctrl+C then: python server.py
```

---

## Customization

### Styling (NES.css)

The dashboard uses [NES.css](https://nostalgic-css.github.io/NES.css/) for retro styling.

**Change Theme Colors:**

Edit `templates/index.html`:

```html
<style>
    :root {
        --primary: #209cee;      /* Change primary color */
        --success: #92cc41;      /* Change success color */
        --warning: #f7d51d;      /* Change warning color */
        --error: #e76e55;        /* Change error color */
    }
</style>
```

**Add Custom Widgets:**

1. Add HTML section in `templates/index.html`
2. Add data fetch in `static/dashboard.js`
3. Add API endpoint in `server.py`

**Example - Weather Widget:**

**`server.py`:**
```python
@app.route('/api/weather')
def weather():
    # Read weather data from file or API
    return jsonify({"temp": 72, "condition": "Sunny"})
```

**`dashboard.js`:**
```javascript
function updateWeather() {
    fetch('/api/weather')
        .then(response => response.json())
        .then(data => {
            document.getElementById('weather-temp').textContent = data.temp + '°F';
            document.getElementById('weather-condition').textContent = data.condition;
        });
}
```

**`index.html`:**
```html
<div class="nes-container">
    <h3>🌤️ Weather</h3>
    <p>Temperature: <span id="weather-temp">--</span></p>
    <p>Condition: <span id="weather-condition">--</span></p>
</div>
```

---

## Advanced Usage

### Running in Background

**Using `screen`:**

```bash
screen -S udos-dashboard
cd extensions/web/dashboard
python server.py

# Detach: Ctrl+A, then D
# Reattach: screen -r udos-dashboard
```

**Using `nohup`:**

```bash
nohup python extensions/web/dashboard/server.py > dashboard.log 2>&1 &
```

### Production Deployment

For production use, use **Gunicorn** or **uWSGI**:

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5050 server:app
```

### CORS Configuration

To allow external access:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

### HTTPS/SSL

For secure connections:

```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL
app.run(ssl_context=('cert.pem', 'key.pem'), port=5050)
```

---

## Integration with uDOS

### Launching from uDOS

Create a uCODE alias:

**File:** `memory/ucode/aliases.upy`

```python
# Launch dashboard
ALIAS dashboard "python extensions/web/dashboard/server.py"
```

**Usage:**

```bash
dashboard
# Opens dashboard server in background
```

### Auto-Start with uDOS

Edit `core/uDOS_startup.py`:

```python
import subprocess

def start_dashboard():
    """Start dashboard server on startup."""
    subprocess.Popen([
        "python",
        "extensions/web/dashboard/server.py"
    ])

# Call in startup sequence
start_dashboard()
```

---

## Performance

### Resource Usage

**Typical:**
- CPU: < 1%
- RAM: ~30-50 MB
- Network: Minimal (local only)

**Optimization Tips:**

1. **Increase refresh interval** (reduce API calls):
   ```javascript
   setInterval(updateDashboard, 10000);  // 10s instead of 5s
   ```

2. **Cache JSON responses** (Flask):
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})

   @app.route('/api/status')
   @cache.cached(timeout=5)
   def status():
       # Cached for 5 seconds
   ```

3. **Disable debug mode**:
   ```python
   app.run(debug=False)
   ```

---

## Security Considerations

### Local Access Only

Default configuration allows **localhost only** (`127.0.0.1`).

**To allow network access:**

```python
app.run(host='0.0.0.0', port=5050)  # ⚠️ Security risk on public networks
```

### Authentication

For production, add basic auth:

```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

users = {"admin": "password"}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route('/api/status')
@auth.login_required
def status():
    # Protected endpoint
```

### Rate Limiting

Prevent abuse:

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: '127.0.0.1')

@app.route('/api/status')
@limiter.limit("60 per minute")
def status():
    # Max 60 requests per minute
```

---

## FAQ

**Q: Can I run the dashboard on a different machine?**

A: Yes, change `host` to `0.0.0.0` and use the machine's IP address. Ensure firewall allows port 5050.

**Q: Can I embed the dashboard in another app?**

A: Yes, use the API endpoints to fetch JSON data. All widgets are API-backed.

**Q: How do I add custom metrics?**

A: Add fields to state JSON files, create API endpoints in `server.py`, update `dashboard.js` to fetch data.

**Q: Can I use a different CSS framework?**

A: Yes, replace NES.css CDN link in `index.html` with any framework (Bootstrap, Tailwind, etc.).

**Q: Does the dashboard work offline?**

A: Yes, all data is local. No external API calls except NES.css CDN (can be downloaded locally).

---

## Additional Resources

- **Systems Integration:** `wiki/Systems-Integration.md`
- **Command Reference:** `wiki/Command-Reference.md`
- **NES.css Docs:** https://nostalgic-css.github.io/NES.css/
- **Flask Docs:** https://flask.palletsprojects.com/

---

**Extension Path:** `extensions/web/dashboard/`
**Server Script:** `server.py`
**Template:** `templates/index.html`
**JavaScript:** `static/dashboard.js`
**Version:** 1.1.14
**Last Updated:** December 2, 2025
