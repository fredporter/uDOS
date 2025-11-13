# uDOS Utility Scripts

This directory contains **standalone utility scripts** that are not part of the core uDOS system. These are helper tools for specific tasks.

## ⚠️ Important

**These scripts are NOT imported or used by the main uDOS application.** They are standalone utilities you can run separately for specific administrative tasks.

## Available Scripts

### config_manager.py

**Purpose**: Standalone utility for managing structured `user.json` configuration.

**Usage**:
```bash
python3 scripts/config_manager.py --help
```

**Features**:
- View current configuration
- Update specific settings
- Validate configuration structure
- Export/import configs

**Note**: This is redundant with `core/services/config_manager.py` which is used by the main application. This standalone version is kept for manual/debugging use.

---

### generate_user_config.py

**Purpose**: Generate structured `user.json` with default fields and system settings.

**Usage**:
```bash
python3 scripts/generate_user_config.py
```

**Features**:
- Creates default configuration
- Integrates TIZO location codes
- Sets up comprehensive configuration options
- Generates unique installation IDs

**Use Case**: Initial setup or configuration reset.

---

### migrate_config.py

**Purpose**: Migrate from old `USER.UDO` format to new `user.md` + `.env` structure.

**Usage**:
```bash
python3 scripts/migrate_config.py
```

**Features**:
- Reads legacy USER.UDO files
- Converts to modern format
- Integrates TIZO location codes
- Timezone detection

**Use Case**: One-time migration from pre-v1.0 configurations. Historical utility.

---

## When to Use These Scripts

### Use Core Application Instead

For normal uDOS usage, these scripts are **NOT needed**. Use the built-in commands:

```bash
# In uDOS
🔮 > SETUP          # Configure settings
🔮 > CONFIG SET     # Update configuration
🔮 > STATUS         # View system info
```

### Use These Scripts When

- **Debugging**: Need to inspect configs outside uDOS
- **Batch operations**: Updating multiple configs programmatically
- **Recovery**: Config corrupted, need to regenerate
- **Migration**: Moving from old to new format (one-time)
- **Development**: Testing configuration changes

## Script Dependencies

All scripts require:
- Python 3.8+
- uDOS core modules (for TIZO manager, etc.)

Install dependencies:
```bash
pip3 install -r ../requirements.txt
```

## Maintenance Status

These scripts are **maintained but not actively developed**. They work, but new configuration features are added to the core application, not these utilities.

**Last Updated**: November 14, 2025
**Status**: Stable, legacy utilities
