# UCODE ENV Command Reference
**Version:** 1.0
**Status:** Active
**Last Updated:** 2026-02-24

---

## Overview

The `UCODE ENV` command provides a shell interface for managing `.env` variables directly from the uDOS TUI and Wizard. It can be used in hints, configuration messages, and automated workflows.

---

## Usage

### List All Variables
```bash
UCODE ENV
```

**Output:**
```
Current .env variables:
  UDOS_ROOT = /Users/fredrick/Code/uDOS
  USER_NAME = Fredrick
  UDOS_TIMEZONE = America/Los_Angeles
  UDOS_LOCATION = San Francisco
  OS_TYPE = mac
  MISTRAL_API_KEY = ***
  WIZARD_KEY = ***
  ... (and more)
```

**Notes:**
- Sensitive keys (API keys, tokens) are masked as `***`
- Long values (>50 chars) are truncated with `...`
- Comments in .env are ignored in listing

### Set Single Variable
```bash
UCODE ENV username="Fred"
```

**Output:**
```
Set environment variables:
  ✓ username = Fred

File: /path/to/uDOS/.env
```

### Set Multiple Variables
```bash
UCODE ENV username="Fred" mistral_api_key="sk-123" udos_timezone="UTC"
```

**Output:**
```
Set environment variables:
  ✓ username = Fred
  ✓ mistral_api_key = ***
  ✓ udos_timezone = UTC

File: /path/to/uDOS/.env
```

### With Quoted Values (Spaces)
```bash
UCODE ENV location_name="San Francisco" user_bio="OK Model researcher from CA"
```

Variables with spaces require quotes around the value.

---

## Syntax Rules

### Correct Formats
```bash
UCODE ENV key=value
UCODE ENV key="value"
UCODE ENV key="multi word value"
UCODE ENV key1="value1" key2="value2" key3="value3"
```

### Things to Remember
- ✅ Use `=` without spaces around it: `key="value"` (not `key = "value"`)
- ✅ Quotes optional for single-word values: `UDOS_LOG_LEVEL=INFO`
- ✅ Quotes required for multi-word values: `location_name="San Francisco"`
- ✅ Multiple assignments in one command are supported
- ❌ Don't use single quotes: `key='value'` (use double quotes)
- ❌ Don't use `$` for variable expansion (not supported)

### Examples

**Single variable (no spaces):**
```bash
UCODE ENV UDOS_LOG_LEVEL=INFO
```

**Single variable (with spaces):**
```bash
UCODE ENV UDOS_LOCATION_NAME="San Francisco Bay Area"
```

**Multiple variables:**
```bash
UCODE ENV UDOS_LOG_LEVEL=INFO UDOS_TIMEZONE=UTC OS_TYPE=mac
```

**Mix of quoted and unquoted:**
```bash
UCODE ENV OS_TYPE=mac LOCATION_NAME="California" UDOS_LOG_LEVEL=INFO
```

---

## Use Cases

### 1. Setup Scripts & Hints

In Wizard config messages or hints:
```json
{
  "hint": "Set your username with: UCODE ENV USER_NAME=\"YourName\"",
  "setup_command": "UCODE ENV USER_NAME=\"Fredrick\" UDOS_TIMEZONE=\"America/Los_Angeles\""
}
```

### 2. Automated Configuration

In shell scripts:
```bash
#!/bin/bash
# Auto-setup for new machine
UCODE ENV USER_NAME="AutoUser" OS_TYPE="linux" UDOS_LOG_LEVEL="DEBUG"
```

### 3. CI/CD Pipelines

In GitHub Actions or similar:
```yaml
- name: Configure uDOS
  run: |
    UCODE ENV OS_TYPE=ubuntu UDOS_AUTOMATION=1
```

### 4. Interactive Setup

In SETUP story or dialog:
```python
# Wizard could say to user:
print("Execute this to save your choice:")
print(f"UCODE ENV UDOS_LOCATION=\"{user_choice}\"")
```

### 5. Debugging

Check current config:
```bash
UCODE ENV  # List all
```

Quick variable check in hints:
```
Try: UCODE ENV
Then: UCODE ENV USER_NAME="NewName"
```

---

## Security Considerations

### Sensitive Keys are Masked in Output
These keys are never displayed, even when listing:
- `MISTRAL_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GITHUB_TOKEN`
- `AWS_SECRET_ACCESS_KEY`
- `WIZARD_ADMIN_TOKEN`
- `WIZARD_KEY`
- `USER_PASSWORD`
- `GCP_SERVICE_ACCOUNT`

