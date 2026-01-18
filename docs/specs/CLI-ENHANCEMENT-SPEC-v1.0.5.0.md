# Wizard/Goblin CLI Enhancement Specification

**Phase:** v1.0.5.0 (Post-Alpha)  
**Date:** 2026-01-16  
**Status:** Specification Phase

---

## Overview

This specification outlines the planned enhancements to the Wizard/Goblin command-line interface:

1. **Persistent Status Bar** - Service health + task scheduler state
2. **Educational Startup Splash** - Terminal capabilities + dependency check
3. **Enhanced Installers** - Better error messages and dependency feedback
4. **Command Registry Service** - Central schema for all interfaces

---

## 1. Persistent Status Bar

### Purpose

Display a persistent footer showing:

- Running services and their health status
- Task scheduler state (Plant/Sprout/Prune/etc)
- Progressive achievement verbiage (uDOS-themed)
- Current time and next scheduled event

### Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🌀 uDOS (v1.0.2.0) | Wizard (8765) ✓ | Goblin (8767) ✓ | Frontend (5173) ✓ │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tasks: Plant(0) | Sprout(1) | Prune(2) | Trellis(5) | Harvest(0) | Compost(0)
│                                                                              │
│ 🌀  [Waiting for your command...]                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Components

#### 1.1 Service Health Display

```python
# dev/goblin/core/ui/status_bar.py

class StatusBar:
    def __init__(self, theme: str = "dungeon"):
        self.services = {}  # {name: ServiceStatus}
        self.scheduler = {}  # {stage: count}
        self.theme = StatusThemes[theme]

    def render_header(self) -> str:
        """Render top status line with services."""
        # Format: 🌀 uDOS (v1.0.2.0) | Service1 (port) ✓ | Service2 ✓

    def render_scheduler(self) -> str:
        """Render task scheduler stages."""
        # Format: Plant(0) | Sprout(2) | Prune(1) | ... | Compost(5)

    def render_achievement(self) -> str:
        """Render progressive achievement message."""
        # Example: "🌀 Coils spinning, 3 research tasks trellis-ready..."
```

#### 1.2 Service Status Structure

```python
@dataclass
class ServiceStatus:
    name: str              # "Wizard", "Goblin", "Frontend"
    port: int              # 8765, 8767, 5173
    status: str            # "running", "idle", "error", "offline"
    version: str           # "v1.1.0.0"
    message: str           # "Processing 2 tasks"
    last_check: datetime   # Timestamp of last health check
    color: str             # Theme-specific color
```

#### 1.3 Service Monitoring

Services report status via API:

```python
# GET /api/v1/health (Wizard)
{
    "status": "healthy",
    "timestamp": "2026-01-16T14:32:00Z",
    "services": {
        "wizard": {"status": "running", "uptime": 3600},
        "goblin": {"status": "running", "uptime": 1800},
        "frontend": {"status": "running", "uptime": 1200}
    },
    "scheduler": {
        "plant": 0,
        "sprout": 1,
        "prune": 2,
        "trellis": 5,
        "harvest": 0,
        "compost": 3
    }
}
```

#### 1.4 Theme Support

Three themes with different color schemes:

```python
# dev/goblin/core/ui/status_themes.py

class StatusThemes:
    DUNGEON = {
        "service_running": "bright_magenta",
        "service_idle": "bright_yellow",
        "service_error": "bright_red",
        "achievement": "bright_cyan",
        "separator": "magenta",
        "background": "black",
    }

    ELECTRIC = {
        "service_running": "bright_green",
        "service_idle": "bright_yellow",
        "service_error": "bright_red",
        "achievement": "bright_cyan",
        "separator": "bright_green",
        "background": "black",
    }

    MINIMAL = {
        # ASCII only, no colors
        "service_running": "✓",
        "service_idle": "○",
        "service_error": "✗",
        "achievement": ">>",
    }
```

#### 1.5 Progressive Achievement Verbiage

Based on system state, display themed messages:

