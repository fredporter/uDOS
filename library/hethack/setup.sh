#!/usr/bin/env bash
set -euo pipefail

# TOYBOX Hethack local setup:
# - Fetch upstream NetHack source from GitHub (git preferred, curl fallback)
# - Build locally in memory/library/containers/hethack
# - Write runtime activation exports used by TOYBOX adapters

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_ROOT="${UDOS_TOYBOX_ROOT:-${REPO_ROOT}/memory/library/containers/hethack}"
SRC_DIR="${TARGET_ROOT}/src"
BIN_DIR="${TARGET_ROOT}/bin"
ACTIVATION_FILE="${REPO_ROOT}/memory/bank/private/toybox-runtime.env"
DOTENV_FILE="${REPO_ROOT}/.env"

REPO_URL="${TOYBOX_HETHACK_REPO_URL:-https://github.com/NetHack/NetHack.git}"
REPO_REF="${TOYBOX_HETHACK_REPO_REF:-NetHack-3.6.7_Released}"
BIN_URL="${TOYBOX_HETHACK_BIN_URL:-}"

mkdir -p "${SRC_DIR}" "${BIN_DIR}" "$(dirname "${ACTIVATION_FILE}")"

fetch_source() {
  if [[ -d "${SRC_DIR}/.git" ]]; then
    echo "[hethack] Updating existing repo in ${SRC_DIR}"
    git -C "${SRC_DIR}" fetch --tags --force
    git -C "${SRC_DIR}" checkout "${REPO_REF}"
    git -C "${SRC_DIR}" pull --ff-only origin "${REPO_REF}" || true
    return
  fi

  rm -rf "${SRC_DIR}"
  mkdir -p "${SRC_DIR}"

  if command -v git >/dev/null 2>&1; then
    echo "[hethack] Cloning ${REPO_URL} (${REPO_REF})"
    git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${SRC_DIR}" || {
      echo "[hethack] branch clone failed; cloning default branch and checking out ${REPO_REF}"
      rm -rf "${SRC_DIR}"
      git clone "${REPO_URL}" "${SRC_DIR}"
      git -C "${SRC_DIR}" checkout "${REPO_REF}"
    }
    return
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[hethack] error: neither git nor curl is available." >&2
    exit 1
  fi

  echo "[hethack] Fetching tarball via curl"
  local tmp_tar
  tmp_tar="$(mktemp "${TMPDIR:-/tmp}/hethack.XXXXXX.tar.gz")"
  local tar_url="${TOYBOX_HETHACK_TARBALL_URL:-https://github.com/NetHack/NetHack/archive/refs/tags/${REPO_REF}.tar.gz}"
  curl -fsSL "${tar_url}" -o "${tmp_tar}"
  tar -xzf "${tmp_tar}" --strip-components=1 -C "${SRC_DIR}"
  rm -f "${tmp_tar}"
}

build_source() {
  if ! command -v make >/dev/null 2>&1; then
    echo "[hethack] make not found; skipping local build"
    return
  fi

  echo "[hethack] Attempting local build"
  (
    cd "${SRC_DIR}"
    if [[ -f "sys/unix/setup.sh" ]]; then
      # Generate platform makefiles/config for unix/macOS flow.
      sh "sys/unix/setup.sh" "sys/unix/hints/macosx" || sh "sys/unix/setup.sh" || true
    fi
    make -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" all || make all || true
  )
}

resolve_runtime_cmd() {
  if [[ -x "${SRC_DIR}/src/nethack" ]]; then
    echo "${SRC_DIR}/src/nethack"
    return
  fi
  if [[ -x "${SRC_DIR}/nethack" ]]; then
    echo "${SRC_DIR}/nethack"
    return
  fi
  if command -v nethack >/dev/null 2>&1; then
    command -v nethack
    return
  fi
  echo ""
}

write_launcher() {
  local cmd="$1"
  cat > "${BIN_DIR}/run-hethack.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${cmd}" ]] && [[ -x "${cmd}" ]]; then
  exec "${cmd}" "\$@"
fi
if command -v nethack >/dev/null 2>&1; then
  exec "\$(command -v nethack)" "\$@"
fi
echo "[hethack] No runtime binary found. Re-run library/hethack/setup.sh after installing build deps." >&2
exit 1
EOF
  chmod +x "${BIN_DIR}/run-hethack.sh"
}

download_binary_fallback() {
  if [[ -z "${BIN_URL}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[hethack] TOYBOX_HETHACK_BIN_URL set but curl is unavailable." >&2
    return
  fi
  local out="${BIN_DIR}/nethack"
  echo "[hethack] Downloading binary from ${BIN_URL}"
  curl -fsSL "${BIN_URL}" -o "${out}"
  chmod +x "${out}"
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
  local launcher="${BIN_DIR}/run-hethack.sh"
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_HETHACK_CMD" "\"${launcher}\""
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_HETHACK_HOME" "\"${TARGET_ROOT}\""
  if [[ "${ACTIVATE_DOTENV:-0}" == "1" ]]; then
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_HETHACK_CMD" "\"${launcher}\""
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_HETHACK_HOME" "\"${TARGET_ROOT}\""
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
  echo "[hethack] error: could not resolve a runnable NetHack binary." >&2
  echo "[hethack] install build deps, provide TOYBOX_HETHACK_BIN_URL, or set TOYBOX_HETHACK_CMD manually." >&2
  exit 2
fi
write_launcher "${CMD_PATH}"
activate_exports

echo "[hethack] Setup complete."
echo "[hethack] source: ${SRC_DIR}"
echo "[hethack] launcher: ${BIN_DIR}/run-hethack.sh"
echo "[hethack] activation file: ${ACTIVATION_FILE}"
echo "[hethack] to activate now: source ${ACTIVATION_FILE}"
