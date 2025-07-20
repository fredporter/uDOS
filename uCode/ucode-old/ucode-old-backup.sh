#!/bin/bash
# uCode.sh - uDOS Beta v1.7.1 CLI Shell
# Full-featured command-line interface for uDOS environment

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UHOME="${HOME}/uDOS"
export UDENT="$UHOME/sandbox/identity.md"
export UDOS_DASHBOARD="${UHOME}/uDev/dashboard.json"
export UDOS_MOVES_DIR="${UHOME}/uMemory"
mkdir -p "$UHOME"

# Load Display Configuration System
DISPLAY_VARS="${UHOME}/uMemory/display-vars.sh"
if [[ -f "$DISPLAY_VARS" ]]; then
    source "$DISPLAY_VARS"
    echo "🖥️  Display configuration loaded ($UDOS_DISPLAY_MODE mode)"
else
    echo "🖥️  Initializing template-based display configuration..."
    if [[ -f "$SCRIPT_DIR/display-template-processor.sh" ]]; then
        "$SCRIPT_DIR/display-template-processor.sh" process
        source "$DISPLAY_VARS" 2>/dev/null || echo "⚠️  Display configuration partial"
    else
        echo "⚠️  Display template processor not found - using defaults"
        export UDOS_DISPLAY_MODE="auto"
        export UDOS_TERMINAL_COLS="${COLUMNS:-80}"
        export UDOS_TERMINAL_ROWS="${LINES:-24}"
    fi

# User Setup Check - Core uDOS ethos: One installation per user
if [[ ! -f "$UDENT" ]]; then
    echo "🔐 First-time setup detected - initializing user..."
    if [[ -f "$SCRIPT_DIR/core.sh" ]]; then
        "$SCRIPT_DIR/core.sh" init
    elif [[ -f "$SCRIPT_DIR/init-user.sh" ]]; then
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

# Load VB command interpreter
if [[ -f "$SCRIPT_DIR/vb-command-interpreter.sh" ]]; then
  source "$SCRIPT_DIR/vb-command-interpreter.sh"
  echo "🔷 VB command interpreter loaded"
  VB_INTERPRETER_AVAILABLE=true
else
  echo "⚠️ VB command interpreter not found"
  VB_INTERPRETER_AVAILABLE=false
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
if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
  echo "🔧 Unified processing system available"
elif [[ -f "$SCRIPT_DIR/shortcode-processor-simple.sh" ]]; then
  echo "🔧 Simple shortcode system available"
elif [[ -f "$SCRIPT_DIR/shortcode-processor.sh" ]]; then
  echo "🔧 Advanced shortcode system available (may need compatibility updates)"
else
  echo "⚠️ Shortcode processor not found - [shortcode] syntax unavailable"
fi

# --- Ensure required folders exist following new architecture ---
# uMemory = All user content storage
mkdir -p "$UHOME/uMemory"
mkdir -p "$UHOME/uMemory/milestones" 
mkdir -p "$UHOME/uMemory/legacy"
mkdir -p "$UHOME/sandbox"
mkdir -p "$UHOME/uMemory"
mkdir -p "$UHOME/uMemory/scripts"
mkdir -p "$UHOME/uMemory/templates"
mkdir -p "$UHOME/uMemory/sandbox"

# uKnowledge = Central shared knowledge bank (system docs)
mkdir -p "$UHOME/uKnowledge/companion"
mkdir -p "$UHOME/uKnowledge/general-library"
mkdir -p "$UHOME/uKnowledge/maps"

# docs = Centralized documentation (roadmaps migrated here)
mkdir -p "$UHOME/docs/roadmap"

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

# Package management moved to shortcode commands
# Use [PACKAGE:install-all] or [PKG:install-all] to install packages
# See available commands: [PACKAGE:help] or [PKG:help]

# Track if session end has been logged
export UCODE_SESSION_ENDED=false

# --- uDOS Version Detection ---
IDENTITY_FILE="$UHOME/sandbox/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
  UVERSION=$(grep "Version:" "$IDENTITY_FILE" | cut -d':' -f2 | xargs)
