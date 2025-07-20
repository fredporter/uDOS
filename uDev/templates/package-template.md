# Package Template: {{package_name}}

**Template Version:** v2.1.0  
**Generated:** {{instance_time}}  
**Instance:** {{instance_location}}  
**Session:** {{instance_session}}  
**Package Category:** {{package_category}}  
**Document ID:** {{document_id}}

> **Purpose:** {{package_purpose}}  
> **Installation Method:** {{installation_method}}  
> **Dependencies:** {{dependencies}}  
> **Dataset References:** {{dataset_references_count}}

## 📊 Metadata Block

**Template System:** v2.1.0  
**Dataset Version:** {{dataset_version}}  
**Cross-References:** {{cross_references_count}}  
**Generated With:** [template:generate package --name={{package_name}}]

### 🔗 Cross-References
{{#each cross_references}}
- **[{{this.type}}:{{this.id}}]({{this.path}})** - {{this.description}}
{{/each}}

### 📊 Related Datasets
- **Package Registry** - [dataset:packages] - Package installation database
- **System Commands** - [dataset:ucode_commands] - Available uCode commands
{{#each related_datasets}}
- **{{this.name}}** - [dataset:{{this.id}}] - {{this.description}}
{{/each}}

---

## 📦 Package Information

### 🎯 Package Overview
- **Name:** {{package_name}}
- **Version:** {{package_version}}
- **Description:** {{package_description}}
- **Homepage:** {{package_homepage}}
- **License:** {{package_license}}
- **Maintainer:** {{package_maintainer}}

### 🔧 Installation Configuration
- **Method:** {{installation_method}}
- **Platform Support:** {{dataset:platforms.{{platform_name}}.support_level}}
- **System Requirements:** {{system_requirements}}
- **Installation Size:** {{installation_size}}
- **Estimated Install Time:** {{install_time}}
- **Repository URL:** {{package_repository}}
- **Binary Location:** {{dataset:system_paths.bin_directory}}/{{package_name}}

### 📊 Package Analytics
- **Download Count:** {{dataset:packages.{{package_name}}.downloads}}
- **Success Rate:** {{dataset:packages.{{package_name}}.install_success_rate}}%
- **User Rating:** {{dataset:packages.{{package_name}}.rating}}/5.0
- **Last Updated:** {{dataset:packages.{{package_name}}.last_update}}

---

## ⚙️ Shortcode Integration

### 📋 Available Shortcodes
{{#each shortcodes}}
- **[{{this.name}}:{{this.args}}]** - {{this.description}}
  - **Usage:** `[{{this.name}}:{{this.example_args}}]`
  - **Output:** {{this.expected_output}}
{{/each}}

### 🌀 Package Management Commands
```bash
# Install package
[package:install {{package_name}}]

# Check status
[package:status {{package_name}}]

# Update package
[package:update {{package_name}}]

# Remove package
[package:remove {{package_name}}]

# Show package info
[package:info {{package_name}}]
```

---

## 🛠️ Installation Script

### 📊 Pre-Installation Checks
```bash
{{#each pre_checks}}
# {{this.description}}
{{this.command}}
{{/each}}
```

### 🔄 Installation Steps
{{#each installation_steps}}
**Step {{@index}}: {{this.title}}**
```bash
{{this.command}}
```
*Expected Result:* {{this.expected_result}}
*Error Handling:* {{this.error_handling}}

{{/each}}

### ✅ Post-Installation Validation
```bash
{{#each validation_steps}}
# {{this.description}}
{{this.command}}
{{/each}}
```

---

## 📋 Configuration & Usage

### 🎛️ Default Configuration
```{{config_format}}
{{default_config}}
```

### 🚀 Usage Examples
{{#each usage_examples}}
**{{this.title}}**
```bash
{{this.command}}
```
*Description:* {{this.description}}
*Expected Output:* {{this.output}}

{{/each}}

---

## 🔧 Integration with uDOS

### 📄 File Locations
- **Executable:** {{executable_path}}
- **Config:** {{config_path}}
- **Data:** {{data_path}}
- **Logs:** {{log_path}}

### 🔗 uCode Integration
{{#each ucode_integration}}
- **{{this.command}}** - {{this.description}}
  - Script: `{{this.script_path}}`
  - Shortcode: `[{{this.shortcode}}]`
{{/each}}

### 🎯 Task Integration
{{#each task_integration}}
- **{{this.task_label}}**
  - Command: `{{this.command}}`
  - Args: `{{this.args}}`
  - Group: `{{this.group}}`
{{/each}}

---

## 🔍 Troubleshooting

### ⚠️ Common Issues
{{#each common_issues}}
**Issue:** {{this.problem}}  
**Solution:** {{this.solution}}  
**Prevention:** {{this.prevention}}

{{/each}}

### 🧹 Cleanup & Removal
```bash
{{#each cleanup_steps}}
# {{this.description}}
{{this.command}}
{{/each}}
```

---

## 📈 Monitoring & Maintenance

### 📊 Health Checks
- **Status Check:** `[package:status {{package_name}}]`
- **Version Check:** `[package:version {{package_name}}]`
- **Performance Check:** `[package:benchmark {{package_name}}]`

### 🔄 Update Management
- **Check Updates:** `[package:check-updates {{package_name}}]`
- **Auto Update:** `[package:auto-update {{package_name}}]`
- **Rollback:** `[package:rollback {{package_name}} {{version}}]`

---

## 📝 Metadata

```json
{
  "template": {
    "name": "package-template",
    "version": "v2.0.0",
    "category": "{{package_category}}",
    "generated": "{{timestamp}}",
    "variables": {{template_variables}},
    "shortcodes": {{shortcode_list}},
    "integration": {
      "ucode": true,
      "tasks": true,
      "dashboard": true,
      "monitoring": true
    }
  },
  "package": {
    "name": "{{package_name}}",
    "version": "{{package_version}}",
    "status": "{{package_status}}",
    "install_method": "{{installation_method}}",
    "dependencies": {{dependencies_json}},
    "supported_platforms": {{platform_support_json}}
  }
}
```

---

*Generated by uDOS Package Template System v2.0.0*  
*Template Path:* `uTemplate/package-template.md`  
*Package Manager:* `uCode/packages/manager-enhanced.sh`
