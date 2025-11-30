# Mission Control Dashboard Extension

**Version**: 1.1.2
**Type**: Web Extension
**Category**: Core
**Status**: Production Ready

## Overview

Real-time web-based dashboard for monitoring and controlling uDOS missions, scheduled tasks, and system resources.

## Features

- **Live Mission Monitoring**: Track active missions with progress bars and status indicators
- **Resource Dashboard**: Monitor API quotas, disk usage, CPU, and memory
- **Task Scheduling**: View upcoming scheduled tasks and their patterns
- **Mission Timeline**: Chronological event log with timestamps
- **Real-Time Updates**: WebSocket-powered live updates
- **Celebration Animations**: Animated overlays on mission completion
- **Responsive Design**: Works on desktop, tablet, and mobile

## Installation

### Prerequisites

```bash
pip install flask flask-socketio psutil
```

### Enable Extension

```bash
# In uDOS:
EXTENSION ENABLE mission-control
```

### Access Dashboard

Open browser to: `http://localhost:5000/dashboard`

(Assumes uDOS server is running on port 5000)

## Dashboard Layout

### 4-Panel Grid

1. **Active Missions** (top-left)
   - Mission cards with progress bars
   - Priority badges (CRITICAL, HIGH, MEDIUM, LOW)
   - Status indicators (active, paused, pending)
   - "Next Up" mission suggestion

2. **Resource Usage** (top-right)
   - API quotas (Gemini, GitHub)
   - Disk usage (sandbox + system)
   - CPU and memory monitoring
   - Color-coded status bars (green/yellow/red)

3. **Scheduled Tasks** (bottom-left)
   - List of scheduled tasks
   - Next run times
   - Schedule patterns
   - Enable/disable status

4. **Mission Timeline** (bottom-right)
   - Last 50 events
   - Event types with icons
   - Timestamps
   - Auto-scrolling

## API Endpoints

### REST API

- `GET /dashboard` - Main dashboard UI
- `GET /api/missions` - List all missions
- `GET /api/missions/:id` - Get mission details
- `GET /api/schedules` - List scheduled tasks
- `GET /api/resources` - Resource usage summary

### WebSocket

- `WS /ws/updates` - Real-time updates
  - Events: `mission_update`, `mission_completed`, `schedule_update`, `resource_update`

## Configuration

Edit `extension.json` to customize:

```json
{
  "configuration": {
    "auto_refresh": 5000,              // Auto-refresh interval (ms)
    "websocket_reconnect": true,       // Auto-reconnect WebSocket
    "celebration_duration": 3000,      // Celebration overlay duration (ms)
    "max_timeline_items": 50           // Max timeline events to display
  }
}
```

## Usage Examples

### View Active Missions

Dashboard shows all active/paused missions with:
- Real-time progress updates
- Priority indicators
- Status badges
- Next queued mission

### Monitor Resources

Resource panel displays:
- API quota usage (Gemini: 0/1500, GitHub: 0/5000)
- Disk usage (sandbox + system)
- CPU percentage
- Memory percentage

### Track Schedule

Scheduled tasks panel shows:
- Task name
- Next run time
- Schedule pattern (e.g., "daily at 03:00")
- Command to execute

### Mission Timeline

Timeline displays recent events:
- Mission created
- Mission started
- Mission completed
- Schedule updated
- Resource alerts

## Integration

### Mission Manager

Dashboard integrates with `core/services/mission_manager.py`:

```python
from extensions.core.mission_control.dashboard_handler import broadcast_mission_update

# After mission update:
broadcast_mission_update({
    'id': mission.id,
    'name': mission.name,
    'status': mission.status,
    'completed_steps': len(mission.completed_steps),
    'total_steps': len(mission.steps)
})
```

### Scheduler

Dashboard integrates with `core/services/scheduler.py`:

```python
from extensions.core.mission_control.dashboard_handler import broadcast_schedule_update

# After schedule change:
broadcast_schedule_update({
    'id': task.id,
    'name': task.name,
    'next_run': task.next_run.isoformat()
})
```

