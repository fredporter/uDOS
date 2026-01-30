---
uid: udos-tui-implementation-checklist-2026-01-30
title: TUI Enhancement Implementation Checklist
tags: [tui, checklist, implementation, tasks]
status: living
updated: 2026-01-30
---

# TUI Enhancement Implementation Checklist

**Scope**: Make global command prompt as advanced as FileBrowser  
**Pattern**: Apply `SelectorFramework` + `FileBrowser` architecture to command input  
**Target**: Achieve Vibe-CLI / Claude Code TUI parity

---

## Phase 1: Input Helper Lines ✅ Planning

### 1.1 Create ContextualCommandPrompt (`core/input/command_prompt.py`)

**Subtasks**:
- [ ] Create new file with docstring
- [ ] Import `EnhancedPrompt`, `SmartPrompt`
- [ ] Implement `CommandRegistry` class
  - [ ] `__init__()` - Initialize command dict
  - [ ] `register(name, help_text, options)` - Add command metadata
  - [ ] `get_suggestions(prefix)` - Return matching commands
  - [ ] `get_help(command)` - Return help text
- [ ] Implement `ContextualCommandPrompt` class (extends EnhancedPrompt)
  - [ ] `__init__(registry)` - Store registry
  - [ ] `ask_command()` - Show prompt with helper lines
  - [ ] `_update_suggestions()` - Sync suggestions as user types
  - [ ] `_display_helper_lines()` - Format 2-line context

**Code Template**:
```python
class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, CommandMetadata] = {}
    
    def register(self, name: str, help_text: str, options: List[str]):
        """Register command with metadata."""
        self.commands[name.upper()] = CommandMetadata(
            name=name, help=help_text, options=options
        )
    
    def get_suggestions(self, prefix: str) -> List[str]:
        """Get suggestions for prefix (fuzzy match)."""
        prefix_upper = prefix.upper()
        return [
            cmd for cmd in self.commands.keys() 
            if cmd.startswith(prefix_upper)
        ]
```

**Integration Point**: `core/tui/ucode.py` - Replace `input()` call in REPL loop

### 1.2 Update EnhancedPrompt (complete 2-line context)

**File**: `core/input/enhanced_prompt.py`

**Subtasks**:
- [ ] Review current implementation (lines 19-100)
- [ ] Complete `ask_with_context()` method
  - [ ] Display Line 1: current value OR predictions
  - [ ] Display Line 2: help text or hint
  - [ ] Call SmartPrompt for actual input
- [ ] Complete `ask_confirmation()` method
  - [ ] Show [1|0|Yes|No|OK|Cancel] format
  - [ ] Parse responses correctly
- [ ] Add unit tests
  - [ ] Test 2-line display
  - [ ] Test prediction display
  - [ ] Test confirmation options

### 1.3 Wire ContextualCommandPrompt into uCODE REPL

**File**: `core/tui/ucode.py` (around line 850-900, main loop)

**Subtasks**:
- [ ] Import `CommandRegistry`, `ContextualCommandPrompt`
- [ ] Create registry in `uCODETUI.__init__()`
- [ ] Register all commands (STATUS, HELP, WIZARD, etc.)
- [ ] Replace `input()` call with `prompt.ask_command()`
- [ ] Test in interactive mode

---

## Phase 2: Workspace Picker 📁 Planning

### 2.1 Create WorkspacePicker (`core/ui/workspace_selector.py`)

**Subtasks**:
- [ ] Create new file with docstring
- [ ] Import `SelectorFramework`, `SelectableItem`, `SelectorConfig`
- [ ] Implement `WorkspacePicker` class
  - [ ] `__init__(admin: bool)` - Initialize selector
  - [ ] `_init_items(admin)` - Load workspace items
    - [ ] memory/sandbox (always)
    - [ ] memory/bank (always)
    - [ ] /knowledge (only if admin)
  - [ ] `display()` - Render workspace list
  - [ ] `handle_input()` - Process number keys, TAB, Enter
  - [ ] `pick()` - Main loop, return selected workspace path
- [ ] Add icons for visual clarity
  - [ ] "📁" for memory workspaces
  - [ ] "📚" for knowledge base

