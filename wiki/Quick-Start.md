# Quick Start Guide

Get uDOS running in **5 minutes**! ⚡

---

## Prerequisites

- **Python 3.9+** installed
- **macOS, Linux, or Windows** (with WSL recommended)
- **Terminal** with 256-color support
- **Git** (for cloning the repository)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
```

---

## Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages**:
- `google-generativeai` - Gemini API integration
- `python-dotenv` - Environment variable management
- `prompt_toolkit` - Interactive shell features

---

## Step 4: Configure (Optional)

### Add Gemini API Key (for AI features)

Create a `.env` file:

```bash
echo 'GEMINI_API_KEY=your_key_here' > .env
```

**Note**: uDOS works fully without an API key! It automatically falls back to offline mode.

[Get a free Gemini API key →](https://makersuite.google.com/app/apikey)

---

## Step 5: Launch uDOS

```bash
./start_udos.sh
```

**First Run**: You'll be guided through an interactive setup:
1. Enter your name
2. Choose a project name
3. Select a theme (DUNGEON_CRAWLER, CYBERPUNK, or MINIMAL)

This creates your `data/STORY.UDO` profile.

---

## Step 6: Try Your First Commands

### List Files
```
🔮 > LIST
```

### Load a File
```
🔮 > LOAD README.MD
```

### Show Grid
```
🔮 > SHOW GRID main
```

### Check System Status
```
🔮 > STATUS
```

### View Current Map
```
🔮 > MAP
```

### Get Help
```
🔮 > HELP
```
```
🔮 > ASK "What is uDOS?"
```

### Get Help
```
🔮 > HELP
```

---

## Interactive Features

### Smart Tab Completion
Press **Tab** to see available commands:
```
🔮 > CA[Tab]
  CATALOG  # Lists files
```

### File Path Completion
Type `LOAD "` then press **Tab** to browse files:
```
🔮 > LOAD "[Tab]
  README.MD
  ROADMAP.MD
  data/COMMANDS.UDO
```

### Command History
Use **↑** and **↓** to navigate previous commands.

### Context Hints
After commands, uDOS suggests next steps:
```
✅ File loaded into 'main'
💡 Try: SHOW "main"
```

---

## Running Scripts

Execute a test script:

```bash
./start_udos.sh shakedown.uscript
```

Or from within uDOS:
```
```
🔮 > RUN "knowledge/demos/simple-setup.uscript"
```

---

## CLI Features v1.0.6+ ⚡

### Enhanced Command History
```bash
🔮 > HISTORY LIST              # Show recent commands
🔮 > HISTORY SEARCH file       # Search command history
🔮 > HISTORY STATS             # Usage statistics
```

### Dynamic Themes
```bash
🔮 > THEME LIST                # Available themes
🔮 > THEME SET cyberpunk       # Switch to cyberpunk theme
🔮 > THEME ACCESSIBILITY ON    # Enable high contrast
```

### Session Management
```bash
🔮 > SESSION SAVE work         # Save current workspace
🔮 > SESSION LIST              # Show all sessions
🔮 > SESSION LOAD 1            # Restore previous session
```

### Progress Indicators
Long operations now show real-time progress:
```bash
🔮 > FILE SEARCH *.py
⏳ Searching files... ████████████████████ 100% (23/23) [1.2s]
```

### Responsive Layouts
Automatically adapts to your terminal size:
```bash
🔮 > LAYOUT MODE compact       # Mobile-friendly
🔮 > LAYOUT MODE expanded      # Wide screen
🔮 > LAYOUT AUTO ON            # Auto-adapt
```

### Smart Tab Completion v2.0
- **Fuzzy matching**: Type `THM<Tab>` → `THEME`
- **Context-aware**: Smart parameter suggestions
- **History integration**: Recent commands prioritized

[Full CLI Features Documentation →](CLI-Features-v1-0-6)

---

## Troubleshooting
```

---

## Check System Status

View your configuration:

```
🔮 > STATUS
```

Output shows:
- **Connection mode** (ONLINE/OFFLINE/LIMITED)
- **Viewport** (terminal dimensions)
- **Device type** (DESKTOP/TABLET/MOBILE)
- **User profile** info
- **System health** checks

---

## Test the Viewport

See color palette and terminal capabilities:

```
🔮 > PALETTE
```

Or trigger during reboot:

```
🔮 > REBOOT
```

---

## Explore the Map System

Navigate the multi-layer grid:

```
🔮 > MAP STATUS
🔮 > MOVE 5 3
🔮 > LAYER
🔮 > DESCEND
```

[Learn more about mapping →](Mapping-System)

---

## Next Steps

### Beginner Path
1. ✅ Quick Start (you are here!)
2. 📝 [Command Reference](Command-Reference) - Learn all commands
3. 📋 [Panels Tutorial](Panels-Tutorial) - Multi-buffer workflows
4. 🤖 [AI Integration](AI-Integration) - Work with Gemini
5. 📜 [Your First Script](Your-First-Script) - Automation basics

### Learn Core Concepts
- [Architecture](Architecture) - How uDOS works
- [uCODE Language](uCODE-Language) - Internal command format
- [Grid System](Grid-System) - Panel management

### Customize Your Experience
- [Theming](Theming) - Change the look and feel
- [Configuration](Configuration) - Advanced settings
- [Color Palette](Color-Palette) - Customize colors

---

## Troubleshooting

### Python Version Issues
```bash
# Check your Python version
python3 --version

# Must be 3.9 or higher
```

### Missing Dependencies
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### API Key Not Working
```bash
# Verify .env file exists
cat .env

# Should show: GEMINI_API_KEY='your_key'
```

**Remember**: uDOS works offline without an API key!

### Permission Denied on start_udos.sh
```bash
chmod +x start_udos.sh
```

### Virtual Environment Not Activating
```bash
# macOS/Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

---

## Getting Help

- 📖 [Full Documentation](Home) - Complete wiki
- 💬 [Discussions](https://github.com/fredporter/uDOS/discussions) - Ask questions
- 🐛 [Issues](https://github.com/fredporter/uDOS/issues) - Report bugs
- 📋 [FAQ](FAQ) - Common questions

---

## System Requirements

| Component | Minimum | Recommended |
|:----------|:--------|:------------|
| **Python** | 3.9 | 3.11+ |
| **RAM** | 512 MB | 1 GB |
| **Storage** | 50 MB | 100 MB |
| **Terminal** | 80×24 | 120×40 |
| **Colors** | 16-color | 256-color |

---

**Congratulations! You're running uDOS.** 🎉

Explore the [Command Reference](Command-Reference) or try the [Tutorials](Tutorials) next!

🔮 *Your journey begins...*
