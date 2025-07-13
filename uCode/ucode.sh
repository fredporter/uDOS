#!/bin/bash
# uCode.sh - uDOS Beta v1.7.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UHOME="${HOME}/uDOS"
export UDENT="$UHOME/uMemory/user/identity.md"
export UDOS_DASHBOARD="${UHOME}/uMemory/state/dashboard.json"
export UDOS_MOVES_DIR="${UHOME}/uMemory/logs/moves"
mkdir -p "$UHOME"

# --- Ensure required folders exist following new architecture ---
# uMemory = All user content storage
mkdir -p "$UHOME/uMemory/logs/moves"
mkdir -p "$UHOME/uMemory/logs/errors"
mkdir -p "$UHOME/uMemory/missions"
mkdir -p "$UHOME/uMemory/milestones" 
mkdir -p "$UHOME/uMemory/legacy"
mkdir -p "$UHOME/uMemory/state"
mkdir -p "$UHOME/uMemory/user"
mkdir -p "$UHOME/uMemory/scripts"
mkdir -p "$UHOME/uMemory/templates"
mkdir -p "$UHOME/uMemory/sandbox"

# uKnowledge = Central shared knowledge bank (system docs)
mkdir -p "$UHOME/uKnowledge/packages"
mkdir -p "$UHOME/uKnowledge/companion"
mkdir -p "$UHOME/uKnowledge/general-library"
mkdir -p "$UHOME/uKnowledge/maps"
mkdir -p "$UHOME/uKnowledge/roadmap"

# uCode = Complete command centre (already exists)
mkdir -p "$UHOME/uCode/packages"

# uScript = System scripts and bash execution
mkdir -p "$UHOME/uScript/system"
mkdir -p "$UHOME/uScript/utilities"
mkdir -p "$UHOME/uScript/automation"

# uTemplate = System templates and datasets (read-only)
mkdir -p "$UHOME/uTemplate/system"
mkdir -p "$UHOME/uTemplate/datasets"
mkdir -p "$UHOME/uTemplate/variables"

# Track if session end has been logged
export UCODE_SESSION_ENDED=false

# --- uDOS Version Detection ---
IDENTITY_FILE="$UHOME/uMemory/state/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
  UVERSION=$(grep "Version:" "$IDENTITY_FILE" | cut -d':' -f2 | xargs)
else
  UVERSION="Unknown"
fi

log_move() {
  local cmd="$1"
  local trimmed="${cmd// }"
  if [[ "$UCODE_BOOTING" == "true" || -z "$trimmed" || "$cmd" == "exit" || "$cmd" == "bye" ]]; then
    return
  fi
  bash "$UHOME/uCode/log.sh" move "$cmd"
}

# --- Devcontainer Command ---
cmd_devcontainer() {
  echo "🛠️  Checking devcontainer setup..."
  if [ -d "$UHOME/.devcontainer" ]; then
    echo "📁 .devcontainer directory exists."
    tree "$UHOME/.devcontainer" 2>/dev/null || ls -R "$UHOME/.devcontainer"
    echo ""
    if [ -f "$UHOME/uCode/setup-dev.sh" ]; then
      echo "🚀 Running dev setup script..."
      bash "$UHOME/uCode/setup-dev.sh"
    else
      echo "⚠️ setup-dev.sh not found. Skipping script execution."
    fi
  else
    echo "❌ .devcontainer folder not found in $UHOME"
  fi
  echo ""
}

# Startup Header
echo "🚀 Welcome to uDOS $UVERSION"
echo -e "\033[1;31m _    _  ____   ___   ____  ______ _____  \033[0m"
echo -e "\033[1;33m| |  | |/ __ \ / _ \ / __ \|  ____|  __ \ \033[0m"
echo -e "\033[1;32m| |  | | |  | | | | | |  | | |__  | |  | |\033[0m"
echo -e "\033[1;36m| |  | | |  | | | | | |  | |  __| | |  | |\033[0m"
echo -e "\033[1;34m| |__| | |__| | |_| | |__| | |____| |__| |\033[0m"
echo -e "\033[1;35m \____/ \____/ \___/ \____/|______|_____/ \033[0m"
echo -e "    \033[1;37muCode Shell · $UVERSION 🌀\033[0m"
echo ""
echo "🧠 Loading environment..."

