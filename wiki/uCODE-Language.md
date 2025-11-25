# uCODE Language Specification

**Version:** 2.0.0
**Status:** Draft - Phase 4 Development
**Last Updated:** November 25, 2025

---

## Overview

uCODE is a human-readable, markdown-compatible scripting language for uDOS automation. It combines the simplicity of shortcodes with the power of full scripting, enabling both quick one-liners and complex workflows.

### Design Principles

1. **Human-Readable**: Natural language-like syntax
2. **Markdown-Compatible**: Works in .md and .uscript files
3. **Progressive Complexity**: Simple commands → complex scripts
4. **CLI Integration**: Every uCODE command maps to CLI
5. **Self-Documenting**: Inline help and examples

---

## Basic Syntax

### Command Structure

```
[COMMAND|option|$variable]
```

**Components:**
- `COMMAND`: Action to perform (uppercase by convention)
- `option`: Optional parameters (lowercase)
- `$variable`: Dynamic values (prefixed with $)

**Examples:**
```
[HELP]                          # Show help
[HELP|commands]                 # List all commands
[HELP|GENERATE]                 # Help for specific command
[VERSION]                       # Show version
[STATUS]                        # System status
```

### Variables

```
$USER           # Current username
$HOME           # Home directory
$CATEGORY       # Current category context
$DATE           # Current date (YYYY-MM-DD)
$TIME           # Current time (HH:MM:SS)
$WORKSPACE      # Workspace root path
```

**Custom Variables:**
```
$topic = "water purification"
$format = "svg"
$complexity = "detailed"
```

### Comments

```
# This is a comment
// Also a comment
[COMMENT|This is an inline comment]
```

---

## Command Categories

### 1. GENERATE Commands

Create content (guides, diagrams, checklists).

```
[GENERATE|guide|water/purification]
[GENERATE|diagram|fire/triangle|format=svg]
[GENERATE|checklist|emergency/evacuation]
[GENERATE|batch|category=water|type=guide|count=10]
```

**Parameters:**
- `type`: guide, diagram, checklist, reference
- `category`: water, fire, shelter, food, medical, navigation, tools, communication
- `format`: ascii, teletext, svg, markdown
- `complexity`: simple, detailed, technical
- `style`: technical, hand-drawn, hybrid
- `perspective`: isometric, top-down, side, 3d

### 2. CONVERT Commands

Transform content between formats.

```
[CONVERT|pdf-to-md|manual.pdf]
[CONVERT|html-to-teletext|page.html]
[CONVERT|svg-to-ascii|diagram.svg]
[CONVERT|batch|source=pdfs/|target=knowledge/]
```

### 3. REFRESH Commands

Update content to new standards.

```
[REFRESH|--check|all]
[REFRESH|water]
[REFRESH|--force|knowledge/water/purification.md]
[REFRESH|category=$CATEGORY|--report]
```

### 4. MANAGE Commands

Organize and maintain content.

```
[MANAGE|index|rebuild]
[MANAGE|tags|update]
[MANAGE|links|validate]
[MANAGE|cleanup|temp-files]
[MANAGE|backup|knowledge/]
```

### 5. SEARCH Commands

Find and filter content.

```
[SEARCH|water purification]
[SEARCH|category=medical|tag=emergency]
[SEARCH|type=diagram|format=svg]
[SEARCH|quality<0.8]
```

### 6. MISSION Commands

Execute complex workflows.

```
[MISSION|start|complete_knowledge_bank]
[MISSION|status|current]
[MISSION|complete|task-1]
[MISSION|abort|current]
```

### 7. CONFIG Commands

Manage settings and preferences.

```
[CONFIG|theme|teletext-green]
[CONFIG|ai-model|gemini-2.5-flash]
[CONFIG|output-dir|knowledge/custom/]
[CONFIG|get|theme]
[CONFIG|list]
```

### 8. SYSTEM Commands

System operations and monitoring.

```
[SYSTEM|status]
[SYSTEM|logs|tail]
[SYSTEM|clear-cache]
[SYSTEM|version]
[SYSTEM|diagnostics]
```

---

## Advanced Syntax

### Command Chaining

Use `|>` to pipe output between commands:

```
[SEARCH|category=water] |> [REFRESH|--check] |> [REPORT]
```

### Conditional Execution

```
if [SEARCH|quality<0.7] then
  [REFRESH|--force|all]
  [NOTIFY|Quality improved]
fi
```

**Compact syntax:**
```
[IF|quality<0.7|REFRESH|--force]
```

