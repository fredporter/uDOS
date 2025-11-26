# Micro Editor Usage in uDOS v1.0.31

## Two "Micro" Editors - Clarification

uDOS uses TWO different editors both called "micro":

### 1. Built-in MicroEditor (Primary - Python)
**Location**: `core/ui/micro_editor.py`
**Type**: Python class (372 lines)
**Usage**: Default for `FILE EDIT` and `FILE VIEW` commands
**Features**:
- Lightweight terminal-based editor
- Line-by-line navigation
- Basic syntax highlighting for .md and .uscript files
- Read-only mode for VIEW
- No external dependencies
- Integrated directly into uDOS sessions

**Commands**:
- `FILE EDIT` → Uses MicroEditor by default
- `FILE VIEW` → Uses MicroEditor in read-only mode
- `FILE EDIT --external` → Falls back to system editor

**Version**: v1.0.30 (introduced)

### 2. External Micro Editor (Optional - Go Binary)
**Location**: `extensions/cloned/micro/` (zyedidia/micro)
**Type**: Go binary
**Repository**: https://github.com/zyedidia/micro
**Installation**: Via `editor_manager.install_micro()`
**Usage**: Can be selected as CLI editor preference
**Features**:
- Full-featured terminal editor
- Multiple cursors
- Plugin system
- Syntax highlighting for 130+ languages
- Mouse support
- Persistent undo

**Status**: OPTIONAL - Only needed if user explicitly wants the advanced external editor

## Current Default Behavior (v1.0.30+)

1. `FILE EDIT <file>` → Opens in built-in MicroEditor (Python)
2. `FILE VIEW <file>` → Opens in built-in MicroEditor read-only
3. `FILE EDIT <file> --external` → Opens in external editor (nano/vim/micro binary)

## Recommendation

**Keep both**:
- Built-in MicroEditor: Core functionality, no dependencies, works everywhere
- External micro binary: Advanced users who want full IDE-like features

The external binary in `extensions/cloned/micro/` is part of the cloned repository for reference and can be optionally installed by EditorManager but is NOT used by default.

## Code References

- **Built-in usage**: `core/commands/file_handler.py` lines 391, 450
- **External management**: `core/services/editor_manager.py` lines 45, 150, 179-280
- **Editor class**: `core/ui/micro_editor.py`