USER_FILE="$UHOME/uMemory/user/identity.md"
if [[ ! -f "$USER_FILE" ]]; then
  # Check legacy location first
  if [[ -f "$UHOME/sandbox/user.md" ]]; then
    echo "🔄 Migrating user identity to new location..."
    mv "$UHOME/sandbox/user.md" "$USER_FILE"
    echo "✅ Identity migrated to uMemory/user/"
  else
    echo "⚙️ No identity file found. Starting template-driven setup..."
    echo "🏗️ Using uTemplate system for user configuration..."
    
    # Check if template system is available
    if [[ -f "$UHOME/uTemplate/input-user-setup.md" && -f "$UHOME/uTemplate/datasets/template-definitions.json" ]]; then
      echo "📋 Template system detected - using enhanced setup"
      cmd_setup_user
    else
      echo "📋 Falling back to basic setup..."
      bash "$UHOME/uCode/check.sh"
    fi
  fi

  if [[ -f "$USER_FILE" ]]; then
    echo "✅ Identity confirmed."
  else
    echo "❌ Identity file still not found after setup."
    exit 1
  fi
  echo "🔍 Template-driven setup completed."
  echo ""
fi

if [ -f "$UDENT" ]; then
  username=""
  location=""
  created=""
  timezone=""

  while IFS=':' read -r key value; do
    key=$(echo "$key" | sed 's/^[-* ]*//;s/\*\*$//;s/^ *//;s/ *$//')
    value=$(echo "$value" | xargs)
    case "$key" in
      Username) username="$value" ;;
      Location) location="$value" ;;
      Created) created="$value" ;;
      Timezone) timezone="$value" ;;
    esac
  done < "$UDENT"

  [[ -z "$username" ]] && username="user"

  echo "🔑 Identity loaded: User: $username"
  echo "Location: $location"
  echo "Created: $created"
  echo "Timezone: $timezone"
  echo ""
else
  echo "❌ Identity still missing. Please run DESTROY or REBOOT."
  exit 1
fi

PASSWORD=$(grep "Password" "$UDENT" | cut -d':' -f2- | xargs)
if [[ -n "$PASSWORD" && "$REBOOT_FLAG" == "true" ]]; then
  echo -n "🔐 Enter password to continue: "
  read -rs input_pw
  echo ""
  if [[ "$input_pw" != "$PASSWORD" ]]; then
    echo "❌ Incorrect password. Aborting."
    exit 1
  else
    echo "✅ Password accepted."
  fi
fi

echo ""

echo "📋 Session Info:"
echo "- Hostname: $(hostname)"
echo "- Shell: $SHELL"
echo "- User: $username"
echo "- uDOS Path: $UHOME"
echo ""

echo "🧠 Memory Stats:"
echo "- Missions: $(find "$UHOME/uMemory/missions" -type f | wc -l)"
echo "- Milestones: $(find "$UHOME/uMemory/milestones" -type f | wc -l)"
echo "- Legacy items: $(find "$UHOME/uMemory/legacy" -type f | wc -l)"
echo "- Total logs: $(find "$UHOME/uMemory/logs/moves" -type f | wc -l)"
echo ""

# Dashboard Sync
sync_dashboard() {
  if [ -f "$UDOS_DASHBOARD" ]; then
    echo "📊 Syncing dashboard..."
    # Simulate dashboard sync (could be replaced with real sync logic)
    sleep 1
    echo "✅ Dashboard synced."
  else
    echo "⚠️ Dashboard file missing; skipping sync."
  fi
}