else
  UVERSION="v1.2"
fi

log_move() {
  local cmd="$1"
  local trimmed="${cmd// }"
  if [[ "$UCODE_BOOTING" == "true" || -z "$trimmed" || "$cmd" == "exit" || "$cmd" == "bye" ]]; then
    return
  fi
  bash "$UHOME/uCode/log.sh" move "$cmd"
}

# --- User Setup Function with Template Integration v2.0 ---
cmd_setup_user() {
  echo "👤 uDOS Template-Based User Setup v2.0"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔧 Using unified uTemplate system with [shortcodes] and \$Variables"
  echo ""
  
  # Run the template-based setup
  local setup_processor="$UHOME/uCode/setup-template-processor.sh"
  if bash "$setup_processor"; then
    echo ""
    echo "🎉 Standard setup completed successfully!"
    echo ""
    
    # Load and display the generated configuration
    local config_file="$UHOME/uMemory/setup-vars.sh"
    if [[ -f "$config_file" ]]; then
      echo "📋 Configuration Summary:"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      
      # Show key configuration values
      source "$config_file"
      echo "👤 Username: ${UDOS_USERNAME:-'Not set'}"
      echo "🎯 Role: ${UDOS_DEFAULT_ROLE:-'Not set'}"
      echo "🌍 Location: ${UDOS_CITY_NAME:-'Not set'}"
      echo "⏰ Timezone: ${UDOS_TIMEZONE:-'Not set'}"
      echo "🎨 Theme: ${UDOS_THEME:-'Not set'}"
      echo "🤖 OK Companion: ${UDOS_OK_COMPANION:-'Not set'}"
      echo ""
      
      echo "📁 Generated Files:"
      echo "   📄 Identity: sandbox/identity.md"
      echo "   ⚙️  Config: uMemory/setup-vars.sh"
      echo "   🎯 Mission: uMemory/001-welcome-mission.md"
      echo ""
      
      echo "🚀 Next Steps:"
      echo "   1. Run: ucode CHECK all"
      echo "   2. Try: ucode DASH live"
      echo "   3. Read: docs/user-manual.md"
    else
      echo "⚠️  Configuration file not generated - setup may be incomplete"
    fi
  else
    echo "❌ Setup failed - please check the setup processor and try again"
    exit 1
  fi
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

# Initialize VB command interpreter
if [[ "$VB_INTERPRETER_AVAILABLE" == "true" ]]; then
  vb_init
fi

USER_FILE="$UHOME/sandbox/identity.md"
if [[ ! -f "$USER_FILE" ]]; then
    echo "⚙️ No identity file found. Starting standard setup..."
    echo "🏗️ Using integrated uTemplate system for user configuration..."
    echo ""
    
    cmd_setup_user
    
    # Verify setup completed
    if [[ -f "$USER_FILE" ]]; then
        echo "✅ Identity setup completed successfully."
        echo ""
    else
        echo "❌ Setup failed - identity file not created"
        exit 1
    fi
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
echo "- Missions: $(find "$UHOME/uMemory" -name "*-mission.md" -type f | wc -l)"
echo "- Milestones: $(find "$UHOME/uMemory/milestones" -type f | wc -l)"
echo "- Legacy items: $(find "$UHOME/uMemory/legacy" -type f | wc -l)"
echo "- Total logs: $(find "$UHOME/uMemory" -name "*-log-*.md" -type f | wc -l)"
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
      bash "$UHOME/uCode/core.sh" all
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
      echo "   TIMEZONE  → timezone management"
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

# --- Display Configuration Command ---
cmd_display_config() {
  local subcmd="${1:-summary}"
  
  case "$subcmd" in
    INIT|SETUP|CONFIGURE)
      echo "🖥️  Initializing template-based display configuration..."
      if [[ -f "$SCRIPT_DIR/display-template-processor.sh" ]]; then
        bash "$SCRIPT_DIR/display-template-processor.sh" process
        # Reload variables
        source "${UHOME}/uMemory/config/display-vars.sh" 2>/dev/null || true
        echo "✅ Standard display configuration completed"
      else
        echo "⚠️  Template processor not found - using legacy system"
        if [[ -f "$SCRIPT_DIR/display-config.sh" ]]; then
          bash "$SCRIPT_DIR/display-config.sh" init
          source "${UHOME}/uMemory/config/display-vars.sh" 2>/dev/null || true
          echo "✅ Legacy display configuration completed"
        else
          echo "❌ No display configuration system available"
        fi
      fi
      ;;
    DETECT|SIZE)
      echo "🔍 Current terminal size:"
      if [[ -n "${UDOS_TERMINAL_COLS:-}" ]] && [[ -n "${UDOS_TERMINAL_ROWS:-}" ]]; then
        echo "Configured: ${UDOS_TERMINAL_COLS} × ${UDOS_TERMINAL_ROWS} (${UDOS_DETECTION_METHOD:-unknown})"
      fi
      
      # Also show current detection
      local current_cols current_rows
      if command -v tput >/dev/null 2>&1; then
        current_cols=$(tput cols 2>/dev/null || echo "${COLUMNS:-unknown}")
        current_rows=$(tput lines 2>/dev/null || echo "${LINES:-unknown}")
        echo "Current: ${current_cols} × ${current_rows} (tput)"
      else
        echo "Current: ${COLUMNS:-unknown} × ${LINES:-unknown} (environment)"
      fi
      ;;
    MODE)
      echo "🎯 Display mode information:"
      if [[ -n "${UDOS_DISPLAY_MODE:-}" ]]; then
        echo "Display Mode: $UDOS_DISPLAY_MODE"
        echo "Viewport: ${UDOS_VIEWPORT_COLS:-80} × ${UDOS_VIEWPORT_ROWS:-24}"
        echo "Dashboard: ${UDOS_DASH_COLS:-80} × ${UDOS_DASH_ROWS:-15} (${UDOS_DASH_POSITION:-bottom})"
        echo "Grid System: ${UDOS_GRID_MODE:-standard} (${UDOS_GRID_COLS_MAX:-26}×${UDOS_GRID_ROWS_MAX:-99})"
        echo "Block Style: ${UDOS_BORDER_STYLE:-single} (${UDOS_BLOCK_WIDTH:-40}×${UDOS_BLOCK_HEIGHT:-6})"
      else
        echo "❌ Display configuration not loaded"
        echo "💡 Run: DISPLAY INIT"
      fi
      ;;
    TEST)
      echo "🧪 Testing ASCII interface elements..."
      if [[ -f "$SCRIPT_DIR/display-template-processor.sh" ]]; then
        bash "$SCRIPT_DIR/display-template-processor.sh" test
      elif [[ -f "$SCRIPT_DIR/display-config.sh" ]]; then
        bash "$SCRIPT_DIR/display-config.sh" test
      else
        echo "❌ No display testing system available"
      fi
      ;;
    SUMMARY|SHOW|"")
      echo "📊 Display Configuration Summary:"
      if [[ -f "$SCRIPT_DIR/display-template-processor.sh" ]]; then
        bash "$SCRIPT_DIR/display-template-processor.sh" summary
      elif [[ -f "$SCRIPT_DIR/display-config.sh" ]]; then
        bash "$SCRIPT_DIR/display-config.sh" summary
      else
        echo "❌ No display configuration system available"
        echo "💡 Run: DISPLAY INIT to set up display configuration"
      fi
      ;;
    TEMPLATE)
      echo "🔧 Display template system information:"
      local template_file="${UHOME}/uTemplate/display-config-template.md"
      if [[ -f "$template_file" ]]; then
        echo "✅ Template available: $template_file"
        echo "� Template size: $(wc -l < "$template_file") lines"
        if [[ -f "${UHOME}/uMemory/config/display-vars.sh" ]]; then
          echo "✅ Configuration generated: $(stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' "${UHOME}/uMemory/config/display-vars.sh" 2>/dev/null || echo 'unknown')"
        else
          echo "❌ Configuration not generated"
        fi
      else
        echo "❌ Template not found: $template_file"
      fi
      ;;
    VARS|VARIABLES)
      echo "📝 Display configuration variables:"
      if [[ -f "$SCRIPT_DIR/display-template-processor.sh" ]]; then
        bash "$SCRIPT_DIR/display-template-processor.sh" vars
      else
        echo "❌ Template processor not available"
      fi
      ;;
    HELP)
      echo "🖥️  uDOS Display Configuration Commands:"
      echo ""
      echo "DISPLAY INIT       - Initialize template-based display configuration"
      echo "DISPLAY DETECT     - Detect current terminal size"
      echo "DISPLAY MODE       - Show display mode information"
      echo "DISPLAY TEST       - Test ASCII interface elements"
      echo "DISPLAY SUMMARY    - Show configuration summary"
      echo "DISPLAY TEMPLATE   - Show template system status"
      echo "DISPLAY VARS       - Show generated variables"
      echo "DISPLAY HELP       - Show this help"
      echo ""
      echo "� Template System v2.0:"
      echo "  • Uses [SHORTCODE] and \$VARIABLE format (ALL CAPITALS)"
      echo "  • Processes display-config-template.md"
      echo "  • Generates executable configuration files"
      echo "  • Automatically adapts to terminal size"
      echo ""
      echo "📱 Supported display modes:"
      echo "  • micro (80×45)   • mini (80×60)     • compact (160×90)"
      echo "  • console (160×120) • wide (320×180)  • full (320×240)"
      echo "  • mega (640×360)   • ultra (640×480)"
      ;;
    *)
      echo "❓ Unknown display command: $subcmd"
      echo "💡 Try: DISPLAY HELP"
      ;;
  esac
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
  current_location=$(cat "$UHOME/sandbox/location.md" 2>/dev/null || echo "Unknown")
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