```python
class AchievementVerbiage:
    """
    Generate uDOS-themed progress messages.

    Themes: "dungeon", "electric", "hacker"
    States: "startup", "running", "working", "milestone", "completing", "idle"
    """

    DUNGEON_MESSAGES = {
        "startup": [
            "Just fired up the first reactor...",
            "Coils warming, ancient circuits stirring...",
            "The crystal caverns awaken...",
        ],
        "running": [
            "Coils spinning, systems aligned...",
            "Deep in the dungeons, all is well...",
            "Crystal resonance stable...",
        ],
        "working": [
            "Delving deeper into the data...",
            "Artifacts being processed...",
            "The forge works overtime...",
        ],
        "milestone": [
            "A breakthrough in the depths!",
            "The ancient machine hums with purpose...",
            "Progress echoes through the caverns...",
        ],
        "completing": [
            "Finishing the grand opus...",
            "The final seal is nearly closed...",
            "Emergence from the depths imminent...",
        ],
    }

    ELECTRIC_MESSAGES = {
        "startup": [
            "Firing up the first core...",
            "Neural pathways connecting...",
            "Quantum state stabilizing...",
        ],
        "running": [
            "Processors humming at peak efficiency...",
            "Neural net in sync...",
            "Energy flows like lightning...",
        ],
        # ... more themes
    }
```

### Implementation Plan

**File Structure:**

```
dev/goblin/core/ui/
├── status_bar.py        (StatusBar class)
├── status_themes.py     (Theme definitions)
└── achievement.py       (Verbiage generator)

wizard/services/
├── status_service.py    (Service health monitor)
└── command_registry.py  (Central command registry)
```

**Integration:**

1. Wizard Server health endpoint (`/api/v1/health`)
2. Goblin frontend subscribes to WebSocket updates
3. CLI footer updates every 500ms via callback
4. Themes loaded from config

---

## 2. Educational Startup Splash

### Purpose

Display comprehensive system information and readiness check during startup:

1. Terminal capability detection
2. Viewport dimensions validation
3. Dependency installation progress
4. Step-by-step initialization feedback

### Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║                       🌀 uDOS Startup                                ║  │
│  ║                    Alpha v1.0.2.0 (Dungeon)                          ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                             │
│  Terminal Capabilities                                                     │
│  ──────────────────────────────────────────────────────────────────────── │
│                                                                             │
│    Colors Available:                                                        │
│      • 256 colors        ✓ (Full RGB support)                              │
│      • Unicode           ✓ (Box drawing, symbols)                          │
│      • Attributes        ✓ (Bold, italic, underline)                       │
│                                                                             │
│    Terminal Features:                                                       │
│      • Mouse support     ✓                                                  │
│      • Alt screen        ✓ (Full-screen capability)                         │
│      • True color        ✓ (24-bit RGB)                                     │
│                                                                             │
│  Viewport Dimensions                                                        │
│  ──────────────────────────────────────────────────────────────────────── │
│                                                                             │
│    Detected:                                                                │
│      Width:   120 characters  (recommended ≥80)   ✓                         │
│      Height:  35 lines        (recommended ≥24)   ✓                         │
│                                                                             │
│  System Initialization                                                      │
│  ──────────────────────────────────────────────────────────────────────── │
│                                                                             │
│    ✓ Checking Python version (3.11.0)                                      │
│    ✓ Loading command schemas (234 commands)                                │
│    ✓ Verifying virtual environment                                         │
│    ✓ Initializing logging system                                           │
│    ✓ Starting Wizard Server (8765)                                         │
│    ✓ Starting Goblin Server (8767)                                         │
│    ⟳ Connecting to Notion workspace...                                     │
│                                                                             │
│    Status: 6/8 systems ready [████████░░░░░░░░░░░░░░] 75%                 │
│                                                                             │
│  Dependency Report                                                          │
│  ──────────────────────────────────────────────────────────────────────── │
│                                                                             │
│    ✓ core.commands.shakedown_handler                                       │
│    ✓ core.services.logging_manager                                         │
│    ✓ dev.goblin.core.input.smart_prompt                                    │
│    ✓ extensions.api.server                                                 │
│    ✗ wizard.services.notion_sync_service (offline mode)                    │
│    ⟳ prompt-toolkit (installing from requirements.txt...)                  │
│                                                                             │
│  Next Steps                                                                 │
│  ──────────────────────────────────────────────────────────────────────── │
│                                                                             │
│    • Type HELP for command reference                                       │
│    • Type STATUS to check service health                                   │
│    • Type SHAKEDOWN to run system tests                                    │
│                                                                             │
│    Press ENTER to continue...                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Components

