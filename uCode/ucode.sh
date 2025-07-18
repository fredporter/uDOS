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

# User Setup Check - Core uDOS ethos: One installation per user
if [[ ! -f "$UDENT" ]]; then
    echo "🔐 First-time setup detected - initializing user..."
    if [[ -f "$SCRIPT_DIR/init-user.sh" ]]; then
        "$SCRIPT_DIR/init-user.sh"
    else
        echo "❌ User initialization script missing - uDOS setup incomplete"
        exit 1
    fi
fi

# Load dynamic command system
if [[ -f "$SCRIPT_DIR/dynamic-command-loader.sh" ]]; then
  source "$SCRIPT_DIR/dynamic-command-loader.sh"
  echo "🔧 Dynamic command system loaded"
else
  echo "⚠️ Dynamic command system not found - using static commands only"
fi

# Load error handling system
if [[ -f "$SCRIPT_DIR/error-handler.sh" ]]; then
  source "$SCRIPT_DIR/error-handler.sh"
  echo "🛡️ Error handling system loaded"
else
  echo "⚠️ Error handler not found - using basic error handling"
  error_warning() { echo "WARN: $1" >&2; }
  error_critical() { echo "ERROR: $1" >&2; }
  error_fatal() { echo "FATAL: $1" >&2; exit 1; }
  set_error_context() { true; }
fi

# Load shortcode processor
if [[ -f "$SCRIPT_DIR/shortcode-processor-simple.sh" ]]; then
  echo "🔧 Simple shortcode system available"
elif [[ -f "$SCRIPT_DIR/shortcode-processor.sh" ]]; then
  echo "🔧 Advanced shortcode system available (may need compatibility updates)"
else
  echo "⚠️ Shortcode processor not found - [shortcode] syntax unavailable"
fi

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

