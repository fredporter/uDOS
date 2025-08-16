# 🎯 uDOS Enhanced Input System Documentation
**Version:** 1.0.0  
**Date:** 2025-07-20  
**Status:** Production Ready

## 🌟 Overview

The uDOS Enhanced Input System revolutionizes user interaction with the uDOS environment by providing:

- **🔍 Predictive Shortcode Selection**: Intelligent type-ahead search for shortcodes with arrow key navigation
- **📝 Enhanced Dataget Processing**: Rich, interactive datagets for variable collection with validation and ASCII block styling
- **⌨️ Reduced Keyboard Clicks**: Streamlined input process with smart suggestions and auto-completion
- **🎨 ASCII Visual Integration**: Consistent with uDOS's signature block-oriented visual design

## ✨ Key Features

### 🚀 Predictive Shortcode Input
When you type `[` in the uCode shell, the system automatically launches an intelligent shortcode selector:

```
🔍 Shortcode Selector - Type: [D

┌─────────────────────────────────────────────────────────────────────┐
║                    🔍 Shortcode Selector                           ║
├─────────────────────────────────────────────────────────────────────┤
║                                                                     ║
║ ▶ DASH - Dashboard operations                                       ║
║   DATA - Data processing and manipulation                           ║
║                                                                     ║
║ ↑↓ Navigate | Enter: Select | Esc: Cancel                          ║
╚─────────────────────────────────────────────────────────────────────╝

┌─────────────────────────────────────────────────────┐
║                💡 Example Usage                        ║
├─────────────────────────────────────────────────────┤
║ [DASH:live]                                             ║
╚─────────────────────────────────────────────────────╝
```

### 📋 Interactive Dataget System
Rich datagets for variable collection with real-time validation:

```
📝 uDOS User Setup & Configuration
Complete your uDOS environment setup with intelligent dataset integration

╔═══════════════════════════════════════════════════════════════════╗
║                    📝 uDOS User Configuration                     ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║ ▶ Field 1:                                                        ║
║ 👤 Username* (noblank)                                            ║
║ [agentdigital____________________________]                        ║
║ 💡 Enter a unique username (3-20 characters, alphanumeric only)   ║
║                                                                   ║
║   Field 2:                                                        ║
║ 📍 Location* (noblank)                                            ║
║ [London, United Kingdom (AX14)__________] (default)               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

↑↓ Navigate | Enter: Edit | Tab: Next | Ctrl+S: Save | Esc: Cancel
```

## 🛠️ System Components

### 1. Core Scripts
- **`input-system.sh`** - Main input system with predictive features
- **`input-handler.sh`** - Integration layer with uCode shell
- **`validate-input-system.sh`** - Comprehensive testing and validation

### 2. Dataget Configurations
- **`uTemplate/datagets/user-setup.json`** - User onboarding dataget
- **`uTemplate/datagets/mission-create.json`** - Mission creation dataget  
- **`uTemplate/datagets/system-config.json`** - System configuration dataget
- **`uTemplate/dataget-configuration-template.md`** - Dataget creation guide

### 3. Datasets
- **`uTemplate/datasets/shortcodes.json`** - Shortcode command dataset
- **`uKnowledge/datasets/commands.json`** - Command reference dataset

## 🎯 Usage Guide

### Launching Shortcode Selector

#### Method 1: Trigger Character
```bash
ucode
🌀 [           # Type [ to trigger selector automatically
```

#### Method 2: Direct Command
```bash
ucode INPUT SHORTCODE
```

#### Method 3: Script Direct
```bash
./uCode/input-system.sh shortcode
```

### Using Interactive Datagets

#### Process Built-in Datagets
```bash
ucode DATAGET user-setup      # User configuration
ucode DATAGET mission-create  # Create new mission
ucode DATAGET system-config   # System settings
```

#### Enhanced Command Integration
```bash
ucode SETUP --interactive  # Uses enhanced dataget system
ucode MISSION CREATE       # Launches mission creation dataget
ucode CONFIGURE            # System configuration dataget
```

### Navigation Controls

#### Shortcode Selector Navigation
- **↑↓** - Navigate suggestions
- **Enter** - Select current shortcode
- **Tab** - Auto-complete partial match
- **Esc** - Cancel selection
- **Type** - Filter suggestions in real-time

