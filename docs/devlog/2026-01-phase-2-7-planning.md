# Phase 2.7 Planning: CLI Command Integration

**Status:** Planning  
**Duration:** ~2-3 hours  
**Predecessor:** Phase 2.6 (Plugin Discovery - Complete ✅)  
**Target:** Implement PLUGIN commands for interactive plugin management

---

## Overview

Phase 2.7 integrates the PluginDiscovery system into the uDOS command infrastructure, enabling users to:

1. **PLUGIN SCAN** - Discover and catalog all plugins
2. **PLUGIN LIST** - List plugins with filtering
3. **PLUGIN INFO** - Show detailed plugin information
4. **PLUGIN DEPS** - Show plugin dependencies
5. **PLUGIN VALIDATE** - Check dependency integrity

---

## Implementation Roadmap

### Task 1: Create PluginHandler (80-100 lines)

**File:** `core/commands/plugin_handler.py`

**Purpose:** Route plugin-related commands to PluginDiscovery

**Structure:**
```python
class PluginHandler(BaseCommandHandler):
    def __init__(self, parser, grid):
        # ...
        self.discovery = PluginDiscovery()
    
    def handle(self, command, params, grid, parser):
        if command == "SCAN": return self._handle_scan(params)
        elif command == "LIST": return self._handle_list(params)
        elif command == "INFO": return self._handle_info(params)
        elif command == "DEPS": return self._handle_deps(params)
        elif command == "VALIDATE": return self._handle_validate(params)
    
    def _handle_scan(self, params):
        """PLUGIN SCAN - Discover all plugins"""
        # Call discovery.discover_all()
        # Display registry
        # Save to memory/plugin-registry.json
        
    def _handle_list(self, params):
        """PLUGIN LIST [--tier ucode|wizard|experimental] [--type api|transport|...]"""
        # Parse tier and type filters
        # Call discovery.list_plugins()
        # Format and display
        
    def _handle_info(self, params):
        """PLUGIN INFO <name>"""
        # Get plugin by name
        # Display details (version, deps, author, etc)
        
    def _handle_deps(self, params):
        """PLUGIN DEPS <name> [--recursive]"""
        # Show dependencies (forward and reverse)
        # Display dependency graph
        
    def _handle_validate(self, params):
        """PLUGIN VALIDATE"""
        # Check all dependencies
        # Report missing/broken
        # Suggest fixes
```

**Key Features:**
- ✅ Tight integration with PluginDiscovery
- ✅ Proper error handling
- ✅ Logging with [WIZ] tags
- ✅ Rich output formatting

---

### Task 2: Register with uDOS_commands (20-30 lines)

**File:** `core/uDOS_commands.py`

**Changes:**
```python
from core.commands.plugin_handler import PluginHandler

# In CommandRouter.__init__():
self.plugin_handler = PluginHandler(parser, grid)

# In CommandRouter.route():
if command in ["PLUGIN"]:
    return self.plugin_handler.handle(subcommand, params, grid, parser)
```

---

### Task 3: Create Comprehensive Tests (150-200 lines)

**File:** `core/tests/test_plugin_handler.py`

**Test Classes:**
```python
class TestPluginHandler:
    def test_plugin_scan(self):
        # Mock discovery
        # Verify scan output
        # Check registry saved
        
    def test_plugin_list_all(self):
        # List all plugins
        
    def test_plugin_list_by_tier(self):
        # Filter by tier
        
    def test_plugin_list_by_type(self):
        # Filter by type
        
    def test_plugin_info(self):
        # Show plugin details
        
    def test_plugin_deps_forward(self):
        # Show forward dependencies
        
    def test_plugin_deps_reverse(self):
        # Show who depends on me
        
    def test_plugin_validate_ok(self):
        # All deps satisfied
        
    def test_plugin_validate_missing(self):
        # Report missing deps
        
    def test_help_text(self):
        # PLUGIN HELP output
```

---

### Task 4: Add Help Documentation (100+ lines)

**File:** `core/data/help/plugin.md`