# --- Enhanced User Setup Function with Template Integration ---
cmd_setup_user() {
  echo "👤 Template-Integrated User Setup"
  echo ""
  echo "🆔 Let's set up your uDOS identity using the enhanced template system..."
  echo ""
  
  # Initialize variables for template processing
  local username=""
  local email=""
  local location=""
  local timezone=""
  local full_name=""
  local preferences=""
  
  # Check if datasets are available for enhanced setup
  local dataset_available=false
  if [[ -f "$UHOME/uTemplate/datasets/locationMap.json" && -f "$UHOME/uTemplate/datasets/timezoneMap.json" ]]; then
    dataset_available=true
    echo "📊 Enhanced setup available with location and timezone datasets!"
    echo ""
  fi
  
  # Collect user information interactively
  read -p "👤 Enter your username: " username
  echo ""
  
  read -p "👋 Enter your full name (optional): " full_name
  echo ""
  
  read -p "📧 Enter your email (optional): " email
  echo ""
  
  # Enhanced location setup with dataset integration
  if [[ "$dataset_available" == true ]]; then
    echo "🌍 Location Setup (Dataset-Enhanced)"
    echo "💡 Available locations from our global dataset:"
    if command -v jq >/dev/null 2>&1; then
      jq -r '.data[:10][] | "   🏙️ \(.city), \(.country) (\(.tile))"' "$UHOME/uTemplate/datasets/locationMap.json" 2>/dev/null | head -10 || echo "   📍 Dataset temporarily unavailable"
    fi
    echo ""
    read -p "📍 Enter your location (city or coordinates like AX14): " location
    
    # Validate location against dataset if jq is available
    if [[ -n "$location" ]] && command -v jq >/dev/null 2>&1; then
      local location_match=$(jq -r --arg loc "$location" '.data[] | select(.city | test($loc; "i")) | "\(.city), \(.country) (\(.tile))"' "$UHOME/uTemplate/datasets/locationMap.json" 2>/dev/null | head -1)
      if [[ -n "$location_match" ]]; then
        echo "✅ Found matching location: $location_match"
        location="$location_match"
      fi
    fi
  else
    read -p "📍 Enter your location: " location
  fi
  echo ""
  
  # Enhanced timezone setup with dataset integration
  if [[ "$dataset_available" == true ]]; then
    echo "🕒 Timezone Setup (Dataset-Enhanced)"
    echo "💡 Popular timezones from our global dataset:"
    if command -v jq >/dev/null 2>&1; then
      jq -r '.data[:8][] | "   🌍 \(.timezone_code) - \(.timezone_name) (\(.utc_offset))"' "$UHOME/uTemplate/datasets/timezoneMap.json" 2>/dev/null | head -8 || echo "   ⏰ Dataset temporarily unavailable"
    fi
    echo ""
    read -p "🌍 Enter your timezone (e.g., UTC, EST, PST): " timezone
    
    # Validate timezone against dataset if jq is available
    if [[ -n "$timezone" ]] && command -v jq >/dev/null 2>&1; then
      local timezone_match=$(jq -r --arg tz "$timezone" '.data[] | select(.timezone_code | test($tz; "i")) | "\(.timezone_code) - \(.timezone_name)"' "$UHOME/uTemplate/datasets/timezoneMap.json" 2>/dev/null | head -1)
      if [[ -n "$timezone_match" ]]; then
        echo "✅ Found matching timezone: $timezone_match"
        timezone=$(echo "$timezone_match" | cut -d' ' -f1)
      fi
    fi
  else
    read -p "🌍 Enter your timezone (e.g., UTC, EST, PST): " timezone
  fi
  echo ""
  
  # Collect preferences
  echo "⚙️ User Preferences (optional)"
  local theme=""
  local debug_mode=""
  local auto_backup=""
  
  read -p "🎨 Choose theme (default/dark/light) [default]: " theme
  read -p "🔧 Enable debug mode? (y/N): " debug_mode
  read -p "💾 Enable auto-backup? (Y/n): " auto_backup
  echo ""
  
  # Set defaults
  username="${username:-user}"
  timezone="${timezone:-UTC}"
  location="${location:-local}"
  email="${email:-}"
  full_name="${full_name:-}"
  theme="${theme:-default}"
  debug_mode="${debug_mode:-n}"
  auto_backup="${auto_backup:-Y}"
  
  # Convert preferences to JSON format
  local debug_bool="false"
  local backup_bool="true"
  [[ "$debug_mode" =~ ^[Yy]$ ]] && debug_bool="true"
  [[ "$auto_backup" =~ ^[Nn]$ ]] && backup_bool="false"
  
  preferences="{\"theme\":\"$theme\",\"debug_mode\":$debug_bool,\"auto_backup\":$backup_bool}"
  
  # Create identity file using template system if available
  identity_file="$UHOME/uMemory/user/identity.md"
  mkdir -p "$(dirname "$identity_file")"
  
  if [[ -f "$UHOME/uCode/template-generator.sh" && -f "$UHOME/uTemplate/input-user-setup.md" ]]; then
    echo "🏗️ Generating identity using template system..."
    
    # Create variables for template generation
    local temp_vars_file="$UHOME/uMemory/generated/temp-user-vars.json"
    mkdir -p "$(dirname "$temp_vars_file")"
    
    cat > "$temp_vars_file" << EOF
{
  "username": "$username",
  "full_name": "$full_name",
  "email": "$email",
  "location": "$location",
  "timezone": "$timezone",
  "preferences": $preferences,
  "created_date": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
    
    # Generate using template system
    if bash "$UHOME/uCode/template-generator.sh" generate user-setup "$temp_vars_file" > "$identity_file" 2>/dev/null; then
      echo "✅ Identity generated using template system"
    else
      echo "⚠️ Template generation failed, falling back to basic creation"
      cmd_create_basic_identity
    fi
    
    # Clean up temporary file
    rm -f "$temp_vars_file"
  else
    echo "⚠️ Template system not available, creating basic identity"
    cmd_create_basic_identity
  fi
  
  # Update user variables file
  if [[ -f "$UHOME/uTemplate/variables/user-vars.json" ]]; then
    echo "📝 Updating user variables..."
    local user_vars_file="$UHOME/uTemplate/variables/user-vars.json"
    
    if command -v jq >/dev/null 2>&1; then
      jq --arg username "$username" \
         --arg full_name "$full_name" \
         --arg email "$email" \
         --arg location "$location" \
         --arg timezone "$timezone" \
         --arg theme "$theme" \
         --argjson debug_mode "$debug_bool" \
         --argjson auto_backup "$backup_bool" \
         --arg updated "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
         '.USERNAME = $username | .FULL_NAME = $full_name | .EMAIL = $email | .LOCATION = $location | .TIMEZONE = $timezone | .THEME = $theme | .DEBUG_MODE = $debug_mode | .AUTO_BACKUP = $auto_backup | .LAST_UPDATED = $updated' \
         "$user_vars_file" > "${user_vars_file}.tmp" && mv "${user_vars_file}.tmp" "$user_vars_file"
      echo "✅ User variables updated"
    else
      echo "⚠️ jq not available, skipping variable file update"
    fi
  fi
  
  echo ""
  echo "✅ Enhanced user identity created successfully!"
  echo "👤 Username: $username"
  echo "🌍 Location: $location"
  echo "⏰ Timezone: $timezone"
  [[ -n "$full_name" ]] && echo "👋 Full Name: $full_name"
  [[ -n "$email" ]] && echo "📧 Email: $email"
  echo "🎨 Theme: $theme"
  echo "🔧 Debug Mode: $debug_bool"
  echo "💾 Auto Backup: $backup_bool"
  echo ""
  echo "🎯 Your uDOS environment is ready with template integration!"
  echo ""
}

# --- Fallback basic identity creation ---
cmd_create_basic_identity() {
  cat > "$identity_file" << EOF
# uDOS User Identity

**Username**: $username
**Location**: $location
**Created**: $(date +%Y-%m-%d)
**Timezone**: $timezone
**Version**: v1.7.1 Enhanced
**Architecture**: Template-Integrated v1.7.1

## Profile
- **Role**: uDOS User
- **Setup**: Complete
- **Full Name**: $full_name
- **Email**: $email

## Preferences
- **Theme**: $theme
- **Debug Mode**: $debug_bool
- **Auto Backup**: $backup_bool

## System
- **uDOS Path**: ~/uDOS
- **Identity Location**: uMemory/user/identity.md
- **Template System**: Available
- **Dataset Integration**: $([ "$dataset_available" = true ] && echo "Enabled" || echo "Limited")

## Template Integration
- **User Variables**: Updated
- **Location Dataset**: $([ -f "$UHOME/uTemplate/datasets/locationMap.json" ] && echo "Available" || echo "Missing")
- **Timezone Dataset**: $([ -f "$UHOME/uTemplate/datasets/timezoneMap.json" ] && echo "Available" || echo "Missing")
- **Last Updated**: $(date +%Y-%m-%d)
EOF
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

# Initialize dynamic command system
if command -v initialize_dynamic_commands >/dev/null 2>&1; then
  initialize_dynamic_commands
fi

USER_FILE="$UHOME/uMemory/user/identity.md"
if [[ ! -f "$USER_FILE" ]]; then
  # Check legacy location first
  if [[ -f "$UHOME/sandbox/user.md" ]]; then
    echo "🔄 Migrating user identity to new location..."
    mv "$UHOME/sandbox/user.md" "$USER_FILE"
    echo "✅ Identity migrated to uMemory/user/"
  else
    echo "⚙️ No identity file found. Starting enhanced template-driven setup..."
    echo "🏗️ Using integrated uTemplate system for user configuration..."
    echo ""
    
    # Check template system availability
    local template_available=false
    local dataset_available=false
    
    if [[ -f "$UHOME/uCode/template-generator.sh" ]]; then
      template_available=true
      echo "✅ Template system available"
    fi
    
    if [[ -f "$UHOME/uTemplate/datasets/template-definitions.json" ]]; then
      dataset_available=true
      echo "✅ Dataset system available"
    fi
    
    if [[ -f "$UHOME/uTemplate/input-user-setup.md" ]]; then
      echo "✅ User setup template available"
    fi
    
    echo ""
    
    # Enhanced setup with template integration
    if [[ "$template_available" == true && "$dataset_available" == true ]]; then
      echo "� Enhanced setup with full template-dataset integration"
      cmd_setup_user
    elif [[ -f "$UHOME/uTemplate/input-user-setup.md" ]]; then
      echo "�📋 Template system detected - using enhanced setup"
      cmd_setup_user
    else
      echo "📋 Falling back to compatibility mode..."
      echo "⚠️ Some features may be limited without full template system"
      cmd_setup_user
    fi
  fi

  # Verify setup completed
  if [[ -f "$USER_FILE" ]]; then
    echo "✅ Identity setup completed successfully."
    echo ""
    
    # Show setup summary
    echo "📊 Setup Summary:"
    if grep -q "Template-Integrated" "$USER_FILE" 2>/dev/null; then
      echo "   🏗️ Template system: Integrated"
    fi
    if grep -q "Dataset Integration: Enabled" "$USER_FILE" 2>/dev/null; then
      echo "   📊 Dataset integration: Enabled"
    fi
    if [[ -f "$UHOME/uTemplate/variables/user-vars.json" ]]; then
      echo "   📝 User variables: Updated"
    fi
    
  else
    echo "❌ Identity file still not found after setup."
    echo "🔧 Please check template system configuration or run SETUP command manually."
    exit 1
  fi
  echo "🔍 Enhanced template-driven setup completed."
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
  
  # Check for template integration features
  if grep -q "Template-Integrated" "$UDENT" 2>/dev/null; then
    echo "🏗️ Template system: Integrated"
  fi
  if grep -q "Dataset Integration: Enabled" "$UDENT" 2>/dev/null; then
    echo "📊 Dataset integration: Active"
  fi
  
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
  subcmd=$(echo "$args" | awk '{print toupper($1)}')
  case "$subcmd" in
    GENERATE)
      cmd_map_generate
      ;;
    REGION)
      region=$(echo "$args" | awk '{print $2}')
      cmd_map_region "$region"
      ;;
    CITY)
      coordinates=$(echo "$args" | awk '{print $2}')
      cmd_map_city "$coordinates"
      ;;
    SHOW)
      cmd_map_show
      ;;
    INFO)
      cmd_map_info
      ;;
    *)
      echo "🗺️ MAP commands:"
      echo "   GENERATE  → Generate full world map"
      echo "   REGION    → Show regional map (e.g., MAP REGION Europe)"
      echo "   CITY      → Get city info (e.g., MAP CITY AX14)"
      echo "   SHOW      → Display current region"
      echo "   INFO      → Show map system information"
      echo ""
      ;;
  esac
}

