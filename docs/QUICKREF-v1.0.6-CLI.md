# uDOS v1.0.6 CLI Quick Reference Guide

## 🚀 Quick Start

### Essential Commands
```bash
# Enhanced History
HISTORY LIST              # Show recent commands
HISTORY SEARCH <term>     # Search command history

# Smart Tab Completion
<TAB>                     # Context-aware suggestions
<Command><TAB>            # Parameter completion

# Theme Management  
THEME LIST                # Available themes
THEME SET <name>          # Switch theme

# Session Management
SESSION SAVE              # Save current workspace
SESSION LIST              # Show all sessions
SESSION LOAD <id>         # Restore session

# Progress & Layout
PROGRESS TEST             # Test progress indicators
LAYOUT INFO               # Current layout info
```

## 📋 Command Reference

### HISTORY Commands
| Command | Description | Example |
|---------|-------------|---------|
| `HISTORY LIST [count]` | Show recent commands | `HISTORY LIST 10` |
| `HISTORY SEARCH <term>` | Fuzzy search history | `HISTORY SEARCH file` |
| `HISTORY STATS` | Usage statistics | `HISTORY STATS` |
| `HISTORY CLEAR` | Clear all history | `HISTORY CLEAR` |
| `HISTORY EXPORT <file>` | Export to JSON | `HISTORY EXPORT backup.json` |

### THEME Commands
| Command | Description | Example |
|---------|-------------|---------|
| `THEME LIST` | Available themes | `THEME LIST` |
| `THEME SET <name>` | Switch theme | `THEME SET cyberpunk` |
| `THEME INFO` | Current theme info | `THEME INFO` |
| `THEME ACCESSIBILITY ON\|OFF` | Toggle accessibility | `THEME ACCESSIBILITY ON` |
| `THEME CONTRAST ON\|OFF` | High contrast mode | `THEME CONTRAST ON` |
| `THEME COLORBLIND <type>` | Colorblind support | `THEME COLORBLIND deuteranopia` |

### SESSION Commands
| Command | Description | Example |
|---------|-------------|---------|
| `SESSION LIST` | List all sessions | `SESSION LIST` |
| `SESSION SAVE [name] [desc]` | Save current state | `SESSION SAVE work "Dev session"` |
| `SESSION LOAD <id>` | Restore session | `SESSION LOAD 1` |
| `SESSION DELETE <id>` | Delete session | `SESSION DELETE 2` |
| `SESSION CURRENT` | Current session info | `SESSION CURRENT` |
| `SESSION AUTO ON\|OFF` | Toggle auto-save | `SESSION AUTO ON` |
| `SESSION CHECKPOINT [desc]` | Create checkpoint | `SESSION CHECKPOINT "Before merge"` |

### PROGRESS Commands  
| Command | Description | Example |
|---------|-------------|---------|
| `PROGRESS TEST` | Basic progress test | `PROGRESS TEST` |
| `PROGRESS TEST MULTI` | Multi-stage test | `PROGRESS TEST MULTI` |
| `PROGRESS LIST` | Active indicators | `PROGRESS LIST` |
| `PROGRESS CANCEL [id]` | Cancel progress | `PROGRESS CANCEL 1` |
| `PROGRESS DEMO` | Full demonstration | `PROGRESS DEMO` |

### LAYOUT Commands
| Command | Description | Example |
|---------|-------------|---------|
| `LAYOUT INFO` | Current layout info | `LAYOUT INFO` |
| `LAYOUT MODE <mode>` | Set layout mode | `LAYOUT MODE compact` |
| `LAYOUT RESIZE` | Force resize detection | `LAYOUT RESIZE` |
| `LAYOUT AUTO ON\|OFF` | Auto-resize toggle | `LAYOUT AUTO ON` |
| `LAYOUT TEST` | Test formatting | `LAYOUT TEST` |

## 🎨 Available Themes

### Built-in Themes
- **classic** - Traditional terminal colors
- **cyberpunk** - Neon-inspired futuristic theme  
- **accessibility** - High contrast, accessible colors
- **monochrome** - Black and white compatibility

### Accessibility Options
- **High Contrast** - Enhanced visibility
- **Colorblind Support** - deuteranopia, protanopia, tritanopia
- **Screen Reader** - Optimized for assistive technology

