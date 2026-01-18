# uMarkdown App File Formats Specification

**Version:** v1.0.0  
**Status:** Production (App v1.0.3.0)  
**Last Updated:** 2026-01-17  
**Applies To:** macOS app (Tauri + Svelte), iOS/iPadOS (future)

---

## Overview

The uMarkdown App supports five complementary markdown file formats designed for different use cases, all built on a common frontmatter-based structure with semantic execution blocks.

| Format     | Extension    | Purpose                              | Execution | Audience       | Distribution |
| ---------- | ------------ | ------------------------------------ | --------- | -------------- | ------------ |
| **uCode**  | `-ucode.md`  | Executable documents with live logic | Full uPy  | Developers     | Scripts only |
| **Story**  | `-story.md`  | Self-contained interactive forms     | Sandboxed | End users      | Portable     |
| **Marp**   | `-marp.md`   | Full-viewport slide presentations    | None      | Presenters     | Slides only  |
| **Guide**  | `-guide.md`  | Knowledge articles (static)          | None      | Knowledge base | Reference    |
| **Config** | `-config.md` | System configuration as markdown     | Schema    | Admins         | Settings     |

---

## 1. Common Structure (All Formats)

### 1.1 Frontmatter Block

All formats begin with YAML frontmatter (delimited by `---`):

```markdown
---
title: Document Title
description: Short summary
author: Author Name
created: 2026-01-17
version: 1.0.0
tags: [tag1, tag2]
format: ucode # Format-specific identifier
---
```

**Required Fields:**

- `title` — Display name
- `format` — One of: `ucode`, `story`, `marp`, `guide`, `config`

**Optional Fields:**

- `description` — 1-2 sentence summary
- `author` — Creator or maintainer
- `created` — ISO 8601 date
- `version` — Semantic versioning
- `tags` — Array of classification tags
- `icon` — Unicode emoji or icon reference
- `color` — Brand color hex code

### 1.2 Main Content

Markdown body with standard formatting:

- Headings: `# Title`, `## Subtitle`, etc.
- Paragraphs, lists, tables
- Links: `[text](url)` or `[[Internal Link]]`
- Inline code and bold/italic

### 1.3 Data Section

After main content, separated by `---`:

```markdown
---

# Data (Variables, Objects, Functions)

$global_var = value
$config = {
"key": "value",
"nested": {
"value": 123
}
}

$list = [1, 2, 3, 4, 5]
```

**Data Types Supported:**

- Scalars: strings, numbers, booleans, null
- Objects: `{"key": "value", ...}`
- Arrays: `[item1, item2, ...]`
- Dates: `2026-01-17` (ISO format)
- URLs: Full http/https URLs

---

## 2. Format: uCode (`-ucode.md`)

**Purpose:** Executable markdown documents for developers  
**Runtime:** Full uPY interpreter  
**Distribution:** Development only (not portable)  
**Version:** v1.0.0

### 2.1 Frontmatter

```yaml
---
title: Database Migration Script
description: Automated migration from v1 to v2 schema
format: ucode
executable: true
requires:
  - python: "3.9+"
  - dependencies: ["requests", "pyyaml"]
tags: [automation, database, devops]
---
```

**Format-Specific Fields:**

- `executable` — Boolean (default: true)
- `requires` — Dependencies list
- `timeout` — Max execution time in seconds (default: 300)
- `sandbox` — Boolean (default: false - full access)

### 2.2 Code Blocks

Inline executable code with `upy` tag:

````markdown
```upy
# Python code runs in context of this document
import requests
from datetime import datetime

config = $config  # Access data section
tables = config["tables"]

for table in tables:
    print(f"[INFO] Migrating {table}...")
    # Perform migration
```
````

### 2.3 Advanced Features

**Accessing Document Data:**

```python
# Variables from data section automatically available as $variable
user_config = $user_config  # {"name": "Fred", "role": "admin"}
print(user_config["name"])  # Output: Fred
```

