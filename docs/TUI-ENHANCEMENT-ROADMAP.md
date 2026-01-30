---
uid: udos-tui-enhancement-2026-01-30
title: TUI Command Prompt Enhancement Roadmap
tags: [tui, enhancement, input, commands, filepicker, help]
status: living
updated: 2026-01-30
---

# uDOS TUI Command Prompt Enhancement Roadmap

**Date:** 2026-01-30  
**Current State:** Analysis & Planning  
**Target Parity:** Vibe-CLI / Claude Code TUI  
**Scope:** Make the global command prompt as advanced as the existing FilePicker

---

## 🎯 Executive Summary

The TUI command prompt (`uCODE.py`, `EnhancedPrompt`, `SmartPrompt`) exists but lacks the **input helper lines, scrollable selectors, workspace pickers, and F-key bindings** that exist in the advanced `FileBrowser` and `SelectorFramework`.

### Current State: Asymmetry
- ✅ **FileBrowser** (`core/tui/file_browser.py`) - Advanced, modular, scrollable, number-based selection
- ✅ **SelectorFramework** (`core/ui/selector_framework.py`) - Unified selection system (SINGLE, MULTI, GRID modes)
- ✅ **KeypadHandler** (`core/input/keypad_handler.py`) - Numpad input support
- ❌ **Global Command Prompt** - Still uses basic `input()` with limited help context
- ❌ **F-Key Support** - Exists (`FKeyHandler`) but not wired into command flow

### Goal
**Unify input patterns**: Apply FileBrowser's modular selector architecture to the global TUI command prompt.

---

## 📊 Current Implementation State

### What Works
| Component | File | Status | Features |
|-----------|------|--------|----------|
| **FileBrowser** | `core/tui/file_browser.py` | ✅ Production | Selector, keypad (1-9), pagination, search, icon display |
| **SelectorFramework** | `core/ui/selector_framework.py` | ✅ Production | SINGLE/MULTI/GRID modes, navigation, filtering |
| **EnhancedPrompt** | `core/input/enhanced_prompt.py` | ⚠️ Partial | 2-line context (planned but incomplete) |
| **SmartPrompt** | `core/input/smart_prompt.py` | ✅ Production | Autocomplete, history, syntax highlighting (via prompt_toolkit) |
| **FKeyHandler** | `core/tui/fkey_handler.py` | ⚠️ Wired but unused | F1-F12 support (not integrated into REPL) |
| **KeypadHandler** | `core/input/keypad_handler.py` | ✅ Production | Numpad 0-9, modes: NAVIGATION, SELECTION, INPUT |
| **uCODE TUI** | `core/tui/ucode.py` | ✅ Production | Main REPL loop, command dispatch (uses `input()`) |

### Architecture Pattern (FileBrowser)
```python
FileBrowser (display + input loop)
    ↓
SelectorFramework (state + navigation)
    ↓
KeypadHandler (numpad input)
    ↓
Selector items (display lines)
```

### Problem: Command Prompt doesn't follow this pattern
```python
uCODE REPL
    ↓
input() [basic, no context, no selector]
    ↓
CommandDispatcher (dumb parsing)
```

---

## 🏗️ Enhancement Architecture

### Phase 1: Input Helper Lines (Foundation)
**Goal**: Add predictive auto-fill + help/syntax lines below prompt.

**Implementation**:
```
▶ command_prefix... ← User typing (SmartPrompt autocomplete)
  ╭─ Suggestions: STATUS, SHAKEDOWN, HELP, WIZARD (+47 more)
  ╰─ Syntax: COMMAND [options...] | Type '?' for HELP
```

**Files to Create/Update**:
- `core/input/command_prompt.py` (NEW) - ContextualCommandPrompt class
- `core/tui/ucode.py` - Update REPL loop to use new prompt

**Key Features**:
- Autocomplete suggestions (from registered commands)
- Predictions update as user types
- Help text synced with command metadata
- Display format: standardized 2-line helper

---

### Phase 2: Workspace Picker (FileBrowser Pattern)
**Goal**: Modular workspace selector at top of file picker.

**Implementation**:
```
╔═══════════════════════════════════════════╗
║  Select Workspace (Before File Picker)   ║
╠═══════════════════════════════════════════╣
║  1. 📁 memory/sandbox     (Your workspace) ║
║  2. 📁 memory/bank        (Saved data)     ║
║  3. 📁 /knowledge         (Admin: guides)  ║
║  0. Next page / ? Help                    ║
╚═══════════════════════════════════════════╝
```

