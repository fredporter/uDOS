# uGET Smart Project Wizard

**Type**: Interactive Form
**Version**: v1.3.3
**Purpose**: Collect project configuration data through smart input validation
**Generated**: {{timestamp}}
**Location**: uMEMORY/system/get/

> **Category**: Project Management
> **Output**: Project configuration and documentation
> **Integration**: uDOT templates, uMEMORY storage

---

## 📋 Project Configuration Form

[get:project_title]
question: Enter project title
type: text
required: true
validation: min:3,max:100
default: "New Project"
help: Descriptive name for your project
[/get:project_title]

[get:project_version]
question: Initial version number
type: text
required: true
validation: semantic_version
default: "1.0.0"
help: Semantic version format (e.g., 1.0.0)
[/get:project_version]

[get:project_author]
question: Project author/owner
type: text
required: true
default: [user:name]
help: Primary project contact
[/get:project_author]

[get:project_priority]
question: Project priority level
type: choice
options: ["Low", "Medium", "High", "Critical"]
required: true
default: "Medium"
help: Business priority for resource allocation
[/get:project_priority]

[get:project_description]
question: Project description
type: textarea
required: true
validation: max:1000
help: Brief overview of project goals and deliverables
[/get:project_description]

[get:project_status]
question: Current project status
type: choice
options: ["Planning", "In Progress", "Review", "Complete", "On Hold"]
required: true
default: "Planning"
help: Current project lifecycle stage
[/get:project_status]

[get:project_due_date]
question: Target completion date
type: date
required: false
validation: future_date
default: [date:+30days]
help: Expected project completion date
[/get:project_due_date]

[get:project_budget]
question: Project budget (USD)
type: number
required: false
validation: min:0
default: 0
help: Total allocated budget for project
[/get:project_budget]

[get:team_size]
question: Team size
type: number
required: true
validation: min:1,max:50
default: 1
help: Number of team members involved
[/get:team_size]

[get:core_features_complete]
question: Core features defined?
type: boolean
required: true
default: false
help: Have core project features been identified?
[/get:core_features_complete]

[get:include_advanced_features]
question: Include advanced features?
type: boolean
required: true
default: true
help: Plan for advanced/optional features
[/get:include_advanced_features]

[get:advanced_requirements]
question: Advanced feature requirements
type: textarea
required: false
conditional: [get:include_advanced_features] == true
validation: max:500
help: Details about advanced features to implement
[/get:advanced_requirements]

[get:enable_notifications]
question: Enable project notifications?
type: boolean
required: true
default: true
help: Receive updates about project milestones
[/get:enable_notifications]

[get:stakeholder_updates]
question: Stakeholder update frequency
type: choice
options: ["Daily", "Weekly", "Bi-weekly", "Monthly"]
required: true
default: "Weekly"
help: How often to send status updates
[/get:stakeholder_updates]

[get:project_tags]
question: Project tags (comma-separated)
type: text
required: false
default: "documentation,project"
help: Tags for organizing and filtering projects
[/get:project_tags]

[get:project_requirements]
question: Key project requirements
type: textarea
required: true
validation: max:1000
help: Essential requirements and constraints
[/get:project_requirements]

[get:additional_notes]
question: Additional notes
type: textarea
required: false
validation: max:500
help: Any other relevant project information
[/get:additional_notes]

---

## 🔄 Processing & Output

[process:variables]
project_id = [get:project_title] | slugify
project_filename = [timestamp]-[get:project_id]-project.md
project_config_filename = [timestamp]-[get:project_id]-config.json
creation_date = [date:iso]
[/process:variables]

[output:project_document]
file: uMEMORY/projects/[process:project_filename]
template: uDOT-project-management.md
variables: [get:*], [process:*]
[/output:project_document]

[output:project_config]
file: uMEMORY/config/[process:project_config_filename]
format: json
data: {
  "project": {
    "id": "[process:project_id]",
    "title": "[get:project_title]",
    "version": "[get:project_version]",
    "author": "[get:project_author]",
    "priority": "[get:project_priority]",
    "status": "[get:project_status]",
    "created": "[process:creation_date]"
  },
  "configuration": {
    "budget": "[get:project_budget]",
    "team_size": "[get:team_size]",
    "due_date": "[get:project_due_date]",
    "notifications": "[get:enable_notifications]",
    "update_frequency": "[get:stakeholder_updates]"
  },
  "features": {
    "core_complete": "[get:core_features_complete]",
    "advanced_enabled": "[get:include_advanced_features]",
    "advanced_requirements": "[get:advanced_requirements]"
  }
}
[/output:project_config]

[output:task_checklist]
file: uMEMORY/tasks/[process:project_id]-checklist.md
content: |
# Project Checklist: [get:project_title]

## Setup Tasks
- [ ] Project kickoff meeting
- [ ] Requirements gathering complete
- [ ] Design phase started
- [ ] Development environment setup
- [ ] Team assignments finalized

## Development Tasks
- [ ] Core features implemented
- [ ] Advanced features (if enabled)
- [ ] Testing phase complete
- [ ] Documentation updated
- [ ] Code review completed

## Completion Tasks
- [ ] Stakeholder review
- [ ] Final testing
- [ ] Deployment preparation
- [ ] Project closure documentation
- [ ] Lessons learned captured
[/output:task_checklist]

---

## 🎯 Integration Points

- **Templates**: Uses uDOT-project-management.md for document generation
- **Storage**: Saves to uMEMORY/projects/ and uMEMORY/config/
- **Tasks**: Creates task checklist in uMEMORY/tasks/
- **Notifications**: Integrates with uDOS notification system
- **Dashboard**: Project data available for dashboard display

---

*uDOS v1.3.3 Smart Project Wizard - Interactive Form System*