#### 2.1 Terminal Capability Detection

```python
# core/services/terminal_capabilities.py

class TerminalCapabilities:
    """Detect terminal color and feature support."""

    def __init__(self):
        self.term = os.environ.get("TERM", "xterm-256color")
        self.colors = self._detect_colors()
        self.has_unicode = self._detect_unicode()
        self.has_mouse = self._detect_mouse()
        self.alt_screen = self._detect_alt_screen()
        self.true_color = self._detect_true_color()

    def _detect_colors(self) -> int:
        """Detect available colors (2, 8, 16, 256, truecolor)."""
        if "256color" in self.term:
            return 256
        elif "color" in self.term:
            return 16
        else:
            return 2

    def _detect_unicode(self) -> bool:
        """Check if terminal supports Unicode (box drawing, etc)."""

    def report(self) -> str:
        """Generate capability report as string."""
        # Format for display in splash screen
```

#### 2.2 Viewport Dimension Detection

```python
# core/services/terminal_capabilities.py

class ViewportDimensions:
    """Detect terminal width and height."""

    def __init__(self):
        import shutil
        self.width, self.height = shutil.get_terminal_size((80, 24))
        self.min_recommended_width = 80
        self.min_recommended_height = 24

    def check_adequacy(self) -> Tuple[bool, str]:
        """Check if viewport meets minimum requirements."""
        adequate = (self.width >= self.min_recommended_width and
                    self.height >= self.min_recommended_height)
        message = f"Width: {self.width}ch (≥{self.min_recommended_width}) {'✓' if self.width >= self.min_recommended_width else '✗'}\n"
        message += f"Height: {self.height}L (≥{self.min_recommended_height}) {'✓' if self.height >= self.min_recommended_height else '✗'}"
        return adequate, message

    def report(self) -> str:
        """Generate viewport report."""
```

#### 2.3 Dependency Checker

```python
# core/services/dependency_checker.py

class DependencyChecker:
    """Verify Python packages and system dependencies."""

    def __init__(self):
        self.requirements_file = "requirements.txt"
        self.missing = []
        self.failed_imports = []

    def check_all(self) -> List[DependencyStatus]:
        """Check all dependencies."""
        results = []

        # Parse requirements.txt
        with open(self.requirements_file) as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                pkg_name = line.split("==")[0].strip()
                status = self._check_import(pkg_name)
                results.append(status)

        return results

    def _check_import(self, module: str) -> DependencyStatus:
        """Try to import module, return status."""
        try:
            __import__(module)
            return DependencyStatus(module, "installed", None)
        except ImportError as e:
            return DependencyStatus(module, "missing", str(e))

    def install_missing(self) -> bool:
        """Run pip install for missing packages."""
        if not self.missing:
            return True

        print("Installing missing dependencies...")
        # Show progress as pip runs
        # Return True if all installed successfully
```

#### 2.4 Startup Splash Renderer

```python
# core/services/startup_splash.py

class StartupSplash:
    """Render educational startup splash screen."""

    def __init__(self, theme: str = "dungeon"):
        self.theme = theme
        self.capabilities = TerminalCapabilities()
        self.viewport = ViewportDimensions()
        self.checker = DependencyChecker()
        self.logo = self._get_logo()

    def render_full(self, show_steps: bool = True) -> str:
        """Render complete splash with all sections."""
        lines = []
        lines.append(self._render_header())
        lines.append(self._render_capabilities())
        lines.append(self._render_viewport())
        if show_steps:
            lines.append(self._render_initialization())
        lines.append(self._render_dependencies())
        lines.append(self._render_next_steps())
        return "\n".join(lines)

    def _render_header(self) -> str:
        """Render title and version."""

    def _render_capabilities(self) -> str:
        """Render terminal capabilities report."""

    def _render_viewport(self) -> str:
        """Render viewport dimensions."""

    def _render_initialization(self, progress: float = 0.0) -> str:
        """Render step-by-step initialization with progress."""
        # Shows ✓/⟳/✗ for each system startup
        # Progress bar updates in real-time

    def _render_dependencies(self) -> str:
        """Render dependency check results."""

    def _render_next_steps(self) -> str:
        """Render "where to go from here" help."""
```

