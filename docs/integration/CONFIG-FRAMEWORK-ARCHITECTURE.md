# Config Framework Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          WIZARD SERVER (8765)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
         ┌──────────▼──────────┐    │   ┌──────────▼──────────┐
         │  Config Dashboard   │    │   │  Config Editor      │
         │   (Main UI)         │    │   │  (Standalone)       │
         ├─────────────────────┤    │   ├─────────────────────┤
         │ GET /api/v1/config/ │    │   │ GET /api/v1/config/ │
         │     dashboard       │    │   │  editor/ui          │
         └────────┬────────────┘    │   └────────┬────────────┘
                  │                 │            │
         ┌────────▼─────────────────┼────────────▼────────────┐
         │                          │                         │
    ┌────▼──────────────┐    ┌──────▼────────────┐    ┌───────▼──────────┐
    │ API Status Panel  │    │ Config Editor     │    │ Rest API         │
    ├───────────────────┤    │ Panel (Right)     │    ├──────────────────┤
    │ • AI Providers    │    ├───────────────────┤    │ /editor/files    │
    │ • Developer Tools │    │ File Dropdown ▼   │    │ /editor/read/{f} │
    │ • Cloud Services  │    │ [.env] [wiz.json] │    │ /editor/write/{f}│
    │ • Integrations    │    │                   │    │ /framework/reg   │
    │                   │    │ Text Editor Area  │    │ /framework/stat  │
    │ Status Badges:    │    │                   │    │ /dashboard       │
    │ 🟢 Connected      │    │ [💾 Save] [🔄]   │    └──────────────────┘
    │ 🟡 Partial        │    │                   │
    │ 🔴 Missing        │    │ Saved • 47 bytes  │
    └────┬──────────────┘    └───────────────────┘
         │
    ┌────▼──────────────────────────────────────────────────────┐
    │          ConfigFramework Service (Backend)               │
    ├───────────────────────────────────────────────────────────┤
    │                                                           │
    │  class ConfigFramework:                                  │
    │  ├─ _build_registry()                                    │
    │  │  └─ APIRegistry[20+] with metadata                    │
    │  ├─ get_registry_by_category()                           │
    │  │  └─ Organized by: AI, Developer, Cloud, Integrations  │
    │  ├─ _update_statuses()                                   │
    │  │  └─ Check which APIs are configured                   │
    │  ├─ read_env_file() / write_env_file()                   │
    │  ├─ read_config_file() / write_config_file()             │
    │  ├─ get_config_files()                                   │
    │  └─ validate_config()                                    │
    │                                                           │
    │  Singleton Factory: get_config_framework()               │
    └────┬──────────────────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────────────────┐
    │           Config Files (.env, wizard.json, etc.)         │
    ├───────────────────────────────────────────────────────────┤
    │ ~/.udos/                                                  │
    │ ├─ .env (environment variables)                           │
    │ ├─ wizard.json (Wizard config)                            │
    │ └─ ... (other configs)                                    │
    └───────────────────────────────────────────────────────────┘
```

## Component Flow

```
User Opens Dashboard
        │
        ▼
┌─────────────────────────────────┐
│ GET /config/dashboard           │
│ Returns HTML with JS            │
└─────────────┬───────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ loadAPIs()       │  │ loadFile()       │
│ Fetch registry   │  │ Fetch .env       │
│ Parse categories │  │ Display content  │
└──────────────────┘  └──────────────────┘
    │                    │
    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ Render API List  │  │ Render Editor    │
│ • 🟢 OpenAI     │  │ Text Area        │
│ • 🟡 Google     │  │ Save Button      │
│ • 🔴 Anthropic  │  │ Reload Button    │
└──────────────────┘  └──────────────────┘

User Edits Content
        │
        ▼
┌─────────────────────────────────┐
│ textarea.onchange               │
│ hasChanges = true               │
│ updateStatus()                  │
└─────────────┬───────────────────┘
              │
        ▼ (Ctrl+S or Click Save)
┌─────────────────────────────────┐
│ POST /editor/write/.env         │
│ { "content": "..." }            │
└─────────────┬───────────────────┘
              │
        ▼ (Success)
┌─────────────────────────────────┐
│ File Saved                       │
│ hasChanges = false              │
│ updateStatus()                  │
│ Show ✅ Saved                   │
└─────────────────────────────────┘
```

## API Registry Structure

```
ConfigFramework.registry = [
    {
        name: "OpenAI",
        category: "ai_providers",
        env_key: "OPENAI_API_KEY",
        status: CONNECTED,
        docs_url: "https://platform.openai.com/docs",
        description: "GPT-4 and other models"
    },
    {
        name: "Google",
        category: "ai_providers",
        env_key: "GOOGLE_API_KEY",
        status: MISSING,
        docs_url: "https://cloud.google.com/docs",
        description: "Vertex AI and Gemini"
    },
    ... (20+ more APIs)
]

Organized by Category:
{
    "ai_providers": [OpenAI, Google, Anthropic, Mistral],
    "developer_tools": [GitHub, GitLab, Gitea, Slack],
    "cloud_services": [AWS, GCP, Azure],
    "integrations": [Notion, Gmail, HubSpot, Airtable, Stripe, etc.]
}
```

## Status Tracking Flow

```
ConfigFramework.get_registry_by_category()
        │
        ▼
For each API in registry:
    └─ Check if env_key exists in .env?
       ├─ YES: status = CONNECTED
       │       (if validated: status = CONNECTED)
       │       (if not validated: status = PARTIAL)
       └─ NO:  status = MISSING

Return registry with updated statuses
        │
        ▼
Dashboard renders with color badges:
    🟢 CONNECTED (green)
    🟡 PARTIAL (yellow)
    🔴 MISSING (red)
