# Roadmap TODO Tracker

This live tracker lists the remaining development items referenced by `docs/DEV-WORKFLOW-v1.3.1.md` and the milestones map in `docs/specs/v1.3.1-milestones.md`. Update statuses as work progresses.

| Item | Owner | Status | Notes |
| --- | --- | --- | --- |
| Clean up Wizard dashboard navigation | Wizard | Done | Removed Setup menu from top nav and hamburger menu; rebuilt production assets. |
| Finish Wizard Notion UI + plugin dashboard | Wizard | Done | Notion blocks, plugin cards, mod overlay controls, Obsidian-first mapping. |
| Implement Wizard dataset table + chart UI | Wizard | Done | `/api/data/schema` + `/api/data/query` wired with guardrails + export. |
| Prototype Canvas-based teletext renderer | Wizard | Done | Teletext canvas + NES button kit wired in Tables.svelte (`/api/teletext/*`). |
| Harden Beacon Portal + Sonic device catalog APIs | Wizard/Sonic | Done | Beacon routes wired + persisted (configs/quotas/tunnels/cache), auth toggle added, Sonic APIs already admin-guarded. |
| Migrate Goblin binder/Sonic features to Wizard | Goblin/Open | Done | Binder file-backed endpoints + Screwdriver flash-pack routes now live in Wizard. |
| Binder compiler dev endpoints | Goblin | Done | `/api/dev/binders` wired to filesystem + compiler sync. |
| Screwdriver flash pack scaffolding | Goblin | Done | Flash-pack endpoints + payload schema scaffolded. |
| MeshCore device manager scaffolding | Goblin | Done | Device manager + pairing API scaffolded. |
| Dev workflow endpoints | Goblin | Done | Containers/vibe/logs/vault sync endpoints wired. |
| Ship plugin manifest service + registry | Wizard/Extensions | Done | Registry routes + manifest validation service added. |
| Begin App Typo Editor + converters | App | Early dev | Tauri + converter pipeline. |
| Build Groovebox Songscribe stack | Wizard | Planning | Songscribe Markdown, audio synthesis, sample libs. |
| Update `docs/specs/v1.3.1-milestones.md` | Documentation | Done | Milestones summary created. |
| Add DateTimeApproval + TUI story tests | Core | Done | Added regression coverage for approval/override flows. |
| Build script executor + safety guard | Core | Done | Added ScriptExecutor, allowScripts guard, and runtime tests. |
| Hot reload/self-heal training & docs | Core | Done | Automation logging plus `tui` stability guards added, hot-reload debouncing tested and documented. |
| Phase 1B DocumentRunner state/set coverage | Core | Done | DocumentRunner now exercises state/set blocks end-to-end and new TypeScript tests live in `memory/tests/phase1b_*.test.ts`; legacy `__tests__` moved into `memory/tests/legacy`. |
| Memory test scheduler & startup health hook | Core | Done | TUI now polls `~/memory/tests/` for new/changed test files, runs `automation.py`, and surfaces outcomes in the health summary/log. |
| Prepare v1.3.0 release test plan | Documentation | Done | Test plan published in `docs/v1.3.0-release-test.md`. |

> 🔁 Keep this file synchronized with the milestone moves in `docs/DEV-WORKFLOW-v1.3.1.md`.

---

# v1.3.0 Milestone Status

- **Milestone 1**: ✅ Complete (renderer + theme packs + task indexer + Wizard renderer routes wired)

---

# v1.3.1 Milestone 2 (Refactor Roadmap)

Focus: harden publishing + indexing, stabilize Wizard renderer lane, and lock deterministic vault export.

## Milestone 2 goals
- **Renderer reliability**: regression tests, deterministic output, robust path resolution.
- **Task indexer v1**: seed tasks reliably, formalize schema, CLI stability.
- **Wizard API lane**: publish endpoints stable, public local access configured, render trigger audited.
- **Mission outputs**: standard run reports written to `06_RUNS/` on render.
- **Operational docs**: verified runbook for renderer + indexer + Wizard APIs.

