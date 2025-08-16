# uDOS Template Library Standard

```
    ████████╗███████╗███╗   ███╗██████╗ ██╗      █████╗ ████████╗███████╗
    ╚══██╔══╝██╔════╝████╗ ████║██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝
       ██║   █████╗  ██╔████╔██║██████╔╝██║     ███████║   ██║   █████╗  
       ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝  
       ██║   ███████╗██║ ╚═╝ ██║██║     ███████╗██║  ██║   ██║   ███████╗
       ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝

    Universal Data Operating System - Template Library Standard v1.3
    ═════════════════════════════════════════════════════════════════════
```

**Version**: 1.3  
**Date**: August 16, 2025  
**Part Number**: uDOS-TMP-STD-001  
**Issue**: 3

---

## Template Structure Standard

### Directory Organization

```
uTemplate/
├── library/                    # Standardized template collection
│   ├── documentation/         # Document templates
│   │   ├── user-manual.md     # User guide template
│   │   ├── technical-spec.md  # Technical specification template
│   │   ├── api-reference.md   # API documentation template
│   │   └── quick-start.md     # Quick start guide template
│   ├── system/                # System output templates
│   │   ├── status-report.md   # System status template
│   │   ├── error-log.md       # Error reporting template
│   │   ├── dashboard.md       # Dashboard layout template
│   │   └── mission-brief.md   # Mission documentation template
│   ├── ascii-art/             # ASCII art components
│   │   ├── logos/            # System logos and branding
│   │   ├── borders/          # Border and frame styles
│   │   ├── icons/            # Small ASCII icons
│   │   └── diagrams/         # Technical diagrams
│   └── formats/               # Output format templates
│       ├── terminal/         # Terminal-optimized layouts
│       ├── markdown/         # Markdown document formats
│       ├── json/             # Structured data templates
│       └── web/              # Web-friendly formats
├── active/                    # User workspace templates
│   ├── current-mission.md    # Active mission template
│   ├── daily-log.md          # Daily activity template
│   └── scratch-pad.md        # General workspace template
└── generated/                 # System-generated outputs
    ├── reports/              # Auto-generated reports
    ├── summaries/            # Data summaries
    └── exports/              # Export formats
```

### Template Header Standard

```markdown
---
# uDOS Template Metadata
template_id: "user-manual-v1"
template_name: "User Manual Template"
version: "1.0"
created_date: "2025-08-16"
author: "uDOS System"
category: "documentation"
tags: ["manual", "user-guide", "documentation"]
description: "Standard template for user documentation"
variables:
  - title: "Document Title"
  - version: "Document Version"
  - date: "Creation Date"
  - author: "Document Author"
usage_notes: "Replace placeholder text in [brackets]"
---
```

### Variable Replacement Syntax

#### Standard Variables
```markdown
{{SYSTEM_NAME}}         # uDOS
{{VERSION}}             # Current system version
{{DATE}}                # Current date
{{TIME}}                # Current time
{{USER_NAME}}           # Current user
{{MISSION_NAME}}        # Active mission
{{PROJECT_PATH}}        # Current project directory
```

#### Dynamic Content Variables
```markdown
{{STATUS_SUMMARY}}      # Auto-generated status
{{RECENT_ACTIVITY}}     # Last 5 activities
{{MEMORY_USAGE}}        # Current memory statistics
{{ACTIVE_MODULES}}      # Loaded modules list
{{ERROR_COUNT}}         # Current error count
{{UPTIME}}              # System uptime
```

#### User-Defined Variables
```markdown
{{CUSTOM:project_name}}    # User-defined project name
{{CUSTOM:client_name}}     # User-defined client
{{CUSTOM:deadline}}        # User-defined deadline
{{INPUT:description}}      # User input prompt
{{INPUT:priority}}         # User selection prompt
```

### ASCII Art Library Standards

#### Logo Templates
```ascii
# Primary Logo (Large)
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ██║   ██║██║  ██║██║   ██║███████╗
    ██║   ██║██║  ██║██║   ██║╚════██║
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

# Compact Logo (Medium)
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

# Mini Logo (Small)
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝
```

#### Border Styles
```ascii
# Standard Frame
┌─────────────────────────────────────────────────┐
│ {{CONTENT}}                                     │
└─────────────────────────────────────────────────┘

# Double Line Frame
╔═════════════════════════════════════════════════╗
║ {{CONTENT}}                                     ║
╚═════════════════════════════════════════════════╝

# Rounded Frame
╭─────────────────────────────────────────────────╮
│ {{CONTENT}}                                     │
╰─────────────────────────────────────────────────╯

# Heavy Frame
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {{CONTENT}}                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

#### Status Indicators
```ascii
# Status Icons
✅ SUCCESS    ❌ ERROR      ⚠️ WARNING
🔄 LOADING    ⏸️ PAUSED     ▶️ RUNNING
📊 DATA       🔍 SEARCH     💾 SAVE
🌐 NETWORK    🔧 CONFIG     📋 LIST