## 📱 Layout Modes

### Available Modes
- **compact** - Mobile/small screen optimized
- **standard** - Default balanced layout
- **expanded** - Wide screen with extra details
- **split** - Two-panel layout for large screens
- **dashboard** - Information-dense overview

### Auto-Resize
- Automatically adapts to terminal size changes
- Mobile-friendly responsive design
- Wide-screen enhancements

## ⌨️ Tab Completion Features

### Smart Completion
- **Fuzzy matching** - Type partial commands
- **Context awareness** - Parameter suggestions
- **History integration** - Recent command priority
- **File path completion** - Workspace-aware

### Examples
```bash
THM<TAB>          # Expands to THEME
THEME S<TAB>      # Suggests SET
FILE SEARCH *.p<TAB>  # Completes to *.py
```

## 💾 Session Types

### Session Categories
- **Manual** - User-created sessions
- **Automatic** - Auto-saved at intervals
- **Checkpoint** - Milestone markers
- **Backup** - Safety snapshots

### What's Saved
- Command history
- Current working directory
- Active files and bookmarks
- Theme and layout settings
- Environment variables

## 📊 Progress Indicator Types

### Indicator Styles
- **Determinate** - Known progress (0-100%)
- **Indeterminate** - Unknown duration spinner
- **Multi-stage** - Multiple phases
- **Parallel** - Multiple simultaneous operations

### Integration
- Automatic with `FILE SEARCH`
- Background processing support
- Cancellation with Ctrl+C
- Time estimation

## 🔍 History Search Features

### Search Types
- **Fuzzy matching** - Find similar commands
- **Exact matching** - Precise command lookup
- **Pattern matching** - Regular expressions
- **Frequency ranking** - Most-used commands first

### Search Examples
```bash
HISTORY SEARCH git        # Find git commands
HISTORY SEARCH "file.*py" # Pattern matching
HISTORY SEARCH MAP        # Map-related commands
```

## ⚡ Performance Tips

### Optimization
- Use `SESSION AUTO ON` for automatic saves
- Enable `LAYOUT AUTO ON` for responsive design
- Use fuzzy completion for faster command entry
- Leverage history search for command discovery

### Memory Management
- History automatically deduplicates
- Old sessions cleaned up automatically
- Progress indicators auto-cleanup
- Layout calculations cached

## 🚨 Troubleshooting

### Common Issues
1. **Slow completion** - Clear history: `HISTORY CLEAR`
2. **Wrong theme colors** - Reset: `THEME SET classic`
3. **Session not saving** - Check: `SESSION CURRENT`
4. **Layout issues** - Force resize: `LAYOUT RESIZE`

### Diagnostic Commands
```bash
HISTORY STATS     # Check history performance
THEME INFO        # Verify theme state
SESSION CURRENT   # Check session status
LAYOUT INFO       # Verify layout settings
PROGRESS LIST     # Check active indicators
```

## 🎯 Best Practices

### Workflow Optimization
1. **Start sessions** - `SESSION AUTO ON` for safety
2. **Use themes** - Match environment (dark/light/accessibility)
3. **Leverage completion** - Tab for faster command entry
4. **Search history** - Find previous solutions quickly
5. **Monitor progress** - Long operations show indicators

### Accessibility
1. **Enable accessibility mode** - `THEME ACCESSIBILITY ON`
2. **Use high contrast** - `THEME CONTRAST ON`
3. **Set colorblind support** - `THEME COLORBLIND <type>`
4. **Compact layouts** - `LAYOUT MODE compact` for mobile

### Power User Tips
1. **Checkpoint frequently** - `SESSION CHECKPOINT "desc"`
2. **Export sessions** - Share configurations
3. **Use split layouts** - `LAYOUT MODE split` for wide screens
4. **Monitor stats** - `HISTORY STATS` for usage insights

---

## 🆘 Quick Help

| Need | Command |
|------|---------|
| Recent commands | `HISTORY LIST` |
| Search history | `HISTORY SEARCH <term>` |
| Change theme | `THEME SET <name>` |
| Save work | `SESSION SAVE` |
| Test progress | `PROGRESS TEST` |
| Check layout | `LAYOUT INFO` |
| Get help | `HELP <command>` |

**Remember:** All commands support tab completion and fuzzy matching!