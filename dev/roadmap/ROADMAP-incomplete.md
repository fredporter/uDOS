# uDOS ROADMAP — INCOMPLETE ROUNDS ONLY

*(Compiled from ROADMAP.md, Gmail Sync Brief, Webhook/API/VS Code Brief, and other relevant uploaded files)*

---

# 0. Overview

This document consolidates all **incomplete / planned** roadmap items for uDOS development. All completed releases have been removed. Only **active**, **planned**, or **not yet implemented** phases remain.

Sources merged:

* ROADMAP.md (pruned sections)
* Gmail Sync Brief (v1.2.9)
* Webhook/API Server + VS Code Extension Brief
* Additional integration briefs uploaded by the user

Completed versions (v1.1.4 → v1.2.8, uPY v2.0.2, etc.) were excluded.

---

# 1. v1.2.9 — Gmail Cloud Sync (PLANNED)

**Mission:** Implement personal Gmail login to enable encrypted cloud sync of lightweight memory/shared files (≈15MB per user).

## 1.1 Gmail Authentication

* OAuth2 login via `LOGIN GMAIL`
* Store encrypted tokens in `.env`
* Refresh token flow & profile retrieval
* Scopes used:

  * Drive AppData (private app folder)
  * Gmail Read/Send
  * User Info

## 1.2 Email Integration

* Download emails as `.eml`
* Convert to uDOS-flavoured Markdown (.md)
* Extract tasks into `tasks.json`
* Delete emails from Gmail after import
* Store outputs under `memory/docs/email/`

## 1.3 Google Drive Sync Engine

* Create `/uDOS-sync/` app folder
* Manage 15MB quota
* Upload/download memory/shared/ucode
* Maintain `sync-manifest.json`
* Conflict resolution: last-write-wins + local history
* File filters: `.md`, `.uPY`, `.json`, text files only

## 1.4 Sync Commands

* `SYNC NOW`
* `SYNC STATUS`
* `SYNC CONFIG`
* `SYNC CONFLICTS`
* `SYNC QUOTA`
* `SYNC HISTORY`

## 1.5 Email Commands

* `EMAIL LIST`
* `EMAIL DOWNLOAD <id>`
* `EMAIL SYNC`
* `EMAIL SEND <to> <subject>`
* `EMAIL TASKS`

---

# 2. Webhook Server — Integration Layer (PLANNED)

**Mission:** Bring event‑driven automation into uDOS.

## 2.1 Incoming Webhooks

Supported platforms:

* Slack
* Notion
* ClickUp
* GitHub

## 2.2 Behaviour

* Convert incoming data to `.md` & store in Tier 2/3/4
* Trigger `.uPY` scripts
* Trigger missions, logs, summaries
* Update dashboards
* API-driven callback patterns

## 2.3 Event Processing

* Normalise payloads
* Hash or ID mapping
* Rate limiting
* Event replay (planned extension of analytics)

---

# 3. API Server — External Access Layer (PLANNED)

**Mission:** Expose controlled REST endpoints for automation and integrations.

## 3.1 Core Endpoints

* `/api/run` — execute `.uPY`
* `/api/memory/add` — add docs/entries
* `/api/memory/search`
* `/api/map/status`
* `/api/mission/<id>`
* `/api/ok/ask` (RBAC-enforced)

## 3.2 Use Cases

* Slack bots
* Notion automations
* ClickUp workflows
* GitHub Actions triggers
* Custom user integrations

---

# 4. VS Code Extension — Developer & Simulation Lab (PLANNED)

**Mission:** Provide a full developer environment for `.uPY`, testing, sandboxing, simulation, and integration work.

## 4.1 Language Support

* Intellisense for `.uPY`
* Syntax highlighting
* Snippets
* Hover documentation

## 4.2 Sandbox Runner

* One-click isolated uDOS instance
* Clear/dev workspace
* Replayable tests

## 4.3 Webhook/API Simulation Tools

* Send mock Slack/Notion/ClickUp/GitHub events
* API route tester panel

## 4.4 Scenario Simulation

* Multi-instance mesh simulation (future)
* Scenario test runner

---

# 5. Cloud POKE (Future v1.2.10+) — Cloud Extension Hosting (PLANNED)

**Mission:** Optional secure HTTPS-based extension publishing.

## 5.1 HTTPS Server

* TLS/SSL certs
* Self‑signed or Let’s Encrypt
* Rate limiting
* CORS
* Access logs

## 5.2 Authentication & Access Control

* API keys
* JWT tokens
* Public / Authenticated / Private modes
* Extension-level ACLs

