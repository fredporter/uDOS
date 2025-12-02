# Command Migration Strategy - Round 3 Phase 2

## Overview

Migrate all uDOS commands from single-word (STATUS, HELP) to UPPERCASE-HYPHEN format (SYSTEM-STATUS, SYSTEM-HELP).

## Migration Principles

1. **Backward Compatibility (Temporary)**: Old names work as aliases during transition
2. **Clean Categories**: Group commands by functional area
3. **Remove Legacy**: Delete old command handlers after migration
4. **Update Docs**: Change all references to new names
5. **Test Coverage**: Ensure tests use new names

## Command Mapping

### System Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| STATUS | SYSTEM-STATUS | uDOS_commands.py |
| HELP | SYSTEM-HELP | uDOS_commands.py |
| EXIT | SYSTEM-EXIT | uDOS_commands.py |
| VERSION | SYSTEM-VERSION | uDOS_commands.py |
| CONFIG | SYSTEM-CONFIG | config_handler.py |
| LOG | SYSTEM-LOG | uDOS_commands.py |

### File Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| SAVE | FILE-SAVE | file_handler.py |
| LOAD | FILE-LOAD | file_handler.py |
| LIST | FILE-LIST | file_handler.py |
| INFO | FILE-INFO | file_handler.py |
| TREE | FILE-TREE | file_handler.py |

### Display Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| CLEAR | DISPLAY-CLEAR | uDOS_commands.py |
| THEME | DISPLAY-THEME | theme_loader.py |
| COLOR | DISPLAY-COLOR | uDOS_commands.py |

### Knowledge Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| SEARCH | KNOWLEDGE-SEARCH | knowledge_handler.py |
| READ | KNOWLEDGE-READ | knowledge_handler.py |
| GUIDE | KNOWLEDGE-GUIDE | knowledge_handler.py |
| INDEX | KNOWLEDGE-INDEX | knowledge_handler.py |

### Navigation Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| MAP | NAVIGATION-MAP | map_handler.py |
| GRID | NAVIGATION-GRID | grid_handler.py |
| LOCATION | NAVIGATION-LOCATION | location_handler.py |
| MOVE | NAVIGATION-MOVE | map_handler.py |

### Adventure Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| STORY | ADVENTURE-STORY | story_handler.py |
| SCENARIO | ADVENTURE-SCENARIO | game/scenario_engine.py |
| CHAPTER | ADVENTURE-CHAPTER | story_handler.py |

### Game Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| XP | GAME-XP | game/xp_manager.py |
| INVENTORY | GAME-INVENTORY | game/inventory_manager.py |
| STATS | GAME-STATS | game/sprite_manager.py |

### Content Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| GENERATE | CONTENT-GENERATE | generate_handler.py |

### Graphics Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| SVG | GRAPHICS-SVG | svg_handler.py |
| TELETEXT | GRAPHICS-TELETEXT | teletext_handler.py |
| CHART | GRAPHICS-CHART | chart_handler.py |

### Extension Commands
| Old Name | New Name | Handler File |
|----------|----------|--------------|
| EXTENSION | EXTENSION-MANAGER | extension_handler.py |
| EXT | EXTENSION-MANAGER | extension_handler.py (alias) |

## Migration Steps

### Step 1: Update Command Handlers
For each command handler file:
1. Import CommandRegistry
2. Use @register_command decorator
3. Update handler function names (system_status instead of handle_status)
4. Add old name as alias
5. Remove old command lookup code

### Step 2: Update CommandHandler (uDOS_commands.py)
1. Import get_registry()
2. Replace manual command lookup with registry.execute()
3. Remove old if/elif chains
4. Keep backward compatibility via aliases

### Step 3: Update Tests
1. Change test command names to UPPERCASE-HYPHEN
2. Add alias tests
3. Test registry integration

### Step 4: Clean Up Legacy Code
1. Remove old command handler registration
2. Remove manual command dispatching
3. Remove deprecated command names from docs
4. Clean up unused imports

## Example Migration

**Before:**
```python
def handle_status(args):
    \"\"\"Show system status\"\"\"
    return "System OK"

# In CommandHandler
if command == "STATUS":
    return handle_status(args)
```

**After:**
```python
from core.runtime import register_command, CommandCategory

@register_command(
    name="SYSTEM-STATUS",
    category=CommandCategory.SYSTEM,
    description="Show system status",
    aliases=["STATUS", "STAT"]  # Temporary backward compatibility
)
def system_status(args, context):
    \"\"\"Show system status\"\"\"
    return "System OK"

# In CommandHandler
def process_command(self, command, args):
    registry = get_registry()
    return registry.execute(command, args, context=self)
```

## Testing Strategy

1. **Unit Tests**: Test each command via registry
2. **Integration Tests**: Test command routing
3. **Alias Tests**: Verify old names still work
4. **Error Tests**: Invalid commands fail gracefully

## Rollout Plan

### Phase 2a: Core System Commands (2-3 hours)
- SYSTEM-* commands (6 commands)
- DISPLAY-* commands (3 commands)
- Update CommandHandler routing
- 10+ tests

### Phase 2b: File & Knowledge Commands (2-3 hours)
- FILE-* commands (5 commands)
- KNOWLEDGE-* commands (4 commands)
- Update handlers
- 8+ tests

### Phase 2c: Game & Extension Commands (2-3 hours)
- NAVIGATION-* commands (4 commands)
- ADVENTURE-* commands (3 commands)
- GAME-* commands (3 commands)
- CONTENT-* commands (1 command)
- GRAPHICS-* commands (3 commands)
- EXTENSION-* commands (1 command)
- Update all handlers
- 12+ tests

### Phase 2d: Cleanup (1-2 hours)
- Remove legacy command lookup code
- Remove unused handlers
- Update documentation references
- Final integration testing

## Success Criteria

- [ ] 25+ commands migrated to UPPERCASE-HYPHEN
- [ ] All commands registered in CommandRegistry
- [ ] Old names work as aliases
- [ ] CommandHandler uses registry.execute()
- [ ] 30+ tests passing
- [ ] Zero legacy command lookup code
- [ ] Documentation updated

## Files to Modify

**Core:**
- `core/uDOS_commands.py` (main dispatcher)
- `core/commands/*.py` (all handlers)
- `core/services/game/*.py` (game commands)

**Tests:**
- `memory/ucode/test_*.py` (update command names)

**Docs:**
- `wiki/Command-Reference.md`
- `README.MD`

## Files to Remove (Legacy Cleanup)

- None initially (keep for backward compatibility)
- Phase 3 will remove aliases after user migration period
