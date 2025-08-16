# uDOS v1.3 Style Guide & Naming Convention

```
    ██╗   ██╗██████╗  ██████╗ ███████╗    ██╗   ██████╗ 
    ██║   ██║██╔══██╗██╔═══██╗██╔════╝    ██║   ╚════██╗
    ██║   ██║██║  ██║██║   ██║███████╗    ██║    █████╔╝
    ██║   ██║██║  ██║██║   ██║╚════██║    ██║    ╚═══██╗
    ╚██████╔╝██████╔╝╚██████╔╝███████║    ██║   ██████╔╝
     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝    ╚═╝   ╚═════╝ 
                                                           
    Universal Data Operating System v1.3 - Style Guide
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
```

**Version**: 1.3  
**Date**: August 16, 2025  
**Part Number**: uDOS-STY-GDE-001  
**Issue**: 3

---

## 🎯 **CORE PRINCIPLE: CAPS-NUMERIC-DASH ONLY**

uDOS v3.0 enforces strict naming conventions:
- **UPPERCASE A-Z ONLY** for all technical elements
- **NUMERIC 0-9** for identifiers, codes, and sequences
- **HYPHEN/DASH (-)** as the sole separator character
- **NO lowercase, underscores, or special characters**

---

## 📁 **FILENAME CONVENTION v1.3**

### Universal File Format
```
uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md
```

### Component Breakdown
- **uTYPE**: File type prefix (see types below)
- **YYYYMMDD**: ISO date (20250816)
- **HHMM**: Time in 24-hour format (1640)
- **TTZ**: 2-digit timezone code from existing uDOS cityMap dataset (see mapping below)
- **MMLLNN**: Enhanced location code (Map+Location+Number)

### Examples
```
uSCRIPT-20250816-1640-33-00CQ43.md  # Script in Sydney (AEDT timezone)
uLOG-20250816-0930-08-00SY01.md     # Log in New York (EST timezone)
uDATA-20250816-1500-16-05DR15.md    # Data in Berlin (CET timezone)
uDOC-20250816-2100-30-00NY12.md     # Doc in Tokyo (JST timezone)
uMISSION-20250816-0800-33-00ME22.md # Mission in Sydney (AEDT timezone)
uLEGACY-20250816-1200-15-12WZ05.md  # Legacy in London (GMT timezone)
```

---

## 🏷️ **FILE TYPE PREFIXES**

### Core Types
- **uSCRIPT** - Executable scripts and automation
- **uLOG** - System and user activity logs
- **uDATA** - Data files and datasets
- **uDOC** - Documentation and guides
- **uMISSION** - Mission and project files
- **uLEGACY** - Historical and archived content

### Extended Types
- **uCONFIG** - Configuration files
- **uTEMPLATE** - Template definitions
- **uREPORT** - Generated reports
- **uTEST** - Test files and validation
- **uBACKUP** - Backup and recovery files
- **uTMP** - Temporary working files

### Special Files (No timestamp)
- **README.md** - Repository documentation
- **CHANGELOG.md** - Version history
- **LICENSE.md** - Legal documentation

---

## 🌍 **TIMEZONE CODES v1.3**

### 2-Digit Timezone Mapping

Based on existing uDOS cityMap.json dataset with 3-4 letter TZ conversion:

| TTZ | Original TZ Code | UTC Offset | Primary City | Region |
|-----|------------------|------------|--------------|---------|
| 01 | CST | -06:00 | Mexico City, Chicago | North America |
| 02 | EST | -05:00 | New York, Toronto | North America |
| 03 | PET | -05:00 | Lima | South America |
| 04 | ART | -03:00 | Buenos Aires | South America |
| 05 | BRT | -03:00 | São Paulo | South America |
| 06 | CLT | -04:00 | Santiago | South America |
| 07 | WET | ±00:00 | Casablanca | Africa |
| 08 | CET | +01:00 | Madrid, Paris, Barcelona, Berlin | Europe |
| 09 | GMT | ±00:00 | London | Europe |
| 10 | EET | +02:00 | Athens, Cairo | Europe/Africa |
| 11 | TRT | +03:00 | Istanbul | Europe/Asia |
| 12 | MSK | +03:00 | Moscow | Europe/Asia |
| 13 | EAT | +03:00 | Addis Ababa | Africa |
| 14 | AST | +03:00 | Riyadh | Asia |
| 15 | IRST | +03:30 | Tehran | Asia |
| 16 | PKT | +05:00 | Karachi | Asia |
| 17 | IST | +05:30 | Delhi | Asia |
| 18 | BST | +06:00 | Dhaka | Asia |
| 19 | ICT | +07:00 | Bangkok, Hanoi | Asia |
| 20 | MYT | +08:00 | Kuala Lumpur | Asia |
| 21 | WIB | +07:00 | Jakarta | Asia |
| 22 | PHT | +08:00 | Manila | Asia |
| 23 | JST | +09:00 | Tokyo | Asia |
| 24 | KST | +09:00 | Seoul | Asia |
| 25 | CST | +08:00 | Beijing, Shanghai | Asia |
| 26 | HKT | +08:00 | Hong Kong | Asia |
| 27 | SGT | +08:00 | Singapore | Asia |
| 28 | AEDT | +11:00 | Sydney, Melbourne | Oceania |
| 29 | AWST | +08:00 | Perth | Oceania |
| 30 | ACST | +09:30 | Adelaide | Oceania |
| 31 | NZST | +12:00 | Auckland | Oceania |
| 32 | HST | -10:00 | Honolulu | Pacific |
| 33 | AKST | -09:00 | Anchorage | North America |
| 34 | PST | -08:00 | Los Angeles | North America |
| 35 | MST | -07:00 | Denver | North America |
| 36 | CAT | +02:00 | Cairo | Africa |
| 37 | WAT | +01:00 | Lagos | Africa |
| 38 | UTC | ±00:00 | Coordinated Universal | Global |

