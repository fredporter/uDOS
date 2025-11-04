# Command Palette Guide

The uDOS Command Palette provides quick access to dashboard features through a modern, searchable interface while maintaining the system's retro aesthetic.

## Opening the Command Palette
- **Keyboard Shortcut**: `Cmd/Ctrl + K`
- **Close**: `Esc` key

## Features

### Fuzzy Search
The Command Palette uses fuzzy search to find commands, making it easy to quickly locate what you need:
- Type partial matches
- Case insensitive
- Matches across words
- Higher score for consecutive matches

### Command Categories

#### System Commands
- Toggle Theme - Switch between available themes
- Refresh Dashboard - Reload all dashboard data
- Open Settings - Configure dashboard settings

#### View Commands
- Show System Metrics - Display CPU, memory, and disk usage
- Show File Browser - Open the file browser interface
- Show Process List - View running processes
- Show Network Stats - View network statistics

#### File Operations
- Refresh Files - Reload file browser
- Go to Home - Navigate to home directory

#### Server Management
- Server Status - View all server statuses
- Start All Servers - Start all available servers
- Stop All Servers - Stop all running servers

## Keyboard Navigation
- `↑/↓` Arrow keys to navigate results
- `Enter` to execute selected command
- `Esc` to close palette

## Theme Integration
The Command Palette automatically adapts to the current theme:
- Retro theme colors
- C64-style typography
- Teletext-compatible display
- System 7 visual elements

## Technical Details

### Integration with Dashboard API
```javascript
// Access Command Palette through Dashboard API
window.dashboardAPI.commandPalette

// Register new command
dashboardAPI.commandPalette.registerCommand(
    'category',
    'Command Name',
    'Command Description',
    () => { /* action */ }
);
```

### Custom Command Registration
You can extend the Command Palette with custom commands:
```javascript
// Example: Register custom module command
dashboardAPI.commandPalette.registerCommand(
    'custom',
    'My Command',
    'Description of what the command does',
    () => console.log('Custom command executed')
);
```
