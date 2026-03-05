# uDOS Bin Launchers And Install Scripts

This directory contains the active install and launcher scripts for the v1.5 runtime.

## Files

### `install-udos.sh` (Cross-platform)
- Comprehensive installation script
- Works on macOS, Ubuntu, Alpine, and generic Linux
- Handles all dependencies and configuration

**Usage:**
```bash
./install-udos.sh              # Full install
./install-udos.sh --core       # Core only
./install-udos.sh --wizard     # Add wizard
./install-udos.sh --update     # Update
./install-udos.sh --help       #Show help
```

### `ucode-tui-v1.5.command` (macOS)
- Double-clickable macOS launcher for the stable `ucode` TUI path
- Opens Terminal and runs `bin/udos tui`
- **Usage**: Double-click in Finder after installation

### `smoke-test.sh`
- Comprehensive test suite for the installer
- Tests all failure scenarios and recovery paths
- Validates vault separation and security
- **Run before deployment**: `./smoke-test.sh`

**Test coverage:**
- OS detection and hardware profiling
- Required commands check
- File structure validation
- .env creation and auto-configuration
- Vault data separation (template vs runtime)
- Recovery scenarios (missing files, partial installs)
- Non-blocking failure handling
- Security token generation
- Update scenarios
- DESTROY & REPAIR system validation
- Installer options and help text

### `setup-dev-mode.sh`
- Dev Mode tooling bridge setup script
- Creates symlinks for tools and skills
- Called automatically by the main installer
- **Usage**: `./setup-dev-mode.sh`

## What the Installer Does

1. **System Detection**
   - Identifies OS and hardware specs
   - Checks for required commands

2. **Package Manager**
   - Installs uv if not present
   - Sets up Python environment

3. **Environment Config**
   - Creates .env from template
   - Auto-configures paths and settings
   - Generates security tokens

4. **Editor & Vault**
   - Optionally installs micro editor
   - Checks for Obsidian
   - Sets up vault structure

5. **Dev Mode Tooling**
   - Enables the optional Vibe contributor tool only for the `dev` profile
   - Creates `.vibe/` symlinks for contributor tooling
   - Installs core dependencies

6. **Wizard (optional)**
   - Installs wizard dependencies
   - Sets up config and secrets

7. **Local logic runtime (optional)**
   - Guides GPT4All setup
   - Verifies local model availability
   - Configures local runtime preferences

8. **Health Check**
   - Verifies all components
   - Displays installation summary
   - Provides next steps

## Installation Modes

### Full Install (Default)
Installs everything: core + wizard + optional components
```bash
./install-udos.sh
```

### Core Only
Minimal install: `ucode` + uDOS tools (no wizard server)
```bash
./install-udos.sh --core
```

### Wizard Only
Adds wizard to existing core installation
```bash
./install-udos.sh --wizard
```

### Update Mode
Updates existing installation
```bash
./install-udos.sh --update
```

## After Installation

1. **Test Installation**
   ```bash
   ./bin/udos
   ./bin/ucode-tui-v1.5.command
   ```

2. **Run Setup Story**
   ```
   SETUP
   ```

3. **Start Wizard (if installed)**
   ```
   WIZARD start
   ```

## Troubleshooting

### Command not found after install
Add to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Permission denied
Make executable:
```bash
chmod +x install-udos.sh
chmod +x install-udos.command
chmod +x ucode-tui-v1.5.command
```

### Installation failed
Check the verbose output and ensure:
- Git is installed
- curl is installed
- Python 3.12+ is available

## Documentation

- **Full guide**: [../docs/INSTALLATION.md](../docs/INSTALLATION.md)
- **Quick start**: [../QUICK-START.md](../QUICK-START.md)
- **Main README**: [../README.md](../README.md)

## Support

For issues or questions:
- Check [../docs/INSTALLATION.md](../docs/INSTALLATION.md)
- Open an issue on GitHub
- See troubleshooting section in installation guide
