# Logging System

**Version**: v1.1.6+
**Status**: Production Ready
**Architecture**: Flat-file with daily rotation

---

## Overview

uDOS v1.1.6 introduces a production-grade logging system with flat-file architecture, daily rotation, and comprehensive search capabilities. The system is designed for reliability, simplicity, and offline operation.

### Key Features

- **Flat-file logging** - No database required
- **Daily rotation** - Automatic log file management
- **Multiple categories** - Organize logs by component
- **Structured logging** - JSON format for easy parsing
- **Context injection** - Rich metadata support
- **Search utilities** - Find logs quickly
- **Retention policies** - Automatic cleanup
- **Backward compatible** - Works with existing code

---

## Quick Start

### Basic Logging

```python
from core.services.logging_manager import get_logger

# Get a logger for your component
logger = get_logger('my-component')

# Log at different levels
logger.debug('Detailed debugging information')
logger.info('General information')
logger.warning('Warning message')
logger.error('Error occurred')
```

### Session Logging

```python
from core.services.session_logger import SessionLogger

# Create session logger
logger = SessionLogger()

# Log user actions
logger.log('User executed command: HELP')

# Track moves (for gameplay)
logger.move('Navigate to shelter category')

# Log errors
logger.error('Failed to load knowledge file')

# Close session
logger.close()
```

---

## Architecture

### Directory Structure

```
sandbox/logs/
├── system/
│   ├── startup-2025-11-28.log
│   ├── config-2025-11-28.log
│   └── errors-2025-11-28.log
├── session-commands-2025-11-28.log
├── user-actions-2025-11-28.log
└── extensions/
    ├── svg-generator-2025-11-28.log
    └── teletext-2025-11-28.log
```

### Log File Format

**Filename pattern**: `{category}-{date}.log`

**Daily rotation**: New file created each day at midnight

**Content format**: Structured JSON per line

```json
{
  "timestamp": "2025-11-28T10:30:45.123456",
  "level": "INFO",
  "category": "session-commands",
  "message": "User executed command: HELP",
  "context": {
    "session": 42,
    "move": 15,
    "username": "Fred"
  }
}
```

---

## LoggingManager

The `LoggingManager` is the central logging service.

### Initialization

```python
from core.services.logging_manager import LoggingManager

# Use default log directory (sandbox/logs)
manager = LoggingManager()

# Or specify custom directory
manager = LoggingManager(log_dir='custom/path')
```

### Get a Logger

```python
# Get logger for specific category
logger = manager.get_logger('my-category')

# Specify log level
logger = manager.get_logger('my-category', level=logging.DEBUG)
```

### Convenience Function

```python
from core.services.logging_manager import get_logger

# Get logger directly (recommended)
logger = get_logger('my-category')
```

---

## Logging Levels

### DEBUG
**When**: Detailed diagnostic information
**Use for**: Development, troubleshooting
**Example**: Variable values, function calls

```python
logger.debug(f'Processing file: {filename}')
logger.debug(f'Configuration loaded: {config}')
```

### INFO
**When**: General informational messages
**Use for**: Normal operations, milestones
**Example**: Startup, successful operations

```python
logger.info('Application started')
logger.info('User logged in: Fred')
```

### WARNING
**When**: Unexpected but handled situations
**Use for**: Deprecated features, recoverable errors
**Example**: Missing optional files, fallback used

```python
logger.warning('Config file not found, using defaults')
logger.warning('API key missing, offline mode only')
```

### ERROR
**When**: Error conditions
**Use for**: Failures, exceptions
**Example**: File not found, API errors

```python
logger.error('Failed to load knowledge file')
logger.error(f'API request failed: {e}')
```

---

## Context Injection

Add rich metadata to log entries:

```python
# Get logger with context
logger = get_logger('commands', context={
    'username': 'Fred',
    'session': 42
})

# All logs include context
logger.info('Command executed')
# Result:
# {
#   "message": "Command executed",
#   "context": {"username": "Fred", "session": 42}
# }
```

---

## Log Categories

Organize logs by component or function:

### System Logs
- `startup` - Application initialization
- `config` - Configuration loading/saving
- `errors` - System-level errors

### User Logs
- `session-commands` - User command history
- `user-actions` - User interactions
- `moves` - Gameplay move tracking

### Extension Logs
- `svg-generator` - SVG generation activity
- `teletext` - Teletext rendering
- `assistant` - AI assistant interactions

### Development Logs
- `debug` - Development/debugging
- `performance` - Performance metrics
- `tests` - Test execution

---

## Search Utilities

Find logs quickly with built-in search:

```python
from core.services.logging_manager import LoggingManager

manager = LoggingManager()

# Search by pattern (case-insensitive)
results = manager.search_logs('error')

# Search specific category
results = manager.search_logs('failed', category='session-commands')

# Case-sensitive search
results = manager.search_logs('ERROR', case_sensitive=True)

# Results format
for entry in results:
    print(f"{entry['timestamp']}: {entry['message']}")
```

---

## Retention Policies

Automatic log cleanup to manage disk space:

### Configuration

```python
manager = LoggingManager()

# Set retention (days)
manager.set_retention('session-commands', days=30)
manager.set_retention('debug', days=7)
manager.set_retention('errors', days=90)

# Enforce retention
deleted = manager.enforce_retention(dry_run=False)
print(f"Deleted {deleted} old log files")
```

### Default Retention

| Category | Retention | Reason |
|----------|-----------|--------|
| `session-commands` | 30 days | User history |
| `user-actions` | 30 days | Gameplay tracking |
| `errors` | 90 days | Debug reference |
| `debug` | 7 days | Development only |
| `mission-*` | Never | Permanent record |

### Mission Logs

Logs with `mission-` prefix are **never deleted** automatically:

```python
logger = get_logger('mission-mars-2025')
logger.info('Mission started')
# This log is permanent
```

---

## Log Statistics

Get insights into log usage:

```python
manager = LoggingManager()

# Get stats for all logs
stats = manager.get_log_stats()

print(f"Total size: {stats['total_size_mb']:.2f} MB")
print(f"Total files: {stats['file_count']}")

# Category breakdown
for category, info in stats['categories'].items():
    print(f"{category}: {info['count']} files, {info['size_mb']:.2f} MB")
```

---

## SessionLogger (Backward Compatible)

The `SessionLogger` maintains compatibility with older uDOS code while using the new logging system internally.

### Features

- **Session numbering** - Tracks session count
- **Move tracking** - Counts user moves/turns
- **Action logging** - Records user actions
- **Statistics** - Session/move counts

### Usage

```python
from core.services.session_logger import SessionLogger

logger = SessionLogger()

# Get session info
session_num = logger.get_session_number()
total_moves = logger.get_total_moves()

# Log user action
logger.log('User executed: HELP')

# Track a move
logger.move('Navigate to water section')

# Get move statistics
stats = logger.get_move_stats()
print(f"Current move: {stats['move_count']}")
print(f"Total moves: {stats['total_moves']}")

# Close session
logger.close()
```

---

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ Good
logger.debug(f'Processing {len(items)} items')
logger.info('Configuration loaded successfully')
logger.warning('Using fallback theme')
logger.error('Failed to connect to API')

# ❌ Bad
logger.error('Processing items')  # Not an error
logger.info('Variable x = 42')    # Too detailed for INFO
```

### 2. Log Meaningful Messages

```python
# ✅ Good
logger.info(f'User {username} logged in from {location}')
logger.error(f'Failed to load {filename}: {error_message}')

# ❌ Bad
logger.info('Success')
logger.error('Error')
```

### 3. Use Categories

```python
# ✅ Good - organized by component
startup_log = get_logger('startup')
config_log = get_logger('config')
command_log = get_logger('commands')

# ❌ Bad - everything in one log
logger = get_logger('app')
```

### 4. Include Context

```python
# ✅ Good
logger = get_logger('api', context={
    'username': username,
    'session_id': session_id
})

