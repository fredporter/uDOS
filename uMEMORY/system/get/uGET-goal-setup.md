````markdown
# uGET Goal Setup Form

**Form Type:** Interactive Goal Creation
**Template Target:** uDOT-goal-tracker.md
**Purpose:** Guide users through aspirational goal definition before milestone creation
**Integration:** Workflow Manager, User Journey Tracking

---

## 🎯 Goal Definition

[input:goal_name|text|required]
**Goal Name**: What do you want to call this goal?
~ Keep it descriptive but concise (e.g., "Master Python Automation")

[input:goal_type|select|required]
**Goal Type**: What kind of goal is this?
~ Options: learning,creation,improvement,exploration,mastery,innovation,contribution

[input:goal_description|textarea|required]
**Goal Description**: Describe what you want to achieve
~ Be specific about what success looks like

[input:goal_motivation|textarea|required]
**Motivation**: Why does this goal matter to you?
~ Personal connection makes goals more achievable

---

## 📍 Current Situation

[input:current_status|textarea|required]
**Current Position**: Where are you now relative to this goal?
~ Honest assessment of starting point

[input:prerequisite_skills|list]
**Prerequisites**: What skills or knowledge do you need?
~ List any foundational requirements

[input:recent_moves|dynamic_list]
**Related Recent Moves**: Which recent activities inspired this goal?
~ Select from recent workflow moves

---

## 🎯 Target & Success

[input:target_outcome|textarea|required]
**Target Outcome**: What specific result do you want?
~ Concrete and measurable if possible

[input:success_indicators|list|required]
**Success Indicators**: How will you know you've achieved this?
~ Observable signs of success

[input:timeframe|select|required]
**Timeframe**: Realistic timeline for this goal
~ Options: 1-2 weeks,1 month,2-3 months,6 months,1 year,ongoing

---

## ⚡ Implementation Planning

[input:priority_level|select|required]
**Priority Level**: How important is this goal right now?
~ Options: high,medium,low

[input:effort_estimate|select|required]
**Effort Required**: How much work do you expect this to take?
~ Options: light,moderate,intensive

[input:potential_obstacles|list]
**Potential Obstacles**: What challenges might you face?
~ Thinking ahead helps preparation

[input:support_needed|list]
**Support Needed**: What help or resources might you need?
~ People, tools, information, etc.

---

## 🛤️ Pathway Planning

[input:milestone_pathway|structured_list]
**Potential Milestones**: What achievements might lead to this goal?
~ Structure: name, description, timeframe, success_criteria

[input:mission_alignment|textarea]
**Mission Alignment**: How might this goal connect to larger missions?
~ Optional: relationship to bigger objectives

[input:learning_objectives|list]
**Learning Objectives**: What do you hope to learn?
~ Knowledge and skills you'll gain

---

## 🌱 Growth & Impact

[input:personal_growth|textarea]
**Personal Growth**: How will achieving this goal help you grow?
~ Character, skills, confidence, etc.

[input:legacy_potential|textarea]
**Legacy Potential**: What long-term impact might this have?
~ Future applications and benefits

---

## 🔧 Form Processing Rules

[process:goal_validation]
- Ensure goal_name is unique in current goals
- Validate timeframe is realistic for goal_type
- Check that success_indicators are observable
- Confirm prerequisite_skills are actionable

[process:workflow_integration]
- Link to recent moves that inspired this goal
- Suggest first concrete move toward goal
- Identify potential milestone conversion points
- Connect to existing missions if applicable

[process:tracking_setup]
- Create goal tracking file in sandbox/goals/
- Initialize progress metrics (0% complete)
- Set up reminder system based on timeframe
- Create goal dashboard entry

[output:goal_document]
Generate complete goal tracker document using uDOT-goal-tracker.md template

[output:workflow_entry]
Create workflow system entry for goal tracking

[output:dashboard_widget]
Add goal to user dashboard for progress monitoring

---

## 📱 Smart Features

### Auto-Suggestions
- **Goal Type**: Suggest based on recent move patterns
- **Milestones**: Recommend based on goal type and complexity
- **Timeframe**: Estimate based on effort and priority
- **Prerequisites**: Suggest based on goal type

### Integration Points
- **Recent Moves**: Pull from workflow-manager.sh move history
- **Existing Goals**: Avoid duplication and identify synergies
- **Active Missions**: Suggest alignment opportunities
- **Completed Milestones**: Reference past achievements

### Progress Tracking
- **Move Integration**: Track moves related to goal
- **Milestone Evolution**: Monitor goal-to-milestone conversion
- **Mission Alignment**: Track goal contribution to missions
- **Success Monitoring**: Update progress based on indicators

---

## 🚀 Usage Examples

### Quick Goal Creation
```
Goal Name: Learn React Framework
Type: learning
Description: Build interactive web applications using React
Motivation: Want to modernize my web development skills
Timeframe: 2-3 months
Priority: high
```

### Complex Goal Planning
```
Goal Name: Create Open Source Project
Type: creation
Description: Develop and publish a useful developer tool
Success Indicators:
  - Working prototype completed
  - Documentation written
  - Published on GitHub
  - First external contributor
Milestones:
  - Project planning and architecture
  - Core functionality implementation
  - Testing and documentation
  - Community engagement
```

---

## 🔄 Workflow Integration

### Goal Creation Flow
1. **Inspiration**: User notices pattern in recent moves
2. **Form Completion**: Fill out this uGET form
3. **Goal Document**: Generate uDOT-goal-tracker.md
4. **Workflow Registration**: Add to workflow-manager.sh
5. **Progress Tracking**: Monitor through moves and milestones

### Journey Progression
```
Moves (activities) → Goal (aspiration) → Milestone (achievement) → Mission (objective) → Legacy (impact)
```

### Command Integration
```bash
# Create goal from form
ucode GET goal-setup

# Track goal progress
workflow-manager.sh goal update goal_123 "progress" "25%"

# Convert goal to milestone
workflow-manager.sh goal convert goal_123 milestone "First Python Script"

# Link goal to mission
workflow-manager.sh goal align goal_123 mission_456
```

---

**Form Version:** v1.0.4.1
**Template Compatibility:** uDOT-goal-tracker.md v1.0.4.1
**Integration:** workflow-manager.sh goal management
**User Journey Stage:** Move → **Goal** → Milestone → Mission → Legacy

---

*This form helps bridge the gap between individual activities and concrete achievements by capturing aspirational intentions and planning pathways to success.*

````
