# 📚 uDOS Template Format Specification v2.1.0

**Comprehensive Template Development & Expansion Guide**  
*Generated: {{instance_time}}*  
*Instance: {{instance_location}}*  
*Document ID: TFS-2.1.0-{{instance_session}}*

---

## 🎯 Template Format Standards

### 📋 Universal Template Header Format

```markdown
# {{document_type}}: {{title}}

**Template Version:** v2.1.0  
**Generated:** {{instance_time}}  
**Instance:** {{instance_location}}  
**Session:** {{instance_session}}  
**Document ID:** {{document_id}}  
{{#if category}}**Category:** {{category}}{{/if}}  
{{#if priority}}**Priority:** {{priority}}{{/if}}

> **Type:** {{document_type}}  
> **Purpose:** {{purpose}}  
> **Status:** {{status}}  
> {{#if dependencies}}**Dependencies:** {{dependencies}}{{/if}}

## 📊 Metadata Block

**Template System:** v2.1.0  
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

---
```

### 🔧 Variable Types & Syntax

#### 1. Instance Variables (Auto-Generated)
```markdown
{{instance_time}}      # Current timestamp (ISO 8601)
{{instance_location}}  # System hostname/location  
{{instance_id}}        # Unique instance identifier
{{instance_session}}   # Current session ID
{{instance_timezone}}  # System timezone
```

#### 2. Input Variables (User Input Required)
```markdown
# Basic input types
{{input:variable_name}}                           # Simple text input
{{input:variable_name|type}}                      # Typed input
{{input:variable_name|type|validation}}           # With validation
{{input:variable_name|type|validation|default}}   # With default value

# Specific examples
{{input:project_name|string|required|min:3|max:50}}
{{input:priority|enum|values:low,medium,high,critical}}
{{input:start_date|date|required|format:YYYY-MM-DD}}
{{input:team_size|number|min:1|max:20|default:1}}
{{input:enable_notifications|boolean|default:true}}
{{input:technologies|array|separator:,|min_items:1}}
{{input:config_file|file|exists:true|extension:json}}
```

#### 3. Dataset References
```markdown
# Direct field access
{{dataset:collection.key.field}}
{{dataset:cities.london.population}}
{{dataset:countries.australia.capital}}
{{dataset:currencies.usd.symbol}}

# Filtered queries
{{dataset:collection[filter].operation}}
{{dataset:cities[population>1000000].count}}
{{dataset:countries[continent=Asia].list}}
{{dataset:currencies[region=Europe].unique(symbol)}}

# Aggregated operations
{{dataset:collection.operation(field)}}
{{dataset:cities.sum(population)}}
{{dataset:countries.avg(gdp_per_capita)}}
{{dataset:languages.count()}}
```

#### 4. Cross-Reference Variables
```markdown
# Template references
{{ref:template.field}}
{{ref:mission.current_status}}
{{ref:project.completion_rate}}
{{ref:dashboard.metrics.errors}}

# External references  
{{ref:external.type.field}}
{{ref:external.github.repo_url}}
{{ref:external.docs.api_endpoint}}
```

#### 5. Calculated Variables
```markdown
# Mathematical calculations
{{calc:formula}}
{{calc:completed_tasks / total_tasks * 100}}
{{calc:end_date - current_date}}
{{calc:budget * tax_rate}}

# Function-based calculations
{{calc:function(parameters)}}
{{calc:sum(task_estimates)}}
{{calc:avg(team_velocity)}}
{{calc:max(milestone_dates)}}
```

### 🎮 Conditional Logic & Loops

#### Conditional Statements
```markdown
{{#if condition}}
Content when true
{{else if other_condition}}
Content for other condition
{{else}}
Default content
{{/if}}

# Real examples
{{#if priority == "critical"}}
⚠️ **CRITICAL PRIORITY** - Immediate attention required
{{else if priority == "high"}}
🔥 **HIGH PRIORITY** - Schedule soon
{{else}}
📋 **STANDARD PRIORITY** - Regular workflow
{{/if}}
```

#### Loop Constructs
```markdown
{{#each collection}}
- {{this.field}} - {{this.other_field}}
{{/each}}

# Real example
{{#each team_members}}
- **{{this.name}}** ({{this.role}}) - {{this.allocation}}% allocation
{{/each}}

# With conditionals in loops
{{#each milestones}}
{{#if this.completed}}
✅ **{{this.name}}** - Completed {{this.completion_date}}
{{else}}
🔄 **{{this.name}}** - Due {{this.due_date}}
{{/if}}
{{/each}}
```

#### Unless Statements
```markdown
{{#unless condition}}
Content when condition is false
{{/unless}}

# Real example
{{#unless blockers.empty}}
⚠️ **Current Blockers:**
{{#each blockers}}
- {{this.description}} ({{this.severity}})
{{/each}}
{{/unless}}
```

