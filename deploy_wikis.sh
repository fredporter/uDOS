#!/usr/bin/env bash
#
# deploy_wikis.sh - Deploy wiki content to GitHub wiki repositories
#
# Usage:
#   ./deploy_wikis.sh [main|dev|both]
#
# Examples:
#   ./deploy_wikis.sh both    # Deploy both wikis (default)
#   ./deploy_wikis.sh main    # Deploy uDOS wiki only
#   ./deploy_wikis.sh dev     # Deploy uDOS-dev wiki only

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="/tmp/udos-wiki-deploy"
MAIN_WIKI_REPO="https://github.com/fredporter/uDOS.wiki.git"
DEV_WIKI_REPO="https://github.com/fredporter/uDOS-dev.wiki.git"

# Determine what to deploy
TARGET="${1:-both}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Deploy main uDOS wiki
deploy_main_wiki() {
    log_info "Deploying uDOS main wiki..."

    # Clone wiki repo
    log_info "Cloning uDOS wiki repository..."
    git clone "$MAIN_WIKI_REPO" "$TMP_DIR/uDOS.wiki"

    # Copy content
    log_info "Copying wiki content..."
    cp -r "$WORKSPACE_ROOT/wiki/"* "$TMP_DIR/uDOS.wiki/"

    # Remove deployment guide and backups (not needed in wiki)
    rm -f "$TMP_DIR/uDOS.wiki/WIKI-DEPLOYMENT.md"
    rm -f "$TMP_DIR/uDOS.wiki/"*.bak
    rm -rf "$TMP_DIR/uDOS.wiki/.archive"

    # Commit and push
    cd "$TMP_DIR/uDOS.wiki"
    git add .

    if git diff --cached --quiet; then
        log_warning "No changes to commit for main wiki"
    else
        log_info "Committing changes..."
        git commit -m "Update wiki content - $(date '+%Y-%m-%d')"

        log_info "Pushing to GitHub..."
        git push origin master

        log_success "uDOS main wiki deployed successfully!"
    fi
}

# Deploy uDOS-dev wiki
deploy_dev_wiki() {
    log_info "Deploying uDOS-dev wiki..."

    # Clone wiki repo
    log_info "Cloning uDOS-dev wiki repository..."
    git clone "$DEV_WIKI_REPO" "$TMP_DIR/uDOS-dev.wiki"

    # Copy content
    log_info "Copying wiki content..."
    cp -r "$WORKSPACE_ROOT/dev/wiki/"* "$TMP_DIR/uDOS-dev.wiki/"

    # Commit and push
    cd "$TMP_DIR/uDOS-dev.wiki"
    git add .

    if git diff --cached --quiet; then
        log_warning "No changes to commit for dev wiki"
    else
        log_info "Committing changes..."
        git commit -m "Update dev scaffold wiki - $(date '+%Y-%m-%d')"

        log_info "Pushing to GitHub..."
        git push origin master

        log_success "uDOS-dev wiki deployed successfully!"
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -rf "$TMP_DIR"
    log_success "Cleanup complete"
}

# Main deployment logic
main() {
    log_info "Starting wiki deployment..."
    echo ""

    # Create temp directory
    mkdir -p "$TMP_DIR"

    # Set trap to cleanup on exit
    trap cleanup EXIT

    case "$TARGET" in
        main)
            deploy_main_wiki
            ;;
        dev)
            deploy_dev_wiki
            ;;
        both)
            deploy_main_wiki
            echo ""
            deploy_dev_wiki
            ;;
        *)
            log_error "Invalid target: $TARGET"
            log_info "Usage: $0 [main|dev|both]"
            exit 1
            ;;
    esac

    echo ""
    log_success "All requested wikis deployed successfully!"
    echo ""
    log_info "View wikis at:"
    [[ "$TARGET" == "main" || "$TARGET" == "both" ]] && echo "  • https://github.com/fredporter/uDOS/wiki"
    [[ "$TARGET" == "dev" || "$TARGET" == "both" ]] && echo "  • https://github.com/fredporter/uDOS-dev/wiki"
}

# Run main function
main
