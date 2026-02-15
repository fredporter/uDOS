#!/usr/bin/env bash
set -euo pipefail

# TOYBOX Crawler3D local setup:
# - Fetch upstream crawler source from GitHub (git preferred, curl fallback)
# - Build locally if available
# - Write runtime activation exports for TOYBOX adapter

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_ROOT="${UDOS_TOYBOX_ROOT:-${REPO_ROOT}/memory/library/containers/crawler3d}"
SRC_DIR="${TARGET_ROOT}/src"
BIN_DIR="${TARGET_ROOT}/bin"
BUILD_DIR="${TARGET_ROOT}/build"
ACTIVATION_FILE="${REPO_ROOT}/memory/bank/private/toybox-runtime.env"
DOTENV_FILE="${REPO_ROOT}/.env"

REPO_URL="${TOYBOX_CRAWLER3D_REPO_URL:-https://github.com/tomassedovic/crawl3d.git}"
REPO_REF="${TOYBOX_CRAWLER3D_REPO_REF:-main}"
BIN_URL="${TOYBOX_CRAWLER3D_BIN_URL:-}"

mkdir -p "${SRC_DIR}" "${BIN_DIR}" "${BUILD_DIR}" "$(dirname "${ACTIVATION_FILE}")"

fetch_source() {
  if [[ -d "${SRC_DIR}/.git" ]]; then
    echo "[crawler3d] Updating existing repo in ${SRC_DIR}"
    git -C "${SRC_DIR}" fetch --tags --force
    git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    git -C "${SRC_DIR}" pull --ff-only origin "${REPO_REF}" || true
    return
  fi

  rm -rf "${SRC_DIR}"
  mkdir -p "${SRC_DIR}"

  if command -v git >/dev/null 2>&1; then
    echo "[crawler3d] Cloning ${REPO_URL} (${REPO_REF})"
    git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${SRC_DIR}" || {
      echo "[crawler3d] branch clone failed; cloning default branch and checking out ${REPO_REF}"
      rm -rf "${SRC_DIR}"
      git clone "${REPO_URL}" "${SRC_DIR}"
      git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    }
    return
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[crawler3d] error: neither git nor curl is available." >&2
    exit 1
  fi

  echo "[crawler3d] Fetching tarball via curl"
  local tmp_tar
  tmp_tar="$(mktemp "${TMPDIR:-/tmp}/crawler3d.XXXXXX.tar.gz")"
  local tar_url="${TOYBOX_CRAWLER3D_TARBALL_URL:-https://github.com/tomassedovic/crawl3d/archive/refs/heads/${REPO_REF}.tar.gz}"
  curl -fsSL "${tar_url}" -o "${tmp_tar}"
  tar -xzf "${tmp_tar}" --strip-components=1 -C "${SRC_DIR}"
  rm -f "${tmp_tar}"
}

build_source() {
  echo "[crawler3d] Attempting local build"
  if [[ -f "${SRC_DIR}/CMakeLists.txt" ]] && command -v cmake >/dev/null 2>&1; then
    cmake -S "${SRC_DIR}" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release || true
    cmake --build "${BUILD_DIR}" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
    return
  fi
  if [[ -f "${SRC_DIR}/Cargo.toml" ]] && command -v cargo >/dev/null 2>&1; then
    cargo build --release --manifest-path "${SRC_DIR}/Cargo.toml" || true
    return
  fi
  if [[ -f "${SRC_DIR}/Makefile" ]] && command -v make >/dev/null 2>&1; then
    make -C "${SRC_DIR}" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
    return
  fi
}

resolve_runtime_cmd() {
  local candidates=(
    "${BUILD_DIR}/crawler3d"
    "${BUILD_DIR}/crawl3d"
    "${SRC_DIR}/target/release/crawler3d"
    "${SRC_DIR}/target/release/crawl3d"
    "${SRC_DIR}/crawler3d"
    "${SRC_DIR}/crawl3d"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -x "${c}" ]]; then
      echo "${c}"
      return
    fi
  done
  for fallback in crawler3d crawl3d dungeon3d; do
    if command -v "${fallback}" >/dev/null 2>&1; then
      command -v "${fallback}"
      return
    fi
  done
  echo ""
}

download_binary_fallback() {
  if [[ -z "${BIN_URL}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[crawler3d] TOYBOX_CRAWLER3D_BIN_URL set but curl is unavailable." >&2
    return
  fi
  local out="${BIN_DIR}/crawler3d"
  echo "[crawler3d] Downloading binary from ${BIN_URL}"
  curl -fsSL "${BIN_URL}" -o "${out}"
  chmod +x "${out}"
}

write_launcher() {
  local cmd="$1"
  cat > "${BIN_DIR}/run-crawler3d.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${cmd}" ]] && [[ -x "${cmd}" ]]; then
  exec "${cmd}" "\$@"
fi
for fallback in crawler3d crawl3d dungeon3d; do
  if command -v "\${fallback}" >/dev/null 2>&1; then
    exec "\$(command -v "\${fallback}")" "\$@"
  fi
done
echo "[crawler3d] No runtime binary found. Re-run setup or set TOYBOX_CRAWLER3D_CMD." >&2
exit 1
EOF
  chmod +x "${BIN_DIR}/run-crawler3d.sh"
}

upsert_kv_file() {
  local file="$1"
  local key="$2"
  local value="$3"
  mkdir -p "$(dirname "${file}")"
  touch "${file}"
  if grep -qE "^${key}=" "${file}"; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|g" "${file}" && rm -f "${file}.bak"
  else
    echo "${key}=${value}" >> "${file}"
  fi
}

activate_exports() {
  local launcher="${BIN_DIR}/run-crawler3d.sh"
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_CRAWLER3D_CMD" "\"${launcher}\""
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_CRAWLER3D_HOME" "\"${TARGET_ROOT}\""
  if [[ "${ACTIVATE_DOTENV:-0}" == "1" ]]; then
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_CRAWLER3D_CMD" "\"${launcher}\""
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_CRAWLER3D_HOME" "\"${TARGET_ROOT}\""
  fi
}

fetch_source
build_source
CMD_PATH="$(resolve_runtime_cmd)"
if [[ -z "${CMD_PATH}" ]]; then
  download_binary_fallback
  CMD_PATH="$(resolve_runtime_cmd)"
fi
if [[ -z "${CMD_PATH}" ]]; then
  echo "[crawler3d] error: could not resolve a runnable crawler3d binary." >&2
  echo "[crawler3d] provide TOYBOX_CRAWLER3D_BIN_URL or set TOYBOX_CRAWLER3D_CMD manually." >&2
  exit 2
fi

write_launcher "${CMD_PATH}"
activate_exports

echo "[crawler3d] Setup complete."
echo "[crawler3d] source: ${SRC_DIR}"
echo "[crawler3d] launcher: ${BIN_DIR}/run-crawler3d.sh"
echo "[crawler3d] activation file: ${ACTIVATION_FILE}"
echo "[crawler3d] to activate now: source ${ACTIVATION_FILE}"