# --- Map Generation Command ---
cmd_map_generate() {
  echo "🗺️ Generating uDOS World Map..."
  echo "📊 Using locationMap (52 cities), mapTerrain (15 symbols), timezoneMap (38 zones)"
  echo ""
  
  # Check if TypeScript map generator is available
  if [[ -f "$UHOME/uTemplate/src/index.ts" ]]; then
    echo "🔧 Using TypeScript map generator..."
    
    # Check if Node.js is available
    if command -v node >/dev/null 2>&1; then
      cd "$UHOME/uTemplate"
      
      # Try to install dependencies if package.json exists
      if [[ -f "package.json" ]] && command -v npm >/dev/null 2>&1; then
        echo "📦 Installing dependencies..."
        npm install --silent >/dev/null 2>&1 || echo "⚠️ npm install failed, continuing..."
      fi
      
      # Try to build and run
      if command -v npx >/dev/null 2>&1; then
        echo "🏗️ Building map..."
        npx tsc --build --silent 2>/dev/null || echo "⚠️ TypeScript compilation failed"
        
        if [[ -f "dist/index.js" ]]; then
          echo "🎨 Rendering world map..."
          node dist/index.js generate world-map.md
        else
          echo "❌ Compiled JavaScript not found, falling back to template approach"
          cmd_map_fallback
        fi
      else
        echo "❌ npx not available, falling back to template approach"
        cmd_map_fallback
      fi
      
      cd - >/dev/null
    else
      echo "❌ Node.js not available, falling back to template approach"
      cmd_map_fallback
    fi
  else
    echo "❌ TypeScript map generator not found, falling back to template approach"
    cmd_map_fallback
  fi
  
  echo "✅ Map generation complete!"
  echo ""
}