# --- Map Fallback (Standard) ---
# --- Map Fallback (Standard) ---
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
**Version:** Standard v1.7.1

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
  echo "🕒 Timezone Management (Dataset-Integrated)"
  echo ""
  
  current_timezone=$(cat "$UHOME/sandbox/timezone.md" 2>/dev/null || echo "UTC")
  echo "📍 Current timezone: $current_timezone"
  echo ""
  
  if [[ "$args" =~ ^[A-Z]{3}[0-9]{2}$ ]]; then
    # Coordinate-based timezone lookup
    coordinates="$args"
    echo "🔍 Looking up timezone for coordinates: $coordinates"
    timezone_info=$(bash "$UHOME/uCode/json-processor.sh" search "$coordinates" 2>/dev/null | grep timezoneMap)
    if [[ -n "$timezone_info" ]]; then
      echo "✅ Found: $timezone_info"
      echo "$timezone_info" > "$UHOME/sandbox/timezone.md"
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
  echo "🌍 Location Management (Dataset-Integrated)"
  echo ""
  
  current_location=$(cat "$UHOME/sandbox/location.md" 2>/dev/null || echo "Unknown")
  echo "📍 Current location: $current_location"
  echo ""
  
  if [[ -n "$args" && "$args" != "" ]]; then
    # Search for location in dataset
    location_query="$args"
    echo "🔍 Searching for location: $location_query"
    location_info=$(bash "$UHOME/uCode/json-processor.sh" search "$location_query" 2>/dev/null | grep locationMap)
    if [[ -n "$location_info" ]]; then
      echo "✅ Found: $location_info"
      echo "$location_info" > "$UHOME/sandbox/location.md"
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
  echo "🔧 uDOS Debug Information (with Template Status)"
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
  echo "🌳 Generating uDOS v1.1.0 Project Tree"
  echo "📋 Using consolidated tree generator"
  bash "$UHOME/uCode/tree-generator.sh" simple
}

