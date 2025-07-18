# 🎯 Enhanced Template System v2.1.0

**uDOS Enhanced Template Engine with Shortcode Integration, Cross-linking, and Dataset Access**  
*Generated: {{instance_time}}*  
*Location: {{instance_location}}*  
*Instance: {{instance_id}}*

---

## 📋 Template Standards & Conventions

### 🔧 Variable Naming Convention

#### Instance Variables (Replace username/location)
```markdown
{{instance_time}}      # Current timestamp (ISO 8601)
{{instance_location}}  # Current system hostname/location  
{{instance_id}}        # Unique instance identifier
{{instance_timezone}}  # System timezone
{{instance_session}}   # Current session ID
```

#### Dataset References
```markdown
{{dataset:cities.london.population}}        # Nested dataset access
{{dataset:countries.australia.capital}}     # Country data lookup
{{dataset:languages.english.speakers}}      # Language statistics
{{dataset:currencies.usd.symbol}}           # Currency information
```

#### Cross-Template Linking
```markdown
{{template:mission.current_status}}         # Reference other template variables
{{template:project.completion_rate}}        # Project template data
{{template:dashboard.metrics.errors}}       # Dashboard metrics
```

#### User Input Variables
```markdown
{{input:project_name}}                      # Required user input
{{input:description|"Default description"}} # Optional with default
{{input:priority|enum:low,medium,high}}     # Enumerated choices
{{input:start_date|date}}                   # Typed input validation
```

### 📊 Shortcode Integration Standards

#### Template Generation Shortcodes
```bash
[template:generate mission]                 # Generate from template
[template:generate mission --name="Project X"] # With parameters
[template:list]                             # List available templates
[template:info mission]                     # Template information
```

#### Dataset Access Shortcodes
```bash
[dataset:cities --filter="population>1000000"] # Filtered dataset query
[dataset:countries.australia]               # Specific data lookup
[dataset:export currencies csv]             # Export dataset
[dataset:search "Tokyo"]                    # Search across datasets
```

#### Cross-Reference Shortcodes
```bash
[ref:mission.current --field=progress]      # Reference other documents
[link:project.readme]                       # Create cross-links
[include:template.header]                   # Include template fragments
```

---

## 🎨 Enhanced Template Structure

### 📄 Universal Template Header
```markdown
# {{document_type}}: {{title}}

**Generated:** {{instance_time}}  
**Instance:** {{instance_location}}  
**Session:** {{instance_session}}  
**Template Version:** {{template_version}}  
**Document ID:** {{document_id}}

> **Type:** {{document_type}}  
> **Category:** {{category}}  
> **Status:** {{status}}  
> **Priority:** {{priority}}

---

## 📊 Metadata Block

**Template System:** {{template_system_version}}  
**Dataset Version:** {{dataset_version}}  
**Cross-References:** {{cross_references_count}}  
**Variables Used:** {{variables_count}}  
**Generated With:** [template:generate {{template_name}}]

### 🔗 Cross-References
{{#each cross_references}}
- **[{{this.type}}:{{this.id}}]({{this.path}})** - {{this.description}}
{{/each}}

### 📊 Related Datasets
{{#each related_datasets}}
- **{{this.name}}** - [dataset:{{this.id}}] - {{this.description}}
{{/each}}
```

### 🎯 Enhanced Variable Processing

#### System Variables (Auto-populated)
```json
{
  "instance_time": "{{auto:current_timestamp}}",
  "instance_location": "{{auto:hostname}}",
  "instance_id": "{{auto:generate_uuid}}",
  "instance_timezone": "{{auto:system_timezone}}",
  "instance_session": "{{auto:session_id}}",
  "template_version": "{{auto:template_version}}",
  "document_id": "{{auto:generate_doc_id}}",
  "dataset_version": "{{auto:dataset_version}}"
}
```

#### Calculated Variables (Dynamic)
```json
{
  "progress_percentage": "{{calc:completed_tasks / total_tasks * 100}}",
  "days_remaining": "{{calc:end_date - current_date}}",
  "team_utilization": "{{calc:allocated_hours / available_hours * 100}}",
  "budget_burn_rate": "{{calc:spent_amount / elapsed_days}}",
  "completion_estimate": "{{calc:remaining_work / daily_velocity}}"
}
```

---

## 🌐 Dataset Integration

### 📊 Available Datasets
```markdown
[dataset:list] # Shows all available datasets

Core Datasets:
- **cities** - {{dataset:cities.count}} major world cities
- **countries** - {{dataset:countries.count}} countries with demographics  
- **languages** - {{dataset:languages.count}} world languages
- **currencies** - {{dataset:currencies.count}} world currencies
- **timezones** - {{dataset:timezones.count}} timezone definitions
- **commands** - {{dataset:ucode_commands.count}} uCode commands
```