## Milestone 2 TODOs
- [x] Add renderer CLI test for output determinism and asset copy results.
- [x] Add indexer tests to validate FK integrity and task parsing.
- [x] Ensure renderer mission report is written to `vault/06_RUNS/`.
- [x] Add spatial DB bootstrap/migration (anchors/places/locids tables) if missing.
- [x] Validate Wizard renderer endpoints: `/api/renderer/themes`, `/site`, `/missions`, `/render`.
- [x] Add minimal auth toggle for local-only renderer routes (documented).
- [x] Update operational docs for renderer + task indexer runbook.

---

# v1.3.2+ Roadmap (Spec-Aligned)

Integrate the attached specs/guides into the future roadmap.

## Canonical contracts to implement
- **Vault Contract**: enforce layout, deterministic indices, and exports. See [docs/Vault-Contract.md](docs/Vault-Contract.md).
- **Theme Pack Contract**: expand pack validation + assets. See [docs/Theme-Pack-Contract.md](docs/Theme-Pack-Contract.md).
- **Engine-Agnostic World Contract**: enforce LocId invariants. See [docs/uDOS-Engine-Agnostic-World-Contract.md](docs/uDOS-Engine-Agnostic-World-Contract.md).

## Spatial universe + anchors
- **Fractal grid + universe mapping** (v1.3.4): ✅ COMPLETE. Anchor registry + LocId parser + validation. See [docs/FRACTAL-GRID-IMPLEMENTATION.md](docs/FRACTAL-GRID-IMPLEMENTATION.md) and [docs/SPATIAL-QUICK-REF.md](docs/SPATIAL-QUICK-REF.md).
- **UGRID core (grid canvas + overlays)** (v1.3.4): implement grid canvas primitives + LocId overlays. See [docs/v1-3%20UGRID-CORE.md](docs/v1-3%20UGRID-CORE.md).
- **Gameplay anchors** (v1.3.5): implement Anchor registry + runtime interfaces. See [sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md](../sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md).
- **World lenses**: Godot 2D/2.5D adapter MVP (v1.3.4), O3DE prototype (v1.3.5). See [docs/v1-3%20-4%203dworld.md](docs/v1-3%20-4%203dworld.md).

## App + TUI alignment
- **App v1.3 refactor**: external vault path, Typo editor, tasks index, export UI. See [docs/uDOS-app-v1-3.md](docs/uDOS-app-v1-3.md).
- **TUI ↔ Vibe integration**: shared IO + keystore boundary. See [docs/TUI-Vibe-Integration.md](docs/TUI-Vibe-Integration.md).
- **Vibe CLI workflow alignment**: Mistral Vibe CLI recommendations mapped to uCODE TUI. See [VIBE-CLI-ROADMAP-ALIGNMENT.md](../VIBE-CLI-ROADMAP-ALIGNMENT.md) for gaps + action plan (v1.3.2+).
- **Vibe capabilities track**: natural language routing, code assistance, and code analysis surfaces. Prototype → testing → feedback loop. See [VIBE-CLI-ROADMAP-ALIGNMENT.md](../VIBE-CLI-ROADMAP-ALIGNMENT.md).
- **uCODE prompt spec**: OK/: commands, slash routing, dynamic autocomplete. See [docs/specs/UCODE-PROMPT-SPEC.md](docs/specs/UCODE-PROMPT-SPEC.md).

## Wizard AI Modes (v1.3.2+)

Define a **Wizard mode contract** and local model defaults for assistant use:

- **Conversation mode**: chat UX + `conversation_id`
- **Creative mode**: prompt templates + temperature preset
- **Local model defaults**: small/fast Ollama models
- **Core access**: route via `/api/ai/complete` with strict offline-first policy

