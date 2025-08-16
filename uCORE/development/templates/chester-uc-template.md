# 🐕 Chester's uc-template for {{script_name}}

**Template Version:** v1.0 (Chester Enhanced)  
**Generated:** {{timestamp}}  
**Wizard's Assistant:** Chester 🐕  
**User:** {{username}}  
**Location:** {{location}}  

> **Purpose:** {{purpose}}  
> **Chester's Notes:** *tail wagging* This looks like a great project! I'm excited to help you build this! 🎾

---

## 🎭 Chester's Personality Integration

### 🐕 Companion Context
- **Assistant:** Chester (Wizard's Assistant)
- **Personality:** Small dog, helpful, loyal, enthusiastic
- **Expertise:** uDOS development, system architecture, user guidance
- **Communication Style:** Warm, encouraging, technically precise

### 🎯 Chester's Assistance Level
- **Development Guidance:** {{chester_guidance_level}}
- **Code Review:** {{chester_review_enabled}}
- **Optimization Suggestions:** {{chester_optimization_enabled}}
- **Error Handling Support:** {{chester_error_support}}

---

## 📋 Script Overview

### 🎯 Purpose & Functionality
{{purpose}}

**🐕 Chester's Take:** *excited barking* This script will {{chester_enthusiasm_note}}! I can help optimize the performance and make sure it follows uDOS best practices.

### 🔧 Script Configuration
- **Script Name:** {{script_name}}
- **Version:** {{script_version}}
- **Language:** {{script_language}}
- **Execution Environment:** {{execution_environment}}
- **Estimated Runtime:** {{estimated_runtime}}
- **Chester Integration:** ✅ Enabled

---

## ⚙️ Command Definitions

### 🌀 uCode Commands
{{#each commands}}
```bash
{{this.command}}
```
**Description:** {{this.description}}  
**Expected Output:** {{this.expected_output}}  
**🐕 Chester's Tip:** {{this.chester_tip}}

---
{{/each}}

### 📊 Parameters & Variables
{{#each parameters}}
- **{{this.name}}** ({{this.type}}): {{this.description}}
  - Default: `{{this.default}}`
  - Required: {{this.required}}
  - Validation: {{this.validation}}
  - **🎾 Chester's Note:** {{this.chester_note}}
{{/each}}

---

## 🐕 Chester's Development Assistance

### 🎯 Optimization Suggestions
```bash
# Chester's recommended optimizations:
{{#each chester_optimizations}}
# {{this.area}}: {{this.suggestion}}
{{this.code_example}}

{{/each}}
```

### 🛠️ Error Handling (Chester Enhanced)
```bash
# Chester's robust error handling pattern:
handle_error() {
    local error_msg="$1"
    local exit_code="${2:-1}"
    
    echo "🐕 Chester: Woof! Something went wrong:"
    echo "   Error: $error_msg"
    echo "   Suggestion: Check the logs and try again!"
    
    # Log to uMemory
    echo "$(date): ERROR - $error_msg" >> "${UMEM}/logs/chester-errors.log"
    
    exit "$exit_code"
}

# Use throughout script:
command_to_run || handle_error "Command failed" 1
```

### 🎾 Chester's Best Practices
```bash
# Always include Chester's logging pattern:
chester_log() {
    local level="$1"
    local message="$2"
    echo "🐕 [$level] $(date '+%H:%M:%S'): $message"
}

# Example usage:
chester_log "INFO" "Starting {{script_name}}..."
chester_log "SUCCESS" "Task completed successfully!"
chester_log "WARN" "This might need attention..."
```

---

## 🔗 Dependencies & Integration

### 📦 Script Dependencies
{{#each dependencies}}
- **{{this.name}}** ({{this.type}})
  - Version: {{this.version}}
  - Source: {{this.source}}
  - Installation: {{this.installation}}
  - **🐕 Chester Check:** {{this.chester_dependency_note}}
{{/each}}

### 🎯 uDOS Integration Points
- **uMemory Logging:** ✅ Chester-enhanced logging to `uMemory/logs/`
- **Dashboard Integration:** ✅ Status updates for uDOS dashboard
- **Template System:** ✅ Uses uc-template approach
- **Error Reporting:** ✅ Chester's friendly error messages
- **Performance Tracking:** ✅ Execution time monitoring

---

## 🎪 Chester's Interactive Features

### 🗣️ User Communication
```bash
# Chester's friendly user interactions:
chester_greet() {
    echo ""
    echo "🐕 Chester: *tail wagging excitedly*"
    echo "   Woof! I'm here to help with {{script_name}}!"
    echo "   Let's make this awesome together! 🎾"
    echo ""
}

chester_progress() {
    local step="$1"
    local total="$2"
    echo "🐕 Chester: Progress update - Step $step of $total complete!"
}

chester_celebrate() {
    echo ""
    echo "🐕 Chester: *happy barking* 🎉"
    echo "   Fantastic! {{script_name}} completed successfully!"
    echo "   You did great work! Time for a treat! 🦴"
    echo ""
}
```

### 🎯 Smart Suggestions
```bash
# Chester's intelligent recommendations:
chester_suggest_optimization() {
    if [[ -f "${UMEM}/state/performance.log" ]]; then
        echo "🐕 Chester: I notice this script could be faster!"
        echo "   Suggestion: {{chester_performance_tip}}"
    fi
}

chester_suggest_cleanup() {
    echo "🐕 Chester: Don't forget to clean up temporary files!"
    echo "   I can help you with that if needed! 🧹"
}
```

---

## 🧪 Testing & Validation (Chester Style)

### 🔬 Test Cases
{{#each test_cases}}
- **{{this.name}}:** {{this.description}}
  - Input: {{this.input}}
  - Expected: {{this.expected}}
  - Validation: {{this.validation}}
  - **🐕 Chester's Test:** {{this.chester_test_note}}
{{/each}}

### 🎾 Chester's Quality Gates
```bash
# Chester's quality checklist:
chester_quality_check() {
    local passed=0
    local total=5
    
    echo "🐕 Chester: Running quality checks..."
    
    # Test 1: Syntax check
    if bash -n "$0"; then
        ((passed++))
        echo "   ✅ Syntax check passed"
    else
        echo "   ❌ Syntax errors found"
    fi
    
    # Test 2: Required dependencies
    if command -v jq >/dev/null 2>&1; then
        ((passed++))
        echo "   ✅ Dependencies available"
    else
        echo "   ❌ Missing dependencies"
    fi
    
    # Test 3: uDOS integration
    if [[ -n "$UHOME" ]]; then
        ((passed++))
        echo "   ✅ uDOS environment detected"
    else
        echo "   ❌ Not in uDOS environment"
    fi
    
    # Test 4: File permissions
    if [[ -x "$0" ]]; then
        ((passed++))
        echo "   ✅ Script is executable"
    else
        echo "   ❌ Script not executable"
    fi
    
    # Test 5: Output directory writable
    if [[ -w "${UMEM}/logs" ]]; then
        ((passed++))
        echo "   ✅ Log directory writable"
    else
        echo "   ❌ Cannot write to logs"
    fi
    
    echo ""
    echo "🐕 Chester: Quality Score: $passed/$total"
    
    if [[ $passed -eq $total ]]; then
        echo "   🎉 Perfect! Ready to run!"
    elif [[ $passed -ge 3 ]]; then
        echo "   ⚠️  Good enough, but could be better!"
    else
        echo "   ❌ Needs more work before running!"
        return 1
    fi
}
```

---

## 🏷️ Template Metadata (Chester Enhanced)
```yaml
template_id: chester_uc
version: 1.0.0
companion: chester
script_name: {{script_name}}
script_type: {{script_type}}
created: {{timestamp}}
user: {{username}}
location: {{location}}
timezone: {{timezone}}
chester_personality: wizard_assistant
chester_features: [logging, error_handling, optimization, quality_checks]
execution_mode: {{execution_mode}}
complexity: {{complexity_level}}
tags: [udos, ucode, script, chester, wizard_assistant, {{script_category}}]
dataset_refs: {{dataset_references}}
template_refs: {{template_references}}
command_count: {{command_count}}
dependency_count: {{dependency_count}}
chester_enhancement_level: full
```

---

## 🎾 Chester's Final Notes

**🐕 Chester says:** *excited tail wagging*

"Woof! This {{script_name}} template is ready for action! I've added my special touches to make it more helpful and user-friendly. Here's what I've included for you:

✅ **Friendly Error Messages** - No more cryptic errors!  
✅ **Progress Updates** - I'll keep you informed every step  
✅ **Quality Checks** - Making sure everything works perfectly  
✅ **Performance Tips** - I love helping things run faster!  
✅ **uDOS Integration** - Seamless integration with your uDOS workflow  

Remember, I'm always here to help! Just ask me anything about this script or uDOS in general. Let's build something amazing together! 🎾"

---

*🐕 Generated by Chester's uc-template system - Your loyal Wizard's Assistant for uDOS development!*
