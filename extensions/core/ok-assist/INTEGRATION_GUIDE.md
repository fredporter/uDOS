# OK Assist - Developer Integration Guide

**How to integrate multi-format generation into your uDOS components**

Version: 1.4.0
Date: November 25, 2025

---

## Quick Start

### 1. Basic Setup

```python
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from project root .env
project_root = Path(__file__).resolve().parents[5]  # Adjust depth as needed
load_dotenv(dotenv_path=project_root / ".env")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
```

### 2. Generate ASCII Art

```python
def generate_ascii_diagram(subject: str, description: str, width: int = 60, height: int = 20) -> str:
    """Generate ASCII art using C64 PetMe character set"""

    prompt = f"""Generate ASCII art using C64 PetMe/PETSCII characters (UTF-8).

SUBJECT: {subject}
DESCRIPTION: {description}
DIMENSIONS: {width} columns × {height} rows maximum
STYLE: Box-drawing technical diagram

Requirements:
- Use box-drawing characters: ┌┐└┘├┤┬┴┼─│
- Use ░▒▓ for shading/textures
- Use ≈∙· for particles/flow
- Label components clearly
- Keep it simple and readable

Output ONLY the ASCII art, no explanations or markdown code blocks."""

    response = model.generate_content(prompt)
    return response.text

# Example usage
ascii_art = generate_ascii_diagram(
    subject="Solar still",
    description="Water collection using condensation",
    width=50,
    height=15
)

# Save to file
output_path = Path("knowledge/diagrams/ascii/solar_still.txt")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(ascii_art)
```

### 3. Generate Teletext Graphics

```python
def generate_teletext_graphic(subject: str, description: str, width: int = 30, height: int = 15) -> str:
    """Generate Teletext HTML with mosaic blocks"""

    prompt = f"""Generate Teletext graphics using HTML mosaic blocks.

SUBJECT: {subject}
DESCRIPTION: {description}
DIMENSIONS: {width} columns × {height} rows maximum
STYLE: Mosaic block graphics (2×3 pixel cells)
COLORS: WST 8-color palette

Requirements:
- Use HTML with <pre> and colored background spans
- Use &#x2588; (█) for solid blocks
- Use &#x2584; (▄) for half blocks
- WST colors: red (#ff0000), green (#00ff00), yellow (#ffff00),
              blue (#0000ff), magenta (#ff00ff), cyan (#00ffff),
              white (#ffffff), black (#000000)
- Create clear, recognizable shapes

Output complete HTML file with inline CSS."""

    response = model.generate_content(prompt)
    return response.text

# Example usage
teletext_html = generate_teletext_graphic(
    subject="Compass rose",
    description="Navigation directions N/S/E/W"
)

# Save to file
output_path = Path("knowledge/diagrams/teletext/compass.html")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(teletext_html)
```

### 4. Generate SVG Diagrams

```python
def generate_svg_technical(subject: str, description: str, width: int = 400, height: int = 400) -> str:
    """Generate SVG in Technical-Kinetic style"""

    prompt = f"""Generate a clean SVG diagram in Technical-Kinetic style.

SUBJECT: {subject}
DESCRIPTION: {description}
STYLE: Technical-Kinetic (geometric, precise, monochromatic)
DIMENSIONS: {width}×{height}px
COMPLEXITY: Simple to moderate

Requirements:
- Clean geometric shapes
- Black lines only, stroke-width: 2px
- No gradients or colors
- Professional technical appearance
- Clear labeling with Arial font
- Scalable and production-ready

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks.
The SVG must be complete and valid."""

    response = model.generate_content(prompt)
    svg = response.text.strip()

    # Clean up markdown code blocks if present
    if svg.startswith("```"):
        svg = svg.split("```")[1]
        if svg.startswith("svg\n"):
            svg = svg[4:]
        svg = svg.strip()

    return svg

def generate_svg_organic(subject: str, description: str, width: int = 300, height: int = 400) -> str:
    """Generate SVG in Hand-Illustrative style"""

    prompt = f"""Generate an SVG diagram in Hand-Illustrative style.

SUBJECT: {subject}
DESCRIPTION: {description}
STYLE: Hand-Illustrative (organic, sketchy, imperfect lines)
DIMENSIONS: {width}×{height}px
COMPLEXITY: Simple to moderate

Requirements:
- Hand-drawn aesthetic with slightly wavy/imperfect lines
- Stroke-width: 2-3px with slight variations
- Organic, natural feel
- Black lines only, no fills or gradients
- Simple and charming
- Natural subject matter (plants, anatomy, landscapes)

Output ONLY the <svg>...</svg> code, no explanations or markdown code blocks.
The SVG must be complete and valid."""

    response = model.generate_content(prompt)
    svg = response.text.strip()

    # Clean up markdown code blocks if present
    if svg.startswith("```"):
        svg = svg.split("```")[1]
        if svg.startswith("svg\n"):
            svg = svg[4:]
        svg = svg.strip()

    return svg

