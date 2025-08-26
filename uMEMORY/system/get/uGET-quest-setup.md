````markdown
# uGET Quest Setup Form

**Form Type:** Interactive Personal Quest Creation
**Template Target:** uDOT-mission-quest.md
**Purpose:** Design personal adventures and learning quests using move-based budgeting
**Integration:** Workflow Manager, Goal System, Milestone Tracking

---

## 🎮 Quest Foundation

[input:mission_name|text|required]
**Quest Name**: What's your adventure called?
~ Make it exciting and personal (e.g., "Master the Art of Python Magic")

[input:quest_leader|text]
**Quest Leader**: Who's leading this adventure?
~ Default: "You" (since this is your personal quest)

[input:quest_type|select|required]
**Quest Type**: What kind of adventure is this?
~ Options: learning,building,exploring,mastering,creating,improving

[input:priority|select|required]
**Priority Level**: How important is this quest?
~ Options: low,medium,high,epic

[input:difficulty|select|required]
**Difficulty Level**: How challenging will this be?
~ Options: easy,moderate,challenging,legendary

---

## 📖 Quest Story & Motivation

[input:objective|textarea|required]
**Primary Objective**: What epic thing are you setting out to accomplish?
~ Be specific about your end goal

[input:quest_story|textarea|required]
**Quest Story**: Why does this mission matter to you personally?
~ Tell the story behind your motivation

[input:current_location|text]
**Starting Point**: Where are you now in relation to this quest?
~ Your current skill/knowledge level

[input:target_destination|text]
**Quest Complete**: What does victory look like?
~ Your desired end state

---

## ⚡ Move Budget & Resource Planning

[input:move_budget|number|required]
**Total Move Budget**: How many moves do you think this quest will take?
~ Default: 50 moves (adjust based on quest scope)

[input:learning_moves|number]
**Learning Moves**: How many moves for research and learning?
~ Suggested: 30% of total budget

[input:building_moves|number]
**Building Moves**: How many moves for creation and implementation?
~ Suggested: 40% of total budget

[input:testing_moves|number]
**Testing Moves**: How many moves for testing and refinement?
~ Suggested: 20% of total budget

[input:polish_moves|number]
**Polish Moves**: How many moves for finishing touches?
~ Suggested: 10% of total budget

---

## 🎯 Quest Objectives & Structure

[input:main_objectives|structured_list|required]
**Main Quest Line**: What are the major objectives?
~ Structure: name, description, estimated_moves, success_criteria, reward

[input:side_quests|structured_list]
**Side Quests**: Any optional objectives for bonus rewards?
~ Structure: name, description, estimated_moves, bonus_reward

[input:milestones|structured_list]
**Achievement Milestones**: What milestones will mark progress?
~ Structure: name, description, unlock_condition, move_cost, points

---

## 🛡️ Skills & Equipment

[input:required_skills|structured_list]
**Skill Requirements**: What skills do you need to develop?
~ Structure: skill, current_level, target_level, moves_to_develop

[input:tools_needed|structured_list]
**Tools & Equipment**: What tools do you need?
~ Structure: tool, purpose, status, setup_moves

[input:quest_inventory|structured_list]
**Quest Inventory**: What resources will you collect?
~ Structure: item, description, acquired (true/false)

---

## 🌟 Strategy & Support

[input:phase_1_description|textarea]
**Phase 1 - Preparation**: What happens in the prep phase?
~ Planning, tool setup, initial learning

[input:phase_1_moves|number]
**Phase 1 Move Budget**: How many moves for preparation?

[input:phase_2_description|textarea]
**Phase 2 - Core Quest**: What's the main adventure?
~ The heart of your quest activities

[input:phase_2_moves|number]
**Phase 2 Move Budget**: How many moves for the core quest?

[input:phase_3_description|textarea]
**Phase 3 - Completion**: How do you finish strong?
~ Testing, polishing, celebrating

[input:phase_3_moves|number]
**Phase 3 Move Budget**: How many moves to complete?

---

## ⚠️ Challenges & Power-Ups

[input:challenges|structured_list]
**Known Challenges**: What obstacles might you face?
~ Structure: challenge, difficulty, mitigation_strategy, backup_plan, additional_moves