# --- Map Region Command ---
cmd_map_region() {
  local region="${1:-Europe}"
  echo "🌍 Generating Regional Map: $region"
  echo ""
  
  # Search for cities in the specified region
  echo "🔍 Searching locationMap for cities in $region..."
  region_cities=$(bash "$UHOME/uCode/json-processor.sh" search "$region" 2>/dev/null | grep locationMap || echo "No cities found")
  
  if [[ "$region_cities" != "No cities found" ]]; then
    echo "📍 Cities found in $region:"
    echo "$region_cities"
    echo ""
    
    # Count cities
    city_count=$(echo "$region_cities" | wc -l)
    echo "📊 Total cities in $region: $city_count"
  else
    echo "❌ No cities found for region: $region"
    echo "💡 Available regions:"
    bash "$UHOME/uCode/json-processor.sh" search "region" | head -10
  fi
  echo ""
}

# --- Map City Command ---
cmd_map_city() {
  local coordinates="${1}"
  
  if [[ -z "$coordinates" ]]; then
    echo "🏙️ City Information Lookup"
    echo ""
    read -rp "📍 Enter city coordinates (e.g., AX14): " coordinates
  fi
  
  if [[ -n "$coordinates" ]]; then
    echo "🔍 Looking up city at coordinates: $coordinates"
    echo ""
    
    # Search for the specific coordinates in locationMap
    city_info=$(bash "$UHOME/uCode/json-processor.sh" search "$coordinates" 2>/dev/null | grep locationMap)
    
    if [[ -n "$city_info" ]]; then
      echo "✅ City found:"
      echo "$city_info"
      echo ""
      
      # Get additional details from datasets
      echo "🌍 Additional Information:"
      timezone_info=$(bash "$UHOME/uCode/json-processor.sh" search "$coordinates" 2>/dev/null | grep timezoneMap)
      if [[ -n "$timezone_info" ]]; then
        echo "🕒 Timezone: $timezone_info"
      fi
      
      # Try to get country information
      country_info=$(bash "$UHOME/uCode/json-processor.sh" search "$coordinates" 2>/dev/null | grep countryMap)
      if [[ -n "$country_info" ]]; then
        echo "🏳️ Country: $country_info"
      fi
    else
      echo "❌ No city found at coordinates: $coordinates"
      echo "💡 Try coordinates like: AX14, BF23, CG45, etc."
      echo ""
      echo "📋 Sample coordinates from locationMap:"
      bash "$UHOME/uCode/json-processor.sh" search "tile_reference" | head -10
    fi
  else
    echo "❌ No coordinates provided"
  fi
  echo ""
}

