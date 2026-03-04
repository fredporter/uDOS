#!/bin/sh
# uDOS TinyCore Stack Installer
# Installs uDOS TCZ packages with tier presets.

set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
HOST_INSTALLER="${REPO_ROOT}/bin/install-udos-vibe.sh"

# Detect default package directory (tcz -> test -> current)
if [ -d "${SCRIPT_DIR}/tcz" ]; then
  PKG_DIR="${SCRIPT_DIR}/tcz"
elif [ -d "${SCRIPT_DIR}/test" ]; then
  PKG_DIR="${SCRIPT_DIR}/test"
else
  PKG_DIR="${SCRIPT_DIR}"
fi

TIER=""
CUSTOM_PACKAGES=""
PROFILE_SELECTION=""
ASSUME_YES=0
DRY_RUN=0
CACHE_DIR="${TMPDIR:-/tmp}/udos-tcz"
TIER_OVERRIDE=0

TC_VERSION="unknown"
ARCH="unknown"
MEM_MB=0
CPU_COUNT=0
RECOMMENDED_TIER="core"
SELECTED_PROFILES="core"
SELECTED_PACKAGE_GROUPS=""
SELECTED_EXTENSIONS=""

maybe_dispatch_to_host_installer() {
  for arg in "$@"; do
    case "$arg" in
      --core|--wizard|--update)
        if [ ! -x "$HOST_INSTALLER" ]; then
          err "Host installer not found: $HOST_INSTALLER"
        fi
        log "Routing install request to host installer: bin/install-udos-vibe.sh"
        exec "$HOST_INSTALLER" "$@"
        ;;
    esac
  done
}

usage() {
  cat <<'EOF'
uDOS TinyCore Installer

Usage: installer.sh [--tier=TIER] [--profile=core,home] [--packages="p1,p2"] [--from=/path/to/tcz] [--yes] [--dry-run]

Options:
  --tier, -t       tier from packaging manifest (default: platform auto-select)
  --profile        certified profiles: core,home,creator,gaming,dev
  --packages, -p   comma-separated custom list (overrides tier)
  --from, -f       directory containing .tcz files (default: auto-detected)
  --yes, -y        non-interactive install
  --dry-run        show actions without installing
  --help, -h       show this help
EOF
}

