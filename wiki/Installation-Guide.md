# Installation Guide

**Date:** 20251213-165500UTC (December 13, 2025)  
**Location:** Documentation - Wiki  
**Version:** v1.2.23

## Quick Start

```bash
# Install uDOS (Lite tier - 7.3MB)
pip install udos

# Verify installation
udos --version
# → uDOS v1.2.23

# Launch
udos
```

---

## Installation Tiers

uDOS offers 5 installation tiers. Choose based on your needs:

| Tier | Size | Command | Best For |
|------|------|---------|----------|
| **ultra** | ~8MB | `pip install udos[ultra]` | Core only, minimal |
| **lite** | ~7-10MB | `pip install udos` | **Recommended** - Offline survival |
| **standard** | ~28MB | `pip install udos[standard]` | + AI assistant |
| **full** | ~58MB | `pip install udos[full]` | Complete system + gameplay |
| **enterprise** | ~120MB+ | `pip install udos[enterprise]` | + Cloud + BIZINTEL |

See [PACKAGE-TIERS.md](../PACKAGE-TIERS.md) for detailed comparison.

---

## System Requirements

### Minimum

- **Python:** 3.9 or higher
- **Storage:** 10MB (ultra), 16MB (lite), 60MB (full)
- **RAM:** 256MB minimum, 512MB recommended
- **OS:** Linux, macOS, Windows

### Recommended

- **Python:** 3.12+ (latest stable)
- **Storage:** 100MB (allows for user content)
- **RAM:** 1GB for comfortable operation
- **Terminal:** Modern terminal with UTF-8 support
- **Internet:** Optional (only for AI/Cloud features)

---

## Installation Methods

### Method 1: PyPI (Recommended)

#### Lite Tier (Default)

```bash
# Install from PyPI
pip install udos

# Upgrade existing
pip install --upgrade udos
```

#### Other Tiers

```bash
# Standard (with AI)
pip install udos[standard]

# Full (complete system)
pip install udos[full]

# Enterprise (cloud + BI)
pip install udos[enterprise]
```

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .[lite]

# Run
python -m core.uDOS_main
# or
./start_udos.sh
```

### Method 3: Offline Installation

```bash
# On internet-connected machine:
pip download udos[lite]
# Downloads: udos-1.2.23-py3-none-any.whl

# Transfer .whl file to offline machine

# On offline machine:
pip install udos-1.2.23-py3-none-any.whl
```

---

## Post-Installation Setup

### Step 1: Verify Installation

```bash
udos --version
# → uDOS v1.2.23

# Or interactive check
udos
uDOS> STATUS
uDOS> TREE --sizes
uDOS> EXIT
```

### Step 2: Initialize Directories (v1.2.23)

```bash
udos
uDOS> CONFIG CHECK
# Validates 16 required directories

uDOS> CONFIG FIX
# Creates missing directories
# Sets up .archive/ structure
```

**Required Directories** (v1.2.23):
```
memory/
├── workflows/
│   ├── tasks/          # Unified task system
│   ├── missions/       # Mission scripts
│   ├── checkpoints/    # Workflow state
│   └── state/          # Execution state
├── bank/
│   ├── user/           # User settings
│   └── system/         # System config
├── docs/               # User documentation
├── drafts/             # Draft content
├── logs/               # System logs
└── ucode/              # uPY scripts
    ├── scripts/        # User scripts
    ├── tests/          # Test suites
    ├── sandbox/        # Experimental
    ├── stdlib/         # Standard library
    ├── examples/       # Example scripts
    └── adventures/     # Adventure scripts
```

### Step 3: Configure API Keys (Optional)

Only required for Standard/Full/Enterprise tiers with AI features.

```bash
# Create .env file
touch .env

# Add Gemini API key
echo "GEMINI_API_KEY=your_key_here" >> .env

# Test AI features
udos
uDOS> OK ASK "What is uDOS?"
```

**Get API Key**:
1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to .env file

### Step 4: Set Location (Optional)

```bash
udos
uDOS> CONFIG SET current_tile AA340
# Sets default TILE code for --located flag

uDOS> TIME SET UTC
# Sets system timezone
```

---

## Upgrading from v1.2.22

### Step 1: Backup Current Installation

```bash
# Backup user data
udos
uDOS> BACKUP memory/workflows/tasks/tasks.json
uDOS> BACKUP memory/missions/
uDOS> BACKUP memory/bank/user/
```

### Step 2: Upgrade Package

```bash
pip install --upgrade udos[lite]
# or your current tier
```

### Step 3: Run Migration Scripts

```bash
# Activate virtual environment (if using)
source .venv/bin/activate

