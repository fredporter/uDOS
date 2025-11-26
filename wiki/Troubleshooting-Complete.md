# Troubleshooting & Repair Guide - v1.0.0

Complete troubleshooting guide for uDOS with ASCII diagrams and step-by-step solutions.

## 📚 Quick Navigation

```
┌─────────────────────────────────────────────────────────────────┐
│                  TROUBLESHOOTING INDEX                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Quick Diagnostics        → Fast health check                │
│  2. Installation Problems    → Setup issues                     │
│  3. Runtime Errors           → Command/execution problems       │
│  4. Performance Issues       → Slow operation fixes             │
│  5. Extension Problems       → Plugin troubleshooting           │
│  6. Knowledge Bank Issues    → Content generation problems      │
│  7. uCODE Script Errors      → Script validation & debugging    │
│  8. Configuration Issues     → Settings and environment         │
│  9. Common Error Messages    → Specific error solutions         │
│ 10. Getting Help             → Support resources                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Quick Diagnostics

### System Health Check

```bash
# Run comprehensive system check
🔮 > STATUS
```

**Expected Output:**
```
┌─────────────────────────────────────────────────────────────────┐
│                      SYSTEM STATUS                               │
├─────────────────────────────────────────────────────────────────┤
│ Version:          1.4.0                                         │
│ Python:           3.11.5                              ✓         │
│ Knowledge Guides: 166 guides                          ✓         │
│ Diagrams:         68 diagrams                         ✓         │
│ Extensions:       4 active, 0 disabled                ✓         │
│ API Status:       Gemini (online)                     ✓         │
│ uCODE Validator:  Operational                         ✓         │
└─────────────────────────────────────────────────────────────────┘
```

**Problem Indicators:**
- ✗ marks → System component failing
- "Offline" API status → Network/API key issue (normal if no key)
- Missing guides/diagrams → Knowledge bank incomplete

### Quick Fix Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│                  FIRST STEPS TROUBLESHOOTING                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  □ Check Python version (3.9+)                                  │
│    python3 --version                                            │
│                                                                  │
│  □ Verify virtual environment active                            │
│    echo $VIRTUAL_ENV  (should show path)                        │
│                                                                  │
│  □ Check directory (must be in uDOS/)                          │
│    pwd  (should end with /uDOS)                                │
│                                                                  │
│  □ Verify dependencies installed                                │
│    pip list | grep -E "google|requests|pyyaml"                 │
│                                                                  │
│  □ Check logs for errors                                        │
│    tail -50 sandbox/logs/udos.log                               │
│                                                                  │
│  □ Test basic command                                           │
│    HELP  (should show command list)                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Installation Problems

### Python Version Issues

**Problem**: `python3: command not found` or version < 3.9

**Diagnosis:**
```bash
# Check Python version
python3 --version
which python3

# Check available Python versions
ls -la /usr/bin/python*     # Linux
ls -la /usr/local/bin/python*  # macOS with Homebrew
```

**Solutions:**

**macOS:**
```bash
# Install via Homebrew
brew install python@3.11

# Verify installation
python3.11 --version

# Create alias (add to ~/.zshrc)
echo 'alias python3=python3.11' >> ~/.zshrc
source ~/.zshrc
```

**Linux (Ubuntu/Debian):**
```bash
# Add deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Set as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

**Linux (Fedora/RHEL):**
```bash
# Install Python 3.11
sudo dnf install python3.11

# Verify
python3.11 --version
```

### Virtual Environment Problems

**Problem**: `ModuleNotFoundError` even after `pip install`

**Flow Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│              VIRTUAL ENVIRONMENT TROUBLESHOOTING                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Is VIRTUAL_ENV set?                                            │
│  echo $VIRTUAL_ENV                                              │
│         │                                                        │
│         ├─ YES → Is it correct path?                            │
│         │        ├─ YES → Reinstall deps: pip install -r req... │
│         │        └─ NO  → Deactivate and reactivate             │
│         │                                                        │
│         └─ NO  → Virtual environment not active                 │
│                  ├─ Does .venv/ exist?                          │
│                  │   ├─ YES → source .venv/bin/activate         │
│                  │   └─ NO  → python3 -m venv .venv             │
│                  │                                               │
│                  └─ Still failing?                              │
│                      → Delete .venv/, recreate                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Solution:**
```bash
# 1. Deactivate current environment
deactivate

# 2. Delete problematic environment
rm -rf .venv/

# 3. Create fresh environment
python3 -m venv .venv

# 4. Activate
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 5. Upgrade pip
pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt

# 7. Verify installation
pip list | grep -E "google|pyyaml|requests"
```

