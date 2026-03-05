---
type: sonic-device-settings
format: obsidian-note
version: v1.5
---

# SETTINGS: sonic-device-template-v1

## Purpose
Capture configurable Sonic device settings in an Obsidian-style Markdown note.

## Inputs
- Device id: {{device_id}}
- Profile id: {{profile_id}}
- Settings scope: {{settings_scope}}
- Local note path: {{note_path}}

## Steps
1. Record the active runtime and firmware settings.
2. Capture local overrides and profile-specific defaults.
3. Note any dependencies on Wizard, Sonic, or local-only services.

## Outputs
- {{note_path}}

## Evidence
- Settings note created or updated
- Runtime defaults and overrides recorded
- Related profiles and dependencies linked

## Notes
- Keep this note local when it contains user-specific overrides.
- Seed catalog entries should reference this template path, not embed opaque settings blobs.