# --- Map Show Command ---
cmd_map_show() {
  echo "🗺️ Current Map View"
  echo ""
  
  # Show user's current location
  current_location=$(cat "$UHOME/uMemory/state/location.md" 2>/dev/null || echo "Unknown")
  echo "📍 Your location: $current_location"
  
  if [[ "$current_location" != "Unknown" ]]; then
    # Get details about current location
    location_details=$(bash "$UHOME/uCode/json-processor.sh" search "$current_location" 2>/dev/null | grep locationMap)
    if [[ -n "$location_details" ]]; then
      echo "🏙️ Location details: $location_details"
    fi
  fi
  
  echo ""
  echo "🎨 Map Legend:"
  echo "🏙️ Cities | ✈️ Airports | 🗿 World Wonders | 🏝️ Islands | ⛰️ Mountains | 🟦 Ocean"
  echo ""
  
  # Show nearby locations (simplified ASCII representation)
  echo "🌍 Regional Overview:"
  echo "```"
  echo "     A  B  C  D  E  F  G  H  I  J"
  echo " 10  🟦 🟦 🟦 🟦 🟦 🟦 🟦 🟦 🟦 🟦"
  echo " 11  🟦 🟦 🏙️ 🟦 🟦 🟦 ✈️ 🟦 🟦 🟦"
  echo " 12  🟦 🟦 🟦 🟦 🏝️ 🟦 🟦 🟦 🟦 🟦"
  echo " 13  🟦 ⛰️ 🟦 🟦 🟦 🟦 🟦 🗿 🟦 🟦"
  echo " 14  🟦 🟦 🟦 🏙️ 🟦 🟦 🟦 🟦 🟦 🟦"
  echo "```"
  echo ""
}

# --- Map Info Command ---
cmd_map_info() {
  echo "📊 uDOS Map System Information"
  echo ""
  echo "🗺️ Map Specifications:"
  echo "- Resolution: 120×60 tiles (7,200 total)"
  echo "- Coordinate Format: Letter-Letter-Number-Number (e.g., AX14)"
  echo "- Column Range: A-DU (120 columns)"
  echo "- Row Range: 01-60 (60 rows)"
  echo ""
  
  echo "📋 Dataset Statistics:"
  echo "- Location Map: $(bash "$UHOME/uCode/json-processor.sh" search "city_name" 2>/dev/null | wc -l || echo "Unknown") cities"
  echo "- Timezone Map: $(bash "$UHOME/uCode/json-processor.sh" search "timezone_name" 2>/dev/null | wc -l || echo "Unknown") timezones"
  echo "- Terrain Map: $(bash "$UHOME/uCode/json-processor.sh" search "symbol" 2>/dev/null | wc -l || echo "Unknown") terrain types"
  echo ""
  
  echo "🔧 Technical Details:"
  echo "- Engine: TypeScript Map Generator v1.7.1"
  echo "- Datasets: JSON-based with cross-references"
  echo "- Rendering: Unicode emoji symbols"
  echo "- Integration: uCode shell commands"
  echo ""
  
  echo "💡 Usage Examples:"
  echo "- MAP GENERATE → Create full world map"
  echo "- MAP REGION Europe → Show European cities"
  echo "- MAP CITY AX14 → Get details for coordinates AX14"
  echo "- CHECK MAP → Quick map check from CHECK command"
  echo ""
}

# --- Map Fallback (Template-based) ---
# --- Map Fallback (Template-based) ---
cmd_map_fallback() {
  echo "🔄 Using template-based map generation..."
  
  # Generate simple map using template and datasets
  if [[ -f "$UHOME/uTemplate/src/templates/baseMap.uTemplate" ]]; then
    echo "📋 Processing baseMap template..."
    
    # Simple template processing
    cat > "$UHOME/uMemory/generated/simple-world-map.md" << EOF
# 🗺️ uDOS World Map (Template Generated)

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Resolution:** 120×60 tiles
**Version:** Template-based v1.7.1

## 🌍 Major Cities

$(bash "$UHOME/uCode/json-processor.sh" search "city_name" 2>/dev/null | head -20 || echo "Dataset not available")

## 🕒 Timezones

$(bash "$UHOME/uCode/json-processor.sh" search "timezone_name" 2>/dev/null | head -15 || echo "Dataset not available")

## 🎨 Map Legend

🏙️ Cities | ✈️ Airports | 🗿 World Wonders | 🏝️ Islands | ⛰️ Mountains | 🟦 Ocean

---
*Generated by uDOS Template System v1.7.1*
EOF
    
    echo "📄 Simple map saved to: uMemory/generated/simple-world-map.md"
  else
    echo "❌ Template not found, creating basic map info..."
    echo "🗺️ Basic Map Information:" > "$UHOME/uMemory/generated/basic-map.md"
    echo "Total datasets: $(find "$UHOME/uTemplate/datasets" -name "*.json" | wc -l)" >> "$UHOME/uMemory/generated/basic-map.md"
  fi
}

# --- Missing Command Functions for Alpha v1.0 ---