**Example:**
```bash
UCODE ENV MISTRAL_API_KEY="real-key-here"
# Output shows: ✓ MISTRAL_API_KEY = ***
# Never displays the actual key
```

### Best Practices
1. ✅ Use SETUP story for initial API keys (stores in encrypted `secrets.tomb`)
2. ✅ Use Wizard dashboard for long-term API key management
3. ✅ Use `UCODE ENV` for non-sensitive config (timezone, paths, names)
4. ✅ Don't paste API keys in hints or visible messages
5. ❌ Don't commit actual `.env` with keys to git (`.gitignore` protects this)

---

## Integration with Wizard & Hints

### Example Hint Message
```python
def show_setup_hint(user_name: str):
    return f"""
    ℹ️  Configuration Tip:

    You can also set environment variables directly:
    UCODE ENV USER_NAME="{user_name}"

    Or multiple at once:
    UCODE ENV UDOS_TIMEZONE="UTC" UDOS_LOG_LEVEL="INFO"

    View current settings:
    UCODE ENV
    """
```

### Example Wizard Config Message
```python
class SetupWizard:
    def get_setup_help(self):
        return {
            "hint": "Run this to apply your choices:",
            "command": f"UCODE ENV {' '.join([f'{k}=\"{v}\"' if ' ' in v else f'{k}={v}' for k, v in self.choices.items()])}",
            "note": "Or use the Wizard dashboard to manage these settings"
        }
```

---

## Response Format

All `UCODE ENV` commands return structured responses:

### List Response
```json
{
  "status": "success",
  "message": "ENV list",
  "output": "Current .env variables:\n  KEY1 = value1\n  ...",
  "variables": {
    "KEY1": "value1",
    "KEY2": "value2"
  },
  "count": 25
}
```

### Set Response
```json
{
  "status": "success",
  "message": "ENV set",
  "output": "Set environment variables:\n  ✓ KEY1 = value1\n  ...",
  "variables_set": {
    "KEY1": "value1"
  },
  "file_path": "/path/to/.env"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Failed parsing assignments",
  "output": "Invalid assignment format. Use: ENV key=\"value\" ...",
  "recovery_hint": "Example: ENV username=\"Fred\" mistral_api_key=\"xyz\""
}
```

---

## Troubleshooting

### "Invalid assignment format"
**Problem:** Syntax error in command
**Solution:**
```bash
# ❌ Wrong
UCODE ENV key = value

# ✅ Right
UCODE ENV key=value
```

### ".env file not found"
**Problem:** No .env in repo
**Solution:**
```bash
# Create it via SETUP
python uDOS.py
# Choose: SETUP
```

### "Failed to write .env"
**Problem:** Permission denied
**Solution:**
```bash
# Check permissions
ls -la .env
# Fix if needed
chmod 644 .env
```

### Variables not showing after set
**Problem:** Different shell session
**Solution:**
```bash
# The UCODE ENV command updates .env file, but doesn't reload shell env vars
# New shell or explicit export required:
export UDOS_ROOT="/path/to/udos"

# Or reload shell config:
source ~/.bashrc  # or ~/.zshrc
```

---

## Examples Library

### Basic Local Config
```bash
UCODE ENV USER_NAME="Alice" OS_TYPE=mac UDOS_TIMEZONE="America/New_York"
```

### After Moving Machines
```bash
UCODE ENV UDOS_ROOT="/Users/newuser/Code/uDOS"
```

### Automation/CI Setup
```bash
UCODE ENV UDOS_AUTOMATION=1 UDOS_LOG_LEVEL=DEBUG UDOS_DEV_MODE=1
```

### Multi-Provider Setup
```bash
UCODE ENV OLLAMA_HOST="http://localhost:11434" LOCAL_MODELS_ALLOWED=1
```

### Logging Configuration
```bash
UCODE ENV UDOS_LOG_LEVEL=DEBUG UDOS_LOG_FORMAT=json UDOS_LOG_DEST=file
```

---

## References

- [SETUP-SECRETS.md](SETUP-SECRETS.md) — Secret management best practices
- [ENV-STRUCTURE-V1.1.0.md](../specs/ENV-STRUCTURE-V1.1.0.md) — .env design spec
- [core/commands/ucode_handler.py](../../core/commands/ucode_handler.py) — Implementation