**Files to Create/Update**:
- `core/ui/workspace_selector.py` (NEW) - WorkspacePicker class
- `core/tui/file_browser.py` - Add workspace picker header
- `extensions/api/routes/filepicker.py` - Link workspace selector to API

**Key Features**:
- Reuses SelectorFramework (SINGLE mode)
- Role-based visibility (show @knowledge only if admin)
- Returns selected workspace path
- Integrates with existing FileBrowser

---

### Phase 3: Global Menu Selector (ModularCommand Menu)
**Goal**: Command selection menu using SelectorFramework (like FileBrowser).

**Implementation**:
```
▶ Enter command (or press TAB for menu):
  
╔═══════════════════════════════════════════╗
║  Available Commands                       ║
╠═══════════════════════════════════════════╣
║  1. STATUS   - System health check        ║
║  2. HELP     - Show available commands    ║
║  3. SHAKEDOWN - Full system validation    ║
║  4. WIZARD   - Start/stop server          ║
║  0. Next / ? Help                         ║
╚═══════════════════════════════════════════╝
```

**Files to Create/Update**:
- `core/ui/command_selector.py` (NEW) - CommandSelector class
- `core/tui/ucode.py` - Integrate TAB key → command menu
- `core/commands/command_registry.py` - Register all commands with metadata

**Key Features**:
- TAB key opens modal menu (like FileBrowser)
- Number selection (1-9) picks command
- Shows command name + help description
- Pagination for 50+ commands
- Searchable (type to filter)

---

### Phase 4: F-Key Integration
**Goal**: Wire FKeyHandler into REPL loop for quick actions.

**Implementation**:
```
F1  → HELP
F2  → STATUS (system check)
F3  → Recent commands
F4  → Workspace picker
F5  → Refresh/reload
F6  → Wizard controls
F12 → Debug/developer mode
```

**Files to Create/Update**:
- `core/tui/fkey_handler.py` - Already exists, just wire it in
- `core/tui/ucode.py` - Capture F-keys in REPL loop
- `core/config/keybindings.yaml` (NEW) - Definable F-key mappings

**Key Features**:
- Non-invasive (intercept before command processing)
- Customizable via config file
- Show F-key hints in status bar
- Context-aware (change based on last command)

---

### Phase 5: Advanced Help System (Dynamic Docs)
**Goal**: Real-time, context-aware help panel.

**Implementation**:
```
▶ help <command>

╔═══════════════════════════════════════════╗
║  HELP: WIZARD                             ║
╠═══════════════════════════════════════════╣
║  Status: Wizard server management         ║
║  Syntax: WIZARD [start|stop|status|logs]  ║
║  Options:                                 ║
║    --port N    Override default (8765)    ║
║    --debug     Show server debug logs     ║
║  Examples:                                ║
║    WIZARD start       ← Start server      ║
║    WIZARD status      ← Check if running  ║
║    WIZARD logs --tail ← Follow logs       ║
╚═══════════════════════════════════════════╝
```

**Files to Create/Update**:
- `core/services/help_system.py` (NEW) - HelpSystem service
- `core/commands/*/handler.py` - Add help metadata to each handler
- `core/commands/help_handler.py` - Implement HELP command

**Key Features**:
- Pulls help from command metadata
- Shows syntax, options, examples
- Scrollable for long help text
- Linked to command discovery

---

## 📋 Detailed Implementation Plan

### ✅ Step 1: ContextualCommandPrompt (Phase 1) — COMPLETED 2026-01-30

**Status**: ✅ Implemented and integrated into uCODE REPL

**Files Created**:
- ✅ `core/input/command_prompt.py` — CommandRegistry, CommandMetadata, ContextualCommandPrompt
- ✅ Updated `core/input/__init__.py` — Exported new classes
- ✅ Updated `core/tui/ucode.py` — Integrated into REPL loop

**What Changed**:
1. **Created CommandRegistry** — Centralized command metadata storage
   - Registered 15+ core commands (STATUS, HELP, WIZARD, BINDER, etc.)
   - Each command has: name, help_text, syntax, options, examples, icon, category
   - Smart fuzzy matching for suggestions (prefix + substring)