# ❌ Bad - no context
logger = get_logger('api')
```

### 5. Handle Sensitive Data

```python
# ✅ Good - sanitize sensitive info
logger.info(f'API key: {api_key[:4]}****')

# ❌ Bad - exposes secrets
logger.info(f'API key: {api_key}')
```

---

## Migration from Old Logger

### Old Code (v1.0.x)

```python
from core.uDOS_logger import Logger

logger = Logger()
logger.log('User action')
logger.log_error('Error message')
logger.close()
```

### New Code (v1.1.6+)

```python
from core.services.session_logger import SessionLogger

logger = SessionLogger()
logger.log('User action')
logger.error('Error message')
logger.close()
```

**Note**: `SessionLogger` is backward compatible - old code continues to work!

---

## Troubleshooting

### Logs Not Appearing

**Check log directory exists:**
```bash
ls -la sandbox/logs/
```

**Check permissions:**
```bash
chmod 755 sandbox/logs/
```

**Verify logger created:**
```python
from core.services.logging_manager import get_logger
logger = get_logger('test')
logger.info('Test message')
# Check: sandbox/logs/test-{date}.log
```

### Log Files Too Large

**Enable retention:**
```python
from core.services.logging_manager import LoggingManager
manager = LoggingManager()
manager.set_retention('large-category', days=7)
manager.enforce_retention()
```

**Lower log level:**
```python
# Change from DEBUG to INFO
logger = get_logger('category', level=logging.INFO)
```

### Searching Slow

**Search specific category:**
```python
# ❌ Slow - searches all logs
results = manager.search_logs('pattern')

# ✅ Fast - searches one category
results = manager.search_logs('pattern', category='commands')
```

**Use date-specific files:**
```python
# Search today's logs only
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
log_file = Path(f'sandbox/logs/commands-{today}.log')
# Parse log_file directly
```

---

## API Reference

### LoggingManager

| Method | Description |
|--------|-------------|
| `__init__(log_dir)` | Initialize manager |
| `get_logger(category, level)` | Get logger instance |
| `search_logs(pattern, category, case_sensitive)` | Search logs |
| `get_log_stats()` | Get statistics |
| `set_retention(category, days)` | Set retention policy |
| `enforce_retention(dry_run)` | Clean old logs |

### SessionLogger

| Method | Description |
|--------|-------------|
| `__init__(log_dir)` | Initialize session logger |
| `log(message)` | Log user action |
| `move(action)` | Track a move |
| `error(message)` | Log error |
| `get_session_number()` | Get session count |
| `get_total_moves()` | Get total moves |
| `get_move_stats()` | Get move statistics |
| `close()` | End session |

---

## Examples

### Extension Logging

```python
from core.services.logging_manager import get_logger

class MyExtension:
    def __init__(self):
        self.logger = get_logger('my-extension', context={
            'version': '1.0.0'
        })

    def process(self, data):
        self.logger.info(f'Processing {len(data)} items')
        try:
            result = self._do_work(data)
            self.logger.info('Processing complete')
            return result
        except Exception as e:
            self.logger.error(f'Processing failed: {e}')
            raise
```

### Command Handler Logging

```python
from core.services.logging_manager import get_logger

def handle_command(command, user):
    logger = get_logger('commands', context={
        'username': user.name,
        'session': user.session_id
    })

    logger.info(f'Executing command: {command}')

    # Execute command...

    logger.info('Command completed successfully')
```

### Performance Logging

```python
import time
from core.services.logging_manager import get_logger

logger = get_logger('performance')

start = time.time()
# ... do work ...
elapsed = time.time() - start

logger.info(f'Operation took {elapsed:.3f}s')
```

---

## See Also

- [Configuration Guide](Configuration.md) - System configuration
- [Developers Guide](Developers-Guide.md) - Development setup
- [System Variables](../core/docs/SYSTEM-VARIABLES.md) - Environment variables
- [Best Practices](../sandbox/docs/LOGGING-BEST-PRACTICES.md) - Detailed logging guide

---

**Updated**: November 28, 2025
**Version**: v1.1.6
