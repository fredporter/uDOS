# uDOS Demos & Examples

Interactive demonstrations and example scripts showcasing uDOS features.

---

## 📜 Example Scripts

### Getting Started

#### `hello-automation.uscript`
Basic automation script demonstrating simple command execution.

**Run**:
```bash
./start_udos.sh knowledge/demos/hello-automation.uscript
```

#### `simple-setup.uscript`
Quick setup example for new users.

---

### Advanced Features

#### `advanced_features.uscript`
Demonstrates v1.0.16 capabilities:
- Functions and return values
- Error handling with TRY/CATCH
- Calculations and logic
- Control flow

#### `task_manager.uscript`
Complete task management application showing:
- Task creation and validation
- List management
- Priority systems
- Real-world application structure

#### `library_example.uscript`
Module imports and code reuse patterns.

#### `panel_demo.uscript`
PANEL system demonstration (v1.0.21 teletext graphics).

---

## 🎮 Interactive Demos

### `option_selector_demo.py`
Interactive demonstration of arrow-key navigation for option selection (v1.0.19).

**Features**:
- Theme selector
- Command selector
- Map cell selector (100 cells: A1-J10)
- Custom single-select
- Custom multi-select (spacebar to toggle)
- Enhanced file picker

**Run**:
```bash
source .venv/bin/activate
python knowledge/demos/option_selector_demo.py
```

---

## 🗺️ Asset Bundles

### `teletext_clone_bundle_with_blocks/`
Complete teletext graphics bundle with block characters for retro-style displays.

**Contents**:
- Block character sets
- Teletext graphics assets
- Rendering examples

### `udos_map_480x270_cellkey/`
Reference map assets for geographic data visualization.

**Contents**:
- Map cell coordinates
- Geographic reference data
- 480×270 cell grid examples

---

## 🚀 Running Examples

### Interactive Mode
```bash
# Start uDOS
./start_udos.sh

# Load and run script
🔮 > RUN knowledge/demos/hello-automation.uscript
```

### Direct Execution
```bash
# Run script directly
./start_udos.sh knowledge/demos/task_manager.uscript
```

### Python Demos
```bash
# Activate virtual environment
source .venv/bin/activate

# Run interactive demo
python knowledge/demos/option_selector_demo.py
```

---

## 📚 Learn More

- **[Getting Started](../../wiki/Getting-Started.md)** - Complete beginner guide
- **[Command Reference](../../wiki/Command-Reference.md)** - All available commands
- **[PANEL Commands](../../wiki/PANEL-Commands.md)** - Teletext graphics system
- **[KNOWLEDGE Commands](../../wiki/KNOWLEDGE-Commands.md)** - Knowledge bank system
- **[uScript Language](../../wiki/uScript-Language.md)** - Scripting documentation

---

## 🎯 Example Categories

| Category | Files | Features Demonstrated |
|:---------|:------|:----------------------|
| **Basics** | `hello-automation`, `simple-setup` | Command execution, system status |
| **Advanced** | `advanced_features`, `task_manager`, `library_example` | Functions, error handling, modules |
| **Graphics** | `panel_demo` | PANEL system, teletext graphics |
| **Interactive** | `option_selector_demo.py` | Arrow-key navigation, user input |
| **Assets** | `teletext_*`, `udos_map_*` | Graphics bundles, map data |

---

*Demos are part of the uDOS knowledge base and distributed with the system.*