**Content:**
```markdown
# PLUGIN Commands

## Overview
Manage and discover available plugins for uDOS.

## Syntax

### PLUGIN SCAN
Discover all plugins and build registry.

Usage: PLUGIN SCAN [--save <path>]

Example:
  PLUGIN SCAN
  PLUGIN SCAN --save memory/custom-registry.json

### PLUGIN LIST
List all plugins with optional filtering.

Usage: PLUGIN LIST [--tier ucode|wizard|experimental] [--type api|transport|library|extension] [--active]

Examples:
  PLUGIN LIST                                    # All plugins
  PLUGIN LIST --tier ucode                       # Shipping only
  PLUGIN LIST --type api                         # API plugins only
  PLUGIN LIST --tier wizard --active             # Active wizard plugins

### PLUGIN INFO
Show detailed information about a plugin.

Usage: PLUGIN INFO <name>

Example:
  PLUGIN INFO api
  PLUGIN INFO meshcore

Output:
  Name: api
  Type: api
  Tier: ucode
  Version: 1.1.0
  Status: ✅ Active
  Author: uDOS
  Homepage: https://github.com/uDOS/core
  Path: /absolute/path/plugins/api
  
  Description:
  REST/WebSocket API server for uDOS
  
  Dependencies:
  - core (≥1.0.0)
  - transport (≥1.0.0)
  
  Dependents:
  - (none)

### PLUGIN DEPS
Show plugin dependencies.

Usage: PLUGIN DEPS <name> [--recursive] [--reverse]

Examples:
  PLUGIN DEPS api                    # Direct dependencies
  PLUGIN DEPS api --recursive        # All transitive deps
  PLUGIN DEPS api --reverse          # What depends on api
  
Output:
  Dependencies of 'api':
  ├─ core (≥1.0.0)
  ├─ transport (≥1.0.0)
  └─ ... (5 total)

### PLUGIN VALIDATE
Validate all plugin dependencies.

Usage: PLUGIN VALIDATE [--fix]

Example:
  PLUGIN VALIDATE
  PLUGIN VALIDATE --fix              # Attempt to fix

Output:
  Validating 13 plugins...
  
  ✅ All dependencies satisfied
  
  Summary:
  - 13 plugins checked
  - 0 missing dependencies
  - 0 version conflicts
```

---

## Dependency Graph Example

```
wizardcore
├── api
│   ├── core
│   │   ├── transport
│   │   └── meshcore
│   └── transport
│       ├── meshcore
│       └── audio
└── wizard
    ├── core
    └── transport

api → core, transport
core → transport, meshcore
transport → meshcore, audio
meshcore → (none)
audio → (none)
wizard → core, transport
```

---

## Integration with REPAIR

**Proposed:** REPAIR auto-discovers plugins after sync

```python
# In RepairHandler._handle_full_repair():
if options.includes.get('plugins'):
    logger.info('[WIZ] Discovering plugins after sync...')
    discovery = PluginDiscovery()
    plugins = discovery.discover_all()
    discovery.save_registry()
    logger.info(f'[WIZ] Found {len(plugins)} plugins')
    
    # Validate dependencies
    missing = discovery.validate_dependencies()
    if missing:
        logger.warning(f'[WIZ] Missing dependencies: {missing}')
```

---

## Integration with Dashboard API

**Proposed:** REST endpoint for plugin registry

```python
# In extensions/api/routes/plugins.py
@app.get("/api/plugins")
def list_plugins(tier=None, type=None, active_only=True):
    """List plugins with optional filters"""
    # Uses PluginDiscovery
    # Returns JSON

@app.get("/api/plugins/<name>")
def get_plugin(name):
    """Get single plugin details"""

@app.get("/api/plugins/<name>/deps")
def get_dependencies(name, recursive=False):
    """Get plugin dependencies"""

@app.post("/api/plugins/validate")
def validate():
    """Validate all dependencies"""
```

---

## Acceptance Criteria

✅ **Implementation Complete When:**

