# uDOS Setup Directory

This directory is reserved for setup, installation, and configuration utilities.

## Purpose

The `/core/setup/` directory provides:
- Installation scripts and wizards
- Configuration utilities
- Environment setup tools
- First-run initialization

## Current Status

This directory is part of the v1.4.0 repository restructuring. Setup functionality is currently handled by:
- `setup.py` (root) - Package installation and distribution
- `core/services/setup_wizard.py` - Interactive setup wizard
- `INSTALL.md` (root) - Installation documentation

## Future Enhancements

Planned additions for future releases:
- Automated dependency installation
- Environment configuration validators
- Extension setup utilities
- Migration tools for version upgrades

## Related Files

- `/setup.py` - Python package configuration
- `/core/services/setup_wizard.py` - Interactive setup
- `/INSTALL.md` - Installation guide
- `/requirements.txt` - Python dependencies
