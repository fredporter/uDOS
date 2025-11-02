# uDOS Development Guidelines
**Last Updated**: October 2025
**Version**: v1.3.0

---

## 📁 Preferred File Locations

### Configuration Files
- **Command Definitions**: `data/COMMANDS.UDO`
- **Lexicon/Terminology**: `data/LEXICON.UDO`
- **Color Palette**: `data/PALETTE.UDO`
- **AI Prompts**: `data/PROMPTS.UDO`
- **Font Settings**: `data/FONTS.UDO`
- **Templates**: `data/*.UDT` (e.g., STORY.UDT, USER.UDT)

### Source Code
- **Core Modules**: `core/*.py`
- **Entry Point**: `uDOS.py` (root)
- **Startup Script**: `start_udos.sh` (root)

### Documentation
- **Wiki Pages**: `wiki/*.md` (GitHub wiki source)
- **Main README**: `README.MD` (root)
- **Development Roadmap**: `ROADMAP.MD` (root)
- **Contributing Guide**: `CONTRIBUTING.md` (root)
- **Release Notes**: `dev/docs/V1.3-COMPLETE-RELEASE.md` ⭐ **v1.3 COMPLETE GUIDE**
- **Quick References**: `dev/docs/*-QUICK-REFERENCE.md`
- **Historical Docs**: `history/docs_archive/*.md` (old implementation details)

### Testing
- **Test Scripts**: `sandbox/tests/*.uscript`
- **Test Files**: `sandbox/tests/*.py`
- **Example Files**: `examples/*.txt`

### User Workspace
- **Temporary Files**: `sandbox/*` (gitignored)
- **Session Logs**: `sandbox/logs/*.log`
- **User Config**: `sandbox/USER.UDO` (gitignored)

### Permanent Storage
- **Project Memory**: `memory/*`
- **Research**: `memory/research/*.md`
- **Missions**: `memory/missions/*.md`
- **Scripts**: `memory/scripts/*.sh`

### Extensions
- **Web Extensions**: `extensions/web/*`
- **Setup Scripts**: `extensions/setup_*.sh`

### Archives
- **Old Concepts**: `history/concepts/*.md`
- **Old Configs**: `history/data/*.UDO`
- **Implementation Docs**: `history/docs_archive/*.md` (v1.0-v1.2 detailed notes)
- **Old Roadmaps**: `history/docs_archive/ROADMAP.MD.old`
- **Backup Files**: `history/backups/*.backup`
- **Old Versions**: `history/v1.x/` (for major version archives)

---

## 🛠️ VS Code Configuration

### Launch Configurations
All launch configs are in `.vscode/launch.json`:

1. **uDOS: Interactive Mode**
   - Launches `uDOS.py` in interactive shell
   - Uses integrated terminal
   - Loads `.env` for API keys

2. **uDOS: Run Shakedown Script**
   - Runs full system test: `sandbox/tests/shakedown.uscript`
   - Uses integrated terminal
   - Good for testing changes

3. **Python: Debug Current File**
   - Debug any Python file
   - Full debugging enabled (`justMyCode: false`)

### Settings
Configured in `.vscode/settings.json`:
- Python interpreter: `.venv/bin/python`
- Auto-activate venv in terminal
- Type checking: basic
- Rulers at 80 and 120 characters
- Auto-trim whitespace
- Insert final newline

### Excluded Patterns
Files hidden in VS Code explorer:
- `.git`, `.svn`, `.hg`, `CVS`
- `.DS_Store`
- `__pycache__`, `*.pyc`

File watcher exclusions:
- `.venv/**`
- `__pycache__/**`

---

## 📝 Development Workflow

### v1.3+ Workflow

**Development Process:**
- Plan features via GitHub Issues or Discussions
- Create feature branches from `main`
- Document changes in appropriate files
- Test thoroughly with health checks and integration tests
- Submit pull requests with clear descriptions
- Update wiki for user-facing features

### Starting New Work

1. **Plan Your Work**:
   - Check ROADMAP.MD for priorities
   - Review relevant docs in `dev/docs/` and wiki
   - Note any dependencies

2. **Document Your Goals**:
   - For major features: Create/update docs in `dev/docs/`
   - For implementation details: Use inline docs and comments
   - For user guides: Update wiki pages

3. **Develop**:
   - Use file management commands (CREATE, DELETE, RENAME, etc.)
   - Test frequently with health checks
   - Monitor with DASH command
   - Check web extensions via DASH WEB

4. **Test**:
   - Run `./start_udos.sh sandbox/tests/shakedown.uscript`
   - Test file operations with UNDO/REDO
   - Verify web extensions with DASH WEB
   - Check SETTINGS system for configuration
   - Use health check CLI tool for diagnostics

