# Quick Reference

**uDOS v1.4.0** - Essential Commands and Development Guide

> **💡 Pro Tip**: Press `TAB` for autocomplete. Use `HELP <command>` for detailed help.

---

## 🚀 Current Status

- **Version**: v1.4.0 (Community Beta Preparation)
- **Progress**: 88% Complete (Phase 5 of 5)
- **Latest**: Comprehensive documentation suite with ASCII diagrams
- **Next**: Community infrastructure, beta release

---

## Essential Commands

### Getting Help
```bash
HELP                      # Show all commands
HELP <command>            # Detailed command help
STATUS                    # System status
VERSION                   # Show version info
```

### File Operations
```bash
LIST [path]               # List directory contents
LOAD <file>               # Load file into memory
SAVE <file>               # Save current content
EDIT <file>               # Edit file in micro editor
```

### Content Generation (OK Assist)
```bash
OK <task>                 # Generate content with AI
OK ASK <question>         # Ask AI assistant
GENERATE guide <topic>    # Generate survival guide
GENERATE diagram <topic>  # Generate SVG diagram
REFRESH                   # Update content to latest standards
```

### Knowledge Bank
```bash
MEMORY                    # Access personal knowledge
PRIVATE                   # Private notes/content
SHARED                    # Shared knowledge base
COMMUNITY                 # Community contributions
KB <topic>                # Quick knowledge lookup
```

### Grid & Panels
```bash
GRID                      # Show grid system
NEW GRID <name>           # Create new grid
PANEL <name>              # Access panel
TILE <coords>             # Geographic tile data
```

### Navigation
```bash
MAP                       # Show current position
GOTO <location>           # Navigate to location
MOVE <direction>          # Move in direction
LEVEL                     # Show current level
```

### System
```bash
REBOOT                    # Restart uDOS
CLEAR                     # Clear screen
SETUP                     # Run first-time setup
REPAIR                    # Run diagnostics
CONFIG                    # View/edit configuration
```

### Automation (uCODE)
```bash
RUN <script.uscript>      # Execute uCODE script
DEBUG <script>            # Debug uCODE script
```

---

## Command Reference by Category

### 📁 File Operations
| Command | Description | Example |
|---------|-------------|---------|
| `LIST` | List directory contents | `LIST knowledge/water/` |
| `LOAD` | Load file into memory | `LOAD README.MD` |
| `SAVE` | Save current content | `SAVE output.txt` |
| `EDIT` | Edit file with micro | `EDIT config.json` |

### 🤖 OK Assist (AI)
| Command | Description | Example |
|---------|-------------|---------|
| `OK` | General AI task | `OK create water purification guide` |
| `OK ASK` | Ask AI question | `OK ASK how to start fire without matches` |
| `OK DEV` | Development assistance | `OK DEV explain this code` |
| `READ` | Read content for context | `READ water-guide.md` |

### 📚 Knowledge Bank
| Command | Description | Example |
|---------|-------------|---------|
| `MEMORY` | Personal knowledge | `MEMORY list` |
| `PRIVATE` | Private content | `PRIVATE add note` |
| `SHARED` | Shared knowledge | `SHARED search water` |
| `COMMUNITY` | Community content | `COMMUNITY latest` |
| `KB` | Quick lookup | `KB water purification` |

### 🎨 Content Generation
| Command | Description | Example |
|---------|-------------|---------|
| `GENERATE` | Create content | `GENERATE guide water/purification` |
| `CONVERT` | Format conversion | `CONVERT pdf-to-md manual.pdf` |
| `REFRESH` | Update content | `REFRESH --check all` |
| `BATCH` | Batch operations | `BATCH category=water type=guide` |

### 🗺️ Navigation
| Command | Description | Example |
|---------|-------------|---------|
| `MAP` | Show map | `MAP` |
| `GOTO` | Navigate to | `GOTO 10,5` |
| `MOVE` | Move direction | `MOVE north` |
| `LEVEL` | Current level | `LEVEL` |
| `GOUP` | Ascend level | `GOUP` |
| `GODOWN` | Descend level | `GODOWN` |

### 🔧 System
| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | System status | `STATUS` |
| `REBOOT` | Restart system | `REBOOT` |
| `REPAIR` | Diagnostics | `REPAIR MODE 1` |
| `CONFIG` | Configuration | `CONFIG theme teletext-green` |
| `VIEWPORT` | Display settings | `VIEWPORT` |

### 🐛 Debugging
| Command | Description | Example |
|---------|-------------|---------|
| `DEBUG` | Start debugger | `DEBUG script.uscript` |
| `BREAK` | Set breakpoint | `BREAK 10` |
| `STEP` | Step through | `STEP` |
| `CONTINUE` | Continue execution | `CONTINUE` |
| `INSPECT` | Inspect variable | `INSPECT $count` |
| `WATCH` | Watch expression | `WATCH $total > 100` |

---

## uCODE Script Quick Reference

### Basic Syntax
```uscript
# Comment
[COMMAND|parameter|option]
$variable = "value"
```

### Common Patterns
```uscript
# Generate content
[GENERATE|guide|water/purification]
[GENERATE|diagram|fire/triangle|format=svg]

# Variables
$category = "water"
$topic = "purification"
[GENERATE|guide|$category/$topic]

# Conditionals
if [SEARCH|quality<0.8] then
  [REFRESH|--force]
fi

# Loops
for cat in water,fire,shelter
  [GENERATE|guide|$cat/basics]
done

# Command chaining
[SEARCH|category=water] |> [REFRESH|--check] |> [REPORT]
```

### Example Script
```uscript
---
title: Daily Maintenance
version: 1.0.0
---

# Check quality
[REFRESH|--check|all]

# Update if needed
if quality < 0.8 then
  [REFRESH|all]
  [NOTIFY|Content updated]
fi

# Rebuild indexes
[MANAGE|index|rebuild]
```