#### Dataget Navigation
- **↑↓** - Navigate between fields
- **Enter** - Edit current field
- **Tab** - Move to next field
- **Shift+Tab** - Move to previous field
- **Ctrl+S** - Save dataget
- **Esc** - Cancel dataget

## 📝 Dataget Field Types

### Text Input
```json
{
    "name": "username",
    "label": "👤 Username",
    "type": "text",
    "required": true,
    "noblank": true,
    "validation": "^[a-zA-Z][a-zA-Z0-9_]{2,19}$",
    "help": "Enter a username (3-20 characters)",
    "default": "user001"
}
```

### Choice Selection
```json
{
    "name": "priority",
    "label": "⚡ Priority Level",
    "type": "choice",
    "options": ["low", "medium", "high", "critical"],
    "default": "medium",
    "noblank": true
}
```

### Boolean (Yes/No)
```json
{
    "name": "auto_backup",
    "label": "💾 Auto Backup",
    "type": "boolean",
    "default": true,
    "noblank": true
}
```

### Password Field
```json
{
    "name": "password",
    "label": "🔑 Password",
    "type": "password",
    "required": false,
    "noblank": false,
    "help": "Leave blank for no password",
    "default": ""
}
```

### Dataset Integration
```json
{
    "name": "location",
    "label": "📍 Location",
    "type": "dataset_select",
    "dataset": "locationMap",
    "predictive_search": true
}
```

## 🔧 Advanced Configuration

### Creating Custom Datagets

1. **Create Dataget Configuration**
```bash
# Create new dataget in uTemplate/datagets/
cat > uTemplate/datagets/my-dataget.json << 'EOF'
{
    "title": "My Custom Dataget",
    "description": "Custom variable collection dataget",
    "fields": [
        {
            "name": "field1",
            "label": "Field 1",
            "type": "text",
            "required": true,
            "noblank": true,
            "default": "default_value"
        }
    ]
}
EOF
```

2. **Use Custom Dataget**
```bash
ucode DATAGET my-dataget
```

### Adding Custom Shortcodes

1. **Edit Shortcode Dataset**
```bash
# Edit uTemplate/datasets/shortcodes.json
jq '.shortcodes += [{
    "command": "CUSTOM",
    "category": "utility",
    "description": "Custom command",
    "args": ["arg1", "arg2"],
    "examples": ["[CUSTOM:arg1]"]
}]' uTemplate/datasets/shortcodes.json > temp.json && mv temp.json uTemplate/datasets/shortcodes.json
```

2. **Reinitialize System**
```bash
./uCode/input-system.sh init
```

## 🎨 Visual Design System

### ASCII Block Styling
The input system uses consistent ASCII block design that adapts to terminal size:

```
Display Mode    Block Width    Border Style
────────────    ───────────    ────────────
micro           30×4          minimal
console         40×6          single  
wide            60×8          double
mega            80×10         heavy
```

### Color Scheme Integration
- **Cyan** (🔵) - Headers and navigation
- **Green** (🟢) - Success and selected items
- **Yellow** (🟡) - Warnings and highlights  
- **Red** (🔴) - Errors and validation issues
- **Dim** (⚫) - Help text and secondary info

### Responsive Design
Datagets automatically adapt to:
- Terminal width (`$UDOS_TERMINAL_COLS`)
- Display mode (`$UDOS_DISPLAY_MODE`)
- Border style preferences (`$UDOS_BORDER_STYLE`)

## 🔍 Troubleshooting

### Common Issues

#### Shortcode Selector Not Triggering
```bash
# Check input handler integration
source uCode/input-handler.sh
echo "Integration status: $?"
```

#### Datagets Not Loading
```bash
# Validate dataget configuration
./uCode/validate-input-system.sh test
```

#### JSON Validation Errors
```bash
# Check JSON syntax
jq '.' uTemplate/datagets/user-setup.json
```

#### Missing Dependencies
```bash
# Check required tools
command -v jq >/dev/null || echo "jq required for JSON processing"
command -v tput >/dev/null || echo "tput recommended for terminal detection"
```

### Performance Optimization

#### Large Datasets
For datasets with >100 entries:
```json
{
    "max_suggestions": 5,
    "search_debounce": 200,
    "cache_results": true
}
```

#### Terminal Compatibility
For older terminals:
```bash
export UDOS_SIMPLE_BORDERS=true
export UDOS_NO_COLORS=true
```

## 📊 System Integration

### uCode Shell Integration
The input system integrates seamlessly with the main uCode shell:

