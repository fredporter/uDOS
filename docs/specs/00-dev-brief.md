# v1.3 Dev Brief (drop-in)

## Lanes (locked)
- **Local Portal (Wizard):** hosts MD→HTML on private/local networks (LAN/beacon), permissions + contributions + scheduler.
- **Headless WordPress (separate lane):** public web login/wiki workflows (optional, later). Vault remains truth.

## UI boundary (firm line)
Use **flat HTML** for:
- publishing/browsing rendered Markdown
- offline bundles
- fastest load and simplest portability

Use **app UI** (SvelteKit or Tauri UI) for:
- admin/control plane: missions, queues, approvals, permissions
- interactive dashboards/search

Default:
- Publishing = static HTML
- Control plane = app UI (can be Tauri)

## Runtime split
- **core/**: deterministic transforms (md/json/sqlite/diff/render)
- **wizard/**: portal + sharing + permissions + scheduler + ai-router
- **vibe**: operator console (interactive agent runner), calls core tools

**Prompt contract:** uCODE prompt routing follows [docs/specs/UCODE-PROMPT-SPEC.md](../../docs/specs/UCODE-PROMPT-SPEC.md).