# Progress Bars
▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ 50%
████████████████████ 100%
[##########----------] 50%
```

### Document Templates

#### User Manual Template
```markdown
# {{TITLE}} User Manual

**Version**: {{VERSION}}  
**Date**: {{DATE}}  
**Part Number**: {{PART_NUMBER}}  
**Status**: Current

---

## About This Manual

This manual provides complete instructions for using {{SYSTEM_NAME}} {{VERSION}}.

### Who Should Use This Manual
- {{TARGET_AUDIENCE}}

### What You'll Learn
- {{LEARNING_OBJECTIVES}}

---

## Getting Started

### Prerequisites
> **📋 IMPORTANT**: {{PREREQUISITES}}

### Installation
{{INSTALLATION_STEPS}}

---

## System Overview

{{SYSTEM_DESCRIPTION}}

### Key Features
{{FEATURE_LIST}}

---

## User Guide

### Basic Operations
{{BASIC_OPERATIONS}}

### Advanced Features  
{{ADVANCED_FEATURES}}

---

## Reference

### Command Reference
{{COMMAND_REFERENCE}}

### Troubleshooting
{{TROUBLESHOOTING}}

---

## Appendices

### Appendix A: Error Codes
{{ERROR_CODES}}

### Appendix B: Configuration
{{CONFIGURATION_OPTIONS}}

---

*{{SYSTEM_NAME}} User Manual v{{VERSION}}*  
*{{DATE}}*
```

#### System Status Template
```markdown
# {{SYSTEM_NAME}} Status Report

```ascii
    ██╗   ██╗██████╗  ██████╗ ███████╗
    ╚██████╔╝██████╔╝╚██████╔╝███████║
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

    System Status: {{STATUS}}
    ═══════════════════════════════════
```

**Generated**: {{DATE}} {{TIME}}  
**Uptime**: {{UPTIME}}  
**User**: {{USER_NAME}}

---

## System Overview

| Component | Status | Details |
|-----------|--------|---------|
| Core System | {{CORE_STATUS}} | {{CORE_DETAILS}} |
| Memory | {{MEMORY_STATUS}} | {{MEMORY_USAGE}} |
| Storage | {{STORAGE_STATUS}} | {{STORAGE_USAGE}} |
| Modules | {{MODULE_STATUS}} | {{ACTIVE_MODULES}} |

---

## Recent Activity

{{RECENT_ACTIVITY}}

---

## Current Mission

**Mission**: {{MISSION_NAME}}  
**Status**: {{MISSION_STATUS}}  
**Progress**: {{MISSION_PROGRESS}}

---

## Alerts

{{SYSTEM_ALERTS}}

---

*Report generated by {{SYSTEM_NAME}} v{{VERSION}}*
```

### Template Processing Rules

#### Variable Resolution Order
1. System variables ({{SYSTEM_NAME}}, {{VERSION}})
2. Dynamic content variables ({{STATUS_SUMMARY}})
3. User-defined variables ({{CUSTOM:name}})
4. Input prompts ({{INPUT:field}})
5. Default values for undefined variables

#### Processing Instructions
```bash
# Template processing command format
TEMPLATE PROCESS <template_name> [output_file] [variable_file]

# Examples
TEMPLATE PROCESS user-manual.md manual.md variables.json
TEMPLATE PROCESS status-report.md status.md
```

#### Variable Files (JSON)
```json
{
  "title": "uDOS User Manual",
  "version": "1.2.0",
  "author": "uDOS Team",
  "custom": {
    "project_name": "Project Alpha",
    "client_name": "Client XYZ"
  },
  "input_prompts": {
    "description": "Enter project description:",
    "priority": "Select priority (Low/Medium/High):"
  }
}
```

### Smart Input Integration

#### Input Field Syntax
```markdown
{{INPUT:field_name|type|prompt|default|validation}}

# Examples
{{INPUT:project_name|text|Enter project name|Untitled|required}}
{{INPUT:priority|select|Choose priority|Medium|Low,Medium,High}}
{{INPUT:deadline|date|Project deadline|today+30|date}}
{{INPUT:budget|number|Project budget|1000|positive}}
```

#### Interactive Processing
When processing templates with INPUT fields:
1. System prompts user for each input
2. Validates input against rules
3. Substitutes values into template
4. Generates final document

---

This template library standard provides a comprehensive framework for creating consistent, professional documentation and system outputs while maintaining the retro computing aesthetic that defines uDOS.