### 🔍 Dataset Query Syntax
```bash
# Direct access
{{dataset:cities.london.name}}              # "London"
{{dataset:cities.london.population}}        # 8982000

# Filtered queries  
{{dataset:cities[population>5000000].count}} # Cities over 5M
{{dataset:countries[continent=Asia].list}}   # Asian countries

# Aggregated data
{{dataset:cities.sum(population)}}          # Total population
{{dataset:countries.avg(gdp_per_capita)}}   # Average GDP
{{dataset:currencies.unique(symbol)}}       # Unique symbols
```

### 📈 Dynamic Dataset Updates
```bash
[dataset:update cities]                     # Update from source
[dataset:validate all]                      # Validate all datasets
[dataset:backup]                            # Create backup
[dataset:restore timestamp]                 # Restore from backup
```

---

## 🔗 Cross-Linking System

### 📎 Reference Syntax
```markdown
# Internal document references
{{ref:mission.current_objectives}}          # Reference mission data
{{ref:project.timeline.milestones}}        # Project timeline
{{ref:dashboard.metrics.current}}          # Dashboard metrics

# External references with validation
{{ref:external.github.repo_url}}           # External GitHub repo
{{ref:external.docs.api_endpoint}}         # External API docs
```

### 🌉 Template Inheritance
```markdown
# Inherit from parent template
{{inherit:base_template}}

# Override specific sections
{{override:header.title}}
{{override:footer.generated_by}}

# Include reusable fragments
{{include:standard_header}}
{{include:footer_with_links}}
{{include:shortcode_reference}}
```

---

## 🎮 Interactive Variables & Input

### 📝 Input Variable Types
```bash
# Text input with validation
{{input:project_name|required|min:3|max:50}}

# Enumerated choices
{{input:priority|enum:low,medium,high,critical}}

# Date input with format
{{input:start_date|date|format:YYYY-MM-DD}}

# Numeric input with range
{{input:team_size|number|min:1|max:20}}

# Boolean input
{{input:enable_notifications|boolean|default:true}}

# Array input (comma-separated)
{{input:technologies|array|separator:,}}

# File path input with validation
{{input:config_file|file|exists:true|ext:json}}
```

### 🎯 Conditional Logic
```markdown
{{#if priority == "critical"}}
⚠️ **CRITICAL PRIORITY** - Immediate attention required
{{else if priority == "high"}}
🔥 **HIGH PRIORITY** - Schedule soon
{{else}}
📋 **STANDARD PRIORITY** - Regular workflow
{{/if}}

{{#each team_members}}
- **{{this.name}}** ({{this.role}}) - {{this.allocation}}%
{{/each}}

{{#unless blockers.empty}}
⚠️ **Current Blockers:**
{{#each blockers}}
- {{this.description}} ({{this.severity}})
{{/each}}
{{/unless}}
```

---

## 📊 JSON Configuration Integration

### 🔧 Template Definition Schema
```json
{
  "template_id": "enhanced_mission",
  "name": "Enhanced Mission Template v2.1",
  "version": "2.1.0",
  "category": "planning",
  "description": "Comprehensive mission template with dataset integration",
  
  "variables": {
    "required": [
      {"name": "mission_name", "type": "string", "min": 3, "max": 100},
      {"name": "objective", "type": "text", "min": 10},
      {"name": "priority", "type": "enum", "values": ["low","medium","high","critical"]}
    ],
    "optional": [
      {"name": "description", "type": "text", "default": ""},
      {"name": "team_size", "type": "number", "min": 1, "max": 50, "default": 1}
    ],
    "calculated": [
      {"name": "completion_rate", "formula": "completed_tasks / total_tasks * 100"},
      {"name": "days_remaining", "formula": "end_date - current_date"}
    ]
  },
  
  "datasets_used": [
    {"name": "cities", "fields": ["name", "population", "timezone"]},
    {"name": "countries", "fields": ["name", "capital", "gdp"]},
    {"name": "timezones", "fields": ["offset", "dst"]}
  ],
  
  "cross_references": [
    {"template": "project", "fields": ["status", "team", "budget"]},
    {"template": "dashboard", "fields": ["metrics", "health"]},
    {"external": "github", "fields": ["repo_url", "issues_count"]}
  ],
  
  "shortcodes": [
    {"name": "mission", "args": ["create", "status", "update", "complete"]},
    {"name": "team", "args": ["add", "remove", "list", "assign"]},
    {"name": "progress", "args": ["update", "report", "chart"]}
  ],
  
  "output_formats": ["markdown", "html", "pdf", "json"],
  "auto_update": true,
  "backup_enabled": true
}
```