Spec: [docs/specs/AI-MODES-v1.3.md](docs/specs/AI-MODES-v1.3.md)

## Publishing + themes expansion
- Add theme validation tooling based on contract.
- Add additional theme packs (NES/teletext/C64/medium) and test export.
- Add theme preview endpoints for app + wizard dashboard.

---

# v1.3.3 Extension & Container Refactor

Core infrastructure components for distributed, modular architecture.

## Groovebox → Songscribe Stack (library/groovebox + /songscribe container)
- **Status:** ✅ Complete (v1.3.3 scaffolding + APIs + storage)
- **Refactor Groovebox extension** for v1.3 module system:
  - Detach audio synthesis engine from UI layer.
  - Standardize plugin API for sample libraries + effects chains.
  - Publish songscribe Markdown grammar + converters (MIDI, WAV, notation).
  - See [docs/GROOVEBOX-SONGSCRIBE.md](docs/GROOVEBOX-SONGSCRIBE.md).
- **Songscribe container** (library/songscribe):
  - Standalone markdown-to-audio pipeline.
  - Multi-format export (MIDI, WAV, PDF notation).
  - Integration with Wizard task/document renderers.

## Sonic → TUI Entry Point (library/sonic + sonic extension)
- **Status:** ✅ Complete (container manifest + plugin catalog + CLI scaffolding)
- **Refactor Sonic extension** as primary entry to uDOS TUI v1.3:
  - `vibe-cli` powered command-line layer + device catalog.
  - Replace legacy screwdriver toolchain with modular plugin system.
  - Device database sync + USB flashing abstraction.
  - See [core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md](core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md).
- **Sonic module layout** (library/sonic):
  - Device specs, vendor integrations, payload templates.
  - CLI commands wired to Core `PLUGIN` infrastructure.

## Home Assistant Container (library/homeassistant)
- **Refactor Home Assistant integration** for v1.3:
  - Container-based deployment with uDOS config binding.
  - REST/WebSocket gateway to Wizard services.
  - Device discovery + automation templates for Beacon/Sonic workflows.

---

# v1.3.4 Physical & Distributed Systems

Offline-first, proximity-based architecture for hardware ecosystems.

## Alpine Baremetal Concept (distribution/alpine-core)
- **Alpine Linux diskless + persistent overlay**:
  - TUI default tier (Tier 1): OpenRC, shell, minimal services.
  - GUI one-app mode (Tier 2): Wayland + Cage + Tauri single-application session.
  - Adopt Alpine-native plugin system (apk-based, replaces Tiny Core .tcz).
  - See [dev/roadmap/alpine-core.md](dev/roadmap/alpine-core.md).
- **Deliverables**:
  - `udos-gui` launcher script (Wayland session manager).
  - OpenRC service definitions (seatd, cage, tier selection).
  - Tauri app packaging target (/usr/local/bin/udos-ui).
  - Persistence strategy (UDOS_PERSIST partition + apkovl).
  - Recovery/failure mode handling.

## Windows 10 Entertainment Stack (distribution/windows10-entertainment)
- **Status:** 🧱 Scaffolded (layout + controller map + build placeholders)
- **Dual-mode Windows 10 living-room system** (Xbox One form factor reference):
  - Controller-first input grammar (Xbox One controller standard).
  - Media Mode: locked-down Plex Media Player, Kodi, RetroArch, casual games.
  - Game Mode: full performance Windows partition for AAA titles + mods.
  - uDOS bootloader orchestrates mode switching + recovery layer.
  - See [sonic/docs/specs/uDOS_Xbox_Entertainment_Spec.md](../sonic/docs/specs/uDOS_Xbox_Entertainment_Spec.md).
- **Deliverables**:
  - Partition layout (uDOS_BOOT, uDOS_CORE, WINDOWS_MEDIA, WINDOWS_GAMES).
  - Controller input mapper (Xbox One XInput) + system overlay.
  - Media shell launcher (Playnite Fullscreen or custom uDOS Media UI).
  - Clean shutdown + reboot-to-mode flow.
  - Recovery hooks + diagnostics.
  - Windows 10 LTSC image builder with telemetry disabled.

