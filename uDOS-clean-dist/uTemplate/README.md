# uTemplate System - v1.7.1

**uTemplate** is the centralized template and dataset management system for uDOS, providing standardized templates and comprehensive geographic, linguistic, and system datasets.

## 🗂️ Structure Overview

### Core Templates
- **input-template.md** - Interactive user input collection
- **input-user-setup.md** - User environment configuration
- **legacy-template.md** - Legacy system compatibility
- **milestone-template.md** - Project milestone tracking
- **mission-template.md** - Mission creation and management
- **move-template.md** - Individual move documentation
- **uc-template.md** - uCode command template

### 🗄️ Datasets (JSON)
Complete dataset collection with 355+ records across 11 datasets:

#### Geographic & Location Data
- **locationMap.json** (52 cities) - Global city coordinates with map tile integration
- **mapTerrain.json** (15 symbols) - ASCII terrain symbols for cartography
- **timezoneMap.json** (38 zones) - Global timezone data with map references
- **countryMap.json** (195 countries) - ISO country codes and regional data
- **cityMap.json** (50 cities) - Major world cities with coordinates

#### Language & Currency Data  
- **languageMap.json** (50 languages) - ISO language codes and regional usage
- **currencyMap.json** (168 currencies) - Global currency data with exchange rates

#### System Data
- **ucode-commands.json** (9 commands) - uDOS command definitions
- **template-definitions.json** (9 templates) - Template schema and metadata
- **template-system-config.json** - Template engine configuration
- **dataset-metadata.json** - Dataset versioning and schema definitions

## 🛠️ Template Engine Features

### Dynamic Variable Substitution
Templates support dynamic variables with automatic dataset integration:
```markdown
Location: {{location}}
Timezone: {{timezone}}
Currency: {{currency}}
```

### Schema Validation
All datasets include comprehensive JSON schemas for data validation and consistency.

### Export Formats
- JSON (native)
- CSV export capability
- YAML conversion
- TSV format support
- Plain text output

## 🚀 Usage with uDOS

### Command Integration
Access templates through uDOS shell:
```bash
TEMPLATE list
TEMPLATE generate mission-template
JSON query locationMap "region=Europe"
```

### Development Workflow
1. Define template structure using markdown
2. Create dataset schemas with validation rules
3. Generate templates with variable substitution
4. Export in required formats
5. Integrate with uDOS commands

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