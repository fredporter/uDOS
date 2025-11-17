# API Reference - v1.0.23

**uDOS Command Consolidation & Smart Input API Documentation**
**Version**: v1.0.23
**Last Updated**: November 17, 2025

---

## Table of Contents

1. [Unified Handlers](#unified-handlers)
2. [Smart Input System](#smart-input-system)
3. [UI Components](#ui-components)
4. [Performance System](#performance-system)
5. [Error Handling](#error-handling)
6. [Data Structures](#data-structures)

---

## Unified Handlers

### DocsUnifiedHandler

**Location**: `core/services/docs_unified_handler.py`

#### Methods

##### `handle(args: dict) -> dict`
Main entry point for documentation access.

**Parameters**:
- `args` (dict): Command arguments
  - `query` (str, optional): Search query
  - `manual` (str, optional): Manual page name
  - `handbook` (str, optional): Handbook volume
  - `example` (str, optional): Example name
  - `search` (str, optional): Search string

**Returns**: dict
- `success` (bool): Operation success status
- `content` (str): Formatted documentation content
- `source` (str): Source type (manual/handbook/doc/example)
- `relevance` (float): Relevance score (0-1)

**Example**:
```python
from core.services.docs_unified_handler import DocsUnifiedHandler

handler = DocsUnifiedHandler()
result = handler.handle({'query': 'git'})
print(result['content'])
```

##### `search_all(query: str) -> list[dict]`
Search across all documentation sources.

**Parameters**:
- `query` (str): Search query

**Returns**: list[dict]
- Each item contains: `source`, `title`, `content`, `relevance`

**Example**:
```python
results = handler.search_all('water purification')
for result in results:
    print(f"{result['source']}: {result['title']} ({result['relevance']:.2f})")
```

##### `get_manual(name: str) -> dict`
Retrieve command manual.

**Parameters**:
- `name` (str): Command name

**Returns**: dict
- `success` (bool)
- `content` (str): Manual content
- `command` (str): Canonical command name

---

### LearnUnifiedHandler

**Location**: `core/services/learn_unified_handler.py`

#### Methods

##### `handle(args: dict) -> dict`
Main entry point for learning content.

**Parameters**:
- `args` (dict): Command arguments
  - `query` (str, optional): Content name or query
  - `list` (bool, optional): List all content
  - `list_guides` (bool, optional): List guides only
  - `list_diagrams` (bool, optional): List diagrams only
  - `continue` (bool, optional): Continue last session

**Returns**: dict
- `success` (bool)
- `content` (str): Learning content
- `type` (str): Content type (guide/diagram/tutorial)
- `progress` (float, optional): Progress percentage

**Example**:
```python
from core.services.learn_unified_handler import LearnUnifiedHandler

handler = LearnUnifiedHandler()
result = handler.handle({'query': 'water-purification'})
print(result['content'])
```

##### `detect_content_type(name: str) -> str`
Auto-detect content type from name/path.

**Parameters**:
- `name` (str): Content name or path

**Returns**: str - Content type ('guide', 'diagram', 'tutorial', or 'unknown')

**Example**:
```python
content_type = handler.detect_content_type('water-purification')
# Returns: 'guide' or 'diagram' based on file location
```

---

### MemoryUnifiedHandler

**Location**: `core/services/memory_unified_handler.py`

#### Methods

##### `handle(args: dict) -> dict`
Main entry point for memory operations.

**Parameters**:
- `args` (dict): Command arguments
  - `query` (str, optional): Search query
  - `tier` (str, optional): Memory tier (private/shared/community/public)
  - `save` (str, optional): File to save
  - `list` (bool, optional): List files in tier

**Returns**: dict
- `success` (bool)
- `content` (str or list): File content or file list
- `tier` (str): Memory tier used
- `suggested_tier` (str, optional): Suggested tier for save operations

**Example**:
```python
from core.services.memory_unified_handler import MemoryUnifiedHandler

handler = MemoryUnifiedHandler()
result = handler.handle({'tier': 'private', 'list': True})
print(result['content'])
```

##### `_analyze_content_security(content: str) -> str` (Internal)
Analyze content to suggest appropriate memory tier.

**Parameters**:
- `content` (str): File content to analyze

**Returns**: str - Suggested tier ('private', 'shared', 'community', or 'public')

**Note**: This is an internal method. Use `handle()` with `save` argument instead.

---

## Smart Input System

### FuzzyMatcher

**Location**: `core/services/fuzzy_matcher.py`

#### Methods

##### `find_matches(query: str, candidates: list[str], max_results: int = 5) -> list[dict]`
Find fuzzy matches for a query string.

**Parameters**:
- `query` (str): Search query
- `candidates` (list[str]): List of candidate strings
- `max_results` (int, default=5): Maximum results to return

**Returns**: list[dict]
- Each item contains: `match`, `score`, `distance`

**Example**:
```python
from core.services.fuzzy_matcher import FuzzyMatcher

matcher = FuzzyMatcher()
files = ['README.md', 'ROADMAP.MD', 'CONTRIBUTING.md']
matches = matcher.find_matches('readmi', files)
print(matches[0]['match'])  # README.md
```

##### `expand_abbreviation(abbr: str) -> str | None`
Expand common abbreviations.

**Parameters**:
- `abbr` (str): Abbreviation to expand

**Returns**: str | None - Expanded form or None if not found

**Example**:
```python
expanded = matcher.expand_abbreviation('readme')
# Returns: 'README.md'
```

**Attributes**:
- `abbreviations` (dict): Abbreviation mapping dictionary

---

### AliasManager

**Location**: `core/services/alias_manager.py`

#### Methods

##### `resolve_alias(alias: str) -> str | None`
Resolve an alias to its command.

**Parameters**:
- `alias` (str): Alias to resolve

**Returns**: str | None - Resolved command or None if not found

**Example**:
```python
from core.services.alias_manager import AliasManager

manager = AliasManager()
command = manager.resolve_alias('?')
# Returns: 'HELP'
```

##### `add_alias(alias: str, command: str) -> bool`
Add a custom alias.

**Parameters**:
- `alias` (str): Alias name
- `command` (str): Command to map to

**Returns**: bool - Success status

**Example**:
```python
success = manager.add_alias('gm', 'DOCS --manual git')
```

##### `remove_alias(alias: str) -> bool`
Remove a custom alias.

**Parameters**:
- `alias` (str): Alias to remove

**Returns**: bool - Success status

**Example**:
```python
success = manager.remove_alias('gm')
```

##### `list_aliases() -> dict`
List all aliases (built-in and custom).

**Returns**: dict
- `builtin` (dict): Built-in aliases
- `custom` (dict): Custom user aliases

**Example**:
```python
aliases = manager.list_aliases()
print(aliases['builtin'])  # {'?': 'HELP', 'd': 'DOCS', ...}
print(aliases['custom'])   # {'gm': 'DOCS --manual git', ...}
```

**Class Attributes**:
- `BUILTIN_ALIASES` (dict): Built-in alias mappings

---

## UI Components

### UniversalPicker

**Location**: `core/ui/universal_picker.py`

#### Classes

##### `PickerType` (Enum)
Picker variant types.

**Values**:
- `SINGLE_SELECT`: Single item selection
- `MULTI_SELECT`: Multiple item selection with checkboxes
- `SEARCH`: Search/filter variant
- `RECENT`: Recent items variant

##### `PickerConfig` (Dataclass)
Picker configuration.

**Attributes**:
- `picker_type` (PickerType): Type of picker
- `title` (str): Picker title
- `subtitle` (str, optional): Subtitle text
- `compact_mode` (bool, default=False): Compact layout for small screens
- `max_items_visible` (int, default=10): Maximum visible items

##### `PickerItem` (Dataclass)
Picker item data.

**Attributes**:
- `key` (str): Item key
- `label` (str): Display label
- `description` (str, optional): Item description
- `metadata` (dict, optional): Additional metadata

#### Methods

##### `show(items: list[PickerItem], config: PickerConfig) -> PickerItem | list[PickerItem] | None`
Display picker and return selection.

**Parameters**:
- `items` (list[PickerItem]): Items to display
- `config` (PickerConfig): Picker configuration

**Returns**: PickerItem | list[PickerItem] | None
- Single item for SINGLE_SELECT
- List of items for MULTI_SELECT
- None if cancelled

**Example**:
```python
from core.ui.universal_picker import UniversalPicker, PickerConfig, PickerItem, PickerType

picker = UniversalPicker()
items = [
    PickerItem(key='docs', label='Documentation', description='View docs'),
    PickerItem(key='manual', label='Manual', description='Command manual')
]
config = PickerConfig(
    picker_type=PickerType.SINGLE_SELECT,
    title='Select Option'
)
selected = picker.show(items, config)
print(selected.key)
```

---

### ProgressIndicators

**Location**: `core/ui/progress_indicators.py`

#### Classes

##### `ProgressBar`
Progress bar with ETA calculation.

**Methods**:
- `update(current: int, total: int) -> None`: Update progress
- `increment(amount: int = 1) -> None`: Increment progress
- `complete() -> None`: Mark as complete
- `render() -> str`: Render progress bar string

**Example**:
```python
from core.ui.progress_indicators import ProgressBar

bar = ProgressBar(total=100, width=40)
for i in range(100):
    bar.update(i + 1, 100)
    print(bar.render())
```

##### `Spinner`
Animated spinner with multiple styles.

**Styles**:
- `dots`: ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏
- `line`: -\\|/
- `arrow`: ←↖↑↗→↘↓↙
- `blocks`: ▁▂▃▄▅▆▇█
- `simple`: ·o0O

**Methods**:
- `start(message: str) -> None`: Start spinner
- `stop() -> None`: Stop spinner
- `update_message(message: str) -> None`: Update message

**Example**:
```python
from core.ui.progress_indicators import Spinner

spinner = Spinner(style='dots')
spinner.start('Processing...')
# ... do work ...
spinner.stop()
```

##### `MultiStageProgress`
Multi-stage progress tracker.

**Methods**:
- `start_stage(name: str) -> None`: Start a stage
- `complete_stage(name: str) -> None`: Complete a stage
- `render() -> str`: Render stage progress

**Example**:
```python
from core.ui.progress_indicators import MultiStageProgress

progress = MultiStageProgress(['Load', 'Process', 'Save'])
progress.start_stage('Load')
# ... load data ...
progress.complete_stage('Load')
progress.start_stage('Process')
# ... process ...
print(progress.render())
```

---

## Performance System

### LazyLoader

**Location**: `core/performance/lazy_loader.py`

#### Methods

##### `load_handler(name: str) -> object`
Lazily load a handler on first access.

**Parameters**:
- `name` (str): Handler name

**Returns**: object - Handler instance

**Example**:
```python
from core.performance.lazy_loader import LazyLoader

loader = LazyLoader()
handler = loader.load_handler('docs')
```

##### `get_stats() -> dict`
Get lazy loading statistics.

**Returns**: dict
- `loaded` (list): Loaded handler names
- `access_counts` (dict): Access count per handler
- `load_times` (dict): Load time per handler (ms)

---

### LRUCache

**Location**: `core/performance/lru_cache.py`

#### Methods

##### `get(key: str) -> Any | None`
Get value from cache.

**Parameters**:
- `key` (str): Cache key

**Returns**: Any | None - Cached value or None if not found

##### `put(key: str, value: Any) -> None`
Put value in cache.

**Parameters**:
- `key` (str): Cache key
- `value` (Any): Value to cache

##### `get_stats() -> dict`
Get cache statistics.

**Returns**: dict
- `hits` (int): Cache hits
- `misses` (int): Cache misses
- `hit_rate` (float): Hit rate percentage
- `size` (int): Current cache size
- `max_size` (int): Maximum cache size

**Example**:
```python
from core.performance.lru_cache import LRUCache

cache = LRUCache(max_size=100)
cache.put('key', 'value')
value = cache.get('key')
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

---

### PerformanceProfiler

**Location**: `core/performance/profiler.py`

#### Methods

##### `profile_command(command: str, execution_time_ms: float) -> None`
Record command execution time.

**Parameters**:
- `command` (str): Command name
- `execution_time_ms` (float): Execution time in milliseconds

##### `get_stats(command: str | None = None) -> dict`
Get performance statistics.

**Parameters**:
- `command` (str, optional): Specific command (None for all)

**Returns**: dict
- `p50` (float): 50th percentile (median)
- `p90` (float): 90th percentile
- `p99` (float): 99th percentile
- `mean` (float): Mean execution time
- `total_calls` (int): Total number of calls

**Example**:
```python
from core.performance.profiler import PerformanceProfiler

profiler = PerformanceProfiler()
profiler.profile_command('DOCS', 45.2)
stats = profiler.get_stats('DOCS')
print(f"P90: {stats['p90']}ms")
```

##### `get_slowest_commands(limit: int = 10) -> list[tuple[str, float]]`
Get slowest commands by P90.

**Parameters**:
- `limit` (int, default=10): Number of results

**Returns**: list[tuple[str, float]] - Command name and P90 time

---

## Error Handling

### EnhancedErrorHandler

**Location**: `core/services/error_handler.py`

#### Methods

##### `file_not_found(filepath: str, available_files: list[str] = None) -> str`
Generate file not found error with suggestions.

**Parameters**:
- `filepath` (str): File that wasn't found
- `available_files` (list[str], optional): List of available files for suggestions

**Returns**: str - Formatted error message

**Example**:
```python
from core.services.error_handler import EnhancedErrorHandler

handler = EnhancedErrorHandler()
files = ['README.md', 'ROADMAP.MD']
error = handler.file_not_found('READMI.md', files)
print(error)
```

##### `command_not_found(command: str, available_commands: list[str] = None) -> str`
Generate command not found error with suggestions.

**Parameters**:
- `command` (str): Command that wasn't found
- `available_commands` (list[str], optional): List of available commands

**Returns**: str - Formatted error message

##### `permission_denied(resource: str, required_tier: str, current_tier: str) -> str`
Generate permission denied error with tier guidance.

**Parameters**:
- `resource` (str): Resource being accessed
- `required_tier` (str): Required tier level
- `current_tier` (str): Current user tier

**Returns**: str - Formatted error message

##### `invalid_argument(param_name: str, provided_value: str, valid_values: list[str] = None, expected: str = None) -> str`
Generate invalid argument error with valid options.

**Parameters**:
- `param_name` (str): Parameter name
- `provided_value` (str): Value that was provided
- `valid_values` (list[str], optional): List of valid values
- `expected` (str, optional): Expected format description

**Returns**: str - Formatted error message

##### `syntax_error(command: str, invalid_syntax: str, expected_format: str = None, example: str = None) -> str`
Generate syntax error with examples.

**Parameters**:
- `command` (str): Command name
- `invalid_syntax` (str): Invalid syntax provided
- `expected_format` (str, optional): Expected format description
- `example` (str, optional): Example of correct usage

**Returns**: str - Formatted error message

##### `timeout_error(operation: str, timeout_seconds: int, suggestion: str = None) -> str`
Generate timeout error with troubleshooting.

**Parameters**:
- `operation` (str): Operation that timed out
- `timeout_seconds` (int): Timeout duration
- `suggestion` (str, optional): Suggestion for resolution

**Returns**: str - Formatted error message

---

## Data Structures

### Common Return Types

#### Handler Response
```python
{
    'success': bool,
    'content': str | list,
    'source': str,
    'relevance': float,
    'error': str  # Only present if success=False
}
```

#### Search Result
```python
{
    'match': str,
    'score': float,
    'distance': int,
    'source': str,
    'relevance': float
}
```

#### Cache Stats
```python
{
    'hits': int,
    'misses': int,
    'hit_rate': float,
    'size': int,
    'max_size': int
}
```

#### Performance Stats
```python
{
    'p50': float,
    'p90': float,
    'p99': float,
    'mean': float,
    'total_calls': int,
    'slowest': list[tuple[str, float]]
}
```

---

## Best Practices

### Handler Usage
```python
# Always check success status
result = handler.handle(args)
if result['success']:
    print(result['content'])
else:
    print(result['error'])
```

### Picker Usage
```python
# Always provide PickerConfig, not raw dict
from core.ui.universal_picker import PickerConfig, PickerType

config = PickerConfig(
    picker_type=PickerType.SINGLE_SELECT,
    title='Select Option'
)
```

### Error Handling
```python
# Provide context for better suggestions
try:
    # ... operation ...
except FileNotFoundError:
    available_files = os.listdir('.')
    error = handler.file_not_found(filepath, available_files)
```

---

## Version History

- **v1.0.23**: Initial API documentation
- Future: API stability guarantees for v1.1.0

---

**Last Updated**: November 17, 2025
**Version**: v1.0.23
**Maintained By**: uDOS Development Team
