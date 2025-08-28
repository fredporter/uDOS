# uDOS Get System

**Location**: `uMEMORY/system/get/`
**Purpose**: Interactive forms and data collection wizards
**Version**: v1.3.3
**Updated**: August 23, 2025

## 📝 Interactive Forms & Data Collection

This directory contains uGET files - interactive forms and wizards that collect user input and generate configuration data for uDOS systems using the v1.3.3 standards.

### 🎯 Available Forms

- **`uGET-smart-project-wizard.md`** - Interactive project creation with validation and template integration
- **`uGET-user-onboarding.md`** - User setup and system configuration with v1.3.3 features
- **`uGET-user-setup-form.md`** - Additional user configuration options

### 📖 Documentation

- **`uDOC-get-configuration.md`** - Complete guide for creating GET forms with uDATA integration
- **`uDOC-input-field-specification.md`** - Field definition format and uDATA lookup specifications

## 🔄 How uGET v1.3.3 Works

uGET forms use the latest uDOS v1.3.3 input system to:
1. **Collect Data** - `[get:field_name]` blocks with validation and help
2. **Process Variables** - `[process:calculations]` for computed values
3. **Generate Output** - `[output:file_name]` blocks with template integration
4. **Conditional Logic** - `[conditional:condition]` for dynamic forms
5. **Integration** - Connect with uMEMORY, uDOT templates, and system services

## 🎨 uGET v1.3.3 Format

uGET files use the standardized format:
- **Field Definitions** - `[get:field_name]` with type, validation, defaults
- **Processing Blocks** - `[process:variables]` for calculations
- **Output Generation** - `[output:filename]` with content or template references
- **Conditional Logic** - `[conditional:expression]...[/conditional]`
- **Integration Points** - Direct connection to uDOT templates and uMEMORY storage

## 🔗 Integration Points

- **uMEMORY** - Store collected configuration in structured directories
- **uDOT Templates** - Generate documents using collected data
- **System Config** - Environment variables and shell configuration
- **Dashboard** - Real-time display of form data and status
- **Validation** - Built-in data validation and user guidance

---

*Part of uDOS v1.3.3 System Architecture*