---

## 📊 Dataset Integration Standards

### 🗂️ Supported Dataset Types

#### Geographic Datasets
```markdown
# Cities dataset
{{dataset:cities.london.name}}           # "London"
{{dataset:cities.london.population}}     # 8982000
{{dataset:cities.london.coordinates}}    # [51.5074, -0.1278]
{{dataset:cities.london.timezone}}       # "Europe/London"

# Countries dataset  
{{dataset:countries.australia.name}}     # "Australia"
{{dataset:countries.australia.capital}}  # "Canberra"
{{dataset:countries.australia.iso_code}} # "AU"
{{dataset:countries.australia.continent}} # "Oceania"

# Timezones dataset
{{dataset:timezones.aest.name}}          # "Australian Eastern Standard Time"
{{dataset:timezones.aest.offset}}        # "+10:00"
{{dataset:timezones.aest.dst}}           # true
```

#### Language & Cultural Datasets
```markdown
# Languages dataset
{{dataset:languages.english.name}}       # "English"
{{dataset:languages.english.native_name}} # "English"
{{dataset:languages.english.speakers}}   # 1500000000
{{dataset:languages.english.writing_system}} # "Latin"

# Currencies dataset
{{dataset:currencies.usd.name}}          # "US Dollar"
{{dataset:currencies.usd.symbol}}        # "$"
{{dataset:currencies.usd.code}}          # "USD"
{{dataset:currencies.usd.countries}}     # ["US", "EC", "SV", ...]
```

#### System & Command Datasets
```markdown
# uCode commands dataset
{{dataset:ucode_commands.dash.description}} # "Dashboard management"
{{dataset:ucode_commands.dash.syntax}}      # "dash [action] [options]"
{{dataset:ucode_commands.dash.examples}}    # ["dash refresh", "dash live"]

# Package registry dataset
{{dataset:packages.ripgrep.status}}      # "installed"
{{dataset:packages.ripgrep.version}}     # "13.0.0"
{{dataset:packages.ripgrep.install_date}} # "2025-07-18"
```

### 🔍 Query Syntax Reference

#### Basic Queries
```markdown
# Direct access
{{dataset:collection.key.field}}

# With fallback
{{dataset:collection.key.field|"default_value"}}

# Type casting
{{dataset:collection.key.field|type:number}}
{{dataset:collection.key.field|type:date}}
{{dataset:collection.key.field|type:boolean}}
```

#### Filtered Queries
```markdown
# Comparison operators
{{dataset:cities[population > 1000000]}}
{{dataset:countries[gdp_per_capita >= 50000]}}
{{dataset:languages[speakers < 10000000]}}

# String matching
{{dataset:cities[name contains "New"]}}
{{dataset:countries[continent = "Europe"]}}
{{dataset:languages[writing_system != "Latin"]}}

# Array operations
{{dataset:currencies[countries contains "US"]}}
{{dataset:cities[coordinates in_bounds(lat1,lon1,lat2,lon2)]}}
```

#### Aggregation Functions
```markdown
# Counting
{{dataset:cities.count()}}                    # Total cities
{{dataset:cities[population > 1000000].count()}} # Cities over 1M

# Mathematical operations
{{dataset:cities.sum(population)}}            # Total population
{{dataset:countries.avg(gdp_per_capita)}}     # Average GDP
{{dataset:cities.max(population)}}            # Largest city
{{dataset:currencies.min(exchange_rate)}}     # Lowest rate

# Unique values
{{dataset:countries.unique(continent)}}       # Unique continents
{{dataset:languages.unique(writing_system)}}  # Unique writing systems
```

---

## 🔗 Cross-Reference System

### 📎 Reference Types

#### Internal Template References
```markdown
# Syntax: {{ref:template.field.subfield}}
{{ref:mission.objectives}}                # Mission objectives
{{ref:project.timeline.milestones}}       # Project milestones
{{ref:team.members.skills}}               # Team skills
{{ref:dashboard.metrics.completion_rate}} # Dashboard metrics
```

#### External Document References
```markdown
# File-based references
{{ref:file:path/to/document.md.field}}
{{ref:file:../project/readme.md.status}}
{{ref:file:./team.md.member_count}}

# URL-based references
{{ref:url:https://api.github.com/repos/user/repo.stargazers_count}}
{{ref:url:https://api.service.com/status.health}}
```

#### Bidirectional Linking
```markdown
# Create automatic bidirectional links
[link:create mission.md project.md "Related project"]
[link:update mission.md]                   # Update all links
[link:validate all]                        # Validate all links
```

### 🔄 Reference Validation

#### Reference Checking
```markdown
# Validate single reference
[ref:validate mission.current_status]

# Validate all references in document
[ref:validate mission.md]

# Validate all references in system
[ref:validate all --fix]
```