1. **Automatic Loading** - Input handler loads with uCode shell
2. **Trigger Detection** - `[` character automatically launches selector
3. **Command Enhancement** - Datagets integrate with existing commands
4. **State Preservation** - Dataget data persists in uMemory structure

### File Structure Impact
```
uDOS/
├── uCode/
│   ├── input-system.sh         # Core input system
│   ├── input-handler.sh        # Integration layer
│   └── validate-input-system.sh # Testing suite
├── uTemplate/
│   ├── datagets/                  # Dataget configurations
│   │   ├── user-setup.json
│   │   ├── mission-create.json
│   │   └── system-config.json
│   └── datasets/               # Variable data collections
│       └── shortcodes.json
└── uMemory/
    ├── datagets/                  # Completed dataget data
    └── config/                 # Generated configurations
```

## 🚀 Future Enhancements

### Planned Features
- **🔮 AI-Powered Suggestions** - Machine learning for command prediction
- **🎨 Custom Themes** - User-defined color schemes and layouts
- **📱 Mobile Terminal Support** - Optimized for mobile SSH clients
- **🌐 Remote Dataget Processing** - Cloud-based dataget validation and storage
- **🔄 Real-time Collaboration** - Multi-user dataget editing

### Extension Points
- **Plugin System** - Custom input field types
- **API Integration** - External data source connections
- **Workflow Engine** - Multi-step dataget processes
- **Analytics Dashboard** - Input pattern analysis

## 📚 API Reference

### Core Functions

#### `interactive_shortcode_selector(partial)`
Launch interactive shortcode selector with optional partial string.

#### `interactive_dataget(config, output)`
Process interactive dataget with given configuration and output file.

#### `get_shortcode_suggestions(partial, max)`
Get shortcode suggestions matching partial input.

#### `render_dataget_field(field_data, value, width)`
Render individual dataget field with current value.

### Configuration Schema

#### Dataget Configuration
```json
{
    "title": "string",
    "description": "string", 
    "category": "setup|configuration|data-entry|survey",
    "version": "string",
    "fields": [
        {
            "name": "string",
            "label": "string", 
            "type": "text|choice|boolean|email|password|number|date",
            "required": "boolean",
            "noblank": "boolean (default: true, except password defaults to false)",
            "validation": "regex",
            "help": "string",
            "options": ["array"],
            "default": "any (meaningful default required if noblank=true)",
            "conditional": {
                "show_when": "field_name",
                "equals": "value"
            }
        }
    ],
    "actions": {
        "save": "auto|manual",
        "validate": "real_time|on_submit",
        "output_format": "json|yaml|env_vars"
    }
}
```

## 🎯 Best Practices

### Dataget Design
1. **Clear Labels** - Use descriptive, emoji-enhanced labels
2. **Logical Grouping** - Group related fields together
3. **Progressive Disclosure** - Use conditional fields appropriately  
4. **Validation Feedback** - Provide immediate validation feedback
5. **Help Text** - Include contextual help for complex fields
6. **Default Values** - Provide meaningful defaults for all non-password fields

### Shortcode Organization
1. **Consistent Naming** - Use clear, descriptive command names
2. **Logical Categories** - Group related commands by category
3. **Example Provision** - Always include usage examples
4. **Documentation** - Provide comprehensive help text

### Performance Considerations
1. **Lazy Loading** - Load datasets only when needed
2. **Result Caching** - Cache suggestion results for better performance
3. **Debounced Input** - Avoid excessive API calls during typing
4. **Memory Management** - Clean up resources after dataget completion

### Dataset Validation Rules
1. **Noblank**: All fields default to "noblank" unless explicitly set to false
2. **Default Values**: Required for all non-password fields when noblank=true
3. **Password Exception**: Password fields default to noblank=false (blank = no password)
4. **Meaningful Defaults**: Default values must be useful examples, not placeholder text
5. **Validation Patterns**: All text inputs should include appropriate regex validation

---

This enhanced input system transforms uDOS into a modern, user-friendly environment while maintaining its distinctive ASCII aesthetic and powerful command-line capabilities. The combination of predictive shortcuts and rich datagets significantly reduces keyboard input requirements while providing an intuitive, guided experience for both new and experienced users.

**Key Terminology:**
- **Dataset**: Collection of saved $variable data (stored values)
- **Dataget**: Collection of questions to gather $variable data (data collection interface)
