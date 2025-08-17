# uDEV Workflow System v1.3

```ascii
    ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗███████╗██╗      ██████╗ ██╗    ██╗
    ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║
    ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║
    ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██╔══╝  ██║     ██║   ██║██║███╗██║
    ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██║     ███████╗╚██████╔╝╚███╔███╔╝
     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ 

    Development Workflow Management System
    ═══════════════════════════════════════════════════════════════════════════════════════
```

**Version**: 1.3.0  
**Date**: August 17, 2025  
**Type**: uDEV System Documentation  
**Status**: Production Ready

---

## 🎯 Workflow System Overview

The uDEV Workflow System provides:
- **Ordered Script Execution**: Run cleanup and maintenance scripts in sequence
- **Automatic Filing**: Archive completed scripts with proper naming
- **Comprehensive Logging**: Track all workflow activities
- **State Management**: Resume workflows and handle failures
- **Template Integration**: Generate reports and documentation

---

## 📁 Directory Structure

```
uDEV/
├── workflows/                    # Workflow definitions and queues
│   ├── active/                  # Currently running workflows
│   ├── pending/                 # Queued workflows waiting to run
│   ├── completed/               # Successfully completed workflows
│   ├── failed/                  # Failed workflows for review
│   └── templates/               # Workflow template definitions
├── scripts/                     # Development scripts organized by type
│   ├── cleanup/                 # File and directory cleanup scripts
│   ├── maintenance/             # System maintenance scripts
│   ├── migration/               # Data migration and conversion scripts
│   ├── validation/              # Testing and validation scripts
│   └── archive/                 # Completed and filed scripts
├── logs/                        # Workflow execution logs
│   ├── daily/                   # Daily activity logs
│   ├── workflows/               # Individual workflow logs
│   └── system/                  # System-level logging
├── reports/                     # Generated workflow reports
│   ├── summaries/               # Workflow completion summaries
│   ├── metrics/                 # Performance and timing metrics
│   └── analysis/                # Workflow analysis and optimization
└── tools/                       # Workflow management tools
    ├── workflow-manager.sh      # Main workflow orchestration
    ├── script-executor.sh       # Individual script runner
    ├── file-organizer.sh        # Automatic filing system
    └── report-generator.sh      # Documentation generator
```

---

## 🔧 Core Components

### 1. Workflow Manager (`workflow-manager.sh`)
Central orchestration system that:
- Reads workflow definitions
- Manages execution order
- Handles dependencies
- Provides status monitoring
- Generates completion reports

### 2. Script Executor (`script-executor.sh`)
Individual script runner that:
- Executes scripts with proper logging
- Captures output and errors
- Tracks execution time
- Manages script state
- Handles cleanup on completion

### 3. File Organizer (`file-organizer.sh`)
Automatic filing system that:
- Archives completed scripts
- Applies proper naming conventions
- Organizes by date and type
- Maintains execution history
- Creates reference documentation

### 4. Report Generator (`report-generator.sh`)
Documentation system that:
- Creates workflow summaries
- Generates performance reports
- Produces maintenance documentation
- Updates system status
- Archives historical data

---

## 📋 Workflow Definition Format

### Workflow Configuration (`workflow.json`)
```json
{
  "workflow_id": "cleanup-maintenance-v1",
  "name": "Daily Cleanup and Maintenance",
  "description": "Standard cleanup scripts for file organization",
  "version": "1.0",
  "created": "2025-08-17",
  "author": "uDEV System",
  "priority": "normal",
  "schedule": "daily",
  "dependencies": [],
  "scripts": [
    {
      "id": "001",
      "name": "cleanup-filenames.sh",
      "description": "Clean up incorrectly named files",
      "type": "cleanup",
      "timeout": 300,
      "retry_count": 2,
      "critical": true
    },
    {
      "id": "002", 
      "name": "reorganize-dev-files.sh",
      "description": "Reorganize development files",
      "type": "maintenance",
      "timeout": 600,
      "retry_count": 1,
      "critical": false,
      "depends_on": ["001"]
    }
  ],
  "post_actions": [
    "generate_report",
    "archive_logs",
    "update_status"
  ]
}
```

### Script Metadata (`script-meta.json`)
```json
{
  "script_name": "cleanup-filenames.sh",
  "version": "1.2",
  "type": "cleanup",
  "category": "file-management",
  "description": "Cleans up incorrectly named development files",
  "author": "uDEV System",
  "created": "2025-08-17",
  "last_modified": "2025-08-17",
  "execution_time_avg": 45,
  "success_rate": 0.98,
  "dependencies": [],
  "parameters": {
    "target_directory": "/Users/agentdigital/uDOS/uDEV/summaries",
    "backup_enabled": true,
    "dry_run": false
  }
}
```

---

## 🚀 Usage Examples

### Basic Workflow Execution
```bash
# Run a single workflow
./tools/workflow-manager.sh run cleanup-maintenance-v1

# Run with specific parameters
./tools/workflow-manager.sh run cleanup-maintenance-v1 --dry-run --verbose

# Schedule recurring workflow
./tools/workflow-manager.sh schedule cleanup-maintenance-v1 daily

# Check workflow status
./tools/workflow-manager.sh status cleanup-maintenance-v1
```

### Script Management
```bash
# Execute individual script
./tools/script-executor.sh cleanup/cleanup-filenames.sh

# Archive completed script
./tools/file-organizer.sh archive cleanup-filenames.sh

# Generate script report
./tools/report-generator.sh script cleanup-filenames.sh
```