#### Error Handling
```markdown
# With fallback values
{{ref:mission.deadline|"Not set"}}
{{ref:project.budget|0}}
{{ref:team.size|1}}

# With error messages
{{ref:project.status|error:"Project status not available"}}
{{ref:team.lead|warning:"Team lead not assigned"}}
```

---

## 🎮 Shortcode Integration

### 📋 Template Management Shortcodes

#### Generation Commands
```bash
# Basic generation
[template:generate template_name]
[template:generate mission]
[template:generate project --name="Alpha"]

# Interactive generation
[template:generate mission --interactive]
[template:generate project --interactive --validate]

# Batch generation
[template:generate mission,project,dashboard --batch]
```

#### Template Information
```bash
# List templates
[template:list]
[template:list --category=planning]
[template:list --format=json]

# Template details
[template:info mission]
[template:info mission --detail=full]
[template:info mission --detail=variables]

# Template validation
[template:validate mission]
[template:validate all --strict]
```

### 📊 Dataset Access Shortcodes

#### Query Commands
```bash
# Basic queries
[dataset:query cities "population > 1000000"]
[dataset:get cities.london.population]
[dataset:search "Tokyo"]

# Advanced queries
[dataset:join cities countries --on=name]
[dataset:aggregate cities sum population]
[dataset:filter countries continent=Asia]
```

#### Data Management
```bash
# Data updates
[dataset:update cities]
[dataset:refresh all]
[dataset:validate cities --strict]

# Data export
[dataset:export cities csv]
[dataset:export countries json --filter="gdp>50000"]
[dataset:backup --timestamp]
```

### 🔗 Reference Management Shortcodes

#### Link Management
```bash
# Create links
[ref:link mission.md project.md]
[ref:link mission.md team.md --description="Team assignment"]

# Reference validation
[ref:validate mission.md]
[ref:validate all --fix]

# Reference display
[ref:show mission.objectives --format=block]
[ref:list mission.md]
```

---

## 📝 Template Development Guidelines

### 🏗️ Template Structure Standards

#### File Organization
```
uTemplate/
├── category/
│   ├── template-name.md          # Main template file
│   ├── template-name.json        # Configuration file
│   └── fragments/                # Reusable fragments
│       ├── header.md
│       ├── footer.md
│       └── metadata.md
├── datasets/                     # Dataset files
└── examples/                     # Example outputs
```

#### Template Naming Convention
```markdown
# File naming: category-purpose-version.md
planning-mission-v2.1.md
tracking-milestone-v1.0.md
reporting-dashboard-v2.0.md

# Template ID: category_purpose
planning_mission
tracking_milestone
reporting_dashboard
```

### 🔧 Configuration File Format

#### Template Configuration (`template-name.json`)
```json
{
  "template_id": "category_purpose",
  "name": "Human Readable Name",
  "version": "2.1.0",
  "category": "planning|tracking|reporting|documentation",
  "description": "Detailed template description",
  "author": "Template author",
  "created": "2025-07-18",
  "last_updated": "2025-07-18",
  
  "variables": {
    "instance": [
      {"name": "instance_time", "type": "datetime", "auto": true},
      {"name": "instance_location", "type": "string", "auto": true},
      {"name": "document_id", "type": "uuid", "auto": true}
    ],
    "required_input": [
      {"name": "title", "type": "string", "min": 3, "max": 100},
      {"name": "description", "type": "text", "min": 10}
    ],
    "optional_input": [
      {"name": "priority", "type": "enum", "values": ["low","medium","high"], "default": "medium"},
      {"name": "due_date", "type": "date", "format": "YYYY-MM-DD"}
    ],
    "calculated": [
      {"name": "progress", "formula": "completed / total * 100"},
      {"name": "days_remaining", "formula": "due_date - current_date"}
    ],
    "dataset_references": [
      {"dataset": "cities", "fields": ["name", "population"]},
      {"dataset": "timezones", "fields": ["offset", "name"]}
    ],
    "cross_references": [
      {"template": "project", "fields": ["status", "timeline"]},
      {"template": "team", "fields": ["members", "allocation"]}
    ]
  },
  
  "validation": {
    "required_fields": ["title", "description"],
    "field_validation": {
      "title": {"min_length": 3, "max_length": 100},
      "priority": {"allowed_values": ["low", "medium", "high"]},
      "due_date": {"format": "YYYY-MM-DD", "future_date": true}
    },
    "dataset_validation": true,
    "cross_reference_validation": true
  },
  
  "output_formats": ["markdown", "html", "pdf"],
  "features": ["dataset_integration", "cross_references", "shortcodes"],
  "shortcodes": [
    {"name": "template_action", "args": ["create", "update", "delete"]},
    {"name": "data_action", "args": ["query", "filter", "export"]}
  ],
  
  "fragments": {
    "header": "fragments/standard-header.md",
    "footer": "fragments/standard-footer.md",
    "metadata": "fragments/metadata-block.md"
  },
  
  "dependencies": [],
  "tags": ["planning", "project", "management"],
  "documentation": "docs/template-name-guide.md"
}
```