5. **Complete Work**:
   - Update relevant documentation (README.MD, ROADMAP.MD, wiki)
   - Update CHANGELOG.md
   - Archive old docs to `history/docs_archive/` if needed
   - Commit with descriptive message

### File Path Rules

✅ **DO**:
- Store all command definitions in `data/COMMANDS.UDO`
- Keep test scripts in `sandbox/tests/`
- Put release notes in `dev/docs/` (e.g., V1.3-COMPLETE-RELEASE.md)
- Archive old docs to `history/docs_archive/`
- Use `sandbox/` for temporary/experimental files
- Use file management commands (CREATE, DELETE, RENAME, COPY, MOVE)
- Check SETTINGS with `SETTINGS SHOW` before hardcoding values
- Use CONFIG for .env management

❌ **DON'T**:
- Create new top-level directories without discussion
- Mix configuration files across multiple directories
- Hardcode ports/paths - use SettingsManager instead
- Leave .backup files scattered
- Create duplicate config files
- Hardcode values that should be in LEXICON.UDO or settings
- Edit .env files directly - use CONFIG command

### Testing Changes

```bash
# Run interactive mode
./start_udos.sh

# Run test script
python uDOS.py sandbox/tests/shakedown.uscript

# Or use VS Code launch config:
# F5 → "uDOS: Run Shakedown Script"
```

### Debugging

```bash
# VS Code debugger
# F5 → "uDOS: Interactive Mode"
# Set breakpoints in core/*.py files

# Check system health
REPAIR
STATUS
DASH              # CLI dashboard
DASH WEB          # GitHub-style web dashboard

# Check settings
SETTINGS SHOW
SETTINGS SHOW OUTPUT

# View logs
tail -f sandbox/logs/session_*.log

# Test file operations
CREATE test.txt
RENAME test.txt renamed.txt
UNDO              # Undo last file operation
REDO              # Redo undone operation
```

---

## 📦 File Organization Best Practices

### Configuration (`/data`)
- One canonical source for each config type
- Use `.UDO` extension for data files
- Use `.UDT` extension for templates
- JSON format for structured data

### Code (`/core`)
- One module per major feature
- Prefix all modules with `uDOS_`
- Keep modules focused and modular
- Document with inline comments

### Testing (`/sandbox/tests`)
- Use `.uscript` extension for command scripts
- Use `.py` extension for Python test files
- Name tests descriptively
- Keep test data isolated

### Documentation (`/docs` and `/history/docs_archive`)
- **User-Facing**: Keep in `dev/docs/` (release notes, quick references)
- **Implementation Details**: Archive to `history/docs_archive/` after release
- Use Markdown format
- Include date and version
- Link to related commits/PRs
- For v1.3: See `dev/docs/V1.3-COMPLETE-RELEASE.md` as example

### Memory (`/memory`)
- User-facing permanent storage
- Organize by topic/project
- Use descriptive folder names
- Commit important findings

---

## 🔄 Common Tasks

### File Operations (from within uDOS)

```bash
# Create files
CREATE myfile.txt
CREATE docs/guide.md --content "# My Guide"

# Manage files
DELETE old_file.txt
RENAME old.md new.md
COPY source.txt destination.txt
MOVE file.txt ../newlocation/

# Undo/Redo
UNDO              # Undo last file operation
REDO              # Redo undone operation

# Settings management
SETTINGS SHOW                    # View all settings
SETTINGS SHOW OUTPUT             # View output settings
SETTINGS SET system.theme DARK   # Change theme
```

### Add a New Command

1. Edit `data/COMMANDS.UDO`:
   ```json
   {
     "NAME": "MYCOMMAND",
     "SYNTAX": "MYCOMMAND <param>",
     "DESCRIPTION": "Does something useful",
     "UCODE_TEMPLATE": "[MODULE|MYCOMMAND*$1]",
     "DEFAULT_PARAMS": {}
   }
   ```

2. Add handler in `core/uDOS_commands.py`:
   ```python
   def handle_mycommand(self, params):
       # Implementation
       pass
   ```

3. Update `core/uDOS_parser.py` if needed

4. Test with `HELP MYCOMMAND`

### Add a Web Extension

1. Create extension in `extensions/web/my-extension/`

2. Create setup script: `extensions/setup_my_extension.sh`

3. Update `core/uDOS_server.py` with starter function

4. Add to dashboard: `extensions/web/dashboard/index.html`

5. Update `data/COMMANDS.UDO` with OUTPUT support

6. Test with `OUTPUT START my-extension` or via DASH WEB

