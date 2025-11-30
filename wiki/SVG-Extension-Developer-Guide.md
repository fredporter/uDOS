# SVG Extension Developer Guide

**Extension**: svg_generator
**Version**: 1.0.0
**Category**: Core Extension
**Type**: Service

## Overview

The SVG Generator extension provides AI-powered vector diagram generation with multiple artistic styles. This guide covers the architecture, API usage, and extension development.

## Architecture

### Directory Structure

```
extensions/core/svg_generator/
├── __init__.py              # Module exports
├── extension.json           # Extension manifest
├── svg_generator.py         # Main service (444 lines)
└── README.md                # User documentation

core/commands/
└── svg_handler.py           # Command handler (216 lines)

sandbox/tests/
├── test_svg_extension.py    # Unit tests (17 tests)
├── test_svg_manual.py       # Manual tests (8 tests)
└── test_svg_performance.py  # Performance tests (6 tests)
```

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│ User Command: SVG <description> --style <style>         │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ core/commands/svg_handler.py                            │
│ - Parse parameters                                      │
│ - Validate style                                        │
│ - Call SVGGenerator                                     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ extensions/core/svg_generator/svg_generator.py          │
│ - Build AI prompt (style-specific)                     │
│ - Call Gemini API OR use template                      │
│ - Validate SVG                                          │
│ - Post-process (xmlns, viewBox)                        │
│ - Save to file                                          │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Output: sandbox/drafts/svg/<filename>.svg               │
└─────────────────────────────────────────────────────────┘
```

## Python API

### SVGGenerator Class

```python
from extensions.core.svg_generator import SVGGenerator

# Initialize
generator = SVGGenerator(config=None)  # Uses default Config

# Generate SVG
svg_content = generator.generate(
    description="water filter diagram",
    style="lineart",  # lineart, blueprint, sketch, isometric
    save_path="water-filter.svg"  # Optional
)

# The generate() method:
# 1. Validates style
# 2. Builds AI prompt (style-specific)
# 3. Calls Gemini API or falls back to template
# 4. Post-processes (adds xmlns, viewBox)
# 5. Validates XML
# 6. Saves if save_path provided
# Returns: SVG content as string
```

### Helper Functions

```python
from extensions.core.svg_generator import generate_svg, quick_svg

# Quick generation with all options
svg = generate_svg(
    description="fire triangle",
    style="blueprint",
    save_path="diagrams/fire.svg"
)

# Ultra-quick lineart generation
svg = quick_svg("simple diagram")
```

### Style Configuration

```python
# Access style definitions
from extensions.core.svg_generator import SVGGenerator

gen = SVGGenerator()
styles = gen.STYLES

# Each style has:
# {
#     'name': str,           # Display name
#     'description': str,    # Purpose description
#     'stroke_width': int,   # Line thickness (1-2)
#     'fill': bool/str,      # Fill setting
#     'colors': list/bool,   # Color palette or False
#     ...additional config
# }
```

## Adding New Styles

### 1. Define Style Configuration

Edit `extensions/core/svg_generator/svg_generator.py`:

```python
STYLES = {
    # ... existing styles ...

    'watercolor': {
        'name': 'Watercolor',
        'description': 'Soft watercolor painting style',
        'stroke_width': 1,
        'fill': True,
        'colors': ['#FFB6C1', '#ADD8E6', '#90EE90'],
        'opacity': 0.7,
        'blend_mode': 'multiply'
    }
}
```

### 2. Add Prompt Template

In `_build_prompt()` method:

```python
elif style == 'watercolor':
    prompt += """
- Soft, flowing shapes
- Translucent overlapping colors
- Gentle gradients
- Pastel color palette
- Organic, fluid edges
"""
```

### 3. Add Template Fallback

In `_generate_template()` method:

```python
if style == 'watercolor':
    svg += '  <defs>\n'
    svg += '    <filter id="watercolor">\n'
    svg += '      <feTurbulence baseFrequency="0.05"/>\n'
    svg += '      <feColorMatrix type="saturate" values="0.8"/>\n'
    svg += '    </filter>\n'
    svg += '  </defs>\n'
