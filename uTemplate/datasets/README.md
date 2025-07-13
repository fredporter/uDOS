# 📊 uDOS JSON Dataset & Template System v1.7.1

A comprehensive JSON-based data management and template generation system for uDOS, providing structured data storage, processing capabilities, and dynamic template generation.

## 🎯 Overview

The uDOS JSON system provides:
- **Structured Datasets**: Comprehensive collections of geographic, linguistic, and system data
- **Template Engine**: Dynamic template generation with variable substitution
- **Data Processing**: Import, export, validation, and transformation tools
- **Integration**: Seamless integration with uDOS command system

## 📁 Dataset Collection

### Geographic Data
- **`cityMap.json`** - 36 major world cities with coordinates, population, timezone
- **`countryMap.json`** - 112 countries with ISO codes, regions, capitals, demographics
- **`timezoneMap.json`** - 36 timezone definitions with offsets and DST information

### Language & Currency Data  
- **`languageMap.json`** - 53 world languages with native names, writing systems, speaker counts
- **`currencyMap.json`** - 51 world currencies with symbols, countries, numeric codes

### System Data
- **`ucode-commands.json`** - 50 uCode commands with syntax, examples, categorization
- **`template-definitions.json`** - 9 template definitions with variables and validation
- **`template-system-config.json`** - Template engine configuration and processing rules

## 🔧 Command Line Tools

### JSON Dataset Processor (`json-processor.sh`)

```bash
# List all datasets
./uCode/json-processor.sh list

# Show dataset information
./uCode/json-processor.sh info cityMap

# Search across all datasets
./uCode/json-processor.sh search "London"

# Export to different formats
./uCode/json-processor.sh export cityMap csv
./uCode/json-processor.sh export countryMap yaml

# Merge multiple datasets
./uCode/json-processor.sh merge worldData cityMap countryMap

# Validate all datasets
./uCode/json-processor.sh validate

# Show statistics summary
./uCode/json-processor.sh stats
```

### Template Generator (`template-generator.sh`)

```bash
# List available templates
./uCode/template-generator.sh list

# Show template information
./uCode/template-generator.sh info mission

# Generate single template
./uCode/template-generator.sh generate mission my-project

# Generate with variables
./uCode/template-generator.sh generate mission my-project \
  '{"mission_name":"AI Project","priority":"high","start_date":"2025-07-13"}'

# Batch generate from CSV file
./uCode/template-generator.sh batch batch-file.csv

# Validate template definition
./uCode/template-generator.sh validate mission

# List generated templates
./uCode/template-generator.sh generated

# Create sample batch file
./uCode/template-generator.sh sample
```

## 🏗️ Integrated uCode Commands

All JSON and template functionality is accessible through the main uDOS shell:

```bash
# Start uDOS shell
./uCode/ucode.sh

# JSON dataset commands
json list                      # List all datasets
json info cityMap              # Dataset information
json search "Tokyo"            # Search across datasets
json export cityMap csv        # Export to CSV
json validate                  # Validate all datasets
json stats                     # Show statistics

# Template commands
template list                  # List templates
template info mission          # Template information  
template generate mission my-project  # Generate template
template batch file.csv        # Batch generation
template validate mission      # Validate template
template generated             # List generated files
```

## 📋 Available Templates

### Planning Templates
- **`mission`** - Project mission definition with objectives and timeline
- **`milestone`** - Project milestones with deliverables and success criteria

### Action Templates  
- **`move`** - Individual actions and moves within projects
- **`input`** - User input and data collection

### Development Templates
- **`uc`** - uCode script templates with documentation structure

### Data Templates
- **`dataset_map_city`** - City mapping and geographic data
- **`dataset_time_space`** - Temporal and spatial data organization

### Configuration Templates
- **`user_setup`** - User configuration and setup processes
- **`legacy`** - Legacy system documentation and migration plans

## 🔍 Dataset Examples

### City Data Sample
```json
{
  "TILE": "CF35",
  "CITY": "Tokyo", 
  "COUNTRY": "Japan",
  "LAT": 35.6762,
  "LON": 139.6503,
  "POPULATION": 37400000,
  "TIMEZONE": "JST",
  "REGION": "Asia"
}
```

### Country Data Sample
```json
{
  "ISO2": "JP",
  "ISO3": "JPN", 
  "NAME": "Japan",
  "CAPITAL": "Tokyo",
  "REGION": "Asia",
  "SUBREGION": "Eastern Asia",
  "POPULATION": 126476461,
  "AREA": 377930,
  "CURRENCY": "JPY",
  "LANGUAGES": ["Japanese"],
  "TIMEZONE": "UTC+9"
}
```