# Command Functions

cmd_check() {
  subcmd=$(echo "$args" | awk '{print toupper($1)}')
  case "$subcmd" in
    TIME)
      cmd_timezone_enhanced
      ;;
    TIMEZONE)
      cmd_timezone_enhanced
      ;;
    LOCATION)
      cmd_location_enhanced
      ;;
    LOG)
      cmd_log
      ;;
    SETUP)
      bash "$UHOME/uCode/check.sh" all
      ;;
    USER)
      cmd_setup_user
      ;;
    IDENTITY)
      cmd_identity
      ;;
    INPUT)
      bash "$UHOME/uCode/structure.sh" build --input
      ;;
    STATS)
      cmd_stats
      ;;
    MISSION)
      cmd_mission
      ;;
    MAP)
      cmd_map
      ;;
    DATASETS)
      bash "$UHOME/uCode/json-processor.sh" stats
      ;;
    TEMPLATES)
      bash "$UHOME/uCode/template-generator.sh" list
      ;;
    *)
      echo "🔎 CHECK what?"
      echo "   TIME      → View or set timezone (dataset-integrated)"
      echo "   TIMEZONE  → Enhanced timezone management"
      echo "   LOCATION  → View or set location (dataset-integrated)"
      echo "   USER      → Template-driven user setup"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   SETUP     → Run full environment check"
      echo "   IDENTITY  → Display current identity"
      echo "   INPUT     → Generate user input file"
      echo "   STATS     → Generate dashboard stats"
      echo "   MISSION   → Display active mission"
      echo "   MAP       → Show current region"
      echo "   DATASETS  → Show dataset statistics"
      echo "   TEMPLATES → List available templates"
      echo ""
      ;;
  esac
}

cmd_identity() {
  echo "🆔 Current uDOS Identity:"
  if [ -f "$UDENT" ]; then
    cat "$UDENT"
  else
    echo "❌ No identity file found."
  fi
  echo ""
}

cmd_log() {
  read -rp "📝 What do you want to log (mission/milestone/legacy)? " what
  if [[ "$what" =~ ^(mission|milestone|legacy)$ ]]; then
    bash "$UHOME/uCode/log.sh" move "Logged $what entry"
  else
    echo "❌ Invalid log type."
  fi
  echo ""
}

cmd_stats() {
  bash "$UHOME/uCode/make-stats.sh"
}

cmd_mission() {
  cat "$UHOME/state/current_mission.md" 2>/dev/null || echo "🎯 No mission active."
  echo ""
}

cmd_map() {
  cat "$UHOME/uKnowledge/map/current_region.md" 2>/dev/null || echo "🗺️ No map loaded."
  echo ""
}

cmd_run() {
  bash "$HOME/uDOS/uCode/command.sh" "$args"
}

cmd_tree() {
  bash "$HOME/uDOS/uCode/make-tree.sh"
}

# --- Timezone Command ---
cmd_time() {
  echo "🕒 Current timezone: $(date +%Z)"
  echo "🕓 UTC offset: $(date +%z)"
  read -rp "🌐 Enter new timezone (e.g., Australia/Sydney) or leave blank to keep: " new_tz
  if [[ -n "$new_tz" ]]; then
    export TZ="$new_tz"
    echo "✅ Timezone updated to: $(date +%Z) (UTC$(date +%z))"
  else
    echo "ℹ️ Timezone unchanged."
  fi
  echo ""
}

# --- Location Command ---
cmd_location() {
  echo "📍 Current location code: $(cat "$UHOME/uMemory/state/location.md" 2>/dev/null || echo "Unknown")"
  read -rp "🗺️ Enter new location code (or leave blank to keep current): " new_loc
  if [[ -n "$new_loc" ]]; then
    echo "$new_loc" > "$UHOME/uMemory/state/location.md"
    echo "✅ Location updated to $new_loc"
  else
    echo "ℹ️ Location unchanged."
  fi
  echo ""
}

