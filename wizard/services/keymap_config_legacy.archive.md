# Archived: Inline Hotkey Keymap Resolvers (2026-02-17)

Legacy duplicated implementations were removed from:

- `wizard/routes/ucode_meta_routes.py`
- `wizard/web/app.py`

They were replaced by the shared service:

- `wizard/services/keymap_config.py`

Reason:

- Duplicate keymap resolution logic created drift risk between API and fallback web UI.
- Shared helper now centralizes profile/OS/self-heal normalization and update semantics.

Git history contains full prior implementations.
