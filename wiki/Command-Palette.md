# Command Palette

The Command Palette is a powerful feature in uDOS that provides quick access to all dashboard functionality through a modern, searchable interface while maintaining the system's retro aesthetic.

## Overview

The Command Palette combines modern usability with uDOS's retro styling:
- Fuzzy search for quick command access
- Keyboard-centric navigation
- Theme-aware styling
- Categorized commands
- Extensible command system

## Usage

### Basic Operations

1. **Opening the Palette**
   - Press `Cmd/Ctrl + K`
   - The palette appears with a search input

2. **Finding Commands**
   - Start typing to search
   - Results update in real-time
   - Fuzzy matching helps find commands quickly

3. **Executing Commands**
   - Use arrow keys to select
   - Press `Enter` to execute
   - Press `Esc` to cancel

### Command Categories

The Command Palette organizes commands into intuitive categories:

- **System**: Core dashboard operations
- **View**: Navigation and display options
- **Files**: File system operations
- **Server**: Server management commands

## Technical Implementation

### Architecture

The Command Palette is implemented as a core dashboard service:

```javascript
class CommandPalette {
    constructor() {
        this.commands = new Map();
        this.categories = new Set();
        // ...
    }

    // Command registration
    registerCommand(category, name, description, action) {
        this.commands.set(name, { category, description, action });
        this.categories.add(category);
    }

    // Fuzzy search implementation
    search(query) {
        // Intelligent fuzzy matching
    }
}
```

### Integration

The Command Palette integrates with:
- Dashboard API for core functionality
- Theme system for consistent styling
- Module system for extensibility
- Socket.IO for real-time updates

## Customization

### Adding Custom Commands

Modules can register custom commands:

```javascript
// Register a custom command
dashboardAPI.commandPalette.registerCommand(
    'category',    // Command category
    'name',        // Command name
    'description', // Command description
    () => {        // Command action
        // Implementation
    }
);
```

### Styling

The Command Palette respects the current theme:
- Uses theme CSS variables
- Adapts to C64/Teletext/System 7 styles
- Maintains consistent typography

## Best Practices

1. **Command Names**
   - Use clear, descriptive names
   - Follow existing naming patterns
   - Include relevant keywords

2. **Categories**
   - Use existing categories when possible
   - Create new categories sparingly
   - Keep categories logical and focused

3. **Descriptions**
   - Be clear and concise
   - Include key functionality
   - Mention important side effects

## Future Development

Planned enhancements:
- Command history tracking
- Custom keybinding support
- Command aliases
- Context-aware suggestions
- Advanced filtering options