## 5.3 Extension Publishing

* Validate manifests
* Publish dashboards & GUIs
* Dynamic DNS integration
* Security scanning

## 5.4 Marketplace (Future)

* Browse extensions
* Install from UI
* Ratings & metadata

---

# 6. Remaining Core System Tasks (Unscheduled)

**Mission:** Ongoing improvements not assigned to a version yet.

## 6.1 RBAC (Role-Based Access Control)

* Enforce role limits (User/Power/Wizard/Root)
* Apply to AI access, API, sync, and webhooks

## 6.2 Security Hardening

* CSRF protection
* Input validation
* JSON schema validation
* Abuse throttling
* MeshCore separation guarantee

## 6.3 Knowledge Bank Upgrades

* Additional conversion pipelines (PDF→MD→SVG)
* Citation mandates
* Indexing rules
* Public Tier 4 enhancements

## 6.4 Offline AI Prompt Tools

* Prompt testing
* Prompt versioning
* Scoring & quality metrics

---

# 7. Graphics & Teletext Systems (Additional Phases)

(From graphics system files—future expansion only)

## 7.1 Teletext Renderer Improvements

* Colour discipline enforcement
* Multi‑panel layout builder
* Character mapping validation

## 7.2 Photo & Video Conversion Tools

* Downscaling
* Posterisation
* Palette mapping
* Frame sequencing

---

# 8. Audio, Groovebox, MML/LilyPond Systems (Future)

(From groovebox.md & MML/LilyPond brief)

## 8.1 MML Pattern Generator

* Drum patterns (808)
* Basslines (303)
* Leads/pads (80s)

## 8.2 LilyPond Score Rendering

* Multi-stave
* MIDI export
* Section markers

## 8.3 FX Layer

* Retro game SFX integration (CC0)
* Funny nostalgic SFX support

---

# 9. Teletext/ANSI Art House Style Guide (Support Tasks)

(From teletext.md files — used for content generation)

## 9.1 Templates

* Title pages
* Infographic tiles
* Multi-panel layouts

## 9.2 Constraints

* 40×24 / 80×25 grids
* Max 5 colours
* No gradients or diagonals
* Block geometry only

---

# 10. Future Major Themes (Unscheduled)

* Mesh networking improvements
* Native app packaging (mobile & desktop)
* Local API tunnelling
* Offline-first collaborative editing

---

# 11. Native Apps & Device Spawning (Future Planned)

## 11.1 Tauri Desktop App

* Cross-platform desktop environment using Tauri
* Embedded CLI + Teletext dashboard
* Native menus, notifications, file integration
* Sandbox instances for development
* Offline-first architecture
* Requires RBAC enforcement prior to exposing AI/web features

## 11.2 Mobile Apps (iOS / Android)

* Lightweight field edition of uDOS
* Features: Missions, Maps, Knowledge Library, Tasks, Barter
* Touch-optimised Teletext UI
* Optional sync via Gmail Drive engine

## 11.3 Device Spawning + Mesh Networking

* Spawn lightweight child nodes (mini uDOS devices)
* LoRa-based mesh networking for off-grid
* Knowledge sync between devices
* Strict Cloud vs Mesh network isolation

---

# 12. Graphics Expansion Roadmap (Future)

## 12.1 Teletext / ANSI Renderer Enhancements

* Multi-panel screen generator
* Auto-layout teletext templates
* Dynamic panel builder (titles, sections, grids)
* Block-character shading engine

## 12.2 Photo & Video Teletext Conversion

* Downscale & posterise pipeline
* Teletext palette mapping
* Character-based shading (█ ▓ ▒ ░)
* 6–12 FPS teletext animation export

## 12.3 Graphics Template Library Integration

* Merge panel libraries from graphics1.md / graphics2.md
* System diagrams, flows, timelines, theatre layouts
* Export via MAKE ASCII / MAKE TELETEXT / MAKE SVG

---

# 13. Audio & Groovebox System (Future)

## 13.1 MML Generator

* Generate MML loops for drums, bass, pads, SFX
* 808 drum patterns, 303 basslines, 80s leads
* Pattern chaining + variation support

## 13.2 LilyPond Renderer

* Multi-stave score builder
* MIDI export for LMMS/DAWs
* Section markers & arrangement tools

## 13.3 Retro & Nostalgic SFX Layer

* CC0 retro SFX library integration
* Funny/nostalgic SFX
* Routing into `.uPY` scenarios and missions

---

# END OF INCOMPLETE ROADMAP