cmd_list() {
  # LIST command with role-based access control
  local list_type="${args:-default}"
  
  if [[ -f "$UHOME/uCode/enhanced-list-command.sh" ]]; then
    bash "$UHOME/uCode/enhanced-list-command.sh" "$list_type"
  else
    # Fallback to original listing
    target_dir="${args:-$UHOME}"
    echo "📁 Directory listing: $target_dir"
    echo ""
    
    if [[ -d "$target_dir" ]]; then
      if command -v tree >/dev/null 2>&1; then
        # Alpha v1.0: Filter out system folders and build artifacts
        tree "$target_dir" -L 3 -I 'node_modules|.git|.DS_Store|*.log|dist|build|out|uMemory|progress'
      else
        find "$target_dir" -type d -maxdepth 3 | grep -v -E '\.(git|DS_Store)|node_modules|dist|build|out|uMemory|progress' | head -20
      fi
    else
      echo "❌ Directory not found: $target_dir"
    fi
    echo ""
  fi
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
  # Call destroy.sh directly without duplicate prompts
  bash "$UHOME/uCode/destroy.sh"
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
trap 'if [ "$UCODE_SESSION_ENDED" = false ]; then echo "🌀 SESSION END → $(date "+%Y-%m-%d %H:%M:%S")" >> "$UHOME/uMemory/move-log-$(date +%Y-%m-%d).md"; export UCODE_SESSION_ENDED=true; fi' EXIT
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
    echo -e "\033[1;35m🔧 Processing SHORTCODE...\033[0m"
    if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
      bash "$SCRIPT_DIR/processor.sh" process "$input"
    elif [[ -f "$SCRIPT_DIR/shortcode-processor-simple.sh" ]]; then
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
      # RUN command with script runner integration
      if [[ -f "$UHOME/uScript/system/enhanced-script-runner.sh" ]]; then
        echo "🚀 Using Script Runner"
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
      if [[ -f "$UHOME/uCode/processor.sh" ]]; then
        bash "$UHOME/uCode/processor.sh" "$args"
      elif [[ -f "$UHOME/uCode/shortcode-processor-simple.sh" ]]; then
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
    # === VB COMMAND LANGUAGE INTEGRATION ===
    VB|VB.*)
      if [[ "$VB_INTERPRETER_AVAILABLE" == "true" ]]; then
        vb_command "$cmd" "$args"
      else
        echo "❌ VB command interpreter not available"
        echo "💡 The VB interpreter provides Visual Basic-style commands"
        echo "   Try: DIM, SET, PRINT, FOR, IF, SUB, CALL, etc."
      fi
      ;;
    DIM|SET|PRINT|INPUT|IF|FOR|NEXT|SUB|CALL|REM|END)
      # Direct VB commands (classic VB syntax)
      if [[ "$VB_INTERPRETER_AVAILABLE" == "true" ]]; then
        vb_execute_line "$input"
      else
        echo "❌ VB command interpreter not available"
        echo "💡 These are Visual Basic-style commands"
        echo "   Install VB interpreter: vb-command-interpreter.sh"
      fi
      ;;
    TREE)
      cmd_tree
      ;;
    LIST)
      cmd_list "$args"
      ;;
    DASH)
      # dashboard command with multiple options
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
          # Default dashboard behavior - try first
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
    DISPLAY)
      cmd_display_config "$args"
      ;;
    VALIDATE)
      validate_template_datasets
      ;;
    DEBUG)
      cmd_debug
      ;;
    # === VB PROGRAM MANAGEMENT ===
    VBRUN|VB.RUN)
      if [[ -f "$SCRIPT_DIR/vb-program-runner.sh" ]]; then
        bash "$SCRIPT_DIR/vb-program-runner.sh" run "$args"
      else
        echo "❌ VB program runner not available"
      fi
      ;;
    VBLIST|VB.LIST)
      if [[ -f "$SCRIPT_DIR/vb-program-runner.sh" ]]; then
        bash "$SCRIPT_DIR/vb-program-runner.sh" list
      else
        echo "❌ VB program runner not available"
      fi
      ;;
    VBCREATE|VB.CREATE)
      if [[ -f "$SCRIPT_DIR/vb-program-runner.sh" ]]; then
        bash "$SCRIPT_DIR/vb-program-runner.sh" create "$args"
      else
        echo "❌ VB program runner not available"
      fi
      ;;
    VBHELP|VB.HELP)
      if [[ "$VB_INTERPRETER_AVAILABLE" == "true" ]]; then
        if [[ -n "$args" ]]; then
          vb_help "$args"
        else
          vb_help
        fi
      else
        echo "❌ VB command interpreter not available"
      fi
      ;;
    # === CONSOLIDATED MANAGEMENT COMMANDS ===
    # === ROLE MANAGEMENT SYSTEM ===
    ROLE|ROLES)
      # User role management system
      echo "👤 User Role Management"
      if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        if [[ -n "$args" ]]; then
          bash "$UHOME/uCode/user-role-manager.sh" $args
        else
          bash "$UHOME/uCode/user-role-manager.sh" status
        fi
      else
        echo "❌ Role management system not available"
      fi
      ;;
    DEVMODE|DEV-MODE)
      # Toggle dev mode (wizard only)
      echo "🔧 Developer Mode Management"
      if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" dev-mode "$args"
      else
        echo "❌ Role management system not available"
      fi
      ;;
    WHOAMI|WHO)
      # Show current user and role information
      if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" status
      else
        echo "👤 User: ${USER:-unknown}"
        echo "🏠 Home: $UHOME"
        if [[ -f "$UDENT" ]]; then
          echo "📋 Identity file exists"
        else
          echo "⚠️ Identity file missing"
        fi
      fi
      ;;
    PERMISSIONS|PERMS)
      # Show folder access permissions
      echo "🔐 Folder Access Permissions"
      if [[ -f "$UHOME/uCode/user-role-manager.sh" ]]; then
        bash "$UHOME/uCode/user-role-manager.sh" folders
      else
        echo "❌ Role management system not available"
      fi
      ;;
    MANAGE|UNIFIED)
      # Access unified management system
      echo "🛠️ uDOS Unified Management System"
      if [[ -n "$args" ]]; then
        bash "$UHOME/uCode/unified-manager.sh" $args
      else
        bash "$UHOME/uCode/unified-manager.sh" help
      fi
      ;;
    PACKAGE|PKG)
      # Package management through unified system
      echo "📦 Package Management"
      if [[ -n "$args" ]]; then
        bash "$UHOME/uCode/unified-manager.sh" package $args
      else
        bash "$UHOME/uCode/unified-manager.sh" package help
      fi
      ;;
    TEMPLATE|TPL)
      # Template processing through unified system
      echo "🔧 Template Processing"
      if [[ -n "$args" ]]; then
        bash "$UHOME/uCode/unified-manager.sh" template $args
      else
        bash "$UHOME/uCode/unified-manager.sh" template help
      fi
      ;;
    TREEGEN)
      # Advanced tree generation with options
      echo "🌳 Advanced Tree Generator"
      if [[ -n "$args" ]]; then
        bash "$UHOME/uCode/tree-generator.sh" $args
      else
        bash "$UHOME/uCode/tree-generator.sh" help
      fi
      ;;
    HELP)
      # HELP with dataset integration
      BOLD='\033[1m'
      NC='\033[0m'
      GREEN='\033[0;32m'
      
      if [[ -n "$args" ]]; then
        # Show help for specific command using system
        if [[ -f "$UHOME/uCode/enhanced-help-system.sh" ]]; then
          bash "$UHOME/uCode/enhanced-help-system.sh" command "$args"
        else
          echo "Command help for: $(echo "$args" | tr '[:lower:]' '[:upper:]')"
          # Fallback to basic help
        fi
      else
        # Show general help with dataset integration notice
        echo "🧩 uDOS Version: $UVERSION (Alpha v1.0 - Production Ready)"
        echo ""
        echo -e "🔧 ${BOLD}Help System Available!${NC}"
        echo -e "💡 Try: ${GREEN}HELP <command>${NC} for detailed command information"
        echo -e "🎮 Try: ${GREEN}./uCode/enhanced-help-system.sh interactive${NC} for interactive help"
        echo -e "📚 Try: ${GREEN}./uCode/enhanced-help-system.sh generate${NC} to create comprehensive docs"
        echo ""
        echo "🧠 Available uDOS commands:"
        echo "   LOG       → Log mission/milestone/legacy"
        echo "   RUN       → Run a uScript"
        echo "   TREE      → Generate file tree"
        echo "   LIST      → Role-based folder structure display"
        echo "   DASH      → Show dashboard"
        echo "   SYNC      → Sync dashboard"
        echo "   RESTART   → Restart shell"
        echo "   REBOOT    → Reboot system"
        echo "   DESTROY   → Delete your identity and/or files"
        echo "   IDENTITY  → Display user identity file"
        echo "   DEVCON    → Check and run setup-dev.sh"
        echo "   QUIT      → Close session"
      echo "   RECENT    → Show last 10 moves"
      echo "   CHECK     → commands with dataset integration"
      echo "   SETUP     → Template-driven user setup"
      echo "   SHOW      → View documentation with glow (SHOW manual, SHOW list)"
      echo "   DISPLAY   → Terminal display configuration and ASCII interface"
      echo "   VALIDATE  → Validate template-dataset integration"
      echo ""
      echo "👤 USER ROLE MANAGEMENT"
      echo "   ROLE      → Show current user role and permissions"
      echo "   ROLES     → List all available roles"
      echo "   WHOAMI    → Show current user information"
      echo "   PERMISSIONS → Show folder access permissions"
      echo "   DEVMODE   → Toggle dev mode (Wizard only)"
      echo "   DEBUG     → debug with template status"
      echo ""
      echo "🆕 ALPHA v1.0 NEW FEATURES"
      echo "   PACKAGE   → Package management (unified system)"
      echo "   TEMPLATE  → Template processing (setup/vscode/vb)"
      echo "   MANAGE    → Unified management interface"
      echo "   TREEGEN   → Advanced tree generator (simple/dynamic/stats)"
      echo "   SANDBOX   → Daily session management (start/finalize/clean)"
      echo "   DEVELOPER → Developer mode (enable/disable/status/backup)"
      echo "   EDIT      → Edit files with integrated text editor"
      echo "   CREATE    → Create new files in sandbox"
      echo "   VIEW      → View files with syntax highlighting"
      echo "   SEARCH    → Fast text search with ripgrep"
      echo "   TRASH     → Manage deleted files (move, list, restore, empty)"
      echo "   DELETE    → Move files to trash (safe deletion)"
      echo "   KILL TRASH  → Permanently delete all trash contents"
      echo ""
      echo "🖥️  DISPLAY CONFIGURATION"
      echo "     display init               - Initialize display configuration"
      echo "     display detect             - Detect current terminal size"
      echo "     display mode               - Show display mode information"
      echo "     display test               - Test ASCII interface elements"
      echo "     display summary            - Show configuration summary"
      echo ""
      echo "🔍 ENHANCED CHECK COMMANDS"
      echo "     check user                  - Template-driven user setup"
      echo "     check location              - Location with dataset lookup"
      echo "     check timezone              - Timezone with dataset integration"
      echo "     check datasets              - Show dataset statistics"
      echo "     check templates             - List available templates"
      echo ""
      echo "📦 PACKAGE SYSTEM"
      echo "     package install <name>      - Install specific package"
      echo "     package install-all         - Install all auto-packages"
      echo "     package list               - List available packages"
      echo "     package info <name>        - Show package information"
      echo "     package validate           - Check installation status"
      echo ""
      echo "🏖️ SANDBOX SYSTEM"
      echo "     sandbox start              - Start new daily session"
      echo "     sandbox finalize           - Finalize current session"
      echo "     sandbox clean              - Clean temporary files"
      echo "     sandbox status             - Show current session status"
      echo "     sandbox list               - List sandbox contents"
      echo ""
      echo "🔧 DEVELOPER MODE"
      echo "     developer enable           - Enable developer mode"
      echo "     developer disable          - Disable developer mode"
      echo "     developer status           - Show current mode status"
      echo "     developer backup           - Create script backups"
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
      fi  # Close the if-else block for HELP command
      ;;
    # === ALPHA v1.0 NEW COMMANDS ===
    PACKAGE)
      # Package management system
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/package-manager.sh" $shift_args
      ;;
    SANDBOX)
      # Sandbox session management
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/sandbox-manager.sh" $shift_args
      ;;
    DEVELOPER)
      # Developer mode management
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/developer-mode.sh" $shift_args
      ;;
    EDIT)
      # Integrated text editor command
      if [[ -n "$args" ]]; then
        if command -v micro >/dev/null 2>&1; then
          micro "$args"
        elif command -v nano >/dev/null 2>&1; then
          nano "$args"
        else
          echo "❌ No text editor available. Install packages first."
          echo "💡 Run: PACKAGE INSTALL-ALL"
        fi
      else
        echo "Usage: EDIT <filename>"
      fi
      ;;
    CREATE)
      # Create new files in sandbox
      if [[ -n "$args" ]]; then
        local filename="$args"
        # Default to markdown if no extension
        if [[ "$filename" != *.* ]]; then
          filename="${filename}.md"
        fi
        
        # Create in sandbox/today if it exists, otherwise current directory
        if [[ -d "${UDOS_ROOT}/sandbox/today" ]]; then
          local target_file="${UDOS_ROOT}/sandbox/today/$filename"
        else
          local target_file="$filename"
        fi
        
        # Create basic template
        echo "# $(basename "$filename" .md)" > "$target_file"
        echo "" >> "$target_file"
        echo "Created: $(date)" >> "$target_file"
        echo "" >> "$target_file"
        
        echo "✅ Created: $target_file"
        echo "💡 Use EDIT $filename to open"
      else
        echo "Usage: CREATE <filename>"
      fi
      ;;
    VIEW)
      # View files with syntax highlighting
      if [[ -n "$args" ]]; then
        if command -v bat >/dev/null 2>&1; then
          bat "$args"
        elif command -v glow >/dev/null 2>&1 && [[ "$args" =~ \.md$ ]]; then
          glow "$args"
        else
          cat "$args"
        fi
      else
        echo "Usage: VIEW <filename>"
      fi
      ;;
    SEARCH)
      # Fast text search
      if [[ -n "$args" ]]; then
        if command -v rg >/dev/null 2>&1; then
          rg "$args" "${UDOS_ROOT}"
        else
          echo "❌ ripgrep not available. Install packages first."
          echo "💡 Run: PACKAGE INSTALL-ALL"
        fi
      else
        echo "Usage: SEARCH <pattern>"
      fi
      ;;
    SHOW)
      # Documentation viewer with glow
      shift_args=$(echo "$args" | cut -d' ' -f1-)
      bash "$SCRIPT_DIR/show-docs.sh" $shift_args
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
    TRASH)
      # uDOS Trash Management System
      if [[ -f "$SCRIPT_DIR/trash.sh" ]]; then
        shift_args=$(echo "$args" | cut -d' ' -f1-)
        bash "$SCRIPT_DIR/trash.sh" $shift_args
      else
        echo "❌ Trash management system not available"
      fi
      ;;
    "KILL TRASH")
      # Quick access to empty trash functionality
      if [[ -f "$SCRIPT_DIR/trash.sh" ]]; then
        bash "$SCRIPT_DIR/trash.sh" empty
      else
        echo "❌ Trash management system not available"
      fi
      ;;
    DELETE)
      # Move files to trash instead of permanent deletion
      if [[ -n "$args" ]]; then
        if [[ -f "$SCRIPT_DIR/trash.sh" ]]; then
          bash "$SCRIPT_DIR/trash.sh" move $args
        else
          echo "❌ Trash management system not available"
          echo "💡 Using rm command would permanently delete files"
          echo "   This is disabled for safety - install trash system"
        fi
      else
        echo "❌ Please specify files to delete"
        echo "💡 Usage: DELETE <file1> [file2] [file3]..."
      fi
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
      echo "🔧 Use 'SHORTCODE list' to see available SHORTCODES."
      
      # Suggest similar commands
      case "$cmd" in
        *RUN*|*EXEC*|*EXECUTE*)
          echo "💡 Did you mean: RUN, BASH, or [RUN:script-name]?"
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
