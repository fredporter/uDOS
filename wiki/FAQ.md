# Frequently Asked Questions

Common questions about uDOS

---

## General Questions

### What is uDOS?

uDOS is an **educational CLI framework** that demonstrates how to build a modular, human-readable command system while integrating AI capabilities. It's designed for:
- Learning CLI development
- Understanding AI integration
- Building custom command-line tools
- Teaching systems programming concepts

### Is uDOS production-ready?

uDOS v1.0.0 is **educational software** with production-quality architecture. It's:
- ✅ Fully functional and tested
- ✅ Well-documented and maintainable
- ✅ Feature-complete for core operations
- ⚠️ Best suited for learning and experimentation

### Do I need an API key to use uDOS?

**No!** uDOS works fully without an API key. It has two modes:
- **ONLINE**: Uses Gemini API for AI features (requires key)
- **OFFLINE**: Uses built-in logic engine (no key needed)

The system automatically detects connectivity and switches modes.

---

## Installation & Setup

### What are the system requirements?

**Minimum**:
- Python 3.9+
- 80×24 terminal
- 512 MB RAM
- 50 MB disk space

**Recommended**:
- Python 3.11+
- 120×40 terminal (256-color)
- 1 GB RAM
- 100 MB disk space

### How do I install uDOS?

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./start_udos.sh
```

[Full installation guide →](Quick-Start)

### Why won't my terminal run the start script?

Make it executable:
```bash
chmod +x start_udos.sh
```

Or run directly:
```bash
source .venv/bin/activate && python3 uDOS_main.py
```

### Where do I get a Gemini API key?

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get a free API key.

Add to `.env` file:
```
GEMINI_API_KEY='your_key_here'
```

---

## Features & Usage

### What's the difference between a command and uCODE?

- **Command**: User-facing syntax (`LOAD "file.txt"`)
- **uCODE**: Internal structured format (`[FILE|LOAD*file.txt*main]`)

Users type commands, uDOS translates to uCODE for execution.

[Learn more about uCODE →](uCODE-Language)

### What are panels?

Panels are **named text buffers** for organizing data. Think of them like:
- Tabs in a text editor
- Clipboard slots
- Named variables for text

```
🔮 > GRID PANEL CREATE "notes"
🔮 > LOAD "file1.txt" TO "notes"
🔮 > LOAD "file2.txt" TO "main"
🔮 > SHOW "notes"
```

[Panels tutorial →](Panels-Tutorial)

### How does the mapping system work?

uDOS has an 8-layer navigation system inspired by NetHack:

```
SATELLITE  (+100)  ← Space
CLOUD      (+50)   ← Aerial
SURFACE    (0)     ← Ground (default)
DUNGEON-1  (-10)   ← Underground
...
CORE       (-100)  ← Bottom
```

Navigate with `MOVE`, `DESCEND`, `ASCEND`, `GOTO`.

[Full mapping guide →](Mapping-System)

### Can I customize the colors?

Yes! The Polaroid color palette is defined in `data/PALETTE.UDO`.

View with:
```
🔮 > PALETTE
```

[Color customization guide →](Color-Palette)

### What themes are available?

Built-in themes:
- **DUNGEON_CRAWLER** - Fantasy RPG style
- **CYBERPUNK** - Neon tech aesthetic
- **MINIMAL** - Clean, simple style

Set in `data/STORY.UDO` or during setup.

[Theming guide →](Theming)

---

## Scripting & Automation

### What is a .uscript file?

A **uCODE script** file containing commands for automation:

```uscript
# example.uscript
[FILE|LOAD*README.MD*main]
[GRID|SHOW*main]
[AI|ASK*Summarize this file*main]
```

Run with:
```
🔮 > RUN "example.uscript"
```

[Script automation guide →](Script-Automation)

### Can I write scripts in regular commands?

Yes! Scripts support both uCODE and regular commands:

```uscript
LOAD "file1.txt" TO "a"
LOAD "file2.txt" TO "b"
ASK "Compare these files" FROM "a"
```

### How do I automate setup?

The `data/SETUP.USC` file uses **uCODE with conditionals**:

```uscript
IF USER.NAME IS_EMPTY THEN
  PROMPT "Enter your name" INTO USER.NAME