[input:power_ups|structured_list]
**Power-Ups & Boosts**: What could accelerate your progress?
~ Structure: power_up, effect, acquisition_method, moves_saved

[input:support_allies|structured_list]
**Support Network**: Who can help on this quest?
~ Structure: ally, how_they_help, contact_method, when_to_reach_out

---

## 🎊 Victory & Rewards

[input:victory_conditions|list|required]
**Victory Conditions**: How do you know you've won?
~ Clear, measurable completion criteria

[input:personal_rewards|list]
**Personal Rewards**: How will you celebrate?
~ Treats, experiences, purchases, etc.

[input:skill_unlocks|structured_list]
**Skill Unlocks**: What new capabilities will you gain?
~ Structure: skill, new_capability

[input:legacy_items|structured_list]
**Legacy Items**: What lasting value will this create?
~ Structure: item, description, future_applications

---

## 📚 Legacy Planning

[input:save_as_legacy|boolean]
**Save as Legacy**: Should this quest become a legendary tale?
~ Preserve for future inspiration and reference

[input:legacy_category|select]
**Legacy Type**: What kind of legacy is this?
~ Options: achievement,knowledge,innovation,mastery
~ Only shown if save_as_legacy is true

[input:legacy_value|textarea]
**Legacy Value**: What makes this quest worth preserving?
~ Only shown if save_as_legacy is true

[input:future_applications|textarea]
**Future Applications**: How might this help future quests?
~ Only shown if save_as_legacy is true

---

## 🔧 Form Processing Rules

[process:quest_validation]
- Ensure move budget allocation adds up to total budget
- Validate that objectives have realistic move estimates
- Check that victory conditions are measurable
- Confirm skill progression is realistic

[process:gamification]
- Calculate experience points based on difficulty and scope
- Assign achievement points to milestones
- Generate fun quest-themed language
- Create progress tracking mechanisms

[process:integration]
- Link to existing goals that inspired this quest
- Connect to workflow manager for move tracking
- Set up milestone conversion pathways
- Create dashboard tracking widgets

[output:quest_document]
Generate complete quest document using uDOT-mission-quest.md template

[output:workflow_integration]
Create mission entry in workflow system with move budget tracking

[output:dashboard_quest_card]
Add quest card to user dashboard with progress visualization

---

## 🎮 Gamification Features

### Auto-Generated Elements
- **Quest ID**: Unique identifier for tracking
- **Experience Points**: Based on difficulty and scope
- **Achievement System**: Points for milestones and completion
- **Progress Bars**: Visual tracking of moves and objectives
- **Level System**: Personal progression tracking

### Fun Language Conversion
- Projects → Quests
- Tasks → Objectives
- Resources → Inventory
- Challenges → Obstacles/Dragons
- Team → Support Network/Allies
- Budget → Move Allocation
- Timeline → Adventure Phases

### Integration with Workflow
- **Moves**: Link daily activities to quest progress
- **Goals**: Connect aspirational goals to quest objectives
- **Milestones**: Transform objectives into achievement milestones
- **Legacy**: Archive completed quests as legendary tales

---

## 🚀 Usage Examples

### Learning Quest
```
Quest Name: Master React Wizardry
Type: learning
Difficulty: challenging
Move Budget: 75 moves
Objective: Build three React applications from scratch
```

### Creation Quest
```
Quest Name: Build the Ultimate Productivity App
Type: creating
Difficulty: legendary
Move Budget: 150 moves
Objective: Design, build, and launch a personal productivity tool
```

### Exploration Quest
```
Quest Name: Discover Machine Learning Secrets
Type: exploring
Difficulty: moderate
Move Budget: 40 moves
Objective: Understand ML fundamentals and build first model
```

---

**Form Version:** v1.0.4.1
**Template Compatibility:** uDOT-mission-quest.md v1.0.4.1
**Integration:** workflow-manager.sh quest management
**User Journey Stage:** Move → Goal → Milestone → **Mission** → Legacy

---

*This form transforms mission planning from corporate project management into personal adventure design, making goal achievement fun, engaging, and gamified while maintaining detailed planning and progress tracking.*

````