# Example usage - Technical
svg_technical = generate_svg_technical(
    subject="Knot diagram",
    description="Bowline knot with labeled parts"
)

output_path = Path("knowledge/diagrams/tools/bowline_knot.svg")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg_technical)

# Example usage - Organic
svg_organic = generate_svg_organic(
    subject="Edible plant",
    description="Dandelion plant showing leaves, flower, and roots"
)

output_path = Path("knowledge/diagrams/food/dandelion.svg")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg_organic)
```

---

## Integration Patterns

### Pattern 1: CLI Help Enhancement

Add ASCII diagrams to command help text:

```python
# In uDOS_commands.py or similar

def cmd_water_filter_help():
    """Show water filter construction guide with ASCII diagram"""

    ascii_diagram = Path("knowledge/diagrams/ascii/water_filter.txt").read_text()

    print("=" * 80)
    print("WATER FILTER CONSTRUCTION")
    print("=" * 80)
    print()
    print(ascii_diagram)
    print()
    print("Materials needed:")
    print("  - Container with drainage holes")
    print("  - Gravel (coarse layer)")
    print("  - Sand (fine filtration)")
    print("  - Charcoal (chemical filtration)")
    print()
```

### Pattern 2: Web Display Integration

Embed Teletext graphics in web extensions:

```python
# In extensions/core/teletext/ or similar

def render_navigation_map():
    """Display Teletext-style navigation map"""

    teletext_html = Path("knowledge/diagrams/teletext/compass.html").read_text()

    # Serve as HTML or embed in template
    return teletext_html
```

### Pattern 3: Knowledge Base Enhancement

Add SVG diagrams to markdown documentation:

```markdown
# First Aid - CPR Guide

## Hand Position

![CPR Hand Position](../diagrams/medical/cpr_hand_position.svg)

The diagram above shows correct hand placement for chest compressions.
```

### Pattern 4: Batch Generation

Generate diagrams for entire content library:

```python
def batch_generate_diagrams(category: str, subjects: list[dict]):
    """Generate diagrams for multiple subjects in a category"""

    for item in subjects:
        subject = item['subject']
        description = item['description']
        formats = item.get('formats', ['ascii', 'svg'])

        if 'ascii' in formats:
            ascii_art = generate_ascii_diagram(subject, description)
            path = f"knowledge/diagrams/ascii/{category}/{subject.lower().replace(' ', '_')}.txt"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(ascii_art)

        if 'teletext' in formats:
            teletext = generate_teletext_graphic(subject, description)
            path = f"knowledge/diagrams/teletext/{category}/{subject.lower().replace(' ', '_')}.html"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(teletext)

        if 'svg' in formats:
            style = item.get('style', 'technical')
            if style == 'technical':
                svg = generate_svg_technical(subject, description)
            else:
                svg = generate_svg_organic(subject, description)

            path = f"knowledge/diagrams/{category}/{subject.lower().replace(' ', '_')}.svg"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(svg)

# Example usage
medical_subjects = [
    {
        'subject': 'Heimlich maneuver',
        'description': 'Abdominal thrust technique for choking',
        'formats': ['ascii', 'svg'],
        'style': 'organic'
    },
    {
        'subject': 'Tourniquet application',
        'description': 'Proper tourniquet placement on limbs',
        'formats': ['ascii', 'svg'],
        'style': 'technical'
    }
]

batch_generate_diagrams('medical', medical_subjects)
```

---

## Directory Structure

Organize generated diagrams by category:

```
knowledge/diagrams/
├── README.md                    # Index of all diagrams
├── ascii/                       # ASCII art (.txt files)
│   ├── medical/
│   ├── water/
│   ├── fire/
│   ├── shelter/
│   ├── food/
│   ├── tools/
│   └── navigation/
├── teletext/                    # Teletext graphics (.html files)
│   ├── navigation/
│   ├── system/
│   └── communication/
├── medical/                     # SVG diagrams by category
│   ├── cpr_*.svg
│   ├── heimlich_*.svg
│   └── ...
├── water/
│   ├── filter_*.svg
│   ├── purification_*.svg
│   └── ...
└── [other categories]/
```

---

## Best Practices

### 1. Prompt Engineering

**Be specific about dimensions:**
```python
# Good
"DIMENSIONS: 60 columns × 20 rows maximum"

# Bad
"Make it fit on screen"
```

**Specify character sets:**
```python
# Good
"Use box-drawing characters: ┌┐└┘├┤┬┴┼─│"

# Bad
"Use ASCII art"
```

**Request clean output:**
```python
# Good
"Output ONLY the ASCII art, no explanations or markdown code blocks."

