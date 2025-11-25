# uDOS Scripts Directory

This directory contains utility scripts for testing, development, and convenience access to uDOS features.

## Scripts

### `test_cli.sh`
Quick CLI testing script for non-interactive command execution.

**Usage:**
```bash
./core/scripts/test_cli.sh
```

**Purpose:**
- Tests basic uDOS startup
- Executes a series of commands (help, status, blank, exit)
- Validates CLI functionality without user interaction

### `web.sh`
Web interface launcher script for quick access.

**Usage:**
```bash
./core/scripts/web.sh [command]
```

**Purpose:**
- Launches uDOS web interface
- Activates virtual environment automatically
- Forwards all arguments to `extensions/web/launch_web.py`
- Convenience wrapper for web server access

## Directory Purpose

This directory separates utility scripts from the main repository root, maintaining a clean project structure while keeping development and convenience tools organized and accessible.

## Related Directories

- `/core/tests/` - Test configuration and test suites
- `/core/setup/` - Setup and installation utilities
- `/extensions/web/` - Web interface implementation
- `/dev/tools/` - Development-specific tools and utilities

## Notes

- All scripts assume execution from the uDOS root directory
- Scripts automatically activate the virtual environment when present
- For production deployment, use `start_udos.sh` from repository root
