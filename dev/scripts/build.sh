#!/bin/bash
# uDOS Build System
# Universal Device Operating System
# Version: 1.0.5.2

# Build Configuration
# ==================

BUILD_DIR="${UDOS_ROOT}/build"
DIST_DIR="${UDOS_ROOT}/dist"
UDOS_VERSION="1.0.5.3"

# Create build directories
init_build_system() {
    echo "🏗️ Initializing uDOS Build System v${UDOS_VERSION}"
    echo "=================================================="
    
    # Set up environment
    UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
    BUILD_DIR="${UDOS_ROOT}/build"
    DIST_DIR="${UDOS_ROOT}/dist"
    
    # Create build directories
    mkdir -p "$BUILD_DIR" "$DIST_DIR"
    
    # Create build manifest
    create_build_manifest
    
    echo "✅ Build system initialized"
}

# Create build manifest
create_build_manifest() {
    local manifest_file="${BUILD_DIR}/manifest.json"
    
    cat > "$manifest_file" << EOF
{
    "name": "uDOS",
    "version": "$UDOS_VERSION",
    "build_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "components": {
        "uCORE": {
            "path": "uCORE",
            "type": "core_system",
            "dependencies": []
        },
        "uMEMORY": {
            "path": "uMEMORY",
            "type": "data_layer",
            "dependencies": ["uCORE"]
        },
        "uKNOWLEDGE": {
            "path": "uKNOWLEDGE",
            "type": "knowledge_base",
            "dependencies": ["uCORE", "uMEMORY"]
        },
        "uNETWORK": {
            "path": "uNETWORK",
            "type": "network_services",
            "dependencies": ["uCORE", "uMEMORY"]
        },
        "uSCRIPT": {
            "path": "uSCRIPT",
            "type": "script_environment",
            "dependencies": ["uCORE"]
        }
    },
    "build_targets": [
        "development",
        "production",
        "testing"
    ]
}
EOF
    
    echo "Build manifest created: $manifest_file"
}

# Build target
build_target() {
    local target="${1:-development}"
    
    echo "🚀 Building uDOS for target: $target"
    echo "====================================="
    
    case "$target" in
        "development")
            build_development
            ;;
        "production")
            build_production
            ;;
        "testing")
            build_testing
            ;;
        *)
            echo "❌ Unknown build target: $target"
            return 1
            ;;
    esac
}

# Development build
build_development() {
    echo "📦 Development Build"
    
    # Initialize foundation
    "${UDOS_ROOT}/uCORE/code/foundation-init-v1053.sh" init
    
    # Set development environment
    export UDOS_ENV="development"
    export UDOS_LOG_LEVEL=0  # Debug level
    
    # Copy development configurations
    copy_development_configs
    
    echo "✅ Development build complete"
}

# Production build
build_production() {
    echo "📦 Production Build"
    
    # Initialize foundation with production settings
    export UDOS_ENV="production"
    export UDOS_LOG_LEVEL=1  # Info level
    
    # Initialize foundation
    "${UDOS_ROOT}/uCORE/code/foundation-init-v1053.sh" init
    
    # Optimize for production
    optimize_for_production
    
    # Create distribution package
    create_distribution_package
    
    echo "✅ Production build complete"
}

# Testing build
build_testing() {
    echo "📦 Testing Build"
    
    # Initialize foundation
    export UDOS_ENV="testing"
    export UDOS_LOG_LEVEL=0  # Debug level
    
    "${UDOS_ROOT}/uCORE/code/foundation-init-v1053.sh" init
    
    # Run foundation tests
    "${UDOS_ROOT}/uCORE/code/foundation-init-v1053.sh" test
    
    echo "✅ Testing build complete"
}

# Copy development configurations
copy_development_configs() {
    local dev_config_dir="${BUILD_DIR}/config/development"
    mkdir -p "$dev_config_dir"
    
    # Copy default configurations
    if [[ -d "${UDOS_ROOT}/uCORE/config" ]]; then
        cp -r "${UDOS_ROOT}/uCORE/config"/* "$dev_config_dir/"
    fi
    
    echo "Development configs copied to $dev_config_dir"
}

# Optimize for production
optimize_for_production() {
    echo "🔧 Optimizing for production..."
    
    # Remove debug scripts
    find "$BUILD_DIR" -name "*debug*" -type f -delete 2>/dev/null || true
    
    # Compress scripts (if available)
    if command -v gzip >/dev/null 2>&1; then
        find "$BUILD_DIR" -name "*.sh" -exec gzip -k {} \; 2>/dev/null || true
    fi
    
    echo "✅ Production optimization complete"
}

# Create distribution package
create_distribution_package() {
    local package_name="udos-${UDOS_VERSION}-$(date +%Y%m%d).tar.gz"
    local package_path="${DIST_DIR}/${package_name}"
    
    echo "📦 Creating distribution package..."
    
    # Create package
    tar -czf "$package_path" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='*.log' \
        --exclude='tmp' \
        -C "$UDOS_ROOT" \
        .
    
    # Create checksum
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$package_path" > "${package_path}.sha256"
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$package_path" > "${package_path}.sha256"
    fi
    
    echo "✅ Distribution package created: $package_path"
}

# Clean build artifacts
clean_build() {
    echo "🧹 Cleaning build artifacts..."
    
    # Remove build directory
    if [[ -d "$BUILD_DIR" ]]; then
        rm -rf "$BUILD_DIR"
        echo "✅ Build directory cleaned"
    fi
    
    # Remove distribution directory
    if [[ -d "$DIST_DIR" ]]; then
        rm -rf "$DIST_DIR"
        echo "✅ Distribution directory cleaned"
    fi
    
    # Clean foundation
    "${UDOS_ROOT}/uCORE/code/foundation-init-v1053.sh" clean
    
    echo "✅ Build cleanup complete"
}

# Show build info
build_info() {
    echo "📋 uDOS Build Information"
    echo "========================"
    echo "Version: $UDOS_VERSION"
    echo "Build Date: $(date)"
    echo "Build Dir: $BUILD_DIR"
    echo "Dist Dir: $DIST_DIR"
    
    if [[ -f "${BUILD_DIR}/manifest.json" ]]; then
        echo ""
        echo "Build Manifest:"
        cat "${BUILD_DIR}/manifest.json" | jq '.'
    fi
}

# Main command handler
main() {
    local command="${1:-init}"
    
    # Set up environment first
    UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
    BUILD_DIR="${UDOS_ROOT}/build"
    DIST_DIR="${UDOS_ROOT}/dist"
    export UDOS_ROOT BUILD_DIR DIST_DIR
    
    case "$command" in
        "init")
            init_build_system
            ;;
        "build")
            local target="${2:-development}"
            build_target "$target"
            ;;
        "clean")
            clean_build
            ;;
        "info")
            build_info
            ;;
        "help")
            echo "uDOS Build System v$UDOS_VERSION"
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  init                  - Initialize build system"
            echo "  build [target]        - Build for target (development|production|testing)"
            echo "  clean                 - Clean build artifacts"
            echo "  info                  - Show build information"
            echo "  help                  - Show this help"
            ;;
        *)
            echo "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
