# uMarkdown App (macOS)

Status: Migration in progress (from dev/app -> app)

This folder hosts the public scaffolding for the macOS uMarkdown App. The actual app code resides under `app/src` and is intended to be a private submodule: fredporter/uMarkdown-app.

## Structure

- App.code-workspace -- Minimal VS Code workspace for app development
- bin/ -- Dev launchers for Tauri
- docs/ -- Migration notes and macOS integration stubs

## Submodule Setup

```bash
# Add private submodule (requires access)
cd app
git submodule add git@github.com:fredporter/uMarkdown-app.git src
cd ..
git add .gitmodules app
git commit -m "Add uMarkdown-app submodule at /app/src"
```

To initialize after cloning:

```bash
git submodule update --init --recursive
```

## Migration Note

- `/dev/app` has been moved into `/app/src` and should be replaced by the private submodule.

## Dev Commands

```bash
cd app/src
npm install
npm run tauri:dev
```

## macOS Integration Stubs

- Xcode migration plan and App Store provisioning in docs/MIGRATION.md
- Sandbox entitlements and signing: provisioned via Tauri config (pre-launch)
- Native bridges: file dialogs, notifications, Apple-specific UX hooks (stubbed under docs/)

## Docs

- docs/MIGRATION.md -- Move from dev/app to app
- docs/APPSTORE.md -- Mac App Store provisioning
- docs/XCODE.md -- Xcode migration notes
- docs/MACOS-INTEGRATION.md -- Integration stubs

## Notes

- Core logic remains in uDOS Core; the App is presentation-only.
- Versioning is managed via core.version across components.