### Dependency Installation Failures

**Problem**: `pip install` fails with compilation errors

**Common Issues:**

**1. Missing build tools:**
```bash
# macOS - Install Xcode Command Line Tools
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt install build-essential python3-dev

# Linux (Fedora/RHEL)
sudo dnf install gcc python3-devel
```

**2. Permission errors:**
```bash
# Don't use sudo! Use virtual environment instead
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Network issues:**
```bash
# Use alternative index
pip install -r requirements.txt -i https://pypi.org/simple

# Or with timeout increase
pip install -r requirements.txt --timeout=100
```

---

## 3. Runtime Errors

### Command Not Found

**Problem**: `❌ Unknown command: XYZ`

**Diagnostic Flow:**
```
Command "XYZ" not found
    │
    ├─ Check spelling
    │  HELP  (list all commands)
    │  Commands are case-insensitive: "help" = "HELP"
    │
    ├─ Check if extension command
    │  Some commands require extensions
    │  EXTENSION|list  (check installed extensions)
    │
    ├─ Check version compatibility
    │  Command may be from newer version
    │  VERSION  (check your version)
    │
    └─ Verify command syntax
       [Command Reference](Command-Reference.md)
```

**Solution:**
```bash
# 1. List available commands
🔮 > HELP

# 2. Check if extension needed
🔮 > EXTENSION|list

# 3. Search command reference
# See wiki/Command-Reference.md

# 4. Check uCODE validator for registered commands
python -m core.ucode.validator --help
```

### File Not Found Errors

**Problem**: `❌ File not found: path/to/file`

**Diagnosis:**
```bash
# Check current directory
pwd

# List files
ls -la

# Find file
find . -name "filename.md" -type f

# Check file permissions
ls -l path/to/file
```

**Common Causes:**

1. **Wrong directory:**
   ```bash
   # Always run from uDOS root
   cd /path/to/uDOS
   ./start_udos.sh
   ```

2. **Relative vs absolute paths:**
   ```bash
   # Use absolute paths
   🔮 > GENERATE|guide|/Users/me/uDOS/knowledge/water/topic

   # Or ensure you're in correct directory
   cd /Users/me/uDOS
   🔮 > GENERATE|guide|knowledge/water/topic
   ```

3. **Case sensitivity (Linux/macOS):**
   ```bash
   # Won't work: Knowledge/Water/File.md
   # Must be: knowledge/water/file.md
   ```

### API Connection Errors

**Problem**: `❌ API connection failed` or `Gemini API error`

**Don't panic!** uDOS works offline.

**Diagnostic Steps:**
```
API Error Occurred
    │
    ├─ Check internet connection
    │  ping google.com
    │  curl https://api.google.com
    │
    ├─ Check API key
    │  cat .env | grep GEMINI_API_KEY
    │  Key should be 39 characters
    │
    ├─ Verify API key validity
    │  Visit: https://makersuite.google.com/app/apikey
    │  Test with: python extensions/core/ok-assist/examples/test_gemini.py
    │
    └─ Use offline mode
       uDOS continues working without API
       Generate commands use templates instead
```

**Solutions:**

**1. Add/fix API key:**
```bash
# Edit .env file
nano .env

# Add line:
GEMINI_API_KEY='your-api-key-here'

# Save and restart uDOS
```

**2. Test API connection:**
```bash
# Run test script
.venv/bin/python extensions/core/ok-assist/examples/test_gemini.py

# Expected output:
# ✓ API connection successful
# ✓ Model responding correctly
```

**3. Work offline:**
```bash
# No API key needed for:
- SEARCH commands
- File management
- uCODE script execution
- Configuration
- Most system operations

