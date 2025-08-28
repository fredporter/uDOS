# uGET Milestone Setup Wizard

**Type**: Interactive Form
**Version**: v1.0.4.1
**Purpose**: Collect milestone configuration data for workflow tracking
**Generated**: {{timestamp}}
**Location**: uMEMORY/system/get/

> **Category**: Milestone Management
> **Output**: Milestone tracker and workflow integration
> **Integration**: Workflow manager, uDOT templates, mission system

---

## 📋 Milestone Configuration Form

[get:milestone_name]
question: Enter milestone title
type: text
required: true
validation: min:3,max:80
default: "New Milestone"
help: Descriptive name for this milestone achievement
[/get:milestone_name]

[get:milestone_type]
question: Milestone type
type: choice
options: ["deliverable", "capability", "process", "knowledge", "quality_gate"]
required: true
default: "deliverable"
help: Type of achievement this milestone represents
[/get:milestone_type]

[get:parent_mission]
question: Parent mission (if any)
type: text
required: false
validation: max:80
help: Mission this milestone contributes to
[/get:parent_mission]

[get:priority]
question: Milestone priority
type: choice
options: ["low", "medium", "high", "critical"]
required: true
default: "medium"
help: Importance level for resource allocation
[/get:priority]

[get:complexity]
question: Complexity level
type: choice
options: ["low", "medium", "high", "enterprise"]
required: true
default: "medium"
help: Expected difficulty and effort required
[/get:complexity]

[get:description]
question: Milestone description
type: textarea
required: true
validation: min:10,max:500
help: Clear description of what this milestone achieves
[/get:description]

[get:context]
question: Context and rationale
type: textarea
required: false
validation: max:300
help: Why this milestone is important
[/get:context]

[get:due_date]
question: Target completion date
type: date
required: false
validation: future_date
default: [date:+7days]
help: When should this milestone be achieved
[/get:due_date]

[get:estimated_effort]
question: Estimated effort
type: choice
options: ["1-2 hours", "half day", "1 day", "2-3 days", "1 week", "2+ weeks"]
required: true
default: "1 day"
help: Expected time investment to achieve milestone
[/get:estimated_effort]

[get:success_criteria_1]
question: Success criterion 1
type: text
required: true
validation: min:5,max:100
help: First key measure of milestone achievement
[/get:success_criteria_1]

[get:success_criteria_2]
question: Success criterion 2
type: text
required: false
validation: min:5,max:100
help: Second key measure of milestone achievement
[/get:success_criteria_2]

[get:deliverable_1]
question: Key deliverable 1
type: text
required: true
validation: min:3,max:100
help: Primary output or result from this milestone
[/get:deliverable_1]

[get:deliverable_2]
question: Key deliverable 2
type: text
required: false
validation: min:3,max:100
help: Secondary output or result from this milestone
[/get:deliverable_2]

[get:dependencies]
question: Dependencies (if any)
type: textarea
required: false
validation: max:200
help: What must be completed before this milestone
[/get:dependencies]

[get:resources_needed]
question: Resources required
type: textarea
required: false
validation: max:200
help: Tools, people, or materials needed
[/get:resources_needed]

[get:save_as_legacy]
question: Save as legacy when achieved?
type: boolean
required: true
default: false
help: Archive this milestone for future reference and learning
[/get:save_as_legacy]

[get:legacy_type]
question: Legacy type
type: choice
options: ["technique", "process", "innovation", "knowledge"]
required: false
conditional: [get:save_as_legacy] == true
default: "technique"
help: Type of legacy value this milestone will create
[/get:legacy_type]

[get:enable_tracking]
question: Enable progress tracking?
type: boolean
required: true
default: true
help: Track progress in workflow system
[/get:enable_tracking]

[get:quality_gates]
question: Quality gate required?
type: boolean
required: true
default: false
help: Does this milestone require formal review/approval
[/get:quality_gates]

[get:testing_required]
question: Testing strategy needed?
type: boolean
required: true
default: false
help: Does this milestone require formal testing
[/get:testing_required]

[get:additional_notes]
question: Additional notes
type: textarea
required: false
validation: max:200
help: Any other relevant milestone information
[/get:additional_notes]

---

## 🔄 Processing & Output

[process:variables]
milestone_id = [get:milestone_name] | slugify
milestone_filename = [timestamp]-[process:milestone_id]-milestone.md
workflow_filename = [timestamp]-[process:milestone_id]-milestone.json
creation_date = [date:iso]
success_criteria_list = [[get:success_criteria_1], [get:success_criteria_2]] | filter_empty
deliverables_list = [[get:deliverable_1], [get:deliverable_2]] | filter_empty
[/process:variables]

[output:milestone_tracker]
file: uMEMORY/milestones/[process:milestone_filename]
template: uDOT-milestone-tracker.md
variables: [get:*], [process:*]
[/output:milestone_tracker]

[output:workflow_milestone]
file: sandbox/workflow/milestones/[process:milestone_id].json
format: json
data: {
  "milestone_id": "[process:milestone_id]",
  "title": "[get:milestone_name]",
  "type": "[get:milestone_type]",
  "priority": "[get:priority]",
  "complexity": "[get:complexity]",
  "status": "planning",
  "created": "[process:creation_date]",
  "due_date": "[get:due_date]",
  "estimated_effort": "[get:estimated_effort]",
  "description": "[get:description]",
  "context": "[get:context]",
  "parent_mission": "[get:parent_mission]",
  "success_criteria": "[process:success_criteria_list]",
  "deliverables": "[process:deliverables_list]",
  "dependencies": "[get:dependencies]",
  "resources_needed": "[get:resources_needed]",
  "tracking_enabled": "[get:enable_tracking]",
  "quality_gates": "[get:quality_gates]",
  "testing_required": "[get:testing_required]",
  "save_as_legacy": "[get:save_as_legacy]",
  "legacy_type": "[get:legacy_type]",
  "progress_percentage": 0,
  "significance": "progress",
  "next_suggested_milestone": "Next Achievement",
  "contributes_to_mission": "[get:parent_mission]"
}
[/output:workflow_milestone]

---

## 🎯 Integration Points

- **Milestone Templates**: Uses uDOT-milestone-tracker.md for document generation
- **Workflow System**: Integrates with sandbox/workflow/ for tracking
- **Storage**: Saves to uMEMORY/milestones/ for permanent records
- **Mission Integration**: Links to parent missions when specified
- **Dashboard**: Milestone data available for dashboard display
- **Legacy System**: Optional preservation for achieved milestones

---

*uDOS v1.0.4.1 Milestone Setup Wizard - Workflow Integration System*
