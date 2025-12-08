# uDOS Installation Guide
**Version**: v1.2.21 (FINAL v1.2.x STABLE)
**Updated**: December 8, 2025

## Quick Install

### Prerequisites
- **Python 3.10+** (3.12 recommended)
- **pip** (included with Python 3.10+)
- **Git** (for cloning repository)
- **Node.js 18+** (optional, for VS Code extension development)

### Install from Source

```bash
# 1. Clone the repository (~104 MiB download)
# For end users (1,331 files):
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# OR for contributors (1,367 files with dev tools):
# git clone --recurse-submodules https://github.com/fredporter/uDOS.git
# cd uDOS

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run uDOS
./start_udos.sh  # On Windows: python uDOS.py
```

### What Gets Installed

**Downloaded from GitHub (tracked - 1,331 files):**
- Core system (`core/`, 525 files)
- Knowledge bank (`knowledge/`, 241 files)
- Extensions source code (`extensions/`, 323 files)
- Documentation (`wiki/`, 61 files)
- uPY scripts and tests (`memory/ucode/`, tracked subset)

**Optional dev mode (via git submodule - +36 files):**
- Development tools (`dev/tools/`)
- Project roadmap (`dev/roadmap/`)
- Development scripts (`dev/scripts/`)
- Add with: `git submodule update --init --recursive`

**Built locally (never tracked in git):**
- Python virtual environment (`.venv/`)
- Python packages (via `pip install`)
- Node modules (via `npm install` - optional for extensions)
- Build artifacts (`__pycache__/`, `.pyc` files)

**Note:** v1.2.21+ separates DISTRIBUTION (what ships) from BUILD (what you generate).
No more 6,702 node_modules files tracked in git! Repository 83.5% smaller.

## Platform Support

### macOS
✅ **Fully Supported** - macOS 11+ (Ventura/Sonoma/Sequoia)

- Terminal.app recommended
- iTerm2 also supported
- 1,062/1,062 tests passing
- All features verified (Intel & Apple Silicon)

### Linux
✅ **Fully Supported**

Tested on:
- Ubuntu 22.04+ LTS
- Debian 12+
- Fedora 39+
- Arch Linux (current)

All distributions fully functional with 100% test pass rate.

### Windows
✅ **Fully Supported**

Tested on:
- Windows 11 with Windows Terminal ✅
- Windows 10 with PowerShell ✅
- WSL2 (Ubuntu) ✅

All features functional, web GUI tested on native Windows and WSL2.

## System Requirements

### Minimum
- **CPU**: Any modern processor (2015+)
- **RAM**: 512MB available
- **Storage**: 100MB for base install
- **Display**: 80x24 terminal minimum

### Recommended
- **CPU**: Multi-core processor
- **RAM**: 1GB available
- **Storage**: 500MB (with knowledge base)
- **Display**: 120x40 terminal or larger

## Dependencies

All dependencies are in `requirements.txt`:

```txt
# Core
prompt_toolkit>=3.0.0
python-dotenv>=0.19.0
psutil>=5.8.0
requests>=2.26.0
cryptography>=41.0.0  # For 4-tier memory encryption

# Web GUI (optional)
flask>=2.0.0
flask-cors>=3.0.0
flask-socketio>=5.0.0

# AI features (optional)
google-generativeai>=0.3.0

# Testing (development only)
pytest>=7.0.0
pytest-cov>=4.0.0
```

## Verification

After installation, verify with:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run system check
python uDOS.py --version
# Should show: uDOS v1.1.0

# Run basic test
echo "STATUS" | python uDOS.py

# Run full test suite (recommended)
pytest memory/tests/test_v1_1_*.py
# All 1,062 tests should pass
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Permission Denied" on start_udos.sh
```bash
chmod +x start_udos.sh
```

### Terminal Display Issues
```bash
# Check terminal size
echo $COLUMNS x $LINES

# Should be at least 80x24
# Resize terminal if needed
```

### Performance Issues
```bash
# Check Python version (3.9+ required)
python --version

# Verify virtual environment
which python  # Should show .venv/bin/python
```

## Next Steps

After installation:

1. **Read the Quick Reference**: `cat QUICK-REFERENCE.md`
2. **Try Interactive Mode**: `./start_udos.sh`
3. **Run a Test Script**: `./start_udos.sh memory/tests/shakedown.uscript`
4. **Explore Commands**: Type `HELP` in interactive mode
5. **Read Documentation**: Browse `wiki/` directory

## Development Install

For contributing to uDOS:

```bash
# Clone with development branch
git clone https://github.com/fredporter/uDOS.git
cd uDOS
git checkout develop

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Run tests
pytest memory/tests/

# Check code style
flake8 core/
black --check core/
```

## Uninstall

```bash
# Remove virtual environment
rm -rf .venv

# Remove repository
cd ..
rm -rf uDOS
```

## Support

- **Documentation**: `docs/` and `wiki/` directories
- **Issues**: https://github.com/fredporter/uDOS/issues
- **Discussions**: https://github.com/fredporter/uDOS/discussions

---

**Platform Support Status**:
- ✅ macOS: Fully tested and supported (11+)
- ✅ Linux: Fully tested and supported (Ubuntu, Debian, Fedora, Arch)
- ✅ Windows: Fully tested and supported (10/11, WSL2)

**v1.1.0** is the **first stable public release** with full cross-platform support and 1,810 passing tests.
