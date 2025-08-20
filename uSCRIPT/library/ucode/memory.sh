#!/bin/bash
# uDOS Memory Module v1.3
# Memory system interface for uMEMORY management

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)" pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

show_memory_status() {
    echo -e "${BLUE}🧠 Memory System Status${NC}"
    echo ""
    
    # Check main directories
    echo "Memory Structure:"
    for dir in "templates" "user" "system" "core"; do
        if [[ -d "$UMEMORY/$dir" ]]; then
            local count=$(find "$UMEMORY/$dir" -type f 2>/dev/null | wc -l)
            echo -e "  ✓ ${GREEN}$dir/${NC} ($count files)"
        else
            echo -e "  ✗ ${RED}$dir/${NC} (missing)"
        fi
    done
    
    echo ""
    
    # Storage information
    local total_files=$(find "$UMEMORY" -type f 2>/dev/null | wc -l)
    local storage_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    
    echo "Storage Information:"
    echo "  Total files: $total_files"
    echo "  Total size: $storage_size"
    
    # Session logs
    local session_logs=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    local install_logs=$(find "$UMEMORY" -name "*Installation.md" 2>/dev/null | wc -l)
    
    echo ""
    echo "Log Files:"
    echo "  Session logs: $session_logs"
    echo "  Installation logs: $install_logs"
}

