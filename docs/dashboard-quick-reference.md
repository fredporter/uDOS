# uDOS Dashboard Quick Reference v2.0.0

**Enhanced Dashboard with uTemplate & ASCII Integration**  
*Ready-to-use commands and shortcuts*

---

## 🚀 Quick Commands

### Dashboard Actions
```bash
# Core Dashboard Operations
[dash:refresh]      # Build complete dashboard with metrics
[dash:ascii]        # Show ASCII terminal dashboard  
[dash:markdown]     # Show rich markdown dashboard via glow
[dash:live]         # Start real-time monitoring (Ctrl+C to exit)

# Analytics & Data
[dash:analytics]    # Show JSON analytics data
[dash:metrics]      # Collect fresh system metrics
[dash:config]       # Display dashboard configuration

# Export Operations  
[dash:export html]  # Export to HTML format
[dash:export pdf]   # Export to PDF format
[dash:export txt]   # Export ASCII version to text file
```

### Combined Operations
```bash
# Popular Combinations
[package:list] && [dash:refresh]        # Update packages then dashboard
[mission:create test] && [dash:ascii]   # Create mission then show ASCII
[check:health] && [dash:analytics]      # Health check then analytics
```

---

## 📊 Dashboard Components

### ASCII Dashboard Features
- **Header:** System info, user, hostname, time
- **Metrics:** Missions, moves, templates, packages, errors
- **Mission Status:** Active mission display
- **Progress Bars:** Visual progress indicators
- **Quick Actions:** One-click shortcode commands
- **Analytics Section:** Performance metrics and trends

### Markdown Dashboard Features  
- **Rich Formatting:** Styled text with glow rendering
- **Comprehensive Overview:** Complete system status
- **Project Portfolio:** Mission and template summaries
- **Activity Feed:** Recent moves and changes
- **Performance Analytics:** Detailed metrics with visualizations

---

## 🎯 Template Variables (50+ available)

### System Variables
- `{{timestamp}}` → Current date/time
- `{{user_name}}` → Current user (agentdigital)
- `{{hostname}}` → System hostname
- `{{uptime}}` → System uptime in days
- `{{health_status}}` → Health indicator (🟢/🟡/🔴)

### uDOS Metrics
- `{{missions_count}}` → Number of active missions
- `{{moves_today}}` → Today's activity count  
- `{{templates_count}}` → Available templates
- `{{errors_today}}` → Error count for today
- `{{packages_installed}}` → Installed packages count

### Progress Indicators
- `{{daily_progress_bar}}` → Visual daily progress
- `{{mission_progress_bar}}` → Mission completion bar
- `{{storage_progress_bar}}` → Storage usage bar
- `{{efficiency_bar}}` → System efficiency indicator

---

## 📁 File Locations

### Templates
```
uTemplate/
├── dashboard-template.md          # Markdown dashboard template
├── ascii-dashboard-template.txt   # ASCII dashboard template
└── package-template.md           # Package template

uMemory/dashboard/
├── current.md                    # Generated markdown dashboard
├── ascii.txt                     # Generated ASCII dashboard  
├── variables.json                # Current template variables
└── config.json                   # Dashboard configuration
```

### Scripts
```
uCode/
├── dash-enhanced.sh              # Main enhanced dashboard
├── dash.sh                       # Original dashboard (legacy)
└── shortcode-processor-simple.sh # Shortcode processor with dash commands
```

---

## ⚡ Performance Tips

### Fast Dashboard Updates
```bash
# Quick ASCII view (fastest)
[dash:ascii]

# Full refresh (comprehensive) 
[dash:refresh]

# Live monitoring (continuous)
[dash:live]
```

### Efficient Workflows
1. **Morning Startup:** `[dash:refresh]` → Get complete overview
2. **Quick Checks:** `[dash:ascii]` → Fast status view  
3. **Deep Analysis:** `[dash:markdown]` → Rich detailed view
4. **Monitoring:** `[dash:live]` → Real-time updates

---

## 🔧 Customization

### Configuration File (`uMemory/dashboard/config.json`)
```json
{
  "refresh_interval": 300,     # Auto-refresh time (seconds)
  "auto_refresh": true,        # Enable auto-refresh
  "ascii_mode": true,          # Default to ASCII mode
  "show_analytics": true,      # Include analytics section
  "show_progress_bars": true   # Display progress indicators
}
```

### Template Modification
- Edit `ascii-dashboard-template.txt` for ASCII layout changes
- Modify `dashboard-template.md` for markdown content
- Add new variables in `dash-enhanced.sh` variable generation function

---

## 🎮 Interactive Features

### Live Dashboard Mode
```bash
[dash:live]
# Features:
# - Updates every 5 seconds
# - Clear screen refresh  
# - Real-time metrics
# - Ctrl+C to exit
```

### Export System
```bash
[dash:export html]  # Creates timestamped HTML file
[dash:export pdf]   # Generates PDF (requires pandoc)
[dash:export txt]   # Plain text ASCII export
```

---

## 🚨 Troubleshooting

### Common Issues
- **Missing glow:** Install with `[package:install glow]`
- **Template variables showing:** Check variable generation in `dash-enhanced.sh`
- **Export failing:** Ensure pandoc installed for PDF export
- **Live mode stuck:** Use Ctrl+C to exit

### Debug Commands
```bash
# Check dashboard files
ls -la uMemory/dashboard/

# View generated variables  
cat uMemory/dashboard/variables.json

# Test template processing
./uCode/shortcode-processor-simple.sh process '[dash:config]'
```

---

## 📈 Metrics Explained

### Progress Bars
- **Daily Progress:** Completion of daily goals (missions, moves)
- **Mission Progress:** Active mission completion percentage  
- **Error Rate:** System error frequency (lower is better)
- **System Efficiency:** Overall uDOS performance metric

### Status Indicators
- 🟢 **Healthy:** All systems operational
- 🟡 **Warning:** Minor issues detected
- 🔴 **Critical:** Significant problems require attention

---

## 🎯 Best Practices

### Regular Usage
1. **Start each session:** `[dash:refresh]` for current status
2. **Quick checks:** `[dash:ascii]` during work
3. **End of day:** `[dash:analytics]` for summary
4. **Troubleshooting:** `[dash:config]` to verify settings

### Performance Optimization
- Use ASCII mode for fast updates
- Enable auto-refresh for background monitoring  
- Export dashboards for reports and documentation
- Combine with package and mission shortcodes for workflows

---

*Dashboard Quick Reference v2.0.0*  
*Enhanced with uTemplate & ASCII Integration*  
*Ready for production use*