## Beacon Portal Infrastructure (wizard/ + library/beacon)
- **Wi-Fi beacon node**: minimal, stateless, replaceable.
  - SSID announce + WPA2 portal redirect.
  - Graceful offline fallback messaging.
  - No internal storage or mesh routing.
  - See [dev/roadmap/beacon-portal.md](dev/roadmap/beacon-portal.md).
- **Wizard Server** integration:
  - Static IP (192.168.1.10), hostname (wizard.local).
  - Captive portal routes to Wizard dashboard.
  - Tombs + Crypts endpoint for local uploads.
  - Optional MeshCore node for packet relay.
- **Deliverables**:
  - Router firmware agnostic configuration tooling.
  - Beacon status page + offline mode messaging.
  - Wizard captive portal template + auth.

---

# v1.3.5 Wireless & Packet Networks

Long-range, encrypted, opt-in peering for Wizards.

## Wizard Networking Standard (wizard/ + library/meshcore)
- **Three-tier transport layer**:
  - **Beacon Wi-Fi (2.4 GHz)**: human portal, local discovery only.
  - **RadioLink (LoRa/MeshCore)**: long-range, low-bandwidth packet relay, multi-hop.
  - **NetLink (WireGuard)**: encrypted tunneling over internet fallback.
- **Opt-in, proximity-first trust**:
  - Phase A: local pairing (beacon overlap / QR / NFC).
  - Phase B: cryptographic peering (Ed25519 handshake).
  - Durable Wizard↔Wizard relationships, optional VPN tunnel.
  - See [dev/roadmap/wizard-networking.md](dev/roadmap/wizard-networking.md).
- **Packet relay via MeshCore**:
  - Content-addressed, signed, append-only capsules.
  - Manifest exchange + incremental sync.
  - Resilient to intermittent links + long delays.
- **Deliverables**:
  - Peering capsule grammar (JSON/CBOR, signed tokens).
  - QR/NFC pairing flow + capability URLs.
  - RadioLink daemon integration (USB LoRa modem).
  - WireGuard tunnel automation + key rotation.
  - Relay topology calculator for coverage planning.

## MeshCore Integration (library/meshcore)
- **Managed relay network**:
  - Optional relay nodes at elevation (always-on).
  - Wizard auto-discovery within radio range.
  - Replay-safe routing + no auto-peering.
- **Contrast with Meshtastic**:
  - uDOS: managed relays, opt-in trust, lightweight routing.
  - Meshtastic: ecosystem UX, automatic federation.
- **Deliverables**:
  - MeshCore relay daemon (minimal, single responsibility).
  - Topology sync service (relay manifest + coverage map).
  - Web dashboard for relay monitoring.

---

# v1.3.6 Transport & Delivery

Distributed file sync, publishing, and plugin distribution.

## Transport/Delivery Network (distribution/ + library/delivery)
- **Content-addressed packet delivery**:
  - Small MD/text capsules sync over beacon/radio/internet.
  - Deterministic hashing + incremental manifests.
  - Multi-transport failover (beacon → radio → internet).
- **Plugin distribution**:
  - Local USB repository (default, no internet required).
  - Online uDOS repo mirror (opt-in updates).
  - Cryptographic signing + manifest validation.
- **Archive & seed sync**:
  - Wizard ↔ Wizard knowledge/story sync.
  - Encryption boundary at rest + in transit.
  - Resumable transfer on link loss.
- **Deliverables**:
  - Delivery daemon (capsule sync orchestrator).
  - Manifest schema (versions, deps, hashes).
  - Repository tooling (sign, publish, mirror).
  - Web dashboard for sync status + history.
  - CLI commands for manual capsule seeding.