### Resource Manager

Dashboard integrates with `core/services/resource_manager.py`:

```python
from extensions.core.mission_control.dashboard_handler import broadcast_resource_update

# After resource change:
broadcast_resource_update({
    'api_quotas': {...},
    'disk': {...},
    'system': {...}
})
```

## Development

### File Structure

```
extensions/core/mission-control/
├── extension.json           # Extension manifest
├── dashboard.html           # Main UI template
├── dashboard.css            # Styling
├── dashboard.js             # Frontend logic
├── dashboard_handler.py     # Flask routes + WebSocket
└── README.md               # This file
```

### Testing

```bash
pytest sandbox/tests/test_dashboard_integration.py -v
```

All 12 tests should pass:
- ✅ File structure validation
- ✅ Configuration schema
- ✅ HTML element presence
- ✅ CSS class availability
- ✅ JavaScript method existence
- ✅ Python route definitions

### Customization

#### Add Custom Panel

1. Edit `dashboard.html` - add panel HTML
2. Edit `dashboard.css` - style the panel
3. Edit `dashboard.js` - add data loading/rendering
4. Edit `dashboard_handler.py` - add API endpoint

#### Change Theme

Edit `dashboard.css` root variables:

```css
:root {
    --bg-primary: #0a0e1a;      /* Background color */
    --text-primary: #e8eaed;    /* Text color */
    --accent-blue: #4a9eff;     /* Primary accent */
    /* ... */
}
```

## Troubleshooting

### Dashboard Won't Load

1. Check uDOS server is running
2. Check extension is enabled: `EXTENSION STATUS mission-control`
3. Check Flask/SocketIO installed: `pip list | grep -i flask`
4. Check console for errors (F12 in browser)

### WebSocket Disconnected

- Dashboard will auto-reconnect every 5 seconds
- Check server logs for WebSocket errors
- Ensure port 5000 is not blocked by firewall

### No Real-Time Updates

- Verify WebSocket connection (green dot in header)
- Check mission/schedule services are running
- Ensure broadcast functions are being called

### Timeline Not Updating

- Check `max_timeline_items` configuration
- Clear browser cache
- Check console for JavaScript errors

## Performance

### Metrics

- **Auto-Refresh**: 5 seconds (only when WebSocket disconnected)
- **WebSocket Reconnect**: 5 seconds delay
- **Timeline Limit**: 50 events (configurable)
- **Asset Size**: ~37KB total (~10KB gzipped)

### Optimization Tips

1. Reduce `auto_refresh` interval if WebSocket stable
2. Lower `max_timeline_items` for better performance
3. Use browser caching for static assets
4. Enable gzip compression on Flask server

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ❌ IE 11 (not supported)

## Security Notes

**⚠️ Current Version**: No authentication - localhost only

**Production Deployment**:
- Add user authentication
- Use HTTPS/WSS
- Implement CORS policies
- Add rate limiting
- Sanitize all user inputs

## Roadmap

### v1.2.0
- [ ] User authentication
- [ ] Mission control actions (pause/resume/cancel)
- [ ] Resource usage graphs (Chart.js)
- [ ] Mission filtering/search
- [ ] Export timeline as CSV/JSON

### v1.3.0
- [ ] Progressive Web App (PWA)
- [ ] Push notifications
- [ ] Dark/light theme toggle
- [ ] Mobile-optimized layout
- [ ] Offline mode support

## License

Part of uDOS project - see main LICENSE.txt

## Credits

- Design: uDOS Development Team
- Testing: 12 integration tests (100% passing)
- Framework: Flask + Vanilla JavaScript (no dependencies)

---

**Documentation**: See `sandbox/dev/session-v1.1.2-move6-dashboard.md` for implementation details.

**Support**: Open issue on GitHub or consult uDOS wiki.

**Version**: 1.1.2 (January 2025)
