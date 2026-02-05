# uDOS Dev Workflow (v1.3.1+)

This guide reorganizes the uDOS development workflow into **Missions**, **Moves**, **Steps**, and **Milestones**. It replaces time-boxed rounds/cycles with tangible outcomes.

## Terminology (uDOS-native)

- **Mission**: what we are doing and the tangible result we must land.
- **Step**: smallest unit of doing (single action, single file, single check).
- **Move**: counted unit of doing; a bundle of steps that produces a visible result.
- **Milestone**: an achievement composed of one or more moves; completion is objective and testable.

## Workflow Spine

1. **Define the Mission** with a measurable result.
2. **Break the Mission into Moves** that each yield a tangible artifact.
3. **Execute Steps** to complete each Move.
4. **Declare the Milestone** only when every Move has a verified result.

---

# Milestone Map (v1.3.1+)

## Milestone: Publishing + Indexing Reliability
**Mission:** renderer and indexer outputs are deterministic, documented, and operationally stable.

**Moves**
- **Move: Renderer determinism**
  - Steps: ensure asset copy results are deterministic; verify output paths; confirm mission report lands in `vault/06_RUNS/`.
- **Move: Task indexer integrity**
  - Steps: validate FK integrity; seed tasks consistently; lock CLI behavior.
- **Move: Wizard renderer lane**
  - Steps: validate `/api/renderer/*` endpoints; document runbook; confirm local-only auth toggle behavior.

**References:** `docs/ROADMAP-TODO.md`, `docs/Vault-Contract.md`, `docs/Theme-Pack-Contract.md`

---

## Milestone: Core TUI Stability + Self-Heal
**Mission:** the TUI is a reliable operational slab for all automation and command workflows.

**Moves**
- **Move: Story form reliability**
  - Steps: keep `DateTimeApproval` coverage current; ensure fallback handlers survive non-interactive shells.
- **Move: Hot-reload & self-heal trust**
  - Steps: log diagnostics to `memory/logs/health-training.log`; gate repair automation on that log.
- **Move: Command surfaces parity**
  - Steps: preserve CLI/TUI command flows; keep repair + status surfaces aligned with diagnostics.

**References:** `core/ROADMAP-TODO.md`, `docs/TUI-STABILITY-PLAN.md`

---

## Milestone: Wizard Optimization + Hardening
**Mission:** Wizard safely hosts OAuth, plugins, and integrations without drift or abuse.

**Moves**
- **Move: Provider gateway reliability**
  - Steps: cache provider fingerprints; balance routing with quotas; enforce circuit breakers; log provider load.
- **Move: Workflow throughput**
  - Steps: prioritize mission containers; reuse Core services for binder/markdown parsing; expose scheduling signals.
- **Move: Secure API surface**
  - Steps: validate requests; enforce rate limits + policy checks; log throttle history.
- **Move: OAuth + secrets hygiene**
  - Steps: enforce PKCE + scope checks; rotate secrets via keystore; log rotations and failed access attempts.
- **Move: Observability trust**
  - Steps: emit SLO/latency metrics; align dashboard logs with CLI `LOGS` output; snapshot hotkeys for automation.

**References:** `docs/WIZARD-OPTIMIZATION-v1.3.1.md`, `docs/WIZARD-PLUGIN-SYSTEM.md`

---

## Milestone: Wizard Dashboard Surfaces
**Mission:** web UI panels and data surfaces are stable, interactive, and consistent with backend APIs.

**Moves**
- **Move: Notion + plugin dashboard**
  - Steps: keep Notion blocks, plugin cards, and overlay controls in sync with registry state.
- **Move: Dataset tables + charts**
  - Steps: maintain `/api/data/*` guardrails; keep schema/query/export aligned.
- **Move: Teletext UI**
  - Steps: preserve teletext canvas; keep NES-style input wiring consistent with grid data sources.

**References:** `docs/specs/v1.3.1-milestones.md`, `wizard/ARCHITECTURE.md`

---

## Milestone: Beacon + Sonic Catalog
**Mission:** device catalog and beacon portal APIs stay hardened and documented.

**Moves**
- **Move: Beacon portal hardening**
  - Steps: enforce auth toggles; persist configs/quotas; log portal activity.
- **Move: Sonic catalog integrity**
  - Steps: keep device routes admin-guarded; document device schema changes.

**References:** `docs/SONIC-QUICK-START.md`, `sonic/docs/specs/sonic-screwdriver-v1.1.0.md`

---

## Milestone: Goblin Dev Services Graduation
**Mission:** dev endpoints become stable, documented, and ready to migrate into Wizard/Core.

**Moves**
- **Move: Binder compiler endpoints**
  - Steps: keep `/api/dev/binders/*` functional; map migration targets.
- **Move: Flash pack + device manager scaffolds**
  - Steps: finalize payload schema; define pairing flow; document graduation plan.

**References:** `docs/specs/v1.3.1-milestones.md`, `docs/BINDER-SONIC-ENDPOINTS.md`

---

## Milestone: Plugin Ecosystem + Bolt-On Distribution
**Mission:** plugin installs, updates, and permissions are standardized and auditable.

**Moves**
- **Move: Manifest contract**
  - Steps: publish manifest spec; validate signatures; record version lineage in `memory/wizard/plugins.db`.
- **Move: Package manager**
  - Steps: implement `PackageManager` service; add registry endpoints; integrate `PLUGIN` command.

**References:** `docs/PLUGIN-MANIFEST-SPEC.md`, `docs/WIZARD-PLUGIN-SYSTEM.md`

---

## Milestone: App Typo Editor + Converters
**Mission:** the App delivers a stable Typo editor with export conversions.

**Moves**
- **Move: Editor core**
  - Steps: scaffold Tauri shell; wire Typo runtime; confirm storage contract.
- **Move: Converter pipeline**
  - Steps: implement markdown → PDF/HTML; align typography system with uDOS contracts.

**References:** `docs/uDOS-app-v1-3.md`, `app/docs/IMPLEMENTATION-ROADMAP.md`

---

## Milestone: Groovebox + Songscribe
**Mission:** audio creativity stack supports Songscribe syntax and multi-format exports.

**Moves**
- **Move: Songscribe grammar + services**
  - Steps: finalize grammar; wire services to export WAV/MIDI/PDF.
- **Move: Groovebox UI**
  - Steps: build sample browser and pattern editor; confirm playback/export endpoints.

**References:** `docs/GROOVEBOX-SONGSCRIBE.md`, `docs/PHASE-2-COMPLETION.md`

---

## Milestone: Physical + Distributed Systems
**Mission:** offline-first distributions and hardware stacks are scoped with clear deliverables.

**Moves**
- **Move: Alpine baremetal stack**
  - Steps: deliver OpenRC services; finalize persistence strategy; package Tauri app target.
- **Move: Windows entertainment stack**
  - Steps: define partition layout; implement controller mapper; ship recovery workflow.
- **Move: Beacon portal infrastructure**
  - Steps: ship captive portal template; document router-agnostic config tooling.

**References:** `docs/roadmap-spec/alpine-core.md`, `docs/roadmap-spec/beacon-portal.md`

---

## Milestone: Wireless + Packet Networks
**Mission:** opt-in peering and packet relay work across Beacon, RadioLink, and NetLink tiers.

**Moves**
- **Move: Wizard networking standard**
  - Steps: define peering capsule grammar; implement QR/NFC pairing; automate WireGuard tunnels.
- **Move: MeshCore relay integration**
  - Steps: produce relay daemon scaffolding; document topology planning.

**References:** `docs/roadmap-spec/wizard-networking.md`
