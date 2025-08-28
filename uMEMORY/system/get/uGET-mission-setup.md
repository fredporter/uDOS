# uGET Mission Setup Wizard

**Type**: Interactive Form
**Version**: v1.0.4.1
**Purpose**: Collect mission configuration data for workflow management
**Generated**: {{timestamp}}
**Location**: uMEMORY/system/get/

> **Category**: Mission Management
> **Output**: Mission brief and workflow integration
> **Integration**: Workflow manager, uDOT templates, uMEMORY storage

---

## 📋 Mission Configuration Form

[get:mission_name]
question: Enter mission title
type: text
required: true
validation: min:3,max:80
default: "New Mission"
help: Descriptive name for your mission
[/get:mission_name]

[get:mission_type]
question: Mission type
type: choice
options: ["development", "research", "deployment", "maintenance", "enhancement", "learning"]
required: true
default: "development"
help: Primary category of mission work
[/get:mission_type]

[get:priority]
question: Mission priority level
type: choice
options: ["low", "medium", "high", "critical"]
required: true
default: "medium"
help: Business/personal priority for resource allocation
[/get:priority]

[get:complexity]
question: Mission complexity
type: choice
options: ["low", "medium", "high", "enterprise"]
required: true
default: "medium"
help: Expected technical and organizational complexity
[/get:complexity]

[get:objective]
question: Primary mission objective
type: textarea
required: true
validation: min:10,max:500
help: Clear description of what you want to achieve
[/get:objective]

[get:context]
question: Mission context and background
type: textarea
required: false
validation: max:500
help: Background information and reasoning for this mission
[/get:context]

[get:estimated_duration]
question: Estimated duration
type: choice
options: ["1-3 days", "1 week", "2-3 weeks", "1 month", "2-3 months", "longer"]
required: true
default: "1 week"
help: Expected time to complete mission
[/get:estimated_duration]

[get:start_date]
question: Mission start date
type: date
required: false
default: [date:today]
help: When should this mission begin
[/get:start_date]

[get:end_date]
question: Target completion date
type: date
required: false
validation: future_date
default: [date:+7days]
help: Target mission completion date
[/get:end_date]

[get:success_criteria_1]
question: Success criterion 1
type: text
required: true
validation: min:5,max:100
help: First key measure of mission success
[/get:success_criteria_1]

[get:success_criteria_2]
question: Success criterion 2
type: text
required: false
validation: min:5,max:100
help: Second key measure of mission success
[/get:success_criteria_2]

[get:success_criteria_3]
question: Success criterion 3
type: text
required: false
validation: min:5,max:100
help: Third key measure of mission success
[/get:success_criteria_3]

[get:resources_needed]
question: Key resources required
type: textarea
required: false
validation: max:300
help: Tools, people, or materials needed for success
[/get:resources_needed]

[get:save_as_legacy]
question: Save as legacy when completed?
type: boolean
required: true
default: false
help: Archive this mission for future reference and learning
[/get:save_as_legacy]

[get:legacy_category]
question: Legacy category
type: choice
options: ["achievement", "knowledge", "innovation", "improvement"]
required: false
conditional: [get:save_as_legacy] == true
default: "achievement"
help: Type of legacy value this mission will create
[/get:legacy_category]

[get:team_size]
question: Team size
type: number
required: true
validation: min:1,max:20
default: 1
help: Number of people working on this mission
[/get:team_size]

[get:enable_tracking]
question: Enable progress tracking?
type: boolean
required: true
default: true
help: Track milestones and progress in workflow system
[/get:enable_tracking]

[get:milestone_frequency]
question: Milestone check frequency
type: choice
options: ["daily", "weekly", "bi-weekly", "monthly"]
required: true
default: "weekly"
help: How often to review mission progress
[/get:milestone_frequency]

[get:additional_notes]
question: Additional notes
type: textarea
required: false
validation: max:300
help: Any other relevant mission information
[/get:additional_notes]

---

## 🔄 Processing & Output

[process:variables]
mission_id = [get:mission_name] | slugify
mission_filename = [timestamp]-[process:mission_id]-mission.md
workflow_filename = [timestamp]-[process:mission_id]-workflow.json
creation_date = [date:iso]
success_criteria_list = [[get:success_criteria_1], [get:success_criteria_2], [get:success_criteria_3]] | filter_empty
[/process:variables]

[output:mission_brief]
file: uMEMORY/missions/[process:mission_filename]
template: uDOT-mission-brief.md
variables: [get:*], [process:*]
[/output:mission_brief]

[output:workflow_config]
file: sandbox/workflow/missions/[process:mission_id].json
format: json
data: {
  "mission_id": "[process:mission_id]",
  "title": "[get:mission_name]",
  "type": "[get:mission_type]",
  "priority": "[get:priority]",
  "complexity": "[get:complexity]",
  "status": "planning",
  "created": "[process:creation_date]",
  "timeline": "[get:estimated_duration]",
  "start_date": "[get:start_date]",
  "end_date": "[get:end_date]",
  "objective": "[get:objective]",
  "context": "[get:context]",
  "success_criteria": "[process:success_criteria_list]",
  "team_size": "[get:team_size]",
  "tracking_enabled": "[get:enable_tracking]",
  "milestone_frequency": "[get:milestone_frequency]",
  "save_as_legacy": "[get:save_as_legacy]",
  "legacy_category": "[get:legacy_category]",
  "progress_percentage": 0,
  "required_milestones": [],
  "completed_milestones": [],
  "assist_recommendations": [],
  "legacy_impact": "[get:legacy_category]"
}
[/output:workflow_config]

[output:initial_milestone]
file: sandbox/workflow/milestones/[process:mission_id]-kickoff.json
format: json
data: {
  "milestone_id": "[process:mission_id]-kickoff",
  "title": "Mission Kickoff: [get:mission_name]",
  "description": "Initial mission setup and planning phase",
  "achieved": "[process:creation_date]",
  "mission_id": "[process:mission_id]",
  "significance": "foundational",
  "next_suggested_milestone": "First Progress Check",
  "contributes_to_mission": "[process:mission_id]"
}
[/output:initial_milestone]

---

## 🎯 Integration Points

- **Mission Templates**: Uses uDOT-mission-brief.md for document generation
- **Workflow System**: Integrates with sandbox/workflow/ for tracking
- **Storage**: Saves to uMEMORY/missions/ for permanent records
- **Milestones**: Creates initial milestone for mission tracking
- **Dashboard**: Mission data available for dashboard display
- **Legacy System**: Optional preservation for completed missions

---

*uDOS v1.0.4.1 Mission Setup Wizard - Workflow Integration System*