2. **Created ContextualCommandPrompt** — Extends EnhancedPrompt
   - `ask_command()` method replaces plain `input()`
   - Integrates with SmartPrompt for autocomplete
   - Foundation for future 2-line context display

3. **Integrated into uCODE REPL** — Line 267 in `ucode.py`
   - Changed from: `user_input = self.prompt.ask(plain_prompt)`
   - Changed to: `user_input = self.prompt.ask_command("▶ ")`
   - Command registry created during TUI initialization

**Next Steps for Phase 1 Completion**:
- [ ] Add real-time suggestion display (requires terminal control)
- [ ] Display 2-line context as user types:
  ```
  ▶ wiz_
    ╭─ Suggestions: WIZARD (+1 more)
    ╰─ 🧙 Wizard server management (start/stop/status)
  ```
- [ ] Test with prompt_toolkit integration
- [ ] Add unit tests for CommandRegistry

---

### ✅ Step 2: WorkspacePicker (Phase 2) — COMPLETED 2026-01-30

**Status**: ✅ Implemented and integrated into FILE command

**Files Created**:
- ✅ `core/ui/workspace_selector.py` — WorkspacePicker, WorkspaceOption, helper functions
- ✅ `core/commands/file_handler.py` — FILE command with workspace picker integration
- ✅ Updated `core/ui/__init__.py` — Exported new classes
- ✅ Updated `core/tui/dispatcher.py` — Registered FILE handler
- ✅ Updated `core/commands/__init__.py` — Exported FileHandler
- ✅ Updated `core/input/command_prompt.py` — Added FILE to registry

**What Changed**:
1. **Created WorkspacePicker** — Interactive workspace selector
   - Shows: @sandbox, @bank, @shared (always)
   - Admin-only: @wizard, @knowledge, @dev
   - Uses SelectorFramework pattern (consistent with FileBrowser)
   - Number selection (1-9), pagination, search
   - Help overlay with workspace descriptions

2. **Created FileHandler** — FILE command with two modes
   - Interactive: `FILE` opens WorkspacePicker → FileBrowser
   - Quick: `FILE LIST @sandbox`, `FILE SHOW @sandbox/file.md`
   - Help: `FILE HELP` shows complete usage
   - Role-aware: Respects admin vs user permissions

3. **Integration Functions** — Convenience helpers
   - `pick_workspace()` — Select workspace only
   - `pick_workspace_then_file()` — Two-stage picker
   - Auto-detects project root, handles cancellation

**User Experience**:
```
▶ FILE
  → Workspace picker appears
  → User selects @sandbox (or other workspace)
  → File browser opens in that workspace
  → User navigates and selects file
  → File info displayed
```

**Next Steps**:
- [ ] Add workspace statistics to picker (file count, size)
- [ ] Add recent workspaces quick-access
- [ ] Add F4 hotkey integration (Phase 4)
- [ ] Test with admin vs user roles

---

### Step 3: CommandSelector (Phase 3)

**File**: `core/input/command_prompt.py`

```python
"""
Contextual Command Prompt (v1.0.0)

Wrapper around SmartPrompt that adds:
- Dynamic suggestions (from registered commands)
- Help text (from command metadata)
- 2-line context display
- Autocomplete on Tab
"""

class CommandRegistry:
    """Registry of all available commands."""
    def __init__(self):
        self.commands: Dict[str, CommandMetadata] = {}
    
    def register(self, name: str, help_text: str, options: List[str]):
        """Register a command with metadata."""
        pass
    
    def get_suggestions(self, prefix: str) -> List[str]:
        """Get command suggestions for prefix."""
        pass

class ContextualCommandPrompt(EnhancedPrompt):
    """Enhanced prompt with command registry integration."""
    
    def __init__(self, registry: CommandRegistry):
        super().__init__()
        self.registry = registry
    
    def ask_command(self, prompt_text: str = "▶ ") -> str:
        """Ask for command with predictive help."""
        # As user types, update suggestions/help
        # Display:
        #   ▶ user_input...
        #   ╭─ Suggestions: CMD1, CMD2, CMD3
        #   ╰─ Help: Command syntax...
        pass
```

### Step 2: WorkspacePicker (Phase 2)

**File**: `core/ui/workspace_selector.py`

