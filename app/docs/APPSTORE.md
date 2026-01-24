# Mac App Store Provisioning (Pre-Launch)

Status: Planning and placeholders only. Do not hardcode secrets or identifiers.

## Checklist

- [ ] Register app identifiers (bundle ID, team ID) in Apple Developer
- [ ] Create App Store Connect record
- [ ] Define app category + age rating
- [ ] Set versioning policy: use core.version manager only
- [ ] Configure notarization + signing in Tauri (release pipeline)
- [ ] Prepare privacy labels and data usage summary
- [ ] Ensure file access is user-consented (sandbox bookmarks)

## Versioning

- Never hardcode versions in app config.
- Use: `python -m core.version bump app <patch|build>`
- Reflect version in Tauri config at build time (scripted).

## Notes

- App is a presentation layer. No business logic.
- Use macOS file panels and scoped bookmarks for all filesystem access.
- Keep cloud routing in Wizard only.
