# Compost Policy (v1.3.17)

uDOS uses a single global runtime archive at `/.compost`.

## Purpose

- Organic archive: retain superseded runtime folders.
- Soft backup: centralize BACKUP/RESTORE snapshots.
- Elastic trash: capture TIDY/CLEAN spillover without hard deletion.

## Structure

- `/.compost/<date>/backups/<scope>/`:
  BACKUP tarballs + manifests used by BACKUP/RESTORE/UNDO.
- `/.compost/<date>/trash/<timestamp>/<scope>/`:
  TIDY and CLEAN destination for junk/non-allowlisted files.
- `/.compost/<date>/archive/<timestamp>/<scope>/`:
  COMPOST destination for older local runtime dirs (`.archive`, `.backup`, `.tmp`, `.temp`).

## Command Mapping

- `BACKUP`:
  writes tar.gz + manifest under `/.compost/<date>/backups/<scope>/`.
- `RESTORE` / `UNDO`:
  read from `/.compost/<date>/backups/<scope>/` (latest first across dates).
- `TIDY` / `CLEAN`:
  move files into `/.compost/<date>/trash/<timestamp>/<scope>/`.
- `COMPOST`:
  migrates older local runtime dirs into `/.compost/<date>/archive/<timestamp>/<scope>/`.
- `DESTROY --compost`:
  archives `/memory` into `/.compost/<date>/trash/<timestamp>/memory` and recreates empty memory layout.

## Enforcement

- Older scratch roots (`.archive`, `.backup`, `.tmp`, `.temp`) are deprecated.
- Runtime commands and maintenance handlers should write to `/.compost`.
- `/.compost` is local-only and ignored by git.
- `docs/.archive/` is local-only, untracked, and should be treated as migration input only.

## Operator Notes

- Do not hard-delete first. Prefer moving into `/.compost/<date>/trash` or `/.compost/<date>/archive`.
- Keep `/.compost` out of release artifacts and source commits.
- If old folders reappear (`.archive`, `.backup`, `.tmp`, `.temp`), run `COMPOST` and remove the roots.