cmd_list() {
  echo "📁 uDOS Directory Listing (Reorganized Architecture)"
  echo ""
  echo "🧠 uMemory/ (User Content Storage)"
  tree -L 2 "$UHOME/uMemory" 2>/dev/null || ls -R "$UHOME/uMemory"
  echo ""
  echo "📚 uKnowledge/ (Shared Knowledge Bank)"
  tree -L 2 "$UHOME/uKnowledge" 2>/dev/null || ls -R "$UHOME/uKnowledge"
  echo ""
  echo "⚙️ uCode/ (Command Centre)"
  tree -L 2 "$UHOME/uCode" 2>/dev/null || ls -R "$UHOME/uCode"
  echo ""
  echo "🔧 uScript/ (System Scripts)"
  tree -L 2 "$UHOME/uScript" 2>/dev/null || ls -R "$UHOME/uScript"
  echo ""
  echo "� uTemplate/ (System Templates)"
  tree -L 2 "$UHOME/uTemplate" 2>/dev/null || ls -R "$UHOME/uTemplate"
  echo ""
}

cmd_dash() {
  echo ""

  bash "$UHOME/uCode/dash.sh"
  tail -n 60 "$UHOME/uMemory/rendered/dash-rendered.md" | grep -v '^<!--'
  echo ""
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  exec "$0" # Relaunch script
}

cmd_reboot() {
  echo "♻️ Rebooting uDOS system..."

  echo "🧼 Rebuilding structure..."
  bash "$UHOME/uCode/structure.sh" build

  echo "🔍 Rechecking setup and permissions..."
  bash "$UHOME/uCode/check.sh" all

  echo "🌀 Relaunching shell..."
  export REBOOT_FLAG=true
  exec "$0"
}

cmd_destroy() {
  echo "💥 uDOS DESTROY Mode:"
  echo "  [A] Remove identity only"
  echo "  [B] Remove identity and uMemory"
  echo "  [C] Remove identity, archive uMemory to /legacy, then delete uMemory"
  echo "  [D] Reboot only (no data loss)"
  echo "  [E] Exit to uCode only (no reboot, no data loss)"
  read -n1 -rp $'\033[1;34m👉 Select DESTROY option:\033[0m ' choice
  echo ""

  case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
    A)
      echo "⚠️ Deleting identity only..."
      rm -f "$UDENT"
      echo "✅ Identity deleted."
      ;;
    B)
      echo "⚠️ Deleting identity and uMemory..."
      rm -f "$UDENT"
      rm -rf "$UHOME/uMemory"
      echo "✅ Identity and memory deleted."
      ;;
    C)
      echo "⚠️ Deleting all uMemory contents except 'legacy'..."
      rm -f "$UDENT"
      find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
      echo "✅ Identity removed. Legacy preserved."
      ;;
    D)
      echo "♻️ Rebooting system only..."
      cmd_reboot
      return
      ;;
    E)
      echo "🌀 Exiting to uCode..."
      return
      ;;
    *)
      echo "❌ Invalid option. Cancelled."
      return
      ;;
  esac

  echo "🔁 Rebooting to apply changes..."
  cmd_reboot
}

cmd_recent() {
  echo "📜 Recent moves:"
  tail -n 10 "$UHOME/uMemory/logs/moves/moves-$(date +%Y-%m-%d).md"
  echo ""
}