### Integration Points

**Entry in startup sequence:**

```python
# bin/start_udos.sh or core/main.py

def main():
    # 1. Show splash screen
    splash = StartupSplash(theme="dungeon")
    print(splash.render_full())

    # 2. Initialize systems (progress updates in real-time)
    systems = initialize_systems()  # Updates splash progress

    # 3. Check dependencies
    checker = DependencyChecker()
    if checker.check_all() has missing:
        print("Some optional dependencies are missing")
        if user_wants_to_install():
            checker.install_missing()

    # 4. Launch main CLI
    launch_wizard_cli()
```

### Themes

Each section supports theme variants:

```python
SPLASH_THEMES = {
    "dungeon": {
        "title_color": "bright_magenta",
        "section_border": "═",
        "check_symbol": "✓",
        "wait_symbol": "⟳",
        "error_symbol": "✗",
    },
    "electric": {
        "title_color": "bright_cyan",
        "section_border": "─",
        "check_symbol": "✓",
        "wait_symbol": "⟳",
        "error_symbol": "✗",
    },
    "minimal": {
        "title_color": "",
        "section_border": "---",
        "check_symbol": "[OK]",
        "wait_symbol": "[...]",
        "error_symbol": "[ERROR]",
    },
}
```

---

## 3. Installer Script Updates

### Current Issues

**bin/install.sh (487 lines)**

- ✅ Platform detection (Linux, macOS, TinyCore)
- ✅ Installation modes (core, desktop, wizard, dev)
- ⚠️ Limited dependency checking
- ⚠️ No installation progress feedback
- ⚠️ Limited error recovery suggestions

**bin/start_udos.sh (370 lines)**

- ✅ Banner display
- ✅ Status functions (print_status, print_success, etc)
- ⚠️ Minimal venv check
- ⚠️ No pre-flight dependency validation

### Proposed Enhancements

#### 3.1 Comprehensive Pre-flight Checks

```bash
# bin/start_udos.sh

pre_flight_checks() {
    echo "Running pre-flight checks..."

    # Check Python version
    check_python_version() {
        version=$(python3 --version 2>&1 | awk '{print $2}')
        if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
            error "Python 3.10+ required (found $version)"
            echo "  Fix: brew install python@3.11  (or update your system Python)"
            return 1
        fi
        success "Python $version"
    }

    # Check venv exists and is activated
    check_venv() {
        if [ -z "$VIRTUAL_ENV" ]; then
            error "Virtual environment not activated"
            echo "  Fix: source .venv/bin/activate"
            return 1
        fi
        success "Virtual environment: $VIRTUAL_ENV"
    }

    # Check requirements.txt packages
    check_requirements() {
        missing=$(python3 -m pip check 2>&1 | grep -c "ERROR" || true)
        if [ $missing -gt 0 ]; then
            warn "Found $missing dependency conflicts"
            echo "  Fixing: pip install -r requirements.txt --upgrade"
            pip install -r requirements.txt --quiet
        else
            success "All requirements installed"
        fi
    }

    # Check optional dependencies
    check_optional_deps() {
        echo ""
        echo "Optional dependencies:"

        if command -v ngrok &>/dev/null; then
            success "ngrok (webhooks)"
        else
            warn "ngrok not found (recommended: brew install ngrok)"
        fi

        if command -v pandoc &>/dev/null; then
            success "pandoc (PDF export)"
        else
            warn "pandoc not found (recommended: brew install pandoc)"
        fi

        if command -v sqlite3 &>/dev/null; then
            success "sqlite3 (database)"
        fi
    }

    # Check port availability
    check_ports() {
        for port in 8765 8767 5173; do
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                warn "Port $port already in use (may conflict with running services)"
            fi
        done
        success "Port availability verified"
    }

    # Run all checks
    check_python_version && \
    check_venv && \
    check_requirements && \
    check_optional_deps && \
    check_ports && \
    return 0 || return 1
}
```

#### 3.2 Installation Progress Feedback

