# uCode Script Template - {{script_name}}

**Template Version:** v1.2.0  
**Generated:** {{timestamp}}  
**User:** {{username}}  
**Location:** {{location}}  
**Assistant:** {{assistant_name}}

> **Purpose:** {{purpose}}  
> **Script Type:** {{script_type}}  
> **Execution Mode:** {{execution_mode}}

---

## 📋 Script Overview

### 🎯 Purpose & Functionality
{{purpose}}

### 🔧 Script Configuration
- **Script Name:** {{script_name}}
- **Version:** {{script_version}}
- **Language:** {{script_language}}
- **Execution Environment:** {{execution_environment}}
- **Estimated Runtime:** {{estimated_runtime}}
- **Assistant Integration:** {{assistant_integration_enabled}}

---

## ⚙️ Command Definitions

### 🌀 uCode Commands
{{#each commands}}
```bash
{{this.command}}
```
**Description:** {{this.description}}  
**Expected Output:** {{this.expected_output}}  
**Error Handling:** {{this.error_handling}}

---
{{/each}}

### 📊 Parameters & Variables
{{#each parameters}}
- **{{this.name}}** ({{this.type}}): {{this.description}}
  - Default: `{{this.default}}`
  - Required: {{this.required}}
  - Validation: {{this.validation}}
  - **Notes:** {{this.notes}}
{{/each}}

---

## 🛠️ Development Features

### 📈 Optimization Suggestions
```bash
# Recommended optimizations:
{{#each optimizations}}
# {{this.area}}: {{this.suggestion}}
{{this.code_example}}

{{/each}}
```

### 🛡️ Error Handling Pattern
```bash
# Robust error handling:
handle_error() {
    local error_msg="$1"
    local exit_code="${2:-1}"
    
    echo "ERROR: $error_msg"
    echo "Suggestion: Check the logs and try again"
    
    # Log to uMemory
    echo "$(date): ERROR - $error_msg" >> "${UMEM}/logs/script-errors.log"
    
    exit "$exit_code"
}

# Usage throughout script:
command_to_run || handle_error "Command failed" 1
```

### 📋 Logging Pattern
```bash
# Standardized logging:
log_message() {
    local level="$1"
    local message="$2"
    echo "[$level] $(date '+%H:%M:%S'): $message"
}

# Example usage:
log_message "INFO" "Starting {{script_name}}..."
log_message "SUCCESS" "Task completed successfully"
log_message "WARN" "This might need attention"
```

---

## 🔗 Dependencies & Integration

### 📦 Script Dependencies
{{#each dependencies}}
- **{{this.name}}** ({{this.type}})
  - Version: {{this.version}}
  - Source: {{this.source}}
  - Installation: {{this.installation}}
  - **Validation:** {{this.validation_method}}
{{/each}}

### 🎯 uDOS Integration Points
- **Memory System:** Logging to `uMemory/logs/`
- **Dashboard Integration:** Status updates for uDOS dashboard
- **Template System:** Uses standardized template approach
- **Error Reporting:** Structured error messages
- **Performance Tracking:** Execution time monitoring

---

## 🎪 User Interaction Features

### 💬 User Communication
```bash
# User interaction functions:
show_welcome() {
    echo ""
    echo "Starting {{script_name}}..."
    echo "Assistant: {{assistant_name}}"
    echo ""
}

show_progress() {
    local step="$1"
    local total="$2"
    echo "Progress: Step $step of $total complete"
}

show_completion() {
    echo ""
    echo "{{script_name}} completed successfully!"
    echo "Execution time: ${execution_time}s"
    echo ""
}
```

### 💡 Smart Suggestions
```bash
# Intelligent recommendations:
suggest_optimization() {
    if [[ -f "${UMEM}/state/performance.log" ]]; then
        echo "Suggestion: This script could be optimized for better performance"
        echo "Recommendation: {{performance_tip}}"
    fi
}

suggest_cleanup() {
    echo "Suggestion: Clean up temporary files after execution"
    echo "Use: rm -rf /tmp/{{script_name}}_*"
}
```

---

## 🧪 Testing & Validation

### 🔬 Test Cases
{{#each test_cases}}
- **{{this.name}}:** {{this.description}}
  - Input: {{this.input}}
  - Expected: {{this.expected}}
  - Validation: {{this.validation}}
  - **Status:** {{this.status}}
{{/each}}

### ✅ Quality Checks
```bash
# Quality validation checklist:
run_quality_checks() {
    local passed=0
    local total=5
    
    echo "Running quality validation..."
    
    # Test 1: Syntax check
    if bash -n "$0"; then
        ((passed++))
        echo "   ✅ Syntax check passed"
    else
        echo "   ❌ Syntax errors found"
    fi
    
    # Test 2: Dependencies available
    if command -v jq >/dev/null 2>&1; then
        ((passed++))
        echo "   ✅ Dependencies available"
    else
        echo "   ❌ Missing dependencies"
    fi
    
    # Test 3: uDOS environment
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
    echo "Quality Score: $passed/$total"
    
    if [[ $passed -eq $total ]]; then
        echo "Status: Ready to execute"
    elif [[ $passed -ge 3 ]]; then
        echo "Status: Acceptable with warnings"
    else
        echo "Status: Requires fixes before execution"
        return 1
    fi
}
```

---

## 🏷️ Template Metadata
```yaml
template_id: ok_assistant_template
version: 1.2.0
assistant_type: {{assistant_type}}
script_name: {{script_name}}
script_type: {{script_type}}
created: {{timestamp}}
user: {{username}}
location: {{location}}
timezone: {{timezone}}
features: [logging, error_handling, optimization, quality_checks]
execution_mode: {{execution_mode}}
complexity: {{complexity_level}}
tags: [udos, ucode, script, assistant, {{script_category}}]
dataset_refs: {{dataset_references}}
template_refs: {{template_references}}
command_count: {{command_count}}
dependency_count: {{dependency_count}}
enhancement_level: {{enhancement_level}}
```

---

## 📝 Final Notes

**{{assistant_name}} Summary:**

This {{script_name}} template provides a comprehensive foundation for uDOS script development. Key features include:

✅ **Structured Error Handling** - Consistent error management  
✅ **Progress Tracking** - Clear status updates throughout execution  
✅ **Quality Validation** - Automated checks for common issues  
✅ **Performance Optimization** - Built-in suggestions for improvements  
✅ **uDOS Integration** - Seamless integration with uDOS workflow  

The template is designed to be assistant-agnostic, allowing any uDOS assistant to provide personalized guidance while maintaining a consistent underlying structure.

---

*Generated by uDOS OK-Assistant Template System v1.2.0*
