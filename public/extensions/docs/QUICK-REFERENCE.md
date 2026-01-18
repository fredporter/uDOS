# uDOS Server Quick Reference

**Status:** 📘 CURRENT DOCUMENTATION  
**Last Updated:** 2025-12-02

## Quick Commands

```bash
# Status
python extensions/server_manager.py status

# Start all
python extensions/server_manager.py start-all

# Restart terminal
python extensions/server_manager.py restart terminal

# Stop all
python extensions/server_manager.py cleanup-all
```

## URLs

- Terminal: http://localhost:8889
- API: http://localhost:5001
- Dashboard: http://localhost:8888
- Teletext: http://localhost:9002
- Desktop: http://localhost:8892

## Health Checks

```bash
curl http://localhost:8889/health  # Terminal
curl http://localhost:5001/api/health  # API
```

## Troubleshooting

```bash
# Check logs
tail -f sandbox/logs/terminal_server.log

# Kill stuck process
lsof -i :8889 | grep LISTEN
kill -9 <PID>

# Force cleanup
python extensions/server_manager.py cleanup-all
```

## Browser

- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Open DevTools: F12
- Check console for errors

## Fixed Issues (v1.0.26)

✅ Duplicate cursor removed (native caret only)
✅ Line spacing fixed (1.0)
✅ Port conflicts auto-resolved
✅ Health monitoring working
✅ API integration logging
✅ Graceful server shutdown
