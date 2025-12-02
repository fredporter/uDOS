# uDOS Dashboard Extension

**Version:** 1.0.0  
**Type:** Web UI Extension  
**Port:** 5050 (configurable)

## Overview

Real-time retro dashboard for monitoring uDOS missions, checklists, and workflows. Features NES.css Nintendo 8-bit styling with auto-refresh every 5 seconds.

## Features

- **Mission Progress Tracking** - View active missions with step completion
- **Checklist Meters** - See checklist completion percentages
- **Workflow Phase Indicators** - Monitor workflow execution state
- **XP & Achievements** - Display total XP and unlocked achievements
- **Retro NES.css Styling** - Authentic 8-bit Nintendo aesthetic
- **Auto-Refresh** - Updates every 5 seconds automatically

## Installation

### 1. Install Python Dependencies

```bash
pip install flask flask-cors
```

### 2. Start Dashboard Server

From the dashboard directory:

```bash
python server.py
```

Or from uDOS:

```bash
POKE START dashboard
```

### 3. Open in Browser

Navigate to: **http://127.0.0.1:5050**

## Configuration

Edit `extension.json` to configure:

```json
{
  "settings": {
    "port": 5050,
    "host": "127.0.0.1",
    "debug": false,
    "refresh_interval": 5,
    "theme": "nes-dark"
  }
}
```

## Widgets

### 📋 Active Missions

- Mission title and priority
- Progress bar (completed/total steps)
- Total missions count
- Completed missions count

### ✓ Checklists

- Active checklist names
- Completion progress bars
- Total items across all checklists
- Completed items count

### ⚙️ Workflow Status

- Current workflow name
- Execution phase (IDLE, INIT, EXECUTE, etc.)
- Checkpoints saved
- Perfect run streak

### 🏆 XP & Achievements

- Total XP earned
- Achievement badges
- Perfect streak indicator

## API Endpoints

### GET `/api/status`

Returns complete dashboard state:

```json
{
  "timestamp": "2025-12-02T15:30:00",
  "missions": { ... },
  "checklists": { ... },
  "workflow": { ... },
  "xp": { ... }
}
```

### GET `/api/missions`

Mission data only.

### GET `/api/checklists`

Checklist data only.

### GET `/api/workflow`

Workflow execution data only.

### GET `/api/xp`

XP and achievements only.

## Data Sources

The dashboard reads from:

- `memory/workflows/state/current.json` - Workflow state
- `memory/workflows/missions/*.json` - Mission files
- `memory/system/user/checklist_state.json` - Checklist progress

## Development

### File Structure

```
dashboard/
├── extension.json         # Extension metadata
├── server.py              # Flask application
├── static/
│   └── dashboard.js       # Real-time update logic
└── templates/
    └── index.html         # Main dashboard UI
```

### Adding Widgets

1. Add HTML in `templates/index.html`
2. Add update logic in `static/dashboard.js`
3. Add data fetcher in `server.py`
4. Update `/api/status` endpoint

### Styling

Uses [NES.css](https://nostalgic-css.github.io/NES.css/) for retro aesthetic.

Custom styles defined in `<style>` block in `index.html`.

## Usage Examples

### Start Dashboard

```bash
# From uDOS
POKE START dashboard

# Direct
cd extensions/web/dashboard
python server.py
```

### Stop Dashboard

```bash
# From uDOS
POKE STOP dashboard

# Direct
Ctrl+C in terminal
```

### Check Status

```bash
# From uDOS
POKE STATUS dashboard
```

## Integration with uDOS Systems

### Missions

Dashboard detects active missions in `memory/workflows/missions/` and calculates:

- Total steps (from all moves)
- Completed steps (status == "completed")
- Progress percentage

### Checklists

Reads `checklist_state.json` to display:

- Active checklists (those with progress)
- Completion counts
- Progress percentages

### Workflows

Monitors `current.json` for:

- Active workflow name
- Execution phase
- Checkpoint count
- Perfect streak

### XP System

Displays from workflow state:

- Total XP earned
- Achievement list
- Gameplay stats

## Troubleshooting

### Port 5050 Already in Use

Change port in `extension.json`:

```json
"settings": {
  "port": 5051
}
```

### Dashboard Not Updating

- Check browser console for errors
- Verify JSON files are readable
- Check Flask server logs
- Ensure auto-refresh is enabled (5s interval)

### Missing Data

Dashboard gracefully handles missing files with:

- Empty state defaults
- "No active X" messages
- Zero counts

## Future Enhancements

- [ ] Dark/Light theme toggle
- [ ] Custom refresh intervals
- [ ] Widget drag-and-drop
- [ ] Mission timeline visualization
- [ ] Audio notifications (NES-style beeps)
- [ ] Export dashboard screenshots
- [ ] Mobile responsive layout

## Credits

- **NES.css** - Nostalgic CSS Framework
- **Flask** - Python web framework
- **Press Start 2P** - Retro font

## License

MIT License - Part of uDOS v1.1.14+

---

**Last Updated:** December 2, 2025  
**Compatibility:** uDOS v1.1.14+