### Auto-Detection from System

The system automatically detects the 2-digit code from your 3-4 letter timezone:
- **AEDT/AEST** → 28 (Sydney time)
- **EST/EDT** → 02 (New York time)  
- **CET/CEST** → 08 (Central European time)
- **JST** → 23 (Japan time)
- **UTC/GMT** → 38/09 (Universal/London time)

---

## 🗺️ **ENHANCED LOCATION CODES v3.0**

### Format: MMLLNN
- **MM**: Map number (00-99)
- **LL**: Location letters (A-Z, 2 chars)
- **NN**: Tile number (01-99)

### Map Types
- **Map 00**: Planet Earth (System Template)
- **Maps 01-99**: Custom user-created maps

### Examples
```
00SY43  # Map 00, Sydney, Tile 43
00NY12  # Map 00, New York, Tile 12
05DR01  # Map 05, Dragon's Lair, Tile 01
12WZ15  # Map 12, Wizard Tower, Tile 15
```

---

## 📝 **NAMING CONVENTIONS**

### 1. Variables
```bash
# Environment Variables (ALL CAPS with underscores)
UDOS-USERNAME
UDOS-LOCATION-CODE
UDOS-TIMEZONE-CODE
UDOS-MAP-NUMBER

# Script Variables (CAPS-DASH format)
CURRENT-USER
FILE-PATH
TIME-STAMP
LOCATION-CODE
```

### 2. Commands
```bash
# All commands in CAPS
STATUS
MEMORY
PACKAGE
RESTART
DASH-LIVE
CONFIG-SET
```

### 3. Shortcodes
```bash
# Format: [TYPE|ACTION]
[MEM|LIST]
[PACK|INSTALL]
[DASH|LIVE]
[CONFIG|SET]
[MAP|CREATE]
[LOG|VIEW]
```

### 4. Directory Names
```
uCORE/
uMEMORY/
uKNOWLEDGE/
UDOS-EXTENSION/
```

---

## 🎨 **TYPOGRAPHY STANDARDS**

### Capitalization Rules

#### ALL CAPS Usage
- **Commands**: STATUS, HELP, MEMORY, PACKAGE
- **File Types**: uSCRIPT, uLOG, uDATA, uDOC
- **Variables**: UDOS-USERNAME, CURRENT-MODE
- **Shortcodes**: [MEM|LIST], [PACK|INSTALL]
- **Technical Elements**: All system identifiers

#### Sentence Case Usage
- **Documentation text**: "Your memory stores all data"
- **User messages**: "Welcome to the system"
- **Descriptions**: "This command shows status"
- **Interface labels**: "Current status:", "Available options:"

#### Proper Case Usage
- **System Name**: "uDOS"
- **Component Names**: "Memory Vaults", "Command Center"
- **Technology Names**: "Markdown", "ASCII"

### Color Coding Standards
```bash
# Commands (YELLOW)
STATUS, HELP, MEMORY, PACKAGE

# Shortcodes (CYAN brackets, YELLOW content)
[MEM|LIST], [PACK|INSTALL], [DASH|LIVE]

# Variables (GREEN)
UDOS-USERNAME, CURRENT-MODE, UDOS-VERSION

# File paths (BLUE)
/Users/username/uDOS/uMEMORY/

# Success (GREEN)
✅ Operation completed successfully

# Warning (YELLOW)
⚠️ This action requires confirmation

# Error (RED)
❌ Command not found

# Info (CYAN)
ℹ️ Helpful information
```

---

## 🔧 **IMPLEMENTATION TOOLS**

### Filename Generator Function
```bash
generate_udos_filename() {
    local file_type="$1"        # uSCRIPT, uLOG, etc.
    local tz_code="$2"          # 2-digit timezone code
    local location_code="$3"    # MMLLNN format
    
    local date_stamp=$(date +%Y%m%d)
    local time_stamp=$(date +%H%M)
    
    echo "u${file_type}-${date_stamp}-${time_stamp}-${tz_code}-${location_code}.md"
}

# Usage examples
generate_udos_filename "SCRIPT" "33" "00SY43"
# Output: uSCRIPT-20250816-1640-33-00SY43.md

generate_udos_filename "LOG" "16" "00BE12"
# Output: uLOG-20250816-0930-16-00BE12.md
```