**Calling External Services:**

```python
# Can import and use full uPY/Python ecosystem
import sys
sys.path.insert(0, "$UDOS_PATH/extensions")
from api.client import APIClient

client = APIClient(url=$api_url, token=$api_token)
result = client.get("/users")
```

**Persisting State:**

```python
# Output variables become data for next execution
$result = {
    "migrated_tables": 5,
    "errors": 0,
    "timestamp": "2026-01-17T10:30:00Z"
}
```

### 2.4 Example

````markdown
---
title: User Onboarding Automation
format: ucode
executable: true
---

# Automated User Onboarding

This script provisions new users in all systems.

## Process

1. Validate email
2. Create user record
3. Send welcome email
4. Add to mailing lists

## Execution

```upy
import requests
import json
from datetime import datetime

# Get new users from queue
new_users = $pending_users  # from data section

results = {
    "created": [],
    "errors": [],
    "timestamp": datetime.now().isoformat()
}

for user_data in new_users:
    try:
        # Provision user
        resp = requests.post(
            $api_url + "/api/users",
            json=user_data,
            headers={"Authorization": f"Bearer {$api_token}"}
        )
        results["created"].append(user_data["email"])
    except Exception as e:
        results["errors"].append({
            "email": user_data["email"],
            "error": str(e)
        })

# Output for next run
$results = results
print(json.dumps(results, indent=2))
```
````

---

## Data

$api_url = "https://api.example.com"
$api_token = "token_xxxxx" # Store in secure config
$pending_users = [
{"email": "alice@example.com", "name": "Alice Smith"},
{"email": "bob@example.com", "name": "Bob Jones"}
]

````

---

## 3. Format: Story (`-story.md`)

**Purpose:** Self-contained interactive forms and questionnaires
**Runtime:** Sandboxed (no file I/O, no external calls)
**Distribution:** Fully portable (email, share via link, embed)
**Version:** v1.0.0

### 3.1 Frontmatter

```yaml
---
title: Customer Feedback Form
description: Collect post-purchase feedback
format: story
interactive: true
sandboxed: true
expires: "2026-12-31"
tags: [feedback, survey, customer-engagement]
---
````

**Format-Specific Fields:**

- `interactive` — Boolean (default: true)
- `sandboxed` — Boolean (default: true - always true for Story)
- `expires` — Optional expiration date (ISO 8601)
- `prefilled` — Boolean (can be sent with data)

### 3.2 Form Blocks

Use `story` code blocks for form elements:

````markdown
```story
form {
  title: "Customer Feedback",
  fields: [
    {
      name: "email",
      type: "email",
      label: "Email Address",
      required: true
    },
    {
      name: "satisfaction",
      type: "radio",
      label: "How satisfied are you?",
      options: ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied"],
      required: true
    },
    {
      name: "comments",
      type: "textarea",
      label: "Additional comments",
      rows: 5,
      required: false
    }
  ],
  submit: "Send Feedback"
}
```
````

### 3.3 Typeform-Style Interaction

Form submission creates response data:

````markdown
---

## Response Data

```story
# After submission, response available as $response
response = $response

# Example structure:
# {
#   "timestamp": "2026-01-17T15:30:00Z",
#   "email": "user@example.com",
#   "satisfaction": "Very satisfied",
#   "comments": "Great experience!"
# }
```
````

````

### 3.4 Rendering Frontmatter as UI

Frontmatter fields render as buttons/tags in the uMarkdown app header:

```yaml
---
title: Pre-Launch Survey
category: Marketing
priority: high  # 🔴 Red highlight
status: active  # 🟢 Green indicator
---
````

Renders as:

- **Title**: "Pre-Launch Survey" (large)
- **Category**: Marketing (tag)
- **Priority**: 🔴 High (urgent indicator)
- **Status**: 🟢 Active (status badge)

### 3.5 Example