log() { printf '%s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
err() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

manifest_default_tier() {
  command -v uv >/dev/null 2>&1 || return 1
  default_tier=$(uv run python -m core.services.packaging_adapters.cli linux installer-default-tier --repo-root "$REPO_ROOT" 2>/dev/null || true)
  [ -n "$default_tier" ] || return 1
  printf '%s\n' "$default_tier"
  return 0
}

tier_packages_from_manifest() {
  tier="$1"
  command -v uv >/dev/null 2>&1 || return 1
  packages=$(uv run python -m core.services.packaging_adapters.cli linux installer-tier-packages --repo-root "$REPO_ROOT" --tier "$tier" 2>/dev/null || true)
  [ -n "$packages" ] || return 1
  printf '%s\n' "$packages"
  return 0
}

load_manifest_defaults() {
  if default_tier=$(manifest_default_tier); then
    TIER="$default_tier"
  fi
}

tier_packages() {
  manifest_packages=$(tier_packages_from_manifest "$1" || true)
  [ -n "$manifest_packages" ] || err "Tier '$1' not found in packaging manifest"
  echo "$manifest_packages"
}

resolve_profiles() {
  requested="$1"
  if [ -z "$requested" ]; then
    requested="core"
  fi
  if command -v uv >/dev/null 2>&1; then
    resolved=$(UDOS_ROOT="$REPO_ROOT" uv run python -m core.services.release_profile_cli resolved --repo-root "$REPO_ROOT" --profiles "$requested" 2>/dev/null || true)
    [ -n "$resolved" ] || resolved="$requested"
  else
    resolved="$requested"
  fi
  printf '%s\n' "$resolved"
}

sync_certified_profiles() {
  if [ -z "$SELECTED_PROFILES" ]; then
    return 0
  fi

  if command -v uv >/dev/null 2>&1; then
    UDOS_ROOT="$REPO_ROOT" uv run python -m core.services.release_profile_cli install --repo-root "$REPO_ROOT" --profiles "$SELECTED_PROFILES" >/dev/null 2>&1 || warn "Could not persist certified profile state"
    return 0
  fi

  mkdir -p "$REPO_ROOT/memory/ucode"
  cat > "$REPO_ROOT/memory/ucode/release-profiles.json" <<EOF
{
  "enabled": ["$(printf '%s' "$SELECTED_PROFILES" | sed 's/,/","/g')"],
  "installed": ["$(printf '%s' "$SELECTED_PROFILES" | sed 's/,/","/g')"]
}
EOF
}

load_profile_summary() {
  if command -v uv >/dev/null 2>&1; then
    SELECTED_PACKAGE_GROUPS=$(UDOS_ROOT="$REPO_ROOT" uv run python -m core.services.release_profile_cli packages --repo-root "$REPO_ROOT" --profiles "$SELECTED_PROFILES" 2>/dev/null || true)
    SELECTED_EXTENSIONS=$(UDOS_ROOT="$REPO_ROOT" uv run python -m core.services.release_profile_cli extensions --repo-root "$REPO_ROOT" --profiles "$SELECTED_PROFILES" 2>/dev/null || true)
  fi
}

detect_platform() {
  # TinyCore version
  if [ -f /etc/os-release ]; then
    TC_VERSION=$(grep -E '^VERSION_ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"')
  elif [ -f /etc/tc-version ]; then
    TC_VERSION=$(cat /etc/tc-version)
  fi

  # Architecture
  ARCH=$(uname -m 2>/dev/null || echo "unknown")

  # Memory (MB)
  MEM_KB=$(grep -i '^MemTotal:' /proc/meminfo 2>/dev/null | awk '{print $2}')
  if [ -n "$MEM_KB" ]; then
    MEM_MB=$((MEM_KB / 1024))
  fi

  # CPU cores
  CPU_COUNT=$(grep -c '^processor' /proc/cpuinfo 2>/dev/null || echo 0)

  # Recommend tier based on memory
  if [ "$MEM_MB" -gt 0 ]; then
    if   [ "$MEM_MB" -lt 256 ];  then RECOMMENDED_TIER="ultra"
    elif [ "$MEM_MB" -lt 512 ];  then RECOMMENDED_TIER="micro"
    elif [ "$MEM_MB" -lt 1024 ]; then RECOMMENDED_TIER="mini"
    elif [ "$MEM_MB" -lt 2048 ]; then RECOMMENDED_TIER="core"
    elif [ "$MEM_MB" -lt 3072 ]; then RECOMMENDED_TIER="standard"
    else                             RECOMMENDED_TIER="wizard"
    fi
  fi
}

confirm() {
  [ "$ASSUME_YES" -eq 1 ] && return 0
  printf '%s [y/N]: ' "$1"
  read ans || exit 1
  case "$ans" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

require_tools() {
  for tool in tce-load md5sum unsquashfs; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      err "Missing required tool: $tool"
    fi
  done
}

prepare_cache() {
  mkdir -p "$CACHE_DIR"
}

copy_metadata() {
  base="$1"
  src_dir="$2"
  dst_dir="$3"
  for ext in dep md5.txt info list; do
    f="$src_dir/${base}.tcz.${ext}"
    [ -f "$f" ] && cp "$f" "$dst_dir/"
  done
}

install_pkg() {
  pkg="$1"
  src="$PKG_DIR/$pkg"
  [ -f "$src" ] || err "Package not found: $src"

  dest="$CACHE_DIR/$pkg"

  if [ "$DRY_RUN" -eq 1 ]; then
    log "[DRY] would install $pkg from $src"
    return 0
  fi

  cp "$src" "$dest"
  copy_metadata "${pkg%.tcz}" "$PKG_DIR" "$CACHE_DIR"

  log "Installing $pkg"
  if ! tce-load -i "$dest" >/dev/null 2>&1; then
    # BusyBox tce-load may not support paths; fall back to working dir
    (cd "$CACHE_DIR" && tce-load -i "$pkg") || err "Install failed for $pkg"
  fi
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --tier=*|-t=*) TIER=${1#*=}; TIER_OVERRIDE=1 ;;
      --tier|-t) TIER=$2; TIER_OVERRIDE=1; shift ;;
      --profile=*|--profiles=*) PROFILE_SELECTION=${1#*=} ;;
      --profile|--profiles) PROFILE_SELECTION=$2; shift ;;
      --packages=*|-p=*) CUSTOM_PACKAGES=${1#*=} ;;
      --packages|-p) CUSTOM_PACKAGES=$2; shift ;;
      --from=*|-f=*) PKG_DIR=${1#*=} ;;
      --from|-f) PKG_DIR=$2; shift ;;
      --yes|-y) ASSUME_YES=1 ;;
      --dry-run) DRY_RUN=1 ;;
      --help|-h) usage; exit 0 ;;
      *) usage; err "Unknown option: $1" ;;
    esac
    shift
  done
}

