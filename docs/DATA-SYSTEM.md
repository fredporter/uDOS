# uDATA System Configuration

```
██████   █████  ████████  █████
██   ██ ██   ██    ██    ██   ██
██   ██ ███████    ██    ███████
██   ██ ██   ██    ██    ██   ██
██████  ██   ██    ██    ██   ██
```

*Universal Device Operating System*

## Overview
The uDOS v1.0.4.1 system uses a simplified uDATA-based configuration system with JSON format compatibility, minified syntax support, and core shell-based parsing for maximum portability and performance.

## Current Structure

### Core uDATA Files in `/uMEMORY/system/`:

1. **uDATA-system-config.json** (16 lines) - Base system configuration for distribution
   - Display modes, interface settings, default values
   - Feature flags (smart terminal, auto-complete, etc.)
   - Performance settings (cache limits, history)
   - All settings use simple key-value format with uCODE naming
   - Supports both standard and minified JSON format

2. **uDATA-config.json** (14 lines) - Core system variables
   - System version v1.0.4.1, uDATA format version
   - Reference to system config file
   - Runtime variables and session data
   - Optimized for core parser compatibility

3. **uDATA-colours.json** (9 lines) - Color palette definitions
   - Polaroid Colors as default palette
   - All color palettes in unified format
   - Minified format for performance

4. **uDATA-commands.json** (26 lines) - Unified command system
   - All commands use [COMMAND|SYNTAX] format
   - Replaces separate shortcodes/commands files
   - Core parser optimized syntax

5. **uDATA-user-roles.json** (9 lines) - User role hierarchy
   - 8-role system from wizard to ghost
   - Simplified permission structure
   - JSON format with compatibility extensions

### User Authentication Data

User authentication data stored in sandbox workspace using uDATA format:

6. **sandbox/user/auth.json** - User authentication configuration
   ```json
   {
     "metadata": {
       "version": "1.0.4.1",
       "type": "user-auth",
       "created": "2025-08-26T12:00:00Z"
     },
     "authentication": {
       "method": "password",
       "hash": "sha256_hash_value",
       "salt": "user_salt"
     },
     "role": {
       "current": "wizard",
       "level": 100,
       "permissions": ["core-development", "system-admin"]
     }
   }
   ```

7. **sandbox/user/identity.md** - User identity in structured markdown
   - User settings and preferences
   - Role assignment and capabilities
   - Workspace configuration

## JSON Format & Compatibility

### Standard JSON Format
```json
{
  "system_version": "1.0.4.1",
  "udata_format": "1.0",
  "display_mode": "terminal",
  "smart_terminal": true,
  "auto_complete": true
}
```

### Minified Format Support
```json
{"system_version":"1.0.4.1","udata_format":"1.0","display_mode":"terminal","smart_terminal":true,"auto_complete":true}
```

### Core Parser Compatibility
- **Shell-native parsing**: Uses `jq` and `grep` for maximum compatibility
- **Fallback parsing**: Pure shell implementation when `jq` unavailable
- **Validation**: Built-in JSON syntax validation
- **Error handling**: Graceful degradation for malformed files

## Configuration Reader

### Core Shell Parser: `/uCORE/system/udata-config-reader.sh`

Replaces Python `config_loader.py` with a lightweight, portable shell script featuring:

**Core Features:**
- JSON parsing with `jq` (preferred) and fallback shell implementation
- Minified JSON support for optimized storage
- Real-time validation with error reporting
- Cross-platform compatibility (macOS, Linux, Unix variants)
- Zero Python dependencies for maximum portability

**Parser Capabilities:**
- Read uDATA values by key path
- Get nested configuration values
- Check boolean feature flags
- Validate JSON syntax and structure
- Generate CSS variables from color palettes
- List available commands and syntax
- Handle minified and formatted JSON equally

**Performance Optimizations:**
- Cached parsing results for frequently accessed values
- Lazy loading of configuration files
- Minimal memory footprint
- Fast key lookup algorithms

### Usage Examples:

