# Command Architecture

uDOS follows a modular command architecture that separates concerns and enables easy extension.

## Overview

The command system is built around specialized handler classes that process user input and execute appropriate functions.

## Core Components

### BaseCommandHandler
**Location**: `core/commands/base_handler.py`

All command handlers inherit from `BaseCommandHandler`, which provides:
- Common utilities and helper methods
- Message template system for consistent output
- Error handling and validation
- Grid integration for panel management

```python
class BaseCommandHandler:
    def __init__(self, **kwargs):
        self.workspace_manager = kwargs.get('workspace_manager')

    def handle(self, command, params, grid):
        """Override this method in subclasses"""
        raise NotImplementedError
```

### Command Handlers

#### SystemCommandHandler
**Location**: `core/commands/system_handler.py`
**Commands**: HELP, STATUS, REPAIR, REBOOT, DESTROY, PALETTE, TREE, DASHBOARD, CLEAN, CONFIG, SETTINGS, SETUP, WORKSPACE

Handles core system operations and diagnostics.

#### AssistantCommandHandler
**Location**: `core/commands/assistant_handler.py`
**Commands**: ASK, ANALYZE, EXPLAIN, GENERATE, DEBUG, CLEAR

Manages AI integration and assistant features.

#### FileCommandHandler
**Location**: `core/commands/file_handler.py`
**Commands**: LIST, VIEW, EDIT, CREATE, DELETE, COPY, MOVE, SEARCH, INFO, PERMISSIONS

Handles all file system operations.

#### MapCommandHandler
**Location**: `core/commands/map_handler.py`
**Commands**: STATUS, VIEW, CELL, CITIES, NAVIGATE, LOCATE, LAYERS, GOTO, TELETEXT, WEB

Manages navigation and geographical features.

#### ConfigurationCommandHandler
**Location**: `core/commands/configuration_handler.py`
**Commands**: GET, SET, LIST, RESET, BACKUP, RESTORE

Handles system configuration management.

#### GridCommandHandler
**Location**: `core/commands/grid_handler.py`
**Commands**: CREATE, SHOW, HIDE, MOVE, RESIZE, SPLIT, MERGE

Manages the grid panel system.

## Command Routing

### Primary Router
**Location**: `core/uDOS_commands.py`

The main command router determines which handler should process each command:

```python
def route_command(self, command_parts, grid):
    """Route commands to appropriate handlers."""
    if not command_parts:
        return "No command entered."

    primary_command = command_parts[0].upper()

    # Route to appropriate handler
    if primary_command in ['HELP', 'STATUS', 'REPAIR', ...]:
        return self.system_handler.handle(...)
    elif primary_command in ['ASK', 'ANALYZE', ...]:
        return self.assistant_handler.handle(...)
    # ... etc
```

### Subcommand Processing
Each handler processes subcommands internally:

```python
def handle(self, command, params, grid):
    """Handle MAP commands."""
    if command == "STATUS":
        return self._handle_status()
    elif command == "VIEW":
        return self._handle_view(params, grid)
    # ... etc
```

## Message System

### Templates
**Location**: `core/commands/base_handler.py`

Handlers use a template system for consistent messaging:

```python
def get_message(self, template_key, **kwargs):
    """Get formatted message from template."""
    templates = {
        'ERROR_FILE_NOT_FOUND': "❌ File not found: {filename}",
        'SUCCESS_FILE_CREATED': "✅ Created: {filename}",
        # ... etc
    }
    return templates.get(template_key, "Unknown message").format(**kwargs)
```

### Error Handling
Standard error patterns across all handlers:
- Input validation with helpful error messages
- Graceful degradation when services unavailable
- Consistent error formatting and symbols

## Integration Points

### Grid System
**Location**: `core/uDOS_grid.py`

Commands interact with the grid system for:
- Panel creation and management
- Content display and formatting
- Multi-panel operations

```python
# Create panel with content
grid.create_panel('file_content', content, 0, 0, 40, 20)

# Get panel content for context
content = grid.get_panel('main')
```

### Service Integration
Commands integrate with core services:

```python
# Example: File handler using multiple services
from core.services.file_picker import FilePicker
from core.services.git_integration import GitService
from core.services.enhanced_history import HistoryService

class FileCommandHandler(BaseCommandHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_picker = FilePicker()
        self.git_service = GitService()
        self.history = HistoryService()
```

## Extension Pattern

### Adding New Commands
1. Create handler class inheriting from `BaseCommandHandler`
2. Implement `handle()` method with command routing
3. Register handler in main command router
4. Add command documentation

### Adding Subcommands
1. Add subcommand to existing handler's `handle()` method
2. Implement private `_handle_subcommand()` method
3. Update help text and documentation

## Best Practices

### Handler Design
- **Single Responsibility**: Each handler manages one domain
- **Consistent Interface**: All handlers follow same patterns
- **Error Handling**: Graceful error messages and recovery
- **Documentation**: Clear docstrings and examples

### Command Design
- **Intuitive Names**: Commands should be self-explanatory
- **Consistent Parameters**: Similar operations use similar syntax
- **Help Integration**: All commands appear in help system
- **Examples**: Provide usage examples in documentation

### Testing
- **Unit Tests**: Test individual command handlers
- **Integration Tests**: Test command routing and interaction
- **Error Cases**: Test invalid input and edge cases
- **Performance**: Test with large inputs and stress scenarios

## Performance Considerations

### Lazy Loading
Services are loaded only when needed:

```python
@property
def map_engine(self):
    """Lazy load mapping engine."""
    if self._map_engine is None:
        from core.services.map_engine import MapEngine
        self._map_engine = MapEngine()
    return self._map_engine
```

### Caching
Expensive operations are cached:
- File system scans
- Database queries
- API responses
- Computed results

### Resource Management
- Services are properly initialized and cleaned up
- Database connections are managed efficiently
- Memory usage is monitored and optimized

## Future Extensions

### Plugin Architecture
Planned features for community extensions:
- External handler registration
- API for third-party commands
- Sandboxed execution environment
- Extension marketplace

### Advanced Routing
Future enhancements:
- Dynamic command discovery
- Context-aware routing
- Command aliases and shortcuts
- Natural language processing

## Tags
#architecture #commands #handlers #routing #design #patterns #integration
