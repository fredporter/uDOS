# uDOS Vision

**Version:** v1.3.0
**Last Updated:** 2026-02-04
**Status:** Vision / Aspirational

> This document describes the long‑term direction. Not every feature listed is part of the v1.3 release manifest.

**A text-first computing environment for humans who value privacy, simplicity, and offline capability.**

---

## 🎯 What is uDOS?

uDOS is a **Python-venv OS layer** targeting Alpine Linux for minimal hardware while providing powerful features:

- **230+ offline survival guides** in markdown format
- **AI-powered content generation** (local-first via Ollama, optional cloud models)
- **Terminal and desktop interfaces** (TUI + uCode Markdown App)
- **Grid-native navigation** for spatial docs, anchors, and map views
- **Project workflows** (missions) with structured, inspectable outputs
- **Private mesh networking** without internet dependency

## 🏛️ Core Principles

### 1. Text-First Computing

```
Text → Markdown → ASCII/Teletext → SVG (only when essential)
```

Every output starts as text. Graphics exist to serve communication, not decoration.

### 1.1 Retro + Grid Native

- **Retro-first UI** for focus and speed
- **Grid and spatial thinking** built into navigation and layout

### 2. Offline-First / Privacy-First

- **Full functionality without internet**
- **No telemetry, no tracking**
- **Explicit opt-in for any cloud features**
- **Data stays on your device by default**

### 3. Two-Realm Architecture

| Realm             | Purpose   | Internet    | Example                       |
| ----------------- | --------- | ----------- | ----------------------------- |
| **User Mesh**     | Daily use | Never       | Laptops, phones, Alpine nodes |
| **Wizard Server** | AI & web  | When needed | Always-on home server         |

The Wizard Server handles web-dependent tasks (Gemini AI, web scraping, email) and communicates with user devices over **private transports only**.

### 4. Human-Centric Design

- **Drip, don't smash** - Content delivered at sustainable pace
- **Wellbeing awareness** - Tasks adapt to user energy levels
- **Simple over clever** - Obvious beats elegant

---

## AI That Helps (Balanced + Controlled)

uDOS treats AI as a **tool, not a replacement**. It should be useful, bounded, and transparent.

- **Local-first** with explicit opt-in for cloud models
- **Workflow-aligned**: assists planning, summarizing, refactoring, and drafting
- **Balanced outputs**: helpful, concise, and grounded in the current project
- **Controlled behavior**: clear prompts, explicit modes, and predictable output

AI is used to support missions and projects without obscuring how results were produced.

---

## Database Extensions (Projects + Missions)

The core uses SQLite for indexing and storage. Extensions can add **project-oriented tables** and **mission/workflow data** when needed.

- **Core stays simple**: minimal schema, deterministic behavior
- **Extensions add power**: project metadata, task states, mission pipelines
- **Inspectable data**: always readable, exportable, and local-first

---

## Unified TUI Experience (Vibe Integration)

Vibe CLI integration is a key part of a **beginner-friendly** and **powerful** TUI:

- **Guided interactions** for beginners
- **Fast commands** for power users
- **Educational by default** (explainable outputs)
- **Open-box platform**: users can inspect, learn, and extend

---

## 🔒 Transport Policy (Non-Negotiable)

### Private Transports (Data Allowed)

- **MeshCore** - Primary P2P mesh
- **Bluetooth Private** - Paired devices only
- **NFC** - Physical contact transfer
- **QR Relay** - Visual data transfer
- **Audio Relay** - Acoustic packets

### Public Channels (Signal Only)

- **Bluetooth Public** - Presence beacons, NEVER data
- **Internet** - Wizard Server only, never user devices

---

## 💡 Key Concepts

### uCODE Commands

Commands typed in TUI or executed from `.udos.md` scripts:

```bash
GUIDE survival/water      # Browse knowledge
BUNDLE START survival     # Begin learning bundle
CAPTURE https://example.com  # Save web content
MAKE TEXT "water guide"   # Generate with AI
```

### .udos.md Documents

Markdown files with embedded scripts:

````markdown
---
title: Water Purification Guide
type: knowledge
bundle: survival
---

# Water Purification

Methods for making water safe...

```upy
# Embedded script
result = GUIDE.SEARCH("filter")
```
````

````

### Bundles

Collections of related documents with "drip" delivery:

```yaml
# .bundle.udos.md
drip:
  interval: daily
  items_per_session: 1
wellbeing:
  energy_cost: medium
````

---

## 🎯 Target Users

1. **Privacy advocates** - No tracking, no cloud dependency
2. **Offline preppers** - Works without internet
3. **Minimalists** - Runs on minimal hardware
4. **Knowledge seekers** - 230+ survival guides included
5. **Makers & hackers** - Fully customizable

---

## 🚀 Getting Started

1. **TUI Users**: Run `./bin/Launch-uCODE.sh` and type `HELP`
2. **Desktop Users**: Launch uCode Markdown App
3. **Developers**: See [Contributing](../wiki/Contributing.md)

---

_"Computing should serve humans, not surveil them."_
