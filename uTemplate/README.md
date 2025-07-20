# uTemplate System - v1.2.0 (Data-Only Templates)

**uTemplate** is the clean, data-focused template repository for uDOS v1.2, providing standardized templates and configuration data for content generation and system operations.

## 🎯 System Philosophy
uTemplate is now organized as a **data-only folder** containing:
- ✅ **Templates** - Markdown template files for content generation
- ✅ **DataGets** - JSON configuration files for data collection  
- ✅ **Examples** - Sample implementations and use cases
- ✅ **Variables** - Template variable definitions and schemas
- ✅ **System** - System template configurations

**Moved to Specialized Folders:**
- 📦 **Installers** → `install/installers/` (platform-specific installation templates)
- 🗺️ **Datasets & Mapping** → `uMapping/` (TypeScript mapping system with geographic datasets)

## 🗂️ Clean Structure Overview

### 🎯 Core Templates (v1.2 Standard)
- **ok-assistant-template.md** - Universal script template with assistant integration (replaces uc-template)
- **project-template.md** - Comprehensive project management with phases, stakeholders, and risk assessment
- **mission-template.md** - Advanced mission planning with KPIs, risk assessment, and uDOS integration
- **milestone-template.md** - Detailed milestone tracking with quality gates and testing strategies
- **input-template.md** - Interactive user input collection with dataset integration
- **input-user-setup.md** - User environment configuration
- **dashboard-template.md** - Real-time project portfolio dashboard with executive summary
- **legacy-template.md** - Legacy system compatibility
- **daily-move-log-v2.md** - Daily activity logging template

### 🛠️ Specialized Templates
- **command-help-template.md** - Documentation template for command help systems
- **vb-command-set-template.md** - VB (Visual Basic) command set documentation
- **package-template.md** - Package configuration and management
- **display-config-template.md** - Display and interface configuration
- **form-configuration-template.md** - Form and input configuration
- **vscode-extension-template.md** - VS Code extension development
- **vscode-workspace-template.md** - VS Code workspace configuration
- **ascii-interface-template.md** - ASCII-based interface design
- **dataget-configuration-template.md** - Data collection configuration

### 📊 Dashboard & Interface Templates  
- **ascii-dashboard-template.txt** - Text-based dashboard layouts
- **system/dash-template.md** - System dashboard components

### � Configuration Data (DataGets)
Clean JSON configuration files:
- **mission-create.json** - Mission creation configuration
- **system-config.json** - System-wide template configuration
- **user-setup.json** - User setup and preferences configuration

## 🛠️ Template Engine Features

### Dynamic Variable Substitution
Templates support dynamic variables with automatic dataset integration:
```markdown
Location: {{location}}
Timezone: {{timezone}}
Currency: {{currency}}
```

## 🛠️ Template Engine Features v2.0

### 🔄 Enhanced Dynamic Variable Substitution
Templates support comprehensive dynamic variables with automatic dataset integration:
```markdown
Location: {{location}}
Timezone: {{timezone}}
Currency: {{currency}}
Project Health: {{health_status}}
Team Allocation: {{team_allocation}}
Budget Status: {{budget_utilization}}%
```

### 📊 Advanced Schema Validation
All datasets include comprehensive JSON schemas for data validation and consistency with enhanced v1.0 features:
- **Type validation** with custom patterns
- **Conditional logic** for template branching
- **Complex object** and array handling
- **Cross-reference validation** between related templates
- **Real-time validation** during template generation

### 🎯 Template Categories
- **Planning**: Project, Mission, Milestone templates with comprehensive tracking
- **Execution**: Enhanced uCode scripts with testing and validation
- **Monitoring**: Real-time dashboards with executive summaries
- **Documentation**: Input templates with dataset integration
- **Legacy**: Backward compatibility support

### 📤 Export Formats
- **Markdown** (primary format with rich formatting)
- **JSON** (structured data with metadata)
- **HTML** (web-ready with CSS styling)
- **PDF** (printable reports via pandoc)
- **CSV/TSV** (data export for analysis)
- **YAML** (configuration file format)

## 🚀 Enhanced Usage with uDOS v1.0

### 🌀 Command Integration
Access enhanced templates through uDOS shell:
```bash
# Template Management
TEMPLATE list                           # Show all available templates
TEMPLATE generate project "My Project"  # Generate comprehensive project
TEMPLATE generate mission "Deploy v1.0" # Create enhanced mission
TEMPLATE generate milestone "Beta Release" # Track detailed milestone

# Advanced Queries
JSON query locationMap "region=Europe&population>1000000"
JSON filter currencyMap "exchange_rate>1.0"
DATASET stats                          # Show dataset statistics

# Integration Commands
ucode.sh template-sync                 # Sync templates with uMemory
dash.sh template-metrics              # Template usage analytics
```

### 🎯 Enhanced Development Workflow
1. **Template Design**: Use enhanced markdown with conditional logic
2. **Schema Definition**: Create comprehensive validation rules
3. **Dataset Integration**: Link with geographic and system data
4. **Variable Mapping**: Define dynamic substitution patterns
5. **Quality Assurance**: Built-in validation and testing
6. **uDOS Integration**: Memory system and dashboard integration
7. **Deployment**: Live template generation and monitoring

### Example Implementation Steps

1. **Extracting Data from Roadmap File**
   ```python
   import json

   def extract_data(roadmap_file):
       with open(roadmap_file, 'r') as file:
           data = json.load(file)
           # Extract relevant datasets
           datasets = {
               "projects": data.get("projects", []),
               "milestones": data.get("milestones", []),
           }
           return datasets
   ```

2. **Creating uTemplate Structure**
   ```html
   <!-- Example uTemplate for a project -->
   <template id="project-template">
       <div class="project">
           <h2>{{ project.name }}</h2>
           <p>{{ project.description }}</p>
           <ul>
               {{#each project.milestones}}
                   <li>{{ this }}</li>
               {{/each}}
           </ul>
       </div>
   </template>
   ```

3. **Rendering the Template with Data**
   ```javascript
   const projects = extract_data('roadmap.json');
   const template = document.getElementById('project-template').innerHTML;

   projects.forEach(project => {
       const rendered = Mustache.render(template, { project });
       document.body.innerHTML += rendered;
   });
   ```

### Conclusion

This outline provides a structured approach to breaking out a dataset from a roadmap file into a template system using uTemplate. Each step can be expanded with more detailed actions based on the specific requirements of your project. Make sure to adapt the implementation to fit the technologies and frameworks you are using.