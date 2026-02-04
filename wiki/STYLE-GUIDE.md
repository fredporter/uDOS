# Style Guide (v1.3)

**Version:** v1.3.0  
**Last Updated:** 2026-02-04

This guide keeps uDOS code and docs consistent, predictable, and easy to maintain.

---

## Principles

- **Clarity over cleverness**
- **Offline-first by default**
- **Deterministic outputs**
- **Small, composable modules**

---

## Module Boundaries

- **`core/`** — Offline runtime and uCODE/TUI logic only
- **`wizard/`** — Networking, plugins, AI routing (local-first)
- **`app/`** — UI and client glue only

Avoid cross-layer leakage (no network in Core, no UI logic in Wizard).

---

## Python Style

- Use type hints
- Prefer small functions
- Log with module logger (avoid `print` in production)
- Keep IO at the edges

Example:

```python
def render_document(path: str) -> str:
    """Render a document deterministically."""
    content = read_text(path)
    return render(content)
```

---

## TypeScript Style

- Use strict types
- Keep functions pure when possible
- Export public types from a single barrel

Example:

```ts
export interface RenderResult {
  html: string;
  warnings: string[];
}
```

---

## Documentation Style

- Add **Version** and **Last Updated** at top of key docs
- Keep wiki **beginner‑friendly**
- Put specs in `/docs/specs/`
- Avoid duplicate sources of truth

---

## Versioning Rules

- Don’t hardcode versions in code
- Update versions in `v1.3.0-release-manifest.yml`
- Keep docs aligned with the manifest

---

## Command Surface (uCODE)

- Command names are **UPPERCASE**
- Keep help text short and consistent
- Prefer flags over positional complexity

---

## Logging & Errors

- Include a clear scope tag (e.g. `CORE`, `WIZARD`, `APP`)
- Fail fast on invalid inputs
- Surface actionable errors to users

---

## Keep It Simple

uDOS is about momentum. Favor small, testable changes over complex refactors.
