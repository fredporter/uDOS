# SYSTEM Command Reference

The `SYSTEM` command provides core system management and diagnostic functions for uDOS.

## Basic Usage

```bash
SYSTEM <subcommand> [options]
```

## Subcommands

### SYSTEM HELP
Display comprehensive help information.

```bash
SYSTEM HELP [category]
```

**Categories:**
- `SYSTEM` - System management commands
- `FILE` - File operations
- `ASSIST` - OK Assisted Task commands
- `MAP` - Navigation and mapping
- `OUTPUT` - Web server management

**Examples:**
```bash
SYSTEM HELP                 # All categories
SYSTEM HELP SYSTEM          # System commands only
SYSTEM HELP MAP             # Mapping commands only
```

### SYSTEM STATUS
Show system status and health information.

```bash
SYSTEM STATUS [--live]
```

**Features:**
- System information (OS, Python version)
- Memory usage and performance metrics
- Active processes and servers
- Configuration status
- Connection health

**Options:**
- `--live`: Real-time monitoring mode

### SYSTEM REPAIR
Diagnose and repair common system issues.

```bash
SYSTEM REPAIR [--auto]
```

**Diagnostic Checks:**
- Configuration file integrity
- Missing dependencies
- File permissions
- Database connectivity
- API key validation

**Options:**
- `--auto`: Automatically fix detected issues

### SYSTEM REBOOT
Restart uDOS system components.

```bash
SYSTEM REBOOT [--clean]
```

**Features:**
- Graceful shutdown of services
- Cache clearing
- Configuration reload
- Service restart

**Options:**
- `--clean`: Clear all caches and temporary files

### SYSTEM DESTROY
Emergency system reset with safety warnings.

```bash
SYSTEM DESTROY
```

⚠️ **WARNING**: This command requires confirmation and will:
- Stop all running services
- Clear all caches
- Reset to factory defaults
- Preserve user data in `/memory`

### SYSTEM PALETTE
Display color palette and test terminal colors.

```bash
SYSTEM PALETTE [test]
```

**Features:**
- Show all theme colors
- Test terminal color support
- Display color codes
- Verify theme consistency

**Options:**
- `test`: Run comprehensive color tests

## Advanced Commands

### SYSTEM TREE
Display repository structure and organization.

```bash
SYSTEM TREE [depth] [path]
```

**Examples:**
```bash
SYSTEM TREE                 # Full repository tree
SYSTEM TREE 2               # Limited to 2 levels deep
SYSTEM TREE 3 /core         # Core directory only
```

### SYSTEM DASHBOARD
Access system dashboard interface.

```bash
SYSTEM DASHBOARD [mode]
```

**Modes:**
- `CLI`: Command-line dashboard (default)
- `WEB`: Web-based dashboard

### SYSTEM CLEAN
Clean temporary files and caches.

```bash
SYSTEM CLEAN [target]
```

**Targets:**
- `cache`: Clear system caches
- `logs`: Archive old log files
- `temp`: Remove temporary files
- `all`: Complete cleanup

### SYSTEM CONFIG
Display system configuration.

```bash
SYSTEM CONFIG [section]
```

**Sections:**
- `env`: Environment variables
- `paths`: File system paths
- `services`: Service configuration
- `api`: API settings

### SYSTEM SETTINGS
Show user profile and preferences.

```bash
SYSTEM SETTINGS [category]
```

**Categories:**
- `profile`: User profile information
- `theme`: Theme and appearance
- `location`: Geographic settings
- `preferences`: General preferences

### SYSTEM SETUP
Display setup and installation guidance.

```bash
SYSTEM SETUP
```

**Provides:**
- Installation verification
- Dependency checking
- Configuration guidance
- First-run setup

### SYSTEM WORKSPACE
Manage workspace directories.

```bash
SYSTEM WORKSPACE [action] [path]
```

**Actions:**
- `list`: Show workspace directories
- `create`: Create new workspace
- `switch`: Change active workspace
- `clean`: Clean workspace files

## Configuration

### Health Monitoring
```bash
# Enable system monitoring
CONFIG set health_monitoring true
CONFIG set health_check_interval 60

# Set alert thresholds
CONFIG set memory_alert_threshold 80
CONFIG set disk_alert_threshold 90
```

### Repair Settings
```bash
# Auto-repair options
CONFIG set auto_repair_enabled true
CONFIG set auto_repair_backup true

# Diagnostic levels
CONFIG set diagnostic_level verbose
```

## Integration

### With Other Commands
```bash
# System health check before operations
SYSTEM STATUS
FILE BATCH DELETE *.tmp

# Repair after issues
SYSTEM REPAIR --auto
SYSTEM REBOOT --clean
```

### Monitoring Scripts
```bash
# Continuous monitoring
while true; do
    SYSTEM STATUS --live
    sleep 30
done
```

## Technical Details

### Implementation
- **Handler**: `SystemCommandHandler` in `core/commands/system_handler.py`
- **Services**: Integrates with all core services
- **Health**: Real-time system monitoring
- **Safety**: Confirmation prompts for destructive operations

### Health Metrics
- **Memory**: RAM usage and availability
- **Disk**: Storage usage and I/O
- **CPU**: Process load and performance
- **Network**: Connection status and latency
- **Services**: Service health and uptime

### Safety Features
- **Confirmation**: Required for destructive operations
- **Backup**: Automatic backup before repairs
- **Rollback**: Ability to undo system changes
- **Logging**: Complete audit trail of actions

## Error Handling

### Common Issues
1. **Permission Denied**: Run with appropriate permissions
2. **Service Unavailable**: Check service status
3. **Configuration Error**: Use `SYSTEM REPAIR`
4. **Memory Issues**: Monitor with `SYSTEM STATUS`

### Recovery Commands
```bash
SYSTEM REPAIR               # Fix configuration issues
SYSTEM REBOOT --clean       # Restart with clean state
SYSTEM DESTROY              # Nuclear option (emergency only)
```

## Examples

### Daily Health Check
```bash
# Quick system overview
SYSTEM STATUS
SYSTEM CONFIG
SYSTEM WORKSPACE list
```

### Troubleshooting Workflow
```bash
# Diagnose issues
SYSTEM STATUS --live
SYSTEM REPAIR

# If issues persist
SYSTEM REBOOT --clean

# Emergency recovery
SYSTEM DESTROY
SYSTEM SETUP
```

### Development Workflow
```bash
# Before development
SYSTEM STATUS
SYSTEM TREE 2

# During development
SYSTEM PALETTE test
SYSTEM DASHBOARD CLI

# After development
SYSTEM CLEAN cache
SYSTEM STATUS
```

## Security

### Safe Operations
- All destructive commands require confirmation
- Automatic backups before major changes
- User data preservation in `/memory`
- Audit logging of all system operations

### Access Control
- Commands respect file system permissions
- Service operations require appropriate access
- Configuration changes are validated
- Emergency stops are always available

## Performance

### Optimization
- Lazy loading of system information
- Cached status for frequent queries
- Efficient health monitoring
- Minimal resource overhead

### Monitoring
- Real-time performance metrics
- Historical trend analysis
- Alert thresholds and notifications
- Automated cleanup routines

## Tags
#system #management #health #diagnostics #repair #status #configuration