````markdown
---
title: Product Satisfaction Survey
description: Quick feedback about your recent purchase
format: story
interactive: true
---

# Product Satisfaction Survey

Thank you for your purchase! Your feedback helps us improve.

This should take 2-3 minutes.

---

```story
form {
  fields: [
    {
      name: "product_name",
      type: "text",
      label: "What product did you purchase?",
      required: true
    },
    {
      name: "rating",
      type: "slider",
      label: "Rate your satisfaction (1-10)",
      min: 1,
      max: 10,
      required: true
    },
    {
      name: "would_recommend",
      type: "radio",
      label: "Would you recommend to a friend?",
      options: ["Yes", "No", "Maybe"],
      required: true
    },
    {
      name: "feedback",
      type: "textarea",
      label: "Tell us more (optional)",
      rows: 4
    }
  ],
  submit: "Submit Feedback"
}
```
````

---

## Data (for pre-filling)

$product_id = "PROD-12345"
$user_email = "customer@example.com"
$purchase_date = "2026-01-10"

````

---

## 4. Format: Marp (`-marp.md`)

**Purpose:** Full-viewport slideshow presentations
**Runtime:** None (rendering only)
**Distribution:** Standalone presentations (PDF export capable)
**Version:** v1.0.0
**Library:** [Marp](https://marp.app)

### 4.1 Frontmatter

```yaml
---
title: Q1 2026 Product Roadmap
theme: gaia  # Marp theme
paginate: true
footer: "Product Team | Q1 2026"
format: marp
---
````

**Format-Specific Fields:**

- `theme` — Marp theme name (`default`, `gaia`, `uncover`)
- `paginate` — Show slide numbers
- `footer` — Slide footer text
- `header` — Slide header text
- `style` — Custom CSS

### 4.2 Slide Structure

Standard Marp syntax with frontmatter prevention:

```markdown
---
title: Quarterly Roadmap
theme: gaia
---

# Q1 2026 Roadmap

## Product Highlights

---

## Feature 1: Better Search

- Faster queries
- Smart filters
- AI suggestions

---

## Feature 2: Mobile App

- iOS support
- Offline mode
- Push notifications
```

### 4.3 Styling

Apply Marp CSS styling:

```markdown
<!-- _class: lead -->

# Title Slide

### With subtitle

---

<!--
_backgroundColor: #f0f0f0
_textColor: #333
-->

# Custom Styled Slide
```

### 4.4 Example

```markdown
---
title: 2026 Engineering Plan
theme: gaia
paginate: true
footer: "Engineering | Q1 2026"
---

# 2026 Engineering Plan

**Presented:** January 17, 2026  
**Status:** In Progress

---

## Three Key Themes

1. **Performance** — 40% faster queries
2. **Scale** — Support 10M users
3. **Intelligence** — AI-powered features

---

## Detailed Timeline

| Month | Focus | Deliverables |
| ----- | ----- | ------------ |
| Q1    | Core  | Search, Auth |
| Q2    | App   | Mobile, API  |
| Q3    | Scale | CDN, Caching |
| Q4    | AI    | Recommender  |

---

## Questions?

Contact: **engineering@example.com**
```

---

## 5. Format: Guide (`-guide.md`)

**Purpose:** Knowledge articles and reference documents  
**Runtime:** None (reading only)  
**Distribution:** Knowledge base entries  
**Version:** v1.0.0

### 5.1 Frontmatter

```yaml
---
title: How to Set Up SSH Keys
description: Step-by-step guide for SSH key generation
format: guide
category: DevOps
difficulty: beginner # beginner | intermediate | advanced
time_to_read: "10 min"
---
```

**Format-Specific Fields:**

- `category` — Knowledge category
- `difficulty` — Skill level
- `time_to_read` — Estimated reading time
- `related` — Array of related guide IDs or titles

### 5.2 Structured Content

Standard markdown with semantic structure:

````markdown
---
title: Setting Up SSH Keys
category: Security
difficulty: beginner
---

# Setting Up SSH Keys

## Prerequisites

- [ ] Terminal access
- [ ] Git installed
- [ ] 5 minutes

## Steps

### 1. Generate Key Pair

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
````

### 2. Add to SSH Agent

```bash
ssh-add ~/.ssh/id_ed25519
```

### 3. Configure GitHub

[Follow this guide](https://github.com/settings/keys)

## Verification

```bash
ssh -T git@github.com
```

Expected output: `Hi username! You've successfully authenticated.`

## Troubleshooting

**Permission denied?**

- Check file permissions: `chmod 600 ~/.ssh/id_ed25519`

**Key not found?**

- Verify path: `ls -la ~/.ssh/`

## See Also

- [[SSH Config Best Practices]]
- [[Git Configuration]]

````

### 5.3 Knowledge Base Integration

Guides link together via `[[Internal Links]]`:

```markdown
For more on authentication, see [[SSH Key Management]].

Related topics:
- [[Certificate-Based Auth]]
- [[OAuth Setup]]
- [[2FA Configuration]]
````

---

## 6. Format: Config (`-config.md`)

**Purpose:** System configuration as human-readable markdown  
**Runtime:** Schema validation  
**Distribution:** Configuration files  
**Version:** v1.0.0

### 6.1 Frontmatter

```yaml
---
title: Application Configuration
description: Main app config with defaults and docs
format: config
schema_version: "1.0"
---
```

**Format-Specific Fields:**

- `schema_version` — Config schema version
- `validates` — Validation rules (JSON schema)

### 6.2 Configuration Sections

Organize config by feature/module:

````markdown
---
title: Application Configuration
format: config
schema_version: "1.0"
---

# Application Configuration

All settings with defaults and descriptions.

## Database

```config
[database]
host = "localhost"
port = 5432
name = "udos_prod"
pool_size = 20
timeout = 30  # seconds
ssl = true
```
````

## API

```config
[api]
host = "0.0.0.0"
port = 8765
workers = 4
timeout = 60  # seconds
rate_limit = 1000  # requests/min
```

## Logging

```config
[logging]
level = "info"  # debug | info | warn | error
format = "json"
file = "memory/logs/app.log"
retention = 30  # days
```

---

## Advanced (Optional)

```config
[experimental]
enable_feature_x = false
new_auth_system = false
```

````

### 6.3 Validation Schema

Define config validation (JSON Schema):

```markdown
---

## Validation Rules

```json
{
  "type": "object",
  "properties": {
    "database": {
      "type": "object",
      "properties": {
        "host": {"type": "string", "minLength": 1},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
        "pool_size": {"type": "integer", "minimum": 1, "maximum": 100}
      },
      "required": ["host", "port", "name"]
    }
  }
}
````

````

### 6.4 Example

```markdown
---
title: Wizard Server Configuration
format: config
schema_version: "1.0"
---

# Wizard Server Configuration

Production settings for uDOS Wizard server.

## Server

```config
[server]
host = "0.0.0.0"
port = 8765
workers = 4
timeout = 120
log_level = "info"
````

## AI Models

```config
[ai]
default_model = "mistral:small"
openrouter_enabled = false
openrouter_api_key = "${OPENROUTER_KEY}"
budget_monthly = 100  # USD
```

## Database

```config
[database]
path = "memory/wizard.db"
backup_enabled = true
backup_interval = 86400  # seconds (1 day)
```

## Security

```config
[security]
require_auth = true
session_timeout = 3600  # seconds
allow_cors = ["https://localhost:3000"]
```

````

---

## Integration Points

### uMarkdown App (Tauri + Svelte)

**File Format Detection:**
```typescript
const format = filename.split('-').pop().replace('.md', '');
// "user-guide.md" → "guide"
// "api-ucode.md" → "ucode"
````

**Rendering Pipeline:**

1. Parse frontmatter (YAML)
2. Identify format type
3. Render body (standard markdown)
4. Load data section (YAML/JSON)
5. Mount runtime (if executable)

### TypeScript Runtime (iOS/iPadOS)

**Compatible Formats:**

- **uCode** — Full execution (Python) on desktop, TS subset on mobile
- **Story** — Full support (sandboxed form execution)
- **Marp** — Presentation mode only (no edit)
- **Guide** — Full support (read-only)
- **Config** — Validation only (read-only)

### Export & Distribution

| Format | Export  | Portable | Shareable |
| ------ | ------- | -------- | --------- |
| uCode  | `.md`   | No       | No        |
| Story  | `.md`   | **Yes**  | **Yes**   |
| Marp   | `.pdf`  | **Yes**  | **Yes**   |
| Guide  | `.md`   | **Yes**  | **Yes**   |
| Config | `.json` | **Yes**  | No\*      |

\*Configs containing secrets should never be shared without sanitization.

---

## File Naming Conventions

All formats follow the pattern:

```
{name}-{format}.md
```

**Examples:**

- `user-onboarding-ucode.md` — Executable script
- `feedback-survey-story.md` — Interactive form
- `quarterly-roadmap-marp.md` — Presentation
- `api-setup-guide.md` — Knowledge article
- `production-config.md` — Configuration

**Benefits:**

- Clear intent from filename
- Syntax highlighting (markdown)
- Easy to filter and organize
- Works with standard tools

---

## Migration Guide

### From Notion to uMarkdown

| Notion           | uMarkdown Format  |
| ---------------- | ----------------- |
| Database record  | Story (.story.md) |
| Public template  | Story (.story.md) |
| Document         | Guide (.guide.md) |
| Database formula | uCode (.ucode.md) |

### From YAML/JSON Config

```yaml
# Old YAML config
database:
  host: localhost
  port: 5432
```

````markdown
---
title: App Configuration
format: config
---

# Configuration

```config
[database]
host = "localhost"
port = 5432
```
````

```

---

## Best Practices

### uCode Format
- ✅ Use for automation and data processing
- ✅ Include clear error handling
- ✅ Document dependencies in frontmatter
- ❌ Don't use for user-facing interactions
- ❌ Don't store secrets in data section

### Story Format
- ✅ Use for forms and questionnaires
- ✅ Keep logic simple (sandboxed)
- ✅ Provide helpful field labels
- ✅ Pre-fill when possible
- ❌ Don't require external APIs
- ❌ Don't implement complex workflows

### Marp Format
- ✅ Use for slide presentations
- ✅ Keep slides concise
- ✅ Use consistent styling
- ❌ Don't overuse animations
- ❌ Don't embed videos

### Guide Format
- ✅ Use clear hierarchical structure
- ✅ Include code examples
- ✅ Link to related guides
- ✅ Update dates regularly
- ❌ Don't embed large binaries
- ❌ Don't use external CDN assets

### Config Format
- ✅ Provide defaults
- ✅ Include validation schema
- ✅ Document each setting
- ✅ Use environment variables for secrets
- ❌ Don't commit secrets to git
- ❌ Don't version config frequently

---

## Roadmap

### v1.1.0 (Q2 2026)

- [ ] Multi-file imports (`!include "path.md"`)
- [ ] Custom themes for Story format
- [ ] Template inheritance for Config
- [ ] Advanced Marp plugins

### v1.2.0 (Q3 2026)

- [ ] Database binding for uCode (`$db.*`)
- [ ] API endpoints for Story forms
- [ ] Analytics for Guide readership
- [ ] Config diff/merge tools

---

## References

- [Marp Documentation](https://marp.app)
- [Notion Database Templates](https://www.notion.so/templates)
- [YAML Specification](https://yaml.org)
- [JSON Schema](https://json-schema.org)

---

_Last Updated: 2026-01-17_
_App Version: v1.0.3.0_
_Status: Production Ready_
```
