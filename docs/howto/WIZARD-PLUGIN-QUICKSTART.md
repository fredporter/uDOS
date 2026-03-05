# Wizard Plugin Quickstart

Updated: 2026-03-03
Status: active how-to

## Purpose

Use this guide to get started with Wizard plugin discovery and installation quickly.

## What the Plugin System Covers

Wizard plugin surfaces include:
- distribution plugins
- library containers
- extensions

The system discovers plugin metadata, install pathways, and status through the Wizard control plane.

## Quick Start

### 1. Set the repo root for Wizard git operations

```dotenv
UDOS_ROOT="/path/to/uDOS"
```

### 2. Start Wizard

Run your normal Wizard startup flow, then open the plugin UI.

### 3. Use the plugin routes

Common routes:
- `GET /api/plugins/catalog`
- `GET /api/plugins/{plugin_id}`
- `POST /api/plugins/{plugin_id}/install`

### 4. Check install type

Common install types:
- git-based
- container
- script-based
- apk package

## Companion Guides

- [Wizard Plugin Reference](WIZARD-PLUGIN-REFERENCE.md)
- [Managed Wizard Operations](MANAGED-WIZARD-OPERATIONS.md)