1. [ ] PluginHandler class created and tested
2. [ ] All 5 commands functional (SCAN, LIST, INFO, DEPS, VALIDATE)
3. [ ] Help documentation complete
4. [ ] Command registered in uDOS_commands.py
5. [ ] All tests passing (15+ tests)
6. [ ] Logging uses [WIZ] tags
7. [ ] Error handling robust
8. [ ] Output formatted nicely (tables, dependency graphs)
9. [ ] Works with both Wizard and experimental plugins
10. [ ] Documentation in QUICK-REFERENCE.md

---

## Code Patterns

### Error Handling

```python
def _handle_info(self, params):
    if not params or len(params) < 1:
        return Result(False, "❌ PLUGIN INFO requires a plugin name\n"
                             "Usage: PLUGIN INFO <name>\n"
                             "Example: PLUGIN INFO api")
    
    plugin_name = params[0]
    plugin = self.discovery.get_plugin(plugin_name)
    
    if not plugin:
        return Result(False, f"❌ Plugin '{plugin_name}' not found")
    
    # Display info...
    return Result(True, formatted_output)
```

### Logging

```python
logger.info(f"[WIZ] Plugin scan initiated by user")
logger.debug(f"[WIZ] Discovered {len(plugins)} plugins")
logger.warning(f"[WIZ] Plugin 'foo' missing dependency 'bar'")
```

### Output Formatting

```python
def _format_plugin_info(self, plugin):
    """Format plugin info as readable text"""
    lines = [
        f"📦 {plugin.name.upper()}",
        f"Type: {plugin.type:15s}  Tier: {plugin.tier}",
        f"Version: {plugin.version:13s}  Status: {'✅ Active' if plugin.active else '⚠️  Inactive'}",
        f"",
        f"Description:",
        f"  {plugin.description}",
        f"",
        f"Author: {plugin.author}",
        f"Homepage: {plugin.homepage}",
        f"Path: {plugin.path}",
    ]
    
    if plugin.dependencies:
        lines.append("")
        lines.append("Dependencies:")
        for dep in plugin.dependencies:
            lines.append(f"  - {dep}")
    
    return "\n".join(lines)
```

---

## Testing Strategy

**Unit Tests:** Test each command in isolation with mocks
**Integration Tests:** Test with real PluginDiscovery instance
**Edge Cases:** Missing plugins, circular dependencies, invalid parameters

---

## Success Metrics

- ✅ All 51 previous tests still passing
- ✅ 15+ new tests for PluginHandler
- ✅ 100% test pass rate
- ✅ Complete help documentation
- ✅ Clean integration with existing command infrastructure
- ✅ Rich, user-friendly output

---

## Files to Modify/Create

| File | Action | Size | Priority |
|------|--------|------|----------|
| core/commands/plugin_handler.py | CREATE | 150-200 lines | 🔴 HIGH |
| core/uDOS_commands.py | MODIFY | +20 lines | 🔴 HIGH |
| core/tests/test_plugin_handler.py | CREATE | 150-200 lines | 🔴 HIGH |
| core/data/help/plugin.md | CREATE | 150+ lines | 🟡 MEDIUM |
| QUICK-REFERENCE.md | MODIFY | +50 lines | 🟡 MEDIUM |

---

## Estimated Timeline

| Task | Duration | Notes |
|------|----------|-------|
| PluginHandler implementation | 60 minutes | Main code |
| uDOS_commands integration | 15 minutes | Simple registration |
| Test suite | 45 minutes | 15+ tests |
| Help documentation | 30 minutes | Comprehensive |
| Testing & debugging | 30 minutes | Edge cases |
| **Total** | **2.5 hours** | Ready for Phase 2.8 |

---

## Next: Phase 2.8 (CI/CD Pipeline)

After Phase 2.7 is complete, Phase 2.8 will automate:
- Build orchestration
- Test execution
- Release publishing
- Artifact management

See [roadmap.md](../roadmap.md) for details.

---

*Planning Complete — Ready to Implement Phase 2.7*  
*Last Updated: 2026-01-14*
