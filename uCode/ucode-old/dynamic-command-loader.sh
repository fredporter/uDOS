#!/bin/bash
# dynamic-command-loader.sh - Dynamic command extension system for uDOS
# Loads commands from datasets and makes them available in the shell

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
DYNAMIC_COMMANDS_FILE="$UHOME/uTemplate/datasets/dynamic-commands.json"
VARIABLE_SYSTEM_FILE="$UHOME/uTemplate/datasets/variable-system.json"

# Global variables for loaded commands (compatible with older bash)
DYNAMIC_COMMANDS_LIST=""
DYNAMIC_COMMANDS_COUNT=0

# --- Load Dynamic Commands from Dataset ---
load_dynamic_commands() {
  if [[ ! -f "$DYNAMIC_COMMANDS_FILE" ]]; then
    echo "⚠️ Dynamic commands dataset not found: $DYNAMIC_COMMANDS_FILE"
    return 1
  fi

  echo "📥 Loading dynamic commands from dataset..."
  
  # Parse JSON and load commands (compatible with older bash)
  DYNAMIC_COMMANDS_COUNT=0
  DYNAMIC_COMMANDS_LIST=""
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"([^\"]+)\" ]]; then
      local cmd="${BASH_REMATCH[1]}"
      if [[ -z "$DYNAMIC_COMMANDS_LIST" ]]; then
        DYNAMIC_COMMANDS_LIST="$cmd"
      else
        DYNAMIC_COMMANDS_LIST="$DYNAMIC_COMMANDS_LIST|$cmd"
      fi
      ((DYNAMIC_COMMANDS_COUNT++))
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  echo "✅ Loaded $DYNAMIC_COMMANDS_COUNT dynamic commands"
  export DYNAMIC_COMMANDS_LIST DYNAMIC_COMMANDS_COUNT
  return 0
}

# --- Check if command is dynamic ---
is_dynamic_command() {
  local cmd="$1"
  if [[ "$DYNAMIC_COMMANDS_LIST" =~ (^|\\|)$cmd(\\||$) ]]; then
    return 0  # Command found
  else
    return 1  # Command not found
  fi
}

