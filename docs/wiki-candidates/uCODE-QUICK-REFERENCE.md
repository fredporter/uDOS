# uCODE Quick Reference

**Launch**: `python uDOS.py`

## Status

```
STATUS              Show component detection + available features
HELP                Show all commands
```

## Wizard Server (if available)

```
WIZARD start        Start Wizard server (non-blocking)
WIZARD stop         Stop Wizard server
WIZARD status       Check server health
WIZARD console      Launch Wizard interactive TUI
WIZARD [page]       Show page: status | ai | devices | quota | logs
```

## Extensions (if available)

```
PLUGIN list         List installed extensions
PLUGIN install      Install plugin
PLUGIN remove       Remove plugin
PLUGIN pack         Package for distribution
```

## Core TUI

Any other command → routed to core dispatcher

```
FILE [cmd]          File operations
NEW [file]          Create file
DELETE [file]       Delete file
WORKFLOW [cmd]      Workflow management
VIEW [file]         View file
... and 90+ more
```

## Exit

```
EXIT, QUIT          Leave uCODE
```

---

**Core-only mode**: If WIZARD/EXTENSIONS missing, uCODE runs seamlessly without them.

See [specs/uCODE-v1.3.md](../specs/uCODE-v1.3.md) for full documentation.