```

## File Management Flow

```
get_config_files()
        │
        ├─ ~/.udos/.env
        ├─ ~/.udos/wizard.json
        └─ ... (other configs)

Read File:
    File Selection ─▶ read_config_file(filename)
                     └─ Load from disk
                     └─ Return content

Write File:
    Editor Content ─▶ write_config_file(filename, content)
                     └─ Validate path (no ../)
                     └─ Write to disk
                     └─ Return success/error
```

## Security Flow

```
User Request: POST /editor/write/.env

    ▼ Validate filename
    └─ Must be in known files list
    └─ No ../ allowed
    └─ Only safe paths

    ▼ Validate content
    └─ Check for max size
    └─ Check for invalid chars (optional)

    ▼ Write to file
    └─ Safe file operations
    └─ Error handling

    ▼ Return response
    └─ Success or error (no system info leaked)
```

## Responsive Layout

### Desktop (>1024px)

```
┌──────────────────────────────────────────────────┐
│ Configuration Dashboard                          │
├──────────────────────┬──────────────────────────┤
│  API Status          │  Config Editor           │
│  (Left Panel)        │  (Right Panel)           │
│  40% width           │  60% width               │
│                      │                          │
│ 📡 APIs...           │ File [.env ▼]            │
│ 🟢 OpenAI           │ ┌──────────────────────┐  │
│ 🟡 Google           │ │ OPENAI_KEY=sk-...   │  │
│ 🔴 Anthropic        │ │ GOOGLE_KEY=...      │  │
│                      │ │                      │  │
│ 💻 Developer...      │ │ [💾 Save] [🔄 Rel]  │  │
│ 🟢 GitHub           │ └──────────────────────┘  │
│ 🔴 GitLab           │ ✓ Saved • 47 bytes       │
└──────────────────────┴──────────────────────────┘
```

### Tablet (768-1024px)

```
┌──────────────────────────────────────────────┐
│ Configuration Dashboard                      │
├──────────────────────────────────────────────┤
│  API Status                                  │
│  (Top Panel - Full Width)                    │
│                                              │
│ 📡 AI Providers: 🟢🟡🔴                      │
│ 💻 Developer: 🟢🔴                          │
│ ☁️  Cloud: 🟢🟡                             │
│                                              │
├──────────────────────────────────────────────┤
│  Config Editor                               │
│  (Bottom Panel - Full Width)                 │
│                                              │
│ File: [.env ▼] [💾 Save] [🔄 Reload]       │
│ ┌──────────────────────────────────────────┐ │
│ │ OPENAI_KEY=sk-...                        │ │
│ │ GOOGLE_KEY=...                           │ │
│ │ ...                                      │ │
│ └──────────────────────────────────────────┘ │
│ ✓ Saved • 47 bytes • 3 lines                 │
└──────────────────────────────────────────────┘
```

### Mobile (<768px)

```
┌──────────────────────────────┐
│ Configuration Dashboard      │
├──────────────────────────────┤
│  Config Editor               │
│  (Full Width)                │
│                              │
│ File: [.env ▼]              │
│ ┌──────────────────────────┐ │
│ │ OPENAI_KEY=sk-...       │ │
│ │ GOOGLE_KEY=...          │ │
│ │                          │ │
│ │                          │ │
│ └──────────────────────────┘ │
│ [💾 Save] [🔄 Reload]        │
│ ✓ Saved • 47 bytes           │
│                              │
├──────────────────────────────┤
│  API Status (Scrollable)     │
│  (Below Editor)              │
│                              │
│ 📡 AI Providers:             │
│ ├─ 🟢 OpenAI - Connected    │
│ ├─ 🟡 Google - Partial      │
│ └─ 🔴 Anthropic - Missing   │
│                              │
│ 💻 Developer Tools:          │
│ ├─ 🟢 GitHub - Connected    │
│ └─ 🔴 GitLab - Missing      │
└──────────────────────────────┘
```

## Integration with Wizard Server

```
FastAPI Application (wizard/server.py)
│
├─ Core Routes
│  ├─ /health
│  └─ /ws
│
├─ Plugin Routes
│  └─ /api/v1/plugin/*
│
├─ Config Routes (Existing)
│  ├─ /api/v1/config/status
│  ├─ /api/v1/config/keys
│  └─ /api/v1/config/panel
│
├─ Config Framework Routes (New)
│  ├─ /api/v1/config/framework/registry  ◄─ From config.py
│  └─ /api/v1/config/framework/status    ◄─ From config.py
│
├─ Config Editor Routes (New)             ◄─ From config_editor.py
│  ├─ /api/v1/config/editor/files
│  ├─ /api/v1/config/editor/read/{file}
│  ├─ /api/v1/config/editor/write/{file}
│  └─ /api/v1/config/editor/ui
│
└─ Config Dashboard Route (New)            ◄─ From config_dashboard.py
   └─ /api/v1/config/dashboard
```

## Extension Points

```
ConfigFramework can be extended to other modules:

Example: Database Config Framework
    - Apply same pattern
    - CustomAPI registry for DB services
    - Custom config files (database.json, etc.)
    - Same dashboard + editor UI

Example: Storage Config Framework
    - S3, GCP, Azure storage configs
    - Custom registry for storage providers
    - Same dashboard + editor UI

Example: Email Config Framework
    - SMTP, Gmail, SendGrid configs
    - Custom registry for email providers
    - Same dashboard + editor UI

Pattern:
    1. Create ConfigFramework instance
    2. Customize API registry
    3. Use same dashboard/editor routes
    4. Register in server
    → Instant config management for any module!
```

---

**Visual Architecture Complete**
_Shows system design, data flow, UI responsiveness, and extension pattern_