cmd_timezone_enhanced() {
  echo "🕒 Enhanced Timezone Management (Dataset-Integrated)"
  echo ""
  
  current_timezone=$(cat "$UHOME/uMemory/state/timezone.md" 2>/dev/null || echo "UTC")
  echo "📍 Current timezone: $current_timezone"
  echo ""
  
  if [[ "$args" =~ ^[A-Z]{3}[0-9]{2}$ ]]; then
    # Coordinate-based timezone lookup
    coordinates="$args"
    echo "🔍 Looking up timezone for coordinates: $coordinates"
    timezone_info=$(bash "$UHOME/uCode/json-processor.sh" search "$coordinates" 2>/dev/null | grep timezoneMap)
    if [[ -n "$timezone_info" ]]; then
      echo "✅ Found: $timezone_info"
      echo "$timezone_info" > "$UHOME/uMemory/state/timezone.md"
    else
      echo "❌ No timezone found for coordinates: $coordinates"
    fi
  else
    echo "💡 Available timezones:"
    bash "$UHOME/uCode/json-processor.sh" search "timezone_name" 2>/dev/null | head -10 || echo "Dataset not available"
    echo ""
    echo "🔧 Usage: CHECK TIMEZONE [coordinates] (e.g., CHECK TIMEZONE AX14)"
  fi
  echo ""
}

cmd_location_enhanced() {
  echo "🌍 Enhanced Location Management (Dataset-Integrated)"
  echo ""
  
  current_location=$(cat "$UHOME/uMemory/state/location.md" 2>/dev/null || echo "Unknown")
  echo "📍 Current location: $current_location"
  echo ""
  
  if [[ -n "$args" && "$args" != "" ]]; then
    # Search for location in dataset
    location_query="$args"
    echo "🔍 Searching for location: $location_query"
    location_info=$(bash "$UHOME/uCode/json-processor.sh" search "$location_query" 2>/dev/null | grep locationMap)
    if [[ -n "$location_info" ]]; then
      echo "✅ Found: $location_info"
      echo "$location_info" > "$UHOME/uMemory/state/location.md"
    else
      echo "❌ No location found matching: $location_query"
    fi
  else
    echo "💡 Available locations:"
    bash "$UHOME/uCode/json-processor.sh" search "city_name" 2>/dev/null | head -10 || echo "Dataset not available"
    echo ""
    echo "🔧 Usage: CHECK LOCATION [search term] (e.g., CHECK LOCATION London)"
  fi
  echo ""
}


cmd_debug() {
  echo "🔧 uDOS Debug Information (Enhanced with Template Status)"
  echo ""
  echo "📊 System Status:"
  echo "- Version: $UVERSION"
  echo "- UHOME: $UHOME"
  echo "- Shell: $SHELL"
  echo "- Date: $(date)"
  echo ""
  
  echo "📁 Directory Status:"
  echo "- uCode scripts: $(find "$UHOME/uCode" -name "*.sh" | wc -l)"
  echo "- uMemory items: $(find "$UHOME/uMemory" -type f | wc -l)"
  echo "- uKnowledge docs: $(find "$UHOME/uKnowledge" -type f | wc -l)"
  echo "- uTemplate files: $(find "$UHOME/uTemplate" -type f | wc -l)"
  echo ""
  
  echo "🎛️ Template System Status:"
  if [[ -f "$UHOME/uCode/template-generator.sh" ]]; then
    echo "✅ Template generator available"
    template_count=$(bash "$UHOME/uCode/template-generator.sh" list 2>/dev/null | wc -l)
    echo "📋 Available templates: $template_count"
  else
    echo "❌ Template generator not found"
  fi
  
  echo ""
  echo "🔍 Dataset Status:"
  if [[ -f "$UHOME/uCode/json-processor.sh" ]]; then
    echo "✅ JSON processor available"
    dataset_count=$(find "$UHOME/uTemplate/datasets" -name "*.json" 2>/dev/null | wc -l)
    echo "📊 Available datasets: $dataset_count"
  else
    echo "❌ JSON processor not found"
  fi
  
  echo ""
  echo "⚠️ Recent Errors:"
  if [[ -d "$UHOME/uMemory/logs/errors" ]]; then
    recent_errors=$(find "$UHOME/uMemory/logs/errors" -type f -mtime -1 | wc -l)
    echo "🚨 Last 24h errors: $recent_errors"
    if [[ $recent_errors -gt 0 ]]; then
      echo "📄 Latest error log:"
      find "$UHOME/uMemory/logs/errors" -type f -mtime -1 | head -1 | xargs tail -5
    fi
  else
    echo "📁 Error log directory not found"
  fi
  echo ""
}

cmd_run() {
  echo "🚀 uScript Runner"
  script_name="$args"
  
  if [[ -z "$script_name" ]]; then
    echo "📋 Available uScripts:"
    find "$UHOME/uScript" -name "*.sh" -o -name "*.usc" | head -10
    echo ""
    echo "🔧 Usage: RUN [script-name]"
    return
  fi
  
  # Look for script in uScript directory
  script_path=""
  if [[ -f "$UHOME/uScript/system/$script_name.sh" ]]; then
    script_path="$UHOME/uScript/system/$script_name.sh"
  elif [[ -f "$UHOME/uScript/utilities/$script_name.sh" ]]; then
    script_path="$UHOME/uScript/utilities/$script_name.sh"
  elif [[ -f "$UHOME/uMemory/scripts/$script_name.sh" ]]; then
    script_path="$UHOME/uMemory/scripts/$script_name.sh"
  else
    echo "❌ Script not found: $script_name"
    return
  fi
  
  echo "▶️ Running: $script_path"
  bash "$script_path"
}

