# Roadmap Legacy Detail (Archived)

Archived on: 2026-02-11

This file contains the legacy roadmap detail removed from the canonical roadmap. The active roadmap now lives in [docs/roadmap.md](../roadmap.md).

---

## v1.3.0 Milestone Status
- Milestone 1: complete (renderer, theme packs, task indexer, Wizard renderer routes).

## v1.3.1 Milestone 2 (Refactor Roadmap)

Focus: harden publishing and indexing, stabilize Wizard renderer lane, and lock deterministic vault export.

Milestone 2 goals
- Renderer reliability: regression tests, deterministic output, robust path resolution.
- Task indexer v1: seed tasks reliably, formalize schema, CLI stability.
- Wizard API lane: publish endpoints stable, public local access configured, render trigger audited.
- Mission outputs: standard run reports written to `06_RUNS/` on render.
- Operational docs: verified runbook for renderer, indexer, and Wizard APIs.

Milestone 2 TODOs
- [x] Add renderer CLI test for output determinism and asset copy results.
- [x] Add indexer tests to validate FK integrity and task parsing.
- [x] Ensure renderer mission report is written to `memory/vault/06_RUNS/`.
- [x] Add spatial DB bootstrap/migration (anchors/places/locids tables) if missing.
- [x] Validate Wizard renderer endpoints: `/api/renderer/themes`, `/site`, `/missions`, `/render`.
- [x] Add minimal auth toggle for local-only renderer routes (documented).
- [x] Update operational docs for renderer and task indexer runbook.

## v1.3.2+ Roadmap (Spec-Aligned)

Canonical contracts to implement
- Vault Contract: implemented. Core validator checks Markdown presence and recommended layout. See [Vault-Contract.md](../Vault-Contract.md).
- Theme Pack Contract: implemented. Core validator checks shell/theme metadata and required slots. See [Theme-Pack-Contract.md](../Theme-Pack-Contract.md).
- Engine-Agnostic World Contract: implemented. Core validator enforces LocId invariants in vault content. See [uDOS-Engine-Agnostic-World-Contract.md](../uDOS-Engine-Agnostic-World-Contract.md).

Spatial universe and anchors
- Fractal grid and universe mapping (v1.3.4): complete. Anchor registry and LocId parser. See [FRACTAL-GRID-IMPLEMENTATION.md](../FRACTAL-GRID-IMPLEMENTATION.md) and [SPATIAL-QUICK-REF.md](../SPATIAL-QUICK-REF.md).
- UGRID core (grid canvas and overlays) (v1.3.4): complete. See [v1-3 UGRID-CORE.md](../v1-3%20UGRID-CORE.md).
- Gameplay anchors (v1.3.5): implement Anchor registry runtime interfaces. See [sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md](../../sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md).
- World lenses: Godot 2D/2.5D adapter MVP (v1.3.4), O3DE prototype adapter (v1.3.5). See [v1-3 -4 3dworld.md](../v1-3%20-4%203dworld.md).

App and TUI alignment
- Mac app boundary: Obsidian Companion is now external in private pre-release repo `fredporter/oc-app`. Treat it independently from uDOS/uCODE core.
- App v1.3 refactor history remains in legacy docs; active ownership moved to `fredporter/oc-app`.
- TUI and Vibe integration: complete. Wrapper routing merged into uCODE TUI, OK/? and slash routing live. See [TUI-Vibe-Integration.md](../TUI-Vibe-Integration.md).
- Vibe CLI workflow alignment: complete. uCODE TUI owns routing and Vibe output. See [VIBE-CLI-ROADMAP-ALIGNMENT.md](../../VIBE-CLI-ROADMAP-ALIGNMENT.md).
- Vibe capabilities track: natural language routing, code assistance, and code analysis surfaces. Prototype to testing to feedback loop.
- uCODE prompt spec: implemented (OK/? commands, slash routing, dynamic autocomplete). See [specs/UCODE-PROMPT-SPEC.md](../specs/UCODE-PROMPT-SPEC.md).
- Roadmap note: uCODE TUI is the single entry point; Vibe CLI routes through uCODE.
- Dev mode gate: `/dev/` public submodule required and admin-only; see [DEV-MODE-POLICY.md](../DEV-MODE-POLICY.md).
- Core/Wizard boundary: `core` (uCODE runtime) is the base runtime; `wizard` is the brand for connected services. Core can run without Wizard (limited). Wizard cannot run without Core. Most extensions/addons require both Core and Wizard.
- Plugin policy: external services/addons should be cloned (not forked/modified), credited, and updated via pulls. uDOS should containerize and overlay UI without modifying upstream repos.
- Extensions consolidation: note that `/extensions/api` has moved; evaluate whether further consolidation is appropriate now that APIs are outside `/extensions/`.
- Logging API v1.3: implemented. See [LOGGING-API-v1.3.md](../LOGGING-API-v1.3.md).
- Empire business extension: private submodule; isolate business-only features and keep public paths clean.

