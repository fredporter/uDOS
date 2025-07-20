# VB Command Template: GRID.POSITION

**Template Version:** v2.0.0  
**Generated:** {{timestamp}}  
**User:** {{username}}  
**Location:** {{location}} ({{grid_position}})  
**Timezone:** {{timezone}}

> **Command Category:** System Integration  
> **Command Type:** Grid Operation  
> **Execution Level:** Intermediate  
> **Integration Mode:** Grid System

---

## 📋 Command Overview

### 🎯 Purpose & Functionality
Set or retrieve the current grid position within the uDOS coordinate system. This command integrates with the display configuration and location mapping systems to provide spatial context for operations.

### 🔧 Command Configuration
- **Command Name:** GRID.POSITION
- **Version:** 2.0.0
- **Category:** system
- **Syntax Level:** intermediate
- **Error Handling:** comprehensive
- **Variable Scope:** global

---

## ⚙️ Command Definition

### 🌀 VB Syntax
```vb
GRID.POSITION [<position>]
```

**Description:** Sets or gets the current grid position using the uDOS coordinate system  
**Return Type:** String (when getting position)  
**Side Effects:** Updates global grid context and location variables  

### 📝 Parameters
- **position** (String): Grid coordinate in format A1-ZZ99
  - Required: false
  - Default: `current position`
  - Validation: Valid grid coordinate format
  - Range: A1 to ZZ99 (depending on grid mode)

### 📊 Examples
```vb
' Get current grid position
DIM currentPos As String
SET currentPos = GRID.POSITION
```
**Context:** Retrieve current position  
**Expected Output:** Grid coordinate string (e.g., "B5")  
**Notes:** Returns current position without changing it

---
```vb
' Set grid position
GRID.POSITION "C7"
```
**Context:** Move to specific grid position  
**Expected Output:** Position updated message  
**Notes:** Updates all related grid variables

---
```vb
' Use in conditional logic
IF GRID.POSITION = "A1" THEN
    PRINT "At origin position"
ELSE
    PRINT "Current position: " + GRID.POSITION
END IF
```
**Context:** Grid-aware conditional processing  
**Expected Output:** Position-based message  
**Notes:** Demonstrates position checking

---

## 🔧 Implementation Details

### 🏗️ Backend Integration
- **uCode Script:** display-config.sh
- **Template Processor:** vb-template-processor.sh
- **Variable Manager:** variable-manager.sh
- **Error Handler:** vb-enhanced-interpreter.sh

### 🗺️ System Integration
- **Grid Position:** {{grid_position}}
- **Location Mapping:** {{location}} coordinate system
- **Timezone Context:** {{timezone}} awareness
- **User Variables:** Persistent grid state

### 📡 Shortcode Integration
- **{{GRID}}**: Current grid position
  - Context: Template processing
  - Variables: UDOS_GRID_POSITION
- **{{LOCATION}}**: Location-grid mapping
  - Context: Geographic positioning
  - Variables: UDOS_CURRENT_LOCATION

---

## 🧪 Testing & Validation

### ✅ Test Cases
**Test 0:** Get Current Position
```vb
DIM pos As String = GRID.POSITION
```
**Expected:** Current grid coordinate  
**Validation:** Format matches grid pattern

**Test 1:** Set Valid Position
```vb
GRID.POSITION "B5"
```
**Expected:** Position updated successfully  
**Validation:** Grid variables updated

**Test 2:** Set Invalid Position
```vb
GRID.POSITION "ZZZ999"
```
**Expected:** Error with validation message  
**Validation:** Error handling active

**Test 3:** Position Persistence
```vb
GRID.POSITION "C3"
' ... other operations
DIM check As String = GRID.POSITION
```
**Expected:** Position remains C3  
**Validation:** State persistence confirmed

**Test 4:** Grid Mode Compatibility
```vb
' Test in both standard and extended grid modes
GRID.POSITION "AA25"  ' Extended mode
```
**Expected:** Works in extended mode, error in standard  
**Validation:** Mode-appropriate behavior

### 🚨 Error Conditions
- **invalid_format**: Invalid grid coordinate format
  - Error Code: GRID_001
  - Recovery: Reset to default position
- **out_of_bounds**: Position outside current grid limits
  - Error Code: GRID_002
  - Recovery: Use nearest valid position
- **grid_not_initialized**: Grid system not properly set up
  - Error Code: GRID_003
  - Recovery: Initialize with defaults

---

## 📚 Related Commands

### 🔗 Command Family
- **LOCATION.SET**: Set geographic location context
  - Category: system
  - Relationship: Updates grid context
- **GRID.HIGHLIGHT**: Highlight current grid position
  - Category: display
  - Relationship: Visual feedback for position
- **GRID.NAVIGATE**: Move to relative grid position
  - Category: navigation
  - Relationship: Position manipulation

### 🎯 Usage Patterns
```vb
' Pattern 1: Position-aware processing
GRID.POSITION "B5"
TEMPLATE.PROCESS "grid-specific-template.md"
```
**Scenario:** Location-specific template processing  
**Best Practice:** Set position before template operations

```vb
' Pattern 2: Grid navigation loop
FOR row = 1 TO 10
    FOR col = 1 TO 5
        GRID.POSITION CHR(64 + col) + STR(row)
        ' Process at each position
    NEXT col
NEXT row
```
**Scenario:** Systematic grid traversal  
**Best Practice:** Use nested loops for area coverage

---

## 🎨 Template Variables

### 📍 System Variables
- `{{CURRENT_USER}}` - Current username: {{username}}
- `{{CURRENT_LOCATION}}` - User location: {{location}}
- `{{CURRENT_GRID}}` - Grid position: {{grid_position}}
- `{{CURRENT_TIME}}` - Timestamp: {{timestamp}}
- `{{CURRENT_TIMEZONE}}` - User timezone: {{timezone}}

### 🎛️ Command Variables
- `{{GRID_MODE}}` - Grid system mode (standard/extended)
  - Type: String
  - Scope: Global
  - Default: standard
- `{{GRID_CELL_SIZE}}` - Cell dimensions
  - Type: String
  - Scope: Display
  - Default: 4x2
- `{{GRID_LIMITS}}` - Maximum grid boundaries
  - Type: String
  - Scope: System
  - Default: A1:Z99

---

## 🔄 Template Processing

**Template File:** `vb-command-template.md`  
**Processor Version:** 2.0.0  
**Generated by:** uDOS VB Command Template System  
**Last Updated:** {{timestamp}}

### 🎯 Generation Context
- **Template Mode:** individual_command
- **Integration Level:** full_system
- **Customization:** grid_integration

---

*Generated by uDOS v1.0 VB Command Template System*