### 📈 Dataset Integration Config
```json
{
  "dataset_integration": {
    "version": "2.1.0",
    "cache_duration": 3600,
    "auto_refresh": true,
    "validation_enabled": true,
    
    "data_sources": {
      "local": "/Users/{{instance_user}}/uDOS/uTemplate/datasets/",
      "backup": "/Users/{{instance_user}}/uDOS/uMemory/datasets/",
      "external": {
        "cities": "https://api.worldbank.org/cities",
        "countries": "https://restcountries.com/v3.1/all",
        "currencies": "https://api.exchangerate-api.com/v4/currencies"
      }
    },
    
    "query_optimization": {
      "cache_queries": true,
      "index_fields": ["name", "id", "code"],
      "max_results": 1000
    }
  }
}
```

---

## 🚀 Enhanced Shortcode System

### 📋 Template Shortcodes
```bash
# Template management
[template:generate mission --interactive]     # Interactive generation
[template:update mission.md --refresh-data]  # Update with fresh data
[template:validate all]                      # Validate all templates
[template:export mission html]               # Export to HTML

# Variable management  
[var:set project_name "New Project"]         # Set variable
[var:get mission.status]                     # Get variable value
[var:list mission]                           # List template variables
[var:calculate completion_rate]              # Calculate dynamic variable
```

### 📊 Dataset Shortcodes
```bash
# Dataset queries
[dataset:query cities "population > 1000000"] # Query with filter
[dataset:get countries.australia.capital]     # Direct field access
[dataset:join cities countries --on=name]     # Join datasets
[dataset:aggregate cities sum population]     # Aggregate functions

# Dataset management
[dataset:refresh all]                         # Refresh from sources
[dataset:backup --timestamp]                 # Create timestamped backup
[dataset:validate cities --strict]           # Strict validation
[dataset:export currencies csv --filter]     # Filtered export
```

### 🔗 Cross-Reference Shortcodes
```bash
# Document linking
[link:create mission.md project.md]          # Create bidirectional link
[link:validate all]                          # Validate all links
[link:update mission.md]                     # Update link references
[ref:show mission.current_status]            # Show referenced value

# Template inheritance
[inherit:apply base_template mission.md]     # Apply inheritance
[include:fragment header_standard]          # Include fragment
[override:apply custom_footer]               # Apply override
```

---

## 📚 Documentation Standards

### 📖 Template Documentation Format
```markdown
# Template: {{template_name}} v{{template_version}}

## 🎯 Purpose
{{template_description}}

## 📊 Variables Reference
{{#each variables}}
### {{this.name}} {{#if this.required}}(Required){{/if}}
- **Type:** {{this.type}}
- **Description:** {{this.description}}
{{#if this.default}}
- **Default:** {{this.default}}
{{/if}}
{{#if this.validation}}
- **Validation:** {{this.validation}}
{{/if}}
{{/each}}

## 🔗 Dataset Dependencies
{{#each datasets}}
- **{{this.name}}** - {{this.description}}
  - Fields used: {{this.fields_used}}
  - Update frequency: {{this.update_frequency}}
{{/each}}

## 🎮 Available Shortcodes
{{#each shortcodes}}
### [{{this.name}}:{{this.syntax}}]
{{this.description}}

**Example:** `[{{this.name}}:{{this.example}}]`
**Output:** {{this.example_output}}
{{/each}}

## 📋 Usage Examples
```bash
# Generate with minimal input
[template:generate {{template_name}} --name="Example"]

# Generate with full parameters
[template:generate {{template_name}} --interactive --validate]

# Update existing document
[template:update document.md --refresh-datasets]
```

## 🔧 Customization Options
{{template_customization_options}}
```

---

## 🎯 Implementation Checklist

### ✅ Core Features Implemented
- [x] Instance variables (no more username references)
- [x] Dataset integration with cross-reference capability
- [x] Enhanced shortcode system
- [x] Template inheritance and fragments
- [x] Interactive variable input with validation
- [x] JSON configuration integration
- [x] Cross-linking system
- [x] Calculated and dynamic variables

### 🔄 Advanced Features
- [x] Template versioning and backup
- [x] Dataset caching and optimization
- [x] Multi-format export (MD, HTML, PDF)
- [x] Conditional logic and loops
- [x] External data source integration
- [x] Real-time template updates
- [x] Comprehensive error handling
- [x] Performance monitoring

### 📊 Quality Assurance
- [x] Template validation system
- [x] Dataset integrity checks
- [x] Cross-reference validation
- [x] Performance benchmarking
- [x] Comprehensive documentation
- [x] Example templates and datasets
- [x] Migration tools for existing templates

---

*Enhanced Template System v2.1.0*  
*Generated at {{instance_time}} for {{instance_location}}*  
*Ready for production deployment*
