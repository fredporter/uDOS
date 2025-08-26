````markdown
# Mission: {{mission_name}} 🎯

**Template Version:** v1.0.4.1
**Generated:** {{instance_time}}
**Quest Leader:** {{quest_leader|default:"You"}}
**Document ID:** {{document_id}}
**Priority:** {{input:priority|enum:low,medium,high,epic|default:medium}}
**Status:** {{input:status|enum:planning,active,on-hold,completed,cancelled|default:planning}}
**Legacy Save:** {{input:save_as_legacy|boolean|default:true}}

> **Quest Type:** {{input:quest_type|enum:learning,building,exploring,mastering,creating,improving}}
> **Difficulty:** {{input:difficulty|enum:easy,moderate,challenging,legendary|default:moderate}}
> **Move Budget:** {{input:move_budget|number|default:50}} moves
> **Adventure Level:** {{input:adventure_level|enum:solo,guided,collaborative|default:solo}}

---

## 🎮 Quest Overview

### 🌟 Primary Objective
{{input:objective|required|min:10}}
*What epic thing are you setting out to accomplish?*

### 📖 Quest Story
{{input:quest_story|textarea}}
*Tell the story of why this mission matters to you personally*

### 🗺️ Adventure Map
{{input:current_location|default:"Starting Point"}} → {{input:target_destination|default:"Quest Complete"}}

---

## ⚡ Quest Resources & Budget

### 🎯 Move Allocation Plan
- **Total Move Budget:** {{input:move_budget|default:50}} moves
- **Learning Moves:** {{input:learning_moves|default:15}} moves
- **Building Moves:** {{input:building_moves|default:20}} moves
- **Testing Moves:** {{input:testing_moves|default:10}} moves
- **Polish Moves:** {{input:polish_moves|default:5}} moves

### 📊 Move Tracking
```
Progress: [{{progress_bar}}] {{progress_percentage}}%
Moves Used: {{moves_used|default:0}} / {{input:move_budget|default:50}}
Moves Remaining: {{moves_remaining}}
Efficiency: {{move_efficiency}}%
```

