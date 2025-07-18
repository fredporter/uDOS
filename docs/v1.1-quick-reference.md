# 🚀 uDOS v1.1 Quick Reference Guide

**Enhanced Logging, Mapping & Analytics**

---

## ⚡ Enhanced Logging Commands

```bash
# Initialize enhanced logging
./uCode/enhanced-log.sh init

# Log a move with metadata
./uCode/enhanced-log.sh move "command description" [type] [context] [duration] [success]
# Types: mission, system, file, development

# Examples
./uCode/enhanced-log.sh move "dash build" system "Building dashboard" 15 true
./uCode/enhanced-log.sh move "create map layer" development "Mapping system work" 30 true

# Log errors with context
./uCode/enhanced-log.sh error "Error message" [command] [context]

# Generate daily report
./uCode/enhanced-log.sh report

# View statistics
./uCode/enhanced-log.sh stats

# Export data
./uCode/enhanced-log.sh export json
./uCode/enhanced-log.sh export csv
./uCode/enhanced-log.sh export markdown

# Archive old files
./uCode/enhanced-log.sh archive [days]
```

---

## 🗺️ Mapping System Commands

```bash
# Process mapping shortcodes
./uTemplate/mapping/process-map-shortcodes.sh process map-layers.md

# Generate complete interactive system
./uTemplate/mapping/process-map-shortcodes.sh generate-all

# Start development server
./uTemplate/mapping/process-map-shortcodes.sh serve

# Run interactive demos
./uTemplate/mapping/demo-map-integration.sh --complete
./uTemplate/mapping/demo-map-integration.sh --menu
./uTemplate/mapping/demo-map-integration.sh --serve
```

---

## 🏷️ Key Shortcodes Reference

### Map Projections
```markdown
{MAP_MERCATOR}
center_lat: 40.7128
center_lon: -74.0060
zoom_level: 4
{/MAP_MERCATOR}

{MAP_ROBINSON}
scale: 160
width: 1000
{/MAP_ROBINSON}

{MAP_ORTHOGRAPHIC}
scale: 250
interactive: true
{/MAP_ORTHOGRAPHIC}
```

### Layer Controls
```markdown
{LAYER_ATMOSPHERE}
data_source: nasa_weather
visualization: particle_system
opacity: 0.7
{/LAYER_ATMOSPHERE}

{LAYER_SURFACE}
data_source: openstreetmap
features: [countries, cities, roads]
{/LAYER_SURFACE}
```

### Data Visualization
```markdown
{VIZ_CHOROPLETH}
dataset: world_bank_gdp
color_scheme: blues
data_field: gdp_per_capita
{/VIZ_CHOROPLETH}

{VIZ_POINTS}
dataset: earthquake_data
point_size: magnitude
clustering: true
{/VIZ_POINTS}
```

### Timeline Controls
```markdown
{TIMELINE_HISTORICAL}
start_date: 1900-01-01
end_date: 2020-12-31
animation_speed: 30fps
{/TIMELINE_HISTORICAL}

{TIMELINE_REALTIME}
data_source: live_feeds
update_interval: 1s
{/TIMELINE_REALTIME}
```

---

## 📊 Analytics Features

### Daily Tracking
- **Activity Dashboard**: ASCII progress bars and metrics
- **Move Categories**: Mission, System, File, Development
- **Performance Scores**: Success rates and productivity metrics
- **Goal Tracking**: Objective-based completion monitoring

### Data Export Options
- **JSON**: Structured data for analysis
- **CSV**: Spreadsheet-compatible format  
- **Markdown**: Human-readable reports
- **HTML**: Web-based visualizations

---

## 🎯 Template Variables

### Date & Time
```markdown
{{log_date}}           # 2025-07-19
{{day_of_week}}        # Saturday  
{{timestamp}}          # 2025-07-19T00:00:00Z
{{session_time}}       # 2h 30m
```

### Activity Metrics
```markdown
{{moves_count}}        # Total moves today
{{commands_count}}     # Total commands
{{errors_count}}       # Error count
{{success_rate}}       # Success percentage
{{progress_bar}}       # ASCII progress bar
```

### Performance Data
```markdown
{{productivity_score}} # Productivity percentage
{{efficiency_score}}   # Efficiency rating
{{session_duration}}   # Session length
{{completion_percentage}} # Goal completion
```

---

## 🔧 File Locations

### Enhanced Logs
```
uMemory/moves/daily-log-YYYY-MM-DD.md    # Enhanced daily reports
uMemory/moves/moves-YYYY-MM-DD.md        # Move logs
uMemory/state/stats-YYYY-MM-DD.json      # JSON statistics
uMemory/logs/errors-YYYY-MM-DD.log       # Error logs
uMemory/exports/YYYY-MM-DD/              # Exported data
```

### Mapping System
```
uTemplate/mapping/map-layers.md          # Core layer definitions
uTemplate/mapping/process-map-shortcodes.sh  # Processor
uTemplate/mapping/demo-map-integration.sh    # Demo system
uTemplate/mapping/README.md             # Documentation
```

### Generated Output
```
map-output/html/map-interface.html       # Interactive interface
map-output/js/map-core.js                # Core engine
map-output/css/map-styles.css            # Styling
map-output/layers/*.json                 # Layer configs
```

---

## 📈 ASCII Dashboard Examples

### Activity Tracker
```ascii
╔═══════════════════════════════════════════════════════╗
║               📊 DAILY ACTIVITY TRACKER              ║
╠═══════════════════════════════════════════════════════╣
║  🎯 MOVES: 15      ⚡ COMMANDS: 28                   ║
║  📊 SUCCESS: 96%   ❌ ERRORS: 1                      ║
║  ⏱️  SESSION: 3h   📈 PRODUCTIVITY: 85%              ║
╚═══════════════════════════════════════════════════════╝
```

### Progress Bars
```ascii
Development: [████████░░] 80%
Documentation: [██████░░░░] 60%  
Testing: [████░░░░░░] 40%
```

### Layer Stack
```ascii
┌─ ATMOSPHERE (+∞)    │  🛰️ Satellites
├─ AVIATION (+10km)   │  ✈️ Flight Paths
├─ SURFACE (0m)       │  🌍 Geography
└─ GEOLOGICAL (-1km)  │  🪨 Rock Data
```

---

## 🚀 Integration Points

### VS Code Tasks
- Use existing uDOS tasks with enhanced logging
- Map generation integrates with workspace
- Templates accessible via VS Code snippets

### uMemory Integration
- All analytics stored in uMemory (private)
- Automatic archival preserves history
- Export options maintain data portability

### Dashboard Integration  
- Enhanced metrics feed dashboard
- ASCII blocks improve visual presentation
- Real-time updates from logging system

---

## 🔮 Next Steps

1. **Test Enhanced Features**: Use new logging and mapping systems
2. **Customize Templates**: Adapt shortcodes for your workflow
3. **Explore Analytics**: Review daily reports and statistics
4. **Create Maps**: Build interactive visualizations
5. **Export Data**: Generate reports in preferred formats

---

**Quick Start**: `./uCode/enhanced-log.sh init && ./uCode/enhanced-log.sh move "first enhanced log" system`

*Reference Guide v1.1.0 - 2025-07-19*
