#!/usr/bin/env bash
set -euo pipefail

# TOYBOX Elite local setup:
# - Fetch upstream Elite-compatible source from GitHub (git preferred, curl fallback)
# - Build locally in memory/library/containers/elite
# - Write runtime activation exports used by TOYBOX adapters

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_ROOT="${UDOS_TOYBOX_ROOT:-${REPO_ROOT}/memory/library/containers/elite}"
SRC_DIR="${TARGET_ROOT}/src"
BIN_DIR="${TARGET_ROOT}/bin"
BUILD_DIR="${TARGET_ROOT}/build"
ACTIVATION_FILE="${REPO_ROOT}/memory/bank/private/toybox-runtime.env"
DOTENV_FILE="${REPO_ROOT}/.env"

REPO_URL="${TOYBOX_ELITE_REPO_URL:-https://github.com/fesh0r/newkind.git}"
REPO_REF="${TOYBOX_ELITE_REPO_REF:-master}"
BIN_URL="${TOYBOX_ELITE_BIN_URL:-}"
RELEASE_ZIP_URL="${TOYBOX_ELITE_RELEASE_ZIP_URL:-https://www.new-kind.com/wp-content/uploads/etnkv12final.zip}"
RUNTIME_DIR="${TARGET_ROOT}/runtime"
WINE_TARBALL_URL="${TOYBOX_ELITE_WINE_TARBALL_URL:-https://github.com/Gcenx/macOS_Wine_builds/releases/download/11.0/wine-stable-11.0-osx64.tar.xz}"
WINE_DIR="${TARGET_ROOT}/wine"
WINE_BIN="${WINE_DIR}/Wine Stable.app/Contents/Resources/wine/bin/wine"

mkdir -p "${SRC_DIR}" "${BIN_DIR}" "${BUILD_DIR}" "$(dirname "${ACTIVATION_FILE}")"

fetch_source() {
  if [[ -d "${SRC_DIR}/.git" ]]; then
    echo "[elite] Updating existing repo in ${SRC_DIR}"
    git -C "${SRC_DIR}" fetch --tags --force
    git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    git -C "${SRC_DIR}" pull --ff-only origin "${REPO_REF}" || true
    return
  fi

  rm -rf "${SRC_DIR}"
  mkdir -p "${SRC_DIR}"

  if command -v git >/dev/null 2>&1; then
    echo "[elite] Cloning ${REPO_URL} (${REPO_REF})"
    git clone --depth 1 --branch "${REPO_REF}" "${REPO_URL}" "${SRC_DIR}" || {
      echo "[elite] branch clone failed; cloning default branch and checking out ${REPO_REF}"
      rm -rf "${SRC_DIR}"
      git clone "${REPO_URL}" "${SRC_DIR}"
      git -C "${SRC_DIR}" checkout "${REPO_REF}" || true
    }
    return
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "[elite] error: neither git nor curl is available." >&2
    exit 1
  fi

  echo "[elite] Fetching tarball via curl"
  local tmp_tar
  tmp_tar="$(mktemp "${TMPDIR:-/tmp}/elite.XXXXXX.tar.gz")"
  local tar_url="${TOYBOX_ELITE_TARBALL_URL:-https://github.com/fesh0r/newkind/archive/refs/heads/${REPO_REF}.tar.gz}"
  curl -fsSL "${tar_url}" -o "${tmp_tar}"
  tar -xzf "${tmp_tar}" --strip-components=1 -C "${SRC_DIR}"
  rm -f "${tmp_tar}"
}

build_source() {
  echo "[elite] Attempting local build"
  if [[ -f "${SRC_DIR}/makefile-linux" ]] && command -v make >/dev/null 2>&1; then
    make -C "${SRC_DIR}" -f makefile-linux -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
  fi
  if [[ -f "${SRC_DIR}/CMakeLists.txt" ]] && command -v cmake >/dev/null 2>&1; then
    cmake -S "${SRC_DIR}" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE=Release || true
    cmake --build "${BUILD_DIR}" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
    return
  fi
  if [[ -f "${SRC_DIR}/Makefile" ]] && command -v make >/dev/null 2>&1; then
    make -C "${SRC_DIR}" -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)" || true
    return
  fi
  echo "[elite] No recognized build system found; using system runtime fallback if available"
}

resolve_runtime_cmd() {
  local candidates=(
    "${BUILD_DIR}/newkind"
    "${BUILD_DIR}/elite"
    "${SRC_DIR}/newkind"
    "${SRC_DIR}/elite"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -x "${c}" ]]; then
      echo "${c}"
      return
    fi
  done
  if command -v newkind >/dev/null 2>&1; then
    command -v newkind
    return
  fi
  if command -v elite >/dev/null 2>&1; then
    command -v elite
    return
  fi
  if command -v oolite >/dev/null 2>&1; then
    command -v oolite
    return
  fi
  echo ""
}

write_launcher() {
  local cmd="$1"
  cat > "${BIN_DIR}/run-elite.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${cmd}" ]] && [[ -x "${cmd}" ]]; then
  if [[ "${cmd}" == *"/wine" ]] && [[ -f "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" ]]; then
    exec "${cmd}" "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" "\$@"
  fi
  exec "${cmd}" "\$@"