### 🎒 Quest Inventory
{{#each quest_inventory}}
- **{{this.item}}**: {{this.description}} {{#if this.acquired}}✅{{else}}⏳{{/if}}
{{/each}}

---

## 🎯 Quest Objectives & Milestones

### 🏆 Main Quest Line
{{#each main_objectives}}
1. **{{this.name}}** ({{this.estimated_moves}} moves)
   - {{this.description}}
   - Success criteria: {{this.success_criteria}}
   - Reward: {{this.reward}}
{{/each}}

### 🌟 Side Quests (Optional)
{{#each side_quests}}
- **{{this.name}}** ({{this.estimated_moves}} moves)
  - {{this.description}}
  - Bonus reward: {{this.bonus_reward}}
{{/each}}

### 🎖️ Achievement Milestones
{{#each milestones}}
- **{{this.name}}** - {{this.description}}
  - Unlock condition: {{this.unlock_condition}}
  - Move cost: {{this.move_cost}}
  - Achievement points: {{this.points}}
{{/each}}

---

## 🛡️ Quest Strategy & Tactics

### 🗂️ Skill Requirements
{{#each required_skills}}
- **{{this.skill}}**: {{this.current_level}} → {{this.target_level}}
  - Learning moves needed: {{this.moves_to_develop}}
{{/each}}

### 🔧 Tools & Equipment
{{#each tools_needed}}
- **{{this.tool}}**: {{this.purpose}}
  - Status: {{this.status}}
  - Setup moves: {{this.setup_moves}}
{{/each}}

### 🧭 Navigation Plan
1. **Phase 1 - Preparation** ({{phase_1_moves}} moves)
   - {{phase_1_description}}
2. **Phase 2 - Core Quest** ({{phase_2_moves}} moves)
   - {{phase_2_description}}
3. **Phase 3 - Completion** ({{phase_3_moves}} moves)
   - {{phase_3_description}}

---

## ⚠️ Quest Challenges & Power-Ups

### 🐉 Known Challenges
{{#each challenges}}
- **{{this.challenge}}** (Difficulty: {{this.difficulty}})
  - Strategy: {{this.mitigation_strategy}}
  - Escape route: {{this.backup_plan}}
  - Move cost if encountered: {{this.additional_moves}}
{{/each}}

### ⚡ Power-Ups & Boosts
{{#each power_ups}}
- **{{this.power_up}}**: {{this.effect}}
  - How to acquire: {{this.acquisition_method}}
  - Move savings: {{this.moves_saved}}
{{/each}}

### 🤝 Support Network
{{#each support_allies}}
- **{{this.ally}}**: {{this.how_they_help}}
  - Contact: {{this.contact_method}}
  - When to call: {{this.when_to_reach_out}}
{{/each}}

---

## 📈 Quest Progress Tracking

### 🎮 Daily Quest Log
*Track your daily progress and moves*

**{{current_date}}**
- Moves today: {{moves_today}}
- Objectives completed: {{objectives_completed_today}}
- New discoveries: {{discoveries_today}}
- Tomorrow's plan: {{tomorrow_plan}}

### 🏃‍♂️ Sprint Planning (Weekly Cycles)
**Week {{current_week}}**
- Weekly move target: {{weekly_move_target}}
- Focus objectives: {{weekly_focus}}
- Success metrics: {{weekly_success_metrics}}

### 🔄 Quest Retrospectives
{{#each retrospectives}}
**{{this.date}}**
- What worked well: {{this.what_worked}}
- What to improve: {{this.improvements}}
- Move efficiency: {{this.efficiency}}
- Energy level: {{this.energy_rating}}/10
{{/each}}

---

## 🎊 Quest Completion & Rewards

### 🏆 Victory Conditions
{{#each victory_conditions}}
- [ ] {{this}}
{{/each}}

### 🎁 Rewards & Loot
**Personal Rewards:**
{{#each personal_rewards}}
- {{this}}
{{/each}}

**Skill Unlocks:**
{{#each skill_unlocks}}
- **{{this.skill}}**: {{this.new_capability}}
{{/each}}

**Legacy Items:**
{{#each legacy_items}}
- **{{this.item}}**: {{this.description}}
  - Future value: {{this.future_applications}}
{{/each}}

### 🌟 XP & Level Progress
- **Experience Gained:** {{experience_points}} XP
- **Current Level:** {{current_level}}
- **Next Level:** {{next_level}} ({{xp_needed_for_next}} XP needed)
- **New Abilities Unlocked:** {{new_abilities}}

---

## 🏛️ Quest Legacy & Impact

{{#if input:save_as_legacy}}
### 📚 Legacy Documentation
This quest will be preserved as a legendary tale for future adventurers.

**Quest Type:** {{input:legacy_category|enum:achievement,knowledge,innovation,mastery|default:achievement}}
**Legacy Value:** {{input:legacy_value|textarea}}
**Future Applications:** {{input:future_applications|textarea}}
**Archive Location:** uMEMORY/legacy/quests/{{mission_name|slugify}}/

### 🎭 Quest Tale Summary
{{input:quest_tale|textarea}}
*The epic story of this quest, told for future inspiration*

### 🧠 Wisdom Gained
{{input:wisdom_gained|textarea}}
*Key insights and lessons learned on this adventure*
{{/if}}

---

## 🛠️ Quest Management

### 📝 Quick Actions
- `[quest:start]` - Begin the adventure
- `[quest:pause]` - Take a rest
- `[quest:move]` - Log a move
- `[quest:milestone]` - Complete objective
- `[quest:complete]` - Finish quest

### 🔄 Related Quests
{{#each related_quests}}
- **{{this.name}}**: {{this.relationship}}
{{/each}}

### 📊 Quest Metrics
- **Total Moves:** {{total_moves}}
- **Completion Rate:** {{completion_percentage}}%
- **Efficiency Score:** {{efficiency_score}}/100
- **Fun Factor:** {{fun_rating}}/10 ⭐

---

**Quest Template Version:** v1.0.4.1
**Last Updated:** August 26, 2025
**Compatibility:** uDOS Core System v1.0.4.1+
**User Journey:** Move → Goal → Milestone → **Mission** → Legacy

---

*This quest template transforms missions from corporate projects into personal adventures, using moves as the primary resource and focusing on individual achievement, learning, and fun.*

````