### Loops

```
for category in water fire shelter food
  [GENERATE|guide|$category/basics]
  [GENERATE|diagram|$category/overview|format=svg]
done
```

**Compact syntax:**
```
[FOR|category|water,fire,shelter|GENERATE|guide|$category/basics]
```

### Variables and Substitution

```
$categories = "water,fire,shelter,food,medical,navigation,tools,communication"
$formats = "ascii,teletext,svg"

[FOR|cat|$categories|GENERATE|guide|$cat/overview]
```

### Multi-line Scripts

```uscript
# Daily content maintenance workflow

# 1. Check quality
[REFRESH|--check|all] |> [REPORT|save=logs/quality_$DATE.txt]

# 2. Update low-quality content
if [SEARCH|quality<0.8|count] > 10 then
  [REFRESH|all]
  [NOTIFY|Updated low-quality content]
fi

# 3. Rebuild indexes
[MANAGE|index|rebuild]
[MANAGE|tags|update]

# 4. Backup
[MANAGE|backup|knowledge/|target=backups/knowledge_$DATE/]

# 5. Generate report
[REPORT|daily|email=$USER@localhost]
```

---

## Script Files (.uscript)

### File Structure

```uscript
---
title: Startup Options
description: Configure environment on startup
version: 1.0.0
author: uDOS
---

# Startup Configuration

## Environment Setup
[CONFIG|theme|teletext-green]
[CONFIG|output-dir|knowledge/]
[CONFIG|ai-model|gemini-2.5-flash]

## Load Extensions
[EXTENSION|load|ok-assist]
[EXTENSION|load|teletext-renderer]

## Verify System
[SYSTEM|diagnostics]
[SYSTEM|status]

## Welcome Message
[NOTIFY|uDOS ready - Type HELP for commands]
```

### Metadata Block

YAML frontmatter (optional):
```yaml
---
title: Script Name
description: What this script does
version: 1.0.0
author: Username
tags: [automation, maintenance, content]
schedule: "0 0 * * *"  # cron format
---
```

### Sections

Use markdown headers to organize:
```uscript
# Main Script Title

## Section 1: Setup
[commands here]

## Section 2: Processing
[commands here]

## Section 3: Cleanup
[commands here]
```

---

## Command Reference Format

### Template

```
COMMAND_NAME [options] [arguments]

Description:
  Brief description of what the command does.

Options:
  --option1       Description of option 1
  --option2=VAL   Description of option 2 (with value)

Arguments:
  arg1            Description of argument 1
  arg2            Description of argument 2 (optional)

Examples:
  [COMMAND|arg1]
  [COMMAND|arg1|--option1]
  [COMMAND|arg1|--option2=value]

Related:
  - RELATED_COMMAND1
  - RELATED_COMMAND2
```

---

## Integration with CLI

Every uCODE command maps to a CLI command:

```bash
# uCODE
[GENERATE|guide|water/purification]

# CLI equivalent
udos generate guide water/purification

# Python API
from core.commands import generate
generate.create_guide("water/purification")
```

---

## Validation Rules

### Syntax Rules

1. Commands must be in square brackets
2. Command names must be uppercase
3. Parameters separated by pipes (|)
4. Variables prefixed with $
5. Strings can be quoted: "value with spaces"
6. Comments start with # or //

### Parameter Rules

1. Options start with -- (double dash)
2. Flags: --flag (boolean)
3. Values: --option=value
4. Short forms: -f (single dash)

### Variable Rules

1. Must start with letter or underscore
2. Can contain letters, numbers, underscores
3. Case-sensitive
4. Reserved: USER, HOME, DATE, TIME, WORKSPACE, CATEGORY

### Naming Conventions

- **Commands**: UPPERCASE_WITH_UNDERSCORES
- **Options**: lowercase-with-hyphens
- **Variables**: $lowercase_with_underscores
- **Files**: lowercase_with_underscores.uscript

---

## Error Handling

### Try-Catch Blocks

```
try
  [GENERATE|guide|water/purification]
catch error
  [LOG|ERROR|Failed to generate: $error]
  [NOTIFY|Generation failed]
finally
  [CLEANUP]
done
```

**Compact syntax:**
```
[TRY|GENERATE|guide|water/purification|CATCH|LOG|ERROR]
```

### Error Codes

- `0`: Success
- `1`: General error
- `2`: Invalid syntax
- `3`: Missing parameter
- `4`: File not found
- `5`: Permission denied
- `10-99`: Command-specific errors

---

## Best Practices

