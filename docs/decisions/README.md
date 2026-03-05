# Architecture Decision Records

This directory contains decision records for uDOS.
Each file captures a discrete architectural, design, or technology choice.

---

## System Architecture

| File | Topic |
|------|-------|
| [WIZARD-SERVICE-SPLIT-MAP.md](WIZARD-SERVICE-SPLIT-MAP.md) | Core vs Wizard service ownership boundaries |
| [VAULT-MEMORY-CONTRACT.md](VAULT-MEMORY-CONTRACT.md) | Secret vault storage contract and memory layout |
| [data-layer-architecture.md](data-layer-architecture.md) | Data layer architecture decision |
| [UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md](UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md) | VM and remote desktop topology decision |

## Provider & Cloud Integration

| File | Topic |
|------|-------|
| [OK-update-v1-4-6.md](OK-update-v1-4-6.md) | Redirect stub to the canonical governance policy |
| [OK-GOVERNANCE-POLICY.md](OK-GOVERNANCE-POLICY.md) | Active governance and terminology policy |
| [MCP-API.md](MCP-API.md) | MCP bridge decision for Wizard and Dev Mode tooling |

## Workflow & Orchestration

| File | Topic |
|------|-------|
| [v1-5-workflow.md](v1-5-workflow.md) | Active v1.5 workflow scheduler decision, scope split, and core/Wizard/extension ownership |
| [v1-5-offline-assist.md](v1-5-offline-assist.md) | Active v1.5 offline assist decision covering `ucode`-first loops, file-backed state, and the `udos_ulogic_pack` reference scaffold |
| [v1-5-logic-input-handler.md](v1-5-logic-input-handler.md) | Active v1.5 smart logic input handler decision for the standard `ucode` runtime |
| [v1-5-workflow-manager.md](v1-5-workflow-manager.md) | Active v1.5 workflow manager standardization decision across core, Wizard, and offline logic |
| [v1-5-python-runtime-contract.md](v1-5-python-runtime-contract.md) | Active v1.5 Python runtime, `.venv`, `uv`, and pytest ownership decision |
| [../specs/WORKFLOW-SCHEDULER-v1.5.md](../specs/WORKFLOW-SCHEDULER-v1.5.md) | Canonical workflow scheduler runtime contract derived from the v1.5 decision |
| [../specs/OFFLINE-ASSIST-STANDARD-v1.5.md](../specs/OFFLINE-ASSIST-STANDARD-v1.5.md) | Canonical offline assist runtime contract derived from the v1.5 decision |

Planning note:
- historical milestone plans were removed from the active decisions tree; current sequencing lives in the local `@dev` roadmap/devlog lane
- contributor-facing decisions now live under `dev/docs/decisions/`
- contributor draft decision submissions now live under `dev/docs/contributors/decisions/`

## OK Provider & Model Runtime

| File | Topic |
|------|-------|
| [v1-5-logic-assist-final-spec.md](v1-5-logic-assist-final-spec.md) | Active v1.5 logic-assist routing and runtime interaction design |
| [v1-5-ucode-tui-spec.md](v1-5-ucode-tui-spec.md) | Active v1.5 `ucode` TUI decision |
| [v1-5-gameplay-3d-thin-gui-assessment.md](v1-5-gameplay-3d-thin-gui-assessment.md) | Pre-release assessment of gameplay/lens scope, 3D extension boundary, and Thin GUI readiness |
| [udos-protocol-v1.md](udos-protocol-v1.md) | Supporting TUI protocol reference |
| [udos-reference-implementation.md](udos-reference-implementation.md) | Supporting TUI reference implementation skeleton |
| [udos-teletext-theme.md](udos-teletext-theme.md) | Supporting teletext theme reference |

## uHOME & Home Automation

| File | Topic |
|------|-------|
| [HOME-ASSISTANT-BRIDGE.md](HOME-ASSISTANT-BRIDGE.md) | uDOS ↔ Home Assistant bridge design |
| [uHOME-spec.md](uHOME-spec.md) | uHOME home profile decision |
| [../specs/UHOME-v1.5.md](../specs/UHOME-v1.5.md) | Canonical v1.5 uHOME runtime and install contract |

## Sonic & Media Stack

| File | Topic |
|------|-------|
| [SONIC-DB-SPEC-GPU-PROFILES.md](SONIC-DB-SPEC-GPU-PROFILES.md) | Sonic DB GPU and launch profile decision |

## Platform & Runtime

| File | Topic |
|------|-------|
| [alpine-linux-spec.md](alpine-linux-spec.md) | Alpine Linux deployment specification |
| [UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md](UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md) | Alpine thin-GUI runtime decision |
| [UDOS-PYTHON-CORE-STDLIB-PROFILE.md](UDOS-PYTHON-CORE-STDLIB-PROFILE.md) | Python stdlib profile (no-networking mode) |
| [UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md](UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md) | Python environment decision |
| [uDOS-v1-3.md](uDOS-v1-3.md) | Historical uDOS v1.3 architecture snapshot |

## Developer Experience & Tooling

| File | Topic |
|------|-------|
| [LOGGING-API-v1.3.md](LOGGING-API-v1.3.md) | Logging API contract (v1.3) |
| [../specs/FORMATTING-SPEC-v1.4.md](../specs/FORMATTING-SPEC-v1.4.md) | Canonical terminal formatting/styling and archival standard |
| [formatting-spec-v1-4.md](formatting-spec-v1-4.md) | Redirect stub to the canonical formatting spec in `docs/specs/FORMATTING-SPEC-v1.4.md` |
| [OBSIDIAN-INTEGRATION.md](OBSIDIAN-INTEGRATION.md) | Obsidian knowledge base integration design |