Wizard AI Modes (v1.3.2+)
- Conversation mode: chat UX and `conversation_id`.
- Creative mode: prompt templates and temperature preset.
- Local model defaults: small/fast Ollama models.
- Core access: route via `/api/ai/complete` with strict offline-first policy.
- Spec: [specs/AI-MODES-v1.3.md](../specs/AI-MODES-v1.3.md).

Publishing and themes expansion
- Add theme validation tooling based on contract.
- Add additional theme packs (NES/teletext/C64/medium) and test export.
- Add theme preview endpoints for app and wizard dashboard.

v1.3.2+ Execution Plan (No Dates)
1. P0 -- Contract Foundation (Core/Docs). Complete. Vault Contract validation, Theme Pack Contract validation, Engine-Agnostic World Contract enforcement in core runtime.
2. P0 -- UGRID Core (Core). Complete. Dependencies: Fractal grid and universe mapping complete. Breakdown: grid canvas primitives, LocId overlays, deterministic render tests, runtime hooks for map blocks.
3. P0 -- Gameplay Anchors (Core/Sonic). Complete. Anchor registry runtime interfaces, validation rules, and TUI adapter surface wired.
4. P1 -- World Lenses (Core/Extensions). Dependencies: UGRID Core. Breakdown: Godot 2D/2.5D adapter MVP, O3DE prototype adapter, minimal integration test harness.
5. P1 -- uCODE Prompt Spec (Core/TUI). Dependencies: none. Breakdown: OK/? commands, slash routing, dynamic autocomplete, shared parser updates.
6. P1 -- TUI and Vibe Integration (Core/Extensions). Dependencies: uCODE Prompt Spec, ENV boundary contract. Breakdown: shared IO boundary, keystore access rules, runtime router wiring.
7. P1 -- Vibe CLI Workflow Alignment (Core). Dependencies: TUI and Vibe Integration. Breakdown: map recommended flows to uCODE commands, close gaps in CLI routing, add UX notes to roadmap.
8. P1 -- Wizard AI Modes (Wizard). Implemented. Breakdown: mode contract (conversation/creative), local model defaults, `/api/ai/complete` policy enforcement.
9. P1 -- Theme Validation Tooling (Wizard/Extensions). Complete. Validator wired in core and Wizard endpoint and dashboard hooks.
10. P2 -- Theme Packs and Previews (Wizard/App). Complete. NES/teletext/C64/medium packs present; preview endpoint and dashboard link added.

## v1.3.3 Extension and Container Refactor

Groovebox to Songscribe stack (library/groovebox + /songscribe container)
- Status: complete (v1.3.3 scaffolding, APIs, storage).
- Refactor Groovebox extension for v1.3 module system:
  - Detach audio synthesis engine from UI layer.
  - Standardize plugin API for sample libraries and effects chains.
  - Publish Songscribe Markdown grammar and converters (MIDI, WAV, notation).
  - See [GROOVEBOX-SONGSCRIBE.md](../../groovebox/docs/GROOVEBOX-SONGSCRIBE.md).
- Songscribe container (library/songscribe):
  - Standalone markdown-to-audio pipeline.
  - Multi-format export (MIDI, WAV, PDF notation).
  - Integration with Wizard task/document renderers.

Sonic to TUI Entry Point (library/sonic + sonic extension)
- Status: complete (container manifest, plugin catalog, CLI scaffolding).
- Refactor Sonic extension as primary entry to uDOS TUI v1.3:
  - `vibe-cli` powered command-line layer and device catalog.
  - Replace legacy screwdriver toolchain with modular plugin system.
  - Device database sync and USB flashing abstraction.
  - See [core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md](../../core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md).
- Sonic module layout (library/sonic):
  - Device specs, vendor integrations, payload templates.
  - CLI commands wired to Core `PLUGIN` infrastructure.

Home Assistant container (library/homeassistant)
- Refactor Home Assistant integration for v1.3:
  - Container-based deployment with uDOS config binding.
  - REST/WebSocket gateway to Wizard services.
  - Device discovery and automation templates for Beacon/Sonic workflows.

## v1.3.4 Physical and Distributed Systems

Alpine baremetal concept (distribution/alpine-core)
- Alpine Linux diskless and persistent overlay:
  - TUI default tier (Tier 1): OpenRC, shell, minimal services.
  - GUI one-app mode (Tier 2): Wayland + Cage + Tauri single-application session.
  - Adopt Alpine-native plugin system (apk-based, replaces Tiny Core .tcz).
  - See [dev/roadmap/alpine-core.md](../../dev/roadmap/alpine-core.md).