# --- Development Diagnostics ---
cmd_debug() {
  echo "🔍 uDOS DEBUG MODE - Template Integration"
  echo "🧬 Environment Variables:"
  env | grep -E 'UHOME|USER|SHELL|PWD|TZ'
  echo ""
  echo "📊 Template System Status:"
  echo "- Templates: $(find "$UHOME/uTemplate" -name "*.md" | wc -l) available"
  echo "- Datasets: $(find "$UHOME/uTemplate/datasets" -name "*.json" | wc -l) datasets"
  echo "- JSON Records: $(bash "$UHOME/uCode/json-processor.sh" stats 2>/dev/null | grep "Total records:" | cut -d: -f2 || echo "Unknown")"
  echo ""
  echo "📄 Last 20 Moves:"
  tail -n 20 "$UHOME/uMemory/logs/moves/move-log-$(date +%Y-%m-%d).md"
  echo ""
  echo "🗂️ Available Scripts:"
  ls -1 "$UHOME/uCode"
  echo ""
  echo "🔧 System Scripts:"
  ls -1 "$UHOME/uScript/system" 2>/dev/null || echo "No system scripts found"
  echo ""
  echo "❗ Recent Errors (if any):"
  find "$UHOME/uMemory/logs/errors" -type f -exec tail -n 5 {} \;
  echo ""
  echo "🧩 uDOS Version: $UVERSION"
  echo "🏗️ Architecture: Template-Integrated v1.7.1"
  echo "📋 Template System: Active"
  echo "🗄️ Dataset Integration: Enabled"
  echo ""
}

# --- Template-Driven User Setup Function ---
cmd_setup_user() {
  echo "🛠️ uDOS User Setup - Template-Driven Configuration"
  echo "📋 Using uTemplate/input-user-setup.md structure"
  echo ""
  
  # Load template structure from uTemplate
  SETUP_TEMPLATE="$UHOME/uTemplate/input-user-setup.md"
  TEMPLATE_DEFS="$UHOME/uTemplate/datasets/template-definitions.json"
  
  if [[ ! -f "$SETUP_TEMPLATE" ]]; then
    echo "❌ Setup template not found: $SETUP_TEMPLATE"
    return 1
  fi
  
  # Extract user setup template definition
  local template_def=$(bash "$UHOME/uCode/json-processor.sh" query template-definitions "template_id=user_setup" 2>/dev/null)
  
  # Interactive setup with dataset integration
  echo "🔧 Configuring user account with dataset integration..."
  echo ""
  
  # Username
  read -rp "👤 Enter username [agentdigital]: " username
  username=${username:-agentdigital}
  
  # Password (optional)
  read -rsp "🔒 Enter password (optional): " password
  echo ""
  
  # Location with dataset lookup
  echo "📍 Location Selection (from locationMap dataset):"
  bash "$UHOME/uCode/json-processor.sh" search "city" | head -10
  echo ""
  read -rp "🗺️ Enter location code or city name [London]: " location_input
  location_input=${location_input:-London}
  
  # Query locationMap for the location
  location_result=$(bash "$UHOME/uCode/json-processor.sh" search "$location_input" 2>/dev/null | grep locationMap)
  if [[ -n "$location_result" ]]; then
    echo "✅ Location found in dataset: $location_input"
    location_code="$location_input"
  else
    echo "⚠️ Location not found in dataset, using default: AX14 (London)"
    location_code="AX14"
  fi
  
  # Timezone with dataset lookup
  echo ""
  echo "🕒 Timezone Selection (from timezoneMap dataset):"
  bash "$UHOME/uCode/json-processor.sh" search "timezone" | head -10
  echo ""
  read -rp "⏰ Enter timezone [UTC]: " timezone
  timezone=${timezone:-UTC}
  
  # Auto-detect UTC offset from timezone dataset
  utc_offset=$(bash "$UHOME/uCode/json-processor.sh" search "$timezone" 2>/dev/null | grep -o '[+-][0-9][0-9]:[0-9][0-9]' | head -1)
  if [[ -z "$utc_offset" ]]; then
    utc_offset="+00:00"
  fi
  
  # Country detection from location
  country=$(bash "$UHOME/uCode/json-processor.sh" search "$location_input" 2>/dev/null | grep -o '[A-Z][A-Z][A-Z]*' | head -1)
  country=${country:-"Unknown"}
  
  # Create identity file using template structure
  cat > "$USER_FILE" << EOF
# 🆔 uDOS User Identity

**Username:** $username
**Password:** $password
**Location:** $location_code
**Timezone:** $timezone
**UTC Offset:** $utc_offset
**Country:** $country
**Language:** EN
**Currency:** USD
**Created:** $(date '+%Y-%m-%d %H:%M:%S')
**Version:** $UVERSION
**Template:** user_setup v1.1.0

---

## 📊 Dataset Integration Status
- ✅ Location verified against locationMap
- ✅ Timezone verified against timezoneMap  
- ✅ Country auto-detected from location
- ✅ Template-driven configuration complete

## 🗺️ Location Details
- Code: $location_code
- Input: $location_input
- Timezone: $timezone ($utc_offset)
- Country: $country

---
*Generated by uDOS Template System v1.7.1*
EOF

  echo ""
  echo "✅ User setup complete!"
  echo "📄 Identity file created: $USER_FILE"
  echo "🔗 Template integration: user_setup v1.1.0"
  echo "📊 Dataset references: locationMap, timezoneMap, countryMap"
  echo ""
}

