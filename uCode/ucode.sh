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

cmd_setup_user() {
  echo "👤 Template-Driven User Setup"
  echo ""
  
  if [[ -f "$UHOME/uTemplate/input-user-setup.md" ]]; then
    echo "📋 Using enhanced template-driven setup..."
    bash "$UHOME/uCode/template-generator.sh" generate user-setup "User Identity"
    
    if [[ -f "$UHOME/uMemory/generated/user-setup.md" ]]; then
      echo "✅ User setup template generated"
      echo "📝 Please edit: uMemory/generated/user-setup.md"
      echo "🔄 Then run: VALIDATE to apply settings"
    fi
  else
    echo "📋 Using basic setup..."
    bash "$UHOME/uCode/check.sh" all
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