---

## Development Quick Start

### Setup Environment
```bash
# Clone repository
git clone https://github.com/fredporter/uDOS.git
cd uDOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch uDOS
./start_udos.sh
```

### Configure OK Assist (Optional)
```bash
# Create .env file
echo 'GEMINI_API_KEY=your_key_here' > .env

# Or set via command
CONFIG SET GEMINI_API_KEY your_key_here
```

### Run Tests
```bash
# All tests
pytest memory/tests/

# Specific version
pytest memory/tests/test_v1_0_*.py

# With coverage
pytest --cov=core --cov-report=html
```

### Generate Content
```bash
# Generate guides with OK Assist
python dev/tools/generate_content_v1_4_0.py --category water --count 5

# Generate diagrams
python dev/tools/generate_svg_diagram.py "water filter" water

# Batch generation
python dev/tools/generate_content_v1_4_0.py --all --guides-only
```

---

## File Locations

### Core System
```
core/                     # Core uDOS system
├── commands/            # Command handlers
├── services/            # Business logic
├── ucode/              # uCODE language
├── utils/              # Utilities
└── config.py           # Configuration

extensions/             # Optional extensions
├── core/ok-assist/     # AI assistant
└── templates/          # Extension templates
```

### User Data
```
memory/                 # User workspace
├── personal/          # Personal content
├── private/           # Private notes
├── shared/            # Shared knowledge
├── logs/              # System logs
└── config/            # User config

knowledge/             # Knowledge base
├── water/            # Water category
├── fire/             # Fire category
├── shelter/          # Shelter category
├── food/             # Food category
├── medical/          # Medical category
├── navigation/       # Navigation category
├── tools/            # Tools category
└── communication/    # Communication category
```

### Documentation
```
wiki/                   # Complete documentation
├── Quick-Reference.md         # This file
├── Tutorial-Getting-Started.md # Interactive tutorial
├── API-Reference.md           # Developer API
├── Architecture-Contributor-Guide.md # Architecture
├── Command-Reference.md       # All commands
├── uCODE-Language.md         # uCODE spec
├── Troubleshooting-Complete.md # Error solutions
└── Theme-System.md            # Themes guide
```

---

## Version History

### v1.4.0 (Current - 88% Complete)
- ✅ Phase 1: Knowledge Infrastructure
- ✅ Phase 2: Content Organization
- ✅ Phase 3: Design Standards
- ✅ Phase 4: uCODE Language Refinement
- 🔄 Phase 5: Community Beta (70% - Documentation complete)

### v1.3.0
- Extension marketplace
- Community features
- Enhanced OK Assist

### v1.2.0
- Multi-format diagram generation
- Content refresh system
- Knowledge bank improvements

### v1.1.0
- OK Assist integration
- uCODE language
- Theme system

### v1.0.x Series
- Core commands
- Grid system
- Navigation
- Debugging tools

---

## Performance Metrics

### v1.0.26 Benchmarks
```
Command P90:     1.70ms  (97% faster than target)
Command P99:     5.43ms  (95% faster than target)
Startup time:    38ms    (92% faster than target)
Memory usage:    <20MB   (80% better than target)
```

### Test Coverage
```
Total tests:     1022    (102% of target)
Passing:         92.4%   (365/395)
Categories:      12      (all core systems)
```

---

## Configuration Options

### Theme Selection
```bash
# Available themes
CONFIG theme default              # Standard theme
CONFIG theme teletext-green       # Teletext style
CONFIG theme dungeon             # RPG dungeon
CONFIG theme cyberpunk           # Cyberpunk aesthetic
```

### AI Model Selection
```bash
# Gemini models
CONFIG ai-model gemini-2.0-flash-exp     # Latest (recommended)
CONFIG ai-model gemini-1.5-flash         # Stable
CONFIG ai-model gemini-1.5-pro           # Advanced
```

### Output Settings
```bash
CONFIG output-dir knowledge/custom/      # Custom output
CONFIG format svg                        # Default diagram format
CONFIG quality 0.8                       # Quality threshold
```

---

## Troubleshooting

### Common Issues

**Command not found:**
```bash
HELP                    # Check available commands
STATUS                  # Verify system status
REPAIR MODE 1           # Run diagnostics
```

**API key errors:**
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Set via command
CONFIG SET GEMINI_API_KEY your_key_here

# Verify
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Performance issues:**
```bash
CLEAR                   # Clear screen/cache
REBOOT                  # Restart system
REPAIR MODE 2           # Deep diagnostics
```

**See full guide:** [Troubleshooting-Complete.md](Troubleshooting-Complete.md)

---

## Links

### Documentation
- [Tutorial (Getting Started)](Tutorial-Getting-Started.md)
- [Command Reference (Complete)](Command-Reference.md)
- [API Reference (Developers)](API-Reference.md)
- [Architecture Guide (Contributors)](Architecture-Contributor-Guide.md)
- [uCODE Language Spec](uCODE-Language.md)
- [Theme System Guide](Theme-System.md)
- [Troubleshooting Guide](Troubleshooting-Complete.md)

### Development
- [Contributing Guidelines](Contributing.md)
- [Project Organization](Project-Organization.md)
- [Development History](Development-History.md)
- [Latest Development](Latest-Development.md)

### Project
- [Home](Home.md)
- [Why uDOS?](Why-uDOS.md)
- [Philosophy](Philosophy.md)
- [FAQ](FAQ.md)

---

**Last Updated**: November 25, 2025
**Version**: v1.4.0 (Phase 5 - Community Beta)
**Status**: Documentation Complete ✅
**Next**: Community Infrastructure Setup