# AI features use templates when offline
```

---

## 4. Performance Issues

### Slow Command Execution

**Problem**: Commands take too long to execute

**Performance Diagnostic:**
```
┌─────────────────────────────────────────────────────────────────┐
│                PERFORMANCE TROUBLESHOOTING                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Slow Startup?                                                  │
│  ├─ Check extension loading                                     │
│  │  Disable unused extensions in sandbox/user/user.json          │
│  └─ Reduce session history size (config setting)                │
│                                                                  │
│  Slow GENERATE commands?                                        │
│  ├─ API timeout (Gemini response delay)                        │
│  │  Normal for complex diagrams (30-60 seconds)                 │
│  └─ Network latency                                             │
│      Test: ping generativelanguage.googleapis.com               │
│                                                                  │
│  Slow SEARCH commands?                                          │
│  ├─ Large knowledge bank (1000+ guides)                        │
│  │  Solution: Use category filters                              │
│  └─ Index rebuild needed                                        │
│      Run: MANAGE|rebuild-index                                  │
│                                                                  │
│  General Slowness?                                              │
│  ├─ Check system resources                                      │
│  │  top  (CPU usage)                                            │
│  │  df -h  (disk space)                                         │
│  └─ Clear logs                                                  │
│      rm sandbox/logs/*.log                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Solutions:**

```bash
# 1. Check system resources
top  # Press 'q' to quit

# 2. Clear logs (if very large)
du -sh sandbox/logs/
rm sandbox/logs/udos.log  # Will be recreated

# 3. Optimize configuration
# Edit sandbox/user/user.json:
{
  "max_session_history": 100,  # Reduce from 1000
  "auto_save_interval": 300,   # Increase from 60
  "enable_auto_backup": false  # Disable if slow
}

# 4. Disable unused extensions
🔮 > EXTENSION|disable|extension-name
```

### High Memory Usage

**Problem**: uDOS using too much RAM

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep python

# Detailed process info
top -p $(pgrep -f uDOS)
```

**Common Causes & Solutions:**

1. **Large session history:**
   ```bash
   # Reduce in sandbox/user/user.json
   "max_session_history": 50  # Down from 1000
   ```

2. **Many loaded guides:**
   ```bash
   # Knowledge bank loaded into memory
   # Normal with 166 guides: ~20-50 MB
   # If higher, check for memory leaks
   ```

3. **Extension issues:**
   ```bash
   # Disable extensions one by one
   🔮 > EXTENSION|disable|ok-assist
   # Monitor memory usage
   ```

---

## 5. Extension Problems

### Extension Won't Install

**Problem**: `Extension installation failed`

**Diagnostic Flow:**
```
Installation Failed
    │
    ├─ Check internet connection
    │  Extension may need to clone from GitHub
    │  ping github.com
    │
    ├─ Check disk space
    │  df -h
    │  Extensions need 50-200 MB each
    │
    ├─ Check Git installed
    │  git --version
    │  sudo apt install git  # If missing
    │
    └─ Manual installation
       cd extensions/cloned
       git clone [extension-url]
```

**Solution:**
```bash
# 1. Verify extension exists
ls extensions/setup/
# Look for setup_[extension].sh

# 2. Run setup script manually
cd extensions/setup
bash setup_typo.sh

# 3. Check for errors
# If "Permission denied":
chmod +x setup_typo.sh
bash setup_typo.sh

# 4. Verify installation
🔮 > EXTENSION|list
```

### Extension Not Loading

**Problem**: Extension installed but not available

**Check extension status:**
```bash
🔮 > EXTENSION|list

# Should show:
# ✓ extension-name (active)
# If shows ✗ or missing, extension not loaded
```

**Solutions:**

1. **Check extension.json:**
   ```bash
   cat extensions/my-extension/extension.json
   # Verify valid JSON
   # Check "type", "entry_point", "compatibility"
   ```

2. **Check dependencies:**
   ```bash
   # Read extension README
   cat extensions/my-extension/README.md

   # Install missing dependencies
   pip install -r extensions/my-extension/requirements.txt
   ```

3. **Enable extension:**
   ```bash
   # Edit sandbox/user/user.json
   {
     "extensions_enabled": ["ok-assist", "my-extension"]
   }

   # Restart uDOS
   ```

4. **Check logs:**
   ```bash
   grep "extension" sandbox/logs/udos.log
   # Look for error messages
   ```

---

## 6. Knowledge Bank Issues

### Content Generation Fails

**Problem**: `GENERATE` command fails or produces empty content

**Diagnostic Tree:**
```
GENERATE fails
    │
    ├─ API key missing/invalid?
    │  cat .env | grep GEMINI
    │  └─ Add valid key or accept offline mode
    │
    ├─ Category doesn't exist?
    │  ls knowledge/
    │  └─ Use valid category: water, fire, shelter, etc.
    │
    ├─ Permissions issue?
    │  ls -ld knowledge/water/
    │  └─ chmod u+w knowledge/water/
    │
    └─ Topic too complex?
       Simplify topic or use detailed mode
```

**Solutions:**

```bash
# 1. Test with simple generation
🔮 > GENERATE|guide|water|boiling

# 2. Check API connection
.venv/bin/python extensions/core/ok-assist/examples/test_quick.py

# 3. Use offline mode (templates)
# Edit sandbox/user/user.json:
{
  "force_offline_mode": true
}

# 4. Check file permissions
chmod -R u+w knowledge/
```

### Diagram Generation Problems

**Problem**: Diagrams not generating or malformed

**Solutions:**

```bash
# 1. Test simple diagram
🔮 > GENERATE|diagram|water_filter|ascii

# 2. Check formats available
# Valid: ascii, teletext, svg-technical, svg-organic

# 3. Verify output directory exists
mkdir -p knowledge/diagrams/water/

# 4. Check generated files
ls -lh knowledge/diagrams/

# 5. Validate diagram files
# ASCII should be text
cat knowledge/diagrams/water_filter_ascii.txt

# HTML should start with <!DOCTYPE
head -1 knowledge/diagrams/water_filter_teletext.html

# SVG should start with <svg
head -1 knowledge/diagrams/water_filter_technical.svg
```

---

## 7. uCODE Script Errors

### Script Validation Failures

**Problem**: `.uscript` file has syntax errors

**Validate script:**
```bash
# Run validator
python -m core.ucode.validator --lint myfile.uscript

# Output shows:
# - Line numbers with errors
# - Error types (syntax, undefined variable, etc.)
# - Warnings about best practices
```

**Common Errors:**

**1. Invalid command:**
```uscript
# ✗ Wrong
[GENRATE|guide|water]  # Typo in command

# ✓ Correct
[GENERATE|guide|water]
```

**2. Missing parameters:**
```uscript
# ✗ Wrong
[GENERATE|guide]  # Missing category

# ✓ Correct
[GENERATE|guide|water|topic]
```

**3. Undefined variables:**
```uscript
# ✗ Wrong
[GENERATE|guide|$category|$topic]  # Variables not defined

# ✓ Correct
$category = "water"
$topic = "filtration"
[GENERATE|guide|$category|$topic]
```

**4. Invalid frontmatter:**
```uscript
# ✗ Wrong
---
title: Missing quotes
---

# ✓ Correct
---
title: "Proper YAML"
version: "1.0.0"
---
```

### Script Execution Fails

**Problem**: Script validates but fails to run

**Debug process:**

```bash
# 1. Validate first
python -m core.ucode.validator --lint script.uscript

# 2. Run with verbose output
🔮 > MISSION|run|script.uscript|verbose

# 3. Check specific command
# Extract failing command from script
# Test it manually in CLI

# 4. Check logs
tail -50 sandbox/logs/udos.log | grep ERROR
```

---

## 8. Configuration Issues

### Settings Not Persisting

**Problem**: Configuration changes don't save across restarts

**Check configuration files:**
```bash
# 1. User settings
cat sandbox/user/user.json
# Should be valid JSON

# 2. Environment variables
cat .env
# Should have KEY='value' format

# 3. File permissions
ls -l sandbox/user/user.json
# Should be writable: -rw-r--r--
```

**Solutions:**

```bash
# 1. Validate JSON syntax
python3 -c "import json; print(json.load(open('sandbox/user/user.json')))"

# 2. Fix permissions
chmod 644 sandbox/user/user.json
chmod 644 .env

# 3. Reset to defaults
cp sandbox/user/user.json sandbox/user/user.json.backup
cat > sandbox/user/user.json << 'EOF'
{
  "username": "user",
  "theme": "c64",
  "workspace": "memory/workspace"
}
EOF
```

### Environment Variables Not Loading

**Problem**: API keys or settings in `.env` not recognized

**Diagnosis:**
```bash
# 1. Check .env file exists
ls -la .env

# 2. Check format
cat .env
# Should be: KEY='value' NOT KEY="value"

# 3. Test loading
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Solutions:**

```bash
# 1. Correct format
# ✗ Wrong:
GEMINI_API_KEY="abc123"

# ✓ Correct:
GEMINI_API_KEY='abc123'

# 2. No spaces around =
# ✗ Wrong:
GEMINI_API_KEY = 'abc123'

# ✓ Correct:
GEMINI_API_KEY='abc123'

# 3. Reload environment
# Restart uDOS to reload .env
```

---

## 9. Common Error Messages

### Complete Error Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                  ERROR MESSAGE DECODER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  "ModuleNotFoundError: No module named 'X'"                     │
│  → pip install X                                                │
│  → Activate virtual environment first                           │
│                                                                  │
│  "Permission denied"                                            │
│  → chmod +x file                                                │
│  → Check file ownership                                         │
│                                                                  │
│  "API key not found"                                            │
│  → Add GEMINI_API_KEY to .env                                   │
│  → uDOS works offline without key                               │
│                                                                  │
│  "Command not found"                                            │
│  → Check spelling with HELP                                     │
│  → Verify command exists in your version                        │
│                                                                  │
│  "File not found"                                               │
│  → Use absolute paths                                           │
│  → Check current directory with pwd                             │
│                                                                  │
│  "Invalid JSON"                                                 │
│  → Validate: python -m json.tool file.json                      │
│  → Check for trailing commas, quotes                            │
│                                                                  │
│  "Extension failed to load"                                     │
│  → Check extension.json validity                                │
│  → Verify dependencies installed                                │
│                                                                  │
│  "Syntax error in script"                                       │
│  → Run validator: python -m core.ucode.validator file.uscript   │
│  → Check command spelling and parameters                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Getting Help

### Self-Help Resources

**1. Documentation:**
- [Getting Started Tutorial](Tutorial-Getting-Started.md)
- [Command Reference](Command-Reference.md)
- [FAQ](FAQ.md)
- [Architecture Guide](Architecture-Contributor-Guide.md)

**2. Check Logs:**
```bash
# Error log
tail -100 sandbox/logs/udos.log | grep ERROR

# Full debug log
cat sandbox/logs/debug.log
```

**3. Search Issues:**
https://github.com/fredporter/uDOS/issues

**4. Run Diagnostics:**
```bash
🔮 > STATUS
🔮 > VERSION
🔮 > CONFIG|show
```

### Community Support

**GitHub Discussions:**
https://github.com/fredporter/uDOS/discussions

**Open an Issue:**
https://github.com/fredporter/uDOS/issues/new

**Include in bug report:**
```
1. uDOS version (from STATUS command)
2. Python version (python3 --version)
3. Operating system (uname -a)
4. Complete error message
5. Steps to reproduce
6. Expected vs actual behavior
7. Relevant logs (last 50 lines)
```

---

## Prevention & Maintenance

### Regular Maintenance

```bash
# Weekly:
- Check logs for errors: grep ERROR sandbox/logs/udos.log
- Clear old logs: rm sandbox/logs/*.log.old
- Update dependencies: pip install -r requirements.txt --upgrade

# Monthly:
- Backup knowledge bank: cp -r knowledge/ knowledge_backup/
- Backup memory: cp -r memory/ memory_backup/
- Pull latest updates: git pull origin main

# Before major updates:
- Full backup: tar -czf udos_backup_$(date +%Y%m%d).tar.gz .
- Test in separate directory
- Review CHANGELOG.md
```

### Best Practices

```
✓ Always use virtual environment
✓ Keep backups of custom content
✓ Review logs periodically
✓ Update regularly
✓ Test scripts with validator before running
✓ Use absolute paths in scripts
✓ Document custom configurations
✓ Monitor disk space
```

---

**Version:** 1.4.0
**Last Updated:** November 25, 2025
**See Also:** [FAQ](FAQ.md) | [Getting Started](Tutorial-Getting-Started.md) | [Command Reference](Command-Reference.md)