**Code Template**:
```python
class WorkspacePicker:
    def __init__(self, admin: bool = False):
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=3,
                show_numbers=True,
            )
        )
        self._init_items(admin)
    
    def _init_items(self, admin: bool):
        items = [
            SelectableItem(
                id="sandbox",
                label="memory/sandbox",
                icon="📁",
                metadata={"path": "memory/sandbox", "writable": True}
            ),
            SelectableItem(
                id="bank",
                label="memory/bank",
                icon="📁",
                metadata={"path": "memory/bank", "writable": True}
            ),
        ]
        if admin:
            items.append(SelectableItem(
                id="knowledge",
                label="/knowledge",
                icon="📚",
                metadata={"path": "/knowledge", "writable": False}
            ))
        self.selector.set_items(items)
    
    def pick(self) -> Optional[str]:
        """Run picker, return path."""
        while True:
            self.display()
            key = self._read_key()
            if key == "q":
                return None
            result = self.handle_input(key)
            if isinstance(result, str):
                return result
```

### 2.2 Update FileBrowser to include WorkspacePicker

**File**: `core/tui/file_browser.py`

**Subtasks**:
- [ ] Import `WorkspacePicker`
- [ ] Add `show_workspace_picker` parameter to `__init__()`
- [ ] In `pick()` main loop, call workspace picker first if enabled
- [ ] Update `display()` to show current workspace at top
- [ ] Test integrated flow

### 2.3 Update API to expose workspace endpoints

**File**: `extensions/api/routes/filepicker.py`

**Subtasks**:
- [ ] Verify `/api/filepicker/workspaces` endpoint exists (it does)
- [ ] Add workspace routing to TUI picker
- [ ] Test API → TUI picker flow

---

## Phase 3: Command Selector (Modal Menu) 🎯 Planning

### 3.1 Create CommandSelector (`core/ui/command_selector.py`)

**Subtasks**:
- [ ] Create new file with docstring
- [ ] Import `SelectorFramework`, `CommandDispatcher`
- [ ] Implement `CommandSelector` class
  - [ ] `__init__(dispatcher)` - Initialize with commands
  - [ ] `_load_commands()` - Convert dispatcher.commands → SelectableItems
    - [ ] Use command name as label
    - [ ] Use help text / docstring as metadata
    - [ ] Add icons (🔧 for system, 📚 for help, etc.)
  - [ ] `display()` - Render command menu
  - [ ] `handle_input()` - Process 1-9, search, Enter
  - [ ] `pick()` - Main loop, return selected command name
  - [ ] `search()` - Filter commands by name/help

**Code Template**:
```python
class CommandSelector:
    def __init__(self, dispatcher: CommandDispatcher):
        self.dispatcher = dispatcher
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                enable_search=True,
                show_numbers=True,
            )
        )
        self._load_commands()
    
    def _load_commands(self):
        items = []
        for cmd_name, handler in self.dispatcher.commands.items():
            help_text = (handler.__doc__ or "No description").split("\n")[0]
            icon = self._get_command_icon(cmd_name)
            items.append(SelectableItem(
                id=cmd_name,
                label=f"{cmd_name:12} - {help_text}",
                icon=icon,
                metadata={"command": cmd_name}
            ))
        self.selector.set_items(sorted(items, key=lambda x: x.label))
    
    def _get_command_icon(self, cmd: str) -> str:
        """Return icon based on command category."""
        icons = {
            "STATUS": "📊",
            "HELP": "❓",
            "SHAKEDOWN": "✅",
            "WIZARD": "🧙",
            # ... more
        }
        return icons.get(cmd, "⚙️")
    
    def pick(self) -> Optional[str]:
        """Run selector, return command name."""
        while True:
            self.display()
            key = self._read_key()
            if key == "q" or key == "\x1b":  # ESC
                return None
            result = self.handle_input(key)
            if isinstance(result, str):
                return result
```

### 3.2 Update uCODE REPL to open selector on TAB

**File**: `core/tui/ucode.py`

**Subtasks**:
- [ ] Import `CommandSelector`
- [ ] Create selector in `uCODETUI.__init__()`
- [ ] In REPL loop, capture TAB key before SmartPrompt
  - [ ] Open selector modal
  - [ ] Get selected command
  - [ ] Insert command into prompt or execute directly
