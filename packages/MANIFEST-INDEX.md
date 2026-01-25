# v1.0.4.0 Package Manifest Index

Complete formal specification of all uDOS packages: core runtime, production services, dev server, extensions, and knowledge base.

---

## 📦 Package Categories

### Core Runtime (4 manifests)

Essential platform and infrastructure:

| Package               | Version  | Status | Purpose                                     |
| --------------------- | -------- | ------ | ------------------------------------------- |
| **udos-core**         | v1.1.0.0 | stable | TUI + uPY runtime, handlers, services       |
| **udos-api**          | v1.1.0.0 | stable | REST/WebSocket API server                   |
| **udos-secret-store** | v1.0.0.0 | NEW    | Fernet-encrypted tomb + in-memory cache     |
| **udos-port-manager** | v1.0.0.0 | NEW    | Port conflict detection + health monitoring |

**Installation:**

```bash
python -m core.version check        # Core
curl http://localhost:8765/health   # API
bin/wizard-secrets list             # Secrets
bin/port-manager status             # Ports
```

---

### Wizard Production (6 manifests)

Always-on services (port 8765, stable API):

| Package                   | Version  | Status            | Purpose                                           |
| ------------------------- | -------- | ----------------- | ------------------------------------------------- |
| **udos-wizard**           | v1.1.0.0 | production-stable | Device auth, plugin repo, AI routing (port 8765)  |
| **udos-github-service**   | v1.0.4.0 | NEW               | Repo sync, webhooks, PR/issue mgmt                |
| **udos-ai-gateway**       | v1.0.0.0 | stable            | Mistral, OpenRouter, Ollama (local-first)         |
| **udos-workflow-manager** | v1.0.4.0 | NEW               | Organic cron, SQLite-backed tasks                 |
| **udos-sonic**            | v1.0.1.0 | alpha             | Sonic Screwdriver USB builder (plan + Linux exec) |
| **udos-sonic-datasets**   | v1.0.0.0 | NEW               | Device catalog in uDOS format (Markdown+JSON+SQL) |

**Features:**

- ✅ GitHub: Webhook receiver, auto-retry, status sync
- ✅ AI: Mistral + OpenRouter with local-first policy
- ✅ Workflow: Plant→Sprout→Prune→Trellis→Harvest→Compost
- ✅ Sonic Datasets: Device capabilities, reflash potential, methods catalog
- ✅ Auth scopes: github:read|write, ai:route, workflow:read|write

**Launch:**

```bash
bin/Launch-Wizard-Dev.command       # Full server
# OR
python wizard/launch_wizard_dev.py --no-tui  # Server only
```

---

### Goblin Dev Server (3 manifests)

Experimental features (port 8767, localhost-only, breaking changes expected):

| Package                   | Version  | Status       | Purpose                                               |
| ------------------------- | -------- | ------------ | ----------------------------------------------------- |
| **udos-goblin**           | v0.2.0.0 | unstable     | Dev server: Notion, runtime, tasks, binder            |
| **udos-notion-sync**      | v0.1.0.0 | experimental | Phase B: queue + schema (Phase C.3/D deferred)        |
| **udos-runtime-executor** | v0.1.0.0 | experimental | Python stubs; full TS in /core/ (v1.0.0.0 production) |

**API:** `/api/v0/*` (unstable, breaking changes expected)

**Launch:**

```bash
bin/Launch-Goblin-Dev.command
```

---

### Extensions (4 manifests)

Optional feature packs:

| Package             | Version  | Status  | Purpose                                               |
| ------------------- | -------- | ------- | ----------------------------------------------------- |
| **udos-transport**  | v1.0.1.0 | stable  | MeshCore, Audio, QR, NFC, Bluetooth (policy-enforced) |
| **udos-groovebox**  | v0.1.0.0 | planned | Music: MML sequencer + 808 drums (target v1.0.7.0)    |
| **udos-vscode**     | v1.0.0.0 | stable  | VS Code extension + port manager integration          |
| **udos-empire-crm** | v1.0.4.0 | NEW     | Business intelligence: contact DB + HubSpot (stubs)   |

**Installation Mode:**

- transport: automatic (policy validator)
- groovebox: manual (music21 required)
- vscode: automatic (npm compile)
- empire: automatic (init DB)

---

### Knowledge (3 manifests)

Reference material (offline-accessible):

| Package                 | Version  | Type       | Purpose                                             |
| ----------------------- | -------- | ---------- | --------------------------------------------------- |
| **udos-knowledge-base** | v1.0.2.0 | reference  | 231+ articles (tools, frameworks, best practices)   |
| **udos-tech-guides**    | v1.0.0.0 | specs+ADRs | Workspace architecture, decisions, how-to guides    |
| **udos-code-examples**  | v1.0.0.0 | samples    | Handler, service, extension, runtime block examples |

**Usage:**

- Offline reference (no network required)
- In-TUI search or browse knowledge/ directory
- Copy-paste templates for new code

---

## 📋 Complete Manifest List

### Directory Structure