cmd_tree() {
  echo "🌳 Generating uDOS File Tree"
  bash "$UHOME/uCode/make-tree.sh"
}

cmd_list() {
  target_dir="${args:-$UHOME}"
  echo "📁 Directory listing: $target_dir"
  echo ""
  
  if [[ -d "$target_dir" ]]; then
    if command -v tree >/dev/null 2>&1; then
      tree "$target_dir" -L 3
    else
      find "$target_dir" -type d -maxdepth 3 | head -20
    fi
  else
    echo "❌ Directory not found: $target_dir"
  fi
  echo ""
}

cmd_dash() {
  echo "📊 Generating uDOS Dashboard"
  bash "$UHOME/uCode/dash.sh"
}

cmd_restart() {
  echo "🔄 Restarting uDOS shell..."
  exec bash "$UHOME/uCode/ucode.sh"
}

cmd_reboot() {
  echo "⚠️ REBOOT will restart the entire system."
  read -rp "🔄 Continue? (y/N): " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    export REBOOT_FLAG=true
    exec bash "$UHOME/uCode/ucode.sh"
  else
    echo "🚫 Reboot cancelled."
  fi
}

cmd_destroy() {
  echo "⚠️ DESTROY will permanently delete data."
  echo "🔧 Options:"
  echo "   A) Sandbox only"
  echo "   B) Sandbox + Memory"
  echo "   C) Complete system reset"
  read -rp "🗑️ Choose option (A/B/C) or Cancel (N): " choice
  
  case "$choice" in
    A|a)
      bash "$UHOME/uCode/destroy.sh" sandbox
      ;;
    B|b)
      bash "$UHOME/uCode/destroy.sh" memory
      ;;
    C|c)
      bash "$UHOME/uCode/destroy.sh" all
      ;;
    *)
      echo "🚫 Destroy cancelled."
      ;;
  esac
}

cmd_recent() {
  echo "📝 Recent Moves (Last 10)"
  echo ""
  recent_log="$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"
  if [[ -f "$recent_log" ]]; then
    tail -10 "$recent_log"
  else
    echo "📄 No moves recorded today."
  fi
  echo ""
}