fi
if [[ -f "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" ]]; then
  if command -v wine >/dev/null 2>&1; then
    exec "\$(command -v wine)" "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" "\$@"
  fi
  if [[ -x "${WINE_BIN}" ]]; then
    exec "${WINE_BIN}" "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" "\$@"
  fi
fi
for fallback in newkind elite oolite; do
  if command -v "\${fallback}" >/dev/null 2>&1; then
    exec "\$(command -v "\${fallback}")" "\$@"
  fi
done
echo "[elite] No runtime binary found. Re-run setup after installing build deps, wine, or setting TOYBOX_ELITE_CMD." >&2
exit 1
EOF
  chmod +x "${BIN_DIR}/run-elite.sh"
}

download_binary_fallback() {
  if [[ -z "${BIN_URL}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[elite] TOYBOX_ELITE_BIN_URL set but curl is unavailable." >&2
    return
  fi
  local out="${BIN_DIR}/elite"
  echo "[elite] Downloading binary from ${BIN_URL}"
  curl -fsSL "${BIN_URL}" -o "${out}"
  chmod +x "${out}"
}

download_release_zip_fallback() {
  if [[ -z "${RELEASE_ZIP_URL}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[elite] release zip fallback requested but curl is unavailable." >&2
    return
  fi
  if ! command -v unzip >/dev/null 2>&1; then
    echo "[elite] release zip fallback requested but unzip is unavailable." >&2
    return
  fi
  local zip_path="${TARGET_ROOT}/etnkv12final.zip"
  mkdir -p "${RUNTIME_DIR}"
  echo "[elite] Downloading upstream release zip from ${RELEASE_ZIP_URL}"
  curl -fsSL "${RELEASE_ZIP_URL}" -o "${zip_path}"
  rm -rf "${RUNTIME_DIR}/E-TNK v1.2"
  unzip -o -q "${zip_path}" -d "${RUNTIME_DIR}"
}

download_portable_wine_fallback() {
  if [[ -z "${WINE_TARBALL_URL}" ]]; then
    return
  fi
  if [[ -x "${WINE_BIN}" ]]; then
    return
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[elite] portable wine fallback requested but curl is unavailable." >&2
    return
  fi
  if ! command -v tar >/dev/null 2>&1; then
    echo "[elite] portable wine fallback requested but tar is unavailable." >&2
    return
  fi
  local tar_path="${TARGET_ROOT}/wine-stable-osx64.tar.xz"
  mkdir -p "${WINE_DIR}"
  echo "[elite] Downloading portable Wine bundle from ${WINE_TARBALL_URL}"
  curl -fsSL "${WINE_TARBALL_URL}" -o "${tar_path}"
  rm -rf "${WINE_DIR}/Wine Stable.app"
  tar -xJf "${tar_path}" -C "${WINE_DIR}"
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
  local launcher="${BIN_DIR}/run-elite.sh"
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_ELITE_CMD" "\"${launcher}\""
  upsert_kv_file "${ACTIVATION_FILE}" "export TOYBOX_ELITE_HOME" "\"${TARGET_ROOT}\""
  if [[ "${ACTIVATE_DOTENV:-0}" == "1" ]]; then
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_ELITE_CMD" "\"${launcher}\""
    upsert_kv_file "${DOTENV_FILE}" "TOYBOX_ELITE_HOME" "\"${TARGET_ROOT}\""
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
  download_release_zip_fallback
  if [[ -f "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" ]] && command -v wine >/dev/null 2>&1; then
    CMD_PATH="$(command -v wine)"
  elif [[ -f "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" ]]; then
    download_portable_wine_fallback
    if [[ -x "${WINE_BIN}" ]]; then
      CMD_PATH="${WINE_BIN}"
    fi
  fi
fi
if [[ -z "${CMD_PATH}" ]]; then
  echo "[elite] error: could not resolve a runnable Elite binary." >&2
  echo "[elite] install build deps, install/provide wine for upstream NewKind.exe, provide TOYBOX_ELITE_BIN_URL, or set TOYBOX_ELITE_CMD manually." >&2
  exit 2
fi
# Keep launcher in explicit EXE mode when wine runtime is selected.
if [[ -f "${RUNTIME_DIR}/E-TNK v1.2/NewKind.exe" ]]; then
  SYSTEM_WINE="$(command -v wine 2>/dev/null || true)"
  if [[ "${CMD_PATH}" == "${WINE_BIN}" ]] || [[ -n "${SYSTEM_WINE}" && "${CMD_PATH}" == "${SYSTEM_WINE}" ]]; then
    CMD_PATH=""
  fi
fi
write_launcher "${CMD_PATH}"
activate_exports

echo "[elite] Setup complete."
echo "[elite] source: ${SRC_DIR}"
echo "[elite] launcher: ${BIN_DIR}/run-elite.sh"
echo "[elite] activation file: ${ACTIVATION_FILE}"
echo "[elite] to activate now: source ${ACTIVATION_FILE}"
