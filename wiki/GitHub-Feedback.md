# GitHub Feedback Integration

**Version**: 1.2.4
**Status**: Stable

## Overview

The GitHub Feedback Integration enables direct feedback submission through GitHub without leaving uDOS. No API tokens required - everything stays local until you manually submit via browser.

## Quick Start

```bash
# Report a bug
> FEEDBACK --github --bug --open

# Request a feature
> FEEDBACK --github --feature --open

# Ask a question
> FEEDBACK --github --question --open

# Share an idea
> FEEDBACK --github --idea --open
```

## Features

### 1. Browser-Based Workflow

No API tokens or authentication needed. Opens pre-filled GitHub forms in your browser.

```bash
> FEEDBACK --github --bug --open
🌐 GitHub Bug Report Ready
============================================================

Category: bug
System: macOS 14.1 | uDOS 1.2.4

This will open GitHub in your browser with a pre-filled template.
No API tokens required - all data stays local until you submit.

✅ Browser opened successfully
   Complete the template and submit on GitHub
```

### 2. Pre-filled Templates

Structured templates with system information automatically included.

**Bug Report Template**:
```markdown
**Describe the bug**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**System Information**
- uDOS Version: 1.2.4
- OS: macOS 14.1
- Python: 3.11.5
- Mode: interactive
```

**Feature Request Template**:
```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How would you like this to work?

**System Information**
- uDOS Version: 1.2.4
- OS: macOS 14.1
```

### 3. Minimal Data Collection

**Only collects non-sensitive system info**:
- uDOS version (e.g., "1.2.4")
- Operating system (e.g., "macOS 14.1")
- Python version (e.g., "3.11.5")
- Mode (e.g., "interactive")

**Never collects**:
- User data
- File contents
- Command history
- Personal information
- API tokens

### 4. User Confirmation

Preview URL before opening browser (--open flag required):

```bash
# Preview only (no browser launch)
> FEEDBACK --github --bug
🌐 GitHub Bug Report Ready
...
URL: https://github.com/fredporter/uDOS/issues/new?title=%5BBug%5D+...

Run again with --open flag to launch browser:
  FEEDBACK --github --open --issue --bug

# Launch browser immediately
> FEEDBACK --github --bug --open
✅ Browser opened successfully
```

## Command Syntax

### Feedback Types

```bash
# Issues (bug reports and feature requests)
FEEDBACK --github --issue [--bug|--feature] [--open]

# Discussions (questions and ideas)
FEEDBACK --github --discussion [--question|--idea|--general] [--open]
```

### Categories

**Issues**:
- `--bug` - Report a bug (creates Issue with bug label)
- `--feature` - Request a feature (creates Issue with feature label)

**Discussions**:
- `--question` - Ask a question (creates Q&A Discussion)
- `--idea` - Share an idea (creates Ideas Discussion)
- `--general` - General feedback (creates General Discussion)

### Flags

- `--github` - Use GitHub browser integration (vs local feedback)
- `--issue` - Create a GitHub Issue (optional, inferred from category)
- `--discussion` - Create a GitHub Discussion (optional, inferred from category)
- `--open` - Automatically open browser (skip confirmation)

## Examples

### Bug Reports

```bash
# Preview bug report URL
> FEEDBACK --github --bug

# Open bug report in browser
> FEEDBACK --github --bug --open

# Shorthand (bug implies issue)
> FEEDBACK --github --bug --open
```

### Feature Requests

```bash
# Preview feature request URL
> FEEDBACK --github --feature

# Open feature request in browser
> FEEDBACK --github --feature --open
```

### Questions

```bash
# Preview question discussion URL
> FEEDBACK --github --question

# Open question discussion in browser
> FEEDBACK --github --question --open
```

### Ideas

```bash
# Share an idea (opens Discussion)
> FEEDBACK --github --idea --open

# General discussion
> FEEDBACK --github --general --open
```

## Local Feedback (Alternative)

Prefer to keep feedback local? Use the traditional command:

```bash
# Save to memory/logs/user_feedback.jsonl
> FEEDBACK "Your feedback message here"

# With category
> FEEDBACK "Confused about workflow syntax" TYPE confusion

# View recent feedback
> FEEDBACK --list
```

## Architecture

### FeedbackHandler

**Location**: `core/commands/feedback_handler.py`

**GitHub Methods** (v1.2.4):
- `handle_github_feedback(type, category, pre_fill, auto_open)` - Main integration
- `_collect_system_info()` - Minimal data collection
- `_generate_issue_url(category, pre_fill, system_info)` - Issue URL builder
- `_generate_discussion_url(category, pre_fill, system_info)` - Discussion URL builder

