# uDOS Input Field Specification

**Type**: Documentation
**Version**: v1.3.3
**Purpose**: Field definition format for uGET interactive forms
**Location**: uMEMORY/system/get/

> **Category**: uGET System Specification
> **Integration**: uMEMORY, uDATA, uCORE systems
> **Format Standard**: uDOS v1.3.3

---

Use this format to define user prompts in Markdown with uDATA integration support. These fields will be rendered dynamically in CLI during onboarding or config steps.

**Template Version**: v1.3.3
**uDATA Support**: locationMap, timezoneMap, countryMap, languageMap, currencyMap
**Last Updated**: August 23, 2025

---

## 🏷️ Field Definition Format

```markdown
## 🏷️ <Display Label>
DATA: <data_key>
ASK: <Question to display in CLI>
DEFAULT: <default_value>
TYPE: <TEXT | PASSWORD | CHOICE | DATE | NUMBER | LOCATION_LOOKUP | TIMEZONE_LOOKUP | AUTO_GENERATE>
uDATA: <dataset_name>  # Reference to JSON dataset for validation/lookup
OPTIONS: [OPTION1, OPTION2, ...]  # only for TYPE: CHOICE
REQUIRED: <TRUE | FALSE>          # optional — assumed TRUE if not present
VALIDATION: <regex_pattern>       # optional validation pattern
HELP: <Additional context or tips shown on hover or on request>  # optional
```

---

### 📌 Enhanced Examples with uDATA Integration:

```markdown
## 👤 Username
DATA: username
ASK: Enter your preferred username
DEFAULT: agentdigital
TYPE: TEXT
REQUIRED: TRUE

## 📍 Location
DATA: location
ASK: Select your location
DEFAULT: LONDON
TYPE: LOCATION_LOOKUP
uDATA: locationMap
HELP: Search from 52 global cities with coordinates

## 🕒 Timezone
DATA: timezone
ASK: Select your timezone
DEFAULT: UTC
TYPE: TIMEZONE_LOOKUP
uDATA: timezoneMap
HELP: Choose from 38 global timezones

## ⏱️ UTC Offset
DATA: utc_offset
ASK: (auto-detected from timezone)
DEFAULT: +00:00
TYPE: AUTO_GENERATE
uDATA: timezoneMap

## 🎨 Theme
DATA: theme
ASK: Choose your interface theme
DEFAULT: DEFAULT
TYPE: CHOICE
OPTIONS: [DEFAULT, CLASSIC, MINIMAL, ASCII]
```

---

### 🔧 Template Integration Features

- **uDATA Lookup**: Real-time validation against JSON datasets
- **Auto-Generation**: Fields that derive from other selections
- **Cross-References**: Automatic population of related fields
- **Validation**: Built-in data validation using uDATA schemas
- **Location Intelligence**: Geographic coordinate integration
- **Timezone Awareness**: UTC offset calculation and DST handling

---

*uDOS v1.3.3 Input Field Specification - uGET System Integration*
