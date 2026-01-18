# AI Knowledge Bank

**Purpose**: Store perfected AI instructions for offline replication.

The idea: Use Gemini (online) to perfect instructions, then store them here for offline use with local models (Ollama) or cached execution.

---

## Directory Structure

```
knowledge/ai/
├── README.md                    # This file
├── instruction.schema.json      # JSON schema for instructions
├── coding/                      # Code-related instructions
│   ├── fix-python-errors.json
│   ├── refactor-function.json
│   └── add-type-hints.json
├── writing/                     # Documentation/writing
│   ├── technical-docs.json
│   └── readme-generator.json
├── image/                       # Image generation prompts
│   ├── technical-kinetic.json
│   ├── teletext-style.json
│   └── ascii-art.json
├── workflow/                    # Task workflows
│   ├── code-review.json
│   └── project-setup.json
├── analysis/                    # Analysis tasks
│   ├── log-analysis.json
│   └── error-diagnosis.json
└── creative/                    # Creative tasks
    ├── brainstorm.json
    └── naming-conventions.json
```

---

## Instruction Format

Each instruction is a JSON file following `instruction.schema.json`:

```json
{
  "instruction": {
    "id": "fix-python-errors",
    "title": "Fix Python Errors",
    "purpose": "Analyze and fix syntax/logic errors in Python code",
    "category": "coding",
    "prompt": "Analyze this Python code and fix any errors:\n\n{{code}}\n\nProvide:\n1. List of issues found\n2. Fixed code\n3. Explanation of changes",
    "variables": [
      {"name": "code", "description": "Python code to fix", "required": true}
    ]
  },
  "metadata": {
    "version": "1.0.0",
    "created": "2026-01-06",
    "author": "uDOS Dev",
    "source_provider": "gemini",
    "iterations": 5,
    "quality_score": 8.5
  },
  "execution": {
    "offline_capable": true,
    "recommended_model": "deepseek-coder:6.7b",
    "fallback_models": ["codellama:7b", "mistral:7b"],
    "temperature": 0.3
  }
}
```

---

## Workflow: Perfecting Instructions

### 1. Draft (Human)
Start with a rough prompt idea.

### 2. Refine (Gemini Online)
Use Gemini to iterate and improve:
```
OK ASK "Help me perfect this instruction for fixing Python errors.
Current version: [draft]
Goal: Reliable, consistent results with local models"
```

### 3. Test (Ollama Local)
Test with local models to ensure offline compatibility.

### 4. Score & Save
Rate quality (0-10), save to knowledge bank.

### 5. Iterate
Update based on real-world usage.

---

## Usage in uDOS

### TUI Commands

```bash
# List available instructions
KB LIST coding

# Show instruction details
KB SHOW fix-python-errors

# Run instruction with input
KB RUN fix-python-errors --code "def foo( return 42"

# Search instructions
KB SEARCH "python error"
```

### In uPY Scripts

```python
# Load and use instruction
KB LOAD fix-python-errors
KB SET code "def foo( return 42"
KB RUN
```

### Via API

```
GET /api/kb/instructions
GET /api/kb/instructions/fix-python-errors
POST /api/kb/run/fix-python-errors {"code": "..."}
```

---

## Two-Realm Integration

```
┌─────────────────────────────────────────────────────────┐
│ Realm B: Wizard Server (Online)                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Gemini API                                          │ │
│ │ - Perfect instructions iteratively                  │ │
│ │ - Test with various inputs                          │ │
│ │ - Score and validate                                │ │
│ └───────────────────────┬─────────────────────────────┘ │
│                         │ Save to Knowledge Bank        │
│                         ▼                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ knowledge/ai/*.json                                 │ │
│ │ - Perfected instructions                            │ │
│ │ - Versioned, scored, documented                     │ │
│ └───────────────────────┬─────────────────────────────┘ │
│                         │ Sync via Private Transport    │
├─────────────────────────┼───────────────────────────────┤
│ Realm A: Device Mesh    │ (Offline)                     │
│                         ▼                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Local Execution                                     │ │
│ │ - Ollama with local models                          │ │
│ │ - Use perfected instructions                        │ │
│ │ - Consistent, reliable results                      │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Quality Guidelines

### Good Instructions Have:
- Clear, specific purpose
- Well-defined variables
- Multiple tested examples
- Appropriate temperature setting
- Fallback models tested

### Quality Score Meaning:
| Score | Meaning |
|-------|---------|
| 9-10 | Production ready, highly reliable |
| 7-8 | Good, occasional edge cases |
| 5-6 | Usable, needs refinement |
| 3-4 | Experimental, inconsistent |
| 1-2 | Draft, not recommended |

---

## Contributing

1. Create instruction in appropriate category folder
2. Follow `instruction.schema.json`
3. Test with at least 3 different inputs
4. Document quality score honestly
5. Add to version control

---

*Version: 1.0.0 | Created: 2026-01-06*
