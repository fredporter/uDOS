# Wizard Font Sync & CDN Publish

**Purpose**: Keep the *critical retro fonts* (Chicago FLF, PetMe64, Player2up, Teletext50, etc.) under local control while streaming them to automation-friendly CDNs so the Wizard Font Manager doesn't rely on unstable upstream URLs.

## Local Font Cache (`~/uDOS/fonts`)

1. **Location**: Fonts must reside at `~/uDOS/fonts` (expand `~` to the current user home). The repo should not check these binaries in; they exist only in your local clone and are mounted into production builds. The cache should mirror the following tree:

   ```text
   ~/uDOS/fonts/
   ├── chicago-flf/
   ├── petme64/
   ├── player2up/
   └── teletext50/
   ```

2. **Content**: Each folder holds the canonical `.ttf`/`.otf` files plus a small `metadata.json` describing the source URL, license, and attribution. Keep the metadata consistent with `/fonts/manifest.json` so the Font Manager can rehydrate the same credit list.

3. **Updates**: When new fonts are added (e.g., new fan-made teletext packs), drop them into `~/uDOS/fonts/<collection>` and update `manifest.json`. Do not commit the binaries—only commit the updated manifest/credits.

## CDN Sync (`https://cdn.fredporter.com/`)

1. **Target bucket**: Sync the local cache to `s3://fredporter-cdn/fonts/` (resolves at `https://cdn.fredporter.com/fonts/`). Prefer `aws s3 sync ~/uDOS/fonts s3://fredporter-cdn/fonts --acl public-read --delete` when you have AWS credentials, or run the new `wizard.services.cdn_upload_handler.CdnUploadHandler` (see `wizard/services/cdn_upload_handler.py`) to script uploads inside uDOS with `UDOS_CDN_*` environment variables.
2. **Placement**: Files may be addressed at `https://cdn.fredporter.com/fonts/<collection>/<file>.ttf`. The Font Manager should rewrite distribution URLs to this CDN when requesting fonts in preflight or offline contexts.
3. **Monitoring**: Each sync run should append a line to `~/uDOS/fonts/_sync.log` with the timestamp, file count, and CDN URL base so the Font Tooling can detect drift and re-sync when needed.

## Repository Hygiene

- The `/fonts` tree now contains only metadata, scripts, and manifest files. The binaries are replaced by CDN URLs documented in `manifest.json` and this guide.
- To keep the repo folders in sync with the home-root cache, we seed `/fonts/manifest-sync.json`. It records the expected downloads (retro, emoji, etc.) and mirrors the relative paths inside `~/uDOS/fonts`; automation scripts can load this manifest to verify that every collection exists before calling `wizard.services.cdn_upload_handler.CdnUploadHandler`.
- `docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md` and `docs/WIZARD-OPTIMIZATION-v1.3.1.md` reference this workflow so every milestone cites the same asset story.
- Automations (e.g., font installers or the config page) should read `manifest.json`, detect whether `~/uDOS/fonts` has the files, and fall back to the CDN copy when the local cache is missing.

## Attribution

Keep the following attributions visible in `/fonts/manifest.json` and `docs/WIZARD-FONT-SYNC.md`:

| Font | Source | License | Remarks |
| --- | --- | --- | --- |
| Chicago FLF | https://fontlibrary.org/en/font/chicago-flf | OFL (redistributable) | Retro Mac UI font. |
| PetMe64 | https://style64.org/fonts/ | Free / retro license | Commodore PETSCII. |
| Player 2 Up | https://www.fontsquirrel.com/fonts/player-2-up | OFL | Arcade-style pixel font. |
| Teletext50 | https://github.com/simon-rawles/teletext50 | OFL | BBC Micro teletext blocks. |

- Apple SF Pro and other Apple system fonts remain excluded unless we obtain explicit redistribution rights; they are marked as *local-only* in the manifest.

## Sync Checklist

1. `aws s3 sync ~/uDOS/fonts s3://fredporter-cdn/fonts --acl public-read --delete`
2. Tag the sync run: `date -u '+%Y-%m-%dT%H:%M:%SZ' >> ~/uDOS/fonts/_sync.log`
3. Confirm `/fonts/manifest.json` references the CDN URLs and same licenses.
4. Rebuild the Font Manager preflight snapshot if the manifest changed.
