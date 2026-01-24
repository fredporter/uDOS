# uMarkdown App Migration (dev/app -> app)

Status: Pre-launch planning for Mac App Store and Xcode migration.

## Goals

- Move app workspace from `dev/app` to `/app` in the public repo.
- Link `/app/src` to private submodule `fredporter/uMarkdown-app` for actual code.
- Provide lean workspace and scripts, aligned with uDOS offline-first philosophy.
- Prepare Mac App Store provisioning and Xcode migration path.

## Steps

1. Create `/app` folder with minimal scaffolding (workspace, bin/, docs/).
2. Move `/dev/app` into `/app/src` (done).
3. Deprecate `dev/app` (keep for history in submodule; do not use as source of truth).
4. Add submodule:
   ```bash
   cd app
   git submodule add git@github.com:fredporter/uMarkdown-app.git src
   cd ..
   git add .gitmodules app
   git commit -m "Add uMarkdown-app submodule at /app/src"
   ```
5. Initialize after clone:
   ```bash
   git submodule update --init --recursive
   ```
6. Use `app/bin/start_umarkdown_dev.sh` for local dev.

## Sync Note

If the private submodule repo is empty, initialize it by committing the contents now
in `app/src` and pushing to `fredporter/uMarkdown-app`. Until then, the submodule
will show untracked files.

## macOS Integration Stubs

- Signing & Notarization: configure Tauri `tauri.conf.json` with Apple Developer Team ID.
- Entitlements: sandbox settings for file access, network (Wizard), notifications.
- Xcode migration: generate Xcode project via Tauri build; maintain bridges for future native port.
- App Store: adopt bundle identifiers, versioning from Core version manager; never hardcode.

## Notes

- Business logic lives in Core/Wizard; the App is a GUI.
- Five markdown formats are supported (uCode, Story, Marp, Guide, Config).
- Transport policy applies: no public channel data; private transports only.