### 📊 Quality Assurance Standards

#### Validation Checklist
- [ ] **Variables**: All variables properly typed and validated
- [ ] **Datasets**: All dataset references exist and are valid
- [ ] **Cross-References**: All references point to valid targets
- [ ] **Shortcodes**: All shortcodes are properly defined and functional
- [ ] **Conditional Logic**: All conditions are logically sound
- [ ] **Output Formats**: Template renders correctly in all supported formats
- [ ] **Documentation**: Template includes comprehensive usage documentation
- [ ] **Examples**: Template includes working examples
- [ ] **Performance**: Template processes efficiently with large datasets
- [ ] **Error Handling**: Template handles missing data gracefully

#### Testing Requirements
```bash
# Template validation
[template:validate template_name --strict]

# Variable validation
[var:validate template_name --check-types]

# Dataset validation
[dataset:validate all --check-references]

# Cross-reference validation
[ref:validate template_name --check-paths]

# Performance testing
[template:benchmark template_name --iterations=100]

# Output validation
[template:test template_name --all-formats]
```

---

## 🚀 Expansion & Development Patterns

### 📈 Template Extension Patterns

#### Inheritance Pattern
```markdown
# Base template (base-template.md)
{{inherit:base_metadata}}
{{inherit:base_header}}
<!-- Template-specific content -->
{{inherit:base_footer}}

# Extended template (extended-template.md)
{{extend:base-template}}
{{override:header_title}}
<!-- Additional content -->
{{include:custom_sections}}
```

#### Composition Pattern
```markdown
# Using fragments
{{include:fragments/header}}
{{include:fragments/metadata}}
<!-- Main content -->
{{include:fragments/footer}}

# Dynamic inclusion based on variables
{{#if include_analytics}}
{{include:fragments/analytics}}
{{/if}}

{{#if output_format == "pdf"}}
{{include:fragments/pdf_styling}}
{{/if}}
```

#### Plugin Pattern
```markdown
# Plugin integration points
{{plugin:before_content}}
<!-- Main template content -->
{{plugin:after_content}}

# Conditional plugins
{{#if enable_ai_assistance}}
{{plugin:ai_suggestions}}
{{/if}}

{{#if enable_collaboration}}
{{plugin:collaboration_tools}}
{{/if}}
```

### 🔄 Version Management

#### Versioning Strategy
```markdown
# Version format: MAJOR.MINOR.PATCH
v2.1.0 - Major feature additions
v2.0.1 - Bug fixes and minor improvements
v1.9.0 - New features, backward compatible

# Version metadata in templates
**Template Version:** v{{template_version}}
**Compatible Versions:** >= v2.0.0
**Migration Required:** {{migration_required}}
```

#### Migration Support
```bash
# Migration commands
[template:migrate template_name --from=v1.0 --to=v2.0]
[template:check_compatibility template_name]
[template:backup_before_migration template_name]

# Batch migration
[template:migrate_all --from=v1.x --to=v2.0 --backup]
```

### 📚 Documentation Standards

#### Template Documentation Format
```markdown
# Template Name v2.1.0

## 🎯 Purpose
Brief description of template purpose and use cases.

## 📊 Variables Reference
Complete list of all variables with types, descriptions, and examples.

## 🔗 Dependencies
List of required datasets, other templates, and external dependencies.

## 🎮 Shortcodes
Available shortcodes with syntax and examples.

## 📝 Usage Examples
Working examples with different variable combinations.

## 🔧 Customization Options
Guide for customizing the template for specific needs.

## 📈 Performance Notes
Information about template performance and optimization tips.

## 🔄 Version History
Change log and migration information.
```

---

## 🎯 Future Development Roadmap

### 📅 Planned Features (v2.2.0)
- **AI-Assisted Generation**: Natural language to template conversion
- **Real-time Collaboration**: Multi-user template editing
- **Advanced Analytics**: Template usage analytics and optimization
- **Visual Template Builder**: GUI for template creation
- **Plugin Architecture**: Extensible plugin system
- **API Integration**: REST API for external tool integration

### 🔮 Vision (v3.0.0)
- **Machine Learning**: Predictive template suggestions
- **Natural Language Processing**: Intelligent content generation
- **Integration Ecosystem**: Deep integration with external tools
- **Mobile Support**: Mobile template editing and generation
- **Cloud Synchronization**: Cross-device template synchronization

---

*Template Format Specification v2.1.0*  
*Comprehensive guide for uDOS template development and expansion*  
*Generated at {{instance_time}} for {{instance_location}}*