### System Monitoring
```bash
# View active workflows
./tools/workflow-manager.sh list --status active

# Check system health
./tools/workflow-manager.sh health

# Generate daily report
./tools/report-generator.sh daily-summary
```

---

## 📊 Logging and Monitoring

### Log File Naming Convention
```
uDEV/logs/workflows/uLOG-YYYYMMDD-HHMM-TZ-WORKFLOW.md
uDEV/logs/daily/uLOG-YYYYMMDD-TZ-DAILY.md
uDEV/logs/system/uLOG-YYYYMMDD-HHMM-TZ-SYSTEM.md
```

### Log Structure
```markdown
# Workflow Execution Log

**Workflow**: cleanup-maintenance-v1  
**Start Time**: 2025-08-17 14:30:00  
**Status**: COMPLETED  
**Duration**: 125 seconds  

## Script Execution Summary

| Script | Status | Duration | Exit Code | Notes |
|--------|--------|----------|-----------|-------|
| cleanup-filenames.sh | ✅ SUCCESS | 45s | 0 | 12 files renamed |
| reorganize-dev-files.sh | ✅ SUCCESS | 80s | 0 | 3 directories organized |

## Performance Metrics
- Total Files Processed: 15
- Total Size Processed: 2.3MB
- Memory Usage Peak: 45MB
- CPU Usage Average: 12%

## Post-Execution Actions
✅ Report generated: reports/summaries/cleanup-maintenance-v1-20250817.md  
✅ Logs archived: logs/workflows/uLOG-20250817-1430-28-WORKFLOW01.md  
✅ Status updated: System status reflects completion  

## Recommendations
- Consider optimizing cleanup-filenames.sh for larger datasets
- Add validation step for reorganize-dev-files.sh
```

---

## 🔄 Workflow States

### State Lifecycle
```
PENDING → QUEUED → RUNNING → [COMPLETED|FAILED] → ARCHIVED
```

### State Descriptions
- **PENDING**: Workflow defined but not scheduled
- **QUEUED**: Scheduled and waiting for execution slot
- **RUNNING**: Currently executing scripts
- **COMPLETED**: All scripts executed successfully
- **FAILED**: One or more scripts failed execution
- **ARCHIVED**: Completed workflow filed away

### State Transitions
```bash
# Manual state management
./tools/workflow-manager.sh set-state workflow-id QUEUED
./tools/workflow-manager.sh retry failed-workflow-id
./tools/workflow-manager.sh archive completed-workflow-id
```

---

## 📈 Metrics and Reporting

### Daily Summary Report
```markdown
# uDEV Daily Activity Summary

**Date**: August 17, 2025  
**Workflows Executed**: 3  
**Scripts Run**: 8  
**Success Rate**: 100%  
**Total Processing Time**: 342 seconds  

## Workflow Summary
| Workflow | Scripts | Duration | Status |
|----------|---------|----------|--------|
| cleanup-maintenance-v1 | 2 | 125s | ✅ SUCCESS |
| validation-suite-v2 | 4 | 180s | ✅ SUCCESS |
| backup-routine-v1 | 2 | 37s | ✅ SUCCESS |

## Files Processed
- **Renamed**: 15 files
- **Organized**: 8 directories  
- **Archived**: 23 scripts
- **Generated**: 5 reports

## System Health
- **Memory Usage**: Normal (avg 67MB)
- **Disk Usage**: Normal (2.1GB available)
- **Performance**: Optimal (avg 15% CPU)

## Recommendations
- Schedule cleanup-maintenance-v1 to run twice daily
- Consider implementing parallel execution for validation-suite-v2
- Archive logs older than 30 days
```

---

## 🛠️ Advanced Features

### Parallel Execution
```json
{
  "execution_mode": "parallel",
  "max_concurrent": 3,
  "scripts": [
    {
      "id": "001",
      "name": "cleanup-task-1.sh",
      "parallel_group": "cleanup"
    },
    {
      "id": "002", 
      "name": "cleanup-task-2.sh",
      "parallel_group": "cleanup"
    }
  ]
}
```

### Conditional Execution
```json
{
  "scripts": [
    {
      "id": "001",
      "name": "check-conditions.sh",
      "conditions": {
        "file_exists": "/path/to/trigger/file",
        "disk_space_gb": 1.0,
        "time_since_last_run": "24h"
      }
    }
  ]
}
```

### Integration Hooks
```json
{
  "hooks": {
    "pre_workflow": ["backup-current-state.sh"],
    "post_script": ["validate-output.sh"],
    "post_workflow": ["cleanup-temp-files.sh"],
    "on_failure": ["send-notification.sh", "rollback-changes.sh"]
  }
}
```

---

## 🔧 Installation and Setup

### Initial Setup
```bash
# Initialize workflow system
cd /Users/agentdigital/uDOS/uDEV
./tools/workflow-manager.sh init

# Create default workflows
./tools/workflow-manager.sh create-template cleanup-maintenance
./tools/workflow-manager.sh create-template validation-suite

# Set up scheduling
./tools/workflow-manager.sh enable-scheduler
```

### Configuration
```bash
# Configure system settings
./tools/workflow-manager.sh config set max_concurrent_workflows 3
./tools/workflow-manager.sh config set log_retention_days 30
./tools/workflow-manager.sh config set enable_notifications true
```

---

This workflow system provides a robust foundation for managing development scripts with proper execution order, comprehensive logging, and automatic filing. The system is designed to scale with the uDOS development process while maintaining clean organization and detailed audit trails.

---

*uDEV Workflow System v1.3 - Development Environment Management*  
*Universal Data Operating System Project*  
*August 2025*
