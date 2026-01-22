# SmartPrompt Quick Reference

## Installation & Setup

**Already integrated into Core TUI.** No additional setup needed.

```python
# In core/tui/repl.py:
from core.input import SmartPrompt

prompt = SmartPrompt()  # Auto-detects mode (advanced or fallback)
```

---

## User Features (In TUI)

### Autocomplete

| Key            | Action                          |
| -------------- | ------------------------------- |
| **Tab**        | Auto-complete current command   |
| **Ctrl+Space** | Show completions menu           |
| **Arrow ↑/↓**  | Navigate history or completions |
| **Enter**      | Execute command                 |
| **Ctrl+C**     | Cancel input                    |

### Supported Commands (13)

```
Navigation:   MAP, PANEL, GOTO, FIND
Info:         TELL, HELP
Game State:   BAG, GRAB, SPAWN, SAVE, LOAD
System:       SHAKEDOWN, REPAIR
NPC:          NPC, TALK
```

### Examples

```
> FI[TAB]
  FIND

> MAP --help[ENTER]
  (displays map help)

> REPAIR --pull[ENTER]
  (pulls latest from git)
```

---

## Developer API

### SmartPrompt Class

```python
from core.input import SmartPrompt

# Initialize
prompt = SmartPrompt()
prompt = SmartPrompt(use_fallback=True)  # Force basic input

# Get input
user_input = prompt.ask("uDOS> ")  # Returns string
user_input = prompt.ask(">> ", default="HELP")  # With default

# Get predictions
predictions = prompt.get_predictions("FI")  # List[Prediction]
# Returns: [Prediction(text="FIND", confidence=0.95, source="schema", ...)]

# Get highlighted command
highlighted = prompt.get_highlighted_command("FIND tokyo")
# Returns: "\033[32mFIND\033[0m tokyo"

# Check mode
if prompt.use_fallback:
    print(f"Fallback: {prompt.fallback_reason}")
else:
    print("Advanced mode with prompt_toolkit")
```

### AutocompleteService

```python
from core.input import AutocompleteService

service = AutocompleteService()

# Get completions
completions = service.get_completions("FI", max_results=5)
# Returns: ["FIND"]

completions = service.get_completions("RE", max_results=5)
# Returns: ["REPAIR"]

# Get options for command
options = service.get_options("REPAIR")
# Returns: ["--help", "--verbose", "--quiet", "--debug", "--pull", "--upgrade-all"]

# Get description
description = service.get_description("FIND")
# Returns: "Search for something"
```

### CommandPredictor

```python
from core.input import CommandPredictor, AutocompleteService

service = AutocompleteService()
predictor = CommandPredictor(service)

# Get predictions with confidence
predictions = predictor.predict("FI", max_results=5)
# Returns: [
#   Prediction(text="FIND", confidence=0.95, source="schema", description="..."),
# ]

# Tokenize for syntax highlighting
tokens = predictor.tokenize("FIND tokyo")
# Returns: [
#   Token(text="FIND", type="command", color="green"),
#   Token(text="tokyo", type="arg", color="white"),
# ]

# Track command for frequency analysis
predictor.record_command("FIND tokyo")
```

### Data Classes

```python
from core.input import Prediction, Token

# Prediction
Prediction(
    text="FIND",
    confidence=0.95,  # 0.0 - 1.0
    source="schema",  # "history", "schema", "fuzzy"
    description="Search for something"
)

# Token
Token(
    text="FIND",
    type="command",  # "command", "arg", "option"
    color="green"     # ANSI color name
)
```

---

## Environment Detection

SmartPrompt automatically detects:

- ✅ `prompt_toolkit` availability
- ✅ Terminal TTY status
- ✅ Terminal capabilities
- ✅ TERM environment variable

**Fallback triggers:**

- Missing `prompt_toolkit` → Uses `input()`
- Non-interactive terminal → Uses `input()`
- Terminal detection failure → Uses `input()`
- Any runtime error → Switches to `input()`

---

## Configuration

### Enable/Disable Advanced Features

```python
# Force fallback for testing
prompt = SmartPrompt(use_fallback=True)

# Check current mode
print(prompt.use_fallback)  # False = advanced, True = fallback
print(prompt.fallback_reason)  # None if advanced, reason if fallback
```

### Access Services Directly

```python
prompt = SmartPrompt()

# Access autocomplete service
autocomplete = prompt.autocomplete_service
completions = autocomplete.get_completions("MA")

# Access predictor
predictor = prompt.predictor
tokens = predictor.tokenize("MAP")

# Access prompt_toolkit objects (if advanced)
if not prompt.use_fallback:
    session = prompt.session  # PromptSession object
    completer = prompt.completer  # CoreCompleter object
```

---

## Logging

SmartPrompt logs initialization to Core's logger:

```
2026-01-22 19:57:49 - tui-repl - INFO - [SmartPrompt] Initialized with prompt_toolkit
```

Or fallback:

```
2026-01-22 19:57:49 - tui-repl - INFO - [SmartPrompt] Using fallback: prompt_toolkit not installed
```

---

## Performance

- **First input:** ~100ms (first-time prompt_toolkit setup)
- **Subsequent inputs:** ~20ms (cached)
- **Autocomplete generation:** <50ms
- **Tokenization:** <10ms
- **Memory footprint:** ~50KB

---

## Troubleshooting

### "prompt_toolkit not installed"

```bash
# Install optional dependency
pip install prompt-toolkit

# Or use fallback (already built-in)
prompt = SmartPrompt()  # Auto-detects
```

### "Non-interactive terminal"

Automatic fallback. SmartPrompt detects and uses basic `input()`.

### Custom Colors Not Showing

Check TERM environment:

```bash
echo $TERM  # Should be 'xterm-256color' or similar
```

---

## See Also

- [INPUT_INTEGRATION.md](INPUT_INTEGRATION.md) — Full integration guide
- `core/input/smart_prompt.py` — Implementation
- `core/input/autocomplete.py` — Command schema
- `core/input/command_predictor.py` — Prediction engine
