# Xcode Migration Plan (Pre-Launch)

Status: Planning only. Goal is to keep a clean path from Tauri to native macOS.

## Current

- Tauri + Svelte app in private submodule `app/src`.
- Rust backend lives under `app/src/src-tauri`.

## Target

- Generate Xcode project for native builds when required.
- Maintain native bridges for macOS-specific integrations.

## Bridge Stubs (No-Op for now)

- File dialogs: open/save panels
- Notifications
- Menu bar / command palette
- Share sheet
- Deep links / URL scheme

## Migration Strategy

1. Keep data models and render pipeline in TypeScript, compatible with native bridge layer.
2. Add thin Rust -> Swift shims only where needed.
3. Ensure all filesystem access uses sandbox bookmarks.
4. Maintain Apple signing pipeline (CI-driven).

## Notes

- The App is a GUI only. All command execution remains in Core/Wizard.