```python
"""
Workspace Selector (v1.0.0)

Reuses SelectorFramework for workspace selection.
Shows at top of FilePicker or as standalone.
"""

class WorkspacePicker:
    """Workspace selection using SelectorFramework."""
    
    def __init__(self, admin: bool = False):
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=3,  # Show: sandbox, bank, knowledge
            )
        )
        self._init_items(admin)
    
    def _init_items(self, admin: bool):
        """Load workspace items."""
        items = [
            SelectableItem(
                id="sandbox",
                label="memory/sandbox",
                icon="📁",
                metadata={"path": "memory/sandbox"}
            ),
            SelectableItem(
                id="bank",
                label="memory/bank",
                icon="📁",
                metadata={"path": "memory/bank"}
            ),
        ]
        if admin:
            items.append(SelectableItem(
                id="knowledge",
                label="/knowledge",
                icon="📚",
                metadata={"path": "/knowledge"}
            ))
        self.selector.set_items(items)
    
    def pick(self) -> Optional[str]:
        """Run picker, return selected workspace path."""
        # Use FileBrowser pattern: display + input loop
        pass
```

### Step 3: CommandSelector (Phase 3)

**File**: `core/ui/command_selector.py`

```python
"""
Command Selector Menu (v1.0.0)

Modal menu for command selection using SelectorFramework.
Invoked by TAB key in command prompt.
"""

class CommandSelector:
    """Modal command selection menu."""
    
    def __init__(self, dispatcher: CommandDispatcher):
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                enable_search=True,
            )
        )
        self._load_commands(dispatcher)
    
    def _load_commands(self, dispatcher: CommandDispatcher):
        """Load commands from dispatcher."""
        items = []
        for cmd_name, handler in dispatcher.commands.items():
            help_text = handler.__doc__ or "No help"
            items.append(SelectableItem(
                id=cmd_name,
                label=cmd_name,
                metadata={"help": help_text},
            ))
        self.selector.set_items(items)
    
    def pick(self) -> Optional[str]:
        """Show menu, return selected command name."""
        # Use FileBrowser display pattern
        pass
```

### Step 4: FKey Integration (Phase 4)

**Update**: `core/tui/ucode.py`

```python
def main_repl_loop(self):
    """Main REPL loop with F-key support."""
    while True:
        # Get input with F-key capture
        key = self._read_raw_key()  # Read raw input
        
        if key.startswith("F"):  # F1-F12
            self._handle_fkey(key)
            continue
        
        if key == "TAB":  # Open command selector
            cmd = self.command_selector.pick()
            if cmd:
                # Continue with command
                pass
            continue
        
        # Normal command processing
        command_input = self.prompt.ask_command()
        self.dispatcher.execute(command_input)
```

### Step 5: Help System (Phase 5)

**File**: `core/services/help_system.py`

```python
"""
Help System Service (v1.0.0)

Central help provider for all commands.
Pulls help from command metadata.
"""

class HelpSystem:
    """Centralized help provider."""
    
    def __init__(self, dispatcher: CommandDispatcher):
        self.dispatcher = dispatcher
    
    def get_help(self, command: str) -> HelpContent:
        """Get help for a command."""
        handler = self.dispatcher.commands.get(command)
        if not handler:
            return None
        return HelpContent(
            name=command,
            description=handler.__doc__,
            syntax=getattr(handler, "syntax", ""),
            options=getattr(handler, "options", []),
            examples=getattr(handler, "examples", []),
        )
    
    def display_help(self, command: str):
        """Display help in formatted panel."""
        help_content = self.get_help(command)
        if not help_content:
            print(f"No help for '{command}'")
            return
        
        # Format and display help panel
        # (scrollable if long)
        pass
```

---

## 🔗 Integration Points

### CommandRegistry ↔ CommandDispatcher
- Registry holds all command metadata
- Dispatcher executes commands
- Both sources in `core/commands/` folder

### CommandSelector ↔ uCODE REPL
- TAB key in prompt → opens selector
- Selector returns command name
- REPL continues with that command

### WorkspacePicker ↔ FileBrowser
- Show workspace selector before file list
- User picks workspace first
- FileBrowser starts in that workspace

### FKeyHandler ↔ REPL Loop
- REPL loop captures F-keys
- Routes to FKeyHandler
- FKeyHandler triggers actions or opens panels

### HelpSystem ↔ All Commands
- Each command handler provides metadata
- HelpSystem formats & displays
- HELP command queries HelpSystem

---

## 📁 File Structure