- [ ] Test TAB → menu → selection flow

### 3.3 Create CommandRegistry metadata system

**File**: `core/commands/command_registry.py` (NEW)

**Subtasks**:
- [ ] Define `CommandMetadata` dataclass
  - [ ] name, help_text, options, icon, examples
- [ ] Implement `CommandRegistry` singleton
  - [ ] `register_all()` - Load from dispatcher
  - [ ] `get_metadata(cmd)` - Lookup command info
- [ ] Update each handler to include metadata
  - [ ] `STATUS` - "System health check"
  - [ ] `HELP` - "Show available commands"
  - [ ] `SHAKEDOWN` - "Full system validation"
  - [ ] WIZARD` - "Start/stop/status server"
  - [ ] etc.

---

## Phase 4: F-Key Integration ⌨️ Planning

### 4.1 Wire FKeyHandler into REPL

**File**: `core/tui/ucode.py`

**Subtasks**:
- [ ] Import `FKeyHandler`
- [ ] Create handler in `uCODETUI.__init__()`
- [ ] In REPL loop, implement `_read_raw_key()` to capture F-keys
  - [ ] Return raw key codes (F1, F2, etc.)
  - [ ] Pass through SmartPrompt if not an F-key
- [ ] In REPL loop, call `_handle_fkey()` for F-keys
  - [ ] F1 → HELP
  - [ ] F2 → STATUS
  - [ ] F3 → History
  - [ ] F4 → Workspace picker
  - [ ] F5 → Refresh/reload
  - [ ] F6 → Wizard controls
  - [ ] F12 → Debug mode
- [ ] Test each F-key

### 4.2 Create FKey Binding Config

**File**: `core/config/keybindings.yaml` (NEW)

**Subtasks**:
- [ ] Define YAML structure
  ```yaml
  fkeys:
    f1: command:help
    f2: command:status
    f3: history:show
    f4: workspace:picker
    f5: reload
    f6: wizard:toggle
    f12: debug:toggle
  
  shortcuts:
    ctrl_k: command:selector
    ctrl_h: help:context
  ```
- [ ] Implement loader in FKeyHandler
- [ ] Make bindings customizable (user can override)

### 4.3 Add F-key hint line to TUI

**File**: `core/tui/status_bar.py`

**Subtasks**:
- [ ] Update status bar to show F-key hints
  - [ ] "F1=Help | F2=Status | F4=Workspace | F6=Wizard"
- [ ] Update based on context (change hints for different modes)

---

## Phase 5: Help System 📖 Planning

### 5.1 Create Help System Service

**File**: `core/services/help_system.py` (NEW)

**Subtasks**:
- [ ] Define `HelpContent` dataclass
  - [ ] name, description, syntax, options[], examples[]
- [ ] Implement `HelpSystem` class
  - [ ] `__init__(dispatcher, registry)` - Initialize with commands
  - [ ] `get_help(command)` - Lookup help content
  - [ ] `display_help(command)` - Render formatted help
  - [ ] `display_example(command, example_num)` - Show specific example

**Code Template**:
```python
@dataclass
class HelpContent:
    name: str
    description: str
    syntax: str
    options: List[str] = None
    examples: List[str] = None

class HelpSystem:
    def __init__(self, dispatcher, registry):
        self.dispatcher = dispatcher
        self.registry = registry
    
    def get_help(self, command: str) -> Optional[HelpContent]:
        """Get help for command."""
        cmd_upper = command.upper()
        handler = self.dispatcher.commands.get(cmd_upper)
        if not handler:
            return None
        
        meta = self.registry.get_metadata(cmd_upper)
        return HelpContent(
            name=cmd_upper,
            description=meta.description,
            syntax=meta.syntax,
            options=meta.options,
            examples=meta.examples,
        )
    
    def display_help(self, command: str):
        """Display formatted help panel."""
        content = self.get_help(command)
        if not content:
            print(f"No help for '{command}'")
            return
        
        # Render panel
        print("\n╔══════════════════════════════════╗")
        print(f"║  HELP: {content.name:26} ║")
        print("╠══════════════════════════════════╣")
        print(f"║  {content.description[:30]:30} ║")
        # ... etc
