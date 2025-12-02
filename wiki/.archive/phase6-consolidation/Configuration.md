# Configuration & Customization

Complete guide to configuring and customizing uDOS for your workflow

---

## Table of Contents

1. [User Settings (USER.UDT)](#user-settings)
2. [Environment Variables](#environment-variables)
3. [Configuration Options Reference](#configuration-options)
4. [Platform-Specific Settings](#platform-specific)
5. [Advanced Configuration](#advanced-configuration)

---

## User Settings (USER.UDT)

The `data/USER.UDT` file stores all user preferences and settings.

### File Location
```bash
uDOS/
  data/
    USER.UDT          # Main user configuration file
```

### File Format

USER.UDT is a JSON file with the following structure:

```json
{
  "user": {
    "name": "Your Name",
    "location": "TZONE:KBFI",
    "screen_tier": 10,
    "theme": "classic_mac"
  },
  "preferences": {
    "autocomplete": true,
    "color_enabled": true,
    "prompt_style": "minimal",
    "viewport_auto_detect": true
  },
  "paths": {
    "knowledge_root": "knowledge/",
    "memory_root": "memory/",
    "extensions_root": "extensions/"
  },
  "security": {
    "encryption_enabled": true,
    "api_key_encrypted": "...",
    "require_confirmation": ["DELETE", "RESET"]
  }
}
```

### Key Settings

#### User Information
- `user.name`: Your display name
- `user.location`: Default TZONE location (see [TILE Commands](TILE-Commands.md))
- `user.screen_tier`: Preferred viewport tier (0-14)
- `user.theme`: Active theme name

#### Preferences
- `autocomplete`: Enable command autocomplete (default: `true`)
- `color_enabled`: Use colors in output (default: `true`)
- `prompt_style`: Prompt format (`minimal`, `detailed`, `custom`)
- `viewport_auto_detect`: Auto-detect terminal size (default: `true`)

#### Paths
- `knowledge_root`: Knowledge base directory
- `memory_root`: Memory/workspace directory
- `extensions_root`: Extensions directory

#### Security
- `encryption_enabled`: Encrypt PRIVATE tier data
- `api_key_encrypted`: Encrypted API keys
- `require_confirmation`: Commands requiring confirmation

---

## Environment Variables

uDOS respects these environment variables:

### Essential Variables

```bash
# Python environment
PYTHONPATH=/path/to/uDOS/core

# uDOS configuration
UDOS_HOME=/path/to/uDOS
UDOS_CONFIG=/path/to/custom/USER.UDT
UDOS_THEME=classic_mac
UDOS_SCREEN_TIER=10

# API keys (optional)
GEMINI_API_KEY=your_api_key_here
```

### Setting Environment Variables

#### macOS/Linux
Add to `~/.zshrc` or `~/.bashrc`:
```bash
export UDOS_HOME="$HOME/Documents/uDOS"
export UDOS_THEME="classic_mac"
export UDOS_SCREEN_TIER=10
```

#### Windows
```cmd
setx UDOS_HOME "C:\Users\YourName\Documents\uDOS"
setx UDOS_THEME "classic_mac"
setx UDOS_SCREEN_TIER "10"
```

---

## Configuration Options Reference

### Display Settings

#### Screen Tiers (0-14)
Control output density and detail level:

| Tier | Width | Height | Description | Devices |
|:----:|:-----:|:------:|:------------|:--------|
| 0 | 40 | 12 | Minimal | Smartwatch |
| 1-2 | 40-60 | 15-20 | Small | Old phones |
| 3-4 | 80 | 24 | Standard | Classic terminals |
| 5-6 | 100-120 | 30-40 | Medium | Modern terminals |
| 7-9 | 132-160 | 43-50 | Large | Wide screens |
| 10-12 | 200-240 | 60-80 | Extra Large | Modern monitors |
| 13-14 | 280-320 | 90-100 | Ultra Wide | 4K displays |

**Set screen tier**:
```bash
VIEWPORT TIER 10        # Set to tier 10
```

#### Theme Selection

**List available themes**:
```bash
THEME LIST
```

**Apply theme**:
```bash
THEME APPLY classic_mac
```

**Built-in themes**:
- `classic_mac` - Retro Mac Plus aesthetic (ChicagoFLF font)
- `commodore` - Commodore PET/C64 style (PetMe fonts)
- `terminal_green` - Classic green phosphor
- `amber` - Amber monochrome
- `cyberpunk` - Neon colors
- `minimal` - Black and white
- `nord` - Nordic color palette
- `dracula` - Dracula color scheme
- `solarized` - Solarized light/dark

**Available fonts**:
- `ChicagoFLF` - Classic Macintosh System font
- `chicago-12-1` - Enhanced Chicago variant
- `PetMe` - Commodore PET/CBM authentic font
- `PetMe64` - Commodore 64 character set
- `PetMe128` - Commodore 128 character set
- `PetMe2X` - Double-wide characters
- `PetMe2Y` - Double-height characters
- `mallard-blocky` - Modern monospace
- `sysfont` - Clean system font

See [Theme System](Theme-System.md) for creating custom themes.

#### Font Configuration

**Set font in theme**:
```json
{
  "theme": {
    "name": "custom_commodore",
    "font": "PetMe64",
    "font_size": 14,
    "line_height": 1.2,
    "anti_aliasing": false
  }
}
```

**Recommended font settings**:
- **High DPI displays**: 14-16pt, anti-aliasing off for pixel-perfect
- **Standard displays**: 12-14pt, anti-aliasing optional
- **Low resolution**: 10-12pt, anti-aliasing off

**Commodore PET/C64 variants**:
- `PetMe` - Standard PET font
- `PetMe64` - Authentic C64 character ROM
- `PetMe128` - C128 variant
- `PetMe642Y` - C64 with double-height
- `PetMe1282Y` - C128 with double-height

**Font credits**:
- ChicagoFLF: Public Domain
- PetMe family: Kreative Software (Free Use License)
- chicago-12-1, mallard: CC BY-SA 3.0
- sysfont: SIL Open Font License

See `extensions/fonts/LICENSE_ASSESSMENT.md` for complete licensing.

### Command Behavior

#### Autocomplete
Enable/disable smart command completion:
```json
{
  "preferences": {
    "autocomplete": true,
    "autocomplete_delay_ms": 180
  }
}
```

#### Command History
Configure command history retention:
```json
{
  "history": {
    "enabled": true,
    "max_entries": 1000,
    "persist": true,
    "file": "sandbox/logs/command_history.log"
  }
}
```

#### Confirmation Prompts
Commands requiring user confirmation:
```json
{
  "security": {
    "require_confirmation": [
      "DELETE",
      "RESET",
      "REPAIR MODE 5",
      "COMMUNITY SHARE"
    ]
  }
}
```

### Performance Tuning

#### Cache Settings
```json
{
  "performance": {
    "cache_enabled": true,
    "cache_size_mb": 100,
    "preload_modules": ["commands", "viewport", "grid"]
  }
}
```

#### Database Optimization
```json
{
  "database": {
    "pragma_cache_size": 10000,
    "pragma_journal_mode": "WAL",
    "pragma_synchronous": "NORMAL",
    "vacuum_on_startup": false
  }
}
```

### File Operations

#### Default Paths
```json
{
  "paths": {
    "knowledge_root": "knowledge/",
    "memory_root": "memory/",
    "extensions_root": "extensions/",
    "output_root": "output/",
    "temp_root": "/tmp/udos/"
  }
}
```

#### File Associations
```json
{
  "file_types": {
    ".uscript": "RUN",
    ".md": "LOAD",
    ".json": "LOAD",
    ".txt": "LOAD"
  }
}
```

---

## Platform-Specific Settings

### macOS Configuration

#### Terminal.app Settings
Recommended terminal settings:
- Font: Monaco 12pt or SF Mono 13pt
- Columns: 100+
- Rows: 30+
- Scrollback: 10,000 lines
- Use Option as Meta key: Yes

#### Path Configuration
```bash
# ~/.zshrc
export UDOS_HOME="$HOME/Documents/uDOS"
export PATH="$UDOS_HOME:$PATH"

# Alias for quick launch
alias udos="cd $UDOS_HOME && ./start_udos.sh"
```

### Linux Configuration

#### Terminal Preferences
Recommended for gnome-terminal/konsole:
- Font: DejaVu Sans Mono 11pt or Hack 12pt
- Columns: 100+
- Rows: 30+
- Color scheme: System default or custom theme

#### systemd Service (Optional)
Run uDOS as background service:
```ini
# ~/.config/systemd/user/udos.service
[Unit]
Description=uDOS Personal Knowledge System
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/username/uDOS
ExecStart=/home/username/uDOS/start_udos.sh --daemon
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable service:
```bash
systemctl --user enable udos
systemctl --user start udos
```

### Windows Configuration

#### WSL2 Setup (Recommended)
1. Install WSL2 with Ubuntu
2. Install Python 3.8+
3. Clone uDOS to WSL filesystem
4. Configure Windows Terminal

#### Windows Terminal Settings
```json
{
  "profiles": {
    "list": [
      {
        "name": "uDOS",
        "commandline": "wsl.exe -d Ubuntu bash -c 'cd ~/uDOS && ./start_udos.sh'",
        "fontSize": 11,
        "fontFace": "Cascadia Code",
        "colorScheme": "One Half Dark"
      }
    ]
  }
}
```

---

## Advanced Configuration

### Custom Prompt Styles

Edit `core/uDOS_prompt.py` to create custom prompts:

```python
# Minimal prompt
"uDOS> "

# Detailed prompt with location and time
"[14:32] uDOS@KBFI> "

# Custom prompt with XP
"[XP:1250] uDOS> "

# Full context prompt
"[Tier:10 KBFI XP:1250]> "
```

### Extension Configuration

Configure extension loading:
```json
{
  "extensions": {
    "autoload": ["web", "teletext"],
    "disabled": [],
    "search_paths": [
      "extensions/core/",
      "extensions/bundled/",
      "extensions/cloned/"
    ]
  }
}
```

### Logging Configuration

Control log verbosity and output:
```json
{
  "logging": {
    "level": "INFO",
    "file": "sandbox/logs/udos.log",
    "console": false,
    "max_size_mb": 10,
    "backup_count": 5,
    "format": "%(asctime)s - %(levelname)s - %(message)s"
  }
}
```

Levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Network Settings

Configuration for web server and network features:
```json
{
  "network": {
    "web_server_enabled": false,
    "web_server_port": 8080,
    "web_server_host": "127.0.0.1",
    "api_enabled": false,
    "p2p_enabled": false
  }
}
```

---

## Configuration Examples

### Minimal Configuration
For low-resource systems:
```json
{
  "user": {
    "screen_tier": 3,
    "theme": "minimal"
  },
  "preferences": {
    "autocomplete": false,
    "color_enabled": false
  },
  "performance": {
    "cache_enabled": false,
    "preload_modules": []
  }
}
```

### Power User Configuration
Maximum features enabled:
```json
{
  "user": {
    "screen_tier": 12,
    "theme": "cyberpunk"
  },
  "preferences": {
    "autocomplete": true,
    "color_enabled": true,
    "prompt_style": "detailed"
  },
  "performance": {
    "cache_enabled": true,
    "cache_size_mb": 500,
    "preload_modules": ["commands", "viewport", "grid", "knowledge"]
  },
  "extensions": {
    "autoload": ["web", "teletext", "custom"]
  }
}
```

### Developer Configuration
Optimized for uDOS development:
```json
{
  "logging": {
    "level": "DEBUG",
    "console": true
  },
  "development": {
    "reload_on_change": true,
    "show_traceback": true,
    "profile_enabled": true
  }
}
```

---

## Backup and Migration

### Export Configuration
```bash
SETUP EXPORT config.json
```

### Import Configuration
```bash
SETUP IMPORT config.json
```

### Reset to Defaults
```bash
SETUP RESET
```

**Warning**: This will delete all custom settings!

---

## Troubleshooting Configuration

### Configuration File Corrupted
If USER.UDT is corrupted:
```bash
# Backup broken file
mv data/USER.UDT data/USER.UDT.backup

# Generate fresh configuration
./start_udos.sh
# Run SETUP to reconfigure
```

### Settings Not Persisting
Check file permissions:
```bash
ls -la data/USER.UDT
# Should be writable by user
```

### Theme Not Loading
Verify theme file exists:
```bash
ls -la data/themes/<theme_name>.theme.json
```

---

## Related Pages

- [Getting Started](Getting-Started.md) - Installation and first launch
- [Theme System](Theme-System.md) - Creating and managing themes
- [SETUP Command](Command-Reference.md#setup) - Interactive configuration
- [Viewport System](Architecture.md#viewport) - Screen tier details
- [Troubleshooting](Troubleshooting-Complete.md) - Fixing common issues

---

**Last Updated**: November 17, 2025
**Version**: v1.0.22
**See Also**: [Documentation Handbook](Documentation-Handbook.md)
