# Template: uDOS Input Field Template v1.7.1

Use this format to define user prompts in Markdown with dataset integration support. These fields will be rendered dynamically in CLI during onboarding or config steps.

**Template Version:** v1.7.1  
**Dataset Support:** locationMap, timezoneMap, countryMap, languageMap, currencyMap  
**Last Updated:** 2025-07-13

---

## 🏷️ <Display Label>  
DATA: <data_key>  
ASK: <Question to display in CLI>  
DEFAULT: <default_value>  
TYPE: <freetext | password | choice | date | number | location_lookup | timezone_lookup | auto_generate>  
DATASET: <dataset_name>  # Reference to JSON dataset for validation/lookup
OPTIONS: [option1, option2, ...]  # only for TYPE: choice  
REQUIRED: <true | false>          # optional — assumed true if not present  
VALIDATION: <regex_pattern>       # optional validation pattern
HELP: <Additional context or tips shown on hover or on request>  # optional  

---

### 📌 Enhanced Examples with Dataset Integration:

```md
## 👤 Username  
DATA: username  
ASK: Enter your preferred username  
DEFAULT: agentdigital  
TYPE: freetext  
REQUIRED: true

## 📍 Location  
DATA: location  
ASK: Select your location  
DEFAULT: London  
TYPE: location_lookup  
DATASET: locationMap
HELP: Search from 52 global cities with coordinates

## 🕒 Timezone  
DATA: timezone  
ASK: Select your timezone  
DEFAULT: UTC  
TYPE: timezone_lookup  
DATASET: timezoneMap
HELP: Choose from 38 global timezones

## ⏱️ UTC Offset  
DATA: utc_offset  
ASK: (auto-detected from timezone)  
DEFAULT: +00:00  
TYPE: auto_generate  
DATASET: timezoneMap

## 🎨 Theme  
DATA: theme  
ASK: Choose your interface theme  
DEFAULT: modern  
TYPE: choice  
OPTIONS: [modern, classic, minimal, ascii]
```

---

### 🔧 Template Integration Features

- **Dataset Lookup:** Real-time validation against JSON datasets
- **Auto-Generation:** Fields that derive from other selections
- **Cross-References:** Automatic population of related fields
- **Validation:** Built-in data validation using dataset schemas
- **Location Intelligence:** Geographic coordinate integration
- **Timezone Awareness:** UTC offset calculation and DST handling

---
*uDOS Template System v1.7.1 - Dataset Integrated*  
TYPE: choice  
OPTIONS: [ascii, dark, light]  
```
