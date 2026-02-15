#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: build-sonic-stick.sh [options]

Build deterministic Sonic Stick artifacts and emit checksums + build manifest.

Options:
  --profile <name>        Build profile (default: alpine-core+sonic)
  --build-id <id>         Build identifier (default: UTC timestamp)
  --source-image <path>   Optional source image to copy into build output
  --output-dir <path>     Output directory (default: distribution/builds/<build-id>)
  --help                  Show this help
USAGE
}

PROFILE="alpine-core+sonic"
BUILD_ID=""
SOURCE_IMAGE=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    --build-id)
      BUILD_ID="${2:-}"
      shift 2
      ;;
    --source-image)
      SOURCE_IMAGE="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [[ -z "${BUILD_ID}" ]]; then
  BUILD_ID="$(date -u +%Y%m%dT%H%M%SZ)"
fi

if [[ -z "${OUTPUT_DIR}" ]]; then
  OUTPUT_DIR="${REPO_ROOT}/distribution/builds/${BUILD_ID}"
fi

mkdir -p "${OUTPUT_DIR}"

VERSION="v1.3.17"
if [[ -f "${REPO_ROOT}/version.json" ]]; then
  VERSION_VALUE="$(python3 - <<'PY' "${REPO_ROOT}/version.json"
import json
import sys
path = sys.argv[1]
try:
    payload = json.load(open(path, "r", encoding="utf-8"))
except Exception:
    print("v1.3.17")
    raise SystemExit(0)
print(payload.get("display") or payload.get("version") or "v1.3.17")
PY
)"
  if [[ -n "${VERSION_VALUE}" ]]; then
    VERSION="${VERSION_VALUE}"
  fi
fi

ROOT_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD)"
SONIC_SHA=""
if [[ -d "${REPO_ROOT}/sonic/.git" || -f "${REPO_ROOT}/sonic/.git" ]]; then
  SONIC_SHA="$(git -C "${REPO_ROOT}/sonic" rev-parse HEAD 2>/dev/null || true)"
fi
if [[ -z "${SONIC_SHA}" ]]; then
  SONIC_SHA="missing"
fi

SAFE_VERSION="${VERSION//[^A-Za-z0-9._-]/-}"
BASENAME="sonic-stick-${SAFE_VERSION}-${BUILD_ID}"
IMG_FILE="${BASENAME}.img"
ISO_FILE="${BASENAME}.iso"
MANIFEST_FILE="build-manifest.json"
CHECKSUM_FILE="checksums.txt"

IMG_PATH="${OUTPUT_DIR}/${IMG_FILE}"
ISO_PATH="${OUTPUT_DIR}/${ISO_FILE}"
MANIFEST_PATH="${OUTPUT_DIR}/${MANIFEST_FILE}"
CHECKSUM_PATH="${OUTPUT_DIR}/${CHECKSUM_FILE}"

if [[ -n "${SOURCE_IMAGE}" ]]; then
  SOURCE_ABS="$(cd "$(dirname "${SOURCE_IMAGE}")" && pwd)/$(basename "${SOURCE_IMAGE}")"
  if [[ ! -f "${SOURCE_ABS}" ]]; then
    echo "Source image not found: ${SOURCE_IMAGE}" >&2
    exit 1
  fi
  cp "${SOURCE_ABS}" "${IMG_PATH}"
else
  SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1704067200}"
  python3 - <<'PY' "${IMG_PATH}" "${PROFILE}" "${BUILD_ID}" "${ROOT_SHA}" "${SONIC_SHA}" "${SOURCE_DATE_EPOCH}"
import hashlib
import os
import sys
from datetime import datetime, timezone

path, profile, build_id, root_sha, sonic_sha, source_epoch = sys.argv[1:7]
seed = "\n".join([
    "uDOS Sonic Stick deterministic image",
    f"profile={profile}",
    f"build_id={build_id}",
    f"root_sha={root_sha}",
    f"sonic_sha={sonic_sha}",
    f"source_date_epoch={source_epoch}",
]) + "\n"
seed_bytes = seed.encode("utf-8")

# Fixed-size deterministic payload (1 MiB)
out = bytearray(1024 * 1024)
for offset in range(0, len(out), len(seed_bytes)):
    chunk = seed_bytes[: min(len(seed_bytes), len(out) - offset)]
    out[offset : offset + len(chunk)] = chunk

with open(path, "wb") as fh:
    fh.write(out)
PY
fi

cp "${IMG_PATH}" "${ISO_PATH}"

python3 - <<'PY' "${OUTPUT_DIR}" "${MANIFEST_PATH}" "${CHECKSUM_PATH}" "${IMG_FILE}" "${ISO_FILE}" "${BUILD_ID}" "${PROFILE}" "${VERSION}" "${ROOT_SHA}" "${SONIC_SHA}"
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

(
    output_dir,
    manifest_path,
    checksum_path,
    img_file,
    iso_file,
    build_id,
    profile,
    version,
    root_sha,
    sonic_sha,
) = sys.argv[1:11]

out = Path(output_dir)
manifest = Path(manifest_path)
checksums = Path(checksum_path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

img_path = out / img_file
iso_path = out / iso_file

artifact_rows = []
for item in [img_path, iso_path]:
    artifact_rows.append(
        {
            "name": item.name,
            "path": item.name,
            "kind": item.suffix.lstrip("."),
            "size_bytes": item.stat().st_size,
            "sha256": sha256(item),
        }
    )

manifest_payload = {
    "schema": "udos.sonic-stick.build-manifest.v1",
    "build_id": build_id,
    "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "profile": profile,
    "version": version,
    "repository": {
        "root_sha": root_sha,
        "sonic_sha": sonic_sha,
    },
    "artifacts": artifact_rows,
}

manifest.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

checksum_rows = []
for item in [img_path, iso_path, manifest]:
    checksum_rows.append(f"{sha256(item)}  {item.name}")
checksums.write_text("\n".join(checksum_rows) + "\n", encoding="utf-8")
PY

echo "[build-sonic-stick] Build complete"
echo "  output_dir: ${OUTPUT_DIR}"
echo "  profile:    ${PROFILE}"
echo "  build_id:   ${BUILD_ID}"
echo "  root_sha:   ${ROOT_SHA}"
echo "  sonic_sha:  ${SONIC_SHA}"
echo "  manifest:   ${MANIFEST_PATH}"
echo "  checksums:  ${CHECKSUM_PATH}"
