# uDOS Style Guide

Standards for code, content, and design across the uDOS project.

---

## 📝 Code Style

### Python

```python
# Use Black formatter
# Max line length: 88
# Use type hints where practical

from core.services.logging_manager import get_logger

logger = get_logger('module-name')

class MyHandler(BaseCommandHandler):
    """Short description of handler."""

    def handle(self, command: str, params: list, grid, parser) -> dict:
        """Handle the command.

        Args:
            command: The command name
            params: List of parameters
            grid: Display grid
            parser: Command parser

        Returns:
            Result dictionary with status and message
        """
        try:
            # Implementation
            return {"status": "success", "message": "Done"}
        except Exception as e:
            logger.error(f"[ERROR] {command} failed: {e}")
            return {"status": "error", "message": str(e)}
```

### TypeScript/Svelte

```typescript
// Use Prettier formatter
// Prefer interfaces over types
// Use async/await over promises

interface CommandResult {
  status: "success" | "error";
  message: string;
  data?: unknown;
}

async function executeCommand(cmd: string): Promise<CommandResult> {
  // Implementation
}
```

---

## 📋 Logging Standards

### Required Tags

```
[LOCAL]   - Local device operation
[MESH]    - MeshCore P2P
[BT-PRIV] - Bluetooth Private
[BT-PUB]  - Bluetooth Public (signal only!)
[NFC]     - NFC contact
[QR]      - QR relay
[AUD]     - Audio transport
[WIZ]     - Wizard Server operation
[GMAIL]   - Gmail relay (Wizard only)
```

### Logger Usage

```python
from core.services.logging_manager import get_logger

# Category naming: {module}-{context}
logger = get_logger('command-backup')
logger = get_logger('system-startup')
logger = get_logger('api-websocket')

# Log levels
logger.debug("Detailed info for debugging")
logger.info("Normal operations")
logger.warning("Something unexpected but handled")
logger.error("Error that needs attention")
```

---

## 📄 Documentation Style

### Markdown Files

```markdown
# Document Title

Brief description (1-2 sentences).

---

## Section Heading

Content here.

### Subsection

More detail.

---

_Last Updated: YYYY-MM-DD_
```

---

## 🔤 Typography Standards (Wizard Dashboard)

Wizard uses a **three-slot typography system** driven by CSS variables (no class explosion):

- **Prose Title** (`--font-prose-title`)
- **Prose Body** (`--font-prose-body`)
- **Code** (`--font-code`)

Each slot supports a scale multiplier:

- `--scale-prose-title`
- `--scale-prose-body`
- `--scale-code`

Emoji fallback is always appended via:

- `--font-emoji`

### Canonical Font Bundle

Bundled fonts live in:

```
/fonts/
```

The manifest is:

```
/fonts/manifest.json
```

### Tailwind + Typography Rules

Tailwind Typography (prose) must read from the variables above. Example:

```js
typography: () => ({
  DEFAULT: {
    css: {
      fontFamily: "var(--font-prose-body)",
      "h1,h2,h3,h4,h5,h6": { fontFamily: "var(--font-prose-title)" },
      "code, pre code": { fontFamily: "var(--font-code)" },
    },
  },
});
```

### UI Toggles

Wizard’s bottom bar exposes:

- **Heading Font**
- **Body Font**
- **Font Size / Ratio**

These controls update the CSS variables at runtime (no recompile).

### Command Documentation

````markdown
## COMMAND

Brief description.

**Syntax:**

```bash
COMMAND <required> [optional]
```
````

**Examples:**

```bash
COMMAND value
COMMAND value --flag
```

**Notes:**

- Important detail 1
- Important detail 2

```

---

## 🎨 Graphics Policy

### Decision Hierarchy

```

1. Text only (most cases)
2. Markdown diagram (mermaid)
3. ASCII/Teletext blocks
4. SVG (special cases only)

````

### When to Use Each

| Type | Use For | Avoid |
|------|---------|-------|
| Text | Explanations, lists | Never avoid text |
| Mermaid | Flowcharts, sequences | Simple linear processes |
| ASCII | Technical diagrams, maps | Natural subjects |
| SVG | Icons, complex visuals | Simple content |

---

## 📦 Version Management

### Version Files

```json
{
  "component": "core",
  "name": "uDOS Core",
  "version": {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build": 63
  },
  "channel": "alpha"
}
````

### Bumping Versions

```bash
# Bump build number (most changes)
python -m core.version bump core build

# Bump patch (bug fixes)
python -m core.version bump core patch

# Bump minor (new features)
python -m core.version bump core minor
```

---

## 📁 File Organization

### Directory Patterns

```
core/           # Core Python code
├── commands/   # Command handlers
├── services/   # Business logic
├── ui/         # UI components
└── data/       # Static data (JSON, YAML)

extensions/     # Extensions
├── api/        # REST/WebSocket API
├── transport/  # Network transports
└── wizard/     # Wizard Server (moved to wizard/)

memory/         # User data (gitignored)
├── inbox/      # Pending items
├── logs/       # Log files
└── ucode/      # User scripts

knowledge/      # Knowledge bank
├── survival/   # Survival guides
└── ai/         # AI instructions
```

### Naming Conventions

```
# Handlers
{topic}_handler.py    # e.g., bundle_handler.py

# Services
{service}_service.py  # e.g., ocr_service.py
{topic}_manager.py    # e.g., logging_manager.py

# Data files
{name}.json           # Structured data
{name}.yaml           # Configuration
```

---

## 🔄 Git Workflow

---

## 🧭 Path Anchoring

All docs and scripts must refer to the repo root as:

```
~/uDOS/
```

Never hardcode machine-specific absolute roots (e.g., `/Users/<name>/Code/`).
If a script needs the root, resolve it via `UDOS_ROOT` or repo detection, then
assert it stays within `~/uDOS/` unless `UDOS_HOME_ROOT_ALLOW_OUTSIDE=1` is set.

### Commit Messages

```
feat: Add BUNDLE command for content packages
fix: Correct parameter parsing in CAPTURE
docs: Update wiki command reference
refactor: Rename System App → uCode Markdown App
test: Add BUNDLE handler unit tests
chore: Update dependencies
```

### Branch Naming

```
feature/bundle-system
fix/capture-timeout
docs/wiki-reorganization
```

---

## ✅ Checklist Before Commit

- [ ] Code formatted (Black/Prettier)
- [ ] Logging uses correct tags
- [ ] Error handling in place
- [ ] Type hints where practical
- [ ] Docstrings for public methods
- [ ] Version bumped if needed
- [ ] Commands.json updated if new command

---

**Last Updated:** 2026-01-24
**Version:** Core v1.1.0.0