list_templates() {
    echo -e "${BLUE}📋 Available Templates${NC}"
    echo ""
    
    if [[ -d "$UMEMORY/templates" ]]; then
        # List template categories
        for category in "$UMEMORY/templates"/*; do
            if [[ -d "$category" ]]; then
                local cat_name=$(basename "$category")
                local file_count=$(find "$category" -type f 2>/dev/null | wc -l)
                echo -e "${CYAN}$cat_name/${NC} ($file_count files)"
                
                # List files in category
                find "$category" -name "*.md" -type f 2>/dev/null | while read -r file; do
                    local filename=$(basename "$file" .md)
                    echo "  • $filename"
                done
                echo ""
            fi
        done
    else
        echo -e "${RED}Templates directory not found${NC}"
    fi
}

search_memory() {
    local search_term="$1"
    
    if [[ -z "$search_term" ]]; then
        echo -e "${RED}Please provide a search term${NC}"
        echo "Usage: memory search <term>"
        return 1
    fi
    
    echo -e "${BLUE}🔍 Searching Memory for: '$search_term'${NC}"
    echo ""
    
    # Search in all markdown files
    local results=$(grep -r -i -l "$search_term" "$UMEMORY" --include="*.md" 2>/dev/null)
    
    if [[ -n "$results" ]]; then
        echo "Found in:"
        echo "$results" | while read -r file; do
            local relative_path=$(echo "$file" | sed "s|$UMEMORY/||")
            echo "  📄 $relative_path"
            
            # Show context
            grep -i -n -A 1 -B 1 "$search_term" "$file" 2>/dev/null | head -5 | sed 's/^/    /'
            echo ""
        done
    else
        echo "No results found for '$search_term'"
    fi
}

backup_memory() {
    echo -e "${BLUE}💾 Creating Memory Backup${NC}"
    echo ""
    
    local backup_dir="$UDOS_ROOT/uMEMORY/backup"
    local timestamp=$(date "+%Y%m%d-%H%M%S")
    local backup_name="memory-backup-$timestamp.tar.gz"
    local backup_path="$backup_dir/$backup_name"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$backup_dir"
    
    # Create compressed backup
    echo "Creating backup: $backup_name"
    
    if tar -czf "$backup_path" -C "$UDOS_ROOT" \
        --exclude="uMEMORY/backup" \
        --exclude="*.tmp" \
        --exclude="*.bak" \
        uMEMORY/ 2>/dev/null; then
        
        local backup_size=$(du -sh "$backup_path" 2>/dev/null | cut -f1)
        echo -e "${GREEN}Backup created successfully${NC}"
        echo "Location: $backup_path"
        echo "Size: $backup_size"
        
        # List recent backups
        echo ""
        echo "Recent backups:"
        ls -la "$backup_dir"/*.tar.gz 2>/dev/null | tail -5 | while read -r line; do
            echo "  $line"
        done
    else
        echo -e "${RED}Backup failed${NC}"
        return 1
    fi
}

restore_memory() {
    local backup_file="$1"
    
    echo -e "${BLUE}🔄 Memory Restore${NC}"
    echo ""
    
    if [[ -z "$backup_file" ]]; then
        echo "Available backups:"
        local backup_dir="$UDOS_ROOT/uMEMORY/backup"
        if [[ -d "$backup_dir" ]]; then
            ls -la "$backup_dir"/*.tar.gz 2>/dev/null | while read -r line; do
                echo "  $line"
            done
        fi
        echo ""
        echo "Usage: memory restore <backup-file>"
        return 1
    fi
    
    # Check if backup file exists
    if [[ ! -f "$backup_file" ]]; then
        # Try relative to backup directory
        local backup_dir="$UDOS_ROOT/uMEMORY/backup"
        local full_path="$backup_dir/$backup_file"
        if [[ -f "$full_path" ]]; then
            backup_file="$full_path"
        else
            echo -e "${RED}Backup file not found: $backup_file${NC}"
            return 1
        fi
    fi
    
    echo -e "${YELLOW}Warning: This will overwrite current memory data${NC}"
    echo "Backup file: $backup_file"
    echo ""
    echo -e "${YELLOW}Continue? (y/N):${NC} "
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Create current backup first
        echo "Creating safety backup..."
        backup_memory > /dev/null
        
        # Restore from backup
        echo "Restoring from backup..."
        if tar -xzf "$backup_file" -C "$UDOS_ROOT" 2>/dev/null; then
            echo -e "${GREEN}Restore completed successfully${NC}"
        else
            echo -e "${RED}Restore failed${NC}"
            return 1
        fi
    else
        echo "Restore cancelled"
    fi
}

show_memory_tree() {
    echo -e "${BLUE}🌳 Memory Structure${NC}"
    echo ""
    
    # Use tree command if available, otherwise use find
    if command -v tree >/dev/null 2>&1; then
        tree "$UMEMORY" -I 'backup|*.tmp|*.bak'
    else
        # Fallback to find with formatting
        find "$UMEMORY" -type d | sort | sed "s|$UMEMORY||" | sed 's|^|  |' | sed 's|/|  |g'
    fi
}

analyze_memory_usage() {
    echo -e "${BLUE}📊 Memory Usage Analysis${NC}"
    echo ""
    
    # File type analysis
    echo "File Types:"
    find "$UMEMORY" -type f -name "*.*" | sed 's/.*\.//' | sort | uniq -c | sort -nr | head -10 | while read -r count ext; do
        echo "  .$ext: $count files"
    done
    
    echo ""
    
    # Directory sizes
    echo "Directory Sizes:"
    du -sh "$UMEMORY"/* 2>/dev/null | sort -hr | while read -r size dir; do
        local dirname=$(basename "$dir")
        echo "  $dirname: $size"
    done
    
    echo ""
    
    # Recent activity
    echo "Recent Activity (last 7 days):"
    local recent_files=$(find "$UMEMORY" -type f -mtime -7 2>/dev/null | wc -l)
    echo "  Modified files: $recent_files"
    
    # Largest files
    echo ""
    echo "Largest Files:"
    find "$UMEMORY" -type f -exec du -sh {} \; 2>/dev/null | sort -hr | head -5 | while read -r size file; do
        local filename=$(basename "$file")
        echo "  $filename: $size"
    done
}

# Main function
memory_main() {
    local action="${1:-status}"
    local param="${2:-}"
    
    case "$action" in
        "status")
            show_memory_status
            ;;
        "templates")
            list_templates
            ;;
        "search")
            search_memory "$param"
            ;;
        "backup")
            backup_memory
            ;;
        "restore")
            restore_memory "$param"
            ;;
        "tree")
            show_memory_tree
            ;;
        "analyze")
            analyze_memory_usage
            ;;
        *)
            echo "Memory module - Available actions: status, templates, search <term>, backup, restore <file>, tree, analyze"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    memory_main "$@"
fi
