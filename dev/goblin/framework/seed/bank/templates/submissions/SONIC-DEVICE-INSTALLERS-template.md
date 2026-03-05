---
type: sonic-device-installers
format: obsidian-note
version: v1.5
---

# INSTALLERS: sonic-device-template-v1

## Purpose
Capture installer and bootstrap steps for a Sonic-capable device in
Obsidian-style Markdown.

## Inputs
- Device id: {{device_id}}
- Installer lane: {{installer_lane}}
- Source artifacts: {{source_artifacts}}
- Local note path: {{note_path}}

## Steps
1. List the installer flows supported by the device.
2. Record required artifacts, preflight checks, and boot methods.
3. Link related workflow or submission evidence.

## Outputs
- {{note_path}}

## Evidence
- Installer note created or updated
- Supported install lanes documented
- Preflight requirements and artifacts linked

## Notes
- Use this for install guidance, not mutable runtime state.