```bash
# bin/install.sh

install_with_progress() {
    total=0
    current=0

    packages=("pip" "setuptools" "wheel" "prompt-toolkit" "fastapi" ...)

    echo "Installing Python dependencies..."
    echo ""

    for package in "${packages[@]}"; do
        ((total++))
    done

    for package in "${packages[@]}"; do
        ((current++))
        percent=$((current * 100 / total))
        printf "[%3d%%] Installing %-30s " $percent "$package"

        if pip install "$package" --quiet 2>/dev/null; then
            printf "✓\n"
        else
            printf "✗ (optional)\n"
        fi
    done

    echo ""
    success "Installation complete"
}
```

#### 3.3 Error Recovery Suggestions

```bash
# bin/install.sh

handle_installation_error() {
    local error_type=$1

    case $error_type in
        "python_not_found")
            error "Python not found"
            echo ""
            echo "To install Python:"
            echo "  macOS:  brew install python@3.11"
            echo "  Linux:  sudo apt install python3.11"
            echo "  Windows: https://python.org/downloads"
            echo ""
            echo "After installing, run: ./bin/install.sh"
            ;;

        "pip_install_failed")
            error "Failed to install Python packages"
            echo ""
            echo "Try these fixes:"
            echo "  1. Update pip: python -m pip install --upgrade pip"
            echo "  2. Clear cache: rm -rf ~/.cache/pip"
            echo "  3. Install with --no-cache-dir:"
            echo "     pip install -r requirements.txt --no-cache-dir"
            echo ""
            echo "Or run in development mode:"
            echo "  ./bin/install.sh --mode dev"
            ;;

        "port_conflict")
            error "Required ports already in use"
            echo ""
            echo "Conflicting services:"
            echo "  Port 8765 (Wizard): $(lsof -i :8765 -n -P | grep LISTEN)"
            echo "  Port 8767 (Goblin): $(lsof -i :8767 -n -P | grep LISTEN)"
            echo "  Port 5173 (Frontend): $(lsof -i :5173 -n -P | grep LISTEN)"
            echo ""
            echo "Options:"
            echo "  1. Stop conflicting services"
            echo "  2. Run in different ports: WIZARD_PORT=8765 goblin_PORT=8768"
            ;;
    esac
}
```

### File Updates

**Files to modify:**

- `bin/start_udos.sh` - Add pre_flight_checks() function
- `bin/install.sh` - Add install_with_progress() and error handling
- `bin/Launch-Goblin-Dev.command` - Add dependency validation

**New files:**

- `bin/pre-flight-checks.sh` - Reusable checks library
- `bin/install-functions.sh` - Installation helpers

---

## 4. Command Registry Service

### Purpose

Centralize command definitions so they're used by:

- Smart prompt (autocomplete)
- Wizard CLI (help, syntax validation)
- Goblin API (command suggestions)
- Tauri app (menu generation)

### Design

```python
# wizard/services/command_registry.py

class CommandRegistry:
    """Central registry of all uDOS commands."""

    def __init__(self, commands_file: str = "core/data/commands.json"):
        self.commands = self._load_commands(commands_file)
        self.categories = self._build_categories()

    def get_command(self, name: str) -> CommandSchema:
        """Get command definition."""
        return self.commands.get(name.upper())

    def get_all_commands(self) -> List[str]:
        """List all available commands."""

    def search(self, keyword: str) -> List[str]:
        """Search for commands by keyword."""

    def get_by_category(self, category: str) -> List[str]:
        """Get commands in category (File, Cloud, System, etc)."""

    def validate(self, command: str, args: List[str]) -> ValidationResult:
        """Validate command syntax against schema."""

@dataclass
class CommandSchema:
    name: str                          # "STATUS"
    category: str                      # "System"
    description: str                   # "Show system status"
    syntax: str                        # "STATUS [--detailed]"
    args: List[ArgumentSchema]         # Expected arguments
    options: List[OptionSchema]        # Optional flags
    examples: List[str]                # Usage examples
    version_added: str                 # "1.0.0"
    related: List[str]                 # Related commands
```

### Schema Format

