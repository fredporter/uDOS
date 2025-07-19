# uDOS CAPITAL Rule Enforcement v1.1.0

## Overview
uDOS now enforces a consistent **CAPITAL RULE** across all commands, shortcodes, and variables for a cleaner, more professional aesthetic.

## What Changed

### 🔧 uCode Commands
- **Still accept input in any case**: `help`, `HELP`, `Help` all work
- **Always displayed in CAPITALS**: Documentation and help text shows `HELP`, `CHECK`, `RUN`
- **Converted automatically**: `cmd=$(echo "$input" | awk '{print toupper($1)}')`

### 🔗 Shortcodes
- **Now require CAPITALS**: `[RUN:script-name]`, `[CHECK:health]`, `[BASH:ls -la]`
- **Auto-converted**: Input like `[run:script]` automatically becomes `[RUN:script]`
- **Consistent display**: All documentation shows `[SHORTCODE:args]` format

### 📊 Variables
- **All CAPITALS**: `$USERNAME`, `$LOCATION`, `$TIMEZONE`, `$UDOS_VERSION`
- **Template variables**: `$VARIABLE` format throughout templates
- **Environment variables**: All uDOS environment variables use CAPITALS

## Examples

### ✅ Correct Format (NEW)
```bash
# Commands (any case input, CAPITAL display)
ucode> help
ucode> CHECK all
ucode> RUN dashboard

# Shortcodes (CAPITAL required)
[RUN:hello-world]
[CHECK:health]
[BASH:ls -la]
[MISSION:create name=test]
[DATA:csv file=data.csv]

# Variables (CAPITAL required)
$USERNAME
$LOCATION  
$TIMEZONE
$UDOS_VERSION
```

### ❌ Old Format (deprecated)
```bash
# Old shortcodes (still work but converted)
[run:hello-world]  → [RUN:hello-world]
[check:health]     → [CHECK:health]
[bash:command]     → [BASH:command]

# Old variables (should be updated)
$username  → $USERNAME
$location  → $LOCATION
```

## Implementation Details

### Shortcode Processors
- `shortcode-processor-simple.sh`: Updated to convert input to CAPITALS
- `shortcode-processor.sh`: Updated for CAPITAL enforcement
- `vb-enhanced-interpreter.sh`: VB shortcodes now use CAPITALS

### Pattern Matching
```bash
# Auto-conversion in processors
shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
```

### Help and Documentation
- All help text updated to show CAPITAL shortcodes
- Examples use CAPITAL format
- Documentation consistently shows `[SHORTCODE:args]` syntax

## Benefits

### 🎯 Visual Consistency
- Clean, professional appearance
- Easy to distinguish between different syntax elements
- Consistent with terminal/command-line conventions

### 🔍 Better Recognition
- CAPITALS make shortcodes stand out in text
- Clear differentiation from regular text
- Improved readability in documentation

### ⚡ Backward Compatibility
- Old lowercase shortcodes still work (auto-converted)
- Gradual migration path for existing scripts
- No breaking changes for users

## Migration Guide

### For Users
1. **Commands**: No change needed - any case still works
2. **Shortcodes**: Start using CAPITALS for new work
3. **Variables**: Update templates to use CAPITAL variables

### For Developers
1. Update shortcode examples in documentation
2. Use CAPITAL format in new templates
3. Convert variables to CAPITALS in new configurations

### For Scripts
```bash
# Old format (deprecated but working)
[run:hello-world]
[check:health]

# New format (preferred)
[RUN:hello-world]  
[CHECK:health]
```

## Files Updated

### Core Processors
- `uCode/shortcode-processor-simple.sh`
- `uCode/shortcode-processor.sh`
- `uCode/vb-enhanced-interpreter.sh`
- `uCode/ucode.sh`

### Test Files
- `uCode/test-extension-integration.sh`

### Documentation
- Updated help text and examples
- Consistent CAPITAL formatting throughout

## Technical Notes

### Case Conversion
```bash
# Automatic case conversion in processors
local shortcode_name=$(echo "${BASH_REMATCH[1]}" | awk '{print toupper($0)}')
```

### Pattern Recognition
- Still accepts mixed case input
- Converts to CAPITALS for processing
- Displays in CAPITALS in output

### Backward Compatibility
- Old format shortcodes automatically converted
- No user-facing breaking changes
- Gradual adoption possible

---

*This update enhances the visual consistency and professional appearance of uDOS while maintaining full backward compatibility.*
