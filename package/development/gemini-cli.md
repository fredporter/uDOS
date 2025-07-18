# 🤖 Gemini CLI - AI Assistant for uDOS

**Gemini CLI** provides Google's Gemini AI directly in the terminal, offering intelligent assistance for uDOS development and mission management.

## 🚀 Installation

### Via VS Code Task
1. Press `Cmd+Shift+P`
2. Type "Tasks: Run Task"
3. Select "🤖 Install Gemini CLI"

### Manual Installation
```bash
./uCode/packages/install-gemini.sh
```

## 🎯 Usage

### Basic AI Assistance
```bash
# Ask questions about uDOS
gemini "How do I create a new mission in uDOS?"

# Get coding help
gemini "Write a bash script to find all TODO items in markdown files"

# Analyze log files
cat ./uMemory/logs/latest.log | gemini "Analyze this log file for issues"
```

### uDOS Integration
```bash
# Start Gemini with uDOS context
./uCode/companion-system.sh gemini

# Get mission help
gemini "Based on the uDOS mission template, help me create a mission for user authentication"

# Code review assistance
git diff | gemini "Review this code change for potential issues"
```

## 🧠 AI-Assisted uDOS Workflows

### Mission Development
```bash
# Mission planning
gemini "Create a mission plan for implementing a dashboard feature with the following requirements: real-time data, responsive design, user authentication"

# Mission documentation
gemini "Generate documentation for this mission based on the code changes" < mission-implementation.md

# Mission review
gemini "Review this mission for completeness and suggest improvements" < ./uMemory/missions/mission-001.md
```

### Code Analysis
```bash
# Script analysis
gemini "Analyze this bash script for potential improvements and security issues" < ./uCode/dash.sh

# Template optimization
gemini "Suggest improvements to this template structure" < ./uTemplate/mission-template.md

# Error diagnosis
gemini "Help me debug this error message from uDOS startup" < error.log
```

### Documentation Generation
```bash
# README generation
gemini "Generate a comprehensive README for this uDOS project" 

# API documentation
gemini "Create API documentation for these uCode functions" < ./uCode/ucode.sh

# User guide creation
gemini "Create a user guide for new uDOS users based on the repository structure"
```

## 🔧 Advanced Features

### Context-Aware Assistance
```bash
# Project-specific help
gemini --context "$(find . -name '*.md' -type f | head -10 | xargs cat)" "How can I improve this project structure?"

# File-specific assistance
gemini --file ./uCode/ucode.sh "Explain how this script works and suggest optimizations"

# Multi-file analysis
gemini "Compare these two implementations and recommend the better approach" < file1.sh file2.sh
```

### Integration with uDOS Tools
```bash
# Combined with ripgrep
rg "TODO|FIXME" --json | gemini "Prioritize these TODO items by importance"

# Combined with git
git log --oneline -10 | gemini "Summarize the recent development activity"

# Combined with package status
./uCode/packages/manager-simple.sh list | gemini "Recommend additional packages for this development environment"
```

## 🎯 Chester AI Integration

### Companion System
```bash
# Start Chester with Gemini backend
./uCode/companion-system.sh chester

# Initialize Chester personality
./uCode/companion-system.sh init-chester

# Chester-specific commands
gemini --persona chester "Help me understand the uDOS architecture"
```

### Personality Configuration
```bash
# Configure Chester's personality
export CHESTER_PERSONALITY="helpful,technical,uDOS-expert"
export CHESTER_CONTEXT="uDOS development assistant"

# Custom Chester prompts
gemini --persona chester --context "$UDOS_ROOT" "What should I work on next?"
```

## 📊 Dashboard Integration

### Automated Reporting
```bash
# Generate status reports
./uCode/dash.sh build | gemini "Create an executive summary of this project status"

# Mission progress analysis
fd 'mission-.*\.md$' ./uMemory/missions/ | xargs cat | gemini "Analyze mission progress and identify blockers"

# Package recommendation
cat ./package/manifest.json | gemini "Recommend additional packages that would benefit this development environment"
```

### Intelligent Monitoring
```bash
# Log analysis
tail -100 ./uMemory/logs/udos.log | gemini "Identify any concerning patterns in these logs"

# Performance optimization
gemini "Analyze the uDOS startup sequence and suggest performance improvements" < ./uCode/ucode.sh

# Resource usage analysis
ps aux | grep udos | gemini "Analyze uDOS resource usage and suggest optimizations"
```

## ⚙️ Configuration

### API Setup
```bash
# Set API key (required)
export GEMINI_API_KEY="your-api-key-here"

# Configuration file
cat > ~/.config/gemini/config.yaml << EOF
api_key: ${GEMINI_API_KEY}
model: gemini-pro
temperature: 0.7
max_tokens: 2048
context_window: 4096
EOF
```

### uDOS-Specific Configuration
```bash
# uDOS context file
cat > ~/.config/gemini/udos-context.txt << EOF
uDOS is a development operations system with:
- Mission-based project management
- Template-driven development  
- AI companion integration (Chester)
- Package management system
- Dashboard monitoring
- User role-based permissions (wizard/sorcerer/ghost/imp)
EOF

# Custom aliases
alias ask-udos='gemini --context "$(cat ~/.config/gemini/udos-context.txt)"'
alias chester='gemini --persona chester'
alias mission-help='gemini "Help me with uDOS mission development:"'
```

## 🔒 Security & Privacy

### Best Practices
- Never share API keys in code or logs
- Use environment variables for sensitive configuration
- Review generated code before execution
- Be mindful of data sent to external AI services

### Local Privacy Options
```bash
# Use local AI models when available
export GEMINI_USE_LOCAL=true
export GEMINI_LOCAL_MODEL="local-model-path"

# Data anonymization
gemini --anonymize "Help me with this code structure" < sanitized-code.txt
```

## 🔧 uDOS Integration Features

- **Mission Intelligence**: AI-powered mission planning and review
- **Code Analysis**: Intelligent code review and optimization suggestions
- **Documentation Generation**: Automated documentation creation
- **Error Diagnosis**: AI-assisted troubleshooting and debugging
- **Chester Integration**: Seamless AI companion functionality
- **Dashboard Intelligence**: Smart reporting and analysis
- **Template Optimization**: AI-driven template improvements

---

*Intelligent AI assistance for enhanced uDOS development workflows.*
