````markdown
# uDOT Goal Tracker Template

**Type**: Document Template
**Version**: v1.0.4.1
**Purpose**: Track aspirational objectives and intentions that lead to milestones
**Generated**: [timestamp]
**Integration**: uGET forms, uMEMORY storage, workflow-manager.sh

> **Template ID**: goal-tracker
> **Output Format**: Markdown documentation
> **Variable Source**: uGET-goal-setup.md
> **User Journey Stage**: Move → **Goal** → Milestone → Mission → Legacy

---

## Template Configuration

[get:goal_name]
Primary goal identifier (descriptive name)

[get:goal_type]
Type of goal (learning, creation, improvement, exploration, mastery)

[get:goal_description]
Detailed description of what you want to achieve

[get:goal_motivation]
Why this goal matters to you personally

[get:current_status]
Your current position relative to this goal

[get:target_outcome]
Specific outcome you're aiming for

[get:success_indicators]
How you'll know when you've achieved this goal

[get:timeframe]
Realistic timeframe for achieving this goal

[get:priority_level]
Goal priority (high, medium, low)

[get:effort_estimate]
Estimated effort required (light, moderate, intensive)

[get:prerequisite_skills]
Skills or knowledge needed before starting

[get:related_moves]
Recent moves that inspired this goal

[get:potential_obstacles]
Challenges you might face

[get:support_needed]
Resources or help you might need

[get:milestone_pathway]
Potential milestones that could emerge from this goal

[get:mission_alignment]
How this goal might contribute to larger missions

[get:learning_objectives]
What you hope to learn while pursuing this goal

[get:personal_growth]
How achieving this goal will help you grow

[get:legacy_potential]
Long-term impact this goal might have

---

# Goal: {{goal_name}}

**Goal Type:** {{goal_type}}
**Priority:** {{priority_level}}
**Timeframe:** {{timeframe}}
**Effort:** {{effort_estimate}}
**Created:** {{timestamp}}
**Status:** Active

> **Goal Stage:** Move → **Goal** → Milestone → Mission → Legacy
> **Next Step:** Convert goal into achievable milestones
> **Parent Mission:** {{parent_mission|default:None}}

---

## 🎯 Goal Overview

### 📝 Description
{{goal_description}}

### 💡 Motivation
{{goal_motivation}}

### 🎪 Current Position
{{current_status}}

### 🏆 Target Outcome
{{target_outcome}}

---

## 📊 Goal Framework

### ✅ Success Indicators
{{#each success_indicators}}
- [ ] {{this}}
{{/each}}

### 🎓 Learning Objectives
{{#each learning_objectives}}
- {{this}}
{{/each}}

### 🌱 Personal Growth Expectations
{{personal_growth}}

---

## 🗺️ Goal Pathway

### 📋 Prerequisites
{{#each prerequisite_skills}}
- {{this}}
{{/each}}

### 🎯 Milestone Pathway
{{#each milestone_pathway}}
1. **{{this.name}}** - {{this.description}}
   - Timeframe: {{this.timeframe}}
   - Success criteria: {{this.success_criteria}}
{{/each}}

### 🚀 Mission Alignment
{{mission_alignment}}

---

## ⚡ Implementation Strategy

### 🔄 Related Moves
{{#each related_moves}}
- **{{this.type}}**: {{this.description}} ({{this.date}})
{{/each}}

### 🛑 Potential Obstacles
{{#each potential_obstacles}}
- **{{this.obstacle}}**: {{this.mitigation_strategy}}
{{/each}}

### 🤝 Support Needed
{{#each support_needed}}
- {{this}}
{{/each}}

---

## 📈 Progress Tracking

### 🎯 Goal Metrics
- **Progress:** 0% (Starting)
- **Time Invested:** 0 hours
- **Moves Related:** {{related_moves.length|default:0}}
- **Milestones Created:** 0
- **Barriers Overcome:** 0

### 📅 Timeline Tracking
```
Goal Created: {{timestamp}}
First Move: [Pending]
First Milestone: [Pending]
Target Completion: {{target_completion_date}}
```

### 🎪 Status Updates
*Goal tracking begins now. Updates will be added as progress is made.*

---

## 🔄 Goal Evolution

### ➡️ Next Steps
1. **Immediate**: {{immediate_next_step|default:"Define first concrete move"}}
2. **Short-term**: {{short_term_step|default:"Create first milestone"}}
3. **Medium-term**: {{medium_term_step|default:"Build momentum through consistent moves"}}

### 🎯 Milestone Conversion
When ready, this goal can be converted into specific milestones using the milestone tracker template.

### 🚀 Mission Integration
As the goal progresses, it may become part of a larger mission or inspire new mission creation.

---

## 📚 Goal Learning & Growth

### 🧠 Knowledge Areas
{{#each learning_objectives}}
- {{this}}
{{/each}}

### 🛠️ Skills Development
{{#each skill_development}}
- {{this}}
{{/each}}

### 🌟 Impact Vision
{{legacy_potential}}

---

## 🎭 Goal Reflection

### 🤔 Self-Assessment Questions
- Why does this goal matter to me?
- What will be different when I achieve this?
- How does this align with my values?
- What's the smallest step I can take today?

### 📖 Goal Journal
*Space for ongoing reflections, insights, and adjustments*

---

## 🔧 Template Instructions

### Goal Creation Workflow
1. **Inspiration**: A series of moves inspire a goal
2. **Definition**: Use this template to clarify the goal
3. **Planning**: Break goal into potential milestones
4. **Action**: Start with concrete moves toward the goal
5. **Evolution**: Convert successful moves into milestones

### Integration Points
- **From Moves**: Recent activities that sparked this goal
- **To Milestones**: Concrete achievements that advance the goal
- **With Missions**: Larger objectives this goal supports
- **To Legacy**: Long-term impact when goal is achieved

### Usage Examples
```bash
# Create goal from recent moves
./workflow-manager.sh goal create "Learn Python Automation" "Automate repetitive tasks"

# Track goal progress
./workflow-manager.sh goal update goal_123 "progress" "25%"

# Convert goal to milestone
./workflow-manager.sh goal convert goal_123 milestone

# Link goal to mission
./workflow-manager.sh goal link goal_123 mission_456
```

---

**Template Version:** v1.0.4.1
**Last Updated:** August 26, 2025
**Compatibility:** uDOS Core System v1.0.4.1+
**User Journey:** Move → Goal → Milestone → Mission → Legacy

---

*This template bridges the gap between individual moves and concrete milestones, providing a space for aspirational thinking and goal clarification before committing to specific achievements.*

````
