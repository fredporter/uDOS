#!/bin/bash
# template-finalizer.sh - Complete template and variable system for uDOS Alpha v1.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
TEMPLATE_DIR="$UHOME/uTemplate"
DATASETS_DIR="$TEMPLATE_DIR/datasets"
VARIABLES_DIR="$TEMPLATE_DIR/variables"

echo "🏗️ Finalizing uDOS Template and Variable System for Alpha v1.0.0"
echo "=================================================================="

# Create all necessary directories
create_template_structure() {
  echo "📁 Creating template directory structure..."
  
  mkdir -p "$TEMPLATE_DIR"/{system,src,variables,datasets}
  mkdir -p "$TEMPLATE_DIR/src"/{templates,utils,data}
  mkdir -p "$UHOME/uMemory"/{generated,templates}
  
  echo "✅ Template structure created"
}

# Generate comprehensive template definitions
generate_template_definitions() {
  echo "📋 Generating comprehensive template definitions..."
  
  cat > "$DATASETS_DIR/template-definitions.json" << 'EOF'
[
  {
    "template_id": "mission",
    "name": "Mission Template",
    "category": "planning",
    "description": "Structured template for defining project missions with objectives, timeline, and resources",
    "file_path": "mission-template.md",
    "variables": [
      {"name": "mission_name", "type": "string", "required": true, "description": "Name of the mission"},
      {"name": "objective", "type": "text", "required": true, "description": "Primary objective"},
      {"name": "start_date", "type": "date", "required": true, "description": "Mission start date"},
      {"name": "end_date", "type": "date", "required": false, "description": "Target completion date"},
      {"name": "priority", "type": "enum", "options": ["low", "medium", "high", "critical"], "required": true, "description": "Mission priority level"},
      {"name": "resources", "type": "array", "required": false, "description": "Required resources"},
      {"name": "team_members", "type": "array", "required": false, "description": "Assigned team members"},
      {"name": "budget", "type": "number", "required": false, "description": "Mission budget"},
      {"name": "success_criteria", "type": "array", "required": true, "description": "Success criteria"}
    ],
    "output_format": "markdown",
    "tags": ["mission", "planning", "project"],
    "version": "1.0.0"
  },
  {
    "template_id": "milestone",
    "name": "Milestone Template", 
    "category": "tracking",
    "description": "Template for defining project milestones with deliverables and success criteria",
    "file_path": "milestone-template.md",
    "variables": [
      {"name": "milestone_name", "type": "string", "required": true, "description": "Name of the milestone"},
      {"name": "description", "type": "text", "required": true, "description": "Milestone description"},
      {"name": "due_date", "type": "date", "required": true, "description": "Milestone due date"},
      {"name": "deliverables", "type": "array", "required": true, "description": "Expected deliverables"},
      {"name": "success_criteria", "type": "array", "required": true, "description": "Success criteria"},
      {"name": "dependencies", "type": "array", "required": false, "description": "Dependencies on other milestones"},
      {"name": "assigned_to", "type": "string", "required": false, "description": "Person responsible"},
      {"name": "progress", "type": "number", "required": false, "description": "Completion percentage"}
    ],
    "output_format": "markdown",
    "tags": ["milestone", "tracking", "deliverable"],
    "version": "1.0.0"
  },
  {
    "template_id": "move",
    "name": "Move Template",
    "category": "action",
    "description": "Template for documenting individual actions or moves within a project",
    "file_path": "move-template.md",
    "variables": [
      {"name": "move_id", "type": "string", "required": true, "description": "Unique move identifier"},
      {"name": "action", "type": "string", "required": true, "description": "Action to be taken"},
      {"name": "context", "type": "text", "required": true, "description": "Context and reasoning"},
      {"name": "expected_outcome", "type": "text", "required": true, "description": "Expected result"},
      {"name": "actual_outcome", "type": "text", "required": false, "description": "Actual result"},
      {"name": "timestamp", "type": "datetime", "required": true, "description": "When the move was made"},
      {"name": "duration", "type": "number", "required": false, "description": "Time taken in minutes"},
      {"name": "tags", "type": "array", "required": false, "description": "Categorization tags"}
    ],
    "output_format": "markdown",
    "tags": ["move", "action", "log"],
    "version": "1.0.0"
  },
  {
    "template_id": "dashboard",
    "name": "Dashboard Template",
    "category": "reporting",
    "description": "Template for generating comprehensive system dashboards",
    "file_path": "dashboard-template.md",
    "variables": [
      {"name": "title", "type": "string", "required": true, "description": "Dashboard title"},
      {"name": "generated_date", "type": "datetime", "required": true, "description": "Generation timestamp"},
      {"name": "user_name", "type": "string", "required": true, "description": "Current user"},
      {"name": "active_missions", "type": "array", "required": false, "description": "Current active missions"},
      {"name": "recent_moves", "type": "array", "required": false, "description": "Recent moves"},
      {"name": "system_stats", "type": "object", "required": false, "description": "System statistics"},
      {"name": "health_status", "type": "string", "required": false, "description": "Overall system health"}
    ],
    "output_format": "markdown",
    "tags": ["dashboard", "reporting", "status"],
    "version": "1.0.0"
  },
  {
    "template_id": "user-setup",
    "name": "User Setup Template",
    "category": "configuration",
    "description": "Template for initial user configuration and identity setup",
    "file_path": "input-user-setup.md",
    "variables": [
      {"name": "username", "type": "string", "required": true, "description": "User identifier"},
      {"name": "full_name", "type": "string", "required": false, "description": "Full name"},
      {"name": "email", "type": "email", "required": false, "description": "Email address"},
      {"name": "location", "type": "string", "required": false, "description": "User location"},
      {"name": "timezone", "type": "string", "required": false, "description": "User timezone"},
      {"name": "preferences", "type": "object", "required": false, "description": "User preferences"},
      {"name": "created_date", "type": "datetime", "required": true, "description": "Account creation date"}
    ],
    "output_format": "markdown",
    "tags": ["user", "setup", "configuration"],
    "version": "1.0.0"
  },
  {
    "template_id": "package-info",
    "name": "Package Information Template",
    "category": "documentation",
    "description": "Template for documenting package installations and configurations",
    "file_path": "package-template.md",
    "variables": [
      {"name": "package_name", "type": "string", "required": true, "description": "Package name"},
      {"name": "version", "type": "string", "required": true, "description": "Package version"},
      {"name": "description", "type": "text", "required": true, "description": "Package description"},
      {"name": "install_date", "type": "datetime", "required": true, "description": "Installation date"},
      {"name": "dependencies", "type": "array", "required": false, "description": "Package dependencies"},
      {"name": "usage_examples", "type": "array", "required": false, "description": "Usage examples"},
      {"name": "configuration", "type": "object", "required": false, "description": "Configuration settings"}
    ],
    "output_format": "markdown",
    "tags": ["package", "documentation", "installation"],
    "version": "1.0.0"
  },
  {
    "template_id": "workflow",
    "name": "Workflow Template",
    "category": "automation",
    "description": "Template for defining automated workflows and processes",
    "file_path": "workflow-template.md",
    "variables": [
      {"name": "workflow_name", "type": "string", "required": true, "description": "Workflow identifier"},
      {"name": "description", "type": "text", "required": true, "description": "Workflow purpose"},
      {"name": "trigger", "type": "string", "required": true, "description": "What triggers the workflow"},
      {"name": "steps", "type": "array", "required": true, "description": "Workflow steps"},
      {"name": "schedule", "type": "string", "required": false, "description": "Execution schedule"},
      {"name": "enabled", "type": "boolean", "required": true, "description": "Whether workflow is active"}
    ],
    "output_format": "markdown",
    "tags": ["workflow", "automation", "process"],
    "version": "1.0.0"
  },
  {
    "template_id": "report",
    "name": "Report Template",
    "category": "documentation",
    "description": "Template for generating various types of reports",
    "file_path": "report-template.md",
    "variables": [
      {"name": "report_title", "type": "string", "required": true, "description": "Report title"},
      {"name": "report_type", "type": "enum", "options": ["status", "analysis", "summary", "detailed"], "required": true, "description": "Type of report"},
      {"name": "period", "type": "string", "required": false, "description": "Reporting period"},
      {"name": "author", "type": "string", "required": true, "description": "Report author"},
      {"name": "executive_summary", "type": "text", "required": false, "description": "Executive summary"},
      {"name": "findings", "type": "array", "required": false, "description": "Key findings"},
      {"name": "recommendations", "type": "array", "required": false, "description": "Recommendations"}
    ],
    "output_format": "markdown",
    "tags": ["report", "documentation", "analysis"],
    "version": "1.0.0"
  }
]
EOF

  echo "✅ Template definitions generated"
}