# Migrate tasks to unified system (dry run first)
python dev/tools/migrate_to_unified_tasks.py --dry-run

# Review output, then run actual migration
python dev/tools/migrate_to_unified_tasks.py

Output:
  ✅ Migrated 15 tasks from tasks.json
  ✅ Migrated 8 missions
  ✅ Created unified_tasks.json
  ✅ Backup: .archive/migration-backup/

# Rename files to uDOS ID format (dry run first)
python dev/tools/rename_distributable_files.py --dry-run

# Review, then rename
python dev/tools/rename_distributable_files.py

Output:
  ✅ Renamed 35 files to uDOS ID format
  ✅ Updated 12 references
  ✅ Backup: .archive/rename-backup/
```

### Step 4: Verify Migration

```bash
udos
uDOS> CONFIG CHECK
uDOS> TASK LIST
uDOS> PROJECT LIST
uDOS> TREE memory/workflows/tasks/ --sizes
```

### Step 5: Run Tests

```bash
# Run comprehensive test suite
./start_udos.sh memory/ucode/tests/test_unified_tasks.upy

# Run shakedown validation
./start_udos.sh memory/ucode/tests/shakedown.upy

Expected:
  ✅ 5 automated tests passing
  📝 18 manual tests documented
  ✅ All v1.2.23 features validated
```

---

## Optional Extensions

### MeshCore (Full/Enterprise Tiers)

Mesh networking features.

```bash
cd extensions/cloned/
git clone https://github.com/meshcore-dev/MeshCore.git meshcore

# Verify
udos
uDOS> REPAIR
# Should detect meshcore
```

### Additional Fonts (Full Tier)

Already included in Full tier. For custom fonts:

```bash
cp my-font.woff2 extensions/assets/fonts/
udos
uDOS> REPAIR
```

---

## Troubleshooting

### "udos: command not found"

```bash
# Add Python scripts to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use Python module syntax
python -m core.uDOS_main
```

### "No module named 'core'"

```bash
# Ensure you're in uDOS directory
cd /path/to/uDOS

# Or install properly
pip install -e .[lite]
```

### "GEMINI_API_KEY not found"

```bash
# Create .env file in project root
echo "GEMINI_API_KEY=your_key" > .env

# Or set environment variable
export GEMINI_API_KEY=your_key
```

### "Permission denied"

```bash
# Make start script executable
chmod +x start_udos.sh

# Or run directly
python core/uDOS_main.py
```

### Package Too Large

```bash
# Check actual size
pip show udos | grep Location
du -sh <location>/udos

# Use smaller tier
pip uninstall udos
pip install udos[ultra]  # 8MB
```

---

## Development Installation

For contributors and developers:

```bash
# Clone with dev submodule
git clone --recurse-submodules https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev tools
pip install -e .[full,dev]

# Install development dependencies
pip install pytest pytest-cov flake8 black

# Run tests
pytest memory/ucode/tests/ -v

# Check code style
flake8 core/
black core/ --check
```

---

## Uninstallation

### Remove Package

```bash
pip uninstall udos
```

### Remove User Data (Optional)

```bash
# Backup first!
tar -czf udos-backup.tar.gz memory/

# Remove user data
rm -rf memory/
rm -f .env
```

---

## Platform-Specific Notes

### Linux

```bash
# Install Python 3.9+ if needed
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install uDOS
pip3 install udos

# Run
udos
```

### macOS

```bash
# Install Python 3.9+ via Homebrew
brew install python@3.12

# Install uDOS
pip3 install udos

# Run
udos
```

### Windows

```powershell
# Install Python 3.9+ from python.org
# Ensure "Add to PATH" is checked

# Install uDOS
pip install udos

# Run
udos
```

---

## Next Steps

After installation:

1. **Read Quick Start**: [QUICK-START.md](../QUICK-START.md)
2. **Explore Commands**: `HELP` or `HELP <command>`
3. **Check Status**: `STATUS`, `TREE`, `CONFIG CHECK`
4. **Run Tests**: `./start_udos.sh memory/ucode/tests/shakedown.upy`
5. **Create First Task**: `TASK CREATE "Learn uDOS"`
6. **Read Documentation**: [Wiki Home](Home.md)

---

**Last Updated:** 20251213-165500UTC (December 13, 2025)  
**Version:** v1.2.23  
**Status:** Production Ready

## See Also

- [Getting Started](Getting-Started.md)
- [Package Tiers](../PACKAGE-TIERS.md)
- [Task Management](Task-Management.md)
- [Command Reference](Command-Reference.md)
- [Troubleshooting](Troubleshooting-Complete.md)