# --- Execute Dynamic Command ---
execute_dynamic_command() {
  local cmd="$1"
  local args="$2"
  
  if ! is_dynamic_command "$cmd"; then
    return 1  # Command not found
  fi
  
  # Extract command details from JSON
  local function_name=""
  local script_path=""
  local syntax=""
  local description=""
  
  # Parse command details (simplified JSON parsing)
  local in_command=false
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"$cmd\" ]]; then
      in_command=true
    elif [[ "$in_command" == true ]]; then
      if [[ "$line" =~ \"function\":\ *\"([^\"]+)\" ]]; then
        function_name="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"script\":\ *\"([^\"]+)\" ]]; then
        script_path="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"syntax\":\ *\"([^\"]+)\" ]]; then
        syntax="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"description\":\ *\"([^\"]+)\" ]]; then
        description="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ ^\s*\}\s*,?\s*$ ]]; then
        break  # End of command object
      fi
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  # Validate command is enabled
  local enabled=true
  if grep -A 20 "\"command\": *\"$cmd\"" "$DYNAMIC_COMMANDS_FILE" | grep -q "\"enabled\": *false"; then
    echo "❌ Command '$cmd' is disabled"
    return 1
  fi
  
  # Execute based on function or script
  if [[ -n "$function_name" ]]; then
    # Try to call function if it exists
    if declare -f "$function_name" >/dev/null 2>&1; then
      echo "▶️ Executing function: $function_name"
      $function_name "$args"
    else
      echo "❌ Function not found: $function_name"
      return 1
    fi
  elif [[ -n "$script_path" ]]; then
    # Execute script
    local full_script_path="$UHOME/uCode/$script_path"
    if [[ -f "$full_script_path" ]]; then
      echo "▶️ Executing script: $script_path"
      if [[ "$script_path" =~ \.sh$ ]]; then
        bash "$full_script_path" $args
      else
        "$full_script_path" $args
      fi
    else
      echo "❌ Script not found: $full_script_path"
      return 1
    fi
  else
    echo "❌ No execution method defined for command: $cmd"
    return 1
  fi
}

# --- Get Dynamic Command Help ---
get_dynamic_command_help() {
  local cmd="$1"
  
  if ! is_dynamic_command "$cmd"; then
    return 1
  fi
  
  echo "📖 Dynamic Command Help: $cmd"
  echo ""
  
  # Extract help information
  local syntax="" description="" examples=() help_text=""
  local in_command=false in_examples=false
  
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"$cmd\" ]]; then
      in_command=true
    elif [[ "$in_command" == true ]]; then
      if [[ "$line" =~ \"syntax\":\ *\"([^\"]+)\" ]]; then
        syntax="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"description\":\ *\"([^\"]+)\" ]]; then
        description="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"help_text\":\ *\"([^\"]+)\" ]]; then
        help_text="${BASH_REMATCH[1]}"
      elif [[ "$line" =~ \"examples\":\ *\[ ]]; then
        in_examples=true
      elif [[ "$in_examples" == true && "$line" =~ \"([^\"]+)\" ]]; then
        examples+=("${BASH_REMATCH[1]}")
      elif [[ "$line" =~ ^\s*\]\s*,?\s*$ ]]; then
        in_examples=false
      elif [[ "$line" =~ ^\s*\}\s*,?\s*$ ]]; then
        break
      fi
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  # Display help information
  [[ -n "$syntax" ]] && echo "📝 Syntax: $syntax"
  [[ -n "$description" ]] && echo "📄 Description: $description"
  [[ -n "$help_text" ]] && echo "💡 Help: $help_text"
  
  if [[ ${#examples[@]} -gt 0 ]]; then
    echo ""
    echo "📚 Examples:"
    for example in "${examples[@]}"; do
      echo "   $example"
    done
  fi
  echo ""
}

# --- List All Dynamic Commands ---
list_dynamic_commands() {
  echo "📋 Available Dynamic Commands:"
  echo ""
  
  local categories=()
  local current_category=""
  
  # Group commands by category
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"([^\"]+)\" ]]; then
      local cmd="${BASH_REMATCH[1]}"
      echo "   $cmd"
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  echo ""
  echo "💡 Use 'HELP <command>' for detailed information"
  echo "🔧 Use 'DYNAMIC list categories' to see commands by category"
}

# --- List Commands by Category ---
list_commands_by_category() {
  echo "📂 Dynamic Commands by Category:"
  echo ""
  
  local categories=()
  declare -A category_commands
  
  # Parse and group commands
  local current_cmd="" current_category=""
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"([^\"]+)\" ]]; then
      current_cmd="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ \"category\":\ *\"([^\"]+)\" ]]; then
      current_category="${BASH_REMATCH[1]}"
      if [[ -n "$current_cmd" && -n "$current_category" ]]; then
        if [[ -z "${category_commands[$current_category]}" ]]; then
          categories+=("$current_category")
          category_commands["$current_category"]="$current_cmd"
        else
          category_commands["$current_category"]="${category_commands[$current_category]}, $current_cmd"
        fi
      fi
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  # Display by category
  for category in "${categories[@]}"; do
    echo "🏷️ $category:"
    echo "   ${category_commands[$category]}"
    echo ""
  done
}

# --- Validate Dynamic Command ---
validate_dynamic_command() {
  local cmd="$1"
  local args="$2"
  
  # Extract validation rules
  local args_required=0
  local arg_pattern=""
  
  local in_command=false in_validation=false
  while IFS= read -r line; do
    if [[ "$line" =~ \"command\":\ *\"$cmd\" ]]; then
      in_command=true
    elif [[ "$in_command" == true ]]; then
      if [[ "$line" =~ \"validation\":\ *\{ ]]; then
        in_validation=true
      elif [[ "$in_validation" == true ]]; then
        if [[ "$line" =~ \"args_required\":\ *([0-9]+) ]]; then
          args_required="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ \"arg_pattern\":\ *\"([^\"]+)\" ]]; then
          arg_pattern="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^\s*\}\s*,?\s*$ ]]; then
          in_validation=false
        fi
      elif [[ "$line" =~ ^\s*\}\s*,?\s*$ && "$in_validation" == false ]]; then
        break
      fi
    fi
  done < "$DYNAMIC_COMMANDS_FILE"
  
  # Validate argument count
  local arg_count=0
  if [[ -n "$args" ]]; then
    arg_count=$(echo "$args" | wc -w)
  fi
  
  if [[ $arg_count -lt $args_required ]]; then
    echo "❌ Command '$cmd' requires at least $args_required arguments"
    return 1
  fi
  
  # Validate argument pattern
  if [[ -n "$arg_pattern" && -n "$args" ]]; then
    if ! [[ "$args" =~ $arg_pattern ]]; then
      echo "❌ Invalid arguments for command '$cmd'"
      return 1
    fi
  fi
  
  return 0
}

# --- Main Dynamic Command Handler ---
handle_dynamic_command() {
  local cmd="$1"
  local args="$2"
  
  # Special dynamic command system commands
  case "$cmd" in
    DYNAMIC)
      local subcmd=$(echo "$args" | awk '{print toupper($1)}')
      case "$subcmd" in
        RELOAD)
          load_dynamic_commands
          ;;
        LIST)
          local filter=$(echo "$args" | awk '{print tolower($2)}')
          if [[ "$filter" == "categories" ]]; then
            list_commands_by_category
          else
            list_dynamic_commands
          fi
          ;;
        HELP)
          local help_cmd=$(echo "$args" | awk '{print toupper($2)}')
          if [[ -n "$help_cmd" ]]; then
            get_dynamic_command_help "$help_cmd"
          else
            echo "Usage: DYNAMIC HELP <command>"
          fi
          ;;
        STATUS)
          echo "🔧 Dynamic Command System Status:"
          echo "Commands loaded: $DYNAMIC_COMMANDS_COUNT"
          echo "Dataset file: $DYNAMIC_COMMANDS_FILE"
          echo "Last loaded: $(date)"
          ;;
        *)
          echo "🔧 Dynamic Command System:"
          echo "   DYNAMIC RELOAD    → Reload command definitions"
          echo "   DYNAMIC LIST      → List all dynamic commands"
          echo "   DYNAMIC HELP <cmd> → Get help for specific command"
          echo "   DYNAMIC STATUS    → Show system status"
          ;;
      esac
      return 0
      ;;
  esac
  
  # Check if it's a dynamic command
  if is_dynamic_command "$cmd"; then
    # Validate command arguments
    if validate_dynamic_command "$cmd" "$args"; then
      # Execute the command
      execute_dynamic_command "$cmd" "$args"
    fi
    return 0
  fi
  
  return 1  # Not a dynamic command
}

# --- Dynamic Command Function Implementations ---

# Package installation function
cmd_install_package() {
  local package_name="$1"
  echo "📦 Installing package: $package_name"
  
  local install_script="$UHOME/uCode/packages/install-$package_name.sh"
  if [[ -f "$install_script" ]]; then
    bash "$install_script"
  else
    echo "❌ Install script not found for package: $package_name"
    echo "💡 Available packages:"
    find "$UHOME/uCode/packages" -name "install-*.sh" | sed 's/.*install-\(.*\)\.sh/   \1/'
  fi
}

# Search datasets function
cmd_search_datasets() {
  local query="$1"
  local dataset="$2"
  
  echo "🔍 Searching datasets for: $query"
  if [[ -n "$dataset" ]]; then
    echo "📊 Limiting search to dataset: $dataset"
  fi
  echo ""
  
  bash "$UHOME/uCode/json-processor.sh" search "$query" "$dataset"
}

# Export data function
cmd_export_data() {
  local dataset="$1"
  local format="${2:-csv}"
  
  echo "📤 Exporting dataset '$dataset' in format '$format'"
  bash "$UHOME/uCode/json-processor.sh" export "$dataset" "$format"
}

# Backup system function
cmd_backup_system() {
  local target="${1:-all}"
  echo "💾 Creating backup of: $target"
  
  local backup_dir="$UHOME/uMemory/backups"
  mkdir -p "$backup_dir"
  
  local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
  local backup_file="$backup_dir/udos-backup-$target-$timestamp.tar.gz"
  
  case "$target" in
    memory)
      tar -czf "$backup_file" -C "$UHOME" uMemory/
      ;;
    missions)
      tar -czf "$backup_file" -C "$UHOME" uMemory/missions/
      ;;
    all)
      tar -czf "$backup_file" -C "$UHOME" uMemory/ uKnowledge/ uTemplate/variables/
      ;;
    *)
      echo "❌ Unknown backup target: $target"
      return 1
      ;;
  esac
  
  echo "✅ Backup created: $backup_file"
}

# Health check function
cmd_health_check() {
  local component="${1:-all}"
  echo "🏥 Running health check for: $component"
  echo ""
  
  local issues=0
  
  case "$component" in
    memory|all)
      echo "🧠 Checking memory integrity..."
      if [[ ! -d "$UHOME/uMemory" ]]; then
        echo "❌ uMemory directory missing"
        ((issues++))
      else
        echo "✅ uMemory directory exists"
      fi
      ;;
  esac
  
  case "$component" in
    templates|all)
      echo "📋 Checking template system..."
      if [[ ! -f "$UHOME/uCode/template-generator.sh" ]]; then
        echo "❌ Template generator missing"
        ((issues++))
      else
        echo "✅ Template generator available"
      fi
      ;;
  esac
  
  case "$component" in
    packages|all)
      echo "📦 Checking package system..."
      if [[ ! -d "$UHOME/uCode/packages" ]]; then
        echo "❌ Package directory missing"
        ((issues++))
      else
        local package_count=$(find "$UHOME/uCode/packages" -name "*.sh" | wc -l)
        echo "✅ Package system available ($package_count scripts)"
      fi
      ;;
  esac
  
  echo ""
  if [[ $issues -eq 0 ]]; then
    echo "🎉 Health check passed - no issues found"
  else
    echo "⚠️ Health check found $issues issues"
  fi
}

# Initialize dynamic command system
initialize_dynamic_commands() {
  echo "🚀 Initializing dynamic command system..."
  load_dynamic_commands
  echo "✅ Dynamic command system ready"
}

# Export functions for use in main shell
export -f handle_dynamic_command
export -f initialize_dynamic_commands
export -f get_dynamic_command_help
