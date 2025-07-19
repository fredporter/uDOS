#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# 🗑️  uDOS Trash Management System v1.0
# ═══════════════════════════════════════════════════════════════════════
# Secure, organized file management with recovery options
# Part of uDOS Advanced File Management Suite
# ═══════════════════════════════════════════════════════════════════════

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Directory paths
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRASH_DIR="$UDOS_ROOT/trash"
TRASH_LOG="$TRASH_DIR/.trash_log"
TRASH_INDEX="$TRASH_DIR/.index"

# Ensure trash directory exists
mkdir -p "$TRASH_DIR"

# ═══════════════════════════════════════════════════════════════════════
# 🎯 Core Functions
# ═══════════════════════════════════════════════════════════════════════

show_header() {
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  🗑️  uDOS TRASH SYSTEM                      ║${NC}"
    echo -e "${PURPLE}║              Secure File Management v1.0                     ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

log_action() {
    local action="$1"
    local target="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $action: $target" >> "$TRASH_LOG"
}

# ═══════════════════════════════════════════════════════════════════════
# 📦 Move to Trash Function
# ═══════════════════════════════════════════════════════════════════════

move_to_trash() {
    local item="$1"
    
    if [[ ! -e "$item" ]]; then
        echo -e "${RED}❌ Error: '$item' does not exist${NC}"
        return 1
    fi
    
    # Get absolute path
    local abs_path=$(realpath "$item")
    local basename=$(basename "$abs_path")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local trash_name="${timestamp}_${basename}"
    local trash_path="$TRASH_DIR/$trash_name"
    
    # Move to trash
    mv "$abs_path" "$trash_path"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}🗑️  Moved to trash: $basename → $trash_name${NC}"
        log_action "MOVED_TO_TRASH" "$abs_path → $trash_name"
        
        # Update index
        echo "$trash_name|$(date '+%Y-%m-%d %H:%M:%S')|$abs_path" >> "$TRASH_INDEX"
    else
        echo -e "${RED}❌ Failed to move '$item' to trash${NC}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 📋 List Trash Contents
# ═══════════════════════════════════════════════════════════════════════

list_trash() {
    show_header
    
    if [[ ! -f "$TRASH_INDEX" ]] || [[ ! -s "$TRASH_INDEX" ]]; then
        echo -e "${GREEN}✨ Trash is empty! No items found.${NC}"
        return 0
    fi
    
    echo -e "${CYAN}📋 Trash Contents:${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    
    local count=0
    while IFS='|' read -r trash_name date_deleted original_path; do
        ((count++))
        local size=""
        if [[ -e "$TRASH_DIR/$trash_name" ]]; then
            if [[ -d "$TRASH_DIR/$trash_name" ]]; then
                size="$(du -sh "$TRASH_DIR/$trash_name" 2>/dev/null | cut -f1) (folder)"
            else
                size="$(du -sh "$TRASH_DIR/$trash_name" 2>/dev/null | cut -f1)"
            fi
        else
            size="(missing)"
        fi
        
        echo -e "${YELLOW}$count.${NC} ${WHITE}$trash_name${NC}"
        echo -e "    📅 Deleted: $date_deleted"
        echo -e "    📂 Original: $original_path"
        echo -e "    📊 Size: $size"
        echo
    done < "$TRASH_INDEX"
    
    echo -e "${CYAN}Total items in trash: $count${NC}"
}

# ═══════════════════════════════════════════════════════════════════════
# 🔄 Restore from Trash
# ═══════════════════════════════════════════════════════════════════════

restore_item() {
    local trash_name="$1"
    
    if [[ -z "$trash_name" ]]; then
        echo -e "${RED}❌ Please specify item name to restore${NC}"
        return 1
    fi
    
    # Find in index
    local original_path=""
    while IFS='|' read -r t_name date_deleted orig_path; do
        if [[ "$t_name" == "$trash_name" ]]; then
            original_path="$orig_path"
            break
        fi
    done < "$TRASH_INDEX"
    
    if [[ -z "$original_path" ]]; then
        echo -e "${RED}❌ Item '$trash_name' not found in trash index${NC}"
        return 1
    fi
    
    local trash_path="$TRASH_DIR/$trash_name"
    if [[ ! -e "$trash_path" ]]; then
        echo -e "${RED}❌ Item '$trash_name' exists in index but not in trash directory${NC}"
        return 1
    fi
    
    # Check if original location exists
    local original_dir=$(dirname "$original_path")
    if [[ ! -d "$original_dir" ]]; then
        echo -e "${YELLOW}⚠️  Original directory doesn't exist, creating: $original_dir${NC}"
        mkdir -p "$original_dir"
    fi
    
    # Check if original path is already occupied
    if [[ -e "$original_path" ]]; then
        echo -e "${YELLOW}⚠️  Original location is occupied: $original_path${NC}"
        echo -e "${WHITE}Choose restoration option:${NC}"
        echo -e "${CYAN}1.${NC} Overwrite existing file/folder"
        echo -e "${CYAN}2.${NC} Restore with new name"
        echo -e "${CYAN}3.${NC} Cancel restoration"
        read -p "Enter choice (1-3): " choice
        
        case $choice in
            1)
                echo -e "${YELLOW}⚠️  Overwriting existing item...${NC}"
                ;;
            2)
                local counter=1
                local base_name=$(basename "$original_path")
                local dir_name=$(dirname "$original_path")
                while [[ -e "$dir_name/${base_name}_restored_$counter" ]]; do
                    ((counter++))
                done
                original_path="$dir_name/${base_name}_restored_$counter"
                echo -e "${BLUE}📝 Restoring as: $original_path${NC}"
                ;;
            3)
                echo -e "${YELLOW}❌ Restoration cancelled${NC}"
                return 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice, restoration cancelled${NC}"
                return 1
                ;;
        esac
    fi
    
    # Restore the item
    mv "$trash_path" "$original_path"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Restored: $trash_name → $original_path${NC}"
        log_action "RESTORED" "$trash_name → $original_path"
        
        # Remove from index
        grep -v "^$trash_name|" "$TRASH_INDEX" > "$TRASH_INDEX.tmp"
        mv "$TRASH_INDEX.tmp" "$TRASH_INDEX"
    else
        echo -e "${RED}❌ Failed to restore '$trash_name'${NC}"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 🧹 Kill Trash Function