- Deliverables:
  - `udos-gui` launcher script (Wayland session manager).
  - OpenRC service definitions (seatd, cage, tier selection).
  - Tauri app packaging target (/usr/local/bin/udos-ui).
  - Persistence strategy (UDOS_PERSIST partition + apkovl).
  - Recovery/failure mode handling.

Windows 10 Entertainment Stack (distribution/windows10-entertainment)
- Status: scaffolded (layout, controller map, build placeholders).
- Dual-mode Windows 10 living-room system (Xbox One form factor reference):
  - Controller-first input grammar (Xbox One controller standard).
  - Media Mode: locked-down Plex Media Player, Kodi, RetroArch, casual games.
  - Game Mode: full performance Windows partition for AAA titles and mods.
  - uDOS bootloader orchestrates mode switching and recovery layer.
  - See [sonic/docs/specs/uDOS_Xbox_Entertainment_Spec.md](../../sonic/docs/specs/uDOS_Xbox_Entertainment_Spec.md).
- Deliverables:
  - Partition layout (uDOS_BOOT, uDOS_CORE, WINDOWS_MEDIA, WINDOWS_GAMES).
  - Controller input mapper (Xbox One XInput) and system overlay.
  - Media shell launcher (Playnite Fullscreen or custom uDOS Media UI).
  - Clean shutdown and reboot-to-mode flow.
  - Recovery hooks and diagnostics.
  - Windows 10 LTSC image builder with telemetry disabled.

Beacon Portal Infrastructure (wizard/ + library/beacon)
- Wi-Fi beacon node: minimal, stateless, replaceable.
  - SSID announce and WPA2 portal redirect.
  - Graceful offline fallback messaging.
  - No internal storage or mesh routing.
  - See [dev/roadmap/beacon-portal.md](../../dev/roadmap/beacon-portal.md).
- Wizard Server integration:
  - Static IP (192.168.1.10), hostname (wizard.local).
  - Captive portal routes to Wizard dashboard.
  - Tombs and Crypts endpoint for local uploads.
  - Optional MeshCore node for packet relay.
- Deliverables:
  - Router firmware-agnostic configuration tooling.
  - Beacon status page and offline mode messaging.
  - Wizard captive portal template and auth.

## v1.3.5 Wireless and Packet Networks

Wizard Networking Standard (wizard/ + library/meshcore)
- Three-tier transport layer:
  - Beacon Wi-Fi (2.4 GHz): human portal, local discovery only.
  - RadioLink (LoRa/MeshCore): long-range, low-bandwidth packet relay, multi-hop.
  - NetLink (WireGuard): encrypted tunneling over internet fallback.
- Opt-in, proximity-first trust:
  - Phase A: local pairing (beacon overlap, QR, NFC).
  - Phase B: cryptographic peering (Ed25519 handshake).
  - Durable Wizard-to-Wizard relationships, optional VPN tunnel.
  - See [dev/roadmap/wizard-networking.md](../../dev/roadmap/wizard-networking.md).
- Packet relay via MeshCore:
  - Content-addressed, signed, append-only capsules.
  - Manifest exchange and incremental sync.
  - Resilient to intermittent links and long delays.
- Deliverables:
  - Peering capsule grammar (JSON/CBOR, signed tokens).
  - QR/NFC pairing flow and capability URLs.
  - RadioLink daemon integration (USB LoRa modem).
  - WireGuard tunnel automation and key rotation.
  - Relay topology calculator for coverage planning.

MeshCore Integration (library/meshcore)
- Managed relay network:
  - Optional relay nodes at elevation (always-on).
  - Wizard auto-discovery within radio range.
  - Replay-safe routing and no auto-peering.
- Contrast with Meshtastic:
  - uDOS: managed relays, opt-in trust, lightweight routing.
  - Meshtastic: ecosystem UX, automatic federation.
- Deliverables:
  - MeshCore relay daemon (minimal, single responsibility).
  - Topology sync service (relay manifest and coverage map).
  - Web dashboard for relay monitoring.

## v1.3.6 Transport and Delivery

Transport/Delivery Network (distribution/ + library/delivery)
- Content-addressed packet delivery:
  - Small MD/text capsules sync over beacon/radio/internet.
  - Deterministic hashing and incremental manifests.
  - Multi-transport failover (beacon to radio to internet).
- Plugin distribution:
  - Local USB repository (default, no internet required).
  - Online uDOS repo mirror (opt-in updates).
  - Cryptographic signing and manifest validation.
- Archive and seed sync:
  - Wizard to Wizard knowledge/story sync.
  - Encryption boundary at rest and in transit.
  - Resumable transfer on link loss.
- Deliverables:
  - Delivery daemon (capsule sync orchestrator).
  - Manifest schema (versions, deps, hashes).
  - Repository tooling (sign, publish, mirror).
  - Web dashboard for sync status and history.
  - CLI commands for manual capsule seeding.