```bash
# Get display defaults with core parser
./uCORE/system/udata-config-reader.sh get-display-defaults

# Check specific system setting with key path
./uCORE/system/udata-config-reader.sh get-value system.display.default_font

# Validate JSON format and structure
./uCORE/system/udata-config-reader.sh validate --all

# Generate CSS variables from color palette
./uCORE/system/udata-config-reader.sh generate-css polaroid_colors

# Parse minified JSON files
./uCORE/system/udata-config-reader.sh parse-minified uDATA-config.json

# Check parser compatibility
./uCORE/system/udata-config-reader.sh check-parser-support

# Benchmark parsing performance
./uCORE/system/udata-config-reader.sh benchmark
```

### Advanced Parser Features:

```bash
# Deep key path access
./uCORE/system/udata-config-reader.sh get-nested "commands.workflow.assist.syntax"

# Batch value extraction
./uCORE/system/udata-config-reader.sh get-batch "system.version,display.mode,features.enabled"

# Format conversion
./uCORE/system/udata-config-reader.sh convert --format minified input.json

# Schema validation
./uCORE/system/udata-config-reader.sh validate-schema --schema udata-v1.0.schema
```

## Removed/Deprecated

**Migration from Complex Systems:**
- `/uMEMORY/system/config/` folder → moved to `archive/config-backup/`
- `config_loader.py` → replaced with core shell parser
- Complex nested JSON configurations → simplified uDATA format with backward compatibility
- Date stamps in filenames → clean naming for foundational system design
- Python dependencies → eliminated for core configuration parsing

**Backward Compatibility:**
- Legacy JSON files still supported through compatibility layer
- Automatic migration tools for old configuration formats
- Graceful fallback for missing configuration values
- Validation warnings for deprecated configuration patterns

## User Settings

**Configuration Hierarchy:**
- `/uMEMORY/system/` - Distributable base reference settings (read-only)
- `/uMEMORY/user/` - User-specific overrides with JSON format support
- `/uMEMORY/role/` - Role-based configurations with minified options
- `/sandbox/` - Temporary/session settings with core parser compatibility

**Format Standards:**
- All user settings support both standard and minified JSON
- Core parser validates all configuration files
- Automatic format detection and conversion
- Error recovery with default value fallback

## Core Parser Implementation

### JSON Processing Pipeline

1. **Format Detection**: Automatically detect standard vs minified JSON
2. **Syntax Validation**: Core validation before parsing
3. **Key Path Resolution**: Efficient nested key access
4. **Value Type Conversion**: String, boolean, number, array handling
5. **Error Recovery**: Graceful handling of malformed data
6. **Caching Layer**: Performance optimization for repeated access

### Compatibility Matrix

| Parser Feature | jq Available | Shell Fallback | Performance |
|----------------|--------------|----------------|-------------|
| JSON Parsing | ✓ Optimal | ✓ Compatible | Fast/Medium |
| Minified Support | ✓ Native | ✓ Compatible | Fast/Medium |
| Nested Keys | ✓ Native | ✓ Custom | Fast/Slow |
| Validation | ✓ Built-in | ✓ Manual | Fast/Medium |
| Arrays | ✓ Full | ✓ Basic | Fast/Medium |

### Performance Characteristics

- **Standard JSON**: ~5ms parse time, 10KB memory
- **Minified JSON**: ~3ms parse time, 8KB memory
- **Cached Access**: ~1ms lookup time, minimal memory
- **Validation**: ~2ms overhead, comprehensive checking

## Benefits

1. **Core System Design**: Zero external dependencies for configuration parsing
2. **JSON Format Compatibility**: Full support for standard and minified JSON formats
3. **Performance Optimized**: Fast parsing with caching and minimal memory usage
4. **uCODE Integration**: Native support for uCODE naming conventions and syntax
5. **Cross-Platform**: Works on all Unix-like systems with shell and basic tools
6. **Foundational Architecture**: Clean, simple design suitable for v1.0.4.1 development stage
7. **Extensible Parser**: Easy to add new format support and validation rules
8. **Error Resilient**: Graceful degradation and comprehensive error handling
9. **Migration Ready**: Smooth transition path from complex configuration systems
10. **Development Friendly**: Clear structure for ongoing development and debugging

