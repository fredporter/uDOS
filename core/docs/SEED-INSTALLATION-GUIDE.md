# Seed Installation Guide

This guide ensures the local memory/bank/seed structure is healthy so the Core
TUI can rely on consistent data after every setup pass.

## 1. Directory layout

| Path | Purpose |
|---|---|
| `memory/` | Streaming state storage for uDOS components |
| `memory/bank/` | Seed/bank data used by the CLI, TUI, and Sonic loaders |
| `core/framework/seed/` | Canonical seed data tracked inside the repo |
| `core/framework/seed/bank/` | Rich bank seed content (graphics, files, templates) |

Each path should exist before shipping the Core TUI experience. The setup story
prints the status of these directories at the end so you can verify that the
runtime view matches the filesystem.

## 2. Seed synchronization checklist

1. Run `REPAIR --seed` (or copy `framework/seed/bank/*` into `memory/bank/`) to
   ensure the bank directory has tracked resources.
2. Confirm that `memory/bank/graphics/` contains the expected textures and
   templates by comparing against `core/framework/seed/bank/graphics/`.
3. Validate the device and location seeds with `python3 framework/seed_installer.py`
   if you add new entries.

## 3. Smoke test

After running the TUI setup story:

- The completion banner includes a “System structure” summary listing each path.
- The summary references this guide (`docs/SEED-INSTALLATION-GUIDE.md`) so you can
  cross-check missing directories.
- Any gaps should also surface in `memory/logs/health-training.log` via the
  Self-Healer diagnostics.

Keeping this structure healthy is a prerequisite for the hot-reload/self-heal
training workflow described in `v1.3.1-milestones.md`.