```

### 4. Update Documentation

- Add to `STYLES` dict docstring
- Update `SVG-Command-Reference.md`
- Add examples to `SVG-Examples.md`

## Extending Functionality

### Custom Validators

```python
class SVGGenerator:
    def _custom_validate(self, svg_content: str) -> bool:
        """Add custom validation logic"""
        # Check for required elements
        if '<rect' not in svg_content and '<circle' not in svg_content:
            return False

        # Check file size
        if len(svg_content) > 100000:  # 100KB limit
            return False

        return True
```

### Custom Post-Processing

```python
def _post_process(self, svg_content: str, style: str) -> str:
    """Override to add custom processing"""
    # Call parent
    svg_content = super()._post_process(svg_content, style)

    # Add watermark
    if style == 'blueprint':
        svg_content = svg_content.replace(
            '</svg>',
            '  <text x="750" y="590" font-size="10" opacity="0.3">uDOS</text>\n</svg>'
        )

    return svg_content
```

### Custom AI Prompts

```python
def _build_custom_prompt(self, description: str, context: dict) -> str:
    """Build context-aware prompts"""
    prompt = f"Generate SVG diagram: {description}\n"

    # Add context from knowledge bank
    if context.get('category') == 'water':
        prompt += "Focus on water-related elements: pipes, containers, flow\n"

    # Add user preferences
    if context.get('detail_level') == 'high':
        prompt += "Include detailed annotations and labels\n"

    return prompt
```

## Testing Your Extensions

### Unit Tests

```python
# sandbox/tests/test_svg_custom.py
import pytest
from extensions.core.svg_generator import SVGGenerator

def test_custom_style():
    """Test custom style generation."""
    gen = SVGGenerator()

    # Should accept custom style
    svg = gen.generate("test", style="watercolor")

    assert svg is not None
    assert '<svg' in svg
    assert gen._validate_svg(svg)

def test_custom_validation():
    """Test custom validation logic."""
    gen = SVGGenerator()

    # Valid SVG
    assert gen._custom_validate('<svg><rect/></svg>')

    # Invalid (no shapes)
    assert not gen._custom_validate('<svg><text/></svg>')
```

### Integration Tests

```python
def test_command_integration():
    """Test SVG command with custom style."""
    from core.commands.svg_handler import SVGHandler

    handler = SVGHandler()
    result = handler.handle_command(["test diagram", "--style", "watercolor"])

    assert "✅" in result
    assert "watercolor" in result.lower()
```

## Performance Optimization

### Template Caching

```python
class SVGGenerator:
    def __init__(self, config=None):
        # ... existing init ...
        self._template_cache = {}

    def _generate_template(self, description: str, style: str) -> str:
        # Check cache
        cache_key = f"{style}:{description[:20]}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]

        # Generate
        svg = self._build_template(description, style)

        # Cache
        self._template_cache[cache_key] = svg
        return svg
```

### Batch Generation

```python
def generate_batch(descriptions: list, style: str = 'lineart'):
    """Generate multiple SVGs efficiently."""
    generator = SVGGenerator()

    results = []
    for desc in descriptions:
        svg = generator.generate(desc, style=style)
        results.append(svg)

    return results

# Usage
diagrams = generate_batch([
    "water filter",
    "fire triangle",
    "shelter types"
], style="blueprint")
```

## AI Integration Details

### Gemini API Usage

```python
# In _generate_with_ai()
if self.gemini:
    try:
        # Build requirements for Gemini
        requirements = [
            f"Style: {style}",
            f"Description: {style_config.get('description', style)}",
        ]

        # Add colors if list
        if isinstance(style_config.get('colors'), list):
            requirements.append(f"Colors: {', '.join(style_config['colors'])}")

        # Call Gemini
        svg_content, metadata = self.gemini.generate_svg(
            subject=description,
            diagram_type=style,
            requirements=requirements
        )

        # Extract if in markdown
        extracted = self._extract_svg(svg_content)
        return extracted if extracted else svg_content

    except Exception as e:
        print(f"AI generation error: {e}, falling back to template")