### Timezone Code Lookup
```bash
get_timezone_code() {
    local timezone_name="$1"
    
    case "$timezone_name" in
        "AEST"|"Australian Eastern Standard Time") echo "33" ;;
        "UTC"|"Coordinated Universal Time") echo "15" ;;
        "EST"|"Eastern Standard Time") echo "08" ;;
        "CET"|"Central European Time") echo "16" ;;
        "JST"|"Japan Standard Time") echo "30" ;;
        *) echo "15" ;; # Default to UTC
    esac
}
```

### Location Code Validator
```bash
validate_location_code() {
    local code="$1"
    
    # Check format: MMLLNN (6 characters)
    if [[ ! "$code" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
        echo "❌ Invalid location code format. Expected: MMLLNN"
        return 1
    fi
    
    local map_num=${code:0:2}
    local location=${code:2:2}
    local tile_num=${code:4:2}
    
    # Validate map number (00-99)
    if [ "$map_num" -gt 99 ]; then
        echo "❌ Invalid map number: $map_num (max: 99)"
        return 1
    fi
    
    # Validate tile number (01-99)
    if [ "$tile_num" -lt 1 ] || [ "$tile_num" -gt 99 ]; then
        echo "❌ Invalid tile number: $tile_num (range: 01-99)"
        return 1
    fi
    
    echo "✅ Valid location code: $code"
    return 0
}
```

---

## 📋 **VALIDATION CHECKLIST**

### File Naming Compliance
- [ ] File type prefix uses uTYPE format
- [ ] Date format is YYYYMMDD
- [ ] Time format is HHMM (24-hour)
- [ ] Timezone code is 2-digit (00-38)
- [ ] Location code is MMLLNN format
- [ ] File extension is .md
- [ ] No lowercase letters in technical elements
- [ ] No underscores or special characters (except dash)

### Content Standards
- [ ] Commands in ALL CAPS
- [ ] Variables use CAPS-DASH format
- [ ] Shortcodes use [TYPE|ACTION] format
- [ ] Descriptions in sentence case
- [ ] Proper timezone integration
- [ ] Valid location codes
- [ ] ASCII art compliance

### System Integration
- [ ] Timezone codes match uDOS dataset
- [ ] Location codes reference valid maps
- [ ] File validation passes all checks
- [ ] Template system compatibility
- [ ] Backup system integration

---

## 🚀 **MIGRATION FROM v2.0 TO v3.0**

### Automated Migration Script
```bash
#!/bin/bash
# migrate-to-v3.sh - Convert files to v3.0 naming convention

migrate_file() {
    local old_file="$1"
    local file_type=$(determine_file_type "$old_file")
    local timezone_code=$(get_current_timezone_code)
    local location_code=$(get_current_location_code)
    
    local new_file=$(generate_udos_filename "$file_type" "$timezone_code" "$location_code")
    
    echo "📄 Migrating: $old_file → $new_file"
    mv "$old_file" "$new_file"
}

# Process all eligible files
find . -name "*.md" -not -name "README.md" -not -name "CHANGELOG.md" | while read file; do
    migrate_file "$file"
done
```

### Breaking Changes
1. **Filename Format**: All files must use new uTYPE-DATE-TIME-TZ-LOCATION format
2. **Timezone Integration**: TZ codes now required and linked to dataset
3. **Location Codes**: Enhanced MMLLNN format replaces old system
4. **Validation**: Stricter compliance checking for all elements

---

## 📚 **DOCUMENTATION STANDARDS v3.0**

### Header Template
```markdown
# Document Title

**Type**: uDOC-20250816-1640-33-00SY43  
**Version**: 3.0  
**Author**: wizard  
**Location**: [00SY43] Sydney, Australia  
**Timezone**: AEST (+10:30)  

---
```

### Cross-References
```markdown
See [uDOC-20250816-1500-33-00SY43.md](./uDOC-20250816-1500-33-00SY43.md) for details.
Refer to uMEMORY for archived [uLOG-20250815-*-33-*.md] files.
```

---

## ⚡ **QUICK REFERENCE**

### Common Patterns
```bash
# Script file
uSCRIPT-20250816-1640-33-00SY43.md

# Log file
uLOG-20250816-0930-16-00BE12.md

# Data file
uDATA-20250816-1500-05-05DR15.md

# Documentation
uDOC-20250816-2100-33-00SY43.md

# Mission file
uMISSION-20250816-0800-15-00LO05.md
```

### Command Examples
```bash
# Generate new script file
./uCORE/scripts/create-file.sh uSCRIPT "Build automation"

# List files by type
./uCORE/scripts/list-files.sh uLOG

# Validate naming convention
./uCORE/scripts/validate-naming.sh "uSCRIPT-20250816-1640-33-00SY43.md"
```

---

**STATUS**: ACTIVE v3.0  
**ENFORCEMENT**: All new files must comply with v3.0 standards  
**MIGRATION**: Legacy files will be gradually migrated  
**SUPPORT**: Contact wizard for implementation assistance

---

*uDOS v3.0 Style Guide - Universal Data Operating System*  
*Precision Through Standardization*