# Bad
# (No instruction about output format)
```

### 2. Error Handling

```python
def generate_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Generate content with retry logic"""

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                continue
            else:
                raise
```

### 3. Output Validation

```python
def validate_svg(svg_content: str) -> bool:
    """Validate SVG content"""

    # Check if it's valid SVG
    if not svg_content.strip().startswith('<svg'):
        return False
    if not svg_content.strip().endswith('</svg>'):
        return False

    # Check size
    if len(svg_content) > 50000:  # 50KB limit
        print(f"Warning: SVG is {len(svg_content)} bytes (>50KB)")
        return False

    return True

def validate_ascii(ascii_content: str, max_width: int = 80) -> bool:
    """Validate ASCII art content"""

    lines = ascii_content.split('\n')

    # Check width
    for line in lines:
        if len(line) > max_width:
            print(f"Warning: Line exceeds {max_width} chars: {len(line)}")
            return False

    return True
```

### 4. Caching and Reuse

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def generate_cached(subject: str, description: str, format_type: str) -> str:
    """Generate with caching to avoid duplicate API calls"""

    if format_type == 'ascii':
        return generate_ascii_diagram(subject, description)
    elif format_type == 'teletext':
        return generate_teletext_graphic(subject, description)
    elif format_type == 'svg_technical':
        return generate_svg_technical(subject, description)
    elif format_type == 'svg_organic':
        return generate_svg_organic(subject, description)
```

---

## Testing

### Unit Tests

```python
import unittest

class TestMultiFormatGeneration(unittest.TestCase):

    def test_ascii_generation(self):
        """Test ASCII art generation"""
        result = generate_ascii_diagram("Test box", "Simple box diagram")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_svg_validation(self):
        """Test SVG content validation"""
        svg = generate_svg_technical("Test diagram", "Simple test")
        self.assertTrue(validate_svg(svg))

    def test_file_size_limits(self):
        """Test generated files stay under size limits"""
        svg = generate_svg_technical("Test", "Test")
        self.assertLess(len(svg), 50000)  # 50KB limit
```

### Integration Tests

```python
def test_full_workflow():
    """Test complete generation workflow"""

    # Generate all formats
    subject = "Test Subject"
    description = "Test description"

    ascii_art = generate_ascii_diagram(subject, description)
    teletext = generate_teletext_graphic(subject, description)
    svg_tech = generate_svg_technical(subject, description)
    svg_org = generate_svg_organic(subject, description)

    # Validate
    assert len(ascii_art) > 0
    assert '<html>' in teletext.lower()
    assert validate_svg(svg_tech)
    assert validate_svg(svg_org)

    print("✅ Full workflow test passed")
```

---

## Performance Considerations

### API Rate Limits

Gemini API has rate limits. Consider:

1. **Batch requests** where possible
2. **Cache results** to avoid regeneration
3. **Implement retry logic** with exponential backoff
4. **Monitor API usage** and quotas

### Generation Time

Typical generation times:
- ASCII art: 3-8 seconds
- Teletext graphics: 5-10 seconds
- SVG diagrams: 5-15 seconds

For batch generation, consider:
- Progress indicators
- Async/parallel processing
- Save checkpoints

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def generate_batch_async(subjects: list[dict], max_workers: int = 3):
    """Generate multiple diagrams in parallel"""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = []

        for item in subjects:
            task = loop.run_in_executor(
                executor,
                generate_svg_technical,
                item['subject'],
                item['description']
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return results
```

---

## Troubleshooting

### Common Issues

**Issue: "Module importlib.metadata has no attribute 'packages_distributions'"**
- This is a benign warning with Python 3.9.6
- Does not affect functionality
- Consider upgrading to Python 3.10+ when convenient

**Issue: SVG wrapped in markdown code blocks**
- Use the cleanup code shown in `generate_svg_*` functions
- Strip `\`\`\`svg` and `\`\`\`` markers

**Issue: API key not found**
- Ensure `.env` file exists in project root
- Check `GEMINI_API_KEY` is set correctly
- Verify path calculation to project root

**Issue: Generated content too large**
- Add size constraints to prompts
- Implement validation and retry with simpler prompts
- Consider splitting complex diagrams

---

## Examples

See working examples in:
- `examples/demo_simple.py` - Complete multi-format demo
- `examples/test_quick.py` - Quick API validation
- `EXAMPLES.md` - Generated examples gallery
- `SUCCESS_REPORT.md` - Implementation report

---

## Support

For questions or issues:
1. Check existing documentation in `docs/`
2. Review working examples in `examples/`
3. See `TROUBLESHOOTING.md` (if exists)
4. Check API documentation: https://ai.google.dev/docs

---

**Last Updated:** November 25, 2025
**Version:** 1.4.0
**Status:** Production Ready ✅
