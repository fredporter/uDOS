# 🤖 uCompanion: Gemini Assistant (Deprecated)

**Template Version:** v1.0
**Created:** 2025-07-18
**Type:** Gemini CLI Integration
**Status:** Deprecated - Use Chester instead

> **⚠️ Deprecated:** This companion is maintained for compatibility only.  
> **Recommended:** Use Chester (🐕) for the full Wizard's Assistant experience with personality and uc-template integration.
> 
> **Purpose:** Basic Gemini CLI access without personality features
> **Migration Path:** Use `./uCode/companion-system.sh chester` instead

---

## 📋 Companion Overview

The Gemini Assistant provides intelligent code analysis and project insights by leveraging Google's Gemini CLI. It serves as a bridge between uDOS workflows and advanced language model capabilities.

### 🔧 Configuration
- **Name:** Gemini Assistant
- **Tool:** @google/gemini-cli
- **Context:** uDOS project-aware
- **Access:** CLI integration

---

## ⚙️ Available Commands

### Core Integration
```bash
# Start interactive Gemini session
./uCode/companion-system.sh gemini

# Project analysis
./uCode/companion-system.sh analyze

# List available companions
./uCode/companion-system.sh list
```

### Direct Gemini Usage
```bash
# In project directory
cd ~/uDOS
gemini
> Analyze this uDOS project structure and suggest improvements

# Code review
gemini
> Review this shell script for best practices and optimization
```

---

## 🎯 Usage Examples

### Project Analysis
- Comprehensive project overview
- Architecture assessment
- Code quality review
- Optimization suggestions

### Code Generation
- uScript function creation
- Template generation
- Workflow automation
- Documentation assistance

### Integration Benefits
- uDOS context awareness
- Template-driven responses
- Shell script optimization
- VS Code workflow enhancement

---

**Created with uc-template approach for consistent companion development**
