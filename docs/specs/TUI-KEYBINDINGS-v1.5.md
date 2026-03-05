# uDOS TUI Interaction Principles

Hotkeys, Shortcuts and Navigation

Updated: 2026-03-05
Status: canonical v1.5 keybinding contract

## Design Goals

The uDOS interface must feel:

- predictable
- muscle-memory friendly
- safe for paste
- usable entirely without a mouse
- consistent across every screen

Every control shares the same navigation and editing model.
Users should not need to relearn controls between screens.

## Global Interaction Model

These shortcuts work everywhere unless explicitly overridden.

| Key | Action |
|---|---|
| `Ctrl+C` | Immediate exit |
| `Esc` | Cancel or go back |
| `Enter` | Confirm or execute |
| `Tab` | Next field or pane |
| `Shift+Tab` | Previous field or pane |
| `Ctrl+L` | Redraw screen |
| `?` | Toggle help overlay |
| `:` | Command palette |
| `/` | Search or filter |

These keys must keep consistent meaning across the interface.

## Navigation Controls

All lists, menus, and selectors use the same keys.

| Key | Action |
|---|---|
| `↑ ↓` | Move selection |
| `← →` | Change column or level |
| `Home` | Jump to start |
| `End` | Jump to end |
| `PgUp` | Page up |
| `PgDn` | Page down |

Optional power-user keys:

| Key | Action |
|---|---|
| `j k` | Move selection |
| `h l` | Move column |

## Selection Controls

Single selection:

| Key | Action |
|---|---|
| `Enter` | Select item |
| `Esc` | Cancel selection |

Multi selection:

| Key | Action |
|---|---|
| `Space` | Toggle item |
| `Enter` | Confirm selection |
| `a` | Select all |
| `x` | Clear selection |

## Search and Filter

Any list can be filtered.

| Key | Action |
|---|---|
| `/` | Enter filter mode |
| `Enter` | Apply filter |
| `Esc` | Clear filter |

Search navigation:

| Key | Action |
|---|---|
| `n` | Next result |
| `N` | Previous result |

## Text Input Controls

Inputs behave like a Unix shell.

| Key | Action |
|---|---|
| `Ctrl+A` | Start of line |
| `Ctrl+E` | End of line |
| `Ctrl+U` | Delete line |
| `Ctrl+W` | Delete word |
| `Ctrl+K` | Delete to end |
| `Ctrl+Y` | Paste buffer |
| `Ctrl+D` | Delete char |

Standard input keys:

| Key | Action |
|---|---|
| `Enter` | Submit input |
| `Esc` | Cancel |

## Copy and Paste Safety

The interface must never break when users paste content.

uDOS uses bracketed paste mode:

- paste start: `\x1b[200~`
- paste end: `\x1b[201~`

Behavior rules:

- pasted content is inserted atomically
- keybindings are disabled during paste
- newline handling depends on field type

Single-line inputs:

- newline becomes space, or triggers validation warning

Multi-line inputs:

- newline preserved
- indentation preserved

## Command Palette

Open command palette with `:`.

Palette features:

- fuzzy search
- command preview
- hotkey hints

Example commands:

- `:install`
- `:scaffold`
- `:run`
- `:logs`
- `:extensions`

## Teletext Function Keys

Reserved system actions:

| Key | Action |
|---|---|
| `F1` | Help |
| `F2` | System status |
| `F3` | Logs |
| `F4` | Extensions |
| `F5` | Refresh |
| `F6` | Toggle panels |
| `F7` | Missions |
| `F8` | Environment |
| `F9` | Settings |
| `F10` | Exit |

## Wizard Mode Shortcuts

Unlocked at Wizard rank:

| Key | Action |
|---|---|
| `Ctrl+R` | Re-run task |
| `Ctrl+P` | Project switcher |
| `Ctrl+T` | Task runner |
| `Ctrl+O` | Object explorer |
| `Ctrl+G` | Generate scaffold |

## Visual Feedback Rules

Every key interaction must produce visible feedback:

- selection highlight
- progress spinner
- inline validation message
- status bar update

No silent actions.

## Help Overlay

Press `?` to reveal:

```text
┌─────────────────────────────────┐
│ uDOS Navigation                 │
│                                 │
│ ↑↓   Move selection             │
│ Enter Select                    │
│ Esc   Back                      │
│ /     Filter                    │
│ :     Command palette           │
│ Ctrl+C Exit                     │
└─────────────────────────────────┘
```

## Principle Summary

1. Consistency: every control behaves the same way.
2. Predictability: keys follow Unix, Vim, and terminal conventions.
3. Safety: paste must never break the interface.
4. Speed: experts can navigate entirely by keyboard.