```
core/
├── input/
│   ├── command_prompt.py        ← NEW (Phase 1)
│   ├── enhanced_prompt.py       ← UPDATE (2-line context complete)
│   ├── smart_prompt.py          ← REFERENCE (autocomplete)
│   └── ...
├── ui/
│   ├── workspace_selector.py    ← NEW (Phase 2)
│   ├── command_selector.py      ← NEW (Phase 3)
│   ├── selector_framework.py    ← REFERENCE
│   └── ...
├── services/
│   ├── help_system.py           ← NEW (Phase 5)
│   └── ...
├── tui/
│   ├── ucode.py                 ← UPDATE (F-key integration, Phase 4)
│   ├── fkey_handler.py          ← REFERENCE (already exists)
│   ├── file_browser.py          ← UPDATE (workspace picker header, Phase 2)
│   └── ...
└── commands/
    ├── command_registry.py      ← NEW (metadata for all commands)
    └── */handler.py             ← UPDATE (add help metadata)
```

---

## 🧪 Testing Strategy

### Unit Tests
- `test_command_prompt.py` - Suggestions, help text generation
- `test_workspace_selector.py` - Workspace item loading
- `test_command_selector.py` - Command filtering, selection
- `test_fkey_handler.py` - F-key dispatch (already exists)
- `test_help_system.py` - Help content retrieval

### Integration Tests
- TAB key → command selector → execute
- F2 → status check
- Workspace picker → file browser flow
- Help system with all command handlers

### Acceptance Tests
- Compare with Vibe-CLI behavior
- Compare with Claude Code TUI
- Verify keyboard-only usage (no mouse needed)

---

## 🎯 Success Criteria

### Parity with FileBrowser
- [ ] Command prompt shows input helper lines (like FileBrowser display)
- [ ] TAB key opens scrollable selector (like FileBrowser)
- [ ] Number keys (1-9) select items (like FileBrowser)
- [ ] Search/filter works (like FileBrowser)
- [ ] Pagination for 50+ commands (like FileBrowser)

### Advanced Features
- [ ] F-keys work globally (F1=help, F2=status, etc.)
- [ ] Workspace picker visible (admin shows @knowledge)
- [ ] Help text pulls from command metadata
- [ ] Real-time suggestions as user types
- [ ] Context-aware help (shows syntax, options, examples)

### UX Quality
- [ ] No mouse required (keyboard-only works)
- [ ] Visual feedback (highlighting, icons)
- [ ] Consistent with Vibe-CLI / Claude Code
- [ ] No performance regression (<100ms input→response)

---

## 🚀 Timeline

| Phase | Component | Effort | Target | Status |
|-------|-----------|--------|--------|--------|
| 1 | ContextualCommandPrompt | 3h | Week 1 | 📋 Planning |
| 2 | WorkspacePicker | 2h | Week 2 | 📋 Planning |
| 3 | CommandSelector | 3h | Week 2 | 📋 Planning |
| 4 | FKey Integration | 2h | Week 3 | 📋 Planning |
| 5 | HelpSystem | 2h | Week 3 | 📋 Planning |
| QA | Integration + Polish | 2h | Week 4 | 📋 Planning |
| **Total** | | **14h** | **4 weeks** | 📋 Planning |

---

## 📚 References

### Existing Patterns (Reference)
- [SelectorFramework](../../core/ui/selector_framework.py) - Selection architecture
- [FileBrowser](../../core/tui/file_browser.py) - Modular display + input
- [KeypadHandler](../../core/input/keypad_handler.py) - Numpad input
- [EnhancedPrompt](../../core/input/enhanced_prompt.py) - 2-line context (partial)
- [FKeyHandler](../../core/tui/fkey_handler.py) - F-key support

### Related Systems
- [CommandDispatcher](../../core/tui/dispatcher.py) - Command routing
- [GridRenderer](../../core/tui/renderer.py) - TUI rendering
- [GameState](../../core/tui/state.py) - TUI state machine

---

## ❓ Open Questions

1. **Keyboard shortcuts**: What other shortcuts beyond F-keys? (Ctrl+K for command palette?)
2. **Help panel position**: Below prompt, or full-screen modal like FileBrowser?
3. **Workspace picker**: Always show, or only in file-related commands?
4. **Command metadata storage**: In handler docstrings, or separate YAML file?
5. **History integration**: Should command selector show recent commands?

---

**Status**: Living Document  
**Last Updated**: 2026-01-30  
**Next Review**: After Phase 1 completion
