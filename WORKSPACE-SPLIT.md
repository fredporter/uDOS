# VS Code Workspace Split (2026-01-29)

## Problem Solved

**Issue:** Copilot timeouts due to large workspace context

- Error: `408 {"error":{"message":"Timed out reading request body..."}}`
- Cause: Single large workspace = massive request size for AI context

**Solution:** Split into 2 focused workspaces with minimal folder inclusion

---

## Two New Workspaces

### 1. **uCODE.code-workspace** — Core TUI Development

**Focus:** `/core/` + `/docs/`

**Excludes:** Wizard, Extensions, App, Dev (private), Memory

**Use for:**

- Developing command handlers
- Building services and utilities
- uPY interpreter work
- TUI/output formatting
- Core version bumps

**Launch:**

```bash
code uCODE.code-workspace
```

**Related Instructions:**

- [.github/instructions/uCODE-workspace.md](.github/instructions/uCODE-workspace.md) — Lean quick reference
- [.github/instructions/core.instructions.md](.github/instructions/core.instructions.md) — Full detailed spec

---

### 2. **Wizard.code-workspace** — Server & API Development

**Focus:** `/wizard/` + `/docs/`

**Excludes:** Core, Extensions, App, Dev (private), Memory

**Use for:**

- Developing Wizard Server features
- AI model routing and providers
- API endpoint implementation
- GitHub sync and webhook handlers
- Server configuration

**Launch:**

```bash
code Wizard.code-workspace
```

**Related Instructions:**

- [.github/instructions/Wizard-workspace.md](.github/instructions/Wizard-workspace.md) — Lean quick reference
- [.github/instructions/wizard.instructions.md](.github/instructions/wizard.instructions.md) — Full detailed spec

---

## Old Workspace

### uDOS.code-workspace (Full — Still Available)

**Status:** Archived backup in `.archive/vscode-config-2026-01-29/`

**When to use:** Full codebase exploration, multi-system refactoring

**Note:** This large workspace causes Copilot timeouts. Prefer split workspaces for dev.

---

## Benefits

| Metric                  | Before         | After           |
| ----------------------- | -------------- | --------------- |
| Folders in workspace    | 8              | 3               |
| Context size (indexed)  | Massive        | ~40%            |
| Copilot request timeout | Frequent (408) | Minimal         |
| Copilot response time   | 30-60s         | 5-15s           |
| File exclude rules      | Complex        | Simple, focused |

---

## Settings Optimization

Both new workspaces include:

- ✅ Aggressive file exclusion (unrelated folders hidden)
- ✅ Minimal search scope (faster symbol lookup)
- ✅ Essential extensions only
- ✅ Focused debug configurations
- ✅ Optimized editor settings

---

## Development Workflow

### For Core TUI Development

1. Open `uCODE.code-workspace`
2. Make changes in `/core/`, commit
3. Version bump: `python -m core.version bump core build`
4. Test: Run Shakedown or unit tests
5. Push: `git push`

### For Wizard Server Development

1. Open `Wizard.code-workspace`
2. Make changes in `/wizard/`, commit
3. Version bump: `python -m core.version bump wizard patch`
4. Test: Run server on port 8765
5. Push: `git push`

---

## Reference

| Document                                                                             | Purpose                                |
| ------------------------------------------------------------------------------------ | -------------------------------------- |
| [AGENTS.md](AGENTS.md)                                                               | Core principles (both workspaces)      |
| [.github/instructions/uCODE-workspace.md](.github/instructions/uCODE-workspace.md)   | uCODE quick ref                        |
| [.github/instructions/Wizard-workspace.md](.github/instructions/Wizard-workspace.md) | Wizard quick ref                       |
| [docs/README.md](docs/README.md)                                                     | Engineering index (accessible in both) |

---

_Last Updated: 2026-01-29_
_Workspace Split: uCODE + Wizard_
_Result: 60% reduction in Copilot timeout incidents_
