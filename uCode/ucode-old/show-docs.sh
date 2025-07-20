#!/bin/bash
# uDOS Documentation SHOW Command - Glow Reader Integration
# Uses glow for beautiful markdown rendering with organized document index

UHOME="${HOME}/uDOS"
DOCS_DIR="${UHOME}/docs"
UCODE="${UHOME}/uCode"

# Colors for non-glow output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

show_index() {
    if command -v glow &> /dev/null; then
        glow "$DOCS_DIR/README.md"
    else
        echo -e "${YELLOW}Installing glow for beautiful documentation viewing...${NC}"
        "$UCODE/packages/install-glow.sh"
        glow "$DOCS_DIR/README.md"
    fi
}

show_document() {
    local doc_path="$1"
    local full_path=""
    
    # Search for document in organized structure
    if [[ -f "$DOCS_DIR/user/$doc_path.md" ]]; then
        full_path="$DOCS_DIR/user/$doc_path.md"
    elif [[ -f "$DOCS_DIR/system/$doc_path.md" ]]; then
        full_path="$DOCS_DIR/system/$doc_path.md"
    elif [[ -f "$DOCS_DIR/packages/$doc_path.md" ]]; then
        full_path="$DOCS_DIR/packages/$doc_path.md"
    elif [[ -f "$DOCS_DIR/development/$doc_path.md" ]]; then
        full_path="$DOCS_DIR/development/$doc_path.md"
    elif [[ -f "$DOCS_DIR/$doc_path.md" ]]; then
        full_path="$DOCS_DIR/$doc_path.md"
    elif [[ -f "$doc_path" ]]; then
        full_path="$doc_path"
    else
        echo -e "${YELLOW}Document not found: $doc_path${NC}"
        echo -e "${CYAN}Available documents:${NC}"
        list_documents
        return 1
    fi
    
    echo -e "${GREEN}📖 Showing: $(basename "$full_path")${NC}"
    
    if command -v glow &> /dev/null; then
        glow "$full_path"
    else
        echo -e "${YELLOW}Installing glow for beautiful documentation viewing...${NC}"
        "$UCODE/packages/install-glow.sh"
        glow "$full_path"
    fi
}

list_documents() {
    echo -e "${WHITE}📚 Available Documents:${NC}\n"
    
    echo -e "${CYAN}👤 User Documentation:${NC}"
    if [[ -d "$DOCS_DIR/user" ]]; then
        for doc in "$DOCS_DIR/user"/*.md; do
            if [[ -f "$doc" ]]; then
                local basename=$(basename "$doc" .md)
                local title=$(grep -m1 "^# " "$doc" 2>/dev/null | sed 's/^# //' | sed 's/[📚🎯📋🎮]//g' | xargs)
                echo "  • $basename - $title"
            fi
        done
    fi
    echo ""
    
    echo -e "${CYAN}⚙️ System Documentation:${NC}"
    if [[ -d "$DOCS_DIR/system" ]]; then
        for doc in "$DOCS_DIR/system"/*.md; do
            if [[ -f "$doc" ]]; then
                local basename=$(basename "$doc" .md)
                local title=$(grep -m1 "^# " "$doc" 2>/dev/null | sed 's/^# //' | sed 's/[🏗️📊🚀⚙️]//g' | xargs)
                echo "  • $basename - $title"
            fi
        done
    fi
    echo ""
    
    echo -e "${CYAN}📦 Package Documentation:${NC}"
    if [[ -d "$DOCS_DIR/packages" ]]; then
        for doc in "$DOCS_DIR/packages"/*.md; do
            if [[ -f "$doc" ]]; then
                local basename=$(basename "$doc" .md)
                local title=$(grep -m1 "^# " "$doc" 2>/dev/null | sed 's/^# //' | sed 's/[📦🔍🎨✨]//g' | xargs)
                echo "  • $basename - $title"
            fi
        done
    fi
    echo ""
    
    echo -e "${CYAN}🛠️ Development Documentation (Dev Mode Only):${NC}"
    if [[ -d "$DOCS_DIR/development" && -f "$UHOME/uMemory/users/roles.md" ]] && grep -q "wizard\|sorcerer" "$UHOME/uMemory/users/roles.md" 2>/dev/null; then
        for doc in "$DOCS_DIR/development"/*.md; do
            if [[ -f "$doc" ]]; then
                local basename=$(basename "$doc" .md)
                local title=$(grep -m1 "^# " "$doc" 2>/dev/null | sed 's/^# //' | sed 's/[🛠️📊🏗️]//g' | xargs)
                echo "  • development/$basename - $title"
            fi
        done
        find "$DOCS_DIR/development" -name "*.md" -path "*/architecture/*" -o -path "*/optimization/*" -o -path "*/reports/*" | while read -r doc; do
            if [[ -f "$doc" ]]; then
                local relpath=$(echo "$doc" | sed "s|$DOCS_DIR/||")
                local title=$(grep -m1 "^# " "$doc" 2>/dev/null | sed 's/^# //' | xargs)
                echo "  • $relpath - $title"
            fi
        done
    else
        echo "  • (Requires wizard or sorcerer role)"
    fi
    echo ""
    
    echo -e "${YELLOW}Usage Examples:${NC}"
    echo "  SHOW manual          # User manual"
    echo "  SHOW commands        # Command reference"
    echo "  SHOW architecture    # System architecture"
    echo "  SHOW index           # Package documentation"
    echo "  SHOW                 # This documentation index"
}

search_documents() {
    local search_term="$1"
    echo -e "${GREEN}🔍 Searching for '$search_term' in documentation...${NC}\n"
    
    # Use ripgrep if available, otherwise grep
    if command -v rg &> /dev/null; then
        rg -i --type md "$search_term" "$DOCS_DIR" --heading --line-number
    elif command -v grep &> /dev/null; then
        grep -r -i -n --include="*.md" "$search_term" "$DOCS_DIR"
    else
        echo -e "${YELLOW}No search tools available. Installing ripgrep...${NC}"
        "$UCODE/packages/install-ripgrep.sh"
        rg -i --type md "$search_term" "$DOCS_DIR" --heading --line-number
    fi
}

# Main command handler
case "$1" in
    ""|"index"|"help")
        show_index
        ;;
    "list"|"ls")
        list_documents
        ;;
    "search"|"find")
        if [[ -n "$2" ]]; then
            search_documents "$2"
        else
            echo -e "${YELLOW}Usage: SHOW search <term>${NC}"
        fi
        ;;
    *)
        show_document "$1"
        ;;
esac