## Format Examples

### System Configuration (uDATA-system-config.json)
```json
{
  "system": {
    "version": "1.0.4.1",
    "display_mode": "terminal",
    "smart_terminal": true,
    "auto_complete": true,
    "cache_limit": 1000,
    "history_limit": 500
  },
  "features": {
    "workflow_assist": true,
    "briefings_auto": true,
    "encryption_default": false
  }
}
```

### Minified Commands (uDATA-commands.json)
```json
{"workflow":{"assist":{"syntax":"[WORKFLOW] <ASSIST> {ENTER}","description":"Enter assist mode"},"briefings":{"syntax":"[WORKFLOW] <BRIEFINGS> {UPDATE}","description":"Update briefings"}},"role":{"switch":{"syntax":"[ROLE] <SWITCH> {TARGET-ROLE}","description":"Switch user role"}}}
```

### Role Hierarchy (uDATA-user-roles.json)
```json
{
  "roles": {
    "wizard": {"level": 100, "access": "full"},
    "sorcerer": {"level": 80, "access": "advanced"},
    "imp": {"level": 60, "access": "development"},
    "knight": {"level": 50, "access": "security"},
    "ghost": {"level": 10, "access": "demo"}
  },
  "default_role": "ghost",
  "parser_compatible": true
}
```

## Geographic Data System

uDOS includes a comprehensive geographic data system for location-based functionality with standardized formats and validation rules.

### Geographic Data Files

**uDATA-geographic-master.json** - Primary geographic reference
- Global cities with coordinates, population, and timezone data
- TILE coordinate system for location mapping
- 4-alpha timezone codes (USPT, EUCE, JPST, etc.)
- Regional distribution and validation rules

### TILE Coordinate System

**Format**: `[A-Z]{2}[0-9]{2}` (2 letters + 2 digits)
- **Examples**: `AA24`, `CF35`, `WG10`
- **Range**: AA00-ZZ99 (global coordinate space)
- **Precision**: Covers global surface with systematic mapping

### Coordinate Standards

**Latitude/Longitude Validation**:
- **Latitude**: -90.0 to +90.0 degrees
- **Longitude**: -180.0 to +180.0 degrees
- **Precision**: 4 decimal places minimum
- **Format**: Decimal degrees (WGS84 standard)

### Timezone System

**4-Alpha Timezone Codes**:
```json
{
  "USPT": {"name": "US Pacific Time", "offset": "-08:00"},
  "USCT": {"name": "US Central Time", "offset": "-06:00"},
  "USET": {"name": "US Eastern Time", "offset": "-05:00"},
  "EUCE": {"name": "Central European Time", "offset": "+01:00"},
  "JPST": {"name": "Japan Standard Time", "offset": "+09:00"},
  "AUET": {"name": "Australian Eastern Time", "offset": "+10:00"},
  "GMTU": {"name": "Greenwich Mean Time", "offset": "+00:00"}
}
```

### City Data Template
```json
{
  "tile": "XX##",
  "city": "City Name",
  "country": "Country",
  "lat": 00.0000,
  "lon": 000.0000,
  "population": 0000000,
  "timezone": "XXXX",
  "region": "Continental Region"
}
```

### Population Classification
- **Megacity**: 10+ million (e.g., Tokyo 37.4M)
- **Large Metro**: 5-10 million (e.g., Sydney 5.4M)
- **Major City**: 2-5 million (e.g., Paris 2.1M)
- **Regional Hub**: 1-2 million (e.g., Barcelona 1.6M)

### Data Quality Standards
- **Cities**: ±100m coordinate accuracy required
- **Countries**: ±1km boundary accuracy
- **Regions**: ±10km center point accuracy
- **Population**: Annual review with official statistics
- **Timezones**: Current DST rules maintained