```

### 5.2 Update command handlers with help metadata

**Files**: `core/commands/*/handler.py` (all handlers)

**Subtasks**:
- [ ] Add `help_text` attribute to each handler class
- [ ] Add `syntax` attribute (command syntax)
- [ ] Add `options` list (command options with descriptions)
- [ ] Add `examples` list (usage examples)
- [ ] Example:
  ```python
  class StatusHandler(BaseCommandHandler):
      help_text = "Display system health and status"
      syntax = "STATUS [--detailed|--quick]"
      options = [
          "--detailed: Show all metrics",
          "--quick: Show summary only",
      ]
      examples = [
          "STATUS",
          "STATUS --detailed",
      ]
  ```

### 5.3 Implement HELP command

**File**: `core/commands/help_handler.py`

**Subtasks**:
- [ ] If no args: show all commands
- [ ] If command arg: show detailed help for that command
- [ ] Show examples with scrolling (if long)
- [ ] Test with various commands

---

## Integration Tests 🧪 Planning

### Test 1: Command Prompt with Suggestions
```
Steps:
  1. Start uDOS
  2. Type "ST" → should show STATUS, STOP, ... suggestions
  3. Press TAB → should open CommandSelector menu
  4. Press "1" → should select first command
  5. Verify command executes
```

### Test 2: Workspace Picker
```
Steps:
  1. Run "BINDER open"
  2. Should show workspace picker first
  3. Press "1" → select sandbox
  4. Should start FileBrowser in sandbox/
```

### Test 3: F-Key Navigation
```
Steps:
  1. Start uDOS
  2. Press F1 → HELP should display
  3. Press F2 → STATUS should run
  4. Press F4 → Workspace picker should open
  5. Press F6 → Wizard status should show
```

### Test 4: Help System
```
Steps:
  1. Run "HELP WIZARD"
  2. Should show:
     - Description
     - Syntax
     - Options list
     - Examples
  3. Verify scrolling works (if long)
```

### Test 5: Complete Flow
```
Steps:
  1. Start uDOS
  2. Press TAB → open command menu
  3. Type "WIZ" → filter to WIZARD
  4. Press Enter → execute WIZARD status
  5. Server status displays
  6. Press F5 → refresh status
  7. Test WIZARD start/stop
```

---

## Files to Create (Summary)

| File | Phase | Purpose |
|------|-------|---------|
| `core/input/command_prompt.py` | 1 | ContextualCommandPrompt class |
| `core/ui/workspace_selector.py` | 2 | WorkspacePicker class |
| `core/ui/command_selector.py` | 3 | CommandSelector modal menu |
| `core/config/keybindings.yaml` | 4 | F-key + shortcut bindings |
| `core/services/help_system.py` | 5 | HelpSystem service |
| `core/commands/command_registry.py` | 3 | CommandRegistry + metadata |

---

## Files to Update (Summary)

| File | Phase | Changes |
|------|-------|---------|
| `core/input/enhanced_prompt.py` | 1 | Complete 2-line context display |
| `core/tui/ucode.py` | 1,2,3,4 | Use ContextualCommandPrompt, TAB handler, F-keys, WorkspacePicker |
| `core/tui/file_browser.py` | 2 | Add WorkspacePicker header |
| `core/tui/status_bar.py` | 4 | Add F-key hints |
| `core/commands/*/handler.py` | 5 | Add help metadata (all handlers) |
| `extensions/api/routes/filepicker.py` | 2 | Link workspace selector |

---

## Success Metrics

- [ ] Command prompt shows suggestions while typing
- [ ] TAB opens scrollable command menu (50+ commands)
- [ ] Number keys (1-9) select items from menu
- [ ] Workspace picker shows before FileBrowser
- [ ] All F-keys (F1-F12) wired and working
- [ ] HELP command shows formatted, scrollable help
- [ ] No performance regression (<100ms per keystroke)
- [ ] Works keyboard-only (no mouse required)
- [ ] Parity with Vibe-CLI and Claude Code TUI

---

**Status**: 📋 Planning  
**Created**: 2026-01-30  
**Next Steps**: Start Phase 1 implementation
