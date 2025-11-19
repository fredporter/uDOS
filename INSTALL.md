# uDOS Installation Guide
**Version**: v1.0.26
**Updated**: November 19, 2025

## Quick Install (pip)

### Prerequisites
- Python 3.9+
- pip
- Git (for development)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run uDOS
./start_udos.sh  # On Windows: python uDOS.py
```

## Platform-Specific Notes

### macOS (Primary Support in v1.0.26)
✅ **Fully Tested** on macOS 13+ (Ventura/Sonoma)

- Terminal.app recommended
- iTerm2 also supported
- 370/395 tests passing
- All core functionality verified

### Linux (v1.1.1)
⏳ **Testing Pending** - Deferred to v1.1.1

Planned testing on:
- Ubuntu 22.04 LTS
- Debian 12
- Fedora 39

Expected to work but untested in v1.0.26.

### Windows (v1.1.1)
⏳ **Testing Pending** - Deferred to v1.1.1

Planned testing on:
- Windows 11 with Windows Terminal
- Windows 10 with PowerShell
- WSL2 (Ubuntu)

Expected to work but untested in v1.0.26.

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
flask>=2.3.0
werkzeug>=2.3.0

# Optional (for AI features)
google-generativeai>=0.3.0

# Testing (development only)
pytest>=7.4.0
pytest-cov>=4.1.0
```

## Verification

After installation, verify with:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run system check
python uDOS.py --version

# Run basic test
echo "STATUS" | python uDOS.py

# Run full test suite (optional)
pytest memory/tests/test_v1_0_26*.py
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
- ✅ macOS: Fully tested and supported
- ⏳ Linux: Planned for v1.1.1
- ⏳ Windows: Planned for v1.1.1

**v1.0.26** is a **macOS-first release**. Full cross-platform support coming in v1.1.1.