### Update Documentation

1. **For v1.2 features**: Add to `dev/docs/V1.2-RELEASE-NOTES.md`

2. **For new major features**: Create release notes in `dev/docs/`

3. **For implementation details**: Document in code, archive to `history/docs_archive/` after release

4. **For roadmap**: Update `ROADMAP.MD`

5. **For users**: Update `README.MD`

6. **For wiki**: Update `wiki/` pages and deploy with `bash memory/scripts/deploy_wiki.sh`

---

## 🎯 Code Style

### Python
- Follow PEP 8
- Use 4-space indentation
- Maximum line length: 120 characters
- Prefer clarity over cleverness
- Document complex logic

### JSON/UDO Files
- Use 2-space indentation
- Keep structure consistent
- Add comments where helpful (JSON5 compatible)

### Markdown
- Use `#` for headers (not `===`)
- Code blocks with language specification
- Line breaks between sections
- Use tables for structured data

---

## 🚀 Release Process

1. **Complete Dev Round**
   - All features tested
   - Documentation updated
   - Notes in `history/docs/`

2. **Update Version Info**
   - ROADMAP.MD - mark phase complete
   - README.MD - update status
   - Any affected wiki pages

3. **Git Commit**
   ```bash
   git add .
   git commit -m "Round X: Feature Name - Brief description

   - Change 1
   - Change 2
   - See history/docs/Round-X-Summary.md for details"
   ```4. **Deploy Wiki** (if updated)
   ```bash
   bash memory/scripts/deploy_wiki.sh
   ```

---

## 📚 Key Files Reference

### Must-Know Files
- `data/COMMANDS.UDO` - All command definitions
- `core/uDOS_main.py` - Application entry point
- `core/uDOS_commands.py` - Command handlers (file ops, settings, dashboard)
- `core/uDOS_parser.py` - Command parser
- `core/uDOS_settings.py` - Settings manager
- `core/uDOS_files.py` - File operations manager
- `dev/docs/V1.2-RELEASE-NOTES.md` - Complete v1.2 documentation
- `ROADMAP.MD` - Development plan (future-focused)
- `README.MD` - Project overview

### Important Scripts
- `start_udos.sh` - Launch uDOS
- `memory/scripts/deploy_wiki.sh` - Deploy wiki updates
- `extensions/setup_*.sh` - Extension installers
- `sandbox/tests/shakedown.uscript` - System test

### Configuration Files
- `.vscode/launch.json` - Debug configurations
- `.vscode/settings.json` - Editor settings
- `.gitignore` - Git exclusions
- `requirements.txt` - Python dependencies
- `.env` - API keys (gitignored)

---

## ✅ Pre-Commit Checklist

- [ ] All tests pass (`./start_udos.sh sandbox/tests/shakedown.uscript`)
- [ ] No syntax errors (`python -m py_compile core/*.py`)
- [ ] Updated relevant documentation (README.MD, dev/docs/, wiki/)
- [ ] Updated ROADMAP.MD if completing major milestone
- [ ] Verified file paths are correct
- [ ] Cleaned up debug code/comments
- [ ] Tested in clean environment
- [ ] File operations work with UNDO/REDO
- [ ] Web dashboard shows correct status (DASH WEB)
- [ ] No hardcoded values that should be in settings/lexicon
- [ ] Moved any .backup files to `history/backups/`

---

## 🆘 Troubleshooting

### Import Errors
- Check virtual environment is activated
- Verify `requirements.txt` dependencies installed
- Check Python path in VS Code settings

### File Not Found
- Use absolute paths or paths relative to project root
- Check file is in expected location per this guide
- Use `TREE` command to verify structure
  - `TREE` - Full repository tree
  - `TREE --depth=2` - Limit depth to 2 levels
  - `TREE SANDBOX` - Sandbox folder only
  - `TREE MEMORY` - Memory folder only
  - `TREE KNOWLEDGE` - Knowledge folder only
  - `TREE HISTORY` - History folder only
  - `TREE CORE` - Core modules only
  - `TREE WIKI` - Wiki pages only
  - `TREE EXTENSIONS` - Extensions only
  - `TREE EXAMPLES` - Examples only

### Config Not Loading
- Verify file is in `data/` directory
- Check JSON syntax is valid
- Look for typos in filename

### Server Won't Start
- Check port isn't already in use
- Verify extension is installed
- Check logs in `sandbox/logs/`

---

**Questions?** Check the [FAQ](https://github.com/fredporter/uDOS/wiki/FAQ) or [Contributing Guide](https://github.com/fredporter/uDOS/wiki/Contributing)
