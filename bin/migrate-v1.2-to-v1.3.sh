#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: migrate-v1.2-to-v1.3.sh [--source <path>] [--dest <path>] [--apply]

Defaults:
  --source: ./vault-md (if present) or ~/Documents/uDOS Vault
  --dest:   ~/Documents/uDOS Vault

Behavior:
  - Dry run by default (no changes).
  - With --apply, copies source to dest (non-destructive).
  - Writes a migration report in the current directory.

USAGE
}

SOURCE=""
DEST=""
APPLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE="$2"; shift 2 ;;
    --dest)
      DEST="$2"; shift 2 ;;
    --apply)
      APPLY=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage; exit 1 ;;
  esac
done

if [[ -z "$SOURCE" ]]; then
  if [[ -d "vault-md" ]]; then
    SOURCE="vault-md"
  elif [[ -d "$HOME/Documents/uDOS Vault" ]]; then
    SOURCE="$HOME/Documents/uDOS Vault"
  fi
fi

if [[ -z "$DEST" ]]; then
  DEST="$HOME/Documents/uDOS Vault"
fi

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
REPORT="migration-report-${TIMESTAMP}.txt"

{
  echo "uDOS v1.2 -> v1.3 Migration Report"
  echo "Timestamp: ${TIMESTAMP}"
  echo "Source: ${SOURCE:-<not found>}"
  echo "Dest: ${DEST}"
  echo "Mode: $([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY RUN)"
  echo

  if [[ -z "${SOURCE}" || ! -d "${SOURCE}" ]]; then
    echo "ERROR: Source directory not found."
    echo "Provide --source <path> to your v1.2 vault or vault-md directory."
    exit 2
  fi

  echo "Scanning source..."
  echo "- Top-level entries:"
  ls -1 "${SOURCE}" || true
  echo

  echo "Searching for task databases (*.db) ..."
  find "${SOURCE}" -type f \( -iname "*task*.db" -o -iname "*tasks*.db" \) -maxdepth 6 || true
  echo

  echo "Planned actions:"
  echo "- Copy source -> dest (non-destructive)."
  echo "- Leave source untouched."
  echo "- If tasks DB exists, create placeholder markdown conversion log (manual follow-up)."
  echo

  if [[ $APPLY -eq 1 ]]; then
    echo "APPLY mode: copying files..."
    mkdir -p "${DEST}"
    if command -v rsync >/dev/null 2>&1; then
      rsync -avh --stats "${SOURCE}/" "${DEST}/"
    else
      cp -a "${SOURCE}/." "${DEST}/"
    fi

    TASK_DB=$(find "${SOURCE}" -type f \( -iname "*task*.db" -o -iname "*tasks*.db" \) -maxdepth 6 | head -n 1 || true)
    if [[ -n "${TASK_DB}" ]]; then
      echo "Found task DB: ${TASK_DB}"
      MIG_DIR="${DEST}/_migration"
      mkdir -p "${MIG_DIR}"
      echo "TODO: Convert ${TASK_DB} to Markdown checkboxes" > "${MIG_DIR}/tasks-migration-note.md"
    fi
  else
    echo "DRY RUN: no changes made. Use --apply to execute copy."
  fi

} | tee "${REPORT}"

exit 0