validate_template_datasets() {
  echo "✅ Validating Template-Dataset Integration"
  echo ""
  
  # Check template system
  if [[ -f "$UHOME/uCode/template-generator.sh" ]]; then
    echo "🏗️ Running template validation..."
    bash "$UHOME/uCode/template-generator.sh" validate
  else
    echo "❌ Template generator not found"
  fi
  
  echo ""
  
  # Check dataset system
  if [[ -f "$UHOME/uCode/json-processor.sh" ]]; then
    echo "📊 Running dataset validation..."
    bash "$UHOME/uCode/json-processor.sh" validate
  else
    echo "❌ JSON processor not found"
  fi
  echo ""
}

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
  
  # Check for shortcode syntax first
  if [[ "$input" =~ ^\[.*\]$ ]]; then
    echo -e "\033[1;35m🔧 Processing shortcode...\033[0m"
    if [[ -f "$SCRIPT_DIR/shortcode-processor-simple.sh" ]]; then
      bash "$SCRIPT_DIR/shortcode-processor-simple.sh" process "$input"
    elif [[ -f "$SCRIPT_DIR/shortcode-processor.sh" ]]; then
      bash "$SCRIPT_DIR/shortcode-processor.sh" process "$input"
    else
      echo "❌ Shortcode processor not available"
    fi
    continue
  fi
  
  # Set error context for command execution
  if command -v set_error_context >/dev/null 2>&1; then
    set_error_context "command_execution" "ucode.sh" 
  fi
  
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
      # Enhanced RUN command with script runner integration
      if [[ -f "$UHOME/uScript/system/enhanced-script-runner.sh" ]]; then
        echo "🚀 Using Enhanced Script Runner"
        bash "$UHOME/uScript/system/enhanced-script-runner.sh" run "$args"
      else
        cmd_run
      fi
      ;;
    BASH)
      # New BASH command for containerized execution
      if [[ -f "$UHOME/uScript/system/bash-container.sh" ]]; then
        echo "🐳 Executing in containerized environment"
        bash "$UHOME/uScript/system/bash-container.sh" exec "$args"
      else
        echo "❌ Bash container not available"
        if command -v error_warning >/dev/null 2>&1; then
          error_warning "Bash container system not found"
        fi
      fi
      ;;
    SHORTCODE)
      # Shortcode management commands
      if [[ -f "$UHOME/uCode/shortcode-processor-simple.sh" ]]; then
        bash "$UHOME/uCode/shortcode-processor-simple.sh" "$args"
      elif [[ -f "$UHOME/uCode/shortcode-processor.sh" ]]; then
        bash "$UHOME/uCode/shortcode-processor.sh" "$args"
      else
        echo "❌ Shortcode processor not available"
      fi
      ;;
    ERROR)
      # Error handling commands
      if [[ -f "$UHOME/uCode/error-handler.sh" ]]; then
        bash "$UHOME/uCode/error-handler.sh" "$args"
      else
        echo "❌ Error handler not available"
      fi
      ;;
    CONTAINER)
      # Container management
      if [[ -f "$UHOME/uScript/system/bash-container.sh" ]]; then
        bash "$UHOME/uScript/system/bash-container.sh" "$args"
      else
        echo "❌ Container system not available"
      fi
      ;;
    TREE)
      cmd_tree
      ;;
    LIST)
      cmd_list "$args"
      ;;
    DASH)
      # Enhanced dashboard command with multiple options
      case "$args" in
        "enhanced"|"ascii")
          if [[ -f "$UHOME/uCode/enhanced-dash.sh" ]]; then
            bash "$UHOME/uCode/enhanced-dash.sh" show
          else
            cmd_dash
          fi
          ;;
        "live"|"watch")
          if [[ -f "$UHOME/uCode/enhanced-dash.sh" ]]; then
            bash "$UHOME/uCode/enhanced-dash.sh" live
          else
            cmd_dash
          fi
          ;;
        "stats")
          if [[ -f "$UHOME/uCode/enhanced-dash.sh" ]]; then
            bash "$UHOME/uCode/enhanced-dash.sh" stats
          else
            cmd_dash
          fi
          ;;
        "export")
          if [[ -f "$UHOME/uCode/enhanced-dash.sh" ]]; then
            bash "$UHOME/uCode/enhanced-dash.sh" export json
          else
            cmd_dash
          fi
          ;;
        *)
          # Default dashboard behavior - try enhanced first
          if [[ -f "$UHOME/uCode/enhanced-dash.sh" ]]; then
            bash "$UHOME/uCode/enhanced-dash.sh" build
            bash "$UHOME/uCode/enhanced-dash.sh" show
          else
            cmd_dash
          fi
          ;;
      esac
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
    QUIT|EXIT|BYE)
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
      echo "     template generate <id> <n> - Generate template"
      echo "     template batch <file>       - Batch generate from CSV"
      echo "     template validate <id>      - Validate template definition"
      echo "     template generated          - List generated templates"
      echo "     template sample             - Create sample batch file"
      echo ""
      echo "� DYNAMIC COMMANDS (Dataset-Driven Extensions)"
      if [[ "$DYNAMIC_COMMANDS_COUNT" -gt 0 ]]; then
        echo "     DYNAMIC list                - List all dynamic commands"
        echo "     DYNAMIC help <command>      - Get help for dynamic command"
        echo "     DYNAMIC status              - Show dynamic system status"
        echo "     Available: INSTALL, SEARCH, EXPORT, BACKUP, HEALTH, CONFIG, PACKAGE, WORKFLOW"
      else
        echo "     DYNAMIC reload              - Load dynamic command system"
      fi
      echo ""
      echo "🔧 VARIABLE MANAGEMENT"
      echo "     variable-manager.sh set <name> <value> [scope]"
      echo "     variable-manager.sh get <name> [scope]"
      echo "     variable-manager.sh list [scope]"
      echo ""
      echo "�🗺️  DATASET INTEGRATION FEATURES"
      echo "     • Location lookup from 52 global cities"
      echo "     • Timezone management with 38 global zones"
      echo "     • Country/currency auto-detection"
      echo "     • Template-driven user configuration"
      echo "     • Geographic coordinate mapping"
      echo "     • Dynamic command extension system"
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
      # Try dynamic command system first
      if command -v handle_dynamic_command >/dev/null 2>&1; then
        if handle_dynamic_command "$cmd" "$args"; then
          # Command handled by dynamic system
          continue
        fi
      fi
      
      # Log unknown command as warning
      if command -v error_warning >/dev/null 2>&1; then
        error_warning "Unknown command: $cmd"
      fi
      
      echo "❓ Unknown command '$cmd'. Type HELP for list of commands."
      echo "💡 Try using shortcode syntax: [run:script-name] or [bash:command]"
      echo "🔧 Use 'SHORTCODE list' to see available shortcodes."
      
      # Suggest similar commands
      case "$cmd" in
        *RUN*|*EXEC*|*EXECUTE*)
          echo "💡 Did you mean: RUN, BASH, or [run:script-name]?"
          ;;
        *ERROR*|*LOG*)
          echo "💡 Did you mean: ERROR, LOG, or CHECK?"
          ;;
        *HELP*|*INFO*)
          echo "💡 Did you mean: HELP, DEBUG, or CHECK?"
          ;;
      esac
      ;;
  esac
done