**URL Structure**:
```python
# GitHub Issues
https://github.com/fredporter/uDOS/issues/new?title=[Bug]&body=...&labels=bug

# GitHub Discussions
https://github.com/fredporter/uDOS/discussions/new?category=Q%26A&body=...
```

### UserCommandHandler

**Location**: `core/commands/user_handler.py`

**Enhancements** (v1.2.4):
- Flag parsing (`--github`, `--open`, `--bug`, etc.)
- `_handle_github_feedback(flags)` - GitHub workflow router
- `_feedback_help()` - Comprehensive help text

### Command Routing

**Location**: `core/uDOS_commands.py`

**Shortcuts** (v1.2.4):
- `FEEDBACK` - Top-level command (routes to USER module)
- No need for `USER FEEDBACK`, just `FEEDBACK`

## System Information Collection

### Implementation

```python
def _collect_system_info(self) -> Dict[str, str]:
    """Collect minimal system information (no sensitive data)"""

    # Get uDOS version from setup.py
    try:
        from pathlib import Path
        setup_path = Path(__file__).parent.parent.parent / "setup.py"
        version = "1.2.4"  # Default to current dev version
        if setup_path.exists():
            with open(setup_path) as f:
                for line in f:
                    if "version=" in line:
                        version = line.split('"')[1]
                        break
    except:
        version = "unknown"

    return {
        "version": version,
        "os": f"{platform.system()} {platform.release()}",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "mode": "interactive"
    }
```

### Privacy

**What's collected**:
- Version string (from `setup.py`)
- OS name and release (from `platform` module)
- Python version (from `sys.version_info`)
- Mode (hardcoded as "interactive")

**What's NOT collected**:
- User information
- File paths
- Command history
- Environment variables
- API tokens
- Personal data

## URL Encoding

### Safe Characters

All special characters in URLs are properly encoded:

```python
from urllib.parse import urlencode

params = {
    "title": "[Bug] ",
    "body": template,
    "labels": "bug"
}

url = f"{GITHUB_ISSUES_URL}?{urlencode(params)}"
```

### Example Encoded URL

```
https://github.com/fredporter/uDOS/issues/new?
  title=%5BBug%5D+
  &body=**Describe+the+bug**%0A...
  &labels=bug
```

## Testing

### SHAKEDOWN Tests

GitHub feedback has 8 comprehensive tests in `SHAKEDOWN`:

```bash
> SHAKEDOWN
...
GITHUB FEEDBACK INTEGRATION (v1.2.4)
  ✅ FeedbackHandler with GitHub methods imported
  ✅ System info collection working
  ✅ Bug report URL generation working
  ✅ Feature request URL generation working
  ✅ Discussion URL generation working
  ✅ UserCommandHandler GitHub integration present
  ✅ FEEDBACK command routing configured
  ✅ URL encoding working
```

### Manual Testing

```bash
# Test all feedback types
> FEEDBACK --github --bug
> FEEDBACK --github --feature
> FEEDBACK --github --question
> FEEDBACK --github --idea

# Test with --open (opens browser)
> FEEDBACK --github --bug --open

# Test help text
> FEEDBACK

# Test local feedback
> FEEDBACK "Test message"
```

## Troubleshooting

### Browser Won't Open

```bash
> FEEDBACK --github --bug --open
❌ Failed to open browser: [Errno 2] No such file or directory
```

**Solution**: Copy URL manually:
```bash
> FEEDBACK --github --bug
# Copy the displayed URL
# Paste into your browser
```

### URL Too Long

GitHub has URL length limits (~2000 chars). If your template is too long:

```bash
> FEEDBACK --github --bug --open
⚠️  URL may be truncated (very long description)
```

**Solution**: Shorten pre-fill text or use manual GitHub issue creation.

### Wrong Category

```bash
> FEEDBACK --github --bug
# Actually wanted a feature request
```

**Solution**: Use correct category flag:
```bash
> FEEDBACK --github --feature --open
```

## See Also

- [Contributing Guide](../CONTRIBUTING.md)
- [Command Reference](Command-Reference.md#feedback)
- [User Handler](Developers-Guide.md#user-command-handler)

## Changelog

### v1.2.4 (December 4, 2025)
- Initial GitHub feedback integration
- FeedbackHandler enhancements (+190 lines)
- UserCommandHandler updates (+135 lines)
- FEEDBACK top-level command (+4 lines)
- SHAKEDOWN integration (+170 lines)
- Total: 499 lines delivered

---

**Status**: Stable
**Tests**: 8/8 passing
**Privacy**: Minimal data, user-controlled
**Documentation**: Complete