ENDIF
```

[uCODE scripting reference →](uCODE-Language)

---

## Development

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

[Contributing guide →](Contributing)

### Can I build extensions?

Yes! uDOS has an extension system:

1. Create `extensions/my_extension.py`
2. Define commands and handlers
3. Register in `uDOS_commands.py`

[Extension development →](Extensions)

### Where's the documentation?

- **Wiki**: Comprehensive guides (you're here!)
- **Code Comments**: Inline documentation
- **ROADMAP.MD**: Project direction
- **[Style Guide](Style-Guide)**: Design principles & conventions

### How do I report bugs?

[Open an issue](https://github.com/fredporter/uDOS/issues) with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Session log (`sandbox/logs/session_*.log`)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Permission denied" errors

Activate virtual environment:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Commands not working

1. Check spelling (case-insensitive)
2. Use quotes for paths: `LOAD "file.txt"`
3. Try `HELP <command>` for syntax
4. Check session log for errors

### AI not responding

- Check internet connection (`STATUS`)
- Verify API key in `.env`
- System auto-falls back to offline mode
- Try `ANALYZE` instead of `ASK`

### Colors not showing

- Terminal may not support 256-color mode
- Check `TERM` environment variable
- Run `PALETTE` to test colors
- uDOS works in monochrome too!

### Viewport detection wrong

Run `REBOOT` to re-detect terminal size:
```
🔮 > REBOOT
```

[Full troubleshooting guide →](Troubleshooting)

---

## Concepts

### What's the "clever flat architecture"?

All core modules are in the root directory (`uDOS_*.py`), not nested in folders. This makes:
- Code easy to find
- Import paths simple
- Learning more direct

### Why the retro aesthetic?

uDOS embraces **8-bit nostalgia** and **terminal culture**:
- ASCII art
- Emoji prompts
- Fantasy/RPG themes
- Command-line purism

It's both educational and fun!

### What's the "human-readable" philosophy?

Commands should read like natural language:

```
LOAD "README.MD" TO "docs"
ASK "What is this file about?" FROM "docs"
SAVE "notes" TO "output.txt"
```

Not:
```
ld -f README.MD -p docs
ai -q "What is this?" -c docs
sv -p notes -o output.txt
```

---

## Compatibility

### Does it work on Windows?

Yes, with some caveats:
- ✅ Works in WSL (Windows Subsystem for Linux)
- ✅ Works in Git Bash
- ⚠️ Limited in PowerShell (color support)
- ⚠️ Limited in CMD (no ANSI colors)

**Recommended**: Use WSL or Git Bash

### Does it work on Linux?

✅ Yes! Works great on all major distributions.

### Does it work on macOS?

✅ Yes! Developed primarily on macOS.

### What about Raspberry Pi?

✅ Yes! Python 3.9+ is available on Raspberry Pi OS.

---

## Performance

### Is uDOS slow?

No! Operations are fast:
- Command parsing: <1ms
- File loading: Limited by disk I/O
- AI queries: Limited by network/API
- Grid operations: Nearly instantaneous

### How much memory does it use?

- Base system: ~10 MB
- Plus content in panels
- Plus session logs

Typical usage: 20-50 MB total

### Can it handle large files?

Yes, but:
- Files load entirely into memory (panels)
- Large files (>100MB) may cause slowness
- Consider loading sections instead

---

## Future Plans

### What's on the roadmap?

**Q4 2025**:
- Plugin system
- Advanced theming
- Network integration
- Enhanced mapping

[Full roadmap →](Roadmap)

### Will there be a GUI?

Not planned. uDOS is **terminal-first** by design. However:
- Extensions could add GUI features
- Terminal UI improvements planned
- Focus remains on CLI experience

### Can I use uDOS in my project?

Yes! uDOS is open source. Check the LICENSE file for terms.

---

## Community

### How do I get help?

1. Check this FAQ
2. Read the [wiki](Home)
3. Search [issues](https://github.com/fredporter/uDOS/issues)
4. Ask in [discussions](https://github.com/fredporter/uDOS/discussions)
5. Open a new issue

### Can I share my extensions?

Absolutely! Share via:
- Pull requests
- Gists
- Discussions
- Your own forks

### How do I stay updated?

- Watch the repository
- Follow discussions
- Check [changelog](Changelog)
- Read commit messages

---

## Still Have Questions?

- 💬 [Ask in Discussions](https://github.com/fredporter/uDOS/discussions)
- 🐛 [Report an Issue](https://github.com/fredporter/uDOS/issues)
- 📖 [Read the Wiki](Home)
- 📧 Contact maintainers

---

*Your question not answered? [Open a discussion](https://github.com/fredporter/uDOS/discussions) and we'll add it!* 🔮