```

### Fallback Strategy

1. **Try Gemini API** → If fails →
2. **Template Generation** → If fails →
3. **Raise ValueError**

This ensures diagrams always generate (offline capability).

## Extension Manifest

```json
{
  "id": "svg-generator",
  "name": "SVG Diagram Generator",
  "version": "1.0.0",
  "category": "core",
  "type": "service",

  "dependencies": {
    "uDOS": ">=1.1.4",
    "python": ">=3.10",
    "extensions": ["ok_assistant"]
  },

  "requires_api": {
    "gemini": {
      "required": true,
      "key_env": "GEMINI_API_KEY"
    }
  },

  "provides": {
    "commands": [{
      "name": "SVG",
      "syntax": "SVG <description> [--style <style>] [--save <file>]"
    }],
    "services": [{
      "name": "SVGGenerator",
      "file": "svg_generator.py"
    }]
  }
}
```

## Common Patterns

### Error Handling

```python
try:
    svg = generator.generate(description, style=style)
except ValueError as e:
    if "Unknown style" in str(e):
        # Handle invalid style
        print(f"Invalid style. Use: {', '.join(generator.STYLES.keys())}")
    elif "not well-formed" in str(e):
        # Handle invalid SVG
        print("Generated SVG is invalid. Using fallback...")
        svg = generator._generate_template(description, 'lineart')
    else:
        raise
```

### Custom Output Locations

```python
# Save to custom directory
svg = generator.generate("diagram", save_path="/custom/path/diagram.svg")

# Save to knowledge bank (for permanent diagrams)
svg = generator.generate(
    "water purification methods",
    style="blueprint",
    save_path="knowledge/water/diagrams/purification.svg"
)
```

### Programmatic Generation

```python
# Generate diagrams from knowledge bank
from core.services.knowledge_manager import KnowledgeManager

km = KnowledgeManager()
generator = SVGGenerator()

# Get water guides
guides = km.list_category("water")

# Generate diagram for each
for guide in guides:
    description = f"{guide['title']} overview"
    svg = generator.generate(
        description,
        style="blueprint",
        save_path=f"diagrams/water/{guide['slug']}.svg"
    )
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

generator = SVGGenerator()
svg = generator.generate("test", style="lineart")
# Will log: prompt, AI response, validation steps, etc.
```

### Inspect Generated SVG

```python
svg = generator.generate("test diagram", style="blueprint")

# Check structure
print(f"Length: {len(svg)} chars")
print(f"Has xmlns: {'xmlns' in svg}")
print(f"Has viewBox: {'viewBox' in svg}")
print(f"Valid XML: {generator._validate_svg(svg)}")

# Save for inspection
with open("debug.svg", "w") as f:
    f.write(svg)
```

### Test AI vs Template

```python
# Force template mode
generator.gemini = None
template_svg = generator.generate("test", style="lineart")

# Try AI mode (if API key available)
from core.services.gemini_generator import get_gemini_generator
generator.gemini = get_gemini_generator()
ai_svg = generator.generate("test", style="lineart")

# Compare
print(f"Template: {len(template_svg)} chars")
print(f"AI: {len(ai_svg)} chars")
```

## Best Practices

1. **Always validate styles** before passing to `generate()`
2. **Handle fallback gracefully** - templates work fine
3. **Cache when possible** - templates are deterministic
4. **Keep descriptions concise** - 5-15 words optimal
5. **Use appropriate styles** - blueprint for technical, sketch for informal
6. **Test without API** - ensure fallback works
7. **Validate output** - always check `_validate_svg()`

## Resources

- **Extension Source**: `extensions/core/svg_generator/`
- **Command Handler**: `core/commands/svg_handler.py`
- **Tests**: `sandbox/tests/test_svg_*.py`
- **Examples**: `sandbox/docs/SVG-Examples.md`
- **User Guide**: `wiki/SVG-Command-Reference.md`

## Support

For issues or questions:
1. Check test files for examples
2. Review source code comments
3. Check wiki documentation
4. Report bugs via GitHub issues

---

**Version**: 1.0.0
**Last Updated**: November 28, 2025
**License**: MIT
