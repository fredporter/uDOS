# Content Commands

> [!WARNING]
> Archived legacy page (v1.1). This page documents pre-v1.3 command families and is retained for historical reference.
> Use `/Users/fredbook/Code/uDOS/docs/howto/UCODE-COMMAND-REFERENCE.md` for canonical current commands.
> Wizard-owned integration/provider flows are documented at `/Users/fredbook/Code/uDOS/docs/howto/commands/wizard.md`.

> **Version:** Core v1.1.0.0

Commands for knowledge, content packages, and web capture.

---

## GUIDE

Knowledge system - Interactive guides and AI instructions.

### Syntax

```
GUIDE [type]
GUIDE AI LIST [category]
GUIDE AI SHOW <id>
GUIDE AI RUN <id> [var=value...]
GUIDE AI SEARCH <query>
GUIDE AI STATS
GUIDE AI BUILD
```

### Examples

```bash
# Browse markdown guides
GUIDE
GUIDE LIST

# AI instruction library
GUIDE AI LIST coding
GUIDE AI SHOW fix-python-errors
GUIDE AI RUN fix-python-errors file=core/test.py
GUIDE AI SEARCH "error handling"
GUIDE AI STATS
GUIDE AI BUILD  # Wizard only
```

### Notes

- `GUIDE` (no AI) = Markdown knowledge/guides
- `GUIDE AI` = AI instruction library
- AI Categories: coding, writing, image, workflow, analysis, creative, system
- Workflow: Perfect with Gemini → Save to `knowledge/ai/` → Execute offline

---

## BUNDLE

Content package management with scheduled drip delivery.

### Syntax

```
BUNDLE [subcommand] [args]
```

### Subcommands

| Command | Description |
| ------- | ----------- |
| `LIST` | List available bundles |
| `SHOW <id>` | Show bundle details and progress |
| `START <id>` | Begin a bundle (activates drip schedule) |
| `PAUSE <id>` | Pause active bundle |
| `RESUME <id>` | Resume paused bundle |
| `NEXT <id>` | Request next piece early (costs wellbeing) |
| `SKIP <id>` | Skip current piece |
| `COMPLETE <id>` | Mark bundle as complete |
| `REVIEW <id>` | Show bundle summary after completion |
| `PLAN <topic>` | Use AI to plan new bundle structure |
| `GENERATE <topic>` | Generate bundle content from plan |

### Examples

```bash
# List and browse
BUNDLE
BUNDLE LIST
BUNDLE SHOW survival-basics

# Manage active bundles
BUNDLE START fire-making-101
BUNDLE NEXT fire-making-101
BUNDLE PAUSE fire-making-101
BUNDLE COMPLETE fire-making-101

# Create new bundles (Wizard)
BUNDLE PLAN "water purification techniques"
BUNDLE GENERATE water-purification
```

### Bundle Structure

```
knowledge/bundles/
└── fire-making-101/
    ├── manifest.yaml       # Bundle metadata
    ├── .state/             # Progress tracking
    │   └── state.json
    └── pieces/
        ├── 01-introduction.md
        ├── 02-materials.md
        ├── 03-techniques.md
        └── 04-practice.md
```

### manifest.yaml Format

```yaml
id: fire-making-101
title: Fire Making Fundamentals
description: Learn essential fire-starting techniques
version: 1.0.0
author: survival-kb

schedule:
  type: daily          # immediate | daily | weekly | on-complete
  interval: 1          # Days between pieces
  
pieces:
  - id: 01-introduction
    title: Introduction to Fire
    unlock: immediate
  - id: 02-materials
    title: Gathering Materials
    unlock: after-previous
  - id: 03-techniques
    title: Starting Techniques
    unlock: after-previous
    
tags: [survival, fire, basics]
difficulty: beginner
estimated_time: 2h
```

### Drip Types

- **immediate**: Available right away
- **daily**: One piece per day
- **weekly**: One piece per week
- **on-complete**: Unlocks when previous is marked complete

### Notes

- Bundles stored in `knowledge/bundles/`
- Progress tracked locally in `.state/` subdirectory
- `NEXT` costs wellbeing energy (integrates with WELLBEING)
- Great for structured learning paths

---

## CAPTURE

Web content capture pipeline (Wizard Server only).

### Syntax

```
CAPTURE <url> [--pipeline TYPE]
CAPTURE LIST
CAPTURE PROCESS [--all]
CAPTURE CLEAR
CAPTURE LINKS <url>
CAPTURE STATUS
```

### Pipelines

| Pipeline | Description | Output |
| -------- | ----------- | ------ |
| `markdown` | Clean article text | `.md` |
| `news` | News articles with metadata | `.md` |
| `docs` | Technical documentation | `.md` |
| `recipe` | Recipe with ingredients/steps | `.md` |
| `teletext` | 40-column teletext format | `.txt` |

### Examples

```bash
# Capture URLs to queue
CAPTURE https://example.com/article
CAPTURE https://recipe.com/soup --pipeline recipe
CAPTURE https://docs.python.org/tutorial --pipeline docs

# Manage queue
CAPTURE LIST
CAPTURE PROCESS
CAPTURE PROCESS --all
CAPTURE CLEAR

# Extract links
CAPTURE LINKS https://example.com

# Check status
CAPTURE STATUS
```

### Output Location

Captured content saved to:
```
memory/inbox/captured/
├── 2026-01-07-article-title.md
├── 2026-01-07-soup-recipe.md
└── ...
```

### Queue Storage

Queue persisted in:
```
memory/inbox/.capture.json
```

### Notes

- **Wizard-only**: Requires internet access (Realm B)
- Queue survives restarts
- Use `TILE` to view captured markdown content
- Default pipeline is `markdown`
- Teletext pipeline produces 40-column retro output

---

## Related Commands

- [TILE](navigation.md#tile) - Navigate content
- [FILE](files.md#file) - File operations
- [WELLBEING](user.md#wellbeing) - Energy tracking (affects BUNDLE)
- [OK](howto/commands/wizard.md#ok) - AI assistance for content creation

---

*Part of the [Command Reference](README.md)*
