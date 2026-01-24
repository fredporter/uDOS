# macOS Integration Stubs

This file documents the integration points that must exist in the app, but are stubbed
until the private submodule implements them.

## Integration Points

- File picker / Finder actions
- Clipboard and drag/drop
- Notifications
- Keychain access (for optional tokens)
- Apple Events (optional)
- Menu bar and command palette
- URL scheme and deep links

## File System Policy

- Always use macOS open/save panels.
- For sandboxed builds, store bookmarks for user-granted paths.
- Never assume direct filesystem access outside user-selected paths.

## Offline-First

- App must be functional without network connectivity.
- Cloud routing is Wizard-only; App remains transport/presentation.
