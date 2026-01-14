# Public / Private Repo Sync Plan

**Last Updated:** 2026-01-14  
**Audience:** Maintainers

---
## Repos
- Private: fredporter/uDOS (source of truth, dev-only content)
- Public: fredporter/uDOS-public (release docs + assets mirror)

---
## What goes where
- Private (keep): dev branches, tests, CI configs, internal tooling, wizard provider keys (gitignored), build scripts, working notes.
- Public (publish): docs (specs/howto/roadmap), version.json snapshots, CHANGELOG, release notes, and release assets (TCZ/ISO + checksums). No secrets.

Generated artifacts are never tracked in git; only uploaded to Releases:
- `distribution/tcz/*.tcz*` (TCZ + .dep/.md5.txt/.info/.list)
- `distribution/uDOS-*.iso`

---
## Release flow
1. Tag in private repo: `vX.Y.Z` (ensure tests pass).
2. Private CI builds TCZ/ISO, generates checksums, creates GitHub Release, uploads assets.
3. Sync job mirrors docs + version metadata to public repo (`main`) and creates a matching Release (assets copied from private release).

---
## Required secrets (private repo)
- `PUBLIC_REPO`: `fredporter/uDOS-public`
- `PUBLIC_TOKEN`: PAT with `repo` scope to push to public repo
- `GH_TOKEN`: default `GITHUB_TOKEN` is fine for private release

---
## CI overview
- `.github/workflows/release.yml`
  - Trigger: tag push `v*`
  - Install `squashfs-tools`, run Python builder (core/api/wizard)
  - Upload built `distribution/tcz` artifacts + checksums to Release
- `.github/workflows/sync-public.yml`
  - Trigger: `release` published
  - Push selected docs + `version.json` to public repo `main`
  - Recreate Release in public and upload same assets

---
## Automation details
- Mirror scope:
  - `docs/**`
  - `README.md` (if present)
  - Version metadata: `core/version.json`, `app/version.json`, `extensions/api/version.json`, `wizard/version.json`
- Exclusions:
  - Do not mirror `.github/` or dev-only files to avoid workflow loops.
- Release tag:
  - Uses the private release tag name verbatim (e.g., `v1.0.2.0`).
- Assets source:
  - Assets are fetched from the private Release and uploaded to the public Release.
- Safety:
  - Public push uses `PUBLIC_TOKEN` limited to the public repo.
  - Private access uses default `GITHUB_TOKEN` to read assets.

---
## Test run (pre-release)
1. Commit and push all changes to `main` (private).
2. Create a pre-release tag (e.g., `v1.0.2.0-rc1`) and publish a Release in private.
3. Verify:
   - Private Release contains `*.tcz` and `*.md5.txt` assets.
   - Public repo `main` has updated `docs/` and version files.
   - Public Release exists for the same tag and includes the assets.

---
## Manual fallback
If CI sync fails:
```sh
# Clone public
rm -rf /tmp/uDOS-public
git clone https://github.com/fredporter/uDOS-public.git /tmp/uDOS-public

# Copy docs + version metadata
rsync -a --delete docs/ /tmp/uDOS-public/docs/
rsync -a core/version.json /tmp/uDOS-public/core/version.json
rsync -a extensions/api/version.json /tmp/uDOS-public/extensions/api/version.json
rsync -a wizard/version.json /tmp/uDOS-public/wizard/version.json
rsync -a app/version.json /tmp/uDOS-public/app/version.json

# Commit + push
cd /tmp/uDOS-public
git checkout -B main
git add -A
git commit -m "docs+versions: sync for vX.Y.Z"
git push origin main
```

---
## Next steps
- Create `fredporter/uDOS-public` (empty on `main`)
- Add repo secrets in private: `PUBLIC_REPO`, `PUBLIC_TOKEN`
- Dry-run CI on a pre-release tag (e.g., `v1.0.2-rc1`)
