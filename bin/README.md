# uDOS Bin Launchers And Install Scripts

This directory contains the active install and launcher scripts for the v1.5 runtime.

## Files

### `udos` (canonical entrypoint)
- Single front door for install, launch, ops, and audit commands
- Installer entrypoint: `./bin/udos install`
- Runtime entrypoint: `./bin/udos`

**Usage:**
```bash
./bin/udos install
./bin/udos install --core
./bin/udos install --wizard
./bin/udos install --update
./bin/udos
```

### `ucode-tui-v1.5.command` (macOS)
- Double-clickable macOS launcher for the stable `ucode` TUI path
- Opens Terminal and runs `bin/udos`
- **Usage**: Double-click in Finder after installation

### `udos` release audit commands
- Automated pre-release audit with readiness scoring
- Runs the v1.5 checklist automation and writes reports
- **Usage**:
```bash
./bin/udos doctor
./bin/udos audit --target-version v1.6
./bin/udos release-check --json
```

`doctor` and `audit` run report mode. `release-check` runs strict gate mode.

### `udos-tui` (Linux/macOS shell)
- Executable launcher for the stable `uDOS` TUI path
- Runs `bin/udos`
- **Usage**: `./bin/udos-tui`

### `dev/tooling/bin/smoke-test.sh`
- Comprehensive test suite for the installer
- Tests all failure scenarios and recovery paths
- Validates vault separation and security
- **Run before deployment**: `./dev/tooling/bin/smoke-test.sh`

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

### `dev/tooling/bin/setup-dev-mode.sh`
- Dev Mode tooling bridge setup script
- Creates symlinks for tools and skills
- Called automatically by the main installer
- **Usage**: `./dev/tooling/bin/setup-dev-mode.sh`

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

9. **v1.5 TUI Build (optional enhancement)**
   - Builds `tui/bin/udos-tui` from the Bubble Tea source
   - Requires Go 1.22+
   - Installer continues even if Go/Bubble Tea build is unavailable

## Installation Modes

### Full Install (Default)
Installs everything: core + wizard + optional components
```bash
./bin/udos install
```

### Core Only
Minimal install: `ucode` + uDOS tools (no wizard server)
```bash
./bin/udos install --core
```

### Wizard Only
Adds wizard to existing core installation
```bash
./bin/udos install --wizard
```

### Update Mode
Updates existing installation
```bash
./bin/udos install --update
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
chmod +x udos
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
