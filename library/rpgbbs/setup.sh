#!/usr/bin/env bash
set -euo pipefail

# TOYBOX RPGBBS local setup:
# - Fetch upstream RPGBBS source from GitHub (git preferred, curl fallback)
# - Build locally if the project provides build steps
# - Write runtime activation exports for TOYBOX adapter

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_ROOT="${UDOS_TOYBOX_ROOT:-${REPO_ROOT}/memory/library/containers/rpgbbs}"
SRC_DIR="${TARGET_ROOT}/src"
BIN_DIR="${TARGET_ROOT}/bin"
ACTIVATION_FILE="${REPO_ROOT}/memory/bank/private/toybox-runtime.env"
DOTENV_FILE="${REPO_ROOT}/.env"

REPO_URL="${TOYBOX_RPGBBS_REPO_URL:-https://github.com/evs-rpg/rpgbbs.git}"
REPO_REF="${TOYBOX_RPGBBS_REPO_REF:-main}"
BIN_URL="${TOYBOX_RPGBBS_BIN_URL:-}"

mkdir -p "${SRC_DIR}" "${BIN_DIR}" "$(dirname "${ACTIVATION_FILE}")"

fetch_source() {
  if [[ -d "${SRC_DIR}/.git" ]]; then
    echo "[rpgbbs] Updating existing repo in ${SRC_DIR}"
    git -C "${SRC_DIR}" fetch --tags --force
    git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    git -C "${SRC_DIR}" pull --ff-only origin "${REPO_REF}" || true
    return
  fi

  rm -rf "${SRC_DIR}"
  mkdir -p "${SRC_DIR}"

  if command -v git >/dev/null 2>&1; then
    echo "[rpgbbs] Cloning ${REPO_URL} (${REPO_REF})"
    git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${SRC_DIR}" || {
      echo "[rpgbbs] branch clone failed; cloning default branch and checking out ${REPO_REF}"
      rm -rf "${SRC_DIR}"
      git clone "${REPO_URL}" "${SRC_DIR}"
      git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    }
    return
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[rpgbbs] error: neither git nor curl is available." >&2
    exit 1
  fi

  echo "[rpgbbs] Fetching tarball via curl"
  local tmp_tar
  tmp_tar="$(mktemp "${TMPDIR:-/tmp}/rpgbbs.XXXXXX.tar.gz")"
  local tar_url="${TOYBOX_RPGBBS_TARBALL_URL:-https://github.com/evs-rpg/rpgbbs/archive/refs/heads/${REPO_REF}.tar.gz}"
  curl -fsSL "${tar_url}" -o "${tmp_tar}"
  tar -xzf "${tmp_tar}" --strip-components=1 -C "${SRC_DIR}"
  rm -f "${tmp_tar}"
}

build_source() {
  echo "[rpgbbs] Attempting local build"
  if [[ -f "${SRC_DIR}/Cargo.toml" ]] && command -v cargo >/dev/null 2>&1; then
    cargo build --release --manifest-path "${SRC_DIR}/Cargo.toml" || true
  elif [[ -f "${SRC_DIR}/go.mod" ]] && command -v go >/dev/null 2>&1; then
    (cd "${SRC_DIR}" && go build ./...) || true
  elif [[ -f "${SRC_DIR}/package.json" ]] && command -v npm >/dev/null 2>&1; then
    (cd "${SRC_DIR}" && npm install && npm run build) || true
  elif [[ -f "${SRC_DIR}/Makefile" ]] && command -v make >/dev/null 2>&1; then
    make -C "${SRC_DIR}" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
  fi
}

resolve_runtime_cmd() {
  local candidates=(
    "${SRC_DIR}/target/release/rpgbbs"
    "${SRC_DIR}/bin/rpgbbs"
    "${SRC_DIR}/rpgbbs"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -x "${c}" ]]; then
      echo "${c}"
      return
    fi
  done
  if command -v rpgbbs >/dev/null 2>&1; then
    command -v rpgbbs
    return
  fi
  echo ""
}

download_binary_fallback() {
  if [[ -z "${BIN_URL}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[rpgbbs] TOYBOX_RPGBBS_BIN_URL set but curl is unavailable." >&2
    return
  fi
  local out="${BIN_DIR}/rpgbbs"
  echo "[rpgbbs] Downloading binary from ${BIN_URL}"
  curl -fsSL "${BIN_URL}" -o "${out}"
  chmod +x "${out}"
}

write_launcher() {
  local cmd="$1"
  cat > "${BIN_DIR}/run-rpgbbs.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${cmd}" ]] && [[ -x "${cmd}" ]]; then
  exec "${cmd}" "\$@"
fi
if command -v rpgbbs >/dev/null 2>&1; then
  exec "\$(command -v rpgbbs)" "\$@"
fi
echo "[rpgbbs] No runtime binary found. Re-run setup or set TOYBOX_RPGBBS_CMD." >&2
exit 1
EOF
  chmod +x "${BIN_DIR}/run-rpgbbs.sh"
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
  local launcher="${BIN_DIR}/run-rpgbbs.sh"
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_RPGBBS_CMD" "\"${launcher}\""
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_RPGBBS_HOME" "\"${TARGET_ROOT}\""
  if [[ "${ACTIVATE_DOTENV:-0}" == "1" ]]; then
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_RPGBBS_CMD" "\"${launcher}\""
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_RPGBBS_HOME" "\"${TARGET_ROOT}\""
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
  echo "[rpgbbs] error: could not resolve a runnable RPGBBS binary." >&2
  echo "[rpgbbs] provide TOYBOX_RPGBBS_BIN_URL or set TOYBOX_RPGBBS_CMD manually." >&2
  exit 2
fi

write_launcher "${CMD_PATH}"
activate_exports

echo "[rpgbbs] Setup complete."
echo "[rpgbbs] source: ${SRC_DIR}"
echo "[rpgbbs] launcher: ${BIN_DIR}/run-rpgbbs.sh"
echo "[rpgbbs] activation file: ${ACTIVATION_FILE}"
echo "[rpgbbs] to activate now: source ${ACTIVATION_FILE}"
