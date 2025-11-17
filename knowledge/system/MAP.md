# MAP Command Reference

The `MAP` command provides comprehensive navigation and geographical features with APAC-centered cell reference system.

## Basic Usage

```bash
MAP <subcommand> [options]
```

## Subcommands

### MAP STATUS
Show current location and mapping system status.

```bash
MAP STATUS
```

**Output:**
- Current location (if set)
- Cell reference (A1-RL270 format)
- Available layers
- Connection status

### MAP VIEW
Generate ASCII map of current or specified location.

```bash
MAP VIEW [width] [height] [cell_ref]
```

**Examples:**
```bash
MAP VIEW                    # Default 30x15 map of current location
MAP VIEW 40 20              # Custom size map
MAP VIEW 30 15 JG79         # Map centered on Tokyo (JG79)
```

### MAP CITIES
List cities in current region or globally.

```bash
MAP CITIES [region|global]
```

**Examples:**
```bash
MAP CITIES                  # Cities in current region
MAP CITIES global           # All 20 TIZO cities
MAP CITIES 3                # Cities within 3 cell radius
```

### MAP CELL
Get detailed information about a specific cell.

```bash
MAP CELL <cell_reference>
```

**Example:**
```bash
MAP CELL JG79               # Information about Tokyo cell
```

**Output:**
- Cell coordinates
- Geographic location (lat/lon)
- Nearby cities
- Layer information

### MAP NAVIGATE
Calculate navigation between two locations.

```bash
MAP NAVIGATE <from> <to>
```

**Examples:**
```bash
MAP NAVIGATE TYO SIN        # Tokyo to Singapore
MAP NAVIGATE JG79 HK133     # Using cell references
MAP NAVIGATE current TYO    # From current location to Tokyo
```

**Output:**
- Distance in kilometers
- Bearing/direction
- Estimated travel time
- Cell path (if adjacent)

### MAP LOCATE
Set current location to a city or cell.

```bash
MAP LOCATE <city_code|cell_ref>
```

**Examples:**
```bash
MAP LOCATE TYO              # Set location to Tokyo
MAP LOCATE JG79             # Set location to cell JG79
MAP LOCATE 35.68 139.69     # Set location by coordinates
```

### MAP LAYERS
Show accessible mapping layers and switch between them.

```bash
MAP LAYERS [layer_name]
```

**Available Layers:**
- **SURFACE**: Standard geographical view
- **CLOUD**: Weather and atmospheric data
- **SATELLITE**: Satellite imagery view
- **DUNGEON**: Underground/subway systems

### MAP GOTO
Move to specific coordinates or cell references.

```bash
MAP GOTO <destination>
```

**Examples:**
```bash
MAP GOTO 35.68 139.69       # Go to coordinates
MAP GOTO JG79               # Go to cell reference
MAP GOTO TYO                # Go to city code
```

## Advanced Features

### Teletext Mode
Generate retro teletext-style maps.

```bash
MAP TELETEXT [width] [height]
```

Features mosaic block characters and classic teletext colors.

### Web Interface
Open maps in web browser.

```bash
MAP WEB [server]
```

**Options:**
- `server`: Start HTTP server for interactive maps
- No option: Open current map in browser

## Cell Reference System

### Format
- **Columns**: A-RL (480 columns)
- **Rows**: 1-270 (270 rows)
- **Examples**: A1, JG79, RL270

### APAC-Centered Grid
- **Center**: 120°E longitude (Asia-Pacific focus)
- **Coverage**: Global with optimized Asian detail
- **Resolution**: ~0.75° longitude, ~0.63° latitude per cell

### Conversion
```bash
# Coordinates to cell
MAP CELL 35.68 139.69       # Returns JG79

# Cell to coordinates
MAP CELL JG79               # Returns 35.68, 139.69
```

## TIZO Location Codes

### Global Cities (20 locations)
- **TYO**: Tokyo, Japan (JG79)
- **SIN**: Singapore (HK133)
- **HKG**: Hong Kong (JH131)
- **BJS**: Beijing, China (JF75)
- **SYD**: Sydney, Australia (KM217)
- **And 15 more...**

### Usage
All TIZO codes work interchangeably with cell references in MAP commands.

## Configuration

### Location Setting
```bash
# Set default location
CONFIG set default_location TYO

# Set cell grid preferences
CONFIG set map_default_size "30x15"
CONFIG set map_ascii_style "detailed"
```

### Layer Preferences
```bash
# Set default layer
CONFIG set default_map_layer SURFACE

# Enable layer transitions
CONFIG set map_layer_animation true
```

## Integration

### With Other Commands
```bash
# Navigate and view
MAP LOCATE TYO
MAP VIEW 40 20

# Search and goto
FILE SEARCH tokyo.txt
MAP GOTO $(FILE PWD)
```

### With ASK Command
```bash
ASK What is cell JG79?
ASK How far is Tokyo from Singapore?
ASK Explain the APAC grid system
```

## Technical Details

### Implementation
- **Handler**: `MapCommandHandler` in `core/commands/map_handler.py`
- **Engine**: `MapEngine` service with `CellReferenceSystem`
- **Database**: TIZO cities with pre-computed cell references
- **Rendering**: ASCII art with optional teletext mosaic

### Cell Calculation Algorithm
1. **Longitude Wrapping**: Normalize around 120°E center
2. **Projection**: Convert lat/lon to grid coordinates
3. **Cell Mapping**: Apply A1-style column/row naming
4. **Validation**: Ensure coordinates within grid bounds

### Performance
- **City Database**: 20 cities with O(1) lookup
- **Cell Calculations**: Optimized coordinate transformations
- **ASCII Rendering**: Efficient character-based maps
- **Caching**: Cell reference caching for repeated queries

## Troubleshooting

### Common Issues
1. **Invalid Cell Reference**: Use format A1-RL270
2. **Location Not Set**: Use `MAP LOCATE` first
3. **Layer Not Available**: Check `MAP LAYERS` for options
4. **Navigation Errors**: Verify both locations exist

### Debug Commands
```bash
MAP STATUS                  # Check system state
MAP LAYERS                  # Verify layer access
MAP CITIES global           # Confirm city database
```

## Examples

### Basic Navigation
```bash
# Set location and explore
MAP LOCATE TYO
MAP VIEW
MAP CITIES
MAP NAVIGATE TYO SIN
```

### Cell Reference Exploration
```bash
# Work with cell coordinates
MAP CELL JG79
MAP GOTO JG79
MAP VIEW 20 10
```

### Multi-layer Exploration
```bash
# Switch between layers
MAP LAYERS SURFACE
MAP VIEW
MAP LAYERS SATELLITE
MAP VIEW
```

## Tags
#mapping #navigation #geography #cells #cities #TIZO #APAC #coordinates
