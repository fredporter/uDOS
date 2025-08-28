# uDOS Display System
Grid-based interface and input handling for v1.0.4

## Overview
The uDOS Display System provides consistent interface elements:
- **uGRID**: Tile-based layout system
- **Smart Input**: Interactive data collection
- **uCELL**: 16×16 pixel display units

## Grid Layout (uGRID)

### Core Components
- **uCELL**: 16×16 pixel base unit
- **uTILE**: Content element within uCELL
- **uMAP**: Coordinate system for positioning

### Grid Sizes
| Size | Grid | Device | Use |
|------|------|--------|-----|
| Wearable | 16×16 | Watch | Single widget |
| Mobile | 40×16 | Phone | Compact interface |
| Terminal | 80×30 | Desktop | Standard CLI |
| Dashboard | 120×48 | Large | Multi-panel |

### Coordinate System
Zero-indexed positioning:
```
     0   1   2   3
   ┌───┬───┬───┬───┐
0  │0,0│1,0│2,0│3,0│
   ├───┼───┼───┼───┤
1  │0,1│1,1│2,1│3,1│
   └───┴───┴───┴───┘
```

### uCELL Format
```
┌────────────────┐ 16px
│ ░░░░░░░░░░░░░░ │
│ ░████████████░ │ ← 2px buffer
│ ░█    TEXT  █░ │ ← content area
│ ░████████████░ │
│ ░░░░░░░░░░░░░░ │
└────────────────┘
```

## Smart Input

### Input Types
```
{{INPUT:field|type|prompt|default|validation}}
```

#### Text Input
```
{{INPUT:title|text|Document title|Untitled|required,max:100}}
```

#### Selection
```
{{INPUT:priority|select|Priority|Medium|Low,Medium,High}}
```

#### Boolean
```
{{INPUT:enabled|boolean|Enable feature?|true}}
```

### Input Processing
1. **Field Discovery**: Parse template for INPUT fields
2. **Validation**: Check input against rules
3. **Collection**: Interactive prompts
4. **Processing**: Apply transformations

### Validation Rules
- `required` - Cannot be empty
- `min:N` - Minimum length/value
- `max:N` - Maximum length/value
- `email` - Valid email format
- `pattern:regex` - Custom pattern matching

## Display Elements

### ASCII Characters
Basic drawing characters:
- **Blocks**: `░ ▒ ▓ █` (25%, 50%, 75%, 100%)
- **Lines**: `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`
- **Arrows**: `← → ↑ ↓ ↖ ↗ ↘ ↙`

### Text Positioning
- **Baseline**: Row 9 of 16 in uCELL
- **Alignment**: Left, center, right within cell
- **Font**: Monospace for consistent spacing

### Layout Examples
```
Header Bar:
┌─────────────────────────────────┐
│           🚀 uDOS v1.0.4         │
└─────────────────────────────────┘

Menu Grid:
┌───────┬───────┬───────┐
│ FILE  │ EDIT  │ VIEW  │
├───────┼───────┼───────┤
│ TOOLS │ HELP  │ EXIT  │
└───────┴───────┴───────┘

Status Display:
┌─────────────────────────────────┐
│ Status: ✅ Active  User: Admin  │
└─────────────────────────────────┘
```

## Screen Management

### Display Modes
- **CLI**: Terminal-based interface
- **DESKTOP**: Native application window
- **WEB**: Browser-based interface

### Screen Contexts
```
MAIN_SCREEN     → Primary interface
SETTINGS_SCREEN → Configuration
DEBUG_SCREEN    → Development tools
```

### Widget System
Basic widget types:
- **Static**: Fixed content (text, images)
- **Interactive**: User input (buttons, forms)
- **Dynamic**: Real-time updates (status, feeds)

## Color System

### Default Palette (Polaroid)
```css
--red: #FF1744     --green: #00E676
--yellow: #FFEB3B  --blue: #2196F3
--purple: #E91E63  --cyan: #00E5FF
--white: #FFFFFF   --black: #000000
```

### Theme Support
- 8 complete color palettes available
- Configuration in `uDATA-colours.json`
- Terminal and web compatibility

## Implementation

### Core Scripts
- `startup.sh` - System initialization
- `setup.sh` - Configuration management
- `variable-manager.sh` - Data handling

### Display Rendering
```bash
# Basic grid operations
uGRID.goto(3,2)          # Position cursor
uGRID.draw_cell(content) # Render content
uGRID.refresh()          # Update display
```

### Input Collection
```bash
# Collect user input
./uCORE/code/variable-manager.sh story user-setup
./uCORE/code/setup.sh
```

## Integration Points

### Variable System
Display elements can reference variables:
```
Welcome {DEVELOPER-NAME}!
Role: {USER-ROLE}
Mode: {DISPLAY-MODE}
```

### Template Processing
Use templates for consistent layouts:
```markdown
# {TITLE}
Status: {STATUS}
Updated: {TIMESTAMP}
```

### File Generation
Templates generate display configurations:
- `installation.template.md` → system profile
- `user.template.md` → user interface

## Best Practices

### Grid Design
- Use consistent spacing (16×16 cells)
- Align elements to grid boundaries
- Leave buffer space for readability

### Input Design
- Clear labels with emoji indicators
- Helpful prompts and validation
- Logical field ordering

### Color Usage
- High contrast for readability
- Consistent palette application
- Accessible color combinations

### Performance
- Minimize display updates
- Cache rendered content
- Efficient coordinate calculations

---
*uDOS v1.0.4 - Simple, lean, fast*