```json
{
  "commands": {
    "STATUS": {
      "category": "System",
      "description": "Show system status and health",
      "syntax": "STATUS [--detailed] [--json]",
      "args": [],
      "options": [
        {
          "name": "detailed",
          "short": "d",
          "description": "Show detailed information",
          "type": "boolean"
        },
        {
          "name": "json",
          "short": "j",
          "description": "Output as JSON",
          "type": "boolean"
        }
      ],
      "examples": ["STATUS", "STATUS --detailed", "STATUS --json | jq ."],
      "version_added": "1.0.0",
      "related": ["HEALTH", "SHAKEDOWN"]
    },
    "CLOUD": {
      "category": "Cloud",
      "description": "Cloud operations",
      "subcommands": {
        "GENERATE": {
          "description": "Generate keywords with AI",
          "syntax": "CLOUD GENERATE <topic> [--max N] [--lang CODE]",
          "args": [
            {
              "name": "topic",
              "type": "string",
              "required": true,
              "description": "Search topic"
            }
          ],
          "options": [
            {
              "name": "max",
              "type": "number",
              "description": "Maximum results"
            }
          ],
          "examples": ["CLOUD GENERATE \"machine learning\" --max 20"]
        }
      }
    }
  }
}
```

### Integration Points

**Used by:**

1. **Smart Prompt** - Get suggestions for subcommands/options

   ```python
   registry = CommandRegistry()
   cloud_cmd = registry.get_command("CLOUD")
   subcommands = [sc for sc in cloud_cmd.subcommands.keys()]
   # ["GENERATE", "RESOLVE", "BUSINESS", ...]
   ```

2. **Wizard CLI** - Validate and help

   ```python
   result = registry.validate("CLOUD GENERATE", ["topic"])
   if not result.valid:
       print(result.error_message)
   ```

3. **Goblin API** - Serve schema

   ```python
   @goblin_app.get("/api/v0/commands")
   def list_commands():
       return registry.get_all_commands()

   @goblin_app.get("/api/v0/commands/{cmd}")
   def get_command(cmd: str):
       return registry.get_command(cmd)
   ```

---

## Implementation Timeline

### Phase 1: Foundation (Week 1)

- [ ] Create `command_registry.py`
- [ ] Build `commands.json` schema
- [ ] Update smart prompt to use registry
- [ ] Document registry API

**Deliverable:** Single source of truth for commands

### Phase 2: Startup & Status (Week 2)

- [ ] Implement `startup_splash.py`
- [ ] Add terminal capability detection
- [ ] Create `status_bar.py` with themes
- [ ] Integrate health checks

**Deliverable:** Educational startup screen + persistent status display

### Phase 3: Installer Updates (Week 3)

- [ ] Add pre-flight checks to `start_udos.sh`
- [ ] Implement installation progress in `install.sh`
- [ ] Add error recovery suggestions
- [ ] Test on all platforms (macOS, Linux, TinyCore)

**Deliverable:** Better installation experience

### Phase 4: Integration & Testing (Week 4)

- [ ] Browser-based REPL in Goblin frontend
- [ ] WebSocket status updates
- [ ] Comprehensive test suite
- [ ] Documentation and user guide

**Deliverable:** Fully integrated CLI enhancement

---

## Success Metrics

1. **User Experience**

   - Installation success rate > 95%
   - Command discoverability improved by smart prompt
   - Startup feedback clear and helpful

2. **Technical Quality**

   - 90%+ test coverage for new modules
   - Zero hardcoded version strings
   - Single source of truth for commands

3. **Documentation**

   - User guide for smart prompt (✅ Done)
   - Developer guide for registry
   - Installation troubleshooting guide

4. **Performance**
   - Startup time unchanged (<5s to CLI)
   - Status bar updates <500ms
   - Smart prompt suggestions <100ms

---

## References

- [Smart Prompt User Guide](./SMART-PROMPT-USER-GUIDE.md)
- [CLI Enhancement Progress](./CLI-ENHANCEMENT-PROGRESS-2026-01-16.md)
- [Wizard Server Documentation](../wizard/README.md)
- [Goblin Dev Server Documentation](../dev/goblin/README.md)

---

_Last Updated: 2026-01-16_  
_Specification Version: 1.0_  
_Target Release: v1.0.5.0_
