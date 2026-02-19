# uDOS Wiki

Version: v1.4.3
Last Updated: 2026-02-19

Welcome to the uDOS wiki. This folder is the canonical source for GitHub Wiki pages and navigation.

## Quick Start

1. [Home](Home.md)
2. [Installation](Installation.md)
3. [Core](Core.md)
4. [Wizard](Wizard.md)
5. [Architecture](ARCHITECTURE.md)
6. [Contributing](CONTRIBUTING.md)

## Core/Wizard split (v1.4.3)

- Core owns offline/local command surfaces.
- Wizard owns provider/integration/full-system network-aware checks.
- No command shims for removed core commands.
- Canonical command surfaces include `PLACE`, `SEND`, `RUN --ts|--py`, `READ --ts`, and `REBOOT`.

Core checks:

```bash
HEALTH
VERIFY
```

Wizard checks:

```bash
WIZARD CHECK
WIZARD PROV STATUS
WIZARD INTEG status
```

## Documentation

- [Core](Core.md)
- [Wizard](Wizard.md)
- [Architecture](ARCHITECTURE.md)
- [TUI Z-Layer, TOYBOX, and Theme Switching](TUI-Z-Layer-and-TOYBOX.md)
- [TypeScript Runtime](TypeScript-Runtime.md)
- [uCODE Command Reference](../docs/howto/UCODE-COMMAND-REFERENCE.md)
- [Wiki Specification](../docs/specs/wiki_spec_obsidian.md)
- [Consolidated Release Notes (v1.4.3)](../docs/releases/v1.4.3-release-notes.md)

## GitHub Wiki Wiring

- `Home.md` is the wiki landing page.
- `_Sidebar.md` defines left navigation.
- `_Footer.md` defines global footer links.

## Issues and Requests

- Bug reports: `../.github/ISSUE_TEMPLATE/bug_report.md`
- Feature requests: `../.github/ISSUE_TEMPLATE/feature_request.md`
- Documentation requests: `../.github/ISSUE_TEMPLATE/documentation.md`