### Command Data Sample
```json
{
  "command": "PRINT",
  "category": "output",
  "syntax": "PRINT <string|variable>",
  "description": "Output text or variable value to console",
  "examples": ["PRINT \"Hello World\"", "PRINT $username"],
  "version": "1.0.0"
}
```

## 🎨 Template System Features

### Variable Types
- **`string`** - Text values
- **`text`** - Multi-line content
- **`number`** - Numeric values
- **`boolean`** - True/false values
- **`date`** - Date values (YYYY-MM-DD)
- **`datetime`** - Date/time values (ISO 8601)
- **`email`** - Email addresses
- **`url`** - Web URLs
- **`path`** - File/directory paths
- **`enum`** - Predefined options
- **`array`** - Lists of values
- **`object`** - JSON objects

### Output Formats
- **Markdown** (`.md`) - Structured documentation
- **JSON** (`.json`) - Data interchange format
- **CSV** (`.csv`) - Tabular data
- **YAML** (`.yml`) - Configuration format
- **HTML** (`.html`) - Web content
- **Text** (`.txt`) - Plain text

### Processing Features
- **Variable Substitution** - `{{variable_name}}`
- **Conditional Blocks** - `{{#if condition}}...{{/if}}`
- **Loops** - `{{#each array}}...{{/each}}`
- **Includes** - `{{>partial_name}}`
- **Validation** - Type checking and required field validation
- **Error Handling** - Comprehensive error reporting

## 📊 Dataset Statistics

- **Total Datasets**: 9 collections
- **Total Records**: 300+ data entries
- **Total Size**: ~80KB of structured data
- **Languages Covered**: 53 world languages
- **Countries Covered**: 112 nations
- **Cities Covered**: 36 major metropolitan areas
- **Timezones**: 36 timezone definitions
- **Currencies**: 51 world currencies
- **Commands**: 50 uCode system commands

## 🔄 Data Integration Workflows

### 1. Dataset Import/Export
```bash
# Export cityMap to CSV for external analysis
json export cityMap csv /path/to/output

# Import processed data back to JSON
# (Manual process - convert CSV back to JSON format)
```

### 2. Template-Based Content Generation
```bash
# Create batch file for multiple projects
template sample
# Edit the generated batch file
template batch sample-batch.csv
```

### 3. Data Analysis and Search
```bash
# Find all cities in Asia
json search "Asia"

# Find all countries using Euro currency
json search "EUR"

# Find all commands in output category
json search "output"
```

### 4. System Integration
```bash
# Generate mission templates for all team projects
for project in alpha beta gamma; do
  template generate mission "$project-mission" \
    "{\"mission_name\":\"Project $project\",\"priority\":\"high\"}"
done
```

## 🎯 Use Cases

### 1. **Project Management**
- Generate mission and milestone templates
- Track project moves and actions
- Document user requirements and input

### 2. **Geographic Analysis** 
- City-based location mapping
- Country demographic analysis
- Timezone coordination for global teams

### 3. **Localization**
- Language and currency mapping
- Multi-regional content generation
- Cultural context data

### 4. **System Documentation**
- Command reference generation
- API documentation templates
- Configuration management

### 5. **Data Processing**
- Export datasets for external analysis
- Merge related datasets for comprehensive views
- Validate data integrity across the system

## 🚀 Future Enhancements

### Planned Features
- **Advanced Query Language** - SQL-like querying of JSON datasets
- **Real-time Data Updates** - Dynamic dataset synchronization
- **Custom Data Types** - User-defined validation patterns
- **Template Inheritance** - Base template extension capabilities
- **API Integration** - REST API for external data access
- **Visualization** - Chart and graph generation from datasets
- **Version Control** - Dataset change tracking and rollback

### Integration Roadmap
- **Database Backends** - PostgreSQL, MongoDB integration
- **Cloud Storage** - AWS S3, Google Cloud Storage sync
- **External APIs** - Live data feeds from geographic and economic APIs
- **Machine Learning** - Pattern recognition and data insights
- **Automation** - Scheduled data updates and template generation

## 📖 Documentation

- **Dataset Schemas**: Each dataset includes metadata describing structure
- **Template Definitions**: Comprehensive variable documentation
- **API Reference**: Command-line interface documentation
- **Examples**: Real-world usage scenarios and sample files
- **Error Codes**: Comprehensive error handling documentation

---

*The uDOS JSON Dataset & Template System provides a robust foundation for structured data management and dynamic content generation, supporting everything from geographic analysis to project management workflows.*