resolve_dependencies() {
  # Expand dependency tree using local .dep files; preserves order, de-duplicates
  input_pkgs="$1"
  resolved=""
  seen=""
  queue="$input_pkgs"

  while [ -n "$queue" ]; do
    pkg=${queue%% *}
    queue=${queue#"$pkg"}
    queue=$(printf "%s" "$queue" | sed 's/^ *//')

    case " $seen " in *" $pkg "*) continue ;; esac
    resolved="$resolved $pkg"
    seen="$seen $pkg"

    dep_file="$PKG_DIR/${pkg%.tcz}.tcz.dep"
    if [ -f "$dep_file" ]; then
      for dep in $(grep -v '^[[:space:]]*$' "$dep_file"); do
        case " $seen $queue " in *" $dep "*) ;; *) queue="$queue $dep" ;; esac
      done
    else
      warn "Missing dependency file: $dep_file"
    fi
  done

  echo "$resolved" | sed 's/^ *//'
}

main() {
  maybe_dispatch_to_host_installer "$@"
  load_manifest_defaults
  parse_args "$@"
  require_tools
  prepare_cache

  detect_platform
  SELECTED_PROFILES=$(resolve_profiles "$PROFILE_SELECTION")
  load_profile_summary

  if [ "$TIER_OVERRIDE" -eq 0 ] && command -v uv >/dev/null 2>&1; then
    mapped_tier=$(UDOS_ROOT="$REPO_ROOT" uv run python -m core.services.release_profile_cli tier --repo-root "$REPO_ROOT" --profiles "$SELECTED_PROFILES" 2>/dev/null || true)
    if [ -n "$mapped_tier" ]; then
      RECOMMENDED_TIER="$mapped_tier"
    fi
  fi

  if [ -z "$CUSTOM_PACKAGES" ] && [ "$TIER_OVERRIDE" -eq 0 ]; then
    TIER="$RECOMMENDED_TIER"
    log "Auto-selected tier based on platform: $TIER (RAM=${MEM_MB}MB, ARCH=${ARCH}, TC=${TC_VERSION})"
  else
    log "Platform: TC=${TC_VERSION}, ARCH=${ARCH}, RAM=${MEM_MB}MB, CPU=${CPU_COUNT}"
  fi

  if [ -n "$CUSTOM_PACKAGES" ]; then
    PKGS=$(printf "%s" "$CUSTOM_PACKAGES" | tr ',' ' ')
  else
    PKGS=$(tier_packages "$TIER")
  fi

  PKGS=$(resolve_dependencies "$PKGS")

  log "uDOS Installer"
  log "Tier: $TIER"
  log "Certified profiles: $SELECTED_PROFILES"
  log "Package groups: ${SELECTED_PACKAGE_GROUPS:-utilities}"
  log "Official extensions: ${SELECTED_EXTENSIONS:-none}"
  log "Packages: $PKGS"
  log "Source: $PKG_DIR"

  if [ "$DRY_RUN" -eq 1 ]; then
    log "Dry run mode - no changes will be made"
  else
    if ! confirm "Proceed with installation?"; then
      log "Aborted"
      exit 1
    fi
  fi

  for pkg in $PKGS; do
    if [ ! -f "$PKG_DIR/$pkg" ]; then
      err "Package missing: $PKG_DIR/$pkg"
    fi
    install_pkg "$pkg"
  done

  sync_certified_profiles

  log "Installation complete"
}

main "$@"