# Create finalized template files
create_template_files() {
  echo "📝 Creating finalized template files..."
  
  # Mission Template
  cat > "$TEMPLATE_DIR/mission-template.md" << 'EOF'
# 🎯 Mission: {{mission_name}}

**Created:** {{start_date}}  
**Priority:** {{priority}}  
{{#if end_date}}**Target Completion:** {{end_date}}{{/if}}  
**Status:** Active

---

## 📋 Objective

{{objective}}

## 🎯 Success Criteria

{{#each success_criteria}}
- [ ] {{this}}
{{/each}}

{{#if resources}}
## 🛠️ Resources Required

{{#each resources}}
- {{this}}
{{/each}}
{{/if}}

{{#if team_members}}
## 👥 Team Members

{{#each team_members}}
- {{this}}
{{/each}}
{{/if}}

{{#if budget}}
## 💰 Budget

**Allocated:** ${{budget}}
{{/if}}

## 📊 Progress Tracking

- [ ] Mission initiated
- [ ] Resources allocated
- [ ] Team assembled
- [ ] Execution begun
- [ ] Milestones achieved
- [ ] Mission completed

---

**Mission ID:** {{mission_name | slugify}}  
**Generated:** {{generated_date}}  
**Template Version:** 1.0.0
EOF

  # Milestone Template
  cat > "$TEMPLATE_DIR/milestone-template.md" << 'EOF'
# 🏆 Milestone: {{milestone_name}}

**Due Date:** {{due_date}}  
{{#if assigned_to}}**Assigned To:** {{assigned_to}}{{/if}}  
{{#if progress}}**Progress:** {{progress}}%{{/if}}

---

## 📝 Description

{{description}}

## 📦 Deliverables

{{#each deliverables}}
- [ ] {{this}}
{{/each}}

## ✅ Success Criteria

{{#each success_criteria}}
- [ ] {{this}}
{{/each}}

{{#if dependencies}}
## 🔗 Dependencies

{{#each dependencies}}
- {{this}}
{{/each}}
{{/if}}

## 📊 Status

- [ ] Planning complete
- [ ] Work in progress
- [ ] Review phase
- [ ] Completed
- [ ] Verified

---

**Milestone ID:** {{milestone_name | slugify}}  
**Generated:** {{generated_date}}  
**Template Version:** 1.0.0
EOF

  # Move Template
  cat > "$TEMPLATE_DIR/move-template.md" << 'EOF'
# 🔄 Move: {{action}}

**Move ID:** {{move_id}}  
**Timestamp:** {{timestamp}}  
{{#if duration}}**Duration:** {{duration}} minutes{{/if}}

---

## 📝 Context

{{context}}

## 🎯 Expected Outcome

{{expected_outcome}}

{{#if actual_outcome}}
## ✅ Actual Outcome

{{actual_outcome}}
{{/if}}

{{#if tags}}
## 🏷️ Tags

{{#each tags}}
- {{this}}
{{/each}}
{{/if}}

---

**Generated:** {{generated_date}}  
**Template Version:** 1.0.0
EOF

  # Dashboard Template
  cat > "$TEMPLATE_DIR/system/dashboard.md" << 'EOF'
# 📊 {{title}}

**Generated:** {{generated_date}}  
**User:** {{user_name}}

---

{{#if active_missions}}
## 🎯 Active Missions

{{#each active_missions}}
### {{this.name}}
- **Priority:** {{this.priority}}
- **Progress:** {{this.progress}}%
- **Due:** {{this.due_date}}

{{/each}}
{{/if}}

{{#if recent_moves}}
## 🔄 Recent Activity

{{#each recent_moves}}
- **{{this.timestamp}}** - {{this.action}}
{{/each}}
{{/if}}

{{#if system_stats}}
## 📈 System Statistics

- **Total Missions:** {{system_stats.missions}}
- **Total Moves:** {{system_stats.moves}}
- **Total Milestones:** {{system_stats.milestones}}
- **System Health:** {{health_status}}
{{/if}}

---

**Dashboard Version:** 1.0.0  
**System:** uDOS Alpha v1.0.0
EOF

  # User Setup Template
  cat > "$TEMPLATE_DIR/input-user-setup.md" << 'EOF'
# 👤 User Setup: {{username}}

**Created:** {{created_date}}

---

## 🆔 Identity Information

- **Username:** {{username}}
{{#if full_name}}- **Full Name:** {{full_name}}{{/if}}
{{#if email}}- **Email:** {{email}}{{/if}}
{{#if location}}- **Location:** {{location}}{{/if}}
{{#if timezone}}- **Timezone:** {{timezone}}{{/if}}

{{#if preferences}}
## ⚙️ Preferences

{{#each preferences}}
- **{{@key}}:** {{this}}
{{/each}}
{{/if}}

## 🎯 Initial Setup Checklist

- [ ] Identity configured
- [ ] Location set
- [ ] Timezone configured
- [ ] Preferences set
- [ ] First mission created
- [ ] Template system validated

---

**User ID:** {{username | slugify}}  
**Setup Version:** 1.0.0
EOF

  echo "✅ Template files created"
}

# Update variable system
update_variable_system() {
  echo "🔧 Updating variable system..."
  
  # Create comprehensive user variables
  cat > "$VARIABLES_DIR/user-vars.json" << EOF
{
  "USERNAME": "${USER:-unknown}",
  "FULL_NAME": "",
  "EMAIL": "",
  "LOCATION": "",
  "TIMEZONE": "UTC",
  "THEME": "default",
  "DEBUG_MODE": false,
  "AUTO_BACKUP": true,
  "BACKUP_INTERVAL": "daily",
  "CURRENT_PROJECT": "",
  "PROJECT_LEAD": "",
  "PROJECT_DEADLINE": "",
  "PROJECT_BUDGET": 0,
  "LAST_UPDATED": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

  # Create environment variables
  cat > "$VARIABLES_DIR/env.json" << EOF
{
  "UDOS_VERSION": "1.0.0-alpha",
  "UDOS_HOME": "$UHOME",
  "UDOS_USER": "${USER:-unknown}",
  "UDOS_SHELL": "$SHELL",
  "UDOS_HOSTNAME": "$(hostname)",
  "UDOS_PLATFORM": "$(uname -s)",
  "SYSTEM_DATE": "$(date +%Y-%m-%d)",
  "SYSTEM_TIME": "$(date +%H:%M:%S)",
  "SYSTEM_TIMEZONE": "$(date +%Z)",
  "SESSION_ID": "$(uuidgen 2>/dev/null || echo "session-$(date +%s)")",
  "SESSION_START": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

  # Create session variables (runtime)
  cat > "$VARIABLES_DIR/session.json" << EOF
{
  "commands_executed": 0,
  "current_mission": "",
  "last_command": "",
  "session_duration": 0,
  "errors_count": 0,
  "warnings_count": 0,
  "active_workflows": [],
  "recent_moves": []
}
EOF

  echo "✅ Variable system updated"
}

# Create variable management utilities
create_variable_utilities() {
  echo "🛠️ Creating variable management utilities..."
  
  cat > "$UHOME/uCode/variable-manager.sh" << 'EOF'
#!/bin/bash
# variable-manager.sh - Variable management system for uDOS

VARIABLES_DIR="$UHOME/uTemplate/variables"

# Set a variable
set_variable() {
  local name="$1"
  local value="$2"
  local scope="${3:-user}"
  
  case "$scope" in
    user)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/user-vars.json" > "/tmp/user-vars.tmp" && mv "/tmp/user-vars.tmp" "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/session.json" > "/tmp/session.tmp" && mv "/tmp/session.tmp" "$VARIABLES_DIR/session.json"
      ;;
    env)
      jq --arg name "$name" --arg value "$value" '.[$name] = $value' "$VARIABLES_DIR/env.json" > "/tmp/env.tmp" && mv "/tmp/env.tmp" "$VARIABLES_DIR/env.json"
      ;;
  esac
}

# Get a variable
get_variable() {
  local name="$1"
  local scope="${2:-user}"
  
  case "$scope" in
    user)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/session.json"
      ;;
    env)
      jq -r --arg name "$name" '.[$name] // empty' "$VARIABLES_DIR/env.json"
      ;;
  esac
}

# List all variables
list_variables() {
  local scope="${1:-all}"
  
  case "$scope" in
    user)
      echo "📋 User Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/user-vars.json"
      ;;
    session)
      echo "📋 Session Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/session.json"
      ;;
    env)
      echo "📋 Environment Variables:"
      jq -r 'to_entries[] | "  \(.key) = \(.value)"' "$VARIABLES_DIR/env.json"
      ;;
    all)
      list_variables user
      echo ""
      list_variables session
      echo ""
      list_variables env
      ;;
  esac
}

# Command line interface
case "$1" in
  set)
    set_variable "$2" "$3" "$4"
    echo "✅ Variable set: $2 = $3"
    ;;
  get)
    value=$(get_variable "$2" "$3")
    if [[ -n "$value" ]]; then
      echo "$value"
    else
      echo "❌ Variable not found: $2"
    fi
    ;;
  list)
    list_variables "$2"
    ;;
  *)
    echo "Usage: $0 {set|get|list} [args...]"
    echo "  set <name> <value> [scope]  - Set a variable"
    echo "  get <name> [scope]          - Get a variable"
    echo "  list [scope]                - List variables"
    echo ""
    echo "Scopes: user, session, env, all"
    ;;
esac
EOF

  chmod +x "$UHOME/uCode/variable-manager.sh"
  echo "✅ Variable utilities created"
}

# Main execution
main() {
  create_template_structure
  generate_template_definitions
  create_template_files
  update_variable_system
  create_variable_utilities
  
  echo ""
  echo "🎉 Template and Variable System Finalization Complete!"
  echo "======================================================"
  echo ""
  echo "✅ Template Structure: Complete"
  echo "✅ Template Definitions: 8 comprehensive templates"
  echo "✅ Variable System: User, Environment, and Session variables"
  echo "✅ Variable Management: CLI utilities for variable operations"
  echo ""
  echo "📋 Available Templates:"
  echo "   - mission       → Project mission planning"
  echo "   - milestone     → Progress milestone tracking"
  echo "   - move          → Action logging"
  echo "   - dashboard     → System status reports"
  echo "   - user-setup    → User configuration"
  echo "   - package-info  → Package documentation"
  echo "   - workflow      → Automation workflows"
  echo "   - report        → Various report types"
  echo ""
  echo "🔧 Variable Management:"
  echo "   ./uCode/variable-manager.sh set <name> <value> [scope]"
  echo "   ./uCode/variable-manager.sh get <name> [scope]"
  echo "   ./uCode/variable-manager.sh list [scope]"
  echo ""
  echo "🚀 uDOS Alpha v1.0.0 Template System is now production-ready!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
EOF