```
packages/
  core/
    ✅ udos-core.manifest.json
    ✅ udos-api.manifest.json
    ✅ udos-secret-store.manifest.json
    ✅ udos-port-manager.manifest.json
  wizard/
    ✅ udos-wizard.manifest.json
    ✅ udos-github-service.manifest.json
    ✅ udos-ai-gateway.manifest.json
    ✅ udos-workflow-manager.manifest.json
  sonic/
    ✅ udos-sonic-datasets.manifest.json
  goblin/
    ✅ udos-goblin.manifest.json
    ✅ udos-notion-sync.manifest.json
    ✅ udos-runtime-executor.manifest.json
  extensions/
    ✅ udos-transport.manifest.json
    ✅ udos-groovebox.manifest.json
    ✅ udos-vscode.manifest.json
    ✅ udos-empire-crm.manifest.json
  knowledge/
    ✅ udos-knowledge-base.manifest.json
    ✅ udos-tech-guides.manifest.json
    ✅ udos-code-examples.manifest.json
```

**Total Manifests:** 17 ✅ Complete

---

## 🔐 Security Model

All manifests reference secret_store (Fernet-encrypted tomb):

- **Secret entries:** API keys, tokens, credentials
- **Unlock:** WIZARD_KEY env (primary) or WIZARD_KEY_PEER (fallback)
- **Storage:** wizard/secrets.tomb (encrypted blob)
- **Management:** bin/wizard-secrets add|list|rotate|export-public

**Secrets per service:**

| Service     | Secrets Required                                |
| ----------- | ----------------------------------------------- |
| Wizard      | device-auth-key, rate-limit-budget              |
| GitHub      | github-personal-main, github-webhook-secret     |
| AI Gateway  | ai-mistral-main, ai-openrouter, budget-tracking |
| Notion Sync | notion-integration-token (feature-flagged)      |
| HubSpot CRM | hubspot-private-app-token                       |

---

## 🚀 Installation Patterns

### Automatic (Scripted)

```bash
# Core
python -m core.version check

# Wizard
python wizard/launch_wizard_dev.py

# Secrets
bin/wizard-secrets add --key-id=github-token --provider=github

# VS Code Extension
code --install-extension udos-vscode/
```

### Manual (User interaction)

```bash
# Groovebox (music extension)
pip install music21 pydub
python -m extensions.groovebox.setup

# Empire CRM
python -m extensions.empire.services.marketing_db --init-db
```

---

## 📊 Version Strategy

Each package independently versioned via manifest.json:

```json
{
  "version": {
    "major": 1,
    "minor": 0,
    "patch": 4,
    "build": 0
  },
  "display": "v1.0.4.0"
}
```

**Version Bumping:**

```bash
python -m core.version bump <component> <part>
# Bumps: udos-core, udos-api, udos-secret-store, udos-port-manager
# Parts: major|minor|patch|build
```

---

## 🔗 Dependencies Map

### Core → Extensions

```
udos-core (v1.1.0.0)
  └─ udos-transport (v1.0.1.0)
  └─ udos-groovebox (v0.1.0.0)
  └─ udos-vscode (v1.0.0.0)

udos-api (v1.1.0.0)
  └─ depends: udos-core ≥1.0.0.0
  └─ udos-vscode (v1.0.0.0)
```

### Wizard → Services

```
udos-wizard (v1.1.0.0, port 8765)
  ├─ udos-github-service (v1.0.4.0)
  ├─ udos-ai-gateway (v1.0.0.0)
  ├─ udos-workflow-manager (v1.0.4.0)
  ├─ udos-sonic-datasets (v1.0.0.0)
  └─ udos-empire-crm (v1.0.4.0)
```

### Goblin → Dev Services

```
udos-goblin (v0.2.0.0, port 8767, localhost-only)
  ├─ udos-notion-sync (v0.1.0.0)
  └─ udos-runtime-executor (v0.1.0.0)
```

---

## 📈 Distribution Channels

### v1.0.4.0 (Current Alpha)

- **Local:** /packages/ (developers, manual installation)
- **Git Releases:** GitHub releases (early adopters)

### v1.0.5.0+

- **Plugin Repository:** Wizard v1.1.0.0+ API (/api/v1/plugins/\*)
- **Package Manager:** brew/apt (Linux/macOS)

### v2.0.0+ (Future)

- **App Store:** iOS/macOS native apps

---

## 🎯 Next Steps

### Immediate (v1.0.4.0)

1. ✅ All 15 manifests created + indexed
2. Validate manifests load as JSON
3. Update distribution/README.md with manifest reference
4. Test installation scripts (automatic + manual)

### Short-term (v1.0.5.0)

- Move GitHub service to Wizard (production-ready)
- Add GitHub event-driven webhooks
- Implement Mac App notifications (Svelte)
- Complete HubSpot CRM sync

### Medium-term (v1.1.0.0)

- Plugin repository API (manifest validation)
- Package manager integration (brew/apt)
- iOS integration testing

---

## 📚 Documentation References

- [packages/README.md](../README.md) — Package types, directory structure, current packages
- [AGENTS.md](../../AGENTS.md) — Workspace boundaries, version management, secrets policy
- [docs/\_index.md](../../docs/_index.md) — Engineering entry point
- [docs/roadmap.md](../../docs/roadmap.md) — v1.0.4.0 status, upcoming releases

---

_Last Updated: 2026-01-17_
_v1.0.4.0 Package Distribution Complete_