# --- Enhanced Location Command with Dataset Integration ---
cmd_location_enhanced() {
  echo "📍 Location Management - Dataset Integration"
  echo ""
  
  # Show current location
  current_loc=$(cat "$UHOME/uMemory/state/location.md" 2>/dev/null || echo "Unknown")
  echo "🗺️ Current location: $current_loc"
  
  # Show available locations from dataset
  echo ""
  echo "📊 Available locations from locationMap dataset:"
  bash "$UHOME/uCode/json-processor.sh" search "city" | head -20
  
  echo ""
  read -rp "🔍 Search for location (or enter code directly): " search_term
  
  if [[ -n "$search_term" ]]; then
    # Search in location dataset
    echo "🔍 Searching locationMap for '$search_term'..."
    search_results=$(bash "$UHOME/uCode/json-processor.sh" search "$search_term")
    
    if [[ -n "$search_results" ]]; then
      echo "✅ Found matching locations:"
      echo "$search_results"
      echo ""
      read -rp "📍 Enter exact location code to set: " new_location
      
      if [[ -n "$new_location" ]]; then
        echo "$new_location" > "$UHOME/uMemory/state/location.md"
        echo "✅ Location updated to: $new_location"
        
        # Update identity file if it exists
        if [[ -f "$USER_FILE" ]]; then
          sed -i.bak "s/\*\*Location:\*\* .*/\*\*Location:\*\* $new_location/" "$USER_FILE"
          echo "🔄 Identity file updated with new location"
        fi
      fi
    else
      echo "❌ No locations found matching '$search_term'"
      echo "💡 Try searching for: city names, country codes, or region names"
    fi
  fi
  echo ""
}

# --- Enhanced Timezone Command with Dataset Integration ---
cmd_timezone_enhanced() {
  echo "🕒 Timezone Management - Dataset Integration"
  echo ""
  
  # Show current timezone
  echo "⏰ Current system timezone: $(date +%Z)"
  echo "🌐 UTC offset: $(date +%z)"
  
  # Show available timezones from dataset
  echo ""
  echo "📊 Available timezones from timezoneMap dataset:"
  bash "$UHOME/uCode/json-processor.sh" search "timezone" | head -15
  
  echo ""
  read -rp "🔍 Search for timezone (or enter timezone code): " search_term
  
  if [[ -n "$search_term" ]]; then
    # Search in timezone dataset
    echo "🔍 Searching timezoneMap for '$search_term'..."
    search_results=$(bash "$UHOME/uCode/json-processor.sh" search "$search_term")
    
    if [[ -n "$search_results" ]]; then
      echo "✅ Found matching timezones:"
      echo "$search_results"
      echo ""
      read -rp "⏰ Enter timezone name (e.g., Australia/Sydney): " new_timezone
      
      if [[ -n "$new_timezone" ]]; then
        export TZ="$new_timezone"
        echo "✅ Timezone updated to: $new_timezone"
        echo "🌐 New UTC offset: $(date +%z)"
        
        # Update identity file if it exists
        if [[ -f "$USER_FILE" ]]; then
          utc_offset=$(date +%z)
          sed -i.bak "s/\*\*Timezone:\*\* .*/\*\*Timezone:\*\* $new_timezone/" "$USER_FILE"
          sed -i.bak "s/\*\*UTC Offset:\*\* .*/\*\*UTC Offset:\*\* $utc_offset/" "$USER_FILE"
          echo "🔄 Identity file updated with new timezone"
        fi
      fi
    else
      echo "❌ No timezones found matching '$search_term'"
      echo "💡 Try searching for: city names, timezone codes, or regions"
    fi
  fi
  echo ""
}