### 1. Use Descriptive Variable Names

```
# Good
$water_guide_count = 26
$target_quality = 0.8

# Bad
$x = 26
$t = 0.8
```

### 2. Add Comments

```
# Check quality before refreshing
[REFRESH|--check|all]

# Only refresh if quality is low
if quality < 0.8 then
  [REFRESH|all]
fi
```

### 3. Group Related Commands

```
# Quality Maintenance
[REFRESH|--check|all]
[MANAGE|links|validate]
[MANAGE|tags|update]

# Backup
[MANAGE|backup|knowledge/]
```

### 4. Use Constants

```
$QUALITY_THRESHOLD = 0.8
$BACKUP_DIR = "backups/"
$CATEGORIES = "water,fire,shelter,food,medical,navigation,tools,communication"
```

### 5. Handle Errors

```
try
  [GENERATE|guide|$category/$topic]
catch
  [LOG|ERROR|Failed: $category/$topic]
  [NOTIFY|Generation failed - check logs]
done
```

---

## Examples

### Simple One-Liners

```
[HELP]
[GENERATE|guide|water/purification]
[REFRESH|--check|all]
[SEARCH|emergency medical]
[CONFIG|theme|teletext-green]
```

### Medium Complexity

```
# Generate water category diagrams
$category = "water"
[GENERATE|diagram|$category/purification|format=svg|complexity=detailed]
[GENERATE|diagram|$category/collection|format=ascii|complexity=simple]
[GENERATE|diagram|$category/storage|format=teletext|complexity=technical]
```

### Complex Workflow

```uscript
---
title: Weekly Content Maintenance
description: Check quality, update content, generate reports
version: 1.0.0
---

# Weekly Maintenance Workflow

## 1. Quality Audit
[REFRESH|--check|all] |> [REPORT|save=logs/quality_weekly.txt]

## 2. Identify Low Quality
$low_quality = [SEARCH|quality<0.7|--list]

## 3. Update Content
if $low_quality.count > 0 then
  [LOG|INFO|Found $low_quality.count low-quality files]
  [REFRESH|--force|all]
  [NOTIFY|Updated $low_quality.count files]
else
  [LOG|INFO|All content meets quality standards]
fi

## 4. Rebuild Indexes
[MANAGE|index|rebuild]
[MANAGE|tags|update]
[MANAGE|links|validate]

## 5. Generate New Content
for category in water fire shelter food
  [GENERATE|guide|$category/weekly_tip_$DATE]
done

## 6. Backup
[MANAGE|backup|knowledge/|target=backups/weekly_$DATE/]

## 7. Summary Report
[REPORT|weekly|email=admin@localhost]
[LOG|INFO|Weekly maintenance complete]
```

---

## Future Enhancements

### Planned Features (v1.5.0)

1. **Parallel Execution**
   ```
   [PARALLEL|
     [GENERATE|guide|water/purification]
     [GENERATE|guide|fire/starting]
     [GENERATE|guide|shelter/basics]
   ]
   ```

2. **Remote Execution**
   ```
   [REMOTE|peer-node-1|GENERATE|guide|water/purification]
   ```

3. **Event Triggers**
   ```
   on [FILE_CREATED|knowledge/*.md] then
     [REFRESH|--check|$FILE]
   done
   ```

4. **Macros**
   ```
   macro QUALITY_CHECK
     [REFRESH|--check|all]
     [REPORT|save=logs/quality_$DATE.txt]
   end

   [QUALITY_CHECK]  # Expands to macro content
   ```

5. **Interactive Prompts**
   ```
   $category = [PROMPT|Select category|water,fire,shelter]
   [GENERATE|guide|$category/overview]
   ```

---

## Migration from v1.x

### Old Syntax (v1.x)

```
GENERATE guide water/purification
REFRESH --check all
```

### New Syntax (v2.0)

```
[GENERATE|guide|water/purification]
[REFRESH|--check|all]
```

**Both supported** - v2.0 maintains backward compatibility.

---

## Appendix A: Complete Command List

See [UCODE_REFERENCE.md](UCODE_REFERENCE.md) for complete command reference.

## Appendix B: Grammar Specification

See [UCODE_GRAMMAR.md](UCODE_GRAMMAR.md) for formal BNF grammar.

## Appendix C: Migration Guide

See [UCODE_MIGRATION.md](UCODE_MIGRATION.md) for v1.x → v2.0 migration.

---

**Maintainer:** @fredporter
**License:** See LICENSE.txt
**Feedback:** GitHub Issues or community forum