# ═══════════════════════════════════════════════════════════════════════

empty_trash() {
    show_header
    
    if [[ ! -d "$TRASH_DIR" ]] || [[ -z "$(ls -A "$TRASH_DIR" 2>/dev/null | grep -v '^\.')" ]]; then
        echo -e "${GREEN}✨ Trash is already empty!${NC}"
        return 0
    fi
    
    echo -e "${RED}⚠️  WARNING: This will PERMANENTLY DELETE all items in trash!${NC}"
    echo -e "${WHITE}This action cannot be undone.${NC}"
    echo
    
    # Show what will be deleted
    local count=0
    if [[ -f "$TRASH_INDEX" ]]; then
        while IFS='|' read -r trash_name date_deleted original_path; do
            ((count++))
            echo -e "${YELLOW}• $trash_name${NC} (deleted: $date_deleted)"
        done < "$TRASH_INDEX"
    fi
    
    # Count actual files in trash (excluding hidden files)
    local actual_count=$(ls -A "$TRASH_DIR" 2>/dev/null | grep -v '^\.' | wc -l | tr -d ' ')
    
    echo
    echo -e "${WHITE}Items in index: $count${NC}"
    echo -e "${WHITE}Files in trash directory: $actual_count${NC}"
    echo
    
    read -p "Type 'KILL TRASH' to confirm permanent deletion: " confirmation
    
    if [[ "$confirmation" == "KILL TRASH" ]]; then
        echo -e "${YELLOW}🗑️  Killing trash...${NC}"
        
        # Remove all files except hidden system files
        find "$TRASH_DIR" -mindepth 1 -name ".*" -prune -o -print0 | xargs -0 rm -rf
        
        # Clear the index but keep the log
        > "$TRASH_INDEX"
        
        log_action "KILLED_TRASH" "All items permanently deleted"
        echo -e "${GREEN}✅ Trash killed successfully!${NC}"
    else
        echo -e "${BLUE}❌ Trash killing cancelled${NC}"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 🔍 Trash Statistics
# ═══════════════════════════════════════════════════════════════════════

show_stats() {
    show_header
    
    local total_items=0
    local total_size=0
    local oldest_date=""
    local newest_date=""
    
    if [[ -f "$TRASH_INDEX" ]]; then
        total_items=$(wc -l < "$TRASH_INDEX" | tr -d ' ')
        
        while IFS='|' read -r trash_name date_deleted original_path; do
            if [[ -e "$TRASH_DIR/$trash_name" ]]; then
                local item_size=$(du -sb "$TRASH_DIR/$trash_name" 2>/dev/null | cut -f1)
                total_size=$((total_size + item_size))
            fi
            
            if [[ -z "$oldest_date" ]] || [[ "$date_deleted" < "$oldest_date" ]]; then
                oldest_date="$date_deleted"
            fi
            
            if [[ -z "$newest_date" ]] || [[ "$date_deleted" > "$newest_date" ]]; then
                newest_date="$date_deleted"
            fi
        done < "$TRASH_INDEX"
    fi
    
    # Convert bytes to human readable
    local human_size=$(numfmt --to=iec --suffix=B $total_size 2>/dev/null || echo "${total_size} bytes")
    
    echo -e "${CYAN}📊 Trash Statistics:${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}📁 Total Items:${NC} $total_items"
    echo -e "${YELLOW}📊 Total Size:${NC} $human_size"
    echo -e "${YELLOW}📅 Oldest Item:${NC} ${oldest_date:-'N/A'}"
    echo -e "${YELLOW}📅 Newest Item:${NC} ${newest_date:-'N/A'}"
    echo -e "${YELLOW}📂 Trash Location:${NC} $TRASH_DIR"
    echo
}

# ═══════════════════════════════════════════════════════════════════════
# 📖 Help Function
# ═══════════════════════════════════════════════════════════════════════

show_help() {
    show_header
    
    echo -e "${CYAN}📖 uDOS Trash System Commands:${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${YELLOW}📦 File Management:${NC}"
    echo -e "${WHITE}  trash move <file/folder>${NC}    Move item to trash"
    echo -e "${WHITE}  trash delete <file/folder>${NC}  Alias for 'move'"
    echo
    echo -e "${YELLOW}📋 Viewing & Information:${NC}"
    echo -e "${WHITE}  trash list${NC}                 List all items in trash"
    echo -e "${WHITE}  trash ls${NC}                   Alias for 'list'"
    echo -e "${WHITE}  trash stats${NC}                Show trash statistics"
    echo -e "${WHITE}  trash info${NC}                 Alias for 'stats'"
    echo
    echo -e "${YELLOW}🔄 Recovery:${NC}"
    echo -e "${WHITE}  trash restore <item>${NC}       Restore item from trash"
    echo -e "${WHITE}  trash recover <item>${NC}       Alias for 'restore'"
    echo
    echo -e "${YELLOW}🧹 Cleanup:${NC}"
    echo -e "${WHITE}  trash empty${NC}                Permanently delete all trash"
    echo -e "${WHITE}  trash clear${NC}                Alias for 'empty'"
    echo -e "${WHITE}  trash kill${NC}                 Alias for 'empty' (KILL TRASH)"
    echo
    echo -e "${YELLOW}ℹ️  Information:${NC}"
    echo -e "${WHITE}  trash help${NC}                 Show this help message"
    echo -e "${WHITE}  trash --help${NC}               Show this help message"
    echo
    echo -e "${PURPLE}💡 Examples:${NC}"
    echo -e "${WHITE}  trash move old_file.txt${NC}"
    echo -e "${WHITE}  trash list${NC}"
    echo -e "${WHITE}  trash restore 20250719_143022_old_file.txt${NC}"
    echo -e "${WHITE}  trash empty${NC}     # Type 'KILL TRASH' to confirm"
    echo
}

# ═══════════════════════════════════════════════════════════════════════
# 🎯 Main Command Router
# ═══════════════════════════════════════════════════════════════════════

main() {
    local command="$1"
    shift
    
    case "$command" in
        "move"|"delete")
            if [[ $# -eq 0 ]]; then
                echo -e "${RED}❌ Please specify file or folder to move to trash${NC}"
                echo -e "${WHITE}Usage: trash move <file/folder>${NC}"
                exit 1
            fi
            for item in "$@"; do
                move_to_trash "$item"
            done
            ;;
        "list"|"ls")
            list_trash
            ;;
        "restore"|"recover")
            if [[ $# -eq 0 ]]; then
                echo -e "${RED}❌ Please specify item to restore${NC}"
                echo -e "${WHITE}Usage: trash restore <item_name>${NC}"
                exit 1
            fi
            restore_item "$1"
            ;;
        "empty"|"clear"|"kill")
            empty_trash
            ;;
        "stats"|"info")
            show_stats
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            list_trash
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            echo -e "${WHITE}Use 'trash help' for available commands${NC}"
            exit 1
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════════
# 🚀 Script Entry Point
# ═══════════════════════════════════════════════════════════════════════

main "$@"