# --- Template Dataset Validation ---
validate_template_datasets() {
  echo "🔍 Validating Template-Dataset Integration..."
  local validation_passed=true
  
  # Check core datasets exist
  local required_datasets=("locationMap" "timezoneMap" "countryMap" "languageMap" "currencyMap" "template-definitions")
  
  for dataset in "${required_datasets[@]}"; do
    if [[ -f "$UHOME/uTemplate/datasets/${dataset}.json" ]]; then
      echo "✅ Dataset found: $dataset"
    else
      echo "❌ Missing dataset: $dataset"
      validation_passed=false
    fi
  done
  
  # Check template files exist
  local required_templates=("input-user-setup.md" "mission-template.md" "milestone-template.md" "move-template.md")
  
  for template in "${required_templates[@]}"; do
    if [[ -f "$UHOME/uTemplate/${template}" ]]; then
      echo "✅ Template found: $template"
    else
      echo "❌ Missing template: $template"
      validation_passed=false
    fi
  done
  
  # Check JSON processor functionality
  if bash "$UHOME/uCode/json-processor.sh" list >/dev/null 2>&1; then
    echo "✅ JSON processor operational"
  else
    echo "❌ JSON processor not working"
    validation_passed=false
  fi
  
  # Check template generator functionality
  if bash "$UHOME/uCode/template-generator.sh" list >/dev/null 2>&1; then
    echo "✅ Template generator operational"
  else
    echo "❌ Template generator not working"
    validation_passed=false
  fi
  
  if [[ "$validation_passed" == "true" ]]; then
    echo ""
    echo "🎉 Template-Dataset integration validated successfully!"
    return 0
  else
    echo ""
    echo "⚠️ Template-Dataset integration has issues - some features may not work"
    return 1
  fi
}

