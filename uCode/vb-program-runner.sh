#!/bin/bash
# vb-program-runner.sh - Execute VB programs in uDOS
# Version: 2.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
VB_EXAMPLES_DIR="$UHOME/uMemory/scripts/vb-examples"
VB_USER_PROGRAMS_DIR="$UHOME/uMemory/scripts/vb-programs"

# Ensure directories exist
mkdir -p "$VB_EXAMPLES_DIR" "$VB_USER_PROGRAMS_DIR"

# Source the VB interpreter if available
if [[ -f "$SCRIPT_DIR/vb-command-interpreter.sh" ]]; then
    source "$SCRIPT_DIR/vb-command-interpreter.sh"
else
    echo "❌ VB command interpreter not found"
    exit 1
fi

vb_run_program() {
    local program_file="$1"
    
    if [[ -z "$program_file" ]]; then
        echo "❌ Program file required"
        echo "Usage: vb_run_program <program.vb>"
        return 1
    fi
    
    # Check if file exists
    if [[ ! -f "$program_file" ]]; then
        # Try different locations
        if [[ -f "$VB_EXAMPLES_DIR/$program_file" ]]; then
            program_file="$VB_EXAMPLES_DIR/$program_file"
        elif [[ -f "$VB_USER_PROGRAMS_DIR/$program_file" ]]; then
            program_file="$VB_USER_PROGRAMS_DIR/$program_file"
        elif [[ -f "$program_file.vb" ]]; then
            program_file="$program_file.vb"
        else
            echo "❌ Program file not found: $program_file"
            echo "💡 Searched in:"
            echo "   - Current directory"
            echo "   - $VB_EXAMPLES_DIR"
            echo "   - $VB_USER_PROGRAMS_DIR"
            return 1
        fi
    fi
    
    echo "🔷 Executing VB Program: $(basename "$program_file")"
    echo "📁 File: $program_file"
    echo "🕒 Started: $(date)"
    echo "=========================================="
    echo ""
    
    # Initialize VB interpreter
    vb_init > /dev/null 2>&1
    
    # Set execution context
    VB_CURRENT_FILE="$program_file"
    VB_CURRENT_LINE=0
    
    # Read and execute program line by line
    local line_number=0
    while IFS= read -r line; do
        ((line_number++))
        VB_CURRENT_LINE="$line_number"
        
        # Skip empty lines and comments at file level
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        if [[ -z "$line" || "$line" =~ ^\'.*$ ]]; then
            continue
        fi
        
        # Execute the line
        vb_execute_line "$line"
        
        # Check for END command
        if [[ "$(echo "$line" | awk '{print toupper($1)}')" == "END" ]]; then
            break
        fi
    done < "$program_file"
    
    echo ""
    echo "=========================================="
    echo "🏁 Program execution completed"
    echo "📊 Lines processed: $line_number"
    echo "🕒 Finished: $(date)"
}

vb_list_programs() {
    echo "📚 Available VB Programs:"
    echo "========================="
    echo ""
    
    echo "🔹 Example Programs:"
    if [[ -d "$VB_EXAMPLES_DIR" ]]; then
        find "$VB_EXAMPLES_DIR" -name "*.vb" -type f | while read -r file; do
            local basename=$(basename "$file" .vb)
            local size=$(wc -l < "$file" 2>/dev/null || echo "?")
            echo "   📄 $basename ($size lines)"
        done
    else
        echo "   No example programs found"
    fi
    
    echo ""
    echo "🔹 User Programs:"
    if [[ -d "$VB_USER_PROGRAMS_DIR" ]] && [[ -n "$(find "$VB_USER_PROGRAMS_DIR" -name "*.vb" -type f 2>/dev/null)" ]]; then
        find "$VB_USER_PROGRAMS_DIR" -name "*.vb" -type f | while read -r file; do
            local basename=$(basename "$file" .vb)
            local size=$(wc -l < "$file" 2>/dev/null || echo "?")
            echo "   📄 $basename ($size lines)"
        done
    else
        echo "   No user programs found"
    fi
    
    echo ""
    echo "💡 Usage: vb_run_program <program_name>"
    echo "   Example: vb_run_program calculator"
}

vb_create_program() {
    local program_name="$1"
    
    if [[ -z "$program_name" ]]; then
        echo "❌ Program name required"
        echo "Usage: vb_create_program <program_name>"
        return 1
    fi
    
    # Add .vb extension if not present
    if [[ ! "$program_name" =~ \.vb$ ]]; then
        program_name="$program_name.vb"
    fi
    
    local program_file="$VB_USER_PROGRAMS_DIR/$program_name"
    
    if [[ -f "$program_file" ]]; then
        echo "❌ Program already exists: $program_file"
        return 1
    fi
    
    # Create template program
    cat > "$program_file" << 'EOF'
' VB Program Template
' Created by uDOS VB Program Generator

DIM message As String = "Hello from uDOS VB!"

PRINT "🔷 uDOS VB Program"
PRINT "=================="
PRINT ""
PRINT $message
PRINT ""
PRINT "🎯 Add your VB code here..."

' Your code goes here
' Examples:
' DIM userName As String
' INPUT "Enter your name: ", userName
' PRINT "Hello, "; $userName

END
EOF
    
    echo "✅ Created new VB program: $program_file"
    echo "📝 Edit the file to add your VB code"
    echo "🚀 Run with: vb_run_program $(basename "$program_name" .vb)"
}

vb_help() {
    cat << 'EOF'
🔷 uDOS VB Program Runner v2.0.0

📚 COMMANDS:
  vb_run_program <name>    - Execute a VB program
  vb_list_programs         - List available programs  
  vb_create_program <name> - Create new VB program template
  vb_help                  - Show this help

📁 PROGRAM LOCATIONS:
  Examples: uMemory/scripts/vb-examples/
  User:     uMemory/scripts/vb-programs/

🎯 EXAMPLE PROGRAMS:
  calculator      - Basic calculator with input/output
  mission-tracker - Mission progress tracking
  system-dashboard - System information display

💡 USAGE EXAMPLES:
  vb_run_program calculator
  vb_create_program my-program
  vb_list_programs

🔗 For VB language help, use: VB.HELP
EOF
}

# Main command dispatch
case "${1:-help}" in
    "run") vb_run_program "$2" ;;
    "list") vb_list_programs ;;
    "create") vb_create_program "$2" ;;
    "help"|"--help"|"-h") vb_help ;;
    *) 
        echo "🔷 uDOS VB Program Runner"
        echo "Usage: $0 {run|list|create|help}"
        echo "Try: $0 help"
        ;;
esac
