# Architecture Decision Records

This directory contains decision records for uDOS.
Each file captures a discrete architectural, design, or technology choice.

---

## System Architecture

| File | Topic |
|------|-------|
| [WIZARD-SERVICE-SPLIT-MAP.md](WIZARD-SERVICE-SPLIT-MAP.md) | Core vs Wizard service ownership boundaries |
| [VAULT-MEMORY-CONTRACT.md](VAULT-MEMORY-CONTRACT.md) | Secret vault storage contract and memory layout |
| [data-layer-architecture.md](data-layer-architecture.md) | Data layer design (SQL/JSON/Python parity) |
| [UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md](UDOS-VM-REMOTE-DESKTOP-ARCHITECTURE.md) | VM and remote desktop topology (Apple Silicon) |

## Provider & Cloud Integration

| File | Topic |
|------|-------|
| [OK-update-v1-4-6.md](OK-update-v1-4-6.md) | OK-mode cloud provider contract updates for v1.4.6 |
| [MCP-API.md](MCP-API.md) | MCP API integration design |

## AI & LLM Backend

| File | Topic |
|------|-------|
| [TUI-Vibe-Integration.md](TUI-Vibe-Integration.md) | TUI ↔ Vibe LLM integration design |
| [vibe-cli-architecture-fix-v1-4-6.md](vibe-cli-architecture-fix-v1-4-6.md) | Vibe CLI architecture fixes for v1.4.6 |
| [vibe-cli-implementation-status-v1-4-6.md](vibe-cli-implementation-status-v1-4-6.md) | Vibe CLI implementation status at v1.4.6 |
| [vibe-cli-integration-plan-v1-4-6.md](vibe-cli-integration-plan-v1-4-6.md) | Vibe CLI integration plan for v1.4.6 |

## uHOME & Home Automation

| File | Topic |
|------|-------|
| [HOME-ASSISTANT-BRIDGE.md](HOME-ASSISTANT-BRIDGE.md) | uDOS ↔ Home Assistant bridge design |
| [uHOME-spec.md](uHOME-spec.md) | uHOME subsystem specification |

## Sonic & Media Stack

| File | Topic |
|------|-------|
| [SONIC-DB-SPEC-GPU-PROFILES.md](SONIC-DB-SPEC-GPU-PROFILES.md) | Sonic DB schema, GPU profiles, thin UI launch profiles |

## Platform & Runtime

| File | Topic |
|------|-------|
| [alpine-linux-spec.md](alpine-linux-spec.md) | Alpine Linux deployment specification |
| [UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md](UDOS-ALPINE-THIN-GUI-RUNTIME-SPEC.md) | Alpine thin-GUI runtime (Chromium kiosk) |
| [UDOS-PYTHON-CORE-STDLIB-PROFILE.md](UDOS-PYTHON-CORE-STDLIB-PROFILE.md) | Python stdlib profile (no-networking mode) |
| [UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md](UDOS-PYTHON-ENVIRONMENTS-DEV-BRIEF.md) | Python environment management dev brief |
| [uDOS-v1-3.md](uDOS-v1-3.md) | uDOS v1.3 platform architecture snapshot |

## Developer Experience & Tooling

| File | Topic |
|------|-------|
| [LOGGING-API-v1.3.md](LOGGING-API-v1.3.md) | Logging API contract (v1.3) |
| [TERMINAL-STYLING-v1.3.md](TERMINAL-STYLING-v1.3.md) | Terminal styling standards (v1.3) |
| [formatting-spec-v1-4.md](formatting-spec-v1-4.md) | Code and output formatting spec (v1.4) |
| [OBSIDIAN-INTEGRATION.md](OBSIDIAN-INTEGRATION.md) | Obsidian knowledge base integration design |