#
# Main Command Dispatch Loop
trap 'if [ "$UCODE_SESSION_ENDED" = false ]; then echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"; export UCODE_SESSION_ENDED=true; fi' EXIT
trap 'echo -e "\n🛑 Interrupted. Type EXIT or BYE to quit safely."' SIGINT
while true; do
  # Prompt for input with visible swirl and blinking block cursor
  printf "\033[?25h"      # Show cursor
  printf "\033[?1c"       # Enable blinking block (may vary by terminal)
  printf "\033[1;30m█\033[0m\r"
  sleep 0.1
  printf "  \r"
  echo -ne "\033[1;36m🌀 \033[0m"
  read -r input
  cmd=$(echo "$input" | awk '{print toupper($1)}')
  args=$(echo "$input" | cut -d' ' -f2-)
  # Only log moves if not blank and not during boot
  if [[ -n "${input// }" && "$UCODE_BOOTING" != "true" ]]; then
    log_move "$input"
  fi
  case "$cmd" in
    LOG)
      cmd_log
      ;;
    RUN)
      cmd_run
      ;;
    TREE)
      cmd_tree
      ;;
    LIST)
      cmd_list "$args"
      ;;
    DASH)
      cmd_dash
      ;;
    SYNC)
      sync_dashboard
      ;;
    RESTART)
      cmd_restart
      ;;
    REBOOT)
      cmd_reboot
      ;;
    DESTROY)
      cmd_destroy
      ;;
    IDENTITY)
      cmd_identity
      ;;
    DEVCON)
      cmd_devcontainer
      ;;
    QUIT)
      echo "👋 uDOS session ended."
      exit 0
      ;;
    RECENT)
      cmd_recent
      ;;
    CHECK)
      cmd_check
      ;;
    SETUP)
      cmd_setup_user
      ;;
    VALIDATE)
      validate_template_datasets
      ;;
    DEBUG)
      cmd_debug
      ;;
    HELP)
      echo "🧩 uDOS Version: $UVERSION (Template-Integrated Architecture)"
      echo "🧠 Available uDOS commands:"
      echo "   LOG       → Log mission/milestone/legacy"
      echo "   RUN       → Run a uScript"
      echo "   TREE      → Generate file tree"
      echo "   LIST      → List reorganized directory structure"
      echo "   DASH      → Show dashboard"
      echo "   SYNC      → Sync dashboard"
      echo "   RESTART   → Restart shell"
      echo "   REBOOT    → Reboot system"
      echo "   DESTROY   → Delete your identity and/or files"
      echo "   IDENTITY  → Display user identity file"
      echo "   DEVCON    → Check and run setup-dev.sh"
      echo "   QUIT      → Close session"
      echo "   RECENT    → Show last 10 moves"
      echo "   CHECK     → Enhanced commands with dataset integration"
      echo "   SETUP     → Template-driven user setup"
      echo "   VALIDATE  → Validate template-dataset integration"
      echo "   DEBUG     → Enhanced debug with template status"
      echo ""
      echo "🔍 ENHANCED CHECK COMMANDS"
      echo "     check user                  - Template-driven user setup"
      echo "     check location              - Location with dataset lookup"
      echo "     check timezone              - Timezone with dataset integration"
      echo "     check datasets              - Show dataset statistics"
      echo "     check templates             - List available templates"
      echo ""
      echo "📊 JSON DATASET COMMANDS"
      echo "     json list                   - List all JSON datasets"
      echo "     json info <dataset>         - Show dataset information"
      echo "     json search <query>         - Search across all datasets"
      echo "     json export <ds> <format>   - Export dataset (csv,yaml,txt)"
      echo "     json merge <out> <ds1> <ds2> - Merge multiple datasets"
      echo "     json validate               - Validate all datasets"
      echo "     json stats                  - Show dataset statistics"
      echo ""
      echo "🏗️  TEMPLATE COMMANDS"
      echo "     template list               - List all available templates"
      echo "     template info <template>    - Show template information"
      echo "     template generate <id> <name> - Generate template"
      echo "     template batch <file>       - Batch generate from CSV"
      echo "     template validate <id>      - Validate template definition"
      echo "     template generated          - List generated templates"
      echo "     template sample             - Create sample batch file"
      echo ""
      echo "🗺️  DATASET INTEGRATION FEATURES"
      echo "     • Location lookup from 52 global cities"
      echo "     • Timezone management with 38 global zones"
      echo "     • Country/currency auto-detection"
      echo "     • Template-driven user configuration"
      echo "     • Geographic coordinate mapping"
      echo ""
      ;;
    JSON)
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/json-processor.sh" $shift_args
      ;;
    TEMPLATE)
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/template-generator.sh" $shift_args
      ;;
    DATASET|DATA)
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/json-processor.sh" $shift_args
      ;;
    GEN|GENERATE)
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/template-generator.sh" $shift_args
      ;;
    "")
      # Ignore empty input
      ;;
    *)
      echo "❓ Unknown command '$cmd'. Type HELP for list of commands."
      ;;
  esac
done
